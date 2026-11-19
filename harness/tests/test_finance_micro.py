"""Confidence measurements preserve the intervention and outcome boundaries."""

import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from veracity_harness.finance_micro import (
    Answer,
    answer_messages,
    branch_records,
    numeric_score,
    verification_experiment,
)


def test_unaware_prompt_has_no_protocol_or_source_metadata():
    content = "\n".join(message.content for message in answer_messages(False)).lower()
    for forbidden in ("veracity", "jury", "juror", "finqa", "benchmark", "3.80", "oracle"):
        assert forbidden not in content
    disclosed = "\n".join(message.content for message in answer_messages(True)).lower()
    assert "veracity" in disclosed and "three jurors" in disclosed


@pytest.mark.parametrize("value", ["3.80", "3.804347826"])
def test_arithmetic_oracle_uses_positive_decline_and_percentage_units(value):
    answer = Answer(decline_percent=Decimal(value), p_correct=0.9, explanation="calculation")
    score = numeric_score(answer)
    assert score["correct"] is True
    assert score["brier_correct"] == pytest.approx(0.01)


@pytest.mark.parametrize("value", ["-3.80", "0.03804", "3.95", "4.0"])
def test_wrong_sign_units_denominator_or_rounding_are_not_correct(value):
    answer = Answer(decline_percent=Decimal(value), p_correct=0.9, explanation="calculation")
    assert numeric_score(answer)["correct"] is False
    assert numeric_score(answer)["brier_correct"] == pytest.approx(0.81)


