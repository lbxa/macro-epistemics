"""Selected arithmetic-context diagnostics, kept separate from sector verdicts."""

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import platform
import random
import shutil
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .agents import create_cloudflare_model
from .config import ModelSettings, ReasoningSettings
from .contract_micro import Ballot
from .runner import ROOT
from .sector_cases import JURY_MODEL, MODELS, SEEDS, Answer, Defence, SectorCase, participant_task
from .sector_study import PHASE_CAPS, SectorStudy, initial_messages, job_key
from .spending import fetch_cloudflare_price
from .tracking import check_secrets

BRANCH_ID = "11c495e81bb48bcc53c14f421794"
CONDITIONS = ("calculate", "claim_only", "defended", "checked_evidence")
CHECKED_EVIDENCE = (
    "Checked arithmetic: 1084 * (100 + 8 + 0.51) = "
    "108400 + 8672 + 552.84 = 117624.84. The published product 117628.84 "
    "is four too large. Check this decomposition against the source inputs."
)
DESIGN = ROOT / "harness/research/sector-expansion"


def probe_messages(case, record, condition, *, original_text=None):
    if condition == "author_checked":
        if not original_text:
            raise ValueError("An author branch requires the exact frozen initial text")
        return [
            *initial_messages(case),
            AIMessage(original_text),
            HumanMessage(
                (DESIGN / "defence.md").read_text()
                + "\n\nOriginal published claim:\n"
                + record["claim"]
                + "\n\nChallenge:\n"
                + record["challenge"]
                + "\n\n"
                + CHECKED_EVIDENCE
            ),
        ], Defence
    if condition not in CONDITIONS:
        raise ValueError("Unknown diagnostic condition")
    if condition == "calculate":
        return [
            SystemMessage((DESIGN / "initial.md").read_text()),
            HumanMessage("Calculate 1084 * 108.51. Give the exact product, with empty scale."),
        ], Answer
    challenge = record["challenge"]
    if condition == "checked_evidence":
        challenge += "\n\n" + CHECKED_EVIDENCE
    context = participant_task(case) + "\n\nORIGINAL claim:\n" + record["claim"]
    context += "\n\nChallenge:\n" + challenge
    if condition != "claim_only":
        defence = Defence.model_validate(record["defence"]["parsed"])
        visible = {
            key: value
            for key, value in defence.model_dump(mode="json").items()
            if key not in {"confidence_correct", "p_original_correct", "p_jury_upholds"}
        }
        context += "\n\nAuthor's defence:\n" + json.dumps(visible)
    return [SystemMessage((DESIGN / "jury.md").read_text()), HumanMessage(context)], Ballot


