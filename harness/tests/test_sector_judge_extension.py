import copy
import json

import pytest

from veracity_harness.sector_cases import SectorCase
from veracity_harness.sector_judge_extension import (
    CalculationProof,
    extension_messages,
    prepare_sources,
    select_sources,
)


def source(group, correct, *, juries=0):
    case = SectorCase(
        case_id=group,
        task_id="finqa:" + group,
        group_id=group,
        benchmark="finqa",
        domain="finance",
        task="Calculate the value of 3 items at 4 each.",
        document="Items | 3\nPrice | 4",
        reference="12",
        source_url="https://example.test/frozen",
        source_sha256="frozen",
    )
    record = {
        "id": group,
        "payload": {"case_id": group, "model": "author", "arm": "audit", "seed": 101},
        "result": {
            "claim": "My answer is 12." if correct else "My answer is 13.",
            "challenge": "Check the source.",
            "initial_correct": correct,
            "original_answer": {
                "answer": "12" if correct else "13",
                "scale": "",
                "confidence_correct": 0.9,
                "explanation": "Original.",
                "citations": [],
            },
            "defence": {
                "status": "complete",
                "parsed": {
                    "answer": "12" if correct else "13",
                    "scale": "",
                    "confidence_correct": 0.9,
                    "explanation": "Frozen defence.",
                    "citations": [],
                    "stance": "maintain",
                    "original_still_supported": True,
                    "p_original_correct": 0.9,
                    "p_jury_upholds": 0.8,
                },
            },
            "support_votes": juries,
        },
    }
    return case, record


def proof():
    return CalculationProof(
        task_id="finqa:wrong",
        source_assertions=("Items | 3", "Price | 4"),
        steps=({"operation": "multiply", "operands": ("3", "4"), "result": "12"},),
        final_value="12",
        scale="",
        explanation="The monetary value is count times unit price.",
    )


def test_selection_uses_sources_and_frozen_answers_not_jury_verdicts():
    sources = [source("wrong", False), source("right", True), source("other", True)]
    cases = {c.case_id: c for c, _ in sources}
    branches = [b for _, b in sources]
    first = select_sources(cases, branches, excluded_tasks=set())
    changed = copy.deepcopy(branches)
    for branch in changed:
        branch["result"]["support_votes"] = 999
    second = select_sources(cases, changed, excluded_tasks=set())
    assert [b["id"] for _, b in first] == [b["id"] for _, b in second]
    assert len(first) == 2
    assert len({c.group_id for c, _ in first}) == 2


def test_proof_requires_exact_arithmetic_and_verbatim_source_inputs():
    case, _ = source("wrong", False)
    assert "3 * 4 = 12" in proof().checked_text(case)
    altered = proof().model_copy(update={"final_value": "13"})
    with pytest.raises(ValueError, match="final"):
        altered.checked_text(case)
    altered = proof().model_copy(update={"source_assertions": ("invented input",)})
    with pytest.raises(ValueError, match="source"):
        altered.checked_text(case)
    altered = proof().model_copy(update={"scale": "million"})
    with pytest.raises(ValueError, match="scale"):
        altered.checked_text(case)


def test_proof_binds_the_original_answer_to_its_truth_class():
    _, wrong = source("wrong", False)
    assert proof().check_original(wrong["result"]) is False
    wrong["result"]["initial_correct"] = True
    with pytest.raises(ValueError, match="truth class"):
        proof().check_original(wrong["result"])
    _, right = source("right", True)
    assert proof().check_original(right["result"]) is True


def test_judge_contexts_change_only_defence_and_checked_calculation():
    case, branch = source("wrong", False)
    texts = {}
    for condition in ("claim_only", "defended", "checked_evidence"):
        messages = extension_messages(case, branch["result"], proof(), condition)
        texts[condition] = "\n".join(m.content for m in messages)
        assert branch["result"]["claim"] in texts[condition]
        assert case.document in texts[condition]
        assert "confidence_correct" not in texts[condition]
        assert "p_jury_upholds" not in texts[condition]
    assert "Frozen defence." not in texts["claim_only"]
    assert "Frozen defence." in texts["defended"]
    assert "Checked calculation" not in texts["defended"]
    assert "Checked calculation" in texts["checked_evidence"]
    with pytest.raises(ValueError, match="condition"):
        extension_messages(case, branch["result"], proof(), "unplanned")


def test_wrong_or_partial_parent_cannot_define_the_extension_cohort(tmp_path):
    for name in ("cases.json", "branch.jsonl", "study.json", "progress.json"):
        (tmp_path / name).write_text(json.dumps({"status": "complete"}))
    with pytest.raises(ValueError, match="admitted v128"):
        prepare_sources(tmp_path, tmp_path / "proofs.json")
