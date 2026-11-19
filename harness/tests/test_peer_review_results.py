"""Admission and pairing tests for the separately reported extensions."""

import copy
import hashlib
import importlib.util
import json
import sys
from itertools import product
from pathlib import Path
from types import SimpleNamespace

import pytest

MODULE = Path(__file__).resolve().parents[2] / "report/analysis/peer_review_results.py"
SPEC = importlib.util.spec_from_file_location("peer_review_results", MODULE)
assert SPEC is not None and SPEC.loader is not None
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


def parent_and_revision():
    parent = {
        "cases": [
            {
                "case_id": "c",
                "task_id": "t",
                "group_id": "g",
                "benchmark": "finqa",
                "domain": "finance",
            }
        ],
        "initials": [
            {
                "case_id": "c",
                "model": "m",
                "correct": True,
                "literal_correct": False,
                "baseline_sha256": "same",
            }
        ],
        "branches": [
            {
                "case_id": "c",
                "model": "m",
                "seed": 101,
                "arm": "misleading",
                "baseline_sha256": "same",
                "defence_status": "complete",
                "final_correct": True,
                "literal_final_correct": False,
                "original_still_supported": True,
                "jury_upheld": True,
                "stance": "maintain",
            }
        ],
    }
    branch = {
        "id": "new",
        "kind": "branch",
        "status": "complete",
        "payload": {
            "case_id": "c",
            "model": "m",
            "seed": 101,
            "arm": "misleading",
            "group_id": "g",
            "benchmark": "finqa",
            "domain": "finance",
            "jury_model": "@cf/openai/gpt-oss-120b",
            "identity_namespace": ANALYSIS.REVISION_PROTOCOL,
            "challenge_sha256": hashlib.sha256(b"frozen objection").hexdigest(),
        },
        "result": {
            "status": "complete",
            "challenge": "frozen objection",
            "baseline_sha256": "same",
            "final_correct": False,
            "defence": {
                "status": "complete",
                "parsed": {
                    "answer": "1",
                    "scale": "",
                    "stance": "retract",
                    "original_still_supported": False,
                },
            },
            "jury_outcome": "CHALLENGER_SUPPORTED",
        },
    }
    assigned = [
        {
            "case_id": "c",
            "model": "m",
            "status": "supported",
            "seeds": [101, 102],
            "challenge": "frozen objection",
        }
    ]
    return parent, branch, assigned


def test_pairing_keeps_unavailable_seed_and_distinct_grade_targets():
    parent, branch, assigned = parent_and_revision()
    rows = ANALYSIS.revision_pairs(parent, [branch], assigned, {})
    assert len(rows) == 2
    first, missing = rows
    assert ANALYSIS.endpoint(first["legacy"], "loss", "audited") == 0
    assert ANALYSIS.endpoint(first["revised"], "loss", "audited") == 1
    assert ANALYSIS.endpoint(first["legacy"], "repair", "literal") == 0
    assert ANALYSIS.endpoint(first["revised"], "repair", "literal") == 0
    assert ANALYSIS.endpoint(missing["revised"], "loss", "audited") is None
    assert ANALYSIS.endpoint(missing["revised"], "valid_defence", "audited") == 0
    assert ANALYSIS.endpoint(first["revised"], "jury_upheld", "audited") == 0
    assert ANALYSIS.endpoint(first["revised"], "supports_original", "audited") == 0


def test_changed_original_or_duplicate_branch_rejects_admission():
    parent, branch, assigned = parent_and_revision()
    branch["result"]["baseline_sha256"] = "changed"
    with pytest.raises(ValueError, match="frozen original"):
        ANALYSIS.revision_pairs(parent, [branch], assigned, {})
    branch["result"]["baseline_sha256"] = "same"
    with pytest.raises(ValueError, match="Duplicate"):
        ANALYSIS.revision_pairs(parent, [branch, branch], assigned, {})


def test_paired_estimand_weights_sources_and_drops_only_unmatched_outcomes():
    rows = [
        {"group_id": "a", "old": 0, "new": 1},
        {"group_id": "a", "old": 0, "new": 1},
        {"group_id": "a", "old": 0, "new": 1},
        {"group_id": "b", "old": 1, "new": 1},
        {"group_id": "b", "old": None, "new": 0},
    ]
    values, pairs = ANALYSIS.paired_source_values(
        rows, lambda r: r["old"], lambda r: r["new"], stratum=lambda r: "one"
    )
    assert values == [("a", "one", 1), ("b", "one", 0)]
    assert len(pairs) == 4


