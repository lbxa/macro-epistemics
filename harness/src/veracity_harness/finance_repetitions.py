"""Bounded five-seed replication of the existing frozen-answer finance study."""

import argparse
import asyncio
import csv
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from game_api.generated import EpisodeView

from .config import Experiment
from .finance_micro import DESIGN, load_baselines, measurement_rows, stake_measurements
from .runner import ROOT
from .spending import CampaignSpending
from .tracking import check_secrets

SEEDS = tuple(range(20261114, 20261119))
STAKES = (1, 10, 100, 1000)
MODEL = "@cf/deepseek-ai/deepseek-v4-pro-0813"
CONDITIONS = ("aware-verified", "aware-withheld", "unaware-verified")


def round_votes(episode: EpisodeView) -> dict:
    """Admit only three revealed votes consistent with the settled contract state."""
    if (
        episode.phase not in {"SETTLED_CREATOR", "SETTLED_CHALLENGER"}
        or len(episode.jurors) != 3
        or len({juror.actor_id for juror in episode.jurors}) != 3
        or any(not juror.revealed or juror.verdict is None for juror in episode.jurors)
    ):
        raise ValueError("Expected a settled round with three distinct revealed jurors")
    counts = Counter(juror.verdict for juror in episode.jurors)
    support = counts["CREATOR_SUPPORTED"]
    reject = counts["CHALLENGER_SUPPORTED"]
    if (support, reject) != (episode.creator_votes, episode.challenger_votes):
        raise ValueError("Reveals and contract vote counts disagree")
    outcome = "CREATOR_SUPPORTED" if support > reject else "CHALLENGER_SUPPORTED"
    if episode.phase != ("SETTLED_CREATOR" if support > reject else "SETTLED_CHALLENGER"):
        raise ValueError("Majority and settlement disagree")
    return {"support_votes": support, "reject_votes": reject, "jury_outcome": outcome}


def collect_study(directory: Path, assignment: dict, baselines: dict) -> tuple[list, dict]:
    """Validate assignment identity and retain per-arm outcomes without imputing missing data."""
    study_file = directory / "study.json"
    state = json.loads(study_file.read_text())
    seed, stakes = assignment["seed"], assignment["stake_multiplier"]
    if (
        state["model"],
        state["provider"],
        state["seed"],
        state.get("sampling_seed"),
        state["stake_multiplier"],
    ) != (MODEL, "cloudflare", seed, seed, stakes):
        raise ValueError("Study does not match the planned provider, seed and stakes")
    rows = measurement_rows(state)
    if len(rows) != 3 or {row["condition"] for row in rows} != set(CONDITIONS):
        raise ValueError("Study must retain all three assigned conditions")
    evidence_hashes = {}
    for arm, row in zip(state["arms"], rows, strict=True):
        expected = baselines[arm["baseline_id"]].model_dump_json().encode()
        if hashlib.sha256(expected).hexdigest() != arm["baseline_sha256"]:
            raise ValueError("Frozen baseline changed")
        if arm["answer"] != baselines[arm["baseline_id"]].model_dump(mode="json"):
            raise ValueError("Frozen answer differs from its hash")
        row.update(
            attempt=directory.name,
            wandb_url=state["wandb_url"],
            study_status=state["status"],
            support_votes=None,
            reject_votes=None,
        )
        if arm["verification"] == "withheld" or arm["jury_outcome"] is None:
            continue
        config = Experiment.model_validate(arm["jury_config"])
        if (config.seed, config.model.sampling_seed, config.jury_size) != (seed, seed, 3):
            raise ValueError("Jury configuration does not match the seed assignment")
        episode_id = arm["episodes"][0]["episode_id"]
        evidence_file = directory / arm["run_directory"] / episode_id / "evidence.json"
        episode = EpisodeView.model_validate(json.loads(evidence_file.read_text())["episode"])
        votes = round_votes(episode)
        if votes["jury_outcome"] != arm["jury_outcome"]:
            raise ValueError("Study verdict disagrees with contract evidence")
        actual_stakes = stake_measurements(episode.configuration.parameters)
        if (
            actual_stakes != state["veracity_stakes"]
            or episode.juror_bond_wei != actual_stakes["juror_bond_wei"]
            or episode.total_deposited_wei != actual_stakes["scheduled_total_stake_wei"]
        ):
            raise ValueError("Observed deposits do not match the planned stakes")
        row.update(votes)
        evidence_hashes[str(evidence_file.relative_to(directory))] = hashlib.sha256(
            evidence_file.read_bytes()
        ).hexdigest()
    return rows, {
        "attempt": directory.name,
        "url": state["wandb_url"],
        "study_sha256": hashlib.sha256(study_file.read_bytes()).hexdigest(),
        "evidence_sha256": evidence_hashes,
    }


