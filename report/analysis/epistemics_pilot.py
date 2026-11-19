"""Admit the frozen pilot and regenerate its report statistics and visual assets.

Extraction verifies the archived file inventory. Ordinary regeneration uses the
portable snapshot and makes no network or model calls. Intervals describe
assumed repeated generations for one fixed answer, not a population of tasks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from matplotlib.colors import ListedColormap
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "report/epistemics"
SNAPSHOT = ROOT / "report/data/epistemics-pilot.json"
ARTIFACT = "lbxa-corp/apart-epistemics-sprint/contract-micro-g9t35ump:v734"
MODELS = {
    "@cf/deepseek-ai/deepseek-v4-pro-0813": "DeepSeek",
    "@cf/zai-org/glm-5.3": "GLM-5.3",
    "@cf/moonshotai/kimi-k2.6": "Kimi K2.6",
}
ARMS = {
    "neutral": "Review",
    "pressure": "Pressure",
    "invalid_argument": "Misleading",
    "source_audit": "Audit",
}
SEEDS = (101, 102, 103, 104, 105)
BLUE, ORANGE, GRAY = "#0072B2", "#D55E00", "#DDDDDD"


@dataclass(frozen=True)
class Cell:
    model: str
    task_id: str
    initial_seed: int
    seed: int
    arm: str
    initial_correct: bool
    final_correct: bool | None
    defence_status: str
    jury_outcome: str | None
    support_votes: int | None
    reject_votes: int | None
    revealed_jurors: int | None
    directory: str
    baseline_sha256: str

    def __post_init__(self):
        if self.model not in MODELS or self.arm not in ARMS or self.seed not in SEEDS:
            raise ValueError("Cell is outside the admitted cohort")
        if type(self.initial_correct) is not bool:
            raise ValueError("Initial correctness must be Boolean")
        if self.final_correct is not None and type(self.final_correct) is not bool:
            raise ValueError("Missing correctness cannot become a zero")
        if (self.final_correct is not None) != (self.defence_status == "complete"):
            raise ValueError("Completion and grading disagree")
        if self.jury_outcome not in {None, "CREATOR_SUPPORTED", "CHALLENGER_SUPPORTED"}:
            raise ValueError("Unknown jury outcome")


def summarize_binary(values: list[bool | None]) -> dict:
    valid = [int(v) for v in values if v is not None]
    n, k = len(valid), sum(valid)
    interval = binomtest(k, n).proportion_ci(method="exact") if n else None
    return {
        "assigned": len(values),
        "completed": n,
        "successes": k,
        "mean": statistics.mean(valid) if n else None,
        "variance": statistics.variance(valid) if n > 1 else None,
        "sd": statistics.stdev(valid) if n > 1 else None,
        "ci_low": interval.low if interval else None,
        "ci_high": interval.high if interval else None,
    }


def extract(source: Path, registry: Path, destination: Path) -> None:
    register = json.loads(registry.read_text())
    if register["artifact"] != ARTIFACT or not register["all_files_verified"]:
        raise ValueError("Use the frozen, verified evidence artifact")
    for name, digest in register["file_sha256"].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Archived file changed: {name}")
    study = json.loads((source / "study.json").read_text())
    references = {c["task_id"]: c["reference"] for c in study["cases"]}
    cells = []
    with (source / "results.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            initial = row["initial_classification"] == references[row["task_id"]]
            final = (
                row["final_classification"] == references[row["task_id"]]
                if row["final_classification"]
                else None
            )
            if row["initial_correct"] != str(initial) or row["final_correct"] != (
                str(final) if final is not None else ""
            ):
                raise ValueError("Source grading differs from the audited CSV")
            cells.append(
                asdict(
                    Cell(
                        model=row["model"],
                        task_id=row["task_id"],
                        initial_seed=int(row["initial_seed"]),
                        seed=int(row["defence_seed"]),
                        arm=row["condition"],
                        initial_correct=initial,
                        final_correct=final,
                        defence_status=row["defence_status"],
                        jury_outcome=row["jury_outcome"] or None,
                        support_votes=int(row["support_votes"])
                        if row["support_votes"]
                        else None,
                        reject_votes=int(row["reject_votes"])
                        if row["reject_votes"]
                        else None,
                        revealed_jurors=int(row["revealed_jurors"])
                        if row["revealed_jurors"]
                        else None,
                        directory=row["directory"],
                        baseline_sha256=row["baseline_sha256"],
                    )
                )
            )

    snippets = {}

    def retain(name, filename, pointer, value, start_marker=None, end_marker=None):
        start = value.index(start_marker) if start_marker else 0
        end = value.index(end_marker, start) if end_marker else len(value)
        snippets[name] = {
            "text": value[start:end],
            "start": start,
            "end": end,
            "file": filename,
            "json_pointer": pointer,
            "file_sha256": register["file_sha256"][filename],
            "field_sha256": hashlib.sha256(value.encode()).hexdigest(),
        }

    selected = {}
    for name, model, arm, seed in (
        ("glm_review", "@cf/zai-org/glm-5.3", "neutral", 104),
        ("glm_audit", "@cf/zai-org/glm-5.3", "source_audit", 104),
        ("deep_review", "@cf/deepseek-ai/deepseek-v4-pro-0813", "neutral", 102),
        ("deep_audit", "@cf/deepseek-ai/deepseek-v4-pro-0813", "source_audit", 102),
    ):
        index, record = next(
            (i, d)
            for i, d in enumerate(study["disputes"])
            if d["model"] == model
            and d["condition"] == arm
            and d["seed"] == seed
            and d["task_id"] == "contractnli:293/nda-1"
        )
        selected[name] = record
        filename = record["directory"] + "/defence.json"
        call = json.loads((source / filename).read_text())
        marker = {
            "glm_review": "Since the obligation",
            "glm_audit": "The absence",
            "deep_review": "A blanket requirement",
            "deep_audit": "It does not contain",
        }[name]
        retain(
            name, filename, "/parsed/explanation", call["parsed"]["explanation"], marker
        )
        retain(
            name + "_prompt",
            "study.json",
            f"/disputes/{index}/challenge",
            record["challenge"],
        )
    glm = selected["glm_review"]
    filename = glm["directory"] + "/juror-1.json"
    ballot = json.loads((source / filename).read_text())
    retain(
        "juror",
        filename,
        "/parsed/assessment",
        ballot["parsed"]["assessment"],
        "Because",
    )
    initial = next(
        s
        for s in study["screens"]
        if s["model"] == glm["model"]
        and s["task_id"] == glm["task_id"]
        and s["seed"] == glm["initial_seed"]
    )
    index = study["screens"].index(initial)
    retain(
        "initial",
        "study.json",
        f"/screens/{index}/call/parsed/explanation",
        initial["call"]["parsed"]["explanation"],
    )
    case_index, case = next(
        (i, c)
        for i, c in enumerate(study["cases"])
        if c["task_id"] == "contractnli:293/nda-1"
    )
    retain(
        "source",
        "study.json",
        f"/cases/{case_index}/document",
        case["document"],
        "keep confidential any information",
        " by:",
    )
    retain(
        "hypothesis",
        "study.json",
        f"/cases/{case_index}/task",
        case["task"],
        "All Confidential Information",
    )
    for name in ("initial.md", "defence.md", "jury.md"):
        text = (source / "design" / name).read_text()
        retain(name, "design/" + name, None, text)
    snapshot = {
        "schema": 1,
        "provenance": {
            k: register[k]
            for k in (
                "artifact",
                "digest",
                "study_sha256",
                "analysis_sha256",
                "collection_cutoff_utc",
            )
        },
        "source_files": {
            name: register["file_sha256"][name]
            for name in (
                "study.json",
                "results.csv",
                "findings.json",
                "source-audit.json",
            )
        },
        "source_audit": json.loads((source / "source-audit.json").read_text()),
        "source_revision": study["source_revision"],
        "reasoning_effort": study["reasoning_effort_by_model"],
        "spending": study["spending"],
        "cases": [
            {k: c[k] for k in ("task_id", "reference", "document_sha256", "source_url")}
            for c in study["cases"]
        ],
        "screens": [
            {
                "model": s["model"],
                "task_id": s["task_id"],
                "seed": s["seed"],
                "correct": s["call"]["parsed"]["classification"]
                == references[s["task_id"]],
            }
            for s in study["screens"]
        ],
        "cells": cells,
        "snippets": snippets,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(snapshot, indent=2) + "\n")


def load_snapshot(path: Path) -> tuple[dict, list[Cell]]:
    data = json.loads(path.read_text())
    if data["schema"] != 1 or data["provenance"]["artifact"] != ARTIFACT:
        raise ValueError("Snapshot belongs to a different study")
    cells = [Cell(**d) for d in data["cells"]]
    keys = {(c.model, c.task_id, c.initial_seed, c.seed, c.arm) for c in cells}
    if len(keys) != len(cells) or len(cells) != 100 or len(data["screens"]) != 45:
        raise ValueError("Duplicate or incomplete admitted cohort")
    for model in MODELS:
        for initial in (True, False):
            group = [
                c for c in cells if c.model == model and c.initial_correct == initial
            ]
            if group:
                for arm in ARMS:
                    if sorted(c.seed for c in group if c.arm == arm) != list(SEEDS):
                        raise ValueError(
                            "Each selected answer needs all five assigned seeds"
                        )
                if len({c.baseline_sha256 for c in group}) != 1:
                    raise ValueError("Conditions no longer share one frozen answer")
    return data, cells


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in text)


def render(data: dict, cells: list[Cell], directory: Path) -> None:
    figures, tables = directory / "figures", directory / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "cmr10",
            "mathtext.fontset": "cm",
            "font.size": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "axes.formatter.use_mathtext": True,
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#666666",
            "axes.linewidth": 0.7,
            "text.color": "#222222",
            "savefig.dpi": 300,
        }
    )
    summaries = {}
    for model in MODELS:
        summaries[model] = {
            arm: summarize_binary(
                [
                    c.final_correct
                    for c in cells
                    if c.model == model and not c.initial_correct and c.arm == arm
                ]
            )
            for arm in ARMS
        }

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.55), layout="constrained")
    for ax, model, marker in zip(axes, list(MODELS)[:2], ("o", "s")):
        for y, arm in enumerate(ARMS):
            s = summaries[model][arm]
            mean = 100 * s["mean"]
            ax.errorbar(
                mean,
                y,
                xerr=[[mean - 100 * s["ci_low"]], [100 * s["ci_high"] - mean]],
                fmt=marker,
                color=BLUE,
                ms=5,
                capsize=3,
                lw=1.15,
            )
            ax.text(
                min(max(mean, 4), 96),
                y - 0.17,
                f"{s['successes']}/5",
                ha="right" if mean > 90 else "left" if mean < 10 else "center",
                fontsize=8.5,
            )
        ax.set(
            yticks=range(4),
            yticklabels=list(ARMS.values()),
            ylim=(3.6, -0.6),
            xlim=(-4, 104),
            xticks=(0, 25, 50, 75, 100),
            xlabel="Error corrected (%)",
        )
        ax.set_title(MODELS[model], loc="left", fontsize=10)
        ax.grid(axis="x", color="#E5E5E5", lw=0.6)
        ax.set_axisbelow(True)
    for suffix in ("pdf", "png"):
        fig.savefig(figures / f"correction-ci.{suffix}")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.35), layout="constrained")
    for ax, model in zip(axes, list(MODELS)[:2]):
        matrix = np.array(
            [
                [
                    next(
                        c.final_correct
                        for c in cells
                        if c.model == model
                        and not c.initial_correct
                        and c.seed == seed
                        and c.arm == arm
                    )
                    for arm in ARMS
                ]
                for seed in SEEDS
            ],
            dtype=int,
        )
        ax.imshow(
            matrix,
            cmap=ListedColormap(["#EEEEEE", "#D1E6F0"]),
            vmin=0,
            vmax=1,
            aspect="auto",
        )
        for y in range(5):
            for x in range(4):
                ax.text(x, y, str(matrix[y, x]), ha="center", va="center", fontsize=10)
        ax.set(
            xticks=range(4),
            xticklabels=list(ARMS.values()),
            yticks=range(5),
            yticklabels=SEEDS,
            ylabel="Defence seed",
        )
        ax.set_title(MODELS[model], loc="left", fontsize=10)
        ax.tick_params(length=0)
    for suffix in ("pdf", "png"):
        fig.savefig(figures / f"seed-outcomes.{suffix}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 1.55), layout="constrained")
    for y, model in enumerate(list(MODELS)[:2]):
        group = [c for c in cells if c.model == model and not c.initial_correct]
        values = [
            sum(c.jury_outcome == "CHALLENGER_SUPPORTED" for c in group),
            sum(c.jury_outcome == "CREATOR_SUPPORTED" for c in group),
            sum(c.jury_outcome is None for c in group),
        ]
        left = 0
        for i, (value, color, label) in enumerate(
            zip(
                values,
                (BLUE, ORANGE, GRAY),
                ("Rejected original error", "Upheld original error", "No verdict"),
            )
        ):
            ax.barh(
                y,
                value,
                left=left,
                height=0.5,
                color=color,
                edgecolor="white",
                hatch="//" if i == 2 else None,
                label=label if y == 0 else None,
            )
            ax.text(
                left + value / 2,
                y,
                str(value),
                ha="center",
                va="center",
                color="white" if i < 2 else "#222222",
                fontsize=9,
            )
            left += value
    ax.set(
        yticks=(0, 1),
        yticklabels=("DeepSeek", "GLM-5.3"),
        xlim=(0, 20),
        xticks=(0, 5, 10, 15, 20),
        xlabel="Assigned branches of the saved error",
    )
    ax.invert_yaxis()
    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1), ncols=3, frameon=False, fontsize=8
    )
    for suffix in ("pdf", "png"):
        fig.savefig(figures / f"jury-reference.{suffix}")
    plt.close(fig)

    primary = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r" & & & \multicolumn{4}{c}{Saved error corrected / 5}\\",
        r"\cmidrule(lr){4-7}",
        r"Answerer & Initial & Retained & Review & Pressure & Mislead & Audit\\",
        r"\midrule",
    ]
    jury = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Answerer & Verdicts & Wrong upheld & No verdict & Full panels\\",
        r"\midrule",
    ]
    uncertainty = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Answerer & Condition & Corrected & $S^2$ & SD (pp) & 95\% CI (\%)\\",
        r"\midrule",
    ]
    for model, name in MODELS.items():
        group = [c for c in cells if c.model == model]
        screens = [s for s in data["screens"] if s["model"] == model]
        correct = [
            c for c in group if c.initial_correct and c.final_correct is not None
        ]
        entries = [
            name,
            f"{sum(s['correct'] for s in screens)}/{len(screens)}",
            f"{sum(c.final_correct for c in correct)}/{len(correct)}",
        ]
        for arm, s in summaries[model].items():
            entries.append(f"{s['successes']}/5" if s["assigned"] else "N/A")
            if s["completed"]:
                uncertainty.append(
                    f"{name} & {ARMS[arm]} & {s['successes']}/5 & "
                    f"{s['variance']:.3f} & {100 * s['sd']:.1f} & "
                    f"[{100 * s['ci_low']:.1f}, {100 * s['ci_high']:.1f}]" + r"\\"
                )
        primary.append(" & ".join(entries) + r"\\")
        settled = [c for c in group if c.jury_outcome is not None]
        errors = [c for c in settled if not c.initial_correct]
        wrong = (
            f"{sum(c.jury_outcome == 'CREATOR_SUPPORTED' for c in errors)}/{len(errors)}"
            if errors
            else "N/A"
        )
        jury.append(
            f"{name} & {len(settled)}/{len(group)} & {wrong} & "
            f"{len(group) - len(settled)} & {sum(c.revealed_jurors == 3 for c in settled)}"
            + r"\\"
        )
    for filename, lines in (
        ("classification.tex", primary),
        ("jury.tex", jury),
        ("uncertainty.tex", uncertainty),
    ):
        (tables / filename).write_text(
            "\n".join(lines + [r"\bottomrule", r"\end{tabular}"]) + "\n"
        )

    q = {key: tex_escape(value["text"]) for key, value in data["snippets"].items()}
    (tables / "source-quote.tex").write_text("``" + q["source"] + "''\n")
    (tables / "hypothesis.tex").write_text("``" + q["hypothesis"] + "''\n")
    trace = next(
        c
        for c in cells
        if c.model == "@cf/zai-org/glm-5.3"
        and not c.initial_correct
        and c.arm == "neutral"
        and c.seed == 104
    )
    panel = [
        r"\begin{modelexample}{Selected GLM defence and jury response, seed 104}",
        r"\textbf{Scripted challenge (neutral review).} ``"
        + q["glm_review_prompt"]
        + "''",
        r"\par\textbf{GLM defence (excerpt; maintained Contradiction).} ``"
        + q["glm_review"]
        + "''",
        r"\tcblower",
        r"\textbf{DeepSeek juror 1 (excerpt).} ``" + q["juror"] + "''",
        r"\par\textbf{Executed vote.} "
        + f"Creator {trace.support_votes}; challenger {trace.reject_votes}.",
        r"\end{modelexample}",
    ]
    (tables / "jury-excerpt.tex").write_text("\n".join(panel) + "\n")
    panel = [
        r"\begin{modelexample}{Same answer, different challenge: DeepSeek, seed 102}",
        r"\textbf{Neutral-review defence (excerpt; maintained Contradiction).} ``"
        + q["deep_review"]
        + "''",
        r"\tcblower",
        r"\textbf{Source-audit prompt (verbatim).} ``" + q["deep_audit_prompt"] + "''",
        r"\par\textbf{Audit defence (excerpt; retracted to NotMentioned).} ``"
        + q["deep_audit"]
        + "''",
        r"\end{modelexample}",
    ]
    (tables / "paired-excerpt.tex").write_text("\n".join(panel) + "\n")
    (directory / "statistics.json").write_text(
        json.dumps(
            {
                "source_snapshot_sha256": hashlib.sha256(
                    SNAPSHOT.read_bytes()
                ).hexdigest(),
                "report_analysis_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest(),
                "method": "95% two-sided exact Clopper-Pearson; conditional Bernoulli model",
                "software": {
                    "matplotlib": matplotlib.__version__,
                    "numpy": np.__version__,
                    "scipy": scipy.__version__,
                },
                "correction": summaries,
            },
            indent=2,
        )
        + "\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", action="store_true")
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT
        / "harness/results/contract-micro/trial-20261115-native-continuation",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=ROOT / "harness/research/contract-micro/evidence-register.json",
    )
    args = parser.parse_args()
    if args.extract:
        extract(args.source, args.registry, SNAPSHOT)
    data, cells = load_snapshot(SNAPSHOT)
    render(data, cells, REPORT)
    print(f"Regenerated assets from {len(cells)} retained branches; no model calls.")


if __name__ == "__main__":
    main()
