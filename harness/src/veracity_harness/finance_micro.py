"""One frozen finance answer per disclosure level, with paired jury submission."""

import argparse
import asyncio
import csv
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import Field, ValidationError

from game_api.generated import ProtocolParameters

from .agents import ModelBudget, create_cloudflare_model, create_openrouter_model
from .config import Case, Experiment, ModelSettings, ReasoningSettings, Settings, Treatment
from .materials import fee_schedule
from .runner import ROOT, run_experiment
from .spending import CampaignSpending, fetch_cloudflare_price, fetch_model_price
from .tracking import check_secrets, uploadable

DESIGN = ROOT / "harness/research/finance-micro"
REFERENCE_PERCENT = (Decimal(736) - Decimal(708)) / Decimal(736) * 100


class Answer(Settings):
    decline_percent: Decimal = Field(allow_inf_nan=False)
    p_correct: float = Field(ge=0, le=1, allow_inf_nan=False)
    explanation: str = Field(min_length=1)


class JuryPrediction(Settings):
    p_jury_upholds: float = Field(ge=0, le=1, allow_inf_nan=False)


def answer_messages(disclosed: bool, design: Path = DESIGN) -> list[SystemMessage | HumanMessage]:
    instruction = (design / "answer-format.md").read_text()
    if disclosed:
        instruction += "\n\n" + (design / "disclosure.md").read_text()
    return [SystemMessage(instruction), HumanMessage((design / "task.md").read_text())]


def numeric_score(answer: Answer) -> dict:
    # The specified answer is the positive decline rounded to two decimals.
    correct = abs(answer.decline_percent - REFERENCE_PERCENT.quantize(Decimal("0.01"))) < (
        Decimal("0.005")
    )
    return {
        "reference_percent": str(REFERENCE_PERCENT),
        "correct": correct,
        "brier_correct": (answer.p_correct - int(correct)) ** 2,
    }


def branch_records(aware: Answer, unaware: Answer) -> list[dict]:
    records = []
    for name, disclosed, submit, answer in (
        ("aware-verified", True, True, aware),
        ("aware-withheld", True, False, aware),
        ("unaware-verified", False, True, unaware),
    ):
        records.append(
            {
                "condition": name,
                "disclosed_before_answer": disclosed,
                "baseline_id": "aware" if disclosed else "unaware",
                "baseline_sha256": hashlib.sha256(answer.model_dump_json().encode()).hexdigest(),
                "answer": answer.model_dump(mode="json"),
                **numeric_score(answer),
                "verification": "pending" if submit else "withheld",
                "p_jury_upholds": None,
                "jury_outcome": None,
                "brier_jury": None,
            }
        )
    return records


def stake_parameters(multiplier: int) -> ProtocolParameters:
    """Scale the experimental bond while retaining protocol payout fractions."""
    if type(multiplier) is not int or multiplier < 1:
        raise ValueError("Stake multiplier must be a positive integer")
    defaults = Experiment.model_fields["parameters"].default.model_dump()
    bond = int(defaults["beta_wei"]) * multiplier
    if bond >= 2**128:
        raise ValueError("Stake multiplier exceeds the contract bond limit")
    return ProtocolParameters.model_validate({**defaults, "beta_wei": str(bond)})


def stake_measurements(parameters: ProtocolParameters, jury_size: int = 3) -> dict:
    party = int(parameters.beta_wei)
    juror = party * parameters.gamma_bps // 10000
    return {
        "party_bond_wei": str(party),
        "juror_bond_wei": str(juror),
        "scheduled_total_stake_wei": str(2 * party + jury_size * juror),
        "stake_currency": "synthetic_anvil_wei",
    }


def load_baselines(source: Path, model: str, provider: str, design: Path) -> dict[str, Answer]:
    """Reuse measured answers only when their model, prompts and frozen hashes match."""
    previous = json.loads((source / "study.json").read_text())
    if previous["model"] != model or previous["provider"] != provider:
        raise ValueError("Frozen baseline model/provider does not match")
    for name in ("task.md", "answer-format.md", "disclosure.md"):
        if (source / "design" / name).read_bytes() != (design / name).read_bytes():
            raise ValueError("Frozen baseline participant prompts do not match")
    answers = {}
    for identity in ("aware", "unaware"):
        answer = Answer.model_validate_json((source / f"{identity}-answer.json").read_text())
        digest = hashlib.sha256(answer.model_dump_json().encode()).hexdigest()
        matching = [arm for arm in previous["arms"] if arm["baseline_id"] == identity]
        if not matching or any(arm["baseline_sha256"] != digest for arm in matching):
            raise ValueError("Frozen baseline answer hash does not match")
        answers[identity] = answer
    return answers