def test_judge_false_claim_and_true_control_have_opposite_correct_verdicts():
    sources = [
        {
            "case": {"task_id": task, "group_id": task, "benchmark": "finqa", "domain": "finance"},
            "branch": {"id": task, "result": {"initial_correct": right}},
            "historical_trigger_source": False,
        }
        for task, right in [("false", False), ("true", True)]
    ]
    observations = [
        {
            "id": task,
            "kind": "judge-extension",
            "status": "complete",
            "payload": {
                "task_id": task,
                "model": "j",
                "condition": "claim_only",
                "seed": 101,
                "juror": 0,
                "original_correct": right,
                "branch_id": task,
                "group_id": task,
                "benchmark": "finqa",
                "domain": "finance",
                "historical_trigger_source": False,
            },
            "result": {"status": "complete", "parsed": {"verdict": "CREATOR_SUPPORTED"}},
        }
        for task, right in [("false", False), ("true", True)]
    ]
    rows = ANALYSIS.judge_records(sources, observations, ["j"], [101], jurors=[0])
    claim_rows = {row["task_id"]: row for row in rows if row["condition"] == "claim_only"}
    assert claim_rows["false"]["correct"] is False
    assert claim_rows["true"]["correct"] is True
    assert all(row["correct"] is None for row in rows if row["condition"] != "claim_only")
    with pytest.raises(ValueError, match="Duplicate"):
        ANALYSIS.judge_records(sources, observations * 2, ["j"], [101], jurors=[0])


@pytest.mark.parametrize(
    "field,value",
    [
        ("arm", "review"),
        ("identity_namespace", "other"),
        ("group_id", "other"),
        ("challenge_sha256", "changed"),
    ],
)
def test_revision_rejects_relabelled_source_or_objection(field, value):
    parent, branch, assignments = parent_and_revision()
    branch["payload"][field] = value
    with pytest.raises(ValueError, match="payload|objection"):
        ANALYSIS.revision_pairs(parent, [branch], assignments, {})


def test_failed_journal_row_cannot_supply_successful_result():
    parent, branch, assignments = parent_and_revision()
    branch["status"] = "failed"
    with pytest.raises(ValueError, match="Journal status"):
        ANALYSIS.revision_pairs(parent, [branch], assignments, {})


def complete_design():
    cases = [
        {"case_id": f"c{i}", "domain": "finance" if i < 30 else "education"} for i in range(60)
    ]
    assignments = [
        {
            "case_id": case["case_id"],
            "model": model,
            "status": "supported",
            "challenge": "frozen",
            "seeds": [101, 102, 103, 104, 105],
        }
        for case in cases
        for model in ANALYSIS.MODEL_IDS
    ]
    sources = [
        {
            "case": {"group_id": f"g{i}"},
            "branch": {"id": f"b{i}"},
            "operator_check_original_correct": i >= 4,
        }
        for i in range(8)
    ]
    revision = {
        "protocol": ANALYSIS.REVISION_PROTOCOL,
        "models": list(ANALYSIS.MODEL_IDS),
        "jury_model": "@cf/openai/gpt-oss-120b",
        "seeds": [101, 102, 103, 104, 105],
        "arms": ["misleading"],
        "assigned_branches": 1500,
    }
    judges = {
        "protocol": "numeric-judge-context-v1",
        "judges": list(ANALYSIS.JUDGE_IDS),
        "conditions": ["claim_only", "defended", "checked_evidence"],
        "seeds": [101, 102, 103, 104, 105],
        "jurors": [1, 2, 3],
        "planned_calls": 720,
        "selected_branches": [f"b{i}" for i in range(8)],
    }
    return {"cases": cases}, revision, assignments, judges, sources


@pytest.mark.parametrize(
    "kind,field,value",
    [
        ("revision", "models", ["other"]),
        ("revision", "seeds", [101]),
        ("revision", "arms", ["review"]),
        ("revision", "assigned_branches", 1499),
        ("judge", "conditions", ["claim_only"]),
        ("judge", "jurors", [0, 1, 2]),
        ("judge", "planned_calls", 719),
        ("judge", "selected_branches", ["changed"]),
    ],
)
def test_changed_prospective_design_is_rejected(kind, field, value):
    parent, revision, assignments, judges, sources = complete_design()
    ANALYSIS.validate_design(parent, revision, assignments, judges, sources)
    (revision if kind == "revision" else judges)[field] = value
    with pytest.raises(ValueError, match="design|sources"):
        ANALYSIS.validate_design(parent, revision, assignments, judges, sources)


