import json
import time
from decimal import Decimal

import pytest

from veracity_harness.runner import ROOT
from veracity_harness.sector_cases import MODELS, build_cohort
from veracity_harness.sector_study import SectorStudy, StudyJournal, initial_messages, job_key


def test_journal_deduplicates_and_never_replaces_terminal_output(tmp_path):
    journal = StudyJournal(tmp_path / "journal.sqlite")
    assert journal.begin("a", "initial", {"model": "x"})
    journal.finish("a", "complete", {"text": "saved"})
    assert not journal.begin("a", "initial", {"model": "x"})
    with pytest.raises(ValueError):
        journal.finish("a", "failed", {})
    assert journal.get("a")["result"] == {"text": "saved"}


def test_recovery_preserves_interrupted_work_without_paid_resampling(tmp_path):
    path = tmp_path / "journal.sqlite"
    journal = StudyJournal(path)
    assert journal.begin("a", "initial", {})
    StudyJournal(path).recover()
    assert not journal.begin("a", "initial", {})
    assert journal.get("a")["status"] == "interrupted"


def test_initial_prompt_has_confidence_but_no_dispute_metadata():
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    messages = initial_messages(case)
    text = json.dumps([m.content for m in messages])
    assert "confidence_correct" in text
    assert "Veracity" not in text
    assert "p_jury_upholds" not in text


def test_journal_summary_keeps_failed_and_completed_distinct(tmp_path):
    journal = StudyJournal(tmp_path / "journal.sqlite")
    journal.begin("a", "call", {})
    journal.finish("a", "complete", {"status": "complete"})
    journal.begin("b", "call", {})
    journal.finish("b", "failed", {"status": "output_limit"})
    assert journal.counts() == {"call:complete": 1, "call:failed": 1}


def test_representation_recovery_preserves_raw_terminal_observation(tmp_path):
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)
    study.cases = (case,)
    raw = {
        "answer": float(case.reference),
        "scale": case.scale or "empty",
        "confidence_correct": 0.9,
        "explanation": "calculation",
        "citations": [],
    }
    key = job_key("initial", case.case_id, MODELS[0])
    payload = {"case_id": case.case_id, "model": MODELS[0]}
    study.journal.begin(key, "initial", payload)
    study.journal.finish(
        key,
        "failed",
        {"call": {"status": "invalid_output", "text": json.dumps(raw)}, "correct": None},
    )
    study.normalize_initials()
    study.normalize_initials()
    assert study.journal.get(key)["status"] == "failed"
    assert study.frozen_initial(case.case_id, MODELS[0])["result"]["correct"] is True
    assert study.journal.counts()["interpretation:complete"] == 1


@pytest.mark.asyncio
async def test_sector_dispute_executes_real_commit_reveal_and_settlement(tmp_path, monkeypatch):
    case = build_cohort(ROOT / "tasks/veracity_tasks.sqlite")[0]
    study = SectorStudy(tmp_path, Decimal("1"), time.time() + 120)
    original = {
        "answer": case.reference,
        "scale": case.scale,
        "confidence_correct": 0.9,
        "explanation": "Source calculation.",
        "citations": [],
    }
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

    async def invoke(model, messages, identity, seed, schema):
        if schema.__name__ == "Ballot":
            parsed = {
                "verdict": "CREATOR_SUPPORTED",
                "assessment": "Supported by the supplied source.",
            }
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
    await study.dispute(case, MODELS[0], "review", 101)
    result = study.journal.get(job_key("branch", case.case_id, MODELS[0], "review", 101))["result"]
    assert result["jury_outcome"] == "CREATOR_SUPPORTED"
    assert result["support_votes"] == result["revealed_jurors"] == 3
    assert result["final_correct"] is True
    from veracity_harness.sector_archive import validate_episode

    identity = job_key("branch", case.case_id, MODELS[0], "review", 101)
    row = study.journal.get(identity)
    evidence = json.loads((tmp_path / "episodes" / identity / "evidence.json").read_text())
    admitted = validate_episode(row, evidence)
    assert admitted["phase"] == "SETTLED_CREATOR"
    assert admitted["revealed"] == 3
    evidence["episode"]["creator_votes"] = 2
    with pytest.raises(ValueError, match="votes"):
        validate_episode(row, evidence)
    evidence["private_transcripts"] = {"unexpected": {"message": "private"}}
    with pytest.raises(ValueError, match="private"):
        validate_episode(row, evidence)
