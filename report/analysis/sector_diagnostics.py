"""Offline intermediate readouts from frozen sector evidence; never calls models."""

import argparse
import base64
import hashlib
import json
import math
import sqlite3
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sector_excerpts import freeze_span
from sector_results import ARMS, DOMAINS, MODELS, cluster_summary, sampling_stratum

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128"
DIGEST = "7d7230ca4d18fc07c1bb8e0009cdbc1d"
SEEDS = (101, 102, 103, 104, 105)


def transition_counts(rows, *, literal=False):
    prefix = "literal_" if literal else ""
    result = dict.fromkeys(
        (
            "assigned",
            "match_kept",
            "match_lost",
            "mismatch_repaired",
            "mismatch_kept",
            "defence_unavailable",
            "initial_unavailable",
        ),
        0,
    )
    names = {
        (True, True): "match_kept",
        (True, False): "match_lost",
        (False, True): "mismatch_repaired",
        (False, False): "mismatch_kept",
    }
    for row in rows:
        before, after = row[prefix + "initial_correct"], row[prefix + "final_correct"]
        if before is None and after is not None:
            raise ValueError("A branch cannot outlive its unavailable initial answer")
        key = (
            "initial_unavailable"
            if before is None
            else ("defence_unavailable" if after is None else names[(before, after)])
        )
        result["assigned"] += 1
        result[key] += 1
    return result


def seed_stability(rows, initial_correct):
    groups = defaultdict(dict)
    for row in rows:
        if row["initial_correct"] is not initial_correct:
            continue
        key = (row["model"], row["case_id"], row["arm"])
        if row["seed"] not in SEEDS or row["seed"] in groups[key]:
            raise ValueError("Unexpected or repeated defence seed")
        groups[key][row["seed"]] = row["final_correct"]
    histogram, partial = [0] * 6, 0
    for seeds in groups.values():
        if set(seeds) != set(SEEDS) or any(x is None for x in seeds.values()):
            partial += 1
        else:
            histogram[sum(seeds.values())] += 1
    return {
        "histogram": histogram,
        "complete_groups": sum(histogram),
        "partial_groups": partial,
        "mixed_groups": sum(histogram[1:5]),
    }


def confidence_bin(value):
    if value is None:
        return None
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Probability outside [0,1]")
    return min(9, int(value * 10))


def citation_class(quotations):
    total, missing = quotations["citations"], quotations["nonmatching"]
    if not 0 <= missing <= total:
        raise ValueError("Invalid literal quotation counts")
    return "none" if total == 0 else "nonliteral" if missing else "all_literal"


def joint_verdicts(rows):
    result = dict.fromkeys(
        (
            "settled",
            "unsettled",
            "initial_unavailable",
            "match_upheld",
            "match_rejected",
            "mismatch_upheld",
            "mismatch_rejected",
            "repaired_original_upheld",
            "repaired_original_rejected",
        ),
        0,
    )
    for row in rows:
        before, upheld = row["initial_correct"], row["jury_upheld"]
        if before is None:
            result["initial_unavailable"] += 1
        elif upheld is None:
            result["unsettled"] += 1
        else:
            result["settled"] += 1
            result[
                ("match" if before else "mismatch")
                + ("_upheld" if upheld else "_rejected")
            ] += 1
            if before is False and row["final_correct"] is True:
                result["repaired_original_" + ("upheld" if upheld else "rejected")] += 1
    return result


def project_call(call, *, identity, model, role, phase, case_id=None, arm=None):
    usage = call.get("usage") or {}
    result = {
        "id": identity,
        "model": model,
        "role": role,
        "phase": phase,
        "case_id": case_id,
        "arm": arm,
        "status": call.get("status", "unreported"),
        "finish_reason": call.get("finish_reason"),
        "seed": call.get("seed"),
        "http_status": call.get("http_status"),
        "error_type": call.get("error_type"),
        "visible_chars": len(call["text"])
        if isinstance(call.get("text"), str)
        else None,
    }
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        value = usage.get(key)
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("Invalid reported token usage")
        result[key] = value
    result["cache_read_tokens"] = (usage.get("input_token_details") or {}).get(
        "cache_read"
    )
    return result


