"""Frozen-source numerical judge-context replication, separate from sector scores."""

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import platform
import random
from collections import Counter
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path
from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field

from .agents import create_cloudflare_model
from .config import ModelSettings, ReasoningSettings
from .contract_micro import Ballot
from .runner import ROOT
from .sector_cases import JURY_MODEL, MODELS, SEEDS, Defence, SectorCase, numeric, participant_task
from .sector_study import DESIGN, SectorStudy, job_key
from .spending import fetch_cloudflare_price
from .tracking import check_secrets

PROTOCOL = "numeric-judge-context-v1"
CONDITIONS = ("claim_only", "defended", "checked_evidence")
JUDGES = (JURY_MODEL, MODELS[0])
AMBIGUOUS_TASK = "mathdial:5000751/1/row495"
HISTORICAL_TRIGGER = "finqa:GPN/2018/page_94.pdf-2"
PARENT_RUN = "da7e42f28ba54247"
PARENT_ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128"
PARENT_DIGEST = "7d7230ca4d18fc07c1bb8e0009cdbc1d"
PARENT_HASHES = {
    "cases.json": "223ffe96bdc2de750b6dc3098671cf281d29dfd4758a9811eddba63cc4b68155",
    "branch.jsonl": "ec6e9d9c52d955bb65e9a8cebc62c4b533a3caab8b260737bcc68fb4d6710515",
    "study.json": "6463f684dfe4506dbe075271106c681b76f223c56867ea4359d9d6ed2d4a3461",
}


class CalculationStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    operation: Literal["add", "subtract", "multiply", "divide"]
    operands: tuple[str, str]
    result: str

    def checked_value(self):
        left, right = map(Fraction, self.operands)
        value = {
            "add": lambda: left + right,
            "subtract": lambda: left - right,
            "multiply": lambda: left * right,
            "divide": lambda: left / right,
        }[self.operation]()
        if value != Fraction(self.result):
            raise ValueError("Checked arithmetic step has an incorrect result")
        symbol = {"add": "+", "subtract": "-", "multiply": "*", "divide": "/"}[self.operation]
        return value, f"{self.operands[0]} {symbol} {self.operands[1]} = {self.result}"