def test_duplicate_or_changed_assignment_seeds_rejected():
    parent, revision, assignments, judges, sources = complete_design()
    assignments[-1] = copy.deepcopy(assignments[0])
    with pytest.raises(ValueError, match="Duplicate"):
        ANALYSIS.validate_design(parent, revision, assignments, judges, sources)
    parent, revision, assignments, judges, sources = complete_design()
    assignments[0]["seeds"] = [101]
    with pytest.raises(ValueError, match="assignments"):
        ANALYSIS.validate_design(parent, revision, assignments, judges, sources)


def artifact_fixture(tmp_path):
    revision, judge = tmp_path / "revision", tmp_path / "judge"
    (revision / "source").mkdir(parents=True)
    judge.mkdir()
    for directory, names, run in (
        (
            revision,
            (
                "study.json",
                "cases.json",
                "progress.json",
                "branch.jsonl",
                "source/assignments.json",
            ),
            "revision-run",
        ),
        (judge, ("study.json", "progress.json", "sources.json", "observations.jsonl"), "judge-run"),
    ):
        for name in names:
            (directory / name).write_text(json.dumps({"wandb_run_id": run}))
    files = {
        kind: {
            str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob("*")
            if path.is_file()
        }
        for kind, directory in (("revision", revision), ("judge", judge))
    }
    archive_sha = "a" * 64
    register = tmp_path / "evidence-register.json"
    register.write_text(
        json.dumps(
            {
                "status": "validated",
                "protocol": ANALYSIS.REVISION_PROTOCOL,
                "run_id": "revision-run",
                "assigned_branches": 1500,
                "archive_sha256": archive_sha,
                "input_sha256": files["revision"],
            }
        )
    )
    admission = {
        "schema": "peer-review-admission-v1",
        "status": "verified",
        "parent_artifact": ANALYSIS.PARENT_ARTIFACT,
        "parent_digest": ANALYSIS.PARENT_DIGEST,
        "artifacts": {
            kind: {
                "artifact": f"lbxa-corp/apart-epistemics-sprint/{kind}:v1",
                "digest": "0" * 32,
                "run_id": f"{kind}-run",
                "files": files.get(
                    kind,
                    {
                        "evidence-register.json": hashlib.sha256(register.read_bytes()).hexdigest(),
                        "executed-evidence.tar.gz": archive_sha,
                    },
                ),
            }
            for kind in ("revision", "judge", "execution_evidence")
        },
    }
    path = tmp_path / "admission.json"
    path.write_text(json.dumps(admission))
    return path, revision, judge, register


@pytest.mark.parametrize(
    "kind,name",
    [
        ("revision", "study.json"),
        ("revision", "cases.json"),
        ("revision", "branch.jsonl"),
        ("revision", "source/assignments.json"),
        ("judge", "sources.json"),
        ("judge", "observations.jsonl"),
    ],
)
def test_file_changed_after_api_verified_admission_is_rejected(tmp_path, kind, name):
    path, revision, judge, register = artifact_fixture(tmp_path)
    ANALYSIS.verify_admission(path, revision, judge, register)
    ((revision if kind == "revision" else judge) / name).write_text("changed")
    with pytest.raises(ValueError, match="artifact file hash mismatch"):
        ANALYSIS.verify_admission(path, revision, judge, register)


def test_execution_register_must_match_verified_artifact(tmp_path):
    path, revision, judge, register = artifact_fixture(tmp_path)
    register.write_text("changed")
    with pytest.raises(ValueError, match="Executed evidence register"):
        ANALYSIS.verify_admission(path, revision, judge, register)


