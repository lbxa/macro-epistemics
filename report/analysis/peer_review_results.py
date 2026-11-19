"""Paired offline analysis of the separately collected peer-review extensions."""

import argparse
import hashlib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = ("claim_only", "defended", "checked_evidence")
PARENT_ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128"
PARENT_DIGEST = "7d7230ca4d18fc07c1bb8e0009cdbc1d"
PARENT_SNAPSHOT_SHA256 = (
    "c44d7a3f3963941a0eb661c4a01832005c1742713aaade8b2aeba347d56883f6"
)
MODEL_IDS = (
    "@cf/deepseek-ai/deepseek-v4-pro-0813",
    "@cf/zai-org/glm-5.3",
    "@cf/moonshotai/kimi-k2.6",
    "@cf/openai/gpt-oss-120b",
    "@cf/thinkingmachines/inkling-2-small",
)
JUDGE_IDS = (MODEL_IDS[3], MODEL_IDS[0])
SEEDS = (101, 102, 103, 104, 105)
REVISION_PROTOCOL = "numeric-objection-v2-replication"


def validate_observation_status(row):
    """A failed journal row cannot contribute a successfully parsed judgment."""
    result = row.get("result") or {}
    if row.get("status") not in {"complete", "failed"} or (
        (row["status"] == "complete") != (result.get("status") == "complete")
    ):
        raise ValueError("Journal status disagrees with retained result status")


def verify_admission(admission_path, revision_dir, judge_dir, revision_register):
    """Bind consumed exports to the operator's API-verified immutable artifacts."""
    admission = json.loads(admission_path.read_text())
    if (
        admission.get("schema") != "peer-review-admission-v1"
        or admission.get("status") != "verified"
        or admission.get("parent_artifact") != PARENT_ARTIFACT
        or admission.get("parent_digest") != PARENT_DIGEST
        or set(admission.get("artifacts", {}))
        != {"revision", "judge", "execution_evidence"}
    ):
        raise ValueError(
            "Admission register is not the verified v128 extension selection"
        )
    artifacts = admission["artifacts"]
    for artifact in artifacts.values():
        if (
            not re.fullmatch(
                r"lbxa-corp/apart-epistemics-sprint/[^/:]+:v[0-9]+",
                artifact["artifact"],
            )
            or not re.fullmatch(r"[a-f0-9]{32}", artifact["digest"])
            or not artifact["run_id"]
            or not isinstance(artifact["files"], dict)
        ):
            raise ValueError("Admission must identify an immutable artifact and digest")
    consumed = {
        "revision": (
            revision_dir,
            (
                "study.json",
                "cases.json",
                "progress.json",
                "branch.jsonl",
                "source/assignments.json",
            ),
        ),
        "judge": (
            judge_dir,
            ("study.json", "progress.json", "sources.json", "observations.jsonl"),
        ),
    }
    for kind, (directory, names) in consumed.items():
        artifact = artifacts[kind]
        for name in names:
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != artifact[
                "files"
            ].get(name):
                raise ValueError(f"Admitted {kind} artifact file hash mismatch: {name}")
        manifest = json.loads((directory / "study.json").read_text())
        if manifest["wandb_run_id"] != artifact["run_id"]:
            raise ValueError(f"Admitted {kind} run identity differs from its manifest")
    execution = artifacts["execution_evidence"]
    if hashlib.sha256(revision_register.read_bytes()).hexdigest() != execution[
        "files"
    ].get("evidence-register.json"):
        raise ValueError(
            "Executed evidence register differs from its admitted artifact"
        )
    register = json.loads(revision_register.read_text())
    if (
        register.get("status") != "validated"
        or register.get("protocol") != REVISION_PROTOCOL
        or register.get("run_id") != artifacts["revision"]["run_id"]
        or register.get("assigned_branches") != 1500
        or register.get("archive_sha256")
        != execution["files"].get("executed-evidence.tar.gz")
    ):
        raise ValueError(
            "Executed evidence register does not validate this replication"
        )
    for name in consumed["revision"][1]:
        if (
            register.get("input_sha256", {}).get(name)
            != artifacts["revision"]["files"][name]
        ):
            raise ValueError(
                f"Executed evidence register used different raw input: {name}"
            )
    return admission


