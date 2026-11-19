import hashlib
import json
import sqlite3
import tarfile
import time
from decimal import Decimal

import pytest

from veracity_harness.runner import ROOT
from veracity_harness.sector_cases import JURY_MODEL, MODELS, SEEDS, Answer, build_cohort
from veracity_harness.sector_revision import PROTOCOL
from veracity_harness.sector_revision_archive import (
    archive,
    engine_databases,
    receipt_projection,
    validate_assignment_rows,
)
from veracity_harness.sector_study import SectorStudy, job_key


@pytest.fixture
def replication(tmp_path, monkeypatch):
    source = tmp_path / "source"
    (source / "source").mkdir(parents=True)
    cases = tuple(c for c in build_cohort(ROOT / "tasks/veracity_tasks.sqlite") if not c.labels)
    initials, assignments, rows = [], [], []
    for case in cases:
        for model in MODELS:
            index = len(assignments)
            answer = Answer(
                answer=case.reference,
                scale=case.scale,
                confidence_correct=0.9,
                explanation="PRIVATE_PROVIDER_REASONING_SENTINEL",
                citations=(),
            )
            call = {
                "status": "complete",
                "parsed": answer.model_dump(mode="json"),
                "text": answer.model_dump_json(),
            }
            key = job_key("initial", case.case_id, model)
            initials.append(
                {
                    "id": key,
                    "kind": "initial",
                    "status": "complete",
                    "payload": {"case_id": case.case_id, "model": model},
                    "result": {"call": call, "correct": True},
                }
            )
            status = (
                "initial_unavailable"
                if index < 13
                else "numeric_policy_unsupported"
                if index == 13
                else "supported"
            )
            challenge = "A scripted invalid alternative." if status == "supported" else None
            assignment = {
                "case_id": case.case_id,
                "model": model,
                "initial_job": key,
                "status": status,
                "challenge": challenge,
                "seeds": SEEDS,
            }
            assignments.append(assignment)
            for seed in SEEDS:
                payload = {
                    "case_id": case.case_id,
                    "model": model,
                    "seed": seed,
                    "domain": case.domain,
                    "benchmark": case.benchmark,
                    "group_id": case.group_id,
                    "arm": "misleading",
                    "jury_model": JURY_MODEL,
                    "identity_namespace": PROTOCOL,
                }
                result = {"status": status}
                if challenge:
                    payload["challenge_sha256"] = hashlib.sha256(challenge.encode()).hexdigest()
                    result = {
                        "status": "engine_error",
                        "initial_correct": True,
                        "baseline_sha256": hashlib.sha256(call["text"].encode()).hexdigest(),
                        "original_answer": call["parsed"],
                        "challenge": challenge,
                        "claim": (
                            "For the supplied task, my answer is "
                            + answer.answer
                            + ", scale "
                            + (answer.scale or "unscaled")
                            + ". This answer is supported by the supplied material."
                        ),
                    }
                rows.append(
                    {
                        "id": job_key("branch", PROTOCOL, case.case_id, model, "misleading", seed),
                        "kind": "branch",
                        "status": "failed",
                        "payload": payload,
                        "result": result,
                    }
                )
    prepared = {
        "parent_run_id": "parent",
        "parent_sha256": {"cases.json": "pinned"},
        "cases": cases,
        "initial": initials,
        "interpretation": [],
        "assignments": assignments,
    }
    monkeypatch.setattr("veracity_harness.sector_revision_archive.prepare", lambda parent: prepared)
    (source / "progress.json").write_text(
        json.dumps(
            {
                "status": "complete_with_failures",
                "counts": {"branch:failed": 1500},
                "spending": {"limit_usd": "50", "charged_usd": "0", "accounted_usd": "0"},
            }
        )
    )
    (source / "cases.json").write_text(json.dumps([c.model_dump(mode="json") for c in cases]))
    (source / "source/assignments.json").write_text(json.dumps(assignments))
    source_hashes = {}
    for name in (
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
    ):
        data = ("fixture source bytes: " + name).encode()
        (source / "source" / name).write_bytes(data)
        source_hashes[name] = hashlib.sha256(data).hexdigest()
    (source / "study.json").write_text(
        json.dumps(
            {
                "protocol": PROTOCOL,
                "parent_run_id": "parent",
                "parent_sha256": prepared["parent_sha256"],
                "assigned_branches": 1500,
                "models": MODELS,
                "jury_model": JURY_MODEL,
                "seeds": SEEDS,
                "source_sha256": source_hashes,
                "wandb_run_id": "fixture-replication",
                "api_cap_usd": "50",
            }
        )
    )
    (source / "branch.jsonl").write_text("\n".join(map(json.dumps, rows)))
    engines = tmp_path / "engine-runs"
    engines.mkdir()
    return source, engines, prepared, rows