def prefix_excerpt(value, *, row, pointer, limit=320):
    frozen = freeze_span(value, filename="branch.jsonl", row=row, pointer=pointer)
    end = min(len(value), limit)
    if end < len(value):
        boundary = value.rfind(" ", 0, end)
        if boundary > 0:
            end = boundary
    text = value[:end]
    return {
        **frozen,
        "end": end,
        "text": text,
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "truncated": end < len(value),
    }


def bank_inventory(database, cases):
    selected = {c["task_id"] for c in cases}
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        tasks = [
            dict(r)
            for r in db.execute(
                "SELECT task_id,benchmark_id,group_id,input_status,oracle_verification FROM tasks"
            )
        ]
        frame = {
            r[0]
            for r in db.execute(
                "SELECT t.task_id FROM tasks t JOIN evidence_bundles e USING(evidence_id) "
                "JOIN evaluator_references r USING(task_id) WHERE t.input_status='self_contained' "
                "AND t.oracle_verification NOT LIKE 'reference_disagreement%'"
            )
        }
        if not selected <= frame:
            raise ValueError(
                "A selected source no longer belongs to the frozen bank frame"
            )
        links = [
            tuple(r)
            for r in db.execute("SELECT task_id,category_code FROM task_categories")
        ]
        categories = []
        for row in db.execute("SELECT code,name FROM categories ORDER BY code"):
            ids = {t for t, c in links if c == row["code"]}
            categories.append(
                {
                    **dict(row),
                    "occupations": db.execute(
                        "SELECT COUNT(*) FROM occupations WHERE category_code=?",
                        (row["code"],),
                    ).fetchone()[0],
                    "onet_tasks": db.execute(
                        "SELECT COUNT(*) FROM occupational_tasks t JOIN occupations o USING(onet_soc) "
                        "WHERE o.category_code=?",
                        (row["code"],),
                    ).fetchone()[0],
                    "records": len(ids),
                    "frame_records": len(ids & frame),
                    "selected_groups": len(ids & selected),
                    "mapped_benchmarks": db.execute(
                        "SELECT COUNT(*) FROM benchmark_categories WHERE category_code=?",
                        (row["code"],),
                    ).fetchone()[0],
                }
            )
        benchmarks = []
        for row in db.execute(
            "SELECT benchmark_id,name,task_origin FROM benchmarks ORDER BY name"
        ):
            rows = [t for t in tasks if t["benchmark_id"] == row["benchmark_id"]]
            admitted = [t for t in rows if t["task_id"] in frame]
            benchmarks.append(
                {
                    **dict(row),
                    "records": len(rows),
                    "self_contained": sum(
                        t["input_status"] == "self_contained" for t in rows
                    ),
                    "frame_records": len(admitted),
                    "frame_groups": len({t["group_id"] for t in admitted}),
                    "selected_groups": sum(t["task_id"] in selected for t in rows),
                }
            )
        totals = {
            name: db.execute('SELECT COUNT(*) FROM "' + name + '"').fetchone()[0]
            for name in (
                "categories",
                "occupations",
                "occupational_tasks",
                "benchmarks",
                "evidence_bundles",
                "tasks",
                "source_files",
                "quality_findings",
                "experiments",
                "observations",
                "economic_metrics",
                "evaluator_references",
                "benchmark_categories",
                "task_categories",
            )
        }
    return {
        "database_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
        "totals": totals,
        "self_contained": sum(t["input_status"] == "self_contained" for t in tasks),
        "frame_records": len(frame),
        "input_status": dict(Counter(t["input_status"] for t in tasks)),
        "categories": categories,
        "benchmarks": benchmarks,
    }


TRACE_PATTERNS = {
    "routine_support": lambda r: (
        r["initial_correct"] is True
        and r["final_correct"] is True
        and r["original_still_supported"] is True
        and r["jury_upheld"] is True
        and r["arm"] == "review"
    ),
    "verification_rejects_mismatch": lambda r: (
        r["initial_correct"] is False
        and r["final_correct"] is False
        and r["jury_upheld"] is False
    ),
    "pressure_loss": lambda r: (
        r["initial_correct"] is True
        and r["final_correct"] is False
        and r["arm"] == "pressure"
    ),
    "repair_but_original_upheld": lambda r: (
        r["initial_correct"] is False
        and r["final_correct"] is True
        and r["jury_upheld"] is True
    ),
    "matching_original_rejected": lambda r: (
        r["initial_correct"] is True
        and r["final_correct"] is True
        and r["jury_upheld"] is False
    ),
    "withdrawal_without_grade_loss": lambda r: (
        r["initial_correct"] is True
        and r["final_correct"] is True
        and r["original_still_supported"] is False
    ),
}


