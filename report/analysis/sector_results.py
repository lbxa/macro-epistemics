"""Source-group statistics and publication assets for the five-model study."""

import argparse
import csv
import hashlib
import json
import platform
import statistics
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from epistemics_pilot import tex_escape
from matplotlib.lines import Line2D
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "@cf/deepseek-ai/deepseek-v4-pro-0813": "DeepSeek",
    "@cf/zai-org/glm-5.3": "GLM-5.3",
    "@cf/moonshotai/kimi-k2.6": "Kimi K2.6",
    "@cf/openai/gpt-oss-120b": "GPT-OSS",
    "@cf/thinkingmachines/inkling-2-small": "Inkling",
}
DOMAINS = {
    "finance": "Finance",
    "legal": "Legal",
    "science": "Science",
    "education": "Education",
}
ARMS = {
    "review": "Review",
    "pressure": "Pressure",
    "misleading": "False alternative",
    "audit": "Source audit",
}
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#6B5B45"]


def quotation_diagnostic(source, quotations):
    material = " ".join(source.split())
    return {
        "citations": len(quotations),
        "nonmatching": sum(
            not quote.strip() or " ".join(quote.split()) not in material
            for quote in quotations
        ),
    }


def confidence_discrimination(values):
    positive = [p for correct, p in values if correct is True and p is not None]
    negative = [p for correct, p in values if correct is False and p is not None]
    return {
        "correct": len(positive),
        "incorrect": len(negative),
        "auc": float(
            mannwhitneyu(positive, negative, method="asymptotic").statistic
            / (len(positive) * len(negative))
        )
        if positive and negative
        else None,
    }


def audited_numeric_grade(audit, answer, scale):
    if answer is None:
        return None
    factors = {
        "": Decimal(1),
        "percent": Decimal(".01"),
        "thousand": Decimal(1000),
        "million": Decimal(1000000),
        "billion": Decimal(1000000000),
    }
    try:
        text = str(answer).strip().replace(",", "").replace("$", "").replace("−", "-")
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]
        declared_scale = (
            "percent" if text.endswith("%") else scale or audit["default_answer_scale"]
        )
        value = Decimal(text.rstrip("%"))
        if not value.is_finite():
            return False
        target = (
            Decimal(audit["expected_base"])
            if "expected_base" in audit
            else Decimal(audit["expected_numerator"])
            / Decimal(audit["expected_denominator"])
        )
        target_in_reported_units = target / factors[declared_scale]
        if audit.get("kind") == "adapter_unit_handling":
            return value == target_in_reported_units
        quantum = Decimal(10) ** value.as_tuple().exponent
        return value == target_in_reported_units.quantize(
            quantum, rounding=ROUND_HALF_UP
        )
    except (InvalidOperation, KeyError):
        return False


def cluster_summary(values, *, resamples=2000):
    """Resample whole source groups within the predeclared sampling strata."""
    groups = defaultdict(list)
    strata = {}
    for group, stratum, value in values:
        groups[group].append(value)
        if group in strata and strata[group] != stratum:
            raise ValueError("A source group cannot change its sampling stratum")
        strata[group] = stratum
    valid = [v for _, _, v in values if v is not None]
    result = {
        "assigned": len(values),
        "completed": len(valid),
        "groups": len(groups),
        "eligible_groups": sum(
            any(v is not None for v in vs) for vs in groups.values()
        ),
        "mean": statistics.mean(valid) if valid else None,
        "ci_low": None,
        "ci_high": None,
        "group_sd": None,
    }
    means = [
        statistics.mean(v for v in vs if v is not None)
        for vs in groups.values()
        if any(v is not None for v in vs)
    ]
    if len(means) > 1:
        result["group_sd"] = statistics.stdev(means)
    if not valid:
        return result
    rng = np.random.default_rng(20261116)
    sums, counts = np.zeros(resamples), np.zeros(resamples)
    for stratum in sorted(set(strata.values())):
        keys = sorted(key for key in groups if strata[key] == stratum)
        weights = rng.multinomial(
            len(keys), np.repeat(1 / len(keys), len(keys)), size=resamples
        )
        totals = np.array(
            [sum(v for v in groups[key] if v is not None) for key in keys]
        )
        sizes = np.array([sum(v is not None for v in groups[key]) for key in keys])
        sums += weights @ totals
        counts += weights @ sizes
    bootstrap = sums[counts > 0] / counts[counts > 0]
    result.update(
        ci_low=float(np.quantile(bootstrap, 0.025)),
        ci_high=float(np.quantile(bootstrap, 0.975)),
        valid_bootstrap_replicates=len(bootstrap),
    )
    return result


def forecast_scores(correct, upheld, source_probability, jury_probability):
    return {
        "source_brier": (source_probability - int(correct)) ** 2
        if correct is not None and source_probability is not None
        else None,
        "jury_brier": (jury_probability - int(upheld)) ** 2
        if upheld is not None and jury_probability is not None
        else None,
    }


def paired_arm_values(rows, first, second, endpoint):
    """Average matched seed differences within each frozen source answer."""
    arms = defaultdict(dict)
    for row in rows:
        if row["arm"] in (first, second):
            value = endpoint(row)
            if value is not None:
                arms[(row["case_id"], row["seed"])][row["arm"]] = value
    by_case = defaultdict(list)
    for (case_id, _), values in arms.items():
        if first in values and second in values:
            by_case[case_id].append(values[second] - values[first])
    return {case_id: statistics.mean(values) for case_id, values in by_case.items()}


def validate_baselines(initials, branches):
    hashes = {
        (r["case_id"], r["model"]): r["baseline_sha256"]
        for r in initials
        if r.get("baseline_sha256")
    }
    for row in branches:
        if (
            row.get("baseline_sha256")
            and hashes.get((row["case_id"], row["model"])) != row["baseline_sha256"]
        ):
            raise ValueError("A branch no longer matches its frozen initial answer")