def test_admission_retains_partial_failures_without_claiming_executed_outcomes(
    replication, tmp_path
):
    source, engines, _, _ = replication
    result = archive(source, tmp_path / "parent", engines, tmp_path / "admitted")
    assert result["counts"] == {
        "initial_unavailable": 65,
        "numeric_policy_unsupported": 5,
        "partial_failures": 1430,
    }
    assert result["phases"] == {}
    assert (
        result["input_sha256"]["source/assignments.json"]
        == hashlib.sha256((source / "source/assignments.json").read_bytes()).hexdigest()
    )
    with tarfile.open(tmp_path / "admitted/executed-evidence.tar.gz") as bundle:
        assert len(bundle.getmembers()) == 1430
        for member in bundle:
            body = bundle.extractfile(member).read()
            assert b"PRIVATE_PROVIDER_REASONING_SENTINEL" not in body
            assert b"sqlite" not in body
    second = archive(source, tmp_path / "parent", engines, tmp_path / "admitted-repeat")
    assert result["archive_sha256"] == second["archive_sha256"]


def test_assignment_tampering_and_frozen_source_changes_fail_admission(replication, tmp_path):
    source, engines, prepared, rows = replication
    with pytest.raises(ValueError, match="1,500"):
        validate_assignment_rows(rows[:-1], prepared)
    changed = [
        {**r, "result": {**r["result"], "baseline_sha256": "changed"}}
        if r["result"]["status"] == "engine_error"
        else r
        for r in rows
    ]
    with pytest.raises(ValueError, match="frozen original"):
        validate_assignment_rows(changed, prepared)
    completed_hidden_as_failure = [
        {**r, "result": {**r["result"], "status": "complete"}}
        if r["result"]["status"] == "engine_error"
        else r
        for r in rows
    ]
    with pytest.raises(ValueError, match="completed execution status"):
        validate_assignment_rows(completed_hidden_as_failure, prepared)
    assignment_path = source / "source/assignments.json"
    assignment_bytes = assignment_path.read_bytes()
    altered = json.loads(assignment_bytes)
    altered[0]["challenge"] = "Changed objection"
    assignment_path.write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="assignments changed"):
        archive(source, tmp_path / "parent", engines, tmp_path / "admitted")
    assignment_path.write_bytes(assignment_bytes)
    (source / "source/sector_revision.py").write_bytes(b"changed")
    with pytest.raises(ValueError, match="source hash"):
        archive(source, tmp_path / "parent", engines, tmp_path / "admitted")


