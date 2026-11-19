"""Validate and archive executed sector evidence without private recovery data."""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import tarfile
from collections import Counter
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from game_api.generated import BalancesView, EpisodeView, SettlementView


def validate_episode(row, evidence):
    """Compare retained contract views with the observation; never infer a verdict."""
    if evidence.get("private_transcripts") != {}:
        raise ValueError("Do not admit private or incomplete transcripts")
    episode = EpisodeView.model_validate(evidence["episode"])
    settlement = SettlementView.model_validate(evidence["settlement"])
    balances = BalancesView.model_validate(evidence["balances"])
    result = row["result"]
    if not (
        episode.episode_id == settlement.episode_id == balances.episode_id == "sector-" + row["id"]
    ):
        raise ValueError("Evidence belongs to another episode")
    if (
        episode.deployment != settlement.deployment
        or episode.phase != settlement.outcome
        or episode.phase != result["episode_phase"]
    ):
        raise ValueError("Retained terminal contract views disagree")
    revealed = sum(j.revealed for j in episode.jurors)
    ballot_votes = Counter(
        (b.get("parsed") or {}).get("verdict")
        for b in result["ballots"]
        if b["status"] == "complete"
    )
    final_votes = Counter(settlement.final_votes.values())
    if (
        episode.creator_votes != result["support_votes"]
        or episode.challenger_votes != result["reject_votes"]
        or revealed != result["revealed_jurors"]
        or len(settlement.final_votes) != revealed
        or ballot_votes != final_votes
        or final_votes["CREATOR_SUPPORTED"] != episode.creator_votes
        or final_votes["CHALLENGER_SUPPORTED"] != episode.challenger_votes
    ):
        raise ValueError("Retained votes disagree with the frozen observation")
    outcome = {
        "SETTLED_CREATOR": "CREATOR_SUPPORTED",
        "SETTLED_CHALLENGER": "CHALLENGER_SUPPORTED",
    }.get(episode.phase)
    if outcome != result["jury_outcome"]:
        raise ValueError("The observation changed its contract verdict")
    if (
        episode.total_deposited_wei != settlement.total_deposited
        or episode.total_credited_wei != settlement.total_credited
        or episode.total_deposited_wei != episode.total_credited_wei
        or int(episode.locked_liability_wei) != 0
        or sum(map(int, balances.entitlements.values())) != int(settlement.total_credited)
    ):
        raise ValueError("Retained contract totals disagree")
    return {
        "phase": episode.phase,
        "revealed": revealed,
        "deposited_wei": episode.total_deposited_wei,
    }