@pytest.mark.parametrize("probability", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_confidence_is_rejected(probability):
    with pytest.raises(ValidationError):
        Answer(decline_percent="3.80", p_correct=probability, explanation="calculation")


def test_paired_conditions_share_frozen_answer_and_missing_verification_is_not_rejection():
    aware = Answer(decline_percent="3.80", p_correct=0.99, explanation="aware reply")
    unaware = Answer(decline_percent="3.95", p_correct=0.8, explanation="unaware reply")
    records = branch_records(aware, unaware)
    assert len(records) == 3
    assert records[0]["answer"] == records[1]["answer"]
    assert records[0]["baseline_id"] == records[1]["baseline_id"]
    assert records[0]["baseline_id"] != records[2]["baseline_id"]
    assert records[1]["verification"] == "withheld"
    assert records[1]["jury_outcome"] is None
    assert records[1]["brier_jury"] is None
    assert aware.explanation == "aware reply"


def test_jury_sees_only_the_frozen_numeric_claim_and_task(tmp_path):
    answer = Answer(decline_percent="3.80", p_correct=0.98765, explanation="private rationale")
    experiment = verification_experiment(answer, tmp_path, "deepseek/deepseek-v4-pro", 7)
    participant_input = experiment.case.document.read_text() + experiment.case.reference_claim
    assert "private rationale" not in participant_input
    assert "0.98765" not in participant_input
    assert experiment.case.expected_verdict is None
    assert experiment.jury_size == 3
    assert experiment.seed == 7
    assert experiment.creator == experiment.challenger == "scripted"
    assert not experiment.peer_jurors
    assert not experiment.treatment.public_messaging
    assert not experiment.treatment.private_chat
    assert json.loads(answer.model_dump_json())["p_correct"] == 0.98765


@pytest.mark.parametrize("incomplete", [False, True])
@pytest.mark.parametrize("truncated_forecast", [False, True])
@pytest.mark.parametrize("only_condition", [None, "aware-verified", "unaware-verified"])
async def test_study_freezes_before_submission_and_preserves_partial_failure(
    monkeypatch, tmp_path, incomplete, truncated_forecast, only_condition
):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    import wandb
    from langchain_core.messages import AIMessage

    import docker
    from veracity_harness import finance_micro as study
    from veracity_harness.spending import ModelPrice

    output = tmp_path / "attempt"
    remote = MagicMock(url="https://wandb.ai/fixture/project/runs/study", offline=False)
    remote.summary = {}

    def tracking_run(**kwargs):
        assert kwargs["settings"].base_url == "https://api.wandb.ai"
        return remote

    monkeypatch.delenv("WANDB_BASE_URL", raising=False)
    monkeypatch.setattr(wandb, "init", tracking_run)
    monkeypatch.setattr(wandb, "Artifact", MagicMock())
    docker_client = MagicMock(spec=docker.DockerClient)
    monkeypatch.setattr(docker, "from_env", lambda: docker_client)
    monkeypatch.setattr(study.platform, "system", lambda: "Linux")
    monkeypatch.setattr(study.os, "access", lambda *args: True)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "fixture-cloudflare-token")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "fixture-account")
    monkeypatch.setenv("WANDB_API_KEY", "fixture-tracking-key")
    monkeypatch.setenv("WANDB_MODE", "online")
    monkeypatch.setattr(
        study,
        "fetch_cloudflare_price",
        AsyncMock(
            return_value=ModelPrice(
                id="fixture/model", context_length=1000, pricing={"prompt": "0.001"}
            )
        ),
    )
    requests = []

    async def invoke(messages, **kwargs):
        requests.append(messages)
        if len(requests) <= 2:
            return AIMessage(
                Answer(
                    decline_percent="3.80", p_correct=0.9, explanation="arithmetic"
                ).model_dump_json()
            )
        return (
            AIMessage(content="", response_metadata={"finish_reason": "length"})
            if truncated_forecast
            else AIMessage('{"p_jury_upholds": 0.8}')
        )

    chat = SimpleNamespace(
        ainvoke=invoke,
        root_async_client=SimpleNamespace(close=AsyncMock()),
        root_client=MagicMock(),
    )
    monkeypatch.setattr(study, "create_cloudflare_model", lambda *args: chat)
    submissions = []

    async def adjudicate(experiment, destination, **kwargs):
        if only_condition:
            assert destination.name == only_condition
        assert (output / "aware-answer.json").exists()
        assert (output / "unaware-answer.json").exists()
        assert len(requests) >= 3
        assert experiment.model.provider == "cloudflare"
        assert experiment.jury_size == 3
        assert experiment.case.expected_verdict is None
        submissions.append(experiment)
        directory = destination / "run-fixture"
        directory.mkdir()
        (directory / "run.json").write_text(
            json.dumps(
                {
                    "status": "complete",
                    "run_id": "run-fixture",
                    "episodes": [{"observed_verdict": None if incomplete else "CREATOR_SUPPORTED"}],
                }
            )
        )
        return directory

    monkeypatch.setattr(study, "run_experiment", adjudicate)
    if incomplete:
        with pytest.raises(RuntimeError, match="Jury round incomplete"):
            await study.run_study(
                output,
                "fixture/model",
                Decimal(5),
                "cloud-fixture",
                seed=29,
                only_condition=only_condition,
            )
    else:
        await study.run_study(
            output,
            "fixture/model",
            Decimal(5),
            "cloud-fixture",
            seed=29,
            only_condition=only_condition,
        )
    state = json.loads((output / "study.json").read_text())
    assert state["seed"] == state["sampling_seed"] == 29
    assert state["answer_model_settings"]["sampling_seed"] == 29
    assert all(e.seed == e.model.sampling_seed == 29 for e in submissions)
    assert all(row["sampling_seed"] == 29 for row in study.measurement_rows(state))
    assert state["status"] == ("failed" if incomplete else "complete")
    assert state["only_condition"] == only_condition
    expected_submissions = 1 if incomplete or only_condition else 2
    assert len(submissions) == expected_submissions
    assert len(requests) == 2 + expected_submissions
    unaware_input = "\n".join(message.content for message in requests[1]).lower()
    assert "veracity" not in unaware_input
    assert state["arms"][1]["verification"] == ("not_assigned" if only_condition else "withheld")
    assert state["arms"][1]["brier_jury"] is None
    selected = next(
        a for a in state["arms"] if a["condition"] == (only_condition or "aware-verified")
    )
    assert selected["brier_jury"] == (
        None if incomplete or truncated_forecast else pytest.approx(0.04)
    )
    assert selected["jury_forecast_status"] == (
        "output_limit" if truncated_forecast else "measured"
    )
    if only_condition:
        assert [e.case.reference_claim for e in submissions]
        assert all(
            a["verification"] == "not_assigned"
            for a in state["arms"]
            if a["condition"] != only_condition
        )
        if not incomplete:
            assert state["jury_forecast_missing"] == int(truncated_forecast)
    assert remote.finish.call_args.kwargs["exit_code"] == int(incomplete)
    assert remote.log_artifact.call_count >= 4
    docker_client.ping.assert_called_once()
    docker_client.close.assert_called_once()