async def run_campaign(output: Path, baselines_from: Path, runner_id: str):
    import wandb

    if os.getenv("WANDB_MODE", "online") != "online":
        raise ValueError("Online tracking is required")
    baselines = load_baselines(baselines_from, MODEL, "cloudflare", DESIGN)
    spending = CampaignSpending(output.parent / "spending.sqlite", Decimal(100))
    await asyncio.to_thread(output.mkdir, mode=0o700, parents=False, exist_ok=False)
    revision = await asyncio.to_thread(
        subprocess.check_output, ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    )
    assignments = [
        {
            "seed": seed,
            "stake_multiplier": stakes,
            "status": "pending",
            "attempt": f"seed-{seed}-stakes-{stakes}x",
        }
        for seed in SEEDS
        for stakes in STAKES
    ]
    plan = {
        "status": "running",
        "model": MODEL,
        "provider": "cloudflare",
        "seeds": SEEDS,
        "stake_multipliers": STAKES,
        "concurrency": 2,
        "runner_id": runner_id,
        "local_smoke_exception": True,
        "baseline_origin": str(baselines_from),
        "initial_answers": 2,
        "source_tasks": 1,
        "api_cap_usd": "100",
        "assignments": assignments,
        "source_revision": revision.strip(),
    }
    # Package existing authored source and dependency locks, never manufacture source text.
    archive = output / "source.zip"
    sources = [
        *sorted((ROOT / "harness/src").rglob("*.py")),
        *sorted(DESIGN.glob("*.md")),
        ROOT / "harness/pyproject.toml",
        ROOT / "harness/uv.lock",
        ROOT / "CONSTITUTION.md",
    ]
    plan["source_sha256"] = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sources:
            bundle.write(path, str(path.relative_to(ROOT)))
    needles = tuple(
        value
        for key, value in os.environ.items()
        if key.endswith(("API_KEY", "API_TOKEN")) or key == "CLOUDFLARE_ACCOUNT_ID"
    )
    for path in sources:
        if any(value.encode() in path.read_bytes() for value in needles if value):
            raise ValueError("Credential detected in source archive")
    remote = wandb.init(
        entity=os.getenv("WANDB_ENTITY", "lbxa-corp"),
        project="apart-epistemics-sprint",
        name=output.name,
        job_type="finance-repetitions",
        settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
        config={key: value for key, value in plan.items() if key != "assignments"},
    )
    if not remote.url or remote.offline:
        raise ValueError("Online tracking is required before dispatch")
    plan["wandb_url"] = remote.url
    rows, provenance = [], []

    def checkpoint():
        plan["spending"] = spending.snapshot()
        plan["cohort"] = provenance
        (output / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
        public = [output / "plan.json", archive]
        if rows:
            csv_path = output / "measurements.csv"
            with csv_path.open("w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(
                    sorted(rows, key=lambda r: (r["seed"], r["stake_multiplier"], r["condition"]))
                )
            public.append(csv_path)
        check_secrets(output, needles)
        artifact = wandb.Artifact(f"finance-repetitions-{remote.id}", type="experiment-comparison")
        for path in public:
            artifact.add_file(str(path), name=path.name)
        remote.log_artifact(artifact)
        counts = Counter(item["status"] for item in assignments)
        remote.log(
            {
                **{
                    f"assignments/{key}": counts[key]
                    for key in ("pending", "running", "complete", "failed")
                },
                "accounted_usd": float(plan["spending"]["accounted_usd"]),
            }
        )
        remote.summary.update(
            {"status": plan["status"], "completed": counts["complete"], "failed": counts["failed"]}
        )

    semaphore = asyncio.Semaphore(2)

    async def assigned_study(item):
        async with semaphore:
            item["status"] = "running"
            checkpoint()  # Persist and publish intent before the paid child starts.
            destination = output.parent / item["attempt"]
            log_path = output.parent / f"{item['attempt']}.private.log"
            try:
                with log_path.open("xb") as log:
                    child = await asyncio.create_subprocess_exec(
                        sys.executable,
                        "-m",
                        "veracity_harness.finance_micro",
                        "--provider",
                        "cloudflare",
                        "--model",
                        MODEL,
                        "--output",
                        str(destination),
                        "--budget-usd",
                        "100",
                        "--runner-id",
                        runner_id,
                        "--allow-local-smoke",
                        "--stake-multiplier",
                        str(item["stake_multiplier"]),
                        "--seed",
                        str(item["seed"]),
                        "--baselines-from",
                        str(baselines_from),
                        cwd=ROOT,
                        stdout=log,
                        stderr=log,
                    )
                    item["pid"] = child.pid
                    await child.wait()
                item["exit_code"] = child.returncode
                measured, source = collect_study(destination, item, baselines)
                rows.extend(measured)
                provenance.append(source)
                item["status"] = "complete" if child.returncode == 0 else "failed"
            except Exception as error:
                item.update(status="failed", error_type=type(error).__name__)
            checkpoint()

    try:
        checkpoint()
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(assigned_study(item)) for item in assignments]
            pending = set(tasks)
            while pending:
                _, pending = await asyncio.wait(
                    pending, timeout=30, return_when=asyncio.FIRST_COMPLETED
                )
                checkpoint()
        plan["status"] = (
            "complete" if all(a["status"] == "complete" for a in assignments) else "failed"
        )
    finally:
        checkpoint()
        remote.finish(exit_code=0 if plan["status"] == "complete" else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baselines-from", type=Path, required=True)
    parser.add_argument("--runner-id", required=True)
    parser.add_argument("--dotenv", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    asyncio.run(run_campaign(args.output.resolve(), args.baselines_from.resolve(), args.runner_id))


if __name__ == "__main__":
    main()