@pytest.mark.asyncio
@pytest.mark.parametrize("valid_jurors", [0, 2, 3])
async def test_real_engine_receipts_are_admitted_without_exporting_recovery_data(
    replication, tmp_path, monkeypatch, valid_jurors
):
    source, engines, prepared, rows = replication
    assignment = next(a for a in prepared["assignments"] if a["status"] == "supported")
    case = next(c for c in prepared["cases"] if c.case_id == assignment["case_id"])
    original = next(r for r in prepared["initial"] if r["id"] == assignment["initial_job"])
    study = SectorStudy(source, Decimal("1"), time.time() + 120)
    study.journal.begin(original["id"], "initial", original["payload"])
    study.journal.finish(original["id"], "complete", original["result"])

    async def invoke(model, messages, identity, seed, schema):
        if schema.__name__ == "Ballot" and int(identity.rsplit("-", 1)[1]) > valid_jurors:
            return {"status": "invalid_output", "text": "Unparseable ballot"}
        parsed = (
            {"verdict": "CREATOR_SUPPORTED", "assessment": "PUBLIC_ASSESSMENT_SENTINEL"}
            if schema.__name__ == "Ballot"
            else {
                **original["result"]["call"]["parsed"],
                "stance": "maintain",
                "original_still_supported": True,
                "p_original_correct": 0.9,
                "p_jury_upholds": 0.8,
            }
        )
        return {"status": "complete", "parsed": parsed, "text": json.dumps(parsed)}

    # Rust's local engine stores recovery data relative to its working directory.
    # Own that directory so concurrent campaigns cannot enter this test's DB set.
    engine_home = tmp_path / "engine-home"
    engine_home.mkdir()
    (engine_home / "target").symlink_to(ROOT / "target", target_is_directory=True)
    (engine_home / "contracts").symlink_to(ROOT / "contracts", target_is_directory=True)
    monkeypatch.setattr("veracity_harness.sector_study.ROOT", engine_home)
    monkeypatch.setattr(study, "invoke", invoke)
    await study.dispute(
        case,
        assignment["model"],
        "misleading",
        101,
        challenge_override=assignment["challenge"],
        identity_namespace=PROTOCOL,
    )
    identity = job_key("branch", PROTOCOL, case.case_id, assignment["model"], "misleading", 101)
    row = study.journal.get(identity)
    assert row["result"]["jury_outcome"] == ("CREATOR_SUPPORTED" if valid_jurors >= 2 else None)
    created = set((engine_home / ".harness/runs").glob("*/game.sqlite"))
    assert len(created) == 1
    (engines / "isolated").symlink_to(
        next(iter(created)).resolve().parent, target_is_directory=True
    )
    rows = [row if r["id"] == identity else r for r in rows]
    (source / "branch.jsonl").write_text("\n".join(map(json.dumps, rows)))
    progress = json.loads((source / "progress.json").read_text())
    progress["counts"] = {"branch:complete": 1, "branch:failed": 1499}
    (source / "progress.json").write_text(json.dumps(progress))
    result = archive(source, tmp_path / "parent", engines, tmp_path / "admitted")
    assert result["counts"]["validated_executions"] == 1
    assert result["counts"]["confirmed_receipts"] == 4 + 2 * valid_jurors
    assert result["counts"]["partial_failures"] == 1429
    with tarfile.open(tmp_path / "admitted/executed-evidence.tar.gz") as bundle:
        body = bundle.extractfile("episodes/" + identity + ".json").read()
        projection = json.loads(body)
        assert b"PRIVATE_PROVIDER_REASONING_SENTINEL" not in body
        assert b"PUBLIC_ASSESSMENT_SENTINEL" not in body
        assert b"raw_transaction" not in body
        assert b"reveal_material" not in body
        assert projection["episode"]["content"] is None
        assert projection["receipts"]["confirmed_receipt_count"] == 4 + 2 * valid_jurors
    partial = {**row, "status": "failed", "result": {**row["result"], "status": "engine_error"}}
    rows = [partial if r["id"] == identity else r for r in rows]
    (source / "branch.jsonl").write_text("\n".join(map(json.dumps, rows)))
    progress["counts"] = {"branch:failed": 1500}
    (source / "progress.json").write_text(json.dumps(progress))
    partial_admission = archive(source, tmp_path / "parent", engines, tmp_path / "partial-admitted")
    assert partial_admission["counts"]["partial_failures"] == 1430
    assert partial_admission["counts"]["confirmed_partial_receipts"] == 4 + 2 * valid_jurors
    assert partial_admission["phases"] == {}
    db = engine_databases(engines, {"sector-" + identity})["sector-" + identity]
    episode = json.loads((source / "episodes" / identity / "evidence.json").read_text())["episode"]
    with sqlite3.connect(db) as connection:
        connection.execute(
            "UPDATE receipts SET receipt_json=json_set(receipt_json,'$.success',json('false'))"
        )
    with pytest.raises(ValueError, match="successful confirmed receipt"):
        receipt_projection(db, episode, terminal=True)
