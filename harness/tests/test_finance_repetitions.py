"""Repetition counts come from distinct revealed votes, not forecasts."""

import json
import runpy
from pathlib import Path

import pytest

from game_api.generated import EpisodeView, JurorView
from veracity_harness.finance_repetitions import MODEL, collect_study, round_votes

ANALYSIS = runpy.run_path(
    str(Path(__file__).parents[1] / "research/finance-micro/analyze_repetitions.py")
)


def test_recovery_selects_only_an_unresolved_cell_and_preserves_original_attempts():
    aware = {
        "seed": 29,
        "stake_multiplier": 10,
        "condition": "aware-verified",
        "source_cohort": "original",
        "verification": "submitted",
        "jury_outcome": "CREATOR_SUPPORTED",
    }
    missing = {
        **aware,
        "condition": "unaware-verified",
        "verification": "pending",
        "jury_outcome": None,
    }
    recovered = {
        **missing,
        "source_cohort": "recovery",
        "verification": "submitted",
        "jury_outcome": "CREATOR_SUPPORTED",
    }
    attempts = [aware, missing, recovered]
    assert ANALYSIS["select_results"](attempts) == [aware, recovered]
    assert attempts == [aware, missing, recovered]
    assert ANALYSIS["select_results"]([aware, missing]) == [aware, missing]


@pytest.mark.parametrize("second_verdict", ["CREATOR_SUPPORTED", "CHALLENGER_SUPPORTED"])
def test_recovery_cannot_replace_any_already_settled_result(second_verdict):
    original = {
        "seed": 29,
        "stake_multiplier": 1000,
        "condition": "aware-verified",
        "source_cohort": "original",
        "verification": "submitted",
        "jury_outcome": "CREATOR_SUPPORTED",
    }
    duplicate = {**original, "source_cohort": "recovery", "jury_outcome": second_verdict}
    with pytest.raises(ValueError, match="Multiple settled attempts"):
        ANALYSIS["select_results"]([original, duplicate])


def test_analysis_retains_quorum_settlement_without_imputing_an_absent_vote():
    jurors = [
        JurorView(
            actor_id=f"juror-{index}",
            assessment_hash=None,
            commitment=None,
            revealed=index < 2,
            verdict="CREATOR_SUPPORTED" if index < 2 else None,
        )
        for index in range(3)
    ]
    episode = EpisodeView.model_construct(
        jurors=jurors,
        creator_votes=2,
        challenger_votes=0,
        required_votes=2,
        phase="SETTLED_CREATOR",
        total_deposited_wei="2200000000",
    )
    result = ANALYSIS["jury_observation"](episode)
    assert result == {
        "jury_outcome": "CREATOR_SUPPORTED",
        "support_votes": 2,
        "reject_votes": 0,
        "assigned_jurors": 3,
        "revealed_jurors": 2,
        "missing_votes": 1,
        "participation_complete": False,
        "actual_total_deposited_wei": "2200000000",
    }
    with pytest.raises(ValueError, match="required quorum"):
        ANALYSIS["jury_observation"](
            episode.model_copy(
                update={
                    "creator_votes": 1,
                    "jurors": [
                        jurors[0],
                        jurors[1].model_copy(update={"revealed": False, "verdict": None}),
                        jurors[2],
                    ],
                }
            )
        )
    with pytest.raises(ValueError, match="distinct assigned"):
        ANALYSIS["jury_observation"](episode.model_copy(update={"jurors": jurors[:2]}))
    with pytest.raises(ValueError, match="Reveal flags"):
        ANALYSIS["jury_observation"](
            episode.model_copy(
                update={
                    "jurors": [
                        *jurors[:2],
                        jurors[2].model_copy(update={"verdict": "CREATOR_SUPPORTED"}),
                    ]
                }
            )
        )


def test_analysis_refuses_an_unfinished_cohort(tmp_path):
    plan = {
        "seeds": [1, 2, 3, 4, 5],
        "stake_multipliers": [1, 10, 100, 1000],
        "status": "running",
        "assignments": [
            {"seed": seed, "stake_multiplier": stake, "status": "pending"}
            for seed in range(1, 6)
            for stake in (1, 10, 100, 1000)
        ],
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    with pytest.raises(ValueError, match="unfinished assignments"):
        ANALYSIS["analyze"](tmp_path, tmp_path / "output")


@pytest.mark.parametrize(
    "changed",
    [{"sampling_seed": None}, {"seed": 7}, {"stake_multiplier": 100}, {"provider": "openrouter"}],
)
def test_collection_rejects_unseeded_or_misassigned_studies(tmp_path, changed):
    state = {
        "model": MODEL,
        "provider": "cloudflare",
        "seed": 29,
        "sampling_seed": 29,
        "stake_multiplier": 10,
        **changed,
    }
    (tmp_path / "study.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="planned provider, seed and stakes"):
        collect_study(tmp_path, {"seed": 29, "stake_multiplier": 10}, {})


@pytest.mark.parametrize("support", [0, 1, 2, 3])
def test_three_votes_must_match_both_the_tally_and_settlement(support):
    jurors = [
        JurorView(
            actor_id=f"juror-{index}",
            assessment_hash="hash",
            commitment="commit",
            revealed=True,
            verdict=("CREATOR_SUPPORTED" if index < support else "CHALLENGER_SUPPORTED"),
        )
        for index in range(3)
    ]
    # Only the fields used by this typed policy are relevant to these unit cases.
    episode = EpisodeView.model_construct(
        jurors=jurors,
        creator_votes=support,
        challenger_votes=3 - support,
        phase="SETTLED_CREATOR" if support >= 2 else "SETTLED_CHALLENGER",
    )
    assert round_votes(episode) == {
        "support_votes": support,
        "reject_votes": 3 - support,
        "jury_outcome": "CREATOR_SUPPORTED" if support >= 2 else "CHALLENGER_SUPPORTED",
    }
    with pytest.raises(ValueError, match="counts disagree"):
        round_votes(episode.model_copy(update={"creator_votes": 10}))
    with pytest.raises(ValueError, match="settlement disagree"):
        round_votes(
            episode.model_copy(
                update={"phase": "SETTLED_CHALLENGER" if support >= 2 else "SETTLED_CREATOR"}
            )
        )
    with pytest.raises(ValueError, match="distinct revealed"):
        round_votes(episode.model_copy(update={"jurors": [jurors[0]] * 3}))
    with pytest.raises(ValueError, match="distinct revealed"):
        round_votes(episode.model_copy(update={"jurors": jurors[:2]}))
    with pytest.raises(ValueError, match="distinct revealed"):
        round_votes(episode.model_copy(update={"phase": "REVEAL"}))
    with pytest.raises(ValueError, match="distinct revealed"):
        round_votes(
            episode.model_copy(
                update={"jurors": [jurors[0].model_copy(update={"revealed": False}), *jurors[1:]]}
            )
        )