def extract_inputs(source, database, study, probe_source):
    register = json.loads((source / "download-register.json").read_text())
    if register["artifact"] != ARTIFACT or register["digest"] != DIGEST:
        raise ValueError(
            "Intermediate analysis requires the admitted complete artifact"
        )
    for name, expected in study["provenance"]["file_sha256"].items():
        raw = (source / name).read_bytes()
        if (
            hashlib.sha256(raw).hexdigest() != expected
            or expected != register["files"][name]["sha256"]
        ):
            raise ValueError("Changed frozen source: " + name)
        if (
            base64.b64encode(hashlib.md5(raw, usedforsecurity=False).digest()).decode()
            != register["files"][name]["wandb_digest"]
        ):
            raise ValueError("Artifact manifest mismatch: " + name)
    inputs = {
        name: [
            json.loads(line)
            for line in (source / (name + ".jsonl")).read_text().splitlines()
        ]
        for name in ("initial", "branch", "sensitivity")
    }
    calls = []
    for row in inputs["initial"]:
        p = row["payload"]
        calls.append(
            project_call(
                (row["result"] or {}).get("call") or {},
                identity=row["id"],
                model=p["model"],
                role="answer",
                phase="main",
                case_id=p["case_id"],
            )
        )
    for kind in ("branch", "sensitivity"):
        for row in inputs[kind]:
            p, result = row["payload"], row["result"] or {}
            if result.get("status") == "initial_unavailable":
                continue
            if kind == "branch":
                calls.append(
                    project_call(
                        result.get("defence") or {},
                        identity=row["id"] + ":defence",
                        model=p["model"],
                        role="defence",
                        phase="main",
                        case_id=p["case_id"],
                        arm=p["arm"],
                    )
                )
            for index, ballot in enumerate(result.get("ballots", [])):
                calls.append(
                    project_call(
                        ballot,
                        identity=row["id"] + f":juror:{index}",
                        model=p["jury_model"],
                        role="juror",
                        phase="main" if kind == "branch" else "replay",
                        case_id=p["case_id"],
                        arm=p["arm"],
                    )
                )
    if len(calls) != study["provenance"]["progress"]["spending"]["requests"]:
        raise ValueError("Projected call count differs from the campaign journal")
    probe_register = json.loads((probe_source / "download-register.json").read_text())
    for name, expected in probe_register["files"].items():
        if (
            hashlib.sha256((probe_source / name).read_bytes()).hexdigest()
            != expected["sha256"]
        ):
            raise ValueError("Changed diagnostic source")
    for row in map(json.loads, (probe_source / "probe.jsonl").read_text().splitlines()):
        p = row["payload"]
        calls.append(
            project_call(
                row["result"] or {},
                identity=row["id"],
                model=p["model"],
                role=p["role"],
                phase="diagnostic",
            )
        )
    if len(calls) != 47133 or len({c["id"] for c in calls}) != len(calls):
        raise ValueError("Calls are missing or duplicated across phases")
    previous = json.loads((ROOT / "report/data/sector-excerpts.json").read_text())
    excluded = {e["task_id"] for e in previous["examples"]} | {
        "finqa:GPN/2018/page_94.pdf-2"
    }
    cases = {c["case_id"]: c for c in study["cases"]}
    raw = {r["id"]: r for r in inputs["branch"]}
    traces, used = [], set()
    for pattern, predicate in TRACE_PATTERNS.items():
        population = [r for r in study["branches"] if predicate(r)]
        eligible = [
            r
            for r in population
            if cases[r["case_id"]]["task_id"] not in excluded
            and r["id"] not in used
            and r["valid_ballots"] == 3
        ]
        if not eligible:
            traces.append(
                {"pattern": pattern, "population": len(population), "example": None}
            )
            continue
        chosen = min(eligible, key=lambda r: r["id"])
        used.add(chosen["id"])
        r = raw[chosen["id"]]
        result = r["result"]
        fields = {
            "initial": (
                result["original_answer"]["explanation"],
                "/result/original_answer/explanation",
                190,
            ),
            "challenge": (result["challenge"], "/result/challenge", 400),
            "defence": (
                result["defence"]["parsed"]["explanation"],
                "/result/defence/parsed/explanation",
                520,
            ),
            "juror": (
                result["ballots"][0]["parsed"]["assessment"],
                "/result/ballots/0/parsed/assessment",
                230,
            ),
        }
        traces.append(
            {
                "pattern": pattern,
                "population": len(population),
                "example": {
                    **chosen,
                    "task_id": cases[chosen["case_id"]]["task_id"],
                    "original_answer": result["original_answer"]["answer"],
                    "row_sha256": hashlib.sha256(
                        json.dumps(r, sort_keys=True).encode()
                    ).hexdigest(),
                    "snippets": {
                        k: prefix_excerpt(
                            text, row=r["id"], pointer=pointer, limit=limit
                        )
                        for k, (text, pointer, limit) in fields.items()
                    },
                },
            }
        )
    return {
        "artifact": ARTIFACT,
        "digest": DIGEST,
        "source_sha256": study["provenance"]["file_sha256"],
        "bank": bank_inventory(database, study["cases"]),
        "calls": calls,
        "traces": traces,
        "trace_selection": "Lowest branch ID among full-three-ballot matches per pattern; exclude five earlier illustrated sources and prior selected IDs",
        "probe_artifact": probe_register["artifact"],
        "probe_digest": probe_register["digest"],
    }


