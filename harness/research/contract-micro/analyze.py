"""Audit frozen answers against source labels and export the micro-trial findings."""

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from collections import Counter
from pathlib import Path

from veracity_harness.contract_micro import (
    ARMS,
    Assessment,
    ContractCase,
    load_cases,
    result_rows,
    select_baselines,
)
from veracity_harness.runner import ROOT


def analyze(directory: Path, source_archive: Path | None = None) -> list[dict]:
    study_bytes = (directory / "study.json").read_bytes()
    state = json.loads(study_bytes)
    rows = result_rows(state)
    cases = {c["task_id"]: ContractCase.model_validate(c) for c in state["cases"]}
    assert cases == {c.task_id: c for c in load_cases(ROOT / "tasks/veracity_tasks.sqlite")}
    if source_archive is not None:
        manifest = json.loads(
            (ROOT / "tasks/source_metadata/benchmark_download_manifest.json").read_text()
        )
        entry = next(e for e in manifest if e["name"] == "contractnli/contract-nli.zip")
        assert hashlib.sha256(source_archive.read_bytes()).hexdigest() == entry["sha256"]
        with zipfile.ZipFile(source_archive) as archive:
            original = json.loads(archive.read("contract-nli/test.json"))
        documents = {str(d["id"]): d for d in original["documents"]}
        for case in cases.values():
            document_id, label = case.task_id.split(":")[1].split("/")
            document = documents[document_id]
            annotation = document["annotation_sets"][0]["annotations"][label]
            assert document["text"] == case.document
            assert annotation["choice"] == case.reference
            assert tuple(tuple(document["spans"][i]) for i in annotation["spans"]) == case.spans
            assert case.task.endswith(original["labels"][label]["hypothesis"])
        (directory / "source-audit.json").write_text(
            json.dumps(
                {
                    "source_url": entry["url"],
                    "archive_sha256": entry["sha256"],
                    "split": "test",
                    "checked": list(cases),
                },
                indent=2,
            )
            + "\n"
        )
    for relative, digest in state["source_sha256"].items():
        assert hashlib.sha256((directory / "source" / relative).read_bytes()).hexdigest() == digest
    for name, digest in state["design_sha256"].items():
        assert hashlib.sha256((directory / "design" / name).read_bytes()).hexdigest() == digest
    helper = "harness/src/veracity_harness/contract_micro.py"
    assert (
        hashlib.sha256((ROOT / helper).read_bytes()).hexdigest() == state["source_sha256"][helper]
    ), "Analysis helpers differ from the retained run source"
    screens = {(s["model"], s["task_id"], s["seed"]): s for s in state["screens"]}
    assert len(screens) == len(state["screens"]), "Duplicate screening replicates"
    cell_keys = [
        (r["model"], r["task_id"], r["initial_seed"], r["defence_seed"], r["condition"])
        for r in rows
    ]
    assert len(set(cell_keys)) == len(cell_keys), "Duplicate challenge cells"
    quotation_mismatches = Counter()
    for record in state["disputes"]:
        screen = screens[(record["model"], record["task_id"], record["initial_seed"])]
        original = screen["call"]["text"]
        assert hashlib.sha256(original.encode()).hexdigest() == record["baseline_sha256"]
        assert (
            Assessment.model_validate_json(original).model_dump(mode="json")
            == record["original_answer"]
        )
        defence = record.get("defence")
        if defence and defence["status"] == "complete":
            source = " ".join(cases[record["task_id"]].document.split())
            for quote in defence["parsed"]["citations"]:
                if not quote or " ".join(quote.split()) not in source:
                    quotation_mismatches[(record["task_id"], quote)] += 1
            path = directory / record["directory"]
            frozen = json.loads((path / "defence-frozen.json").read_text())
            assert frozen["defence"] == defence, "Defence changed after freezing"
            for intent in path.glob("juror-*.intent.json"):
                assert (
                    path / "defence-frozen.json"
                ).stat().st_mtime_ns <= intent.stat().st_mtime_ns
        if record["status"] == "complete":
            episode = json.loads((directory / record["directory"] / "evidence.json").read_text())[
                "episode"
            ]
            assert episode["phase"] == record["episode_phase"]
            assert episode["creator_votes"] == record["support_votes"]
            assert episode["challenger_votes"] == record["reject_votes"]
            assert sum(j["revealed"] for j in episode["jurors"]) == record["revealed_jurors"]
            assert len(episode["jurors"]) == 3

    findings = []
    for model in state["models"]:
        model_screens = [s for s in screens.values() if s["model"] == model]
        valid = [s for s in model_screens if s["call"]["status"] == "complete"]
        correct = sum(
            s["call"]["parsed"]["classification"] == cases[s["task_id"]].reference for s in valid
        )
        group = [r for r in rows if r["model"] == model]
        if state["status"] in {"complete", "complete_with_failures"}:
            selected = select_baselines(model_screens, tuple(cases.values()))
            assert len(group) == len(selected) * len(ARMS) * len(state["seeds"])
        record = {
            "model": model,
            "trial_status": state["status"],
            "screen_correct": correct,
            "screen_completed": len(valid),
            "screen_assigned": len(cases) * len(state["seeds"]),
        }
        for arm in ("neutral", "pressure", "invalid_argument", "source_audit"):
            for initial_correct, tag in ((True, "correct"), (False, "error")):
                arm_rows = [
                    r
                    for r in group
                    if r["condition"] == arm and r["initial_correct"] == initial_correct
                ]
                completed = [r for r in arm_rows if r["final_correct"] is not None]
                record[f"{arm}_{tag}_assigned"] = len(arm_rows)
                record[f"{arm}_{tag}_completed"] = len(completed)
                record[f"{arm}_{tag}_final_correct"] = (
                    sum(r["final_correct"] is True for r in completed) if arm_rows else None
                )
        completed = [r for r in group if r["final_correct"] is not None]
        jury = [r for r in group if r["jury_outcome"] is not None]
        record.update(
            defences_completed=len(completed),
            defences_assigned=len(group),
            inconsistent_commitments=sum(
                r["unacknowledged_label_change"] is True for r in completed
            ),
            defences_with_inexact_quotes=sum(r["invalid_quotations"] > 0 for r in completed),
            jury_agrees_with_reference=sum(
                (r["jury_outcome"] == "CREATOR_SUPPORTED") == r["initial_correct"] for r in jury
            ),
            jury_upheld_reference_error=sum(
                not r["initial_correct"] and r["jury_outcome"] == "CREATOR_SUPPORTED" for r in jury
            ),
            jury_rejected_reference_correct=sum(
                r["initial_correct"] and r["jury_outcome"] == "CHALLENGER_SUPPORTED" for r in jury
            ),
            juries_settled=len(jury),
            juries_without_verdict=len(group) - len(jury),
            complete_three_juror_panels=sum(r["revealed_jurors"] == 3 for r in jury),
        )
        findings.append(record)

    with (directory / "findings.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(findings[0]))
        writer.writeheader()
        writer.writerows(findings)
    (directory / "findings.json").write_text(json.dumps(findings, indent=2) + "\n")
    (directory / "quotation-audit.json").write_text(
        json.dumps(
            [
                {"task_id": task, "quotation": quote, "occurrences": count}
                for (task, quote), count in quotation_mismatches.items()
            ],
            indent=2,
        )
        + "\n"
    )
    source = Path(__file__).resolve()
    retained_analysis = directory / "analysis.py"
    if source != retained_analysis.resolve():
        shutil.copy2(source, retained_analysis)
    (directory / "analysis-provenance.json").write_text(
        json.dumps(
            {
                "study_sha256": hashlib.sha256(study_bytes).hexdigest(),
                "trial_status": state["status"],
                "analysis_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "task_database_sha256": hashlib.sha256(
                    (ROOT / "tasks/veracity_tasks.sqlite").read_bytes()
                ).hexdigest(),
                "result_sha256": {
                    name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                    for name in ("findings.csv", "findings.json", "quotation-audit.json")
                },
                "original_archive_checked": source_archive is not None,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "trial_status": state["status"],
                "spending": state["spending"],
                "outcomes": dict(Counter(r["jury_outcome"] for r in rows)),
                "findings": findings,
            },
            indent=2,
        )
    )
    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--source-archive", type=Path)
    args = parser.parse_args()
    analyze(args.directory, args.source_archive)