def validate_design(parent, revision_manifest, assignments, judge_manifest, sources):
    """Reject silent changes to the prospective 1500-branch/720-call schedules."""
    expected_revision = {
        "protocol": REVISION_PROTOCOL,
        "models": list(MODEL_IDS),
        "jury_model": MODEL_IDS[3],
        "seeds": list(SEEDS),
        "arms": ["misleading"],
        "assigned_branches": 1500,
    }
    if any(
        revision_manifest.get(key) != value for key, value in expected_revision.items()
    ):
        raise ValueError("Replication design differs from its prospective schedule")
    numerical = [
        case for case in parent["cases"] if case["domain"] in {"finance", "education"}
    ]
    if len(numerical) != 60 or Counter(c["domain"] for c in numerical) != {
        "finance": 30,
        "education": 30,
    }:
        raise ValueError("Replication requires the complete numerical source cohort")
    expected_pairs = {
        (case["case_id"], model) for case in numerical for model in MODEL_IDS
    }
    indexed = unique_index(assignments, lambda row: (row["case_id"], row["model"]))
    if set(indexed) != expected_pairs or any(
        a["seeds"] != list(SEEDS)
        or a["status"]
        not in {"supported", "initial_unavailable", "numeric_policy_unsupported"}
        or ((a["status"] == "supported") != isinstance(a.get("challenge"), str))
        for a in assignments
    ):
        raise ValueError(
            "Replication assignments differ from the exact 300 original slots"
        )
    expected_judge = {
        "protocol": "numeric-judge-context-v1",
        "judges": list(JUDGE_IDS),
        "conditions": list(CONDITIONS),
        "seeds": list(SEEDS),
        "jurors": [1, 2, 3],
        "planned_calls": 720,
    }
    if any(judge_manifest.get(key) != value for key, value in expected_judge.items()):
        raise ValueError("Judge design differs from its prospective schedule")
    if (
        len(sources) != 8
        or len({s["case"]["group_id"] for s in sources}) != 8
        or Counter(s["operator_check_original_correct"] for s in sources)
        != {True: 4, False: 4}
        or judge_manifest.get("selected_branches")
        != [s["branch"]["id"] for s in sources]
    ):
        raise ValueError(
            "Judge sources differ from the exact selected eight-source cohort"
        )


def unique_index(rows, key):
    """Reject repeated observations rather than silently retaining the last one."""
    indexed = {}
    for row in rows:
        identity = key(row)
        if identity in indexed:
            raise ValueError(f"Duplicate observation identity: {identity}")
        indexed[identity] = row
    return indexed


