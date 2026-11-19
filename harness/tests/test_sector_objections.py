from decimal import Decimal

import pytest

from veracity_harness.sector_cases import Answer, SectorCase, challenge_text, grade
from veracity_harness.sector_objections import inverse_legacy_objection, numeric_alternative_v2


def case(reference):
    return SectorCase(
        case_id="c",
        task_id="finqa:c",
        group_id="finqa:c",
        benchmark="finqa",
        domain="finance",
        task="Calculate.",
        document="Source.",
        reference=str(reference),
        source_url="https://example.test/pinned",
        source_sha256="frozen",
    )


def answer(value):
    return Answer(answer=str(value), confidence_correct=0.9, explanation="Original.", citations=())


@pytest.mark.parametrize("reference", ["-1000", "-28", "-3.5", "0", "28", "40", "117624.84"])
def test_legacy_objection_exactly_encodes_the_reference(reference):
    _, alternative = challenge_text(case(reference), answer("12345"), "misleading")
    assert inverse_legacy_objection(alternative.answer) == Decimal(reference)


def test_future_proposal_is_unchanged_when_a_different_reference_is_compatible():
    first = numeric_alternative_v2(case("40"), answer("100"))
    second = numeric_alternative_v2(case("80"), answer("100"))
    assert first == second
    assert inverse_legacy_objection(first.answer) == Decimal(100)
    assert not grade(case("40"), first) and not grade(case("80"), second)


def test_future_policy_rejects_an_accidentally_correct_candidate():
    alternative = numeric_alternative_v2(case("125"), answer("100"))
    assert not grade(case("125"), alternative)
    assert inverse_legacy_objection(alternative.answer) != Decimal(125)
