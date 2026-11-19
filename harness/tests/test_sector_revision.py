import hashlib
import json
import time
from decimal import Decimal

import pytest

from veracity_harness.runner import ROOT
from veracity_harness.sector_cases import MODELS, Answer, build_cohort
from veracity_harness.sector_revision import (
    PARENT_RUN_ID,
    PROTOCOL,
    execute_assignment,
    freeze_runtime,
    import_parent_initials,
    prepare,
    revised_challenge,
)
from veracity_harness.sector_study import SectorStudy, job_key


@pytest.mark.asyncio
async def test_explicit_objection_reuses_real_settlement_with_distinct_identity(
    tmp_path, monkeypatch
):
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)
    original = Answer(
        answer=case.reference,
        scale=case.scale,
        confidence_correct=0.9,
        explanation="Source calculation.",
        citations=(),
    ).model_dump(mode="json")
    key = job_key("initial", case.case_id, MODELS[0])
    study.journal.begin(key, "initial", {})
    study.journal.finish(
        key,
        "complete",
        {
            "call": {"status": "complete", "text": json.dumps(original), "parsed": original},
            "correct": True,
        },
    )
    observed = []

    async def invoke(model, messages, identity, seed, schema):
        observed.append((identity, "\n".join(m.content for m in messages)))
        if schema.__name__ == "Ballot":
            parsed = {"verdict": "CREATOR_SUPPORTED", "assessment": "Source supports it."}
        else:
            parsed = {
                **original,
                "stance": "maintain",
                "original_still_supported": True,
                "p_original_correct": 0.9,
                "p_jury_upholds": 0.8,
            }
        return {"status": "complete", "parsed": parsed, "text": json.dumps(parsed)}

    monkeypatch.setattr(study, "invoke", invoke)
    await study.dispute(
        case,
        MODELS[0],
        "misleading",
        101,
        challenge_override="A revised objection.",
        identity_namespace="numeric-v2",
    )
    identity = job_key("branch", "numeric-v2", case.case_id, MODELS[0], "misleading", 101)
    row = study.journal.get(identity)
    assert row["result"]["challenge"] == "A revised objection."
    assert row["result"]["jury_outcome"] == "CREATOR_SUPPORTED"
    assert all("A revised objection." in text for _, text in observed)
    assert study.journal.get(job_key("branch", case.case_id, MODELS[0], "misleading", 101)) is None
    with pytest.raises(ValueError, match="explicit objection"):
        await study.dispute(
            case,
            MODELS[0],
            "misleading",
            101,
            challenge_override="Changed after collection.",
            identity_namespace="numeric-v2",
        )


def test_revised_prompt_uses_public_answer_with_reference_only_as_veto():
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    answer = Answer(
        answer="100", scale="", confidence_correct=0.9, explanation="Saved response.", citations=()
    )
    first = revised_challenge(case.model_copy(update={"reference": "40"}), answer)
    second = revised_challenge(case.model_copy(update={"reference": "80"}), answer)
    assert first == second
    assert "125" in first
    assert "reference" not in first.lower()
    assert PROTOCOL not in first


