from decimal import Decimal

import pytest

from veracity_harness.contract_micro import Ballot
from veracity_harness.sector_cases import Answer, Defence, SectorCase
from veracity_harness.sector_probe import CHECKED_EVIDENCE, probe_messages


def source():
    case = SectorCase(
        case_id="arithmetic",
        task_id="finqa:GPN/2018/page_94.pdf-2",
        group_id="finqa:GPN/2018",
        benchmark="finqa",
        domain="finance",
        task="Calculate the monetary value in thousands.",
        document="unvested at december 31 2018 | 1084 | $ 108.51",
        reference="117624.84",
        source_url="https://example.test/pinned",
        source_sha256="frozen",
    )
    record = {
        "claim": "My answer is 117628.84, unscaled.",
        "challenge": "Audit the source.",
        "defence": {
            "parsed": {
                "answer": "117628.84",
                "scale": "",
                "confidence_correct": 0.85,
                "explanation": "A UNIQUE MISTAKEN DEFENCE.",
                "citations": [],
                "stance": "maintain",
                "original_still_supported": True,
                "p_original_correct": 0.85,
                "p_jury_upholds": 0.8,
            }
        },
    }
    return case, record


def test_calculator_has_no_frozen_wrong_answer_or_game_context():
    messages, schema = probe_messages(*source(), "calculate")
    text = "\n".join(m.content for m in messages)
    assert schema is Answer
    assert "1084 * 108.51" in text
    assert "117628.84" not in text
    assert "Veracity" not in text


def test_judge_conditions_keep_source_and_claim_but_filter_forecasts():
    case, record = source()
    for condition in ("claim_only", "defended", "checked_evidence"):
        messages, schema = probe_messages(case, record, condition)
        text = "\n".join(m.content for m in messages)
        assert schema is Ballot
        assert case.document in text and record["claim"] in text
        assert "p_original_correct" not in text and "confidence_correct" not in text
        assert ("UNIQUE MISTAKEN DEFENCE" in text) == (condition != "claim_only")
        assert (CHECKED_EVIDENCE in text) == (condition == "checked_evidence")


def test_checked_arithmetic_is_exact_and_unknown_condition_rejected():
    assert Decimal(1084) * Decimal("108.51") == Decimal("117624.84")
    assert Decimal(108400) + Decimal(8672) + Decimal("552.84") == Decimal("117624.84")
    with pytest.raises(ValueError, match="condition"):
        probe_messages(*source(), "unplanned")


def test_original_author_receives_frozen_text_and_checked_counterevidence():
    original = '{"answer":"117628.84","confidence_correct":1.0}'
    messages, schema = probe_messages(*source(), "author_checked", original_text=original)
    assert schema is Defence
    assert messages[-2].content == original
    assert CHECKED_EVIDENCE in messages[-1].content
    with pytest.raises(ValueError, match="frozen"):
        probe_messages(*source(), "author_checked")