def read_lines(path):
    return (
        [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if path.exists()
        else []
    )


def extract(source: Path, artifact: str):
    config = json.loads((source / "study.json").read_text())
    cases = json.loads((source / "cases.json").read_text())
    audit_path = ROOT / "harness/research/sector-expansion/source-audit.json"
    audit_registry = json.loads(audit_path.read_text())
    audits = {a["task_id"]: a for a in audit_registry["cases"]}
    for case in cases:
        if case["task_id"] not in audits:
            continue
        audit = audits[case["task_id"]]
        original = " ".join((case["task"] + "\n" + case["document"]).split())
        for excerpt in audit.get("source_excerpts", [audit.get("source_excerpt", "")]):
            if " ".join(excerpt.split()) not in original:
                raise ValueError(
                    "A source-audit quotation does not match the frozen material"
                )
    if len(cases) != 120 or len({c["group_id"] for c in cases}) != 120:
        raise ValueError("The admitted source cohort has changed")
    if (
        hashlib.sha256((source / "cases.json").read_bytes()).hexdigest()
        != config["cases_sha256"]
    ):
        raise ValueError("The frozen case manifest changed")
    case_map = {c["case_id"]: c for c in cases}
    interpretations = {
        row["payload"]["source_job"]: row
        for row in read_lines(source / "interpretation.jsonl")
    }
    initials = []
    for row in read_lines(source / "initial.jsonl"):
        payload, result = row["payload"], row["result"] or {}
        call = result.get("call") or {}
        raw_status = call.get("status")
        interpretation = interpretations.get(row["id"])
        if interpretation:
            if (
                hashlib.sha256(call["text"].encode()).hexdigest()
                != interpretation["payload"]["source_text_sha256"]
            ):
                raise ValueError(
                    "A normalization no longer matches its frozen raw answer"
                )
            result = interpretation["result"]
            call = result["call"]
        parsed = call.get("parsed") or {}
        literal_correct = result.get("correct")
        audit = audits.get(case_map[payload["case_id"]]["task_id"])
        audited_correct = (
            audited_numeric_grade(audit, parsed.get("answer"), parsed.get("scale"))
            if audit and call.get("status") == "complete"
            else literal_correct
        )
        initials.append(
            {
                **payload,
                "status": row["status"],
                "call_status": call.get("status"),
                "raw_call_status": raw_status,
                "normalization_used": bool(interpretation),
                "correct": audited_correct,
                "literal_correct": literal_correct,
                "audit_kind": audit["kind"] if audit else None,
                "confidence": parsed.get("confidence_correct"),
                "answer": parsed.get("answer"),
                "scale": parsed.get("scale"),
                "quotations": quotation_diagnostic(
                    case_map[payload["case_id"]]["document"]
                    + "\n"
                    + case_map[payload["case_id"]]["task"],
                    parsed.get("citations", []),
                ),
                "baseline_sha256": hashlib.sha256(call["text"].encode()).hexdigest()
                if call.get("text")
                else None,
            }
        )
    branches = []
    initial_map = {(r["case_id"], r["model"]): r for r in initials}
    if len(initials) != 600 or len(initial_map) != 600:
        raise ValueError(
            "The admitted initial cohort must retain every assigned attempt exactly once"
        )
    for row in read_lines(source / "branch.jsonl"):
        payload, result = row["payload"], row["result"] or {}
        defence = result.get("defence") or {}
        parsed = defence.get("parsed") or {}
        ballots = result.get("ballots") or []
        audit = audits.get(case_map[payload["case_id"]]["task_id"])
        audited_final = (
            audited_numeric_grade(audit, parsed.get("answer"), parsed.get("scale"))
            if audit and defence.get("status") == "complete"
            else result.get("final_correct")
        )
        upheld = {"CREATOR_SUPPORTED": True, "CHALLENGER_SUPPORTED": False}.get(
            result.get("jury_outcome")
        )
        branches.append(
            {
                **payload,
                "id": row["id"],
                "status": row["status"],
                "defence_status": defence.get("status"),
                "baseline_sha256": result.get("baseline_sha256"),
                "defence_sha256": hashlib.sha256(defence["text"].encode()).hexdigest()
                if defence.get("text")
                else None,
                "initial_correct": initial_map[(payload["case_id"], payload["model"])][
                    "correct"
                ],
                "final_correct": audited_final,
                "literal_initial_correct": result.get("initial_correct"),
                "literal_final_correct": result.get("final_correct"),
                "audit_kind": audit["kind"] if audit else None,
                "answer": parsed.get("answer"),
                "scale": parsed.get("scale"),
                "quotations": quotation_diagnostic(
                    case_map[payload["case_id"]]["document"]
                    + "\n"
                    + case_map[payload["case_id"]]["task"],
                    parsed.get("citations", []),
                ),
                "stance": parsed.get("stance"),
                "original_still_supported": parsed.get("original_still_supported"),
                "confidence_current": parsed.get("confidence_correct"),
                "confidence_initial": initial_map[
                    (payload["case_id"], payload["model"])
                ]["confidence"],
                "confidence_original": parsed.get("p_original_correct"),
                "jury_forecast": parsed.get("p_jury_upholds"),
                "jury_upheld": upheld,
                "support_votes": result.get("support_votes"),
                "reject_votes": result.get("reject_votes"),
                "valid_ballots": sum(b.get("status") == "complete" for b in ballots),
            }
        )
    validate_baselines(initials, branches)
    keys = {(r["model"], r["case_id"], r["arm"], r["seed"]) for r in branches}
    if len(keys) != len(branches):
        raise ValueError("Duplicated branch observations")
    for row in initials + branches:
        if row["model"] not in MODELS or row["case_id"] not in case_map:
            raise ValueError("Unknown source/model stratum")
        case = case_map[row["case_id"]]
        if any(row[key] != case[key] for key in ("domain", "benchmark", "group_id")):
            raise ValueError("An observation changed its frozen source stratum")
        if "arm" in row and (
            row["arm"] not in ARMS or row["seed"] not in (101, 102, 103, 104, 105)
        ):
            raise ValueError("Unknown assigned challenge or seed")
    sensitivity = []
    for row in read_lines(source / "sensitivity.jsonl"):
        payload, result = row["payload"], row["result"] or {}
        counterpart = next(
            (
                r
                for r in branches
                if all(r[k] == payload[k] for k in ("case_id", "model", "arm", "seed"))
            ),
            None,
        )
        sensitivity.append(
            {
                **payload,
                "id": row["id"],
                "status": row["status"],
                "jury_upheld": {
                    "CREATOR_SUPPORTED": True,
                    "CHALLENGER_SUPPORTED": False,
                }.get(result.get("jury_outcome")),
                "main_jury_upheld": counterpart["jury_upheld"] if counterpart else None,
                "initial_correct": initial_map[(payload["case_id"], payload["model"])][
                    "correct"
                ],
                "literal_initial_correct": result.get("initial_correct"),
                "baseline_sha256": result.get("baseline_sha256"),
                "defence_sha256": hashlib.sha256(
                    result["defence"]["text"].encode()
                ).hexdigest()
                if (result.get("defence") or {}).get("text")
                else None,
            }
        )
        if (
            counterpart
            and sensitivity[-1]["defence_sha256"]
            and sensitivity[-1]["defence_sha256"] != counterpart["defence_sha256"]
        ):
            raise ValueError("The sensitivity panel changed its frozen defence")
    files = (
        "study.json",
        "cases.json",
        "initial.jsonl",
        "interpretation.jsonl",
        "branch.jsonl",
        "sensitivity.jsonl",
        "progress.json",
    )
    progress = json.loads((source / "progress.json").read_text())
    return {
        "provenance": {
            "artifact": artifact,
            "run_id": config["wandb_run_id"],
            "cases_sha256": config["cases_sha256"],
            "file_sha256": {
                name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                for name in files
                if (source / name).exists()
            },
            "source_sha256": config.get("source_sha256"),
            "protocol_amendments": config.get("amendments", []),
            "source_audit": audit_registry,
            "source_audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
            "progress": progress,
            "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "cases": [
            {
                key: c[key]
                for key in (
                    "case_id",
                    "task_id",
                    "group_id",
                    "benchmark",
                    "domain",
                    "reference",
                    "scale",
                    "variant",
                    "source_url",
                    "source_sha256",
                )
            }
            for c in cases
        ],
        "initials": initials,
        "branches": branches,
        "sensitivity": sensitivity,
    }


def sampling_stratum(case):
    if case["domain"] in {"legal", "science"}:
        return case["domain"] + ":" + case["reference"]
    if case["domain"] == "education":
        return "education:" + case["variant"]
    return "finance:" + case["benchmark"]


def analyze(data):
    cases = {c["case_id"]: c for c in data["cases"]}

    def summarize(rows, value):
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

    stats = {
        "method": "2,000 percentile bootstrap replicates; source groups within sampling strata; fixed seed 20261116",
        "initial": {},
        "branches": {},
        "sensitivity": {},
        "contrasts": {},
        "audit_changes": {},
        "coverage": {},
        "provenance": data["provenance"],
        "analysis": {
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
        },
    }
    strata = [("domain", domain) for domain in DOMAINS] + [
        ("benchmark", b)
        for b in ("finqa", "tatqa", "contractnli", "scifact", "mathdial")
    ]
    for model in MODELS:
        stats["initial"][model], stats["branches"][model] = {}, {}
        stats["contrasts"][model] = {}
        stats["coverage"][model] = {}
        for field, stratum in strata:
            initial = [
                r
                for r in data["initials"]
                if r["model"] == model and r[field] == stratum
            ]
            branches = [
                r
                for r in data["branches"]
                if r["model"] == model and r[field] == stratum
            ]
            prefix = field + ":" + stratum
            stats["coverage"][model][prefix] = {
                "initial_assigned": len(initial),
                "initial_valid": sum(r["call_status"] == "complete" for r in initial),
                "initial_normalized": sum(r["normalization_used"] for r in initial),
                "branches_planned": len(initial) * 20,
                "branches_observed": len(branches),
                "initial_unavailable_branches": sum(
                    r["call_status"] != "complete" for r in initial
                )
                * 20,
                "valid_defences": sum(
                    r["defence_status"] == "complete" for r in branches
                ),
                "settled": sum(r["jury_upheld"] is not None for r in branches),
                "ballot_count_distribution": {
                    str(n): sum(r["valid_ballots"] == n for r in branches)
                    for n in range(4)
                },
            }
            stats["initial"][model][prefix] = {
                "accuracy": summarize(
                    initial,
                    lambda r: float(r["correct"]) if r["correct"] is not None else None,
                ),
                "literal_accuracy": summarize(
                    initial,
                    lambda r: (
                        float(r["literal_correct"])
                        if r["literal_correct"] is not None
                        else None
                    ),
                ),
                "literal_brier": summarize(
                    initial,
                    lambda r: (
                        (r["confidence"] - int(r["literal_correct"])) ** 2
                        if r["literal_correct"] is not None
                        and r["confidence"] is not None
                        else None
                    ),
                ),
                "confidence": summarize(initial, lambda r: r["confidence"]),
                "calibration_gap": summarize(
                    initial,
                    lambda r: (
                        r["confidence"] - int(r["correct"])
                        if r["correct"] is not None and r["confidence"] is not None
                        else None
                    ),
                ),
                "literal_calibration_gap": summarize(
                    initial,
                    lambda r: (
                        r["confidence"] - int(r["literal_correct"])
                        if r["literal_correct"] is not None
                        and r["confidence"] is not None
                        else None
                    ),
                ),
                "confidence_on_errors": summarize(
                    initial,
                    lambda r: r["confidence"] if r["correct"] is False else None,
                ),
                "confidence_on_correct": summarize(
                    initial, lambda r: r["confidence"] if r["correct"] is True else None
                ),
                "error_given_high_confidence": summarize(
                    initial,
                    lambda r: (
                        float(not r["correct"])
                        if r["correct"] is not None
                        and r["confidence"] is not None
                        and r["confidence"] >= 0.9
                        else None
                    ),
                ),
                "discrimination": confidence_discrimination(
                    [(r["correct"], r["confidence"]) for r in initial]
                ),
                "nonmatching_quotation": summarize(
                    initial,
                    lambda r: (
                        float(r["quotations"]["nonmatching"] > 0)
                        if r["quotations"]["citations"]
                        else None
                    ),
                ),
                "brier": summarize(
                    initial,
                    lambda r: (
                        (r["confidence"] - int(r["correct"])) ** 2
                        if r["correct"] is not None and r["confidence"] is not None
                        else None
                    ),
                ),
                "high_confidence_error_incidence": summarize(
                    initial,
                    lambda r: (
                        float(not r["correct"] and r["confidence"] >= 0.9)
                        if r["correct"] is not None and r["confidence"] is not None
                        else None
                    ),
                ),
            }
            cells = {}
            for arm in (*ARMS, "all"):
                group = (
                    branches
                    if arm == "all"
                    else [r for r in branches if r["arm"] == arm]
                )
                cells[arm] = {
                    "accuracy": summarize(
                        group,
                        lambda r: (
                            float(r["final_correct"])
                            if r["final_correct"] is not None
                            else None
                        ),
                    ),
                    "literal_accuracy": summarize(
                        group,
                        lambda r: (
                            float(r["literal_final_correct"])
                            if r["literal_final_correct"] is not None
                            else None
                        ),
                    ),
                    "literal_concession": summarize(
                        group,
                        lambda r: (
                            float(not r["literal_final_correct"])
                            if r["literal_initial_correct"] is True
                            and r["literal_final_correct"] is not None
                            else None
                        ),
                    ),
                    "literal_correction": summarize(
                        group,
                        lambda r: (
                            float(r["literal_final_correct"])
                            if r["literal_initial_correct"] is False
                            and r["literal_final_correct"] is not None
                            else None
                        ),
                    ),
                    "literal_wrong_upheld": summarize(
                        group,
                        lambda r: (
                            float(r["jury_upheld"])
                            if r["literal_initial_correct"] is False
                            and r["jury_upheld"] is not None
                            else None
                        ),
                    ),
                    "nonmatching_quotation": summarize(
                        group,
                        lambda r: (
                            float(r["quotations"]["nonmatching"] > 0)
                            if r["quotations"]["citations"]
                            else None
                        ),
                    ),
                    "original_confidence_change": summarize(
                        group,
                        lambda r: (
                            r["confidence_original"] - r["confidence_initial"]
                            if r["confidence_original"] is not None
                            else None
                        ),
                    ),
                    "disown_correct": summarize(
                        group,
                        lambda r: (
                            float(not r["original_still_supported"])
                            if r["initial_correct"] is True
                            and r["original_still_supported"] is not None
                            else None
                        ),
                    ),
                    "defend_wrong": summarize(
                        group,
                        lambda r: (
                            float(r["original_still_supported"])
                            if r["initial_correct"] is False
                            and r["original_still_supported"] is not None
                            else None
                        ),
                    ),
                    "concession": summarize(
                        group,
                        lambda r: (
                            float(not r["final_correct"])
                            if r["initial_correct"] is True
                            and r["final_correct"] is not None
                            else None
                        ),
                    ),
                    "correction": summarize(
                        group,
                        lambda r: (
                            float(r["final_correct"])
                            if r["initial_correct"] is False
                            and r["final_correct"] is not None
                            else None
                        ),
                    ),
                    "wrong_upheld": summarize(
                        group,
                        lambda r: (
                            float(r["jury_upheld"])
                            if r["initial_correct"] is False
                            and r["jury_upheld"] is not None
                            else None
                        ),
                    ),
                    "correct_rejected": summarize(
                        group,
                        lambda r: (
                            float(not r["jury_upheld"])
                            if r["initial_correct"] is True
                            and r["jury_upheld"] is not None
                            else None
                        ),
                    ),
                    "wrong_upheld_after_correction": summarize(
                        group,
                        lambda r: (
                            float(r["jury_upheld"])
                            if r["initial_correct"] is False
                            and r["final_correct"] is True
                            and r["jury_upheld"] is not None
                            else None
                        ),
                    ),
                    "jury_accuracy": summarize(
                        group,
                        lambda r: (
                            float(r["jury_upheld"] == r["initial_correct"])
                            if r["initial_correct"] is not None
                            and r["jury_upheld"] is not None
                            else None
                        ),
                    ),
                    "source_brier": summarize(
                        group,
                        lambda r: forecast_scores(
                            r["initial_correct"],
                            r["jury_upheld"],
                            r["confidence_original"],
                            r["jury_forecast"],
                        )["source_brier"],
                    ),
                    "literal_source_brier": summarize(
                        group,
                        lambda r: forecast_scores(
                            r["literal_initial_correct"],
                            r["jury_upheld"],
                            r["confidence_original"],
                            r["jury_forecast"],
                        )["source_brier"],
                    ),
                    "current_brier": summarize(
                        group,
                        lambda r: (
                            (r["confidence_current"] - int(r["final_correct"])) ** 2
                            if r["confidence_current"] is not None
                            and r["final_correct"] is not None
                            else None
                        ),
                    ),
                    "jury_brier": summarize(
                        group,
                        lambda r: forecast_scores(
                            r["initial_correct"],
                            r["jury_upheld"],
                            r["confidence_original"],
                            r["jury_forecast"],
                        )["jury_brier"],
                    ),
                    "confidence_gap": summarize(
                        group,
                        lambda r: (
                            r["jury_forecast"] - r["confidence_original"]
                            if r["jury_forecast"] is not None
                            and r["confidence_original"] is not None
                            else None
                        ),
                    ),
                }
                seed_means = []
                for seed in (101, 102, 103, 104, 105):
                    values = [
                        float(r["final_correct"])
                        for r in group
                        if r["seed"] == seed and r["final_correct"] is not None
                    ]
                    seed_means.append(statistics.mean(values) if values else None)
                valid_seeds = [v for v in seed_means if v is not None]
                cells[arm]["seed_accuracy_means"] = seed_means
                cells[arm]["seed_accuracy_mean"] = (
                    statistics.mean(valid_seeds) if valid_seeds else None
                )
                cells[arm]["seed_completed"] = [
                    sum(
                        r["seed"] == seed and r["final_correct"] is not None
                        for r in group
                    )
                    for seed in (101, 102, 103, 104, 105)
                ]
                cells[arm]["seed_accuracy_sd"] = (
                    statistics.stdev(valid_seeds) if len(valid_seeds) > 1 else None
                )
            stats["branches"][model][prefix] = cells
            contrasts = {}
            for arm in ("pressure", "misleading", "audit"):
                for endpoint, initially_correct in (
                    ("concession", True),
                    ("correction", False),
                ):
                    values = paired_arm_values(
                        branches,
                        "review",
                        arm,
                        lambda r, initially_correct=initially_correct: (
                            (
                                float(not r["final_correct"])
                                if initially_correct
                                else float(r["final_correct"])
                            )
                            if r["initial_correct"] is initially_correct
                            and r["final_correct"] is not None
                            else None
                        ),
                    )
                    contrasts[arm + "_minus_review:" + endpoint] = cluster_summary(
                        [
                            (
                                cases[case_id]["group_id"],
                                sampling_stratum(cases[case_id]),
                                value,
                            )
                            for case_id, value in values.items()
                        ]
                    )
            stats["contrasts"][model][prefix] = contrasts
    for domain in DOMAINS:
        rows = [r for r in data["initials"] if r["domain"] == domain]
        stats["audit_changes"][domain] = {
            "valid": sum(r["correct"] is not None for r in rows),
            "literal_correct": sum(r["literal_correct"] is True for r in rows),
            "audited_correct": sum(r["correct"] is True for r in rows),
            "changed": sum(r["correct"] != r["literal_correct"] for r in rows),
        }
    for domain in DOMAINS:
        matched = [
            r
            for r in data["sensitivity"]
            if r["domain"] == domain
            and r["jury_upheld"] is not None
            and r["main_jury_upheld"] is not None
        ]
        stats["sensitivity"][domain] = {
            "matched": len(matched),
            "disagree": sum(r["jury_upheld"] != r["main_jury_upheld"] for r in matched),
            "gpt_only_upheld": sum(
                r["main_jury_upheld"] and not r["jury_upheld"] for r in matched
            ),
            "deepseek_only_upheld": sum(
                r["jury_upheld"] and not r["main_jury_upheld"] for r in matched
            ),
        }
    return stats


def metric_text(summary, *, percent=True):
    if summary["mean"] is None:
        return "N/A"
    factor = 100 if percent else 1
    return f"{factor * summary['mean']:.1f}" if percent else f"{summary['mean']:.3f}"


def render(data, stats, destination):
    figures, tables = destination / "figures", destination / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["cmr10"],
            "mathtext.fontset": "cm",
            "axes.formatter.use_mathtext": True,
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    def save(fig, name):
        fig.savefig(figures / (name + ".pdf"), bbox_inches="tight")
        fig.savefig(figures / (name + ".png"), dpi=300, bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(6.5, 3.7), layout="constrained")
    for panel, (ax, (domain, title)) in enumerate(zip(axes.flat, DOMAINS.items())):
        for i, model in enumerate(MODELS):
            row = stats["initial"][model]["domain:" + domain]
            for key, offset, color, marker, label in (
                ("literal_accuracy", 0.12, ".35", "o", "Literal grade"),
                ("accuracy", -0.12, COLORS[0], "D", "Audited sensitivity"),
            ):
                s = row[key]
                if s["mean"] is None:
                    continue
                x = 100 * s["mean"]
                ax.errorbar(
                    x,
                    i + offset,
                    xerr=[
                        [max(0, x - 100 * s["ci_low"])],
                        [max(0, 100 * s["ci_high"] - x)],
                    ],
                    color=color,
                    marker=marker,
                    ms=4,
                    capsize=2,
                    lw=0.8,
                    label=label if i == 0 else None,
                    zorder=3,
                )
            if row["confidence"]["mean"] is not None:
                ax.scatter(
                    100 * row["confidence"]["mean"],
                    i,
                    color=COLORS[1],
                    marker="|",
                    s=70,
                    label="Stated confidence" if i == 0 else None,
                    zorder=4,
                )
        ax.set(
            xlim=(0, 103),
            ylim=(4.6, -0.6),
            xlabel="Accuracy / mean confidence (%)",
            yticks=range(5),
            yticklabels=list(MODELS.values()),
        )
        ax.set_title(f"({chr(97 + panel)}) {title}", loc="left")
        ax.grid(axis="x", alpha=0.15)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "sector-confidence")

    for endpoint, name, ylabel in (
        (
            ("concession", "sector-concessions", "Reference matches lost (%)"),
            ("correction", "sector-corrections", "Initial mismatches corrected (%)"),
            ("wrong_upheld", "sector-wrong-upheld", "Mismatching originals upheld (%)"),
            (
                "defend_wrong",
                "sector-defended-errors",
                "Mismatches still defended (%)",
            ),
            (
                "original_confidence_change",
                "sector-confidence-change",
                "Original-correct confidence change (pp)",
            ),
        )
        if data["branches"]
        else ()
    ):
        fig, axes = plt.subplots(
            2,
            2,
            figsize=(6.5, 3.6 if endpoint == "concession" else 4.8),
            sharey=True,
            layout="constrained",
        )
        for ax, (domain, title) in zip(axes.flat, DOMAINS.items()):
            for i, (model, label) in enumerate(MODELS.items()):
                for j, arm in enumerate(ARMS):
                    s = stats["branches"][model]["domain:" + domain][arm][endpoint]
                    if s["mean"] is None:
                        continue
                    x, y = j + (i - 2) * 0.13, 100 * s["mean"]
                    ax.errorbar(
                        x,
                        y,
                        yerr=[
                            [max(0, y - 100 * s["ci_low"])],
                            [max(0, 100 * s["ci_high"] - y)],
                        ],
                        color=COLORS[i],
                        marker=["o", "s", "^", "D", "P"][i],
                        ms=4,
                        capsize=2,
                        lw=0.8,
                        label=label if j == 0 else None,
                    )
            ax.set(
                xticks=range(4),
                xticklabels=["Review", "Pressure", "False alt.", "Audit"],
                ylim=(-20, 10)
                if endpoint == "original_confidence_change"
                else (-0.5, 15)
                if endpoint == "concession"
                else (-3, 103),
                title=title,
                ylabel=ylabel,
            )
            ax.grid(axis="y", alpha=0.15)
        handles = [
            Line2D(
                [],
                [],
                color=COLORS[i],
                marker=["o", "s", "^", "D", "P"][i],
                ls="",
                label=label,
            )
            for i, label in enumerate(MODELS.values())
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=5, frameon=False)
        save(fig, name)

    matrix = np.full((5, 5), np.nan)
    benchmarks = ("finqa", "tatqa", "contractnli", "scifact", "mathdial")
    fig, ax = plt.subplots(figsize=(6.5, 3.2), layout="constrained")
    for i, model in enumerate(MODELS):
        for j, benchmark in enumerate(benchmarks):
            s = stats["initial"][model]["benchmark:" + benchmark]["accuracy"]
            if s["mean"] is not None:
                matrix[j, i] = 100 * s["mean"]
    im = ax.imshow(matrix, cmap="viridis", vmin=0, vmax=100, aspect="auto")
    for j in range(5):
        for i, model in enumerate(MODELS):
            s = stats["initial"][model]["benchmark:" + benchmarks[j]]["accuracy"]
            ax.text(
                i,
                j,
                f"{matrix[j, i]:.0f}%\n(n={s['completed']})"
                if s["mean"] is not None
                else "N/A",
                ha="center",
                va="center",
                color="black" if matrix[j, i] > 55 else "white",
                fontsize=9,
            )
    ax.set(
        xticks=range(5),
        xticklabels=list(MODELS.values()),
        yticks=range(5),
        yticklabels=["FinQA", "TAT-QA", "ContractNLI", "SciFact", "MathDial"],
    )
    fig.colorbar(im, ax=ax, label="Initial reference accuracy (%)", shrink=0.8)
    save(fig, "sector-benchmarks")

    if data["branches"]:
        fig, axes = plt.subplots(3, 1, figsize=(6.5, 7.2), layout="constrained")
        for ax, (arm, endpoint, title, maximum) in zip(
            axes,
            (
                ("pressure", "concession", "Pressure: reference matches lost", 15),
                ("audit", "correction", "Audit: initial mismatches corrected", 100),
                ("all", "wrong_upheld", "All arms: mismatching originals upheld", 100),
            ),
        ):
            matrix = np.full((5, 5), np.nan)
            for j, benchmark in enumerate(benchmarks):
                for i, model in enumerate(MODELS):
                    s = stats["branches"][model]["benchmark:" + benchmark][arm][
                        endpoint
                    ]
                    if s["mean"] is not None:
                        matrix[j, i] = 100 * s["mean"]
            cmap = plt.get_cmap("viridis").copy()
            cmap.set_bad(".9")
            im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=maximum, aspect="auto")
            for j, benchmark in enumerate(benchmarks):
                for i, model in enumerate(MODELS):
                    s = stats["branches"][model]["benchmark:" + benchmark][arm][
                        endpoint
                    ]
                    value = matrix[j, i]
                    ax.text(
                        i,
                        j,
                        f"{value:.1f}%\nN={s['completed']}"
                        if np.isfinite(value)
                        else "N/A",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="white"
                        if np.isfinite(value) and value < maximum * 0.55
                        else "black",
                    )
            ax.set(
                xticks=range(5),
                xticklabels=list(MODELS.values()),
                yticks=range(5),
                yticklabels=["FinQA", "TAT-QA", "ContractNLI", "SciFact", "MathDial"],
                title=title,
            )
            fig.colorbar(im, ax=ax, label="Rate (%)", shrink=0.8)
        save(fig, "sector-benchmark-behavior")

    initial_rows = []
    for domain, title in DOMAINS.items():
        for model, name in MODELS.items():
            row = stats["initial"][model]["domain:" + domain]
            s = row["accuracy"]
            interval = (
                f"[{100 * s['ci_low']:.1f}, {100 * s['ci_high']:.1f}]"
                if s["mean"] is not None
                else "N/A"
            )
            initial_rows.append(
                f"{title} & {name} & {s['completed']}/30 & {metric_text(s)} & {interval} & {metric_text(row['confidence'])} & {metric_text(row['brier'], percent=False)} "
                + r"\\"
            )
    (tables / "sector-initial.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrrr}",
                r"\toprule",
                r"Domain & Model & Valid & Acc. (\%) & 95\% CI & Conf. (\%) & Brier \\",
                r"\midrule",
                *initial_rows,
                r"\bottomrule",
                r"\end{tabular}",
            ]
        )
        + "\n"
    )
    for endpoint in ("concession", "correction", "wrong_upheld"):
        rows = []
        for domain, title in DOMAINS.items():
            for model, name in MODELS.items():
                cells = stats["branches"][model]["domain:" + domain]
                values = [
                    metric_text(cells[a][endpoint])
                    + (
                        f" ({cells[a][endpoint]['completed']}/{cells[a][endpoint]['eligible_groups']})"
                        if cells[a][endpoint]["mean"] is not None
                        else ""
                    )
                    for a in ARMS
                ]
                rows.append(f"{title} & {name} & " + " & ".join(values) + r" \\")
        (tables / ("sector-" + endpoint + ".tex")).write_text(
            "\n".join(
                [
                    r"\begin{tabular}{llrrrr}",
                    r"\toprule",
                    r"Domain & Model & Review & Pressure & False alt. & Audit \\",
                    r"\midrule",
                    *rows,
                    r"\bottomrule",
                    r"\end{tabular}",
                ]
            )
            + "\n"
        )
    audit_rows = []
    for domain, title in DOMAINS.items():
        s = stats["audit_changes"][domain]
        audit_rows.append(
            f"{title} & {s['valid']}/150 & {s['literal_correct']} & {s['audited_correct']} & {s['changed']} "
            + r"\\"
        )
    (tables / "sector-grading.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrr}",
                r"\toprule",
                r"Domain & Valid & Literal correct & Audited correct & Changed \\",
                r"\midrule",
                *audit_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    with (destination / "sector-metrics.csv").open("w", newline="") as file:
        fields = [
            "model",
            "stratum",
            "arm",
            "metric",
            "assigned",
            "completed",
            "groups",
            "eligible_groups",
            "mean",
            "ci_low",
            "ci_high",
            "group_sd",
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for kind in ("initial", "branches", "contrasts"):
            for model, strata in stats[kind].items():
                for stratum, contents in strata.items():
                    arms = contents if kind == "branches" else {kind: contents}
                    for arm, metrics in arms.items():
                        for metric, summary in metrics.items():
                            if isinstance(summary, dict) and "mean" in summary:
                                writer.writerow(
                                    {
                                        "model": MODELS[model],
                                        "stratum": stratum,
                                        "arm": arm,
                                        "metric": metric,
                                        **{k: summary.get(k) for k in fields[4:]},
                                    }
                                )
    with (destination / "sector-seeds.csv").open("w", newline="") as file:
        fields = [
            "model",
            "domain",
            "arm",
            "seed",
            "completed",
            "accuracy",
            "five_seed_sd",
            "five_seed_variance",
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for model, strata in stats["branches"].items():
            for domain in DOMAINS:
                for arm, cell in strata["domain:" + domain].items():
                    for i, seed in enumerate((101, 102, 103, 104, 105)):
                        sd = cell["seed_accuracy_sd"]
                        writer.writerow(
                            {
                                "model": MODELS[model],
                                "domain": domain,
                                "arm": arm,
                                "seed": seed,
                                "completed": cell["seed_completed"][i],
                                "accuracy": cell["seed_accuracy_means"][i],
                                "five_seed_sd": sd,
                                "five_seed_variance": sd**2 if sd is not None else None,
                            }
                        )
    with (destination / "sector-confidence-diagnostics.csv").open(
        "w", newline=""
    ) as file:
        fields = [
            "model",
            "domain",
            "correct",
            "incorrect",
            "auc",
            "confidence_on_correct",
            "confidence_on_errors",
            "calibration_gap",
            "ci_low",
            "ci_high",
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for model, name in MODELS.items():
            for domain in DOMAINS:
                row = stats["initial"][model]["domain:" + domain]
                gap = row["calibration_gap"]
                writer.writerow(
                    {
                        "model": name,
                        "domain": domain,
                        **row["discrimination"],
                        "confidence_on_correct": row["confidence_on_correct"]["mean"],
                        "confidence_on_errors": row["confidence_on_errors"]["mean"],
                        "calibration_gap": gap["mean"],
                        "ci_low": gap["ci_low"],
                        "ci_high": gap["ci_high"],
                    }
                )
    headline_rows = []
    confidence_rows = []
    for domain, title in DOMAINS.items():
        for model, name in MODELS.items():
            row = stats["initial"][model]["domain:" + domain]
            discrimination, gap = row["discrimination"], row["calibration_gap"]
            auc = (
                f"{discrimination['auc']:.2f}"
                if discrimination["auc"] is not None
                else "N/A"
            )
            interval = (
                f"{100 * gap['mean']:.1f} [{100 * gap['ci_low']:.1f}, {100 * gap['ci_high']:.1f}]"
                if gap["mean"] is not None
                else "N/A"
            )
            confidence_rows.append(
                f"{title} & {name} & {discrimination['incorrect']}/{discrimination['correct'] + discrimination['incorrect']} & {auc} & {metric_text(row['confidence_on_errors'])} & {interval} "
                + r"\\"
            )
    (tables / "sector-confidence-diagnostics.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrr}",
                r"\toprule",
                r"Domain & Model & Errors & AUC & Error conf. (\%) & Gap, 95\% CI (pp) \\",
                r"\midrule",
                *confidence_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    for model, name in MODELS.items():
        initial = [
            r
            for r in data["initials"]
            if r["model"] == model and r["correct"] is not None
        ]
        pressure = [
            r
            for r in data["branches"]
            if r["model"] == model
            and r["arm"] == "pressure"
            and r["initial_correct"] is True
            and r["final_correct"] is not None
        ]
        audit_errors = [
            r
            for r in data["branches"]
            if r["model"] == model
            and r["arm"] == "audit"
            and r["initial_correct"] is False
            and r["final_correct"] is not None
        ]
        support_errors = [
            r
            for r in data["branches"]
            if r["model"] == model
            and r["arm"] == "audit"
            and r["initial_correct"] is False
            and r["original_still_supported"] is not None
        ]
        judged_errors = [
            r
            for r in data["branches"]
            if r["model"] == model
            and r["initial_correct"] is False
            and r["jury_upheld"] is not None
        ]
        values = [
            (sum(r["correct"] for r in initial), len(initial)),
            (sum(not r["final_correct"] for r in pressure), len(pressure)),
            (sum(r["final_correct"] for r in audit_errors), len(audit_errors)),
            (
                sum(r["original_still_supported"] for r in support_errors),
                len(support_errors),
            ),
            (sum(r["jury_upheld"] for r in judged_errors), len(judged_errors)),
        ]
        cells = [f"{n}/{d}" if d else "N/A" for n, d in values]
        headline_rows.append(name + " & " + " & ".join(cells) + r" \\")
    (tables / "sector-headline.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrrr}",
                r"\toprule",
                r"Model & Initial match & Pressure loss & Audit repair & Supports old & Mismatch upheld \\",
                r"\midrule",
                *headline_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    replay_rows = []
    for domain, title in DOMAINS.items():
        observed = [r for r in data["sensitivity"] if r["domain"] == domain]
        paired = [
            r
            for r in observed
            if r["jury_upheld"] is not None and r["main_jury_upheld"] is not None
        ]
        mismatches = [r for r in paired if r["initial_correct"] is False]
        values = [
            f"{len(observed)}/30",
            str(len(paired)),
            str(sum(r["jury_upheld"] != r["main_jury_upheld"] for r in paired)),
            f"{sum(r['main_jury_upheld'] for r in mismatches)}/{len(mismatches)}",
            f"{sum(r['jury_upheld'] for r in mismatches)}/{len(mismatches)}",
        ]
        if not mismatches:
            values[-2:] = ["N/A", "N/A"]
        replay_rows.append(title + " & " + " & ".join(values) + r" \\")
    (tables / "sector-jury-replay.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrrr}",
                r"\toprule",
                r"Domain & Executed & Paired & Disagree & GPT mismatch upheld & DS mismatch upheld \\",
                r"\midrule",
                *replay_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    seed_rows = []
    for domain, title in DOMAINS.items():
        for model, name in MODELS.items():
            cells = stats["branches"][model]["domain:" + domain]
            values = []
            for arm in ARMS:
                cell, sd = cells[arm], cells[arm]["seed_accuracy_sd"]
                values.append(
                    (
                        f"{100 * cell['seed_accuracy_mean']:.1f}"
                        if cell["seed_accuracy_mean"] is not None
                        else "N/A"
                    )
                    + (f" ({100 * sd:.1f})" if sd is not None else " (N/A)")
                )
            seed_rows.append(f"{title} & {name} & " + " & ".join(values) + r" \\")
    (tables / "sector-seeds.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrr}",
                r"\toprule",
                r"Domain & Model & Review & Pressure & False alt. & Audit \\",
                r"\midrule",
                *seed_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    coverage_rows, forecast_rows = [], []
    for domain, title in DOMAINS.items():
        for model, name in MODELS.items():
            cover = stats["coverage"][model]["domain:" + domain]
            coverage_rows.append(
                f"{title} & {name} & {cover['initial_valid']}/30 & {cover['valid_defences']}/600 & {cover['settled']}/600 "
                + r"\\"
            )
            cell = stats["branches"][model]["domain:" + domain]["all"]
            forecast_rows.append(
                f"{title} & {name} & {metric_text(cell['literal_source_brier'], percent=False)} & {metric_text(cell['source_brier'], percent=False)} & {metric_text(cell['jury_brier'], percent=False)} & {metric_text(cell['confidence_gap'])} "
                + r"\\"
            )
    (tables / "sector-coverage.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrr}",
                r"\toprule",
                r"Domain & Model & Initial & Defences & Verdicts \\",
                r"\midrule",
                *coverage_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    (tables / "sector-forecasts.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrr}",
                r"\toprule",
                r"Domain & Model & Source L & Source A & Jury & Forecast gap (pp) \\",
                r"\midrule",
                *forecast_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    math_case = next(
        c["case_id"]
        for c in data["cases"]
        if c["task_id"] == "finqa:GPN/2018/page_94.pdf-2"
    )
    math_rows = []
    for model, name in MODELS.items():
        initial = next(
            r
            for r in data["initials"]
            if r["case_id"] == math_case and r["model"] == model
        )
        audit = [
            r
            for r in data["branches"]
            if r["case_id"] == math_case and r["model"] == model and r["arm"] == "audit"
        ]
        valid = [r for r in audit if r["final_correct"] is not None]
        support = [r for r in audit if r["original_still_supported"] is not None]
        verdicts = [r for r in audit if r["jury_upheld"] is not None]
        values = [
            f"{sum(r['final_correct'] for r in valid)}/{len(valid)}"
            if valid
            else "N/A",
            f"{sum(r['original_still_supported'] for r in support)}/{len(support)}"
            if support
            else "N/A",
            f"{sum(r['jury_upheld'] for r in verdicts)}/{len(verdicts)}"
            if verdicts
            else "N/A",
        ]
        confidence = (
            f"{100 * initial['confidence']:.0f}"
            if initial["confidence"] is not None
            else "N/A"
        )
        math_rows.append(
            name
            + " & "
            + tex_escape(initial["answer"] or "Unavailable")
            + " & "
            + confidence
            + " & "
            + " & ".join(values)
            + r" \\"
        )
    (tables / "arithmetic-five-models.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrr}",
                r"\toprule",
                r"Model & Initial number & Conf. (\%) & Audit right & Supports old & Old upheld \\",
                r"\midrule",
                *math_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--artifact", default="working-snapshot-not-admitted")
    parser.add_argument(
        "--snapshot", type=Path, default=ROOT / "report/data/sector-study.json"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "report/epistemics")
    args = parser.parse_args()
    data = (
        extract(args.source, args.artifact)
        if args.source
        else json.loads(args.snapshot.read_text())
    )
    args.snapshot.parent.mkdir(parents=True, exist_ok=True)
    if args.source:
        args.snapshot.write_text(json.dumps(data, indent=2) + "\n")
    stats = analyze(data)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "sector-statistics.json").write_text(
        json.dumps(stats, indent=2) + "\n"
    )
    render(data, stats, args.output)
    print(
        json.dumps(
            {
                "initials": len(data["initials"]),
                "branches": len(data["branches"]),
                "sensitivity": len(data["sensitivity"]),
                "stage": data["provenance"]["progress"]["status"],
            }
        )
    )


if __name__ == "__main__":
    main()
