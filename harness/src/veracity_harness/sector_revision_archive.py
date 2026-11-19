"""Admit numerical-v2 executions and export safe receipt-backed projections."""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import tarfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from game_api.generated import DeploymentView, ForumMessagePage, ReceiptView

from .sector_archive import validate_episode
from .sector_cases import JURY_MODEL, MODELS, SEEDS, Answer
from .sector_revision import PROTOCOL, prepare
from .sector_study import job_key

FROZEN_SOURCES = {
    "sector_revision.py",
    "sector_objections.py",
    "sector_study.py",
    "sector_cases.py",
    "agents.py",
    "spending.py",
    "config.py",
    "initial.md",
    "defence.md",
    "jury.md",
    "objection-protocol.md",
}


def json_digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def receipt_projection(path: Path, episode: dict | None, *, terminal: bool) -> dict:
    """Read only public transaction metadata, never signing or reveal material."""
    if terminal and episode is None:
        raise ValueError("Terminal receipt admission requires the retained episode view")
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        identity = json.loads(db.execute("SELECT identity_json FROM deployment").fetchone()[0])
        # core/src/game/reads.rs adds this derived field to the persisted identity.
        deployment = DeploymentView.model_validate(
            {**identity, "finality_policy": "confirmation_depth"}
        ).model_dump(mode="json")
        identities = db.execute("SELECT id,onchain_id,configuration_hash FROM episodes").fetchall()
        if episode is None:
            if len(identities) != 1:
                raise ValueError("Partial receipt store must identify exactly one episode")
            episode = {
                "episode_id": identities[0][0],
                "onchain_episode_id": identities[0][1],
                "configuration_hash": identities[0][2],
                "deployment": deployment,
            }
        if {**deployment, "contract_address": deployment["contract_address"].lower()} != {
            **episode["deployment"],
            "contract_address": episode["deployment"]["contract_address"].lower(),
        }:
            raise ValueError("Receipt store belongs to another deployment")
        if identities != [
            (episode["episode_id"], episode["onchain_episode_id"], episode["configuration_hash"])
        ]:
            raise ValueError("Receipt store episode identity differs from the retained view")
        rows = db.execute(
            "SELECT o.id,o.actor_id,o.kind,o.status,s.transaction_hash,r.receipt_json "
            "FROM operations o LEFT JOIN signed_transactions s ON s.operation_id=o.id "
            "LEFT JOIN receipts r ON r.operation_id=o.id WHERE o.episode_id=? ORDER BY o.id",
            (episode["episode_id"],),
        ).fetchall()
        retained_logs = {
            json_digest(json.loads(row[0]))
            for row in db.execute("SELECT payload_json FROM chain_events")
        }
    operations, receipt_logs = [], set()
    for operation_id, actor, kind, status, transaction_hash, receipt_json in rows:
        record = {"operation_id": operation_id, "actor_id": actor, "kind": kind, "status": status}
        if terminal and status != "confirmed":
            raise ValueError("A completed engine episode has an unconfirmed operation")
        if receipt_json is None:
            if terminal:
                raise ValueError("A completed engine operation lacks its retained receipt")
            operations.append(record)
            continue
        raw = json.loads(receipt_json)
        receipt = ReceiptView.model_validate(
            {
                key: str(raw[key]) if key in {"gas_used", "effective_gas_price"} else raw[key]
                for key in ReceiptView.model_fields
            }
        )
        if receipt.transaction_hash != transaction_hash or (
            status == "confirmed" and (not receipt.success or not receipt.confirmed)
        ):
            raise ValueError("Stored operation and successful confirmed receipt disagree")
        logs = []
        for log in raw["logs"]:
            if (
                log["chain_id"] != deployment["chain_id"]
                or log["contract_address"].lower() != deployment["contract_address"].lower()
                or log["transaction_hash"] != transaction_hash
                or log["block_number"] != receipt.block_number
                or log["block_hash"] != receipt.block_hash
            ):
                raise ValueError("Receipt contains a log from another transaction or deployment")
            if not isinstance(log["topics"], list) or not all(
                isinstance(topic, str) and re.fullmatch(r"0x[0-9a-fA-F]{64}", topic)
                for topic in log["topics"]
            ):
                raise ValueError("Public event topics must contain only hexadecimal hashes")
            digest = json_digest(log)
            receipt_logs.add(digest)
            logs.append(
                {
                    key: log[key]
                    for key in (
                        "chain_id",
                        "contract_address",
                        "transaction_hash",
                        "block_number",
                        "block_hash",
                        "log_index",
                        "topics",
                    )
                }
                | {"payload_sha256": digest}
            )
        record.update(
            receipt=receipt.model_dump(mode="json"),
            logs=logs,
            source_receipt_sha256=hashlib.sha256(receipt_json.encode()).hexdigest(),
        )
        operations.append(record)
    if terminal:
        required = {
            ("treasury", "register"),
            ("creator", "post_claim"),
            ("challenger", "challenge"),
            ("treasury", "settle"),
        }
        for juror in episode["jurors"]:
            if juror["revealed"]:
                required.update(
                    {(juror["actor_id"], "commit_vote"), (juror["actor_id"], "reveal_vote")}
                )
        observed = Counter((o["actor_id"], o["kind"]) for o in operations)
        if any(observed[operation] != 1 for operation in required):
            raise ValueError("Receipt store lacks a unique required game operation")
        if not receipt_logs or receipt_logs != retained_logs:
            raise ValueError("Persisted event logs disagree with confirmed operation receipts")
    return {
        "deployment": deployment,
        "episode_identity": {
            key: episode[key]
            for key in (
                "episode_id",
                "onchain_episode_id",
                "configuration_hash",
            )
        },
        "operations": operations,
        "confirmed_receipt_count": sum(
            o.get("receipt", {}).get("confirmed", False) and o["receipt"]["success"]
            for o in operations
        ),
        "public_log_count": len(receipt_logs),
    }