def revision_pairs(parent, branches, assignments, audits):
    """Retain every assigned seed and verify each reused original's hash."""
    cases = {case["case_id"]: case for case in parent["cases"]}
    initials = unique_index(parent["initials"], lambda r: (r["case_id"], r["model"]))
    legacy = unique_index(
        [row for row in parent["branches"] if row["arm"] == "misleading"],
        lambda r: (r["case_id"], r["model"], r["seed"]),
    )
    revised = unique_index(
        branches,
        lambda r: (
            r["payload"]["case_id"],
            r["payload"]["model"],
            r["payload"]["seed"],
        ),
    )
    scheduled = set()
    rows = []
    for assignment in assignments:
        case = cases[assignment["case_id"]]
        initial = initials[(assignment["case_id"], assignment["model"])]
        for seed in assignment["seeds"]:
            key = (assignment["case_id"], assignment["model"], seed)
            if key in scheduled:
                raise ValueError(f"Duplicate scheduled identity: {key}")
            scheduled.add(key)
            old = legacy.get(key)
            raw = revised.get(key)
            result = (raw or {}).get("result") or {}
            if raw:
                validate_observation_status(raw)
                expected_payload = {
                    "case_id": case["case_id"],
                    "model": assignment["model"],
                    "seed": seed,
                    "group_id": case["group_id"],
                    "benchmark": case["benchmark"],
                    "domain": case["domain"],
                    "arm": "misleading",
                    "jury_model": MODEL_IDS[3],
                    "identity_namespace": REVISION_PROTOCOL,
                }
                if raw.get("kind") != "branch" or any(
                    raw["payload"].get(field) != value
                    for field, value in expected_payload.items()
                ):
                    raise ValueError(
                        "Replication payload differs from its scheduled source identity"
                    )
                challenge = assignment.get("challenge")
                if challenge is not None:
                    challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()
                    if (
                        raw["payload"].get("challenge_sha256") != challenge_hash
                        or result.get("challenge") != challenge
                    ):
                        raise ValueError(
                            "Replication objection differs from its frozen assignment"
                        )
                elif raw["payload"].get("challenge_sha256") is not None:
                    raise ValueError(
                        "Unavailable assignment unexpectedly has an objection hash"
                    )
                if (
                    result.get("jury_outcome") is not None
                    and raw["status"] != "complete"
                ):
                    raise ValueError(
                        "Failed replication cannot supply a settled jury verdict"
                    )
            defence = result.get("defence") or {}
            parsed = defence.get("parsed") or {}
            for observed_hash in (
                (old or {}).get("baseline_sha256"),
                result.get("baseline_sha256"),
            ):
                if (
                    observed_hash is not None
                    and observed_hash != initial["baseline_sha256"]
                ):
                    raise ValueError("Extension differs from its frozen original")
            if defence.get("status") == "complete" and not result.get(
                "baseline_sha256"
            ):
                raise ValueError("Valid defence has no frozen original hash")
            audited_final = result.get("final_correct")
            if case["task_id"] in audits and defence.get("status") == "complete":
                from sector_results import audited_numeric_grade

                audited_final = audited_numeric_grade(
                    audits[case["task_id"]], parsed.get("answer"), parsed.get("scale")
                )
            new = {
                "status": (raw or {}).get("status", "missing"),
                "defence_status": defence.get("status"),
                "initial_correct": initial["correct"],
                "literal_initial_correct": initial["literal_correct"],
                "final_correct": audited_final
                if defence.get("status") == "complete"
                else None,
                "literal_final_correct": result.get("final_correct")
                if defence.get("status") == "complete"
                else None,
                "original_still_supported": parsed.get("original_still_supported"),
                "stance": parsed.get("stance"),
                "confidence_original": parsed.get("p_original_correct"),
                "confidence_current": parsed.get("confidence_correct"),
                "jury_forecast": parsed.get("p_jury_upholds"),
                "jury_upheld": {
                    "CREATOR_SUPPORTED": True,
                    "CHALLENGER_SUPPORTED": False,
                }.get(result.get("jury_outcome")),
            }
            rows.append(
                {
                    "case_id": case["case_id"],
                    "group_id": case["group_id"],
                    "domain": case["domain"],
                    "benchmark": case["benchmark"],
                    "variant": case.get("variant", "original"),
                    "model": assignment["model"],
                    "seed": seed,
                    "assignment_status": assignment["status"],
                    "legacy": {
                        **(old or {}),
                        "initial_correct": initial["correct"],
                        "literal_initial_correct": initial["literal_correct"],
                    },
                    "revised": new,
                }
            )
    if set(revised) - scheduled:
        raise ValueError("Extension contains unscheduled branches")
    return rows


def endpoint(row, name, grading):
    """Define endpoint eligibility separately from author stance and jury outcome."""
    if grading not in {"literal", "audited"}:
        raise ValueError("Unknown grading policy")
    if name == "valid_defence":
        return int(row.get("defence_status") == "complete")
    if name == "settled":
        return int(row.get("jury_upheld") is not None)
    if name in {"jury_upheld", "supports_original"}:
        key = "jury_upheld" if name == "jury_upheld" else "original_still_supported"
        value = row.get(key)
        return int(value) if value is not None else None
    if name in {"maintain", "qualify", "retract"}:
        stance = row.get("stance")
        return int(stance == name) if stance is not None else None
    if name in {"confidence_original", "confidence_current", "jury_forecast"}:
        return row.get(name)
    prefix = "literal_" if grading == "literal" else ""
    initial = row.get(prefix + "initial_correct")
    final = row.get(prefix + "final_correct")
    if name == "loss":
        return int(not final) if initial is True and final is not None else None
    if name == "repair":
        return int(final) if initial is False and final is not None else None
    if name == "current_match":
        return int(final) if final is not None else None
    raise ValueError(f"Unknown endpoint: {name}")


