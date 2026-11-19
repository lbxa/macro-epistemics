"""Create a read-only admission view excluding positively identified test stores."""

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from veracity_harness.sector_revision import PROTOCOL
from veracity_harness.sector_study import job_key

SCRIPTED_CHALLENGE = "A scripted invalid alternative."
SCRIPTED_EXPLANATION = "PRIVATE_PROVIDER_REASONING_SENTINEL"


def file_hashes(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("A test-store directory unexpectedly contains a symlink")
        if path.is_file():
            files[str(path.relative_to(directory))] = {
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    return files


def fixture_views(pytest_root):
    views = {}
    for path in pytest_root.glob(
        "pytest-*/test_real_engine_receipts_are_*/source/episodes/*/evidence.json"
    ):
        path = path.resolve()
        evidence = json.loads(path.read_text())
        frozen_path = path.with_name("defence-frozen.json")
        frozen = json.loads(frozen_path.read_text())
        episode = evidence["episode"]
        if (
            episode["evidence"] != SCRIPTED_CHALLENGE
            or frozen.get("challenge") != SCRIPTED_CHALLENGE
            or frozen.get("original_answer", {}).get("explanation") != SCRIPTED_EXPLANATION
            or frozen.get("defence", {}).get("parsed", {}).get("explanation")
            != SCRIPTED_EXPLANATION
        ):
            raise ValueError("A candidate pytest record lacks the exact scripted fixture markers")
        views[str(path)] = {
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "frozen_path": str(frozen_path),
            "frozen_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
            "episode": episode,
        }
    return list(views.values())


def plan(repo, pytest_root):
    fixtures = fixture_views(pytest_root)
    episodes = {item["episode"]["episode_id"] for item in fixtures}
    if not fixtures:
        raise ValueError("No retained pytest fixture evidence was found")
    # Historical campaign stores predate these tests by many hours. This is
    # only a scan filter; every moved directory still needs the exact proofs.
    earliest_fixture = min(Path(item["path"]).stat().st_mtime for item in fixtures) - 3600
    candidates = []
    for database in sorted((repo / ".harness/runs").glob("*/game.sqlite")):
        if database.stat().st_mtime < earliest_fixture:
            continue
        matching = []
        with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            if not db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='episodes'"
            ).fetchone():
                continue
            identities = db.execute(
                "SELECT id,onchain_id,configuration_hash FROM episodes"
            ).fetchall()
            if not any(row[0] in episodes for row in identities):
                continue
            identity = json.loads(db.execute("SELECT identity_json FROM deployment").fetchone()[0])
            for fixture in fixtures:
                episode = fixture["episode"]
                deployment = episode["deployment"]
                if identities != [
                    (
                        episode["episode_id"],
                        episode["onchain_episode_id"],
                        episode["configuration_hash"],
                    )
                ]:
                    continue
                if (
                    any(
                        identity[key] != deployment[key]
                        for key in (
                            "chain_id",
                            "code_hash",
                            "abi_version",
                            "confirmation_depth",
                        )
                    )
                    or identity["contract_address"].lower()
                    != deployment["contract_address"].lower()
                ):
                    continue
                if not db.execute(
                    "SELECT 1 FROM artifacts WHERE hash=? AND utf8=?",
                    (
                        episode["evidence_hash"],
                        SCRIPTED_CHALLENGE,
                    ),
                ).fetchone():
                    continue
                if db.execute(
                    "SELECT 1 FROM operations "
                    "WHERE status NOT IN ('confirmed','reverted','failed') LIMIT 1"
                ).fetchone():
                    raise ValueError("An identified test store has a nonterminal operation")
                matching.append(
                    {
                        key: fixture[key]
                        for key in (
                            "path",
                            "sha256",
                            "frozen_path",
                            "frozen_sha256",
                        )
                    }
                )
        if matching:
            directory = database.resolve().parent
            candidates.append(
                {
                    "directory": str(directory),
                    "pytest_evidence": matching,
                }
            )
    for item in candidates:
        item["files"] = file_hashes(Path(item["directory"]))
    return {
        "status": "planned",
        "fixture_challenge": SCRIPTED_CHALLENGE,
        "candidates": candidates,
        "candidate_count": len(candidates),
    }


def create_admission_view(repo, pytest_root, study_directory, view):
    progress = json.loads((study_directory / "progress.json").read_text())
    if progress["status"] not in {"complete", "complete_with_failures"}:
        raise ValueError("Build the final engine view only after numerical collection finishes")
    study = json.loads((study_directory / "study.json").read_text())
    if study["protocol"] != PROTOCOL:
        raise ValueError("Unexpected study protocol for the engine admission view")
    assignments_path = study_directory / "source/assignments.json"
    assignments = json.loads(assignments_path.read_text())
    expected = {
        "sector-" + job_key("branch", PROTOCOL, item["case_id"], item["model"], "misleading", seed)
        for item in assignments
        for seed in item["seeds"]
    }
    rows_path = study_directory / "branch.jsonl"
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    if len(rows) != 1500 or {"sector-" + row["id"] for row in rows} != expected:
        raise ValueError("Wait for the final 1,500-row numerical export before constructing a view")
    ownership = plan(repo, pytest_root)
    if ownership["candidate_count"] != 3:
        raise ValueError("Expected exactly the three positively identified failed-test stores")
    excluded = {Path(item["directory"]) for item in ownership["candidates"]}
    floor = datetime.fromisoformat(study["started_at"]).timestamp() - 600
    included = {}
    for database in sorted((repo / ".harness/runs").glob("*/game.sqlite")):
        if database.parent.resolve() in excluded or database.stat().st_mtime < floor:
            continue
        with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            if not db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='episodes'"
            ).fetchone():
                continue
            identities = db.execute("SELECT id FROM episodes").fetchall()
        for (episode_id,) in identities:
            if episode_id not in expected:
                continue
            if episode_id in included:
                raise ValueError(
                    "An unknown or production duplicate remains; refusing an admission view"
                )
            included[episode_id] = database.resolve().parent
    complete = {"sector-" + row["id"] for row in rows if row["status"] == "complete"}
    if not complete.issubset(included):
        raise ValueError("The engine view would omit a completed numerical branch")
    if view.exists():
        raise ValueError("Use a fresh admission-view directory to avoid stale entries")
    view.mkdir(parents=True)
    entries = []
    for episode_id, directory in sorted(included.items()):
        alias = view / directory.name
        alias.symlink_to(directory, target_is_directory=True)
        entries.append({"episode_id": episode_id, "source": str(directory), "alias": str(alias)})
    record = {
        "status": "read_only_view_created",
        "run_id": study["wandb_run_id"],
        "view": str(view),
        "included_count": len(entries),
        "included": entries,
        "excluded_identified_fixtures": ownership["candidates"],
        "permission_block": (
            "Container denied /proc/526/fd/0 inspection; no original stores were moved"
        ),
        "source_sha256": {
            "study.json": hashlib.sha256((study_directory / "study.json").read_bytes()).hexdigest(),
            "branch.jsonl": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
            "source/assignments.json": hashlib.sha256(assignments_path.read_bytes()).hexdigest(),
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    manifest = view / "manifest.json"
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    return {
        "status": record["status"],
        "view": str(view),
        "included_count": len(entries),
        "excluded_count": len(excluded),
        "manifest": str(manifest),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--pytest-root", type=Path, default=Path("/tmp/pytest-of-root"))
    parser.add_argument("--admission-view", type=Path, required=True)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    print(
        json.dumps(
            create_admission_view(
                repo,
                args.pytest_root,
                args.study.resolve(),
                args.admission_view.resolve(),
            )
        )
    )


if __name__ == "__main__":
    main()