def archive(source, destination, needles=()):
    progress = json.loads((source / "progress.json").read_text())
    if progress["status"] not in {"complete", "complete_with_failures"}:
        raise ValueError("Finish collection before admitting executed evidence")
    rows = [
        json.loads(line)
        for kind in ("branch", "sensitivity")
        for line in (source / (kind + ".jsonl")).read_text().splitlines()
    ]
    if sum(r["kind"] == "branch" for r in rows) != 12000:
        raise ValueError("The primary assignment is incomplete")
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / "executed-evidence.tar.gz"
    entries, counts, phases = {}, Counter(), Counter()
    encoded = tuple(value.encode() for value in needles if value)
    with (
        path.open("wb") as raw,
        gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as compressed,
        tarfile.open(fileobj=compressed, mode="w") as bundle,
    ):
        for row in sorted(rows, key=lambda r: r["id"]):
            identity, result = row["id"], row["result"] or {}
            if not re.fullmatch(r"[a-f0-9]{28}", identity):
                raise ValueError("Unexpected evidence path identity")
            directory = source / "episodes" / identity
            episode_path = directory / "evidence.json"
            if row["status"] == "complete":
                admitted = validate_episode(row, json.loads(episode_path.read_text()))
                counts[row["kind"] + ":validated"] += 1
                phases[admitted["phase"]] += 1
            elif result.get("status") == "initial_unavailable":
                if directory.exists():
                    raise ValueError("A structurally unavailable branch has episode files")
                counts[row["kind"] + ":initial_unavailable"] += 1
            else:
                counts[row["kind"] + ":partial_failure"] += 1
            for name in ("evidence.json", "defence-frozen.json"):
                file = directory / name
                if not file.exists():
                    if name == "defence-frozen.json" and row["status"] == "complete":
                        raise ValueError("A completed episode lost its frozen defence")
                    continue
                data = file.read_bytes()
                body = json.loads(data)
                if body.get("private_transcripts", {}) != {}:
                    raise ValueError("Refusing to archive private transcript bodies")
                if any(value in data for value in encoded):
                    raise ValueError("Refusing to archive credential material")
                if name == "defence-frozen.json" and (
                    body.get("baseline_sha256") != result.get("baseline_sha256")
                    or body.get("defence") != result.get("defence")
                ):
                    raise ValueError("A frozen defence changed after juror invocation")
                relative = str(file.relative_to(source))
                info = tarfile.TarInfo(relative)
                info.size, info.mode, info.mtime = len(data), 0o600, 0
                bundle.addfile(info, io.BytesIO(data))
                entries[relative] = {
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                    "job_status": row["status"],
                    "kind": row["kind"],
                }
    register = {
        "status": "validated",
        "parent_run_id": json.loads((source / "study.json").read_text())["wandb_run_id"],
        "counts": dict(counts),
        "phases": dict(phases),
        "planned_main_branches": 12000,
        "planned_sensitivity_branches": 120,
        "observed_sensitivity_branches": sum(r["kind"] == "sensitivity" for r in rows),
        "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "files": entries,
        "input_sha256": {
            name: hashlib.sha256((source / name).read_bytes()).hexdigest()
            for name in ("study.json", "branch.jsonl", "sensitivity.jsonl", "progress.json")
        },
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (destination / "evidence-register.json").write_text(json.dumps(register, indent=2) + "\n")
    shutil.copy2(Path(__file__), destination / "sector_archive.py")
    return register


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    if args.dotenv:
        load_dotenv(args.dotenv, override=False)
    needles = tuple(
        os.getenv(key, "")
        for key in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "WANDB_API_KEY")
    )
    register = archive(args.source, args.output, needles)
    if args.upload:
        import wandb

        parent = wandb.Api(
            overrides={"base_url": os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"},
            timeout=30,
        ).artifact(
            "lbxa-corp/apart-epistemics-sprint/sector-study-"
            + register["parent_run_id"]
            + ":latest"
        )
        parent_name = (
            "lbxa-corp/apart-epistemics-sprint/sector-study-"
            + register["parent_run_id"]
            + ":"
            + parent.version
        )
        config = {k: v for k, v in register.items() if k != "files"}
        config.update(parent_artifact=parent_name, parent_digest=parent.digest)
        with wandb.init(
            entity="lbxa-corp",
            project="apart-epistemics-sprint",
            id=uuid4().hex[:16],
            job_type="sector-evidence-audit",
            config=config,
            settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
        ) as run:
            run.use_artifact(parent_name)
            artifact = wandb.Artifact(
                "sector-executed-evidence-" + register["parent_run_id"],
                type="sector-executed-evidence",
                metadata=config,
            )
            for name in ("executed-evidence.tar.gz", "evidence-register.json", "sector_archive.py"):
                artifact.add_file(str(args.output / name), name=name)
            run.log_artifact(artifact)
            run.summary.update(
                {
                    "status": "validated",
                    "files": len(register["files"]),
                    "counts": register["counts"],
                }
            )
            (args.output / "tracking.json").write_text(
                json.dumps(
                    {
                        "run_id": run.id,
                        "url": run.url,
                        "parent_artifact": parent_name,
                        "parent_digest": parent.digest,
                    },
                    indent=2,
                )
                + "\n"
            )
    print(json.dumps({k: v for k, v in register.items() if k not in {"files", "input_sha256"}}))


if __name__ == "__main__":
    main()