def judge_records(sources, observations, models, seeds, jurors=(1, 2, 3)):
    """Enumerate assigned standalone calls without converting failures into errors."""
    observed = unique_index(
        observations,
        lambda r: tuple(
            r["payload"][key]
            for key in ("task_id", "model", "condition", "seed", "juror")
        ),
    )
    scheduled = set()
    rows = []
    for source in sources:
        case = source["case"]
        truth = source.get(
            "operator_check_original_correct",
            source["branch"]["result"]["initial_correct"],
        )
        if not isinstance(truth, bool):
            raise TypeError("Judge source has no checked original correctness class")
        for model in models:
            for condition in CONDITIONS:
                for seed in seeds:
                    for juror in jurors:
                        key = (case["task_id"], model, condition, seed, juror)
                        if key in scheduled:
                            raise ValueError("Duplicate scheduled judge identity")
                        scheduled.add(key)
                        row = observed.get(key) or {}
                        result = row.get("result") or {}
                        parsed = result.get("parsed") or {}
                        if row:
                            validate_observation_status(row)
                            expected_payload = {
                                "branch_id": source["branch"]["id"],
                                "task_id": case["task_id"],
                                "group_id": case["group_id"],
                                "benchmark": case["benchmark"],
                                "domain": case["domain"],
                                "original_correct": truth,
                                "historical_trigger_source": source[
                                    "historical_trigger_source"
                                ],
                            }
                            if row.get("kind") != "judge-extension" or any(
                                row["payload"].get(field) != value
                                for field, value in expected_payload.items()
                            ):
                                raise ValueError(
                                    "Judge observation differs from its selected source identity"
                                )
                        verdict = (
                            parsed.get("verdict")
                            if result.get("status") == "complete"
                            else None
                        )
                        if result.get("status") == "complete" and verdict not in {
                            "CREATOR_SUPPORTED",
                            "CHALLENGER_SUPPORTED",
                        }:
                            raise ValueError(
                                "Completed judge result has no valid binary verdict"
                            )
                        upheld = {
                            "CREATOR_SUPPORTED": True,
                            "CHALLENGER_SUPPORTED": False,
                        }.get(verdict)
                        rows.append(
                            {
                                "task_id": case["task_id"],
                                "group_id": case["group_id"],
                                "benchmark": case["benchmark"],
                                "domain": case["domain"],
                                "model": model,
                                "condition": condition,
                                "seed": seed,
                                "juror": juror,
                                "original_correct": truth,
                                "historical_trigger_source": source[
                                    "historical_trigger_source"
                                ],
                                "status": row.get("status", "missing"),
                                "correct": upheld == truth
                                if upheld is not None
                                else None,
                                "upheld": upheld,
                            }
                        )
    if set(observed) - scheduled:
        raise ValueError("Judge extension contains unscheduled observations")
    return rows


def paired_source_values(rows, first, second, *, stratum):
    """Give each eligible source one paired mean, regardless of replicate count."""
    groups = defaultdict(list)
    eligible = []
    for row in rows:
        left, right = first(row), second(row)
        if left is not None and right is not None:
            groups[row["group_id"]].append((left, right))
            eligible.append((left, right))
    values = [
        (
            group,
            stratum(next(row for row in rows if row["group_id"] == group)),
            statistics.mean(right - left for left, right in pairs),
        )
        for group, pairs in groups.items()
    ]
    return values, eligible


def paired_summary(rows, first, second, *, stratum):
    """Resample source means, keeping all matched replicates within their source."""
    from sector_results import cluster_summary

    values, eligible = paired_source_values(rows, first, second, stratum=stratum)
    return {
        "assigned_pairs": len(rows),
        "eligible_pairs": len(eligible),
        "missing_or_ineligible_pairs": len(rows) - len(eligible),
        "first_positive": sum(left for left, _ in eligible),
        "second_positive": sum(right for _, right in eligible),
        "first_pooled_rate": statistics.mean(left for left, _ in eligible)
        if eligible
        else None,
        "second_pooled_rate": statistics.mean(right for _, right in eligible)
        if eligible
        else None,
        "source_mean_difference": cluster_summary(values),
    }


def missing_outcome_bounds(rows, first, second):
    """Sharp source-mean bounds with observed binary outcomes held fixed.

    Missing outcomes range over zero and one. These deterministic bounds
    describe the complete assigned cohort and are not confidence intervals.
    """
    groups = defaultdict(list)
    missing_pairs = 0
    for row in rows:
        left, right = first(row), second(row)
        if any(value is not None and value not in (0, 1) for value in (left, right)):
            raise ValueError("Missing-outcome bounds require binary outcomes")
        missing_pairs += left is None or right is None
        lower = (0 if right is None else right) - (1 if left is None else left)
        upper = (1 if right is None else right) - (0 if left is None else left)
        groups[row["group_id"]].append((lower, upper))
    return {
        "low": statistics.mean(
            statistics.mean(low for low, _ in values) for values in groups.values()
        )
        if groups
        else None,
        "high": statistics.mean(
            statistics.mean(high for _, high in values) for values in groups.values()
        )
        if groups
        else None,
        "groups": len(groups),
        "assigned_pairs": len(rows),
        "missing_pairs": missing_pairs,
    }