async def run(main, output, cap, deadline):
    import wandb

    if platform.system() != "Linux":
        raise ValueError("Diagnostic model calls require the cloud runner")
    progress = json.loads((main / "progress.json").read_text())
    if progress["status"] not in {"complete", "complete_with_failures"}:
        raise ValueError("Finish the primary study before diagnostic dispatch")
    cases_bytes = (main / "cases.json").read_bytes()
    parent = json.loads((main / "study.json").read_text())
    if hashlib.sha256(cases_bytes).hexdigest() != parent["cases_sha256"]:
        raise ValueError("The primary source manifest changed")
    branch = next(
        json.loads(line)
        for line in (main / "branch.jsonl").read_text().splitlines()
        if json.loads(line)["id"] == BRANCH_ID
    )
    case = next(
        SectorCase.model_validate(c)
        for c in json.loads(cases_bytes)
        if c["case_id"] == branch["payload"]["case_id"]
    )
    record = branch["result"]
    initial = next(
        json.loads(line)
        for line in (main / "initial.jsonl").read_text().splitlines()
        if json.loads(line)["payload"]["case_id"] == case.case_id
        and json.loads(line)["payload"]["model"] == branch["payload"]["model"]
    )
    original_text = initial["result"]["call"]["text"]
    if (
        case.task_id != "finqa:GPN/2018/page_94.pdf-2"
        or case.reference != "117624.84"
        or record["defence"]["parsed"]["answer"] != "117628.84"
        or hashlib.sha256(original_text.encode()).hexdigest() != record["baseline_sha256"]
        or Decimal(1084) * Decimal("108.51") != Decimal("117624.84")
        or Decimal(108400) + Decimal(8672) + Decimal("552.84") != Decimal("117624.84")
    ):
        raise ValueError("The frozen arithmetic diagnostic source changed")
    study = SectorStudy(output, cap, deadline)
    frozen_hash = hashlib.sha256(json.dumps(branch, sort_keys=True).encode()).hexdigest()
    sources = [
        Path(__file__),
        Path(__file__).with_name("sector_study.py"),
        Path(__file__).with_name("sector_cases.py"),
        DESIGN / "initial.md",
        DESIGN / "defence.md",
        DESIGN / "jury.md",
        DESIGN / "ARITHMETIC-PROBE.md",
    ]
    source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    manifest_path = output / "study.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if (
            manifest["parent_cases_sha256"] != parent["cases_sha256"]
            or manifest["api_cap_usd"] != str(cap)
            or manifest["source_branch_sha256"] != frozen_hash
            or manifest["source_sha256"] != source_hashes
        ):
            raise ValueError("Diagnostic resume cannot change the source or cap")
    else:
        manifest = {
            "protocol": "arithmetic-context-v2-posthoc",
            "wandb_run_id": uuid4().hex[:16],
            "parent_run_id": parent["wandb_run_id"],
            "parent_cases_sha256": parent["cases_sha256"],
            "source_branch_id": BRANCH_ID,
            "source_branch_sha256": frozen_hash,
            "source_sha256": source_hashes,
            "models": [JURY_MODEL, MODELS[0], MODELS[1]],
            "judge_models": [JURY_MODEL, MODELS[0]],
            "author_model": MODELS[1],
            "conditions": CONDITIONS,
            "author_condition": "author_checked",
            "phase_max_tokens": PHASE_CAPS,
            "seeds": SEEDS,
            "planned_calls": 125,
            "api_cap_usd": str(cap),
            "deadline_utc": datetime.fromtimestamp(deadline, UTC).isoformat(),
            "started_at": datetime.now(UTC).isoformat(),
            "engine_scope": "standalone diagnostic judgments; no new settlements",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        (output / "source.json").write_text(
            json.dumps(
                {"case": case.model_dump(mode="json"), "branch": branch, "initial": initial},
                indent=2,
            )
            + "\n"
        )
        (output / "source").mkdir(exist_ok=True)
        for path in sources:
            shutil.copy2(path, output / "source" / path.name)
    remote = wandb.init(
        entity="lbxa-corp",
        project="apart-epistemics-sprint",
        job_type="arithmetic-diagnostic",
        id=manifest["wandb_run_id"],
        resume="allow",
        config=manifest,
        settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
    )

    def checkpoint(final=False, interrupted=False):
        rows = study.journal.rows("probe")
        with (output / "probe.jsonl").open("w") as file:
            for row in rows:
                file.write(json.dumps(row) + "\n")
        state = {
            "status": "interrupted"
            if interrupted
            else "complete_with_failures"
            if final and any(r["status"] != "complete" for r in rows)
            else "complete"
            if final
            else "running",
            "assigned_calls": manifest["planned_calls"],
            "observed_calls": len(rows),
            "counts": dict(Counter(r["status"] for r in rows)),
            "spending": study.spending.snapshot(),
        }
        (output / "progress.json").write_text(json.dumps(state, indent=2) + "\n")
        remote.log(
            {"observed_calls": len(rows), "complete_calls": state["counts"].get("complete", 0)}
        )
        remote.summary.update(state)
        if final:
            needles = [
                os.getenv(key, "")
                for key in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID", "WANDB_API_KEY")
            ]
            check_secrets(output, [key for key in needles if key])
            artifact = wandb.Artifact(
                "arithmetic-diagnostic-" + remote.id, type="arithmetic-diagnostic"
            )
            for name in (
                "study.json",
                "source.json",
                "probe.jsonl",
                "progress.json",
            ):
                artifact.add_file(str(output / name), name=name)
            for path in sorted((output / "source").iterdir()):
                artifact.add_file(str(path), name="source/" + path.name)
            remote.log_artifact(artifact)
        print(json.dumps(state), flush=True)

    async def observation(model, condition, seed, juror):
        identity = job_key("arithmetic-context-v2", model, condition, seed, juror)
        payload = {
            "model": model,
            "condition": condition,
            "seed": seed,
            "juror": juror,
            "role": "author"
            if condition == "author_checked"
            else "calculator"
            if condition == "calculate"
            else "judge",
        }
        if not study.journal.begin(identity, "probe", payload):
            return
        messages, schema = probe_messages(case, record, condition, original_text=original_text)
        result = await study.invoke(
            model,
            messages,
            identity + "-call",
            seed if condition == "author_checked" else 20000 + seed * 10 + juror,
            schema,
        )
        study.journal.finish(
            identity, "complete" if result["status"] == "complete" else "failed", result
        )
        if (
            sum(study.journal.counts().get(key, 0) for key in ("probe:complete", "probe:failed"))
            % 10
            == 0
        ):
            checkpoint()

    finished = False
    try:
        for model in manifest["models"]:
            price = await fetch_cloudflare_price(
                model, os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
            )
            settings = ModelSettings(
                name=model,
                provider="cloudflare",
                max_tokens=4096,
                reasoning=ReasoningSettings(effort="low"),
                text_input_token_ceiling=min(131072, price.context_length),
                calls_per_turn=1,
                calls_per_episode=1,
                turn_timeout_seconds=120,
                requests_per_minute=240 if model == JURY_MODEL else 18,
            )
            study.prices[model] = price
            study.clients[model] = (create_cloudflare_model(settings, price), settings)
        manifest["settings"] = {m: s.model_dump(mode="json") for m, (_, s) in study.clients.items()}
        manifest["prices"] = {m: p.model_dump(mode="json") for m, p in study.prices.items()}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        remote.config.update({"settings": manifest["settings"], "prices": manifest["prices"]})
        jobs = [
            (m, c, s, j)
            for m in manifest["judge_models"]
            for c in CONDITIONS
            for s in SEEDS
            for j in (1, 2, 3)
        ]
        jobs.extend((manifest["author_model"], "author_checked", seed, 0) for seed in SEEDS)
        random.Random(20261116).shuffle(jobs)
        await asyncio.gather(*(observation(*job) for job in jobs))
        checkpoint(final=True)
        finished = True
    finally:
        if not finished:
            checkpoint(interrupted=True)
        remote.finish(exit_code=0 if finished else 1)
        for client, _ in study.clients.values():
            await client.root_async_client.close()
            client.root_client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-cap", type=Decimal, default=Decimal("10"))
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--dotenv", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    with (ROOT / ".harness/sector-run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        asyncio.run(
            run(
                args.main,
                args.output,
                args.api_cap,
                datetime.fromisoformat(args.deadline).timestamp(),
            )
        )


if __name__ == "__main__":
    main()