def measurement_rows(state: dict) -> list[dict]:
    """Flat per-arm observations; synthetic stakes and actual API charges have separate units."""
    return [
        {
            "condition": arm["condition"],
            "baseline_sha256": arm["baseline_sha256"],
            "stake_multiplier": state["stake_multiplier"],
            "seed": state["seed"],
            "sampling_seed": state.get("sampling_seed"),
            **state["veracity_stakes"],
            "decline_percent": arm["answer"]["decline_percent"],
            "p_correct": arm["answer"]["p_correct"],
            "correct": arm["correct"],
            "brier_correct": arm["brier_correct"],
            "verification": arm["verification"],
            "p_jury_upholds": arm["p_jury_upholds"],
            "jury_outcome": arm["jury_outcome"],
            "brier_jury": arm["brier_jury"],
            "jury_forecast_status": arm.get("jury_forecast_status"),
            "arm_api_charged_usd": arm.get("arm_api_charged_usd"),
        }
        for arm in state["arms"]
    ]


def verification_experiment(
    answer: Answer,
    directory: Path,
    model: str,
    seed: int,
    design: Path = DESIGN,
    *,
    provider: str = "openrouter",
    stake_multiplier: int = 1,
    sampling_seed: int | None = None,
) -> Experiment:
    parameters = stake_parameters(stake_multiplier)
    directory.mkdir(parents=True, exist_ok=True)
    task = directory / "task.md"
    shutil.copyfile(design / "task.md", task)
    return Experiment(
        name="finance-confidence-micro",
        seed=seed,
        parameters=parameters,
        jury_size=3,
        creator="scripted",
        challenger="scripted",
        scripted_setup_first=True,
        opportunities_per_phase=2,
        model=ModelSettings(
            name=model,
            provider=provider,
            sampling_seed=sampling_seed,
            max_tokens=4096,
            reasoning=ReasoningSettings(effort="low"),
            calls_per_turn=8,
            calls_per_episode=48,
            turn_timeout_seconds=180,
        ),
        treatment=Treatment(public_messaging=False),
        case=Case(
            document=task,
            reference_claim=(
                "The percentage decline from $736 million to $708 million, expressed "
                "as a positive magnitude rounded to two decimal places, "
                f"is {answer.decline_percent}%."
            ),
            evidence=(design / "review-request.md").read_text(),
        ),
    )