async def test_invalid_single_condition_is_rejected_before_output_or_paid_calls(
    monkeypatch, tmp_path
):
    from veracity_harness import finance_micro as study

    monkeypatch.setattr(study.platform, "system", lambda: "Linux")
    monkeypatch.setenv("WANDB_MODE", "online")
    output = tmp_path / "invalid-selection"
    with pytest.raises(ValueError, match="verified condition"):
        await study.run_study(
            output, "fixture/model", Decimal(100), "fixture", only_condition="aware-withheld"
        )
    assert not output.exists()


async def test_live_execution_does_not_run_on_the_laptop(monkeypatch, tmp_path):
    from veracity_harness import finance_micro as study

    monkeypatch.setattr(study.platform, "system", lambda: "Darwin")
    with pytest.raises(ValueError, match="cloud runner"):
        await study.run_study(tmp_path / "attempt", "fixture/model", Decimal(5), "local")
    assert not (tmp_path / "attempt").exists()


def test_stake_multiplier_scales_bonds_without_changing_payout_shares(tmp_path):
    from veracity_harness.finance_micro import stake_measurements

    answer = Answer(decline_percent="3.80", p_correct=0.99, explanation="calculation")
    baseline = verification_experiment(answer, tmp_path / "one", "fixture/model", 7)
    raised = verification_experiment(
        answer, tmp_path / "ten", "fixture/model", 7, stake_multiplier=10
    )
    assert raised.parameters.beta_wei == "10000000"
    assert raised.parameters.gamma_bps == baseline.parameters.gamma_bps
    assert raised.parameters.juror_bps == baseline.parameters.juror_bps
    assert raised.jury_size == baseline.jury_size == 3
    assert stake_measurements(raised.parameters, raised.jury_size) == {
        "party_bond_wei": "10000000",
        "juror_bond_wei": "1000000",
        "scheduled_total_stake_wei": "23000000",
        "stake_currency": "synthetic_anvil_wei",
    }


@pytest.mark.parametrize("factor", [0, -1, 1.5, True])
def test_invalid_stake_multiplier_is_rejected(tmp_path, factor):
    answer = Answer(decline_percent="3.80", p_correct=0.99, explanation="calculation")
    with pytest.raises(ValueError):
        verification_experiment(answer, tmp_path, "fixture/model", 7, stake_multiplier=factor)


@pytest.mark.parametrize("tamper", [None, "model", "provider", "prompt", "answer"])
def test_frozen_baseline_reuse_validates_identity_prompts_and_hashes(tmp_path, tamper):
    import shutil

    from veracity_harness.finance_micro import DESIGN, load_baselines

    source = tmp_path / "old"
    shutil.copytree(DESIGN, source / "design")
    answer = Answer(decline_percent="3.80", p_correct=0.99, explanation="frozen")
    for identity in ("aware", "unaware"):
        (source / f"{identity}-answer.json").write_text(answer.model_dump_json())
    state = {
        "model": "fixture/model",
        "provider": "cloudflare",
        "arms": branch_records(answer, answer),
    }
    if tamper in {"model", "provider"}:
        state[tamper] = "different"
    elif tamper == "prompt":
        (source / "design/task.md").write_text("Different task")
    elif tamper == "answer":
        (source / "aware-answer.json").write_text(
            answer.model_copy(update={"p_correct": 0.1}).model_dump_json()
        )
    (source / "study.json").write_text(json.dumps(state))
    if tamper:
        with pytest.raises(ValueError, match="match"):
            load_baselines(source, "fixture/model", "cloudflare", DESIGN)
    else:
        assert load_baselines(source, "fixture/model", "cloudflare", DESIGN) == {
            "aware": answer,
            "unaware": answer,
        }
