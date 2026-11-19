"""Cloud-native execution of the source-stratified, five-model dispute study."""

import argparse
import asyncio
import hashlib
import json
import os
import platform
import random
import sqlite3
import threading
import time
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError

from game_api.generated import RegisterEpisode
from game_api.local_engine import LocalEngine

from .agents import ModelBudget, create_cloudflare_model
from .config import ModelSettings, ReasoningSettings
from .contract_micro import Ballot
from .finance_micro import stake_parameters
from .runner import ROOT, retain_evidence
from .sector_cases import (
    ARMS,
    JURY_MODEL,
    MODELS,
    SEEDS,
    Answer,
    Defence,
    SectorCase,
    build_cohort,
    challenge_text,
    grade,
    participant_task,
)
from .spending import CampaignSpending, SpendingLimitReached, fetch_cloudflare_price

DESIGN = ROOT / "harness/research/sector-expansion"
PHASE_CAPS = {"Answer": 4096, "Defence": 8192, "Ballot": 2048}


class StudyJournal:
    """An intent journal whose unique job keys prevent paid resampling on restart."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY,kind TEXT NOT NULL,"
                "status TEXT NOT NULL,payload TEXT NOT NULL,result TEXT,"
                "started_at TEXT NOT NULL,finished_at TEXT)"
            )

    def recover(self):
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE jobs SET status='interrupted',finished_at=? WHERE status='running'",
                (datetime.now(UTC).isoformat(),),
            )

    def begin(self, identity: str, kind: str, payload: dict) -> bool:
        encoded = json.dumps(payload, sort_keys=True)
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT kind,payload FROM jobs WHERE id=?", (identity,)).fetchone()
            if row:
                if row != (kind, encoded):
                    raise ValueError("A frozen job key cannot change its inputs")
                return False
            db.execute(
                "INSERT INTO jobs VALUES (?,?,'running',?,NULL,?,NULL)",
                (identity, kind, encoded, datetime.now(UTC).isoformat()),
            )
        return True

    def finish(self, identity: str, status: str, result: dict):
        if status not in {"complete", "failed"}:
            raise ValueError("Unknown terminal job status")
        with sqlite3.connect(self.path) as db:
            updated = db.execute(
                "UPDATE jobs SET status=?,result=?,finished_at=? WHERE id=? AND status='running'",
                (status, json.dumps(result), datetime.now(UTC).isoformat(), identity),
            )
            if updated.rowcount != 1:
                raise ValueError("A terminal observation cannot be replaced")

    def get(self, identity: str) -> dict | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT id,kind,status,payload,result FROM jobs WHERE id=?", (identity,)
            ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "kind": row[1],
            "status": row[2],
            "payload": json.loads(row[3]),
            "result": json.loads(row[4]) if row[4] else None,
        }

    def rows(self, kind: str | None = None) -> list[dict]:
        with sqlite3.connect(self.path) as db:
            query = "SELECT id,kind,status,payload,result FROM jobs"
            rows = db.execute(
                query + (" WHERE kind=?" if kind else "") + " ORDER BY id", (kind,) if kind else ()
            ).fetchall()
        return [
            {
                "id": r[0],
                "kind": r[1],
                "status": r[2],
                "payload": json.loads(r[3]),
                "result": json.loads(r[4]) if r[4] else None,
            }
            for r in rows
        ]

    def counts(self) -> dict:
        with sqlite3.connect(self.path) as db:
            return {
                f"{kind}:{status}": count
                for kind, status, count in db.execute(
                    "SELECT kind,status,count(*) FROM jobs GROUP BY kind,status"
                )
            }


def initial_messages(case: SectorCase) -> list:
    return [
        SystemMessage((DESIGN / "initial.md").read_text()),
        HumanMessage(participant_task(case)),
    ]


def job_key(*parts) -> str:
    return hashlib.sha256("\0".join(map(str, parts)).encode()).hexdigest()[:28]


class SectorStudy:
    """Own model-client lifetime, cloud checkpoints and the bounded run lifecycle."""

    def __init__(self, output: Path, cap: Decimal, deadline: float):
        self.output, self.deadline = output, deadline
        output.mkdir(parents=True, exist_ok=True)
        self.journal = StudyJournal(output / "journal.sqlite")
        self.journal.recover()
        self.spending = CampaignSpending(output / "spending.sqlite", cap)
        self.clients = {}
        self.prices = {}
        self.model_slots = {
            model: asyncio.Semaphore(24 if model == JURY_MODEL else 8) for model in MODELS
        }
        self.engine_slots = asyncio.Semaphore(40)
        self.cases = ()
        self.remote = None
        self.status = "preparing"
        self.finished = asyncio.Event()
        self.started = time.time()
        self.checkpoint_lock = threading.Lock()

    async def invoke(self, model, messages, identity, seed, schema):
        payload = {
            "model": model,
            "seed": seed,
            "schema": schema.__name__,
            "messages_sha256": hashlib.sha256(
                json.dumps([m.content for m in messages]).encode()
            ).hexdigest(),
        }
        existing = self.journal.get(identity)
        if existing:
            if existing["payload"] != payload:
                raise ValueError("Saved model call differs from its frozen request")
            return existing["result"] or {"status": "interrupted"}
        async with self.model_slots[model]:
            if time.time() >= self.deadline:
                return {"status": "deadline_not_dispatched"}
            self.journal.begin(identity, "call", payload)
            settings = self.clients[model][1].model_copy(
                update={"max_tokens": PHASE_CAPS[schema.__name__]}
            )
            budget = ModelBudget(settings, self.spending, self.prices[model])
            budget.begin_turn()
            record = {"status": "pending", "model": model, "seed": seed}
            try:
                result = await self.clients[model][0].ainvoke(
                    messages,
                    extra_body={"response_format": {"type": "json_object"}},
                    seed=seed,
                    max_completion_tokens=settings.max_tokens,
                    config={"callbacks": [budget]},
                    extra_headers={"cf-aig-skip-cache": "true", "cf-aig-max-attempts": "1"},
                )
                record.update(
                    text=result.text,
                    usage=result.usage_metadata,
                    neurons=result.response_metadata.get("neurons"),
                    finish_reason=result.response_metadata.get("finish_reason"),
                )
                if (
                    result.usage_metadata
                    and result.usage_metadata["input_tokens"] > settings.text_input_token_ceiling
                ):
                    raise ValueError("Provider input exceeded the reserved ceiling")
                if record["finish_reason"] == "length":
                    record["status"] = "output_limit"
                else:
                    try:
                        record.update(
                            status="complete",
                            parsed=schema.model_validate_json(result.text).model_dump(mode="json"),
                        )
                    except ValidationError:
                        record["status"] = "invalid_output"
            except SpendingLimitReached:
                record["status"] = "budget_limited"
                self.journal.finish(identity, "failed", record)
                raise
            except Exception as error:
                record.update(
                    status="provider_error",
                    error_type=type(error).__name__,
                    http_status=getattr(error, "status_code", None),
                )
            self.journal.finish(
                identity, "complete" if record["status"] == "complete" else "failed", record
            )
            return record

    def normalize_initials(self):
        cases = {case.case_id: case for case in self.cases}
        parser_hash = hashlib.sha256(
            (ROOT / "harness/src/veracity_harness/sector_cases.py").read_bytes()
        ).hexdigest()
        for row in self.journal.rows("initial"):
            result = row["result"] or {}
            call = result.get("call") or {}
            if call.get("status") != "invalid_output" or not call.get("text"):
                continue
            try:
                parsed = Answer.model_validate_json(call["text"])
            except ValidationError:
                continue
            identity = job_key("interpretation", row["id"])
            payload = {
                **row["payload"],
                "source_job": row["id"],
                "source_text_sha256": hashlib.sha256(call["text"].encode()).hexdigest(),
                "parser_sha256": parser_hash,
            }
            if self.journal.begin(identity, "interpretation", payload):
                normalized = {
                    **call,
                    "raw_status": call["status"],
                    "status": "complete",
                    "parsed": parsed.model_dump(mode="json"),
                }
                self.journal.finish(
                    identity,
                    "complete",
                    {
                        "call": normalized,
                        "correct": grade(cases[row["payload"]["case_id"]], parsed),
                        "normalization": "lossless-json-primitives-v2",
                    },
                )

    def frozen_initial(self, case_id, model):
        identity = job_key("initial", case_id, model)
        return self.journal.get(job_key("interpretation", identity)) or self.journal.get(identity)

    async def initial(self, case, model, index):
        identity = job_key("initial", case.case_id, model)
        payload = {
            "model": model,
            "case_id": case.case_id,
            "domain": case.domain,
            "benchmark": case.benchmark,
            "group_id": case.group_id,
            "seed": 100000 + index,
        }
        if not self.journal.begin(identity, "initial", payload):
            return
        call = await self.invoke(
            model, initial_messages(case), identity + "-call", payload["seed"], Answer
        )
        result = {
            "call": call,
            "correct": grade(case, Answer.model_validate(call["parsed"]))
            if call["status"] == "complete"
            else None,
        }
        self.journal.finish(
            identity, "complete" if call["status"] == "complete" else "failed", result
        )

    async def dispute(
        self,
        case,
        model,
        arm,
        seed,
        *,
        replay=None,
        challenge_override=None,
        identity_namespace=None,
    ):
        kind = "sensitivity" if replay else "branch"
        identity = job_key(
            kind,
            *((identity_namespace,) if identity_namespace else ()),
            case.case_id,
            model,
            arm,
            seed,
        )
        payload = {
            "model": model,
            "case_id": case.case_id,
            "domain": case.domain,
            "benchmark": case.benchmark,
            "group_id": case.group_id,
            "arm": arm,
            "seed": seed,
            "jury_model": MODELS[0] if replay else JURY_MODEL,
        }
        if identity_namespace:
            payload["identity_namespace"] = identity_namespace
        if challenge_override is not None:
            payload["challenge_sha256"] = hashlib.sha256(challenge_override.encode()).hexdigest()
        existing = self.journal.get(identity)
        if existing:
            if existing["payload"] != payload and (
                identity_namespace or challenge_override is not None
            ):
                raise ValueError("A frozen dispute cannot change its explicit objection")
            return
        async with self.engine_slots:
            if time.time() >= self.deadline:
                return
            self.journal.begin(identity, kind, payload)
            initial = self.frozen_initial(case.case_id, model)
            baseline = (initial or {}).get("result") or {}
            original = baseline.get("call") or {}
            if original.get("status") != "complete":
                self.journal.finish(
                    identity, "failed", {"status": "initial_unavailable", "initial_correct": None}
                )
                return
            answer = Answer.model_validate(original["parsed"])
            challenge = challenge_override
            if challenge is None:
                challenge, _ = challenge_text(case, answer, arm)
            claim = (
                "For the supplied task, my answer is "
                + answer.answer
                + ", scale "
                + (answer.scale or "unscaled")
                + ". This answer is supported by the supplied material."
            )
            record = {
                "status": "running",
                "baseline_sha256": hashlib.sha256(original["text"].encode()).hexdigest(),
                "initial_correct": baseline["correct"],
                "original_answer": answer.model_dump(mode="json"),
                "challenge": challenge,
                "claim": claim,
                "ballots": [],
            }
            directory = self.output / "episodes" / identity
            directory.mkdir(parents=True, exist_ok=True)
            engine = LocalEngine(ROOT, key_seed=int(identity[:7], 16), startup_timeout=60)
            try:
                async with engine:
                    client = engine.client

                    async def confirmed(operation):
                        return await client.wait_operation(await operation)

                    episode = "sector-" + identity
                    await confirmed(
                        client.register_episode(
                            RegisterEpisode(
                                episode_id=episode,
                                creator_id="creator",
                                challenger_id="challenger",
                                treasury_id="treasury",
                                juror_ids=["juror-1", "juror-2", "juror-3"],
                                parameters=stake_parameters(1),
                                experiment_id="sector-epistemics-v1",
                            ),
                            idempotency_key=episode + "-register",
                        )
                    )
                    await confirmed(
                        client.post_claim(
                            episode, "creator", claim, idempotency_key=episode + "-claim"
                        )
                    )
                    await confirmed(
                        client.challenge(
                            episode, "challenger", challenge, idempotency_key=episode + "-challenge"
                        )
                    )
                    await client.send_forum_message(
                        episode,
                        "challenger",
                        challenge,
                        round_num=1,
                        idempotency_key=episode + "-objection",
                    )
                    if replay:
                        defence = replay["defence"]
                    else:
                        messages = [
                            *initial_messages(case),
                            AIMessage(original["text"]),
                            HumanMessage(
                                (DESIGN / "defence.md").read_text()
                                + "\n\nOriginal published claim:\n"
                                + claim
                                + "\n\nChallenge:\n"
                                + challenge
                            ),
                        ]
                        defence = await self.invoke(
                            model, messages, identity + "-defence", seed, Defence
                        )
                    record["defence"] = defence
                    (directory / "defence-frozen.json").write_text(
                        json.dumps(record, indent=2) + "\n"
                    )
                    if defence["status"] == "complete":
                        parsed = Defence.model_validate(defence["parsed"])
                        record["final_correct"] = grade(case, parsed)
                        public_defence = {
                            key: value
                            for key, value in parsed.model_dump(mode="json").items()
                            if key
                            not in {"confidence_correct", "p_original_correct", "p_jury_upholds"}
                        }
                        visible = json.dumps(public_defence)
                        await client.send_forum_message(
                            episode,
                            "creator",
                            visible,
                            round_num=2,
                            idempotency_key=episode + "-defence",
                        )
                        context = (
                            participant_task(case)
                            + "\n\nORIGINAL claim:\n"
                            + claim
                            + "\n\nChallenge:\n"
                            + challenge
                            + "\n\nAuthor's defence:\n"
                            + visible
                        )
                        ballots = await asyncio.gather(
                            *(
                                self.invoke(
                                    payload["jury_model"],
                                    [
                                        SystemMessage((DESIGN / "jury.md").read_text()),
                                        HumanMessage(context),
                                    ],
                                    identity + f"-juror-{juror}",
                                    seed * 10 + juror,
                                    Ballot,
                                )
                                for juror in range(1, 4)
                            )
                        )
                        record["ballots"] = ballots
                        for juror, ballot in enumerate(ballots, 1):
                            if ballot["status"] == "complete":
                                vote = Ballot.model_validate(ballot["parsed"])
                                await confirmed(
                                    client.commit(
                                        episode,
                                        f"juror-{juror}",
                                        vote.verdict,
                                        vote.assessment,
                                        idempotency_key=episode + f"-commit-{juror}",
                                    )
                                )
                    await engine.finish_voting(episode)
                    evidence = await retain_evidence(client, episode, directory)
                    state = evidence["episode"]
                    record.update(
                        status="complete",
                        episode_phase=state["phase"],
                        jury_outcome={
                            "SETTLED_CREATOR": "CREATOR_SUPPORTED",
                            "SETTLED_CHALLENGER": "CHALLENGER_SUPPORTED",
                        }.get(state["phase"]),
                        support_votes=state["creator_votes"],
                        reject_votes=state["challenger_votes"],
                        revealed_jurors=sum(j["revealed"] for j in state["jurors"]),
                    )
            except SpendingLimitReached:
                record["status"] = "budget_limited"
                raise
            except Exception as error:
                record.update(
                    status="engine_error",
                    error_type=type(error).__name__,
                    error_message=str(error)[:500],
                )
            finally:
                self.journal.finish(
                    identity, "complete" if record["status"] == "complete" else "failed", record
                )

    def checkpoint(self, *, artifact=False):
        with self.checkpoint_lock:
            self._checkpoint_locked(artifact=artifact)

    def _checkpoint_locked(self, *, artifact=False):
        counts = self.journal.counts()
        snapshot = {
            "status": self.status,
            "updated_at": datetime.now(UTC).isoformat(),
            "counts": counts,
            "spending": self.spending.snapshot(),
            "elapsed_seconds": time.time() - self.started,
        }
        (self.output / "progress.json").write_text(json.dumps(snapshot, indent=2) + "\n")
        self.remote.log(
            {
                **{key.replace(":", "/"): value for key, value in counts.items()},
                "accounted_usd": float(snapshot["spending"]["accounted_usd"]),
                "charged_usd": float(snapshot["spending"]["charged_usd"]),
                "elapsed_seconds": snapshot["elapsed_seconds"],
            }
        )
        self.remote.summary.update(snapshot)
        if artifact:
            import wandb

            for kind in ("initial", "interpretation", "branch", "sensitivity"):
                with (self.output / f"{kind}.jsonl").open("w") as file:
                    for row in self.journal.rows(kind):
                        file.write(json.dumps(row) + "\n")
            bundle = wandb.Artifact(
                f"sector-study-{self.remote.id}",
                type="sector-study",
                metadata={"stage": self.status, "counts": counts},
            )
            for name in (
                "study.json",
                "cases.json",
                "progress.json",
                "initial.jsonl",
                "interpretation.jsonl",
                "branch.jsonl",
                "sensitivity.jsonl",
            ):
                bundle.add_file(str(self.output / name), name=name)
            for source in sorted((self.output / "source").rglob("*")):
                if source.is_file():
                    bundle.add_file(str(source), name=str(source.relative_to(self.output)))
            self.remote.log_artifact(bundle)
        print(json.dumps(snapshot), flush=True)

    async def monitor(self):
        tick = 0
        while not self.finished.is_set():
            try:
                await asyncio.wait_for(self.finished.wait(), timeout=30)
            except TimeoutError:
                tick += 1
                await asyncio.to_thread(self.checkpoint, artifact=tick % 4 == 0)

    async def run(self, *, phase="all"):
        import shutil

        import wandb

        if platform.system() != "Linux":
            raise ValueError("The full study requires the configured Linux cloud runner")
        frozen = self.output / "cases.json"
        self.cases = (
            tuple(SectorCase.model_validate(c) for c in json.loads(frozen.read_text()))
            if frozen.exists()
            else build_cohort(ROOT / "tasks/veracity_tasks.sqlite")
        )
        if not frozen.exists():
            frozen.write_text(
                json.dumps([c.model_dump(mode="json") for c in self.cases], indent=2) + "\n"
            )
        for model in MODELS:
            self.prices[model] = await fetch_cloudflare_price(
                model, os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
            )
            settings = ModelSettings(
                name=model,
                provider="cloudflare",
                max_tokens=4096,
                reasoning=ReasoningSettings(effort="high" if "kimi-k2.6" in model else "low"),
                text_input_token_ceiling=min(131072, self.prices[model].context_length),
                calls_per_turn=1,
                calls_per_episode=1,
                turn_timeout_seconds=120,
                requests_per_minute=240 if model == JURY_MODEL else 18,
            )
            self.clients[model] = (create_cloudflare_model(settings, self.prices[model]), settings)
            self.prices[model].request_ceiling(
                settings.max_tokens, input_tokens=settings.text_input_token_ceiling
            )
        manifest = self.output / "study.json"
        config = {
            "protocol": "sector-v1",
            "models": MODELS,
            "jury_model": JURY_MODEL,
            "seeds": SEEDS,
            "arms": ARMS,
            "cases": len(self.cases),
            "domains": dict(Counter(c.domain for c in self.cases)),
            "source_group_count": len({c.group_id for c in self.cases}),
            "cases_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
            "runner_id": os.getenv("SECTOR_RUNNER_ID", "cloud-ssh-gpu-alder"),
            "runner_platform": platform.platform(),
            "api_cap_usd": str(self.spending.limit),
            "deadline_utc": datetime.fromtimestamp(self.deadline, UTC).isoformat(),
            "settings": {m: s.model_dump(mode="json") for m, (_, s) in self.clients.items()},
            "prices": {m: p.model_dump(mode="json") for m, p in self.prices.items()},
            "reference_scope": (
                "benchmark-relative; adapted numerical endpoints; "
                "not independent human adjudication"
            ),
        }
        if manifest.exists():
            old = json.loads(manifest.read_text())
            for key in (
                "protocol",
                "models",
                "jury_model",
                "cases_sha256",
                "api_cap_usd",
                "settings",
            ):
                if json.loads(json.dumps(config[key])) != old[key]:
                    raise ValueError("Resume cannot change the admitted study configuration")
            run_id = old["wandb_run_id"]
            self.started = datetime.fromisoformat(old["started_at"]).timestamp()
            if old.get("phase_max_tokens") != PHASE_CAPS:
                amendment = {
                    "recorded_at": datetime.now(UTC).isoformat(),
                    "reason": (
                        "Lossless JSON representation normalization; preserve raw failures. "
                        "Before disputes, raise defence allowance and bound short juror output."
                    ),
                    "phase_max_tokens": PHASE_CAPS,
                    "source_sha256": {},
                }
                for name in ("sector_cases.py", "sector_study.py"):
                    path = ROOT / "harness/src/veracity_harness" / name
                    target = self.output / "source" / ("amendment-v2-" + name)
                    shutil.copy2(path, target)
                    amendment["source_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
                old.setdefault("amendments", []).append(amendment)
                old["phase_max_tokens"] = PHASE_CAPS
                manifest.write_text(json.dumps(old, indent=2) + "\n")
            config = old
        else:
            run_id = uuid4().hex[:16]
            config.update(
                wandb_run_id=run_id,
                started_at=datetime.now(UTC).isoformat(),
                source_revision=os.getenv("SECTOR_SOURCE_REVISION", "working-tree-snapshot"),
            )
            source = self.output / "source"
            source.mkdir(exist_ok=True)
            for name in (
                "sector_cases.py",
                "sector_study.py",
                "agents.py",
                "config.py",
                "spending.py",
            ):
                shutil.copy2(ROOT / "harness/src/veracity_harness" / name, source / name)
            for name in ("initial.md", "defence.md", "jury.md", "ARCHITECTURE.md"):
                shutil.copy2(DESIGN / name, source / name)
            if (ROOT / "frozen-source.tgz").exists():
                shutil.copy2(ROOT / "frozen-source.tgz", source / "full-source.tgz")
            config["source_sha256"] = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.iterdir()
                if p.is_file()
            }
            manifest.write_text(json.dumps(config, indent=2) + "\n")
        self.remote = wandb.init(
            entity="lbxa-corp",
            project="apart-epistemics-sprint",
            id=run_id,
            resume="allow",
            name="sector-five-model-full",
            job_type="sector-study",
            config=config,
            settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
        )
        if self.remote.offline or not self.remote.url:
            raise ValueError("Live remote tracking must precede paid dispatch")
        monitor = asyncio.create_task(self.monitor())
        try:
            self.status = "initial_answers"
            await asyncio.to_thread(self.checkpoint, artifact=True)
            initial_jobs = [
                (case, model, index) for index, case in enumerate(self.cases) for model in MODELS
            ]
            random.Random(20261115).shuffle(initial_jobs)
            await asyncio.gather(*(self.initial(*job) for job in initial_jobs))
            self.normalize_initials()
            await asyncio.to_thread(self.checkpoint, artifact=True)
            if phase == "initial":
                self.status = "initial_phase_complete"
                return
            self.status = "disputes"
            jobs = [
                (case, model, arm, seed)
                for case in self.cases
                for model in MODELS
                for arm in ARMS
                for seed in SEEDS
            ]
            random.Random(20261116).shuffle(jobs)
            await asyncio.gather(*(self.dispute(*job) for job in jobs))
            self.status = "judge_sensitivity"
            sensitivity = []
            for index, case in enumerate(self.cases):
                model, arm, seed = MODELS[index % 5], ARMS[index % 4], SEEDS[0]
                branch = self.journal.get(job_key("branch", case.case_id, model, arm, seed))
                if (
                    branch
                    and branch["result"]
                    and (branch["result"].get("defence") or {}).get("status") == "complete"
                ):
                    sensitivity.append(
                        self.dispute(case, model, arm, seed, replay=branch["result"])
                    )
            await asyncio.gather(*sensitivity)
            self.status = (
                (
                    "complete_with_failures"
                    if any(key.endswith(":failed") for key in self.journal.counts())
                    else "complete"
                )
                if time.time() < self.deadline
                else "deadline_reached"
            )
        except SpendingLimitReached:
            self.status = "budget_limited"
            raise
        except BaseException:
            self.status = "interrupted"
            raise
        finally:
            self.finished.set()
            await monitor
            await asyncio.to_thread(self.checkpoint, artifact=True)
            self.remote.finish(
                exit_code=0
                if self.status in {"complete", "complete_with_failures", "initial_phase_complete"}
                else 1
            )
            for client, _ in self.clients.values():
                await client.root_async_client.close()
                client.root_client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-cap", type=Decimal, default=Decimal("1500"))
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--phase", choices=("initial", "all"), default="all")
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    asyncio.run(
        SectorStudy(
            args.output, args.api_cap, datetime.fromisoformat(args.deadline).timestamp()
        ).run(phase=args.phase)
    )


if __name__ == "__main__":
    main()