def engine_databases(root: Path, episodes: set[str]) -> dict[str, Path]:
    """Locate only the requested episodes without copying any engine database."""
    found = {}
    for path in sorted(root.glob("*/game.sqlite")):
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            if not db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='episodes'"
            ).fetchone():
                continue
            identities = [row[0] for row in db.execute("SELECT id FROM episodes")]
        for identity in set(identities) & episodes:
            if identity in found:
                raise ValueError("More than one engine store claims the same replication episode")
            found[identity] = path
    return found


def validate_assignment_rows(rows: list[dict], prepared: dict) -> dict[str, dict]:
    expected = {
        job_key(
            "branch", PROTOCOL, assignment["case_id"], assignment["model"], "misleading", seed
        ): (assignment, seed)
        for assignment in prepared["assignments"]
        for seed in SEEDS
    }
    if (
        len(rows) != 1500
        or len({row["id"] for row in rows}) != 1500
        or set(expected) != {row["id"] for row in rows}
    ):
        raise ValueError("Numerical replication must retain exactly its 1,500 assigned branches")
    cases = {c.case_id: c for c in prepared["cases"]}
    originals = {row["id"]: row for row in prepared["initial"]}
    originals.update({row["payload"]["source_job"]: row for row in prepared["interpretation"]})
    admitted = {}
    for row in rows:
        assignment, seed = expected[row["id"]]
        case = cases[assignment["case_id"]]
        payload, result = row["payload"], row["result"] or {}
        expected_payload = {
            "model": assignment["model"],
            "case_id": case.case_id,
            "domain": case.domain,
            "benchmark": case.benchmark,
            "group_id": case.group_id,
            "arm": "misleading",
            "seed": seed,
            "jury_model": JURY_MODEL,
            "identity_namespace": PROTOCOL,
        }
        if assignment["challenge"] is not None:
            expected_payload["challenge_sha256"] = hashlib.sha256(
                assignment["challenge"].encode()
            ).hexdigest()
        if (
            payload != expected_payload
            or row["kind"] != "branch"
            or row["status"] not in {"complete", "failed"}
        ):
            raise ValueError("Replication branch payload or terminal status changed")
        if (row["status"] == "complete") != (result.get("status") == "complete"):
            raise ValueError("Branch row and observation disagree on completed execution status")
        if assignment["status"] != "supported":
            if row["status"] != "failed" or result.get("status") != assignment["status"]:
                raise ValueError(
                    "An unavailable assignment was replaced by a generated observation"
                )
        else:
            baseline = originals[assignment["initial_job"]]["result"]
            call = baseline["call"]
            answer = Answer.model_validate(call["parsed"])
            claim = (
                "For the supplied task, my answer is "
                + answer.answer
                + ", scale "
                + (answer.scale or "unscaled")
                + ". This answer is supported by the supplied material."
            )
            if (
                result.get("baseline_sha256") != hashlib.sha256(call["text"].encode()).hexdigest()
                or result.get("original_answer") != answer.model_dump(mode="json")
                or result.get("initial_correct") != baseline["correct"]
                or result.get("challenge") != assignment["challenge"]
                or result.get("claim") != claim
            ):
                raise ValueError("A replication branch changed its frozen original or objection")
        admitted[row["id"]] = {"assignment": assignment, "row": row}
    return admitted