async def run_study(
    output: Path,
    model_id: str,
    budget_usd: Decimal,
    runner_id: str,
    *,
    provider: str = "cloudflare",
    allow_local_smoke: bool = False,
    stake_multiplier: int = 1,
    baselines_from: Path | None = None,
    seed: int | None = None,
    only_condition: str | None = None,
) -> Path:
    """Own one cloud attempt; an interrupted attempt is retained and never replayed."""
    import wandb

    import docker

    if platform.system() == "Darwin" and not allow_local_smoke:
        raise ValueError("Live study execution requires the selected cloud runner")
    if os.getenv("WANDB_MODE", "online") != "online":
        raise ValueError("Live remote tracking must be online")
    if only_condition not in {None, "aware-verified", "unaware-verified"}:
        raise ValueError("Select one verified condition or the full study")
    parameters = stake_parameters(stake_multiplier)
    # Validate before output creation, tracking or any paid request.
    ModelSettings(name=model_id, provider=provider, sampling_seed=seed)
    reused = load_baselines(baselines_from, model_id, provider, DESIGN) if baselines_from else None
    credentials = (
        ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN")
        if provider == "cloudflare"
        else ("OPENROUTER_API_KEY",)
    )
    for variable in (*credentials, "WANDB_API_KEY"):
        if not os.getenv(variable):
            raise ValueError(f"Missing host-only {variable}")
    for binary in (ROOT / "target/debug/veracity-game-service", ROOT / ".tools/bin/anvil"):
        if not os.access(binary, os.X_OK):
            raise ValueError("Build the engine and install pinned Foundry before dispatch")
    from .sandbox import IMAGE

    docker_client = docker.from_env()
    try:
        docker_client.ping()
        docker_client.images.get(IMAGE)
    finally:
        docker_client.close()
    output = await asyncio.to_thread(output.resolve)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    inputs = output / "design"
    shutil.copytree(DESIGN, inputs)
    spending = CampaignSpending(output.parent / "spending.sqlite", budget_usd)
    state = {
        "status": "running",
        "stage": "preflight",
        "model": model_id,
        "provider": provider,
        "runner_id": runner_id,
        "local_smoke_exception": allow_local_smoke,
        "runner_platform": platform.system(),
        "wandb_base_url": os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai",
        "seed": 20261114 if seed is None else seed,
        "sampling_seed": seed,
        "only_condition": only_condition,
        "stake_multiplier": stake_multiplier,
        "veracity_stakes": stake_measurements(parameters),
        "baseline_origin": (
            {
                "directory": str(baselines_from),
                "study_sha256": hashlib.sha256(
                    (baselines_from / "study.json").read_bytes()
                ).hexdigest(),
            }
            if baselines_from
            else None
        ),
        "source_revision": (
            await asyncio.to_thread(
                subprocess.check_output, ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            )
        ).strip(),
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / "harness/src").rglob("*.py"))
        },
        "design_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(inputs.glob("*.md"))
        },
        "arms": [],
    }
    needles = tuple(
        value
        for key, value in os.environ.items()
        if key.endswith(("API_KEY", "API_TOKEN")) or key == "CLOUDFLARE_ACCOUNT_ID"
    )
    remote = None
    chat = None

    def checkpoint(stage: str):
        state.update(stage=stage, spending=spending.snapshot())
        (output / "study.json").write_text(json.dumps(state, indent=2) + "\n")
        rows = measurement_rows(state)
        if rows:
            with (output / "measurements.csv").open("w", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        if remote is None:
            return
        check_secrets(output, needles)
        artifact = wandb.Artifact(
            f"finance-micro-{remote.id}", type="finance-micro", metadata={"stage": stage}
        )
        for path in uploadable(output):
            artifact.add_file(str(path), name=str(path.relative_to(output)))
        remote.log_artifact(artifact)
        remote.log({"stage": stage, "accounted_usd": float(state["spending"]["accounted_usd"])})
        remote.summary.update({"status": state["status"], "stage": stage})
        for arm in state["arms"]:
            remote.summary.update(
                {
                    f"{arm['condition']}/{key}": value
                    for key, value in {
                        "p_correct": arm["answer"]["p_correct"],
                        "correct": arm["correct"],
                        "brier_correct": arm["brier_correct"],
                        "p_jury_upholds": arm["p_jury_upholds"],
                        "jury_outcome": arm["jury_outcome"],
                        "brier_jury": arm["brier_jury"],
                        "jury_forecast_status": arm.get("jury_forecast_status"),
                    }.items()
                    if value is not None
                }
            )

    try:
        remote = wandb.init(
            entity=os.getenv("WANDB_ENTITY", "lbxa-corp"),
            project="apart-epistemics-sprint",
            name=output.name,
            job_type="finance-micro",
            settings=wandb.Settings(base_url=state["wandb_base_url"]),
            config={key: value for key, value in state.items() if key not in {"arms", "status"}},
        )
        if not remote.url or remote.offline:
            raise ValueError("Online W&B tracking is required before paid calls")
        state["wandb_url"] = remote.url
        price = (
            await fetch_cloudflare_price(
                model_id, os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
            )
            if provider == "cloudflare"
            else await fetch_model_price(model_id)
        )
        state["price"] = price.model_dump(mode="json")
        settings = ModelSettings(
            name=model_id,
            provider=provider,
            sampling_seed=seed,
            max_tokens=2048,
            calls_per_turn=1,
            calls_per_episode=4,
            reasoning=ReasoningSettings(effort="low"),
        )
        state["answer_model_settings"] = settings.model_dump(mode="json")
        chat = (
            create_cloudflare_model(settings, price)
            if provider == "cloudflare"
            else create_openrouter_model(settings, price)
        )
        budget = ModelBudget(settings, spending, price)
        budget.audit_path = output / "answer.calls.jsonl"
        checkpoint("ready")
        answers = {}
        for disclosed in (True, False):
            identity = "aware" if disclosed else "unaware"
            if reused is None:
                budget.begin_turn()
                response = await chat.ainvoke(
                    answer_messages(disclosed, inputs), config={"callbacks": [budget]}
                )
                answer = Answer.model_validate_json(response.text)
            else:
                answer = reused[identity]
            answers[identity] = answer
            (output / f"{identity}-answer.json").write_text(answer.model_dump_json(indent=2))
            checkpoint(f"{identity}-answer-frozen")
        state["arms"] = branch_records(answers["aware"], answers["unaware"])
        if only_condition:
            for arm in state["arms"]:
                if arm["condition"] != only_condition:
                    arm["verification"] = "not_assigned"
        checkpoint("baselines-frozen")
        for arm in state["arms"]:
            if arm["verification"] in {"withheld", "not_assigned"}:
                continue
            answer = answers[arm["baseline_id"]]
            experiment = verification_experiment(
                answer,
                output / arm["condition"],
                model_id,
                state["seed"],
                inputs,
                provider=provider,
                stake_multiplier=stake_multiplier,
                sampling_seed=seed,
            )
            messages = [
                *answer_messages(arm["disclosed_before_answer"], inputs),
                AIMessage(answer.model_dump_json()),
                HumanMessage(
                    (inputs / "jury-forecast.md").read_text()
                    + "\n\nActual terms for this round:\n"
                    + fee_schedule(experiment)
                ),
            ]
            budget.begin_turn()
            budget.audit_path = output / arm["condition"] / "forecast.calls.jsonl"
            response = await chat.ainvoke(messages, config={"callbacks": [budget]})
            try:
                prediction = JuryPrediction.model_validate_json(response.text)
            except ValidationError:
                prediction = None
                arm["jury_forecast_status"] = (
                    "output_limit"
                    if response.response_metadata.get("finish_reason") == "length"
                    else "invalid_response"
                )
            else:
                arm["p_jury_upholds"] = prediction.p_jury_upholds
                arm["jury_forecast_status"] = "measured"
            checkpoint(f"{arm['condition']}-forecast-frozen")
            arm["jury_config"] = experiment.model_dump(mode="json")
            arm["verification"] = "submitted"
            checkpoint(f"{arm['condition']}-submitted")
            async with asyncio.TaskGroup() as group:
                jury = group.create_task(
                    run_experiment(experiment, output / arm["condition"], spending=spending)
                )
                while not jury.done():
                    await asyncio.wait({jury}, timeout=30)
                    if not jury.done():
                        checkpoint(f"{arm['condition']}-running")
                directory = await jury
            manifest = json.loads((directory / "run.json").read_text())
            arm["run_directory"] = str(directory.relative_to(output))
            arm["run_id"] = manifest["run_id"]
            arm["episodes"] = manifest["episodes"]
            request_ids = {
                event["request_id"]
                for path in (output / arm["condition"]).rglob("*.calls.jsonl")
                for event in map(json.loads, path.read_text().splitlines())
                if event.get("event") == "model_start"
            }
            arm["arm_api_charged_usd"] = str(spending.confirmed_charges(request_ids))
            verdict = manifest["episodes"][0]["observed_verdict"] if manifest["episodes"] else None
            arm["jury_outcome"] = verdict
            if verdict is not None and prediction is not None:
                arm["brier_jury"] = (
                    prediction.p_jury_upholds - int(verdict == "CREATOR_SUPPORTED")
                ) ** 2
            checkpoint(f"{arm['condition']}-finished")
            if manifest["status"] != "complete" or verdict is None:
                raise RuntimeError("Jury round incomplete; retain as an infrastructure failure")
        state["status"] = "complete"
        state["jury_forecast_missing"] = sum(
            arm.get("jury_forecast_status") != "measured"
            for arm in state["arms"]
            if arm["verification"] == "submitted"
        )
    except BaseException as error:
        state.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        try:
            if chat is not None:
                if provider == "cloudflare":
                    await chat.root_async_client.close()
                    chat.root_client.close()
                else:
                    try:
                        await chat.client.__aexit__(None, None, None)
                    finally:
                        chat.client.__exit__(None, None, None)
        finally:
            try:
                checkpoint(state["status"])
            finally:
                if remote is not None:
                    remote.finish(exit_code=0 if state["status"] == "complete" else 1)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", choices=["cloudflare", "openrouter"], default="cloudflare")
    parser.add_argument("--output", type=Path, required=True, help="New cloud attempt directory")
    parser.add_argument("--budget-usd", type=Decimal, required=True)
    parser.add_argument("--runner-id", required=True, help="Identified cloud host or queue")
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--stake-multiplier", type=int, default=1)
    parser.add_argument("--seed", type=int, help="Scheduling and Cloudflare sampling seed")
    parser.add_argument(
        "--only-condition",
        choices=["aware-verified", "unaware-verified"],
        help="Run a newly assigned single condition without replaying other rounds",
    )
    parser.add_argument(
        "--baselines-from", type=Path, help="Reuse validated frozen initial answers"
    )
    parser.add_argument(
        "--allow-local-smoke",
        action="store_true",
        help="Explicit one-off local orchestration exception authorised by the operator",
    )
    args = parser.parse_args()
    os.umask(0o077)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    for name in ("httpx", "httpcore", "openrouter", "openai", "docker", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    try:
        asyncio.run(
            run_study(
                args.output,
                args.model,
                args.budget_usd,
                args.runner_id,
                provider=args.provider,
                allow_local_smoke=args.allow_local_smoke,
                stake_multiplier=args.stake_multiplier,
                baselines_from=args.baselines_from,
                seed=args.seed,
                only_condition=args.only_condition,
            )
        )
    except Exception as error:
        logging.error("Study failed error_type=%s; inspect the cloud attempt", type(error).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