def analyze_revision(rows):
    from sector_results import sampling_stratum

    endpoints = (
        "valid_defence",
        "settled",
        "current_match",
        "loss",
        "repair",
        "supports_original",
        "jury_upheld",
        "maintain",
        "qualify",
        "retract",
        "confidence_original",
        "confidence_current",
        "jury_forecast",
    )
    result = []
    for model in sorted({row["model"] for row in rows}):
        for domain in ("all", *sorted({row["domain"] for row in rows})):
            selected = [
                r
                for r in rows
                if r["model"] == model and (domain == "all" or r["domain"] == domain)
            ]
            for grading in ("literal", "audited"):
                result.append(
                    {
                        "model": model,
                        "domain": domain,
                        "grading": grading,
                        "assigned": len(selected),
                        "assignment_status_counts": dict(
                            Counter(r["assignment_status"] for r in selected)
                        ),
                        "legacy_stance_counts": dict(
                            Counter(r["legacy"].get("stance") for r in selected)
                        ),
                        "revised_stance_counts": dict(
                            Counter(r["revised"].get("stance") for r in selected)
                        ),
                        "reference_transitions": {
                            cohort: dict(
                                Counter(
                                    "missing"
                                    if endpoint(r[cohort], "current_match", grading)
                                    is None
                                    else "matching_to_mismatch"
                                    if endpoint(r[cohort], "loss", grading) == 1
                                    else "mismatch_to_matching"
                                    if endpoint(r[cohort], "repair", grading) == 1
                                    else "matching_to_matching"
                                    if endpoint(r[cohort], "loss", grading) == 0
                                    else "mismatch_to_mismatch"
                                    for r in selected
                                )
                            )
                            for cohort in ("legacy", "revised")
                        },
                        "endpoints": {
                            name: paired_summary(
                                selected,
                                lambda r, n=name, g=grading: endpoint(
                                    r["legacy"], n, g
                                ),
                                lambda r, n=name, g=grading: endpoint(
                                    r["revised"], n, g
                                ),
                                stratum=sampling_stratum,
                            )
                            for name in endpoints
                        },
                    }
                )
    return result


def analyze_judges(rows):
    from sector_results import cluster_summary

    result = []
    for exclude_trigger in (False, True):
        for model in sorted({row["model"] for row in rows}):
            for truth in (False, True):
                selected = [
                    r
                    for r in rows
                    if r["model"] == model
                    and r["original_correct"] == truth
                    and not (exclude_trigger and r["historical_trigger_source"])
                ]
                indexed = {
                    (r["task_id"], r["seed"], r["juror"], r["condition"]): r
                    for r in selected
                }
                cells = []
                contrasts = []
                for condition in CONDITIONS:
                    subset = [r for r in selected if r["condition"] == condition]
                    valid = [r for r in subset if r["correct"] is not None]
                    by_source = defaultdict(list)
                    for row in valid:
                        by_source[row["group_id"]].append(row["correct"])
                    cells.append(
                        {
                            "condition": condition,
                            "assigned": len(subset),
                            "valid": len(valid),
                            "correct": sum(r["correct"] for r in valid),
                            "upheld": sum(r["upheld"] for r in valid),
                            "groups": len({r["group_id"] for r in subset}),
                            "correct_rate": statistics.mean(r["correct"] for r in valid)
                            if valid
                            else None,
                            "source_mean_correct": cluster_summary(
                                [
                                    (
                                        group,
                                        next(
                                            r["benchmark"]
                                            for r in subset
                                            if r["group_id"] == group
                                        ),
                                        statistics.mean(values),
                                    )
                                    for group, values in by_source.items()
                                ]
                            ),
                        }
                    )
                    if condition == "claim_only":
                        continue
                    paired = []
                    for row in subset:
                        baseline = indexed[
                            (row["task_id"], row["seed"], row["juror"], "claim_only")
                        ]
                        paired.append({**row, "baseline_correct": baseline["correct"]})
                    contrasts.append(
                        {
                            "condition": condition,
                            **paired_summary(
                                paired,
                                lambda r: r["baseline_correct"],
                                lambda r: r["correct"],
                                stratum=lambda r: r["benchmark"],
                            ),
                            "assigned_source_mean_difference_bounds": missing_outcome_bounds(
                                paired,
                                lambda r: r["baseline_correct"],
                                lambda r: r["correct"],
                            ),
                        }
                    )
                result.append(
                    {
                        "model": model,
                        "original_correct": truth,
                        "exclude_historical_trigger": exclude_trigger,
                        "cells": cells,
                        "contrasts": contrasts,
                    }
                )
    return result