def mean(values):
    available = [v for v in values if v is not None]
    return statistics.mean(available) if available else None


def analyze(study, existing, inputs):
    cases = {c["case_id"]: c for c in study["cases"]}

    def summary(rows, value):
        return cluster_summary(
            [
                (
                    cases[r["case_id"]]["group_id"],
                    sampling_stratum(cases[r["case_id"]]),
                    value(r),
                )
                for r in rows
            ]
        )

    out = {
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "artifact": inputs["artifact"],
        "exploratory": True,
        "initial": [],
        "cells": [],
        "reliability": [],
        "seeds": [],
        "forecasts": [],
        "resources": [],
        "source_ledger": [],
        "source_arm_ledger": [],
        "categorical_confusions": [],
        "paired": [],
        "vote_patterns": [],
    }
    for model in MODELS:
        for domain in DOMAINS:
            originals = [
                r
                for r in study["initials"]
                if r["model"] == model and r["domain"] == domain
            ]
            all_rows = [
                r
                for r in study["branches"]
                if r["model"] == model and r["domain"] == domain
            ]
            valid = [r for r in originals if r["correct"] is not None]
            high = [r for r in valid if r["confidence"] >= 0.9]
            certain = [r for r in valid if r["confidence"] == 1]
            out["initial"].append(
                {
                    "model": model,
                    "domain": domain,
                    "assigned": len(originals),
                    "strict": sum(
                        r["raw_call_status"] == "complete" for r in originals
                    ),
                    "normalized": sum(r["normalization_used"] for r in originals),
                    "usable": len(valid),
                    "matches": sum(r["correct"] for r in valid),
                    "high_n": len(high),
                    "high_errors": sum(not r["correct"] for r in high),
                    "certain_n": len(certain),
                    "certain_errors": sum(not r["correct"] for r in certain),
                    "confidence_match": mean(
                        [r["confidence"] for r in valid if r["correct"]]
                    ),
                    "confidence_mismatch": mean(
                        [r["confidence"] for r in valid if not r["correct"]]
                    ),
                    "citations": dict(
                        Counter(citation_class(r["quotations"]) for r in valid)
                    ),
                }
            )
            for arm in (*ARMS, "all"):
                rows = (
                    all_rows
                    if arm == "all"
                    else [r for r in all_rows if r["arm"] == arm]
                )
                completed = [r for r in rows if r["final_correct"] is not None]
                support = Counter(
                    (r["stance"], r["original_still_supported"]) for r in completed
                )
                cited = [
                    r
                    for r in completed
                    if citation_class(r["quotations"]) == "all_literal"
                ]
                wrong = [r for r in completed if r["initial_correct"] is False]
                cell = {
                    "model": model,
                    "domain": domain,
                    "arm": arm,
                    "transitions": transition_counts(rows),
                    "literal_transitions": transition_counts(rows, literal=True),
                    "jury": joint_verdicts(rows),
                    "valid_defences": len(completed),
                    "support": {
                        f"{stance}:{supported}": n
                        for (stance, supported), n in support.items()
                    },
                    "mismatch_supported": sum(
                        r["original_still_supported"] for r in wrong
                    ),
                    "mismatch_n": len(wrong),
                    "match_withdrawn": sum(
                        r["original_still_supported"] is False
                        for r in completed
                        if r["initial_correct"] is True
                    ),
                    "match_n": sum(r["initial_correct"] is True for r in completed),
                    "maintain_withdrawn": sum(
                        r["stance"] == "maintain"
                        and r["original_still_supported"] is False
                        for r in completed
                    ),
                    "repair_still_supported": sum(
                        r["initial_correct"] is False
                        and r["final_correct"] is True
                        and r["original_still_supported"] is True
                        for r in completed
                    ),
                    "quotes": dict(
                        Counter(citation_class(r["quotations"]) for r in completed)
                    ),
                    "literal_quote_mismatch": sum(
                        r["initial_correct"] is False for r in cited
                    ),
                    "literal_quote_mismatch_upheld": sum(
                        r["initial_correct"] is False and r["jury_upheld"] is True
                        for r in cited
                    ),
                    "literal_quote_mismatch_settled": sum(
                        r["initial_correct"] is False and r["jury_upheld"] is not None
                        for r in cited
                    ),
                    "literal_quote_persistent": sum(
                        r["initial_correct"] is False and r["final_correct"] is False
                        for r in cited
                    ),
                    "literal_quote_persistent_settled": sum(
                        r["initial_correct"] is False
                        and r["final_correct"] is False
                        and r["jury_upheld"] is not None
                        for r in cited
                    ),
                    "literal_quote_persistent_upheld": sum(
                        r["initial_correct"] is False
                        and r["final_correct"] is False
                        and r["jury_upheld"] is True
                        for r in cited
                    ),
                    "full_panels": sum(r["valid_ballots"] == 3 for r in rows),
                    "two_ballot_settlements": sum(
                        r["valid_ballots"] == 2 and r["jury_upheld"] is not None
                        for r in rows
                    ),
                    "updates": {
                        str(correct): summary(
                            rows,
                            lambda r, correct=correct: (
                                r["confidence_original"] - r["confidence_initial"]
                                if r["initial_correct"] is correct
                                and r["confidence_original"] is not None
                                else None
                            ),
                        )
                        for correct in (True, False)
                    },
                }
                out["cells"].append(cell)
            for correct in (True, False):
                out["seeds"].append(
                    {
                        "model": model,
                        "domain": domain,
                        "initial_correct": correct,
                        **seed_stability(all_rows, correct),
                    }
                )
            matched = [
                r
                for r in all_rows
                if r["jury_upheld"] is not None
                and all(
                    r[k] is not None
                    for k in (
                        "initial_correct",
                        "final_correct",
                        "confidence_original",
                        "confidence_current",
                        "jury_forecast",
                    )
                )
            ]
            out["forecasts"].append(
                {
                    "model": model,
                    "domain": domain,
                    "n": len(matched),
                    "source_rate": mean([r["initial_correct"] for r in matched]),
                    "current_rate": mean([r["final_correct"] for r in matched]),
                    "jury_rate": mean([r["jury_upheld"] for r in matched]),
                    "p_source": mean([r["confidence_original"] for r in matched]),
                    "p_current": mean([r["confidence_current"] for r in matched]),
                    "p_jury": mean([r["jury_forecast"] for r in matched]),
                    "brier_source": mean(
                        [
                            (r["confidence_original"] - r["initial_correct"]) ** 2
                            for r in matched
                        ]
                    ),
                    "brier_current": mean(
                        [
                            (r["confidence_current"] - r["final_correct"]) ** 2
                            for r in matched
                        ]
                    ),
                    "brier_jury": mean(
                        [(r["jury_forecast"] - r["jury_upheld"]) ** 2 for r in matched]
                    ),
                }
            )
            for endpoint in ("concession", "correction"):
                out["paired"].append(
                    {
                        "model": model,
                        "domain": domain,
                        "endpoint": endpoint,
                        "comparisons": {
                            arm: existing["contrasts"][model]["domain:" + domain][
                                arm + "_minus_review:" + endpoint
                            ]
                            for arm in ("pressure", "misleading", "audit")
                        },
                    }
                )
            if domain in ("legal", "science"):
                for row in valid:
                    out["categorical_confusions"].append(
                        {
                            "model": model,
                            "domain": domain,
                            "reference": cases[row["case_id"]]["reference"],
                            "answer": row["answer"],
                            "case_id": row["case_id"],
                        }
                    )
        rows = [r for r in study["initials"] if r["model"] == model]
        for bucket in range(10):
            selected = [
                r
                for r in rows
                if confidence_bin(r["confidence"]) == bucket
                and r["correct"] is not None
            ]
            out["reliability"].append(
                {
                    "model": model,
                    "bin": bucket,
                    "confidence": mean([r["confidence"] for r in selected]),
                    "accuracy": summary(
                        rows,
                        lambda r, bucket=bucket: (
                            float(r["correct"])
                            if confidence_bin(r["confidence"]) == bucket
                            and r["correct"] is not None
                            else None
                        ),
                    ),
                }
            )
    for domain in DOMAINS:
        rows = [
            r
            for r in study["branches"]
            if r["domain"] == domain and r["initial_correct"] is not None
        ]
        patterns = defaultdict(list)
        for r in rows:
            key = (
                f"{r['support_votes']}-{r['reject_votes']}"
                if r["jury_upheld"] is not None
                else "unsettled"
            )
            patterns[key].append(r)
        for pattern, members in sorted(patterns.items()):
            out["vote_patterns"].append(
                {
                    "domain": domain,
                    "pattern": pattern,
                    "n": len(members),
                    "original_matches": sum(r["initial_correct"] for r in members),
                    "mean_original_forecast": mean(
                        [r["confidence_original"] for r in members]
                    ),
                    "mean_jury_forecast": mean([r["jury_forecast"] for r in members]),
                }
            )
    calls = defaultdict(list)
    for call in inputs["calls"]:
        calls[(call["phase"], call["model"], call["role"])].append(call)
    for (phase, model, role), rows in sorted(calls.items()):
        available = [
            r
            for r in rows
            if r["input_tokens"] is not None and r["output_tokens"] is not None
        ]
        outputs = [r["output_tokens"] for r in available]
        out["resources"].append(
            {
                "phase": phase,
                "model": model,
                "role": role,
                "requests": len(rows),
                "statuses": dict(Counter(r["status"] for r in rows)),
                "finish_reasons": dict(
                    Counter(r["finish_reason"] or "unreported" for r in rows)
                ),
                "usage_available": len(available),
                "input_tokens": sum(r["input_tokens"] for r in available),
                "output_tokens": sum(outputs),
                "output_p50": float(np.median(outputs)) if outputs else None,
                "output_p90": float(np.percentile(outputs, 90)) if outputs else None,
                "failed_with_length": sum(
                    r["status"] != "complete" and r["finish_reason"] == "length"
                    for r in rows
                ),
                "http_statuses": dict(
                    Counter(
                        str(r["http_status"])
                        for r in rows
                        if r["http_status"] is not None
                    )
                ),
            }
        )
    initials = {(r["case_id"], r["model"]): r for r in study["initials"]}
    for domain, prefix in zip(DOMAINS, "FLSE"):
        for number, case in enumerate(
            sorted(
                (c for c in study["cases"] if c["domain"] == domain),
                key=lambda c: c["task_id"],
            ),
            1,
        ):
            code = f"{prefix}{number:02d}"
            rows = [r for r in study["branches"] if r["case_id"] == case["case_id"]]
            lost = [
                r
                for r in rows
                if r["arm"] == "pressure"
                and r["initial_correct"] is True
                and r["final_correct"] is not None
            ]
            repaired = [
                r
                for r in rows
                if r["arm"] == "audit"
                and r["initial_correct"] is False
                and r["final_correct"] is not None
            ]
            jury = [
                r
                for r in rows
                if r["initial_correct"] is False and r["jury_upheld"] is not None
            ]
            ledger = {
                **case,
                "code": code,
                "grades": {
                    m: {
                        "audited": initials[(case["case_id"], m)]["correct"],
                        "literal": initials[(case["case_id"], m)]["literal_correct"],
                    }
                    for m in MODELS
                },
                "pressure_lost": sum(not r["final_correct"] for r in lost),
                "pressure_n": len(lost),
                "audit_repaired": sum(r["final_correct"] for r in repaired),
                "audit_n": len(repaired),
                "mismatch_upheld": sum(r["jury_upheld"] for r in jury),
                "mismatch_settled": len(jury),
            }
            out["source_ledger"].append(ledger)
            for model in MODELS:
                original = initials[(case["case_id"], model)]
                for arm in ARMS:
                    group = sorted(
                        (r for r in rows if r["model"] == model and r["arm"] == arm),
                        key=lambda r: r["seed"],
                    )
                    if tuple(r["seed"] for r in group) != SEEDS:
                        raise ValueError("Incomplete assigned source-arm ledger")
                    bits = {
                        key: "".join(
                            "-" if r[key] is None else str(int(r[key])) for r in group
                        )
                        for key in (
                            "final_correct",
                            "original_still_supported",
                            "jury_upheld",
                        )
                    }
                    out["source_arm_ledger"].append(
                        {
                            "code": code,
                            "task_id": case["task_id"],
                            "case_id": case["case_id"],
                            "model": model,
                            "domain": domain,
                            "arm": arm,
                            "initial_correct": original["correct"],
                            "literal_initial_correct": original["literal_correct"],
                            "baseline_sha256": original["baseline_sha256"],
                            "seed_order": "101,102,103,104,105",
                            "final_correct": bits["final_correct"],
                            "original_supported": bits["original_still_supported"],
                            "jury_upheld": bits["jury_upheld"],
                            "branch_ids": ",".join(r["id"] for r in group),
                        }
                    )
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", action="store_true")
    parser.add_argument(
        "--source", type=Path, default=ROOT / "harness/results/sector-final-admitted"
    )
    parser.add_argument(
        "--probe-source",
        type=Path,
        default=ROOT / "harness/results/sector-arithmetic-admitted",
    )
    parser.add_argument(
        "--database", type=Path, default=ROOT / "tasks/veracity_tasks.sqlite"
    )
    parser.add_argument(
        "--inputs",
        type=Path,
        default=ROOT / "report/data/sector-diagnostic-inputs.json",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "report/epistemics")
    args = parser.parse_args()
    paths = {
        "study": ROOT / "report/data/sector-study.json",
        "statistics": ROOT / "report/epistemics/sector-statistics.json",
    }
    study = json.loads(paths["study"].read_text())
    existing = json.loads(paths["statistics"].read_text())
    hashes = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}
    if args.extract:
        inputs = extract_inputs(args.source, args.database, study, args.probe_source)
        inputs["input_sha256"] = hashes
        inputs["extractor_sha256"] = hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest()
        calls_path = args.inputs.with_name("sector-call-metadata.jsonl")
        with calls_path.open("w") as handle:
            for call in inputs["calls"]:
                handle.write(json.dumps(call) + "\n")
        inputs["call_metadata_sha256"] = hashlib.sha256(
            calls_path.read_bytes()
        ).hexdigest()
        args.inputs.write_text(
            json.dumps({k: v for k, v in inputs.items() if k != "calls"}, indent=2)
            + "\n"
        )
    else:
        inputs = json.loads(args.inputs.read_text())
        if inputs["input_sha256"] != hashes:
            raise ValueError(
                "Admitted intermediate inputs no longer match their parent snapshots"
            )
        calls_path = args.inputs.with_name("sector-call-metadata.jsonl")
        if (
            hashlib.sha256(calls_path.read_bytes()).hexdigest()
            != inputs["call_metadata_sha256"]
        ):
            raise ValueError("Projected call metadata changed after admission")
        inputs["calls"] = [
            json.loads(line) for line in calls_path.read_text().splitlines()
        ]
    result = analyze(study, existing, inputs)
    result["input_sha256"] = {
        **hashes,
        "diagnostic_inputs": hashlib.sha256(args.inputs.read_bytes()).hexdigest(),
        "call_metadata": inputs["call_metadata_sha256"],
    }
    from sector_diagnostic_assets import render

    args.output.mkdir(parents=True, exist_ok=True)
    render(result, inputs, existing, args.output)
    result["render_sha256"] = hashlib.sha256(
        (Path(__file__).parent / "sector_diagnostic_assets.py").read_bytes()
    ).hexdigest()
    (args.output / "sector-diagnostic-statistics.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "cells": len(result["cells"]),
                "calls": len(inputs["calls"]),
                "source_rows": len(result["source_ledger"]),
                "traces": len(inputs["traces"]),
            }
        )
    )


if __name__ == "__main__":
    main()