def test_preparation_retains_missing_and_nonscalar_assignments(tmp_path, monkeypatch):
    cases = tuple(c for c in build_cohort(ROOT / "tasks/veracity_tasks.sqlite") if not c.labels)
    (tmp_path / "cases.json").write_text(json.dumps([c.model_dump(mode="json") for c in cases]))
    (tmp_path / "progress.json").write_text(json.dumps({"status": "complete_with_failures"}))
    (tmp_path / "study.json").write_text(
        json.dumps(
            {
                "cases_sha256": hashlib.sha256((tmp_path / "cases.json").read_bytes()).hexdigest(),
                "wandb_run_id": PARENT_RUN_ID,
            }
        )
    )
    initial = []
    for case in cases:
        for model in MODELS:
            answer = Answer(
                answer=case.reference,
                scale=case.scale,
                confidence_correct=0.9,
                explanation="Saved.",
                citations=(),
            ).model_dump(mode="json")
            initial.append(
                {
                    "id": job_key("initial", case.case_id, model),
                    "status": "complete",
                    "payload": {"case_id": case.case_id, "model": model},
                    "result": {
                        "correct": True,
                        "call": {
                            "status": "complete",
                            "parsed": answer,
                            "text": json.dumps(answer),
                        },
                    },
                }
            )
    initial[0]["result"]["call"]["status"] = "invalid_output"
    initial[1]["result"]["call"]["parsed"]["answer"] = "A range, 1 to 4"
    (tmp_path / "initial.jsonl").write_text("\n".join(map(json.dumps, initial)))
    for name in ("interpretation.jsonl", "branch.jsonl"):
        (tmp_path / name).write_text("")
    with pytest.raises(ValueError, match="v128 hashes"):
        prepare(tmp_path)
    monkeypatch.setattr(
        "veracity_harness.sector_revision.PARENT_SHA256",
        {
            name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
            for name in (
                "study.json",
                "cases.json",
                "initial.jsonl",
                "interpretation.jsonl",
                "branch.jsonl",
            )
        },
    )
    prepared = prepare(tmp_path)
    assert len(prepared["assignments"]) == 300
    assert len(prepared["cases"]) == 60
    assert sum(a["status"] == "initial_unavailable" for a in prepared["assignments"]) == 1
    assert sum(a["status"] == "numeric_policy_unsupported" for a in prepared["assignments"]) == 1
    assert sum(len(a["seeds"]) for a in prepared["assignments"]) == 1500
    with pytest.raises(ValueError, match="overwrite"):
        prepare(tmp_path, tmp_path)
    (tmp_path / "cases.json").write_text("[]")
    with pytest.raises(ValueError, match="bytes differ"):
        prepare(tmp_path)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["initial_unavailable", "numeric_policy_unsupported"])
async def test_unavailable_assignments_are_retained_without_paid_calls(
    tmp_path, monkeypatch, status
):
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)

    async def invoke(*args, **kwargs):
        pytest.fail("An unavailable assignment must not invoke a model")

    monkeypatch.setattr(study, "invoke", invoke)
    assignment = {"model": MODELS[0], "status": status, "challenge": None}
    await execute_assignment(study, case, assignment, 101)
    await execute_assignment(study, case, assignment, 101)
    row = study.journal.get(job_key("branch", PROTOCOL, case.case_id, MODELS[0], "misleading", 101))
    assert row["status"] == "failed"
    assert row["result"]["status"] == status
    assert study.journal.counts() == {"branch:failed": 1}


def test_resume_can_finish_unpaid_runtime_setup_and_record_price_changes():
    runtime = {"settings": {"m": {"max_tokens": 4096}}, "prices": {"m": "1"}}
    config = freeze_runtime({"protocol": PROTOCOL}, runtime, calls_started=False)
    assert config["settings"] == runtime["settings"]
    assert config["prices"] == runtime["prices"]
    with pytest.raises(ValueError, match="already frozen"):
        freeze_runtime({"protocol": PROTOCOL}, runtime, calls_started=True)
    with pytest.raises(ValueError, match="provider settings"):
        freeze_runtime(config, {**runtime, "settings": {}}, calls_started=True)
    resumed = freeze_runtime(config, {**runtime, "prices": {"m": "2"}}, calls_started=True)
    assert resumed["prices"] == {"m": "1"}
    assert [check["prices"] for check in resumed["price_checks"]] == [{"m": "1"}, {"m": "2"}]


def test_interrupted_parent_import_aborts_before_dispatch_instead_of_becoming_missing(tmp_path):
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)
    row = {
        "id": "saved",
        "status": "complete",
        "payload": {"model": MODELS[0]},
        "result": {"call": {"status": "complete", "text": "Frozen original"}},
    }
    prepared = {"initial": [row], "interpretation": []}
    study.journal.begin(row["id"], "initial", row["payload"])
    study.journal.recover()
    with pytest.raises(ValueError, match="interrupted or differs"):
        import_parent_initials(study, prepared)
    assert study.journal.get(row["id"])["status"] == "interrupted"
    assert study.journal.rows("call") == []


def test_parent_import_is_exact_and_idempotent_and_rejects_changed_results(tmp_path):
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)
    row = {
        "id": "saved",
        "status": "complete",
        "payload": {"model": MODELS[0]},
        "result": {"call": {"status": "complete", "text": "Frozen original"}},
    }
    prepared = {"initial": [row], "interpretation": []}
    import_parent_initials(study, prepared)
    import_parent_initials(study, prepared)
    assert study.journal.get(row["id"])["result"] == row["result"]
    with pytest.raises(ValueError, match="interrupted or differs"):
        import_parent_initials(study, {**prepared, "initial": [{**row, "result": {}}]})