def read_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def validate_selected_sources(parent, revision_cases, sources):
    """Keep selected judge cases and frozen branch texts tied to the parent."""
    cases = unique_index(revision_cases, lambda case: case["case_id"])
    branches = unique_index(parent["branches"], lambda row: row["id"])
    for source in sources:
        case, branch = source["case"], source["branch"]
        if cases.get(case["case_id"]) != case:
            raise ValueError(
                "Judge source differs from the admitted numerical case projection"
            )
        original = branches.get(branch["id"])
        if original is None or any(
            branch["payload"].get(key) != original[key]
            for key in (
                "case_id",
                "model",
                "seed",
                "arm",
                "group_id",
                "benchmark",
                "domain",
            )
        ):
            raise ValueError(
                "Judge source branch identity differs from its frozen parent"
            )
        result = branch.get("result") or {}
        defence = result.get("defence") or {}
        if (
            result.get("baseline_sha256") != original["baseline_sha256"]
            or hashlib.sha256(defence.get("text", "").encode()).hexdigest()
            != original["defence_sha256"]
            or result.get("initial_correct") != original["literal_initial_correct"]
            or source["operator_check_original_correct"]
            != original["literal_initial_correct"]
        ):
            raise ValueError("Judge source changes its frozen original or defence")


def extract(parent_path, revision_dir, judge_dir, admission_path, revision_register):
    """Admit completed extension exports and retain every source file hash."""
    admission = verify_admission(
        admission_path, revision_dir, judge_dir, revision_register
    )
    if hashlib.sha256(parent_path.read_bytes()).hexdigest() != PARENT_SNAPSHOT_SHA256:
        raise ValueError("Parent snapshot differs from the frozen v128 anchor")
    parent = json.loads(parent_path.read_text())
    if parent["provenance"]["artifact"] != PARENT_ARTIFACT:
        raise ValueError("Parent artifact differs from the frozen v128 anchor")
    audit = parent["provenance"]["source_audit"]
    revision_manifest = json.loads((revision_dir / "study.json").read_text())
    judge_manifest = json.loads((judge_dir / "study.json").read_text())
    for directory in (revision_dir, judge_dir):
        progress = json.loads((directory / "progress.json").read_text())
        if progress["status"] not in {"complete", "complete_with_failures"}:
            raise ValueError(
                "Only terminal completed extension exports can enter results"
            )
    if revision_manifest["parent_run_id"] != parent["provenance"]["run_id"]:
        raise ValueError("Replication parent differs from the admitted sector study")
    if revision_manifest["protocol"] != "numeric-objection-v2-replication":
        raise ValueError("Unexpected objection replication protocol")
    if judge_manifest["protocol"] != "numeric-judge-context-v1":
        raise ValueError("Unexpected judge-context protocol")
    for name, expected in revision_manifest["parent_sha256"].items():
        if (
            name in parent["provenance"]["file_sha256"]
            and expected != parent["provenance"]["file_sha256"][name]
        ):
            raise ValueError(
                "Replication parent file differs from the admitted sector study"
            )
    for name, expected in judge_manifest["parent_hashes"].items():
        if (
            name in parent["provenance"]["file_sha256"]
            and expected != parent["provenance"]["file_sha256"][name]
        ):
            raise ValueError("Judge parent file differs from the admitted sector study")
    assignments = json.loads((revision_dir / "source/assignments.json").read_text())
    sources = json.loads((judge_dir / "sources.json").read_text())
    validate_design(parent, revision_manifest, assignments, judge_manifest, sources)
    validate_selected_sources(
        parent, json.loads((revision_dir / "cases.json").read_text()), sources
    )
    revision_branches = read_lines(revision_dir / "branch.jsonl")
    judge_observations = read_lines(judge_dir / "observations.jsonl")
    if len(revision_branches) != 1500 or len(judge_observations) != 720:
        raise ValueError(
            "Completed extensions must retain every scheduled branch and call"
        )
    revision = revision_pairs(
        parent,
        revision_branches,
        assignments,
        {row["task_id"]: row for row in audit["cases"]},
    )
    if len(sources) != 8 or Counter(
        s["operator_check_original_correct"] for s in sources
    ) != {True: 4, False: 4}:
        raise ValueError(
            "Judge extension must retain four checked errors and four controls"
        )
    judges = judge_records(
        sources,
        judge_observations,
        judge_manifest["judges"],
        judge_manifest["seeds"],
        jurors=judge_manifest["jurors"],
    )
    files = [
        parent_path,
        admission_path,
        revision_register,
        *(
            revision_dir / name
            for name in (
                "study.json",
                "cases.json",
                "progress.json",
                "branch.jsonl",
                "source/assignments.json",
            )
        ),
        *(
            judge_dir / name
            for name in (
                "study.json",
                "progress.json",
                "sources.json",
                "observations.jsonl",
            )
        ),
    ]
    return {
        "provenance": {
            "parent_artifact": parent["provenance"]["artifact"],
            "parent_digest": PARENT_DIGEST,
            "admission_sha256": hashlib.sha256(admission_path.read_bytes()).hexdigest(),
            "artifacts": admission["artifacts"],
            "revision_run": revision_manifest.get("wandb_run_id"),
            "judge_run": judge_manifest.get("wandb_run_id"),
            "file_sha256": {
                str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in files
            },
            "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "uncertainty": "Pointwise 95% percentile intervals; 2000 within-stratum source-group resamples; paired replicate differences averaged within source",
            "human_adjudication_status": "pending; source-audit sensitivity is automated and post hoc",
            "scope": "Separate extensions; no frozen sector-v1 statistics overwritten; judge cases selected, not prevalence sample",
        },
        "judge_sources": [
            {
                "task_id": s["case"]["task_id"],
                "group_id": s["case"]["group_id"],
                "domain": s["case"]["domain"],
                "benchmark": s["case"]["benchmark"],
                "branch_id": s["branch"]["id"],
                "operator_check_original_correct": s["operator_check_original_correct"],
                "historical_trigger_source": s["historical_trigger_source"],
                "proof_sha256": hashlib.sha256(
                    json.dumps(s["proof"], sort_keys=True).encode()
                ).hexdigest(),
            }
            for s in sources
        ],
        "revision_rows": revision,
        "judge_rows": judges,
        "revision": analyze_revision(revision),
        "judges": analyze_judges(judges),
    }


