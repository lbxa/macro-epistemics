"""Audit a finished cohort, retaining quorum settlements and participation gaps."""

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from game_api.generated import EpisodeView
from veracity_harness.config import Experiment
from veracity_harness.finance_micro import Answer, measurement_rows, numeric_score, stake_parameters
from veracity_harness.finance_repetitions import MODEL


def jury_observation(episode: EpisodeView) -> dict:
    """Keep actual reveals and settlement distinct from the number assigned."""
    if len(episode.jurors) != 3 or len({j.actor_id for j in episode.jurors}) != 3:
        raise ValueError("Expected three distinct assigned jurors")
    if any(j.revealed != (j.verdict is not None) for j in episode.jurors):
        raise ValueError("Reveal flags and verdicts disagree")
    counts = Counter(j.verdict for j in episode.jurors if j.revealed)
    support, reject = counts["CREATOR_SUPPORTED"], counts["CHALLENGER_SUPPORTED"]
    if (support, reject) != (episode.creator_votes, episode.challenger_votes):
        raise ValueError("Contract tally disagrees with revealed votes")
    verdict = {
        "SETTLED_CREATOR": "CREATOR_SUPPORTED",
        "SETTLED_CHALLENGER": "CHALLENGER_SUPPORTED",
    }.get(episode.phase)
    if verdict and counts[verdict] < episode.required_votes:
        raise ValueError("Settlement lacks the contract's required quorum")
    revealed = support + reject
    return {
        "jury_outcome": verdict,
        "support_votes": support,
        "reject_votes": reject,
        "assigned_jurors": 3,
        "revealed_jurors": revealed,
        "missing_votes": 3 - revealed,
        "participation_complete": revealed == 3,
        "actual_total_deposited_wei": episode.total_deposited_wei,
    }


def select_results(attempt_rows: list[dict]) -> list[dict]:
    """Recover unresolved cells without choosing between already-observed verdicts."""
    originals = [r for r in attempt_rows if r["source_cohort"] == "original"]
    selected = []
    for original in originals:
        if original["verification"] == "withheld":
            selected.append(original)
            continue
        candidates = [
            r
            for r in attempt_rows
            if (r["seed"], r["stake_multiplier"], r["condition"])
            == (original["seed"], original["stake_multiplier"], original["condition"])
            and r["verification"] == "submitted"
            and r["jury_outcome"] is not None
        ]
        if len(candidates) > 1:
            raise ValueError(
                "Multiple settled attempts for one cell; never select a preferred verdict"
            )
        selected.append(candidates[0] if candidates else original)
    return selected


