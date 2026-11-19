"""Export frozen study material for independent source-first human review.

This is an offline packaging boundary. It performs no inference and never
changes historical labels. Only computed packet data is serialized here.
"""

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

ADMITTED_ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128"
ADMITTED_SNAPSHOT_SHA256 = "c44d7a3f3963941a0eb661c4a01832005c1742713aaade8b2aeba347d56883f6"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def build_packet(raw: Path, snapshot: Path, audit: Path, output: Path) -> dict:
    """Enforce frozen-input integrity and metadata separation at export."""
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Refusing to overwrite an existing review packet")
    if digest(snapshot) != ADMITTED_SNAPSHOT_SHA256:
        raise ValueError("Frozen snapshot hash differs from the admitted v128 anchor")
    study = json.loads(snapshot.read_text())
    if study["provenance"]["artifact"] != ADMITTED_ARTIFACT:
        raise ValueError("Frozen snapshot artifact differs from the admitted v128 anchor")
    expected = study["provenance"]["file_sha256"]
    for name in ("cases.json", "initial.jsonl", "interpretation.jsonl"):
        if digest(raw / name) != expected[name]:
            raise ValueError(f"Frozen input hash mismatch: {name}")

    cases = json.loads((raw / "cases.json").read_text())
    source_audit = {row["task_id"]: row for row in json.loads(audit.read_text())["cases"]}
    semantic_priorities = {
        "contractnli:53/nda-1": "Selected omission-versus-negation disagreement",
        "scifact:3": "Selected compound-claim/supplied-abstract disagreement",
        "mathdial:5000751/1/row495": (
            "Potential ambiguity: sprouting versus surviving immediately eaten plants"
        ),
    }
    if len(cases) != 120 or len({row["group_id"] for row in cases}) != 120:
        raise ValueError("Expected the complete 120-source-group cohort")

    ordered_cases = sorted(cases, key=lambda row: row["case_id"])
    random.Random(20261116).shuffle(ordered_cases)
    case_ids = {row["case_id"]: f"T{index:03d}" for index, row in enumerate(ordered_cases, start=1)}
    source_rows = [
        {
            "review_task_id": case_ids[row["case_id"]],
            "task": row["task"],
            "document": row["document"],
            "permitted_labels": row["labels"],
            "content_sha256": hashlib.sha256(
                json.dumps([row["task"], row["document"]], ensure_ascii=False).encode()
            ).hexdigest(),
        }
        for row in ordered_cases
    ]

    effective = {
        (row["payload"]["case_id"], row["payload"]["model"]): row
        for row in json_rows(raw / "initial.jsonl")
    }
    for row in json_rows(raw / "interpretation.jsonl"):
        effective[(row["payload"]["case_id"], row["payload"]["model"])] = row
    usable = [row for row in effective.values() if row["status"] == "complete"]
    usable.sort(key=lambda row: row["id"])
    random.Random(20261117).shuffle(usable)
    if len(usable) != 581:
        raise ValueError("Expected 581 usable frozen original outputs")

    response_rows = []
    response_key = []
    for index, row in enumerate(usable, start=1):
        parsed = row["result"]["call"]["parsed"]
        response_id = f"R{index:03d}"
        response_rows.append(
            {
                "review_response_id": response_id,
                "review_task_id": case_ids[row["payload"]["case_id"]],
                "answer": parsed["answer"],
                "scale": parsed["scale"],
                "explanation": parsed["explanation"],
                "citations": parsed["citations"],
            }
        )
        response_key.append(
            {
                "review_response_id": response_id,
                "source_job": row["payload"].get("source_job", row["id"]),
                "effective_job": row["id"],
                "case_id": row["payload"]["case_id"],
                "model": row["payload"]["model"],
                "seed": row["payload"]["seed"],
                "raw_text_sha256": hashlib.sha256(
                    row["result"]["call"]["text"].encode()
                ).hexdigest(),
            }
        )

    output.mkdir(parents=True, exist_ok=True)
    blinded = output / "reviewer"
    operator = output / "operator-only"
    stage_one = blinded / "stage-1"
    stage_two = blinded / "stage-2"
    stage_one.mkdir(parents=True, exist_ok=True)
    stage_two.mkdir(parents=True, exist_ok=True)
    operator.mkdir(exist_ok=True)
    write_json(stage_one / "sources.json", source_rows)
    write_json(stage_two / "responses.json", response_rows)
    for directory, name, rows, fields in (
        (
            stage_one,
            "source-reviews.csv",
            source_rows,
            [
                "review_task_id",
                "reviewer_id",
                "reviewer_expertise",
                "answer",
                "unit",
                "acceptable_precision",
                "evidence_spans",
                "derivation",
                "ambiguity",
                "insufficient_context",
                "rationale",
                "reviewed_at_utc",
            ],
        ),
        (
            stage_two,
            "response-reviews.csv",
            response_rows,
            [
                "review_response_id",
                "review_task_id",
                "reviewer_id",
                "answer_assessment",
                "explanation_assessment",
                "citation_assessment",
                "evidence_spans",
                "rationale",
                "reviewed_at_utc",
            ],
        ),
    ):
        with (directory / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row[key] for key in fields if key in row})

    write_json(
        operator / "join-key.json",
        {
            "task_key": [
                {
                    "review_task_id": case_ids[row["case_id"]],
                    "case_id": row["case_id"],
                    "task_id": row["task_id"],
                    "group_id": row["group_id"],
                    "benchmark": row["benchmark"],
                    "domain": row["domain"],
                    "variant": row["variant"],
                    "literal_reference": row["reference"],
                    "literal_scale": row["scale"],
                    "literal_tolerance": row["tolerance"],
                    "source_url": row["source_url"],
                    "source_sha256": row["source_sha256"],
                    "prior_automated_audit": source_audit.get(row["task_id"]),
                    "operator_priority_note": semantic_priorities.get(row["task_id"]),
                }
                for row in ordered_cases
            ],
            "response_key": response_key,
        },
    )
    files = {
        str(path.relative_to(output)): digest(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "version": "source-first-human-adjudication-v1",
        "status": "prepared_not_adjudicated",
        "source_artifact": study["provenance"]["artifact"],
        "input_sha256": {
            "portable_snapshot": digest(snapshot),
            "cases.json": digest(raw / "cases.json"),
            "initial.jsonl": digest(raw / "initial.jsonl"),
            "interpretation.jsonl": digest(raw / "interpretation.jsonl"),
            "prior_automated_audit": digest(audit),
        },
        "source_groups": len(source_rows),
        "usable_originals": len(response_rows),
        "unavailable_originals": 600 - len(response_rows),
        "independent_human_reviews_completed": 0,
        "file_sha256": files,
    }
    write_json(output / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path(".harness/sector-working"))
    parser.add_argument("--snapshot", type=Path, default=Path("report/data/sector-study.json"))
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path("harness/research/sector-expansion/source-audit.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("harness/research/sector-expansion/peer-review/adjudication"),
    )
    args = parser.parse_args()
    result = build_packet(args.raw, args.snapshot, args.audit, args.output)
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "source_groups",
                    "usable_originals",
                    "independent_human_reviews_completed",
                )
            }
        )
    )
