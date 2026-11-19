from decimal import Decimal

import pytest

from veracity_harness.runner import ROOT
from veracity_harness.sector_cases import (
    Answer,
    build_cohort,
    challenge_text,
    grade,
    participant_task,
)


@pytest.fixture(scope="module")
def cohort():
    return build_cohort(ROOT / "tasks/veracity_tasks.sqlite")


def test_balanced_common_cohort_retains_unique_source_groups(cohort):
    assert len(cohort) == 120
    for domain in ("finance", "legal", "science", "education"):
        group = [c for c in cohort if c.domain == domain]
        assert len(group) == len({c.group_id for c in group}) == 30
    assert len({c.case_id for c in cohort}) == 120
    assert not any(c.task_id == "contractnli:293/nda-1" for c in cohort)


def test_label_cohorts_include_uncertainty(cohort):
    for domain in ("legal", "science"):
        cases = [c for c in cohort if c.domain == domain]
        assert sorted(sum(c.reference == label for c in cases) for label in cases[0].labels) == [
            10,
            10,
            10,
        ]


def test_participant_input_omits_operator_reference_fields(cohort):
    for case in cohort:
        text = participant_task(case)
        assert "Veracity" not in text
        for key in ("reference_json", "gold_inds", "exe_ans", "teacher_described_confusion"):
            assert key not in text


def test_numeric_grading_respects_percentage_and_precision(cohort):
    case = next(c for c in cohort if c.domain == "finance" and c.scale == "percent")
    expected = Decimal(case.reference)
    assert grade(
        case,
        Answer(
            answer=str(expected),
            scale="percent",
            confidence_correct=0.9,
            explanation="calculation",
            citations=[],
        ),
    )
    assert not grade(
        case,
        Answer(
            answer=str(expected + 100),
            scale="percent",
            confidence_correct=0.9,
            explanation="calculation",
            citations=[],
        ),
    )


def test_false_alternative_is_wrong_and_not_equal_to_original(cohort):
    for case in cohort:
        answer = Answer(
            answer=case.reference,
            scale=case.scale,
            confidence_correct=0.9,
            explanation="source",
            citations=[],
        )
        challenge, alternative = challenge_text(case, answer, "misleading")
        assert alternative is not None and alternative.answer != answer.answer
        assert not grade(case, alternative)
        assert alternative.answer in challenge


def test_education_controls_keep_distinct_problem_groups(cohort):
    cases = [c for c in cohort if c.domain == "education"]
    assert sum(c.variant == "correct_working_control" for c in cases) == 15
    assert sum(c.variant == "original_incorrect_working" for c in cases) == 15


def test_missing_or_unparseable_answer_is_not_graded_as_wrong(cohort):
    assert grade(cohort[0], None) is None
    case = next(c for c in cohort if c.domain == "education")
    assert (
        grade(
            case,
            Answer(
                answer="cannot determine",
                scale="",
                confidence_correct=0.1,
                explanation="uncertain",
                citations=[],
            ),
        )
        is False
    )


def test_confidence_boundary_is_validated():
    with pytest.raises(ValueError):
        Answer(answer="1", scale="", confidence_correct=1.01, explanation="x", citations=[])


def test_count_answers_do_not_accept_fractional_rounding(cohort):
    case = next(c for c in cohort if c.benchmark == "tatqa" and c.variant == "count")
    answer = Answer(
        answer=str(Decimal(case.reference) + Decimal(".4")),
        scale=case.scale,
        confidence_correct=0.9,
        explanation="count",
        citations=[],
    )
    assert grade(case, answer) is False


def test_lossless_json_number_and_empty_scale_normalization():
    answer = Answer(
        answer=55, scale="empty", confidence_correct=0.9, explanation="arithmetic", citations=[]
    )
    assert answer.answer == "55"
    assert answer.scale == ""
    with pytest.raises(ValueError):
        Answer(
            answer=True, scale="", confidence_correct=0.9, explanation="not a number", citations=[]
        )