def analyze(campaign: Path, output: Path, recovery: Path | None = None):
    plan = json.loads((campaign / "plan.json").read_text())
    assignments = plan["assignments"]
    expected = set(itertools.product(plan["seeds"], plan["stake_multipliers"]))
    assigned = [(a["seed"], a["stake_multiplier"]) for a in assignments]
    if len(plan["seeds"]) != 5 or len(assignments) != 20 or set(assigned) != expected:
        raise ValueError("Expected twenty unique assignments across five seeds and four stakes")
    if plan["status"] == "running" or any(
        a["status"] not in {"complete", "failed"} for a in assignments
    ):
        raise ValueError("Cohort has unfinished assignments; do not report a final table")
    python_sources = {
        k: v for k, v in plan["source_sha256"].items() if k.startswith("harness/src/")
    }
    all_assignments = [(a, python_sources, "original") for a in assignments]
    recovery_plan = None
    recovery_archive_hash = None
    if recovery:
        recovery_plan = json.loads(recovery.read_text())
        if recovery_plan["status"] != "complete":
            raise ValueError("Recovery assignments are not complete")
        recovery_source = {
            k: v for k, v in recovery_plan["source_sha256"].items() if k.startswith("harness/src/")
        }
        recovery_archive_hash = hashlib.sha256(
            (recovery.parent / recovery_plan["source_archive"]).read_bytes()
        ).hexdigest()
        if recovery_archive_hash != recovery_plan["source_archive_sha256"]:
            raise ValueError("Recovery source archive changed")
        all_assignments.extend(
            (a, recovery_source, "recovery") for a in recovery_plan["assignments"]
        )
    rows, provenance, baselines = [], [], {}
    for assignment, expected_source, source_cohort in all_assignments:
        directory = campaign.parent / assignment["attempt"]
        study_file = directory / "study.json"
        state = json.loads(study_file.read_text())
        seed, stakes = assignment["seed"], assignment["stake_multiplier"]
        if (
            state["model"],
            state["provider"],
            state["seed"],
            state.get("sampling_seed"),
            state["stake_multiplier"],
        ) != (MODEL, "cloudflare", seed, seed, stakes):
            raise ValueError("Study identity does not match its assignment")
        if state["source_sha256"] != expected_source:
            raise ValueError("Runtime source differs from the frozen campaign source")
        for name in (
            "task.md",
            "answer-format.md",
            "disclosure.md",
            "jury-forecast.md",
            "review-request.md",
        ):
            expected_hash = plan["source_sha256"][f"harness/research/finance-micro/{name}"]
            actual = hashlib.sha256((directory / "design" / name).read_bytes()).hexdigest()
            if actual != expected_hash:
                raise ValueError("Participant prompt changed within the cohort")
        measured = measurement_rows(state)
        if len(measured) != 3 or {r["condition"] for r in measured} != {
            "aware-verified",
            "aware-withheld",
            "unaware-verified",
        }:
            raise ValueError("Expected all three conditions")
        evidence_hashes = {}
        for arm, row in zip(state["arms"], measured, strict=True):
            answer = Answer.model_validate(arm["answer"])
            digest = hashlib.sha256(answer.model_dump_json().encode()).hexdigest()
            if digest != arm["baseline_sha256"]:
                raise ValueError("Answer differs from its frozen hash")
            if baselines.setdefault(arm["baseline_id"], digest) != digest:
                raise ValueError("Baseline changed across repetitions")
            score = numeric_score(answer)
            if (arm["correct"], arm["brier_correct"]) != (score["correct"], score["brier_correct"]):
                raise ValueError("Arithmetic confidence score is inconsistent")
            row.update(
                source_cohort=source_cohort,
                attempt=directory.name,
                wandb_url=state["wandb_url"],
                study_execution_status=state["status"],
                strict_collector_status=assignment["status"]
                if source_cohort == "original"
                else "not_run",
                support_votes=None,
                reject_votes=None,
                assigned_jurors=None,
                revealed_jurors=None,
                missing_votes=None,
                participation_complete=None,
                actual_total_deposited_wei=None,
                agent_execution_failed=None,
                budget_exhaustions=None,
                turn_deadline_yields=None,
            )
            if source_cohort == "recovery" and row["verification"] == "submitted":
                if row["condition"] not in assignment["conditions"]:
                    raise ValueError("Recovery submitted an unassigned condition")
            if arm["verification"] != "withheld" and arm.get("run_directory"):
                config = Experiment.model_validate(arm["jury_config"])
                parameters = stake_parameters(stakes)
                if (config.seed, config.model.sampling_seed, config.jury_size) != (seed, seed, 3):
                    raise ValueError("Jury seed or size changed")
                if config.parameters != parameters:
                    raise ValueError("Configured bonds do not match the stake factor")
                summary = arm["episodes"][0]
                evidence_file = (
                    directory / arm["run_directory"] / summary["episode_id"] / "evidence.json"
                )
                episode = EpisodeView.model_validate(
                    json.loads(evidence_file.read_text())["episode"]
                )
                if episode.configuration.parameters != parameters:
                    raise ValueError("Contract parameters differ from the assignment")
                observed = jury_observation(episode)
                if observed["jury_outcome"] != arm["jury_outcome"]:
                    raise ValueError("Recorded outcome differs from the settled contract")
                row.update(observed)
                row.update(
                    {
                        k: summary[k]
                        for k in (
                            "agent_execution_failed",
                            "budget_exhaustions",
                            "turn_deadline_yields",
                        )
                    }
                )
                evidence_hashes[str(evidence_file.relative_to(directory))] = hashlib.sha256(
                    evidence_file.read_bytes()
                ).hexdigest()
            rows.append(row)
        provenance.append(
            {
                "source_cohort": source_cohort,
                "attempt": directory.name,
                "url": state["wandb_url"],
                "execution_status": state["status"],
                "collector_status": assignment["status"]
                if source_cohort == "original"
                else "not_run",
                "study_sha256": hashlib.sha256(study_file.read_bytes()).hexdigest(),
                "evidence_sha256": evidence_hashes,
            }
        )
    attempt_rows = rows
    rows = select_results(attempt_rows)
    cells = []
    for stakes, condition in itertools.product(
        plan["stake_multipliers"], ("aware-verified", "unaware-verified")
    ):
        group = [r for r in rows if r["stake_multiplier"] == stakes and r["condition"] == condition]
        counts = Counter(r["jury_outcome"] for r in group)
        cells.append(
            {
                "stake_multiplier": stakes,
                "condition": condition,
                "assigned": len(group),
                "upheld": counts["CREATOR_SUPPORTED"],
                "rejected": counts["CHALLENGER_SUPPORTED"],
                "unresolved": counts[None],
                "full_participation": sum(r["participation_complete"] is True for r in group),
                "vote_splits": dict(
                    Counter(
                        (
                            f"{r['support_votes']}-{r['reject_votes']} "
                            f"({r['missing_votes']} missing)"
                            if r["support_votes"] is not None
                            else "no retained vote evidence"
                        )
                        for r in group
                    )
                ),
            }
        )
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "five-seed-results.csv"
    attempts_path = output / "five-seed-attempts.csv"
    for path, records in ((csv_path, rows), (attempts_path, attempt_rows)):
        with path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    summary = {
        "kind": "one_task_frozen_answer_jury_replications",
        "seeds": plan["seeds"],
        "stake_multipliers": plan["stake_multipliers"],
        "source_tasks": 1,
        "initial_answers": len(set(baselines.values())),
        "rows": len(rows),
        "cells": cells,
        "strict_campaign_status": plan["status"],
        "campaign_url": plan["wandb_url"],
        "spending": recovery_plan["spending"] if recovery_plan else plan["spending"],
        "original_campaign_spending": plan["spending"],
        "cohort": provenance,
        "source_archive_sha256": hashlib.sha256((campaign / "source.zip").read_bytes()).hexdigest(),
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "attempts_csv_sha256": hashlib.sha256(attempts_path.read_bytes()).hexdigest(),
        "recovery_source_archive_sha256": recovery_archive_hash,
        "recovery_plan_sha256": hashlib.sha256(recovery.read_bytes()).hexdigest()
        if recovery
        else None,
        "attempt_rows": len(attempt_rows),
        "missing_jury_forecasts": sum(
            r["jury_forecast_status"] != "measured" for r in rows if r["verification"] != "withheld"
        ),
    }
    (output / "five-seed-results.manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recovery", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.campaign, args.output, args.recovery)["cells"], indent=2))