def render(results, destination):
    """Render only new assets; never touch the frozen sector-v1 asset names."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from epistemics_pilot import tex_escape
    from sector_results import COLORS, MODELS

    figures = destination / "figures"
    tables = destination / "tables"
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

    def interval(summary):
        if summary["mean"] is None:
            return "N/A"
        return (
            f"{100 * summary['mean']:+.1f} "
            f"[{100 * summary['ci_low']:+.1f}, {100 * summary['ci_high']:+.1f}]"
        )

    # Numeric table bodies are computed data; captions are authored in the manuscript.
    revision_lines = []
    for row in results["revision"]:
        if row["domain"] != "all":
            continue
        loss, repair = (row["endpoints"][name] for name in ("loss", "repair"))
        revision_lines.append(
            f"{tex_escape(MODELS.get(row['model'], row['model']))} & {row['grading']} & "
            f"{loss['first_positive']}/{loss['eligible_pairs']} & "
            f"{loss['second_positive']}/{loss['eligible_pairs']} & "
            f"{interval(loss['source_mean_difference'])} & "
            f"{repair['first_positive']}/{repair['eligible_pairs']} & "
            f"{repair['second_positive']}/{repair['eligible_pairs']} \\\\"
        )
    (tables / "peer-review-objection-rows.tex").write_text(
        "\n".join(revision_lines) + "\n"
    )
    judge_lines = []
    for row in results["judges"]:
        cells = {cell["condition"]: cell for cell in row["cells"]}
        changes = {cell["condition"]: cell for cell in row["contrasts"]}
        counts = " & ".join(
            f"{cells[c]['correct']}/{cells[c]['valid']}" for c in CONDITIONS
        )
        judge_lines.append(
            f"{tex_escape(MODELS.get(row['model'], row['model']))} & "
            f"{'True' if row['original_correct'] else 'False'} & "
            f"{'Excluded' if row['exclude_historical_trigger'] else 'Included'} & {counts} & "
            f"{interval(changes['defended']['source_mean_difference'])} & "
            f"{interval(changes['checked_evidence']['source_mean_difference'])} \\\\"
        )
    (tables / "peer-review-judge-rows.tex").write_text("\n".join(judge_lines) + "\n")
    case_lines = []
    judge_rows = results["judge_rows"]
    for task_id in sorted({row["task_id"] for row in judge_rows}):
        for model in sorted({row["model"] for row in judge_rows}):
            selected = [
                row
                for row in judge_rows
                if row["task_id"] == task_id and row["model"] == model
            ]
            cells = []
            for condition in CONDITIONS:
                valid = [
                    row
                    for row in selected
                    if row["condition"] == condition and row["correct"] is not None
                ]
                cells.append(f"{sum(row['correct'] for row in valid)}/{len(valid)}")
            case_lines.append(
                f"{tex_escape(task_id)} & {tex_escape(MODELS.get(model, model))} & "
                f"{'True' if selected[0]['original_correct'] else 'False'} & "
                f"{'Yes' if selected[0]['historical_trigger_source'] else 'No'} & "
                + " & ".join(cells)
                + " \\\\"
            )
    (tables / "peer-review-judge-cases-rows.tex").write_text(
        "\n".join(case_lines) + "\n"
    )

    fig, axes = plt.subplots(
        2, 2, figsize=(6.5, 4.4), sharex="row", layout="constrained"
    )
    indexed = {
        (r["model"], r["domain"]): r
        for r in results["revision"]
        if r["grading"] == "audited"
    }
    for column, domain in enumerate(("finance", "education")):
        for line, metric in enumerate(("loss", "repair")):
            ax = axes[line, column]
            ax.axvline(0, color="0.55", lw=0.6)
            for index, (model, name) in enumerate(MODELS.items()):
                summary = indexed[(model, domain)]["endpoints"][metric][
                    "source_mean_difference"
                ]
                if summary["mean"] is None:
                    ax.text(
                        0.03,
                        index,
                        "N/A",
                        va="center",
                        fontsize=8,
                        transform=ax.get_yaxis_transform(),
                    )
                    continue
                x = 100 * summary["mean"]
                ax.errorbar(
                    x,
                    index,
                    xerr=[
                        [max(0, x - 100 * summary["ci_low"])],
                        [max(0, 100 * summary["ci_high"] - x)],
                    ],
                    fmt=["o", "s", "^", "D", "P"][index],
                    color=COLORS[index],
                    capsize=2,
                    ms=4,
                    lw=0.8,
                )
            ax.set_yticks(range(len(MODELS)), list(MODELS.values()))
            ax.set_ylim(len(MODELS) - 0.5, -0.5)
            ax.set_title(
                domain.capitalize()
                + (": reference loss" if metric == "loss" else ": reference repair")
            )
            ax.set_xlabel("Revised minus legacy (pp)")
            ax.grid(axis="x", alpha=0.15)
    for extension in ("pdf", "png"):
        fig.savefig(
            figures / f"peer-review-objection.{extension}",
            dpi=300,
            bbox_inches="tight",
            metadata={"CreationDate": None} if extension == "pdf" else {},
        )
    plt.close(fig)

    fig, axes = plt.subplots(
        1, 2, figsize=(6.5, 3.2), sharey=True, layout="constrained"
    )
    for ax, exclude_trigger in zip(axes, (False, True)):
        selected = [
            r
            for r in results["judges"]
            if not r["original_correct"]
            and r["exclude_historical_trigger"] == exclude_trigger
        ]
        for index, row in enumerate(selected):
            model_index = list(MODELS).index(row["model"])
            cells = {cell["condition"]: cell for cell in row["cells"]}
            for j, condition in enumerate(CONDITIONS):
                summary = cells[condition]["source_mean_correct"]
                if summary["mean"] is None:
                    continue
                y = 100 * summary["mean"]
                ax.errorbar(
                    j + (index - 0.5) * 0.1,
                    y,
                    yerr=[
                        [max(0, y - 100 * summary["ci_low"])],
                        [max(0, 100 * summary["ci_high"] - y)],
                    ],
                    fmt=["o", "s", "^", "D", "P"][model_index],
                    color=COLORS[model_index],
                    label=MODELS.get(row["model"], row["model"]) if j == 0 else None,
                    ms=4,
                    capsize=2,
                    lw=0.8,
                )
        ax.set_xticks(range(3), ["Claim only", "Defended", "Checked"])
        ax.set_title(
            "False claims: three new" if exclude_trigger else "False claims: all four"
        )
        ax.set_ylim(-4, 104)
        ax.grid(axis="y", alpha=0.15)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels, loc="lower left", frameon=False)
        else:
            ax.text(0.5, 0.5, "No valid judgments", transform=ax.transAxes, ha="center")
    axes[0].set_ylabel("Correct judgment (%)")
    for extension in ("pdf", "png"):
        fig.savefig(
            figures / f"peer-review-judge.{extension}",
            dpi=300,
            bbox_inches="tight",
            metadata={"CreationDate": None} if extension == "pdf" else {},
        )
    plt.close(fig)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--parent", type=Path, default=ROOT / "report/data/sector-study.json"
    )
    parser.add_argument("--revision", type=Path, required=True)
    parser.add_argument("--judge", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--revision-register", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assets", type=Path)
    args = parser.parse_args()
    result = extract(
        args.parent, args.revision, args.judge, args.admission, args.revision_register
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    if args.assets:
        render(result, args.assets)