def archive(source: Path, parent: Path, engine_runs: Path, output: Path, needles=()) -> dict:
    progress = json.loads((source / "progress.json").read_text())
    if progress["status"] not in {"complete", "complete_with_failures"}:
        raise ValueError("Finish numerical replication before admitting executions")
    prepared = prepare(parent)
    study = json.loads((source / "study.json").read_text())
    if (
        study["protocol"] != PROTOCOL
        or study["parent_run_id"] != prepared["parent_run_id"]
        or study["parent_sha256"] != prepared["parent_sha256"]
        or study["assigned_branches"] != 1500
        or study["models"] != list(MODELS)
        or study["jury_model"] != JURY_MODEL
        or study["seeds"] != list(SEEDS)
    ):
        raise ValueError("Replication manifest differs from its prospective frozen design")
    if set(study["source_sha256"]) != FROZEN_SOURCES:
        raise ValueError("Replication manifest omits required frozen sources")
    for name, digest in study["source_sha256"].items():
        if (
            Path(name).name != name
            or hashlib.sha256((source / "source" / name).read_bytes()).hexdigest() != digest
        ):
            raise ValueError("Frozen replication source hash changed")
    if json.loads((source / "source/assignments.json").read_text()) != json.loads(
        json.dumps(prepared["assignments"])
    ):
        raise ValueError("Prospective replication assignments changed")
    if json.loads((source / "cases.json").read_text()) != [
        c.model_dump(mode="json") for c in prepared["cases"]
    ]:
        raise ValueError("Replication case projection differs from admitted originals")
    rows = [json.loads(line) for line in (source / "branch.jsonl").read_text().splitlines()]
    assignments = validate_assignment_rows(rows, prepared)
    observed = Counter(row["status"] for row in rows)
    if {
        key.removeprefix("branch:"): value
        for key, value in progress["counts"].items()
        if key.startswith("branch:")
    } != observed:
        raise ValueError("Final progress counters disagree with terminal branch rows")
    if (
        Decimal(study["api_cap_usd"]) != Decimal("50")
        or Decimal(progress["spending"]["limit_usd"]) != Decimal("50")
        or not Decimal(0)
        <= Decimal(progress["spending"]["charged_usd"])
        <= Decimal(progress["spending"]["accounted_usd"])
        <= Decimal("50")
    ):
        raise ValueError("Retained spending summary violates the prospective API cap")
    databases = engine_databases(engine_runs, {"sector-" + identity for identity in assignments})
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "executed-evidence.tar.gz"
    files, counts, phases = {}, Counter(), Counter()
    encoded = tuple(needle.encode() for needle in needles if needle)
    with (
        destination.open("wb") as raw,
        gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as compressed,
        tarfile.open(fileobj=compressed, mode="w") as bundle,
    ):
        for identity, item in sorted(assignments.items()):
            row, assignment = item["row"], item["assignment"]
            result = row["result"] or {}
            directory = source / "episodes" / identity
            episode_id = "sector-" + identity
            if assignment["status"] != "supported":
                if directory.exists() or episode_id in databases:
                    raise ValueError("An unavailable assignment unexpectedly executed an engine")
                counts[assignment["status"]] += 1
                continue
            path = directory / "evidence.json"
            frozen_path = directory / "defence-frozen.json"
            projection = {
                "branch_id": identity,
                "source_original_sha256": result["baseline_sha256"],
                "branch_status": row["status"],
                "observation_status": result["status"],
            }
            if row["status"] == "complete":
                evidence = json.loads(path.read_text())
                verified = validate_episode(row, evidence)
                frozen = json.loads(frozen_path.read_text())
                if any(
                    frozen.get(key) != result.get(key)
                    for key in (
                        "defence",
                        "baseline_sha256",
                        "claim",
                        "challenge",
                        "original_answer",
                    )
                ):
                    raise ValueError("A defence changed after its jurors were dispatched")
                episode = evidence["episode"]
                if (
                    episode["content"] != result["claim"]
                    or episode["evidence"] != result["challenge"]
                ):
                    raise ValueError("On-chain episode content differs from the frozen branch")
                messages = [
                    message
                    for page in evidence["forum_transcript"]
                    for message in ForumMessagePage.model_validate(page).messages
                ]
                defence = result["defence"]
                creators = [m.content for m in messages if m.sender_id == "creator"]
                if defence["status"] == "complete":
                    public = {
                        key: value
                        for key, value in defence["parsed"].items()
                        if key not in {"confidence_correct", "p_original_correct", "p_jury_upholds"}
                    }
                    if len(creators) != 1 or json.loads(creators[0]) != public:
                        raise ValueError("Public defence differs from the frozen model response")
                elif creators:
                    raise ValueError("An invalid defence unexpectedly entered the public forum")
                if [m.content for m in messages if m.sender_id == "challenger"] != [
                    assignment["challenge"]
                ]:
                    raise ValueError("Public objection differs from the assigned intervention")
                if episode_id not in databases:
                    raise ValueError("Completed episode has no retained receipt store")
                receipts = receipt_projection(databases[episode_id], episode, terminal=True)
                projection.update(
                    episode={**episode, "content": None, "evidence": None},
                    settlement=evidence["settlement"],
                    balances=evidence["balances"],
                    source_evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    source_frozen_defence_sha256=hashlib.sha256(
                        frozen_path.read_bytes()
                    ).hexdigest(),
                    receipts=receipts,
                )
                phases[verified["phase"]] += 1
                counts["validated_executions"] += 1
                counts["confirmed_receipts"] += receipts["confirmed_receipt_count"]
                counts["public_logs"] += receipts["public_log_count"]
            else:
                counts["partial_failures"] += 1
                projection["retained_engine_store"] = episode_id in databases
                if episode_id in databases:
                    receipts = receipt_projection(databases[episode_id], None, terminal=False)
                    if receipts["episode_identity"]["episode_id"] != episode_id:
                        raise ValueError("Partial receipt store belongs to another branch")
                    projection["partial_receipts"] = receipts
                    counts["confirmed_partial_receipts"] += receipts["confirmed_receipt_count"]
                if path.exists():
                    projection["source_partial_evidence_sha256"] = hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
            data = (json.dumps(projection, sort_keys=True, indent=2) + "\n").encode()
            if any(needle in data for needle in encoded):
                raise ValueError("Credential material in the safe evidence projection")
            name = "episodes/" + identity + ".json"
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), 0o600, 0
            bundle.addfile(info, io.BytesIO(data))
            files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    if counts["initial_unavailable"] != 65 or counts["numeric_policy_unsupported"] != 5:
        raise ValueError("Replication availability denominators differ from the frozen parent")
    register = {
        "status": "validated",
        "protocol": PROTOCOL,
        "run_id": study["wandb_run_id"],
        "parent_run_id": prepared["parent_run_id"],
        "parent_sha256": prepared["parent_sha256"],
        "assigned_branches": 1500,
        "supported_branches": 1430,
        "counts": dict(counts),
        "phases": dict(phases),
        "files": files,
        "archive_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "input_sha256": {
            name: hashlib.sha256((source / name).read_bytes()).hexdigest()
            for name in (
                "study.json",
                "cases.json",
                "branch.jsonl",
                "progress.json",
                "source/assignments.json",
            )
        },
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bundle_files": {
            "executed-evidence.tar.gz": {
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "bytes": destination.stat().st_size,
            },
            Path(__file__).name: {
                "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "bytes": Path(__file__).stat().st_size,
            },
        },
        "spending": progress["spending"],
        "scope": (
            "Retained local Anvil receipts and contract views; no public-chain deployment claim"
        ),
    }
    (output / "evidence-register.json").write_text(json.dumps(register, indent=2) + "\n")
    shutil.copy2(Path(__file__), output / Path(__file__).name)
    return register


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--engine-runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--source-artifact")
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    needles = tuple(
        os.getenv(key, "")
        for key in (
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_API_TOKEN",
            "WANDB_API_KEY",
        )
    )
    register = archive(args.source, args.parent, args.engine_runs, args.output, needles)
    if args.upload:
        import wandb

        expected = "lbxa-corp/apart-epistemics-sprint/sector-study-" + register["run_id"] + ":v"
        if not args.source_artifact or not re.fullmatch(
            re.escape(expected) + r"\d+", args.source_artifact
        ):
            raise ValueError("Upload requires the exact version of this completed study artifact")
        metadata = {key: value for key, value in register.items() if key != "files"}
        with wandb.init(
            entity="lbxa-corp",
            project="apart-epistemics-sprint",
            id=uuid4().hex[:16],
            job_type="sector-objection-evidence-admission",
            config=metadata,
            settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
        ) as run:
            run.use_artifact(args.source_artifact)
            artifact = wandb.Artifact(
                "sector-objection-executed-evidence-" + register["run_id"],
                type="sector-executed-evidence",
                metadata=metadata,
            )
            for name in ("executed-evidence.tar.gz", "evidence-register.json", Path(__file__).name):
                artifact.add_file(str(args.output / name), name=name)
            run.log_artifact(artifact)
            run.summary.update({"status": "validated", "counts": register["counts"]})
    print(json.dumps({key: value for key, value in register.items() if key != "files"}))


if __name__ == "__main__":
    main()