@pytest.mark.parametrize(
    "field,value",
    [
        ("branch_id", "other"),
        ("group_id", "other"),
        ("benchmark", "mathdial"),
        ("domain", "education"),
        ("historical_trigger_source", True),
    ],
)
def test_judge_relabelled_source_is_rejected(field, value):
    source = {
        "case": {"task_id": "t", "group_id": "g", "benchmark": "finqa", "domain": "finance"},
        "branch": {"id": "b", "result": {"initial_correct": False}},
        "operator_check_original_correct": False,
        "historical_trigger_source": False,
    }
    observation = {
        "id": "call",
        "kind": "judge-extension",
        "status": "complete",
        "payload": {
            "task_id": "t",
            "branch_id": "b",
            "group_id": "g",
            "benchmark": "finqa",
            "domain": "finance",
            "original_correct": False,
            "historical_trigger_source": False,
            "model": "j",
            "condition": "claim_only",
            "seed": 101,
            "juror": 1,
        },
        "result": {"status": "complete", "parsed": {"verdict": "CHALLENGER_SUPPORTED"}},
    }
    ANALYSIS.judge_records([source], [observation], ["j"], [101], jurors=[1])
    observation["payload"][field] = value
    with pytest.raises(ValueError, match="selected source identity"):
        ANALYSIS.judge_records([source], [observation], ["j"], [101], jurors=[1])


def test_complete_judge_result_must_contain_valid_verdict():
    source = {
        "case": {"task_id": "t", "group_id": "g", "benchmark": "finqa", "domain": "finance"},
        "branch": {"id": "b", "result": {"initial_correct": False}},
        "historical_trigger_source": False,
    }
    observation = {
        "kind": "judge-extension",
        "status": "complete",
        "payload": {
            "task_id": "t",
            "branch_id": "b",
            "group_id": "g",
            "benchmark": "finqa",
            "domain": "finance",
            "original_correct": False,
            "historical_trigger_source": False,
            "model": "j",
            "condition": "claim_only",
            "seed": 101,
            "juror": 1,
        },
        "result": {"status": "complete", "parsed": {"verdict": "UNKNOWN"}},
    }
    with pytest.raises(ValueError, match="valid binary verdict"):
        ANALYSIS.judge_records([source], [observation], ["j"], [101], jurors=[1])


def test_revision_bootstrap_reuses_education_variant_strata(monkeypatch):
    strata_seen = set()

    def retained_policy(case):
        return "education:" + case["variant"]

    def collect_strata(values):
        strata_seen.update(stratum for _, stratum, _ in values)
        return {}

    monkeypatch.setitem(
        sys.modules,
        "sector_results",
        SimpleNamespace(sampling_stratum=retained_policy, cluster_summary=collect_strata),
    )
    rows = [
        {
            "group_id": variant,
            "model": "m",
            "domain": "education",
            "benchmark": "mathdial",
            "variant": variant,
            "assignment_status": "supported",
            "legacy": {"defence_status": "complete"},
            "revised": {"defence_status": "complete"},
        }
        for variant in ("original_incorrect_working", "correct_working_control")
    ]
    ANALYSIS.analyze_revision(rows)
    assert strata_seen == {
        "education:original_incorrect_working",
        "education:correct_working_control",
    }


def test_missing_outcome_bounds_equal_exhaustive_possible_completions():
    rows = [
        {"group_id": "a", "old": 0, "new": None},
        {"group_id": "a", "old": None, "new": 1},
        {"group_id": "b", "old": None, "new": None},
    ]
    bounds = ANALYSIS.missing_outcome_bounds(rows, lambda r: r["old"], lambda r: r["new"])
    missing = [
        (index, key) for index, row in enumerate(rows) for key in ("old", "new") if row[key] is None
    ]
    complete_means = []
    for outcomes in product((0, 1), repeat=len(missing)):
        completed = copy.deepcopy(rows)
        for (index, key), value in zip(missing, outcomes, strict=True):
            completed[index][key] = value
        source_means = [
            sum(row["new"] - row["old"] for row in completed if row["group_id"] == group)
            / sum(row["group_id"] == group for row in completed)
            for group in ("a", "b")
        ]
        complete_means.append(sum(source_means) / 2)
    assert bounds["low"] == min(complete_means)
    assert bounds["high"] == max(complete_means)
    assert bounds["groups"] == 2
    assert bounds["assigned_pairs"] == 3
    assert bounds["missing_pairs"] == 3
    assert rows[0]["new"] is None


def test_complete_outcome_bounds_collapse_to_observed_source_mean():
    rows = [
        {"group_id": "a", "old": 1, "new": 0},
        {"group_id": "a", "old": 0, "new": 0},
        {"group_id": "b", "old": 0, "new": 1},
    ]
    bounds = ANALYSIS.missing_outcome_bounds(rows, lambda r: r["old"], lambda r: r["new"])
    assert bounds["low"] == bounds["high"] == 0.25
    assert bounds["missing_pairs"] == 0