class CalculationProof(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    task_id: str
    source_assertions: tuple[str, ...] = Field(min_length=1)
    steps: tuple[CalculationStep, ...] = Field(min_length=1)
    final_value: str
    scale: Literal["", "percent", "thousand", "million", "billion"]
    round_places: int | None = Field(default=None, ge=0, le=12)
    explanation: str = Field(min_length=1)

    def checked_text(self, case):
        if self.task_id != case.task_id:
            raise ValueError("Proof belongs to a different source")
        if self.scale != case.scale:
            raise ValueError("Proof scale differs from the frozen task scale")
        if Fraction(self.final_value) != Fraction(numeric(case.reference)):
            raise ValueError("Proof final value disagrees with the frozen task reference")
        source = case.document + "\n" + case.task
        if any(quote not in source for quote in self.source_assertions):
            raise ValueError("Proof input is absent from the frozen source")
        checked = [step.checked_value() for step in self.steps]
        value = checked[-1][0]
        if self.round_places is None:
            if value != Fraction(self.final_value):
                raise ValueError("Proof final answer differs from its exact calculation")
        else:
            decimal = Decimal(value.numerator) / Decimal(value.denominator)
            rounded = decimal.quantize(
                Decimal(1).scaleb(-self.round_places), rounding=ROUND_HALF_UP
            )
            if rounded != Decimal(self.final_value):
                raise ValueError("Proof final answer has incorrect declared rounding")
        return (
            "Checked calculation from the supplied inputs (operator arithmetic check; "
            "not independent human adjudication):\n"
            + "\n".join(quote for quote in self.source_assertions)
            + "\n"
            + "; ".join(text for _, text in checked)
            + f". Final answer: {self.final_value}, scale {self.scale or 'unscaled'}. "
            + self.explanation
        )

    def check_original(self, record):
        original = record["original_answer"]
        matches = original["scale"] == self.scale and Fraction(
            numeric(original["answer"])
        ) == Fraction(self.final_value)
        if matches != record["initial_correct"]:
            raise ValueError("Proof disagrees with the declared original truth class")
        return matches


def select_sources(cases, branches, *, excluded_tasks):
    """One hash-selected frozen defence per mismatch source, plus benchmark controls."""
    candidates = {False: {}, True: {}}
    for branch in branches:
        case = cases[branch["payload"]["case_id"]]
        result = branch.get("result") or {}
        defence = result.get("defence") or {}
        original = result.get("original_answer") or {}
        right = result.get("initial_correct")
        if (
            case.labels
            or case.task_id in excluded_tasks
            or branch["payload"]["arm"] != "audit"
            or branch["payload"]["seed"] != SEEDS[0]
            or defence.get("status") != "complete"
            or (defence.get("parsed") or {}).get("original_still_supported") is not True
            or right not in candidates
        ):
            continue
        if right and (
            numeric(original["answer"]) != numeric(case.reference)
            or original["scale"] != case.scale
        ):
            continue
        candidates[right].setdefault(case.group_id, []).append((case, branch))

    def rank(value):
        return hashlib.sha256((PROTOCOL + ":" + value).encode()).hexdigest()

    errors = {
        group: min(rows, key=lambda row: rank(row[1]["id"]))
        for group, rows in candidates[False].items()
    }
    selected = [row for _, row in sorted(errors.items(), key=lambda row: rank(row[0]))]
    for benchmark, count in sorted(Counter(case.benchmark for case, _ in selected).items()):
        controls = {
            group: min(rows, key=lambda row: rank(row[1]["id"]))
            for group, rows in candidates[True].items()
            if group not in errors and rows[0][0].benchmark == benchmark
        }
        if len(controls) < count:
            raise ValueError("Insufficient independent source controls in the same benchmark")
        selected.extend(
            row for _, row in sorted(controls.items(), key=lambda row: rank(row[0]))[:count]
        )
    return selected


def extension_messages(case, record, proof, condition):
    if condition not in CONDITIONS:
        raise ValueError("Unknown judge extension condition")
    context = (
        participant_task(case)
        + "\n\nORIGINAL claim:\n"
        + record["claim"]
        + "\n\nChallenge:\n"
        + record["challenge"]
    )
    if condition != "claim_only":
        defence = Defence.model_validate(record["defence"]["parsed"])
        visible = {
            key: value
            for key, value in defence.model_dump(mode="json").items()
            if key not in {"confidence_correct", "p_original_correct", "p_jury_upholds"}
        }
        context += "\n\nAuthor's defence:\n" + json.dumps(visible)
    if condition == "checked_evidence":
        context += "\n\n" + proof.checked_text(case)
    return [SystemMessage((DESIGN / "jury.md").read_text()), HumanMessage(context)]


def prepare_sources(parent, proof_path):
    names = ("cases.json", "branch.jsonl", "study.json", "progress.json")
    parent_hashes = {
        name: hashlib.sha256((parent / name).read_bytes()).hexdigest() for name in names
    }
    if any(parent_hashes[name] != expected for name, expected in PARENT_HASHES.items()):
        raise ValueError("Parent bytes differ from the admitted v128 study")
    study = json.loads((parent / "study.json").read_text())
    if study["wandb_run_id"] != PARENT_RUN or study["cases_sha256"] != parent_hashes["cases.json"]:
        raise ValueError("Parent run identity differs from the admitted study")
    progress = json.loads((parent / "progress.json").read_text())
    if progress["status"] not in {"complete", "complete_with_failures"}:
        raise ValueError("The parent study must be complete before source selection")
    cases = {
        case["case_id"]: SectorCase.model_validate(case)
        for case in json.loads((parent / "cases.json").read_text())
    }
    branches = [json.loads(line) for line in (parent / "branch.jsonl").read_text().splitlines()]
    audit_path = DESIGN / "source-audit.json"
    excluded = {case["task_id"] for case in json.loads(audit_path.read_text())["cases"]}
    excluded.add(AMBIGUOUS_TASK)
    proofs = {
        proof["task_id"]: CalculationProof.model_validate(proof)
        for proof in json.loads(proof_path.read_text())
    }
    selected = []
    for case, branch in select_sources(cases, branches, excluded_tasks=excluded):
        proof = proofs[case.task_id]
        proof.checked_text(case)
        operator_correct = proof.check_original(branch["result"])
        selected.append(
            {
                "case": case.model_dump(mode="json"),
                "branch": branch,
                "proof": proof.model_dump(mode="json"),
                "historical_trigger_source": case.task_id == HISTORICAL_TRIGGER,
                "operator_check_original_correct": operator_correct,
            }
        )
    if set(proofs) != {row["case"]["task_id"] for row in selected}:
        raise ValueError("Proof cards must cover exactly the selected sources")
    return selected, {
        **parent_hashes,
        "source-audit.json": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
    }


async def run(parent, proof_path, output, cap, deadline):
    import wandb

    if platform.system() != "Linux":
        raise ValueError("Judge extension calls require the configured Linux cloud runner")
    if cap <= 0 or cap > Decimal("20"):
        raise ValueError("The authorized judge extension cap is at most US$20")
    selected, parent_hashes = prepare_sources(parent, proof_path)
    sources = [
        Path(__file__),
        Path(__file__).with_name("sector_study.py"),
        Path(__file__).with_name("sector_cases.py"),
        Path(__file__).with_name("sector_objections.py"),
        Path(__file__).with_name("agents.py"),
        Path(__file__).with_name("config.py"),
        Path(__file__).with_name("spending.py"),
        proof_path,
        DESIGN / "jury.md",
        DESIGN / "peer-review/judge-protocol.md",
    ]
    source_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    config = {
        "protocol": PROTOCOL,
        "parent_artifact": PARENT_ARTIFACT,
        "parent_artifact_digest": PARENT_DIGEST,
        "parent_hashes": parent_hashes,
        "source_hashes": source_hashes,
        "selected_branches": [row["branch"]["id"] for row in selected],
        "judges": JUDGES,
        "conditions": CONDITIONS,
        "seeds": SEEDS,
        "jurors": (1, 2, 3),
        "planned_calls": len(selected) * len(JUDGES) * len(CONDITIONS) * len(SEEDS) * 3,
        "api_cap_usd": str(cap),
        "deadline_utc": datetime.fromtimestamp(deadline, UTC).isoformat(),
        "source_truth_classes": {
            row["branch"]["id"]: row["operator_check_original_correct"] for row in selected
        },
        "engine_scope": "standalone judge judgments; no new Veracity settlements",
        "selection_scope": (
            "post hoc source-selected numerical replication; categorical cases pending adjudication"
        ),
    }
    study = SectorStudy(output, cap, deadline)
    manifest_path = output / "study.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for key, value in config.items():
            if manifest[key] != json.loads(json.dumps(value)):
                raise ValueError("Judge extension resume cannot change frozen inputs or cap")
    else:
        manifest = {
            **config,
            "wandb_run_id": uuid4().hex[:16],
            "started_at": datetime.now(UTC).isoformat(),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        (output / "sources.json").write_text(json.dumps(selected, indent=2) + "\n")
    remote = wandb.init(
        entity="lbxa-corp",
        project="apart-epistemics-sprint",
        job_type="numeric-judge-extension",
        id=manifest["wandb_run_id"],
        resume="allow",
        config=manifest,
        settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
    )
    if remote.offline or not remote.url:
        raise ValueError("Live tracking must precede paid dispatch")

    def checkpoint(final=False, interrupted=False):
        rows = study.journal.rows("judge-extension")
        (output / "observations.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
        state = {
            "status": "interrupted"
            if interrupted
            else "complete_with_failures"
            if final and any(row["status"] != "complete" for row in rows)
            else "complete"
            if final
            else "running",
            "assigned_calls": manifest["planned_calls"],
            "observed_calls": len(rows),
            "counts": dict(Counter(row["status"] for row in rows)),
            "spending": study.spending.snapshot(),
        }
        (output / "progress.json").write_text(json.dumps(state, indent=2) + "\n")
        remote.log(
            {"observed_calls": len(rows), "complete_calls": state["counts"].get("complete", 0)}
        )
        remote.summary.update(state)
        if final:
            if any(
                hashlib.sha256(path.read_bytes()).hexdigest() != source_hashes[path.name]
                for path in sources
            ):
                raise ValueError("Judge extension source code changed during collection")
            needles = [
                os.getenv(key, "")
                for key in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID", "WANDB_API_KEY")
            ]
            check_secrets(output, [key for key in needles if key])
            artifact = wandb.Artifact(
                "numeric-judge-extension-" + remote.id, type="numeric-judge-extension"
            )
            for name in ("study.json", "sources.json", "observations.jsonl", "progress.json"):
                artifact.add_file(str(output / name), name=name)
            for path in sources:
                artifact.add_file(str(path), name="source/" + path.name)
            remote.log_artifact(artifact)
        print(json.dumps(state), flush=True)

    async def observe(source, model, condition, seed, juror):
        case = SectorCase.model_validate(source["case"])
        branch = source["branch"]
        identity = job_key(PROTOCOL, branch["id"], model, condition, seed, juror)
        payload = {
            "branch_id": branch["id"],
            "task_id": case.task_id,
            "group_id": case.group_id,
            "benchmark": case.benchmark,
            "domain": case.domain,
            "original_correct": branch["result"]["initial_correct"],
            "historical_trigger_source": source["historical_trigger_source"],
            "model": model,
            "condition": condition,
            "seed": seed,
            "juror": juror,
        }
        if not study.journal.begin(identity, "judge-extension", payload):
            return
        proof = CalculationProof.model_validate(source["proof"])
        result = await study.invoke(
            model,
            extension_messages(case, branch["result"], proof, condition),
            identity + "-call",
            30000 + seed * 10 + juror,
            Ballot,
        )
        study.journal.finish(
            identity, "complete" if result["status"] == "complete" else "failed", result
        )
        if len(study.journal.rows("judge-extension")) % 20 == 0:
            checkpoint()

    finished = False
    stop_monitor = asyncio.Event()

    async def monitor():
        while not stop_monitor.is_set():
            try:
                await asyncio.wait_for(stop_monitor.wait(), timeout=30)
            except TimeoutError:
                checkpoint()

    monitoring = None
    try:
        for model in JUDGES:
            price = await fetch_cloudflare_price(
                model, os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
            )
            settings = ModelSettings(
                name=model,
                provider="cloudflare",
                max_tokens=2048,
                reasoning=ReasoningSettings(effort="low"),
                text_input_token_ceiling=min(131072, price.context_length),
                calls_per_turn=1,
                calls_per_episode=1,
                turn_timeout_seconds=120,
                requests_per_minute=240 if model == JURY_MODEL else 18,
            )
            study.prices[model] = price
            study.clients[model] = (create_cloudflare_model(settings, price), settings)
        settings = {
            model: settings.model_dump(mode="json")
            for model, (_, settings) in study.clients.items()
        }
        prices = {model: price.model_dump(mode="json") for model, price in study.prices.items()}
        for key, value in (("settings", settings), ("prices", prices)):
            if key in manifest and manifest[key] != value:
                raise ValueError("Judge extension resume cannot change model settings or prices")
            manifest[key] = value
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        remote.config.update({"settings": manifest["settings"], "prices": manifest["prices"]})
        jobs = [
            (source, model, condition, seed, juror)
            for source in selected
            for model in JUDGES
            for condition in CONDITIONS
            for seed in SEEDS
            for juror in (1, 2, 3)
        ]
        random.Random(20261117).shuffle(jobs)
        checkpoint()
        monitoring = asyncio.create_task(monitor())
        await asyncio.gather(*(observe(*job) for job in jobs))
        checkpoint(final=True)
        finished = True
    finally:
        stop_monitor.set()
        if monitoring:
            await monitoring
        if not finished:
            checkpoint(interrupted=True)
        remote.finish(exit_code=0 if finished else 1)
        for client, _ in study.clients.values():
            await client.root_async_client.close()
            client.root_client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--proofs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-cap", type=Decimal, default=Decimal("20"))
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--dotenv", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    (ROOT / ".harness").mkdir(exist_ok=True)
    with (ROOT / ".harness/sector-run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        asyncio.run(
            run(
                args.parent,
                args.proofs,
                args.output,
                args.api_cap,
                datetime.fromisoformat(args.deadline).timestamp(),
            )
        )


if __name__ == "__main__":
    main()
