"""Offline checks on frozen provenance, blinding and review-form safety."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).with_name("build_adjudication_packet.py")
SPEC = importlib.util.spec_from_file_location("adjudication_packet", MODULE)
assert SPEC is not None and SPEC.loader is not None
PACKET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKET)
ROOT = MODULE.resolve().parents[4]
RAW = ROOT / ".harness/sector-working"
SNAPSHOT = ROOT / "report/data/sector-study.json"
AUDIT = ROOT / "harness/research/sector-expansion/source-audit.json"


def test_frozen_export_has_no_grades_or_model_metadata(tmp_path):
    output = tmp_path / "packet"
    manifest = PACKET.build_packet(RAW, SNAPSHOT, AUDIT, output)
    assert manifest["source_groups"] == 120
    assert manifest["usable_originals"] == 581
    assert manifest["independent_human_reviews_completed"] == 0
    sources = json.loads((output / "reviewer/stage-1/sources.json").read_text())
    responses = json.loads((output / "reviewer/stage-2/responses.json").read_text())
    assert {p.name for p in (output / "reviewer/stage-1").iterdir()} == {
        "sources.json",
        "source-reviews.csv",
    }
    assert not (output / "reviewer/stage-1/responses.json").exists()
    assert all(
        set(row) == {"review_task_id", "task", "document", "permitted_labels", "content_sha256"}
        for row in sources
    )
    assert all(
        set(row)
        == {
            "review_response_id",
            "review_task_id",
            "answer",
            "scale",
            "explanation",
            "citations",
        }
        for row in responses
    )
    for stage, name in (("stage-1", "source-reviews.csv"), ("stage-2", "response-reviews.csv")):
        with (output / "reviewer" / stage / name).open() as stream:
            rows = list(csv.DictReader(stream))
        assert all(row["reviewer_id"] == "" for row in rows)
        assert all(row["rationale"] == "" for row in rows)
        assert all(row["reviewed_at_utc"] == "" for row in rows)
    with pytest.raises(FileExistsError):
        PACKET.build_packet(RAW, SNAPSHOT, AUDIT, output)


def test_mismatched_frozen_hash_stops_before_export(tmp_path):
    snapshot = json.loads(SNAPSHOT.read_text())
    snapshot["provenance"]["file_sha256"]["cases.json"] = "0" * 64
    changed = tmp_path / "snapshot.json"
    changed.write_text(json.dumps(snapshot))
    output = tmp_path / "packet"
    with pytest.raises(ValueError, match="Frozen snapshot hash"):
        PACKET.build_packet(RAW, changed, AUDIT, output)
    assert not output.exists()


def test_raw_tamper_is_rejected_against_anchored_snapshot(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "cases.json").write_bytes(b"[]\n")
    with pytest.raises(ValueError, match="Frozen input hash mismatch"):
        PACKET.build_packet(raw, SNAPSHOT, AUDIT, tmp_path / "packet")


def test_repeated_exports_are_byte_identical(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    PACKET.build_packet(RAW, SNAPSHOT, AUDIT, first)
    PACKET.build_packet(RAW, SNAPSHOT, AUDIT, second)
    for path in first.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (second / path.relative_to(first)).read_bytes()
