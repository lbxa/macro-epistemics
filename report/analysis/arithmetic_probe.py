"""Source-located arithmetic example and the separate post hoc diagnostic."""

import argparse
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from epistemics_pilot import tex_escape
from sector_excerpts import extract as checked_main_excerpt_source
from sector_excerpts import freeze_span
from sector_results import COLORS, MODELS, ROOT, audited_numeric_grade

BRANCH = "11c495e81bb48bcc53c14f421794"
JUDGES = ("@cf/openai/gpt-oss-120b", "@cf/deepseek-ai/deepseek-v4-pro-0813")
CONDITIONS = ("calculate", "claim_only", "defended", "checked_evidence")


def standalone_call_correct(condition, parsed):
    if condition in {"calculate", "author_checked"}:
        target = {
            "kind": "adapter_unit_handling",
            "expected_base": "117624840"
            if condition == "author_checked"
            else "117624.84",
            "default_answer_scale": "thousand" if condition == "author_checked" else "",
        }
        return audited_numeric_grade(
            target, parsed.get("answer"), parsed.get("scale", "")
        )
    if condition not in CONDITIONS:
        raise ValueError("Unknown diagnostic condition")
    return parsed["verdict"] == "CHALLENGER_SUPPORTED"


def block_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["condition"] != "author_checked":
            groups[(row["model"], row["condition"], row["seed"])].append(row["correct"])
    blocks = []
    for (model, condition, seed), values in sorted(groups.items()):
        valid = [v for v in values if v is not None]
        right, wrong = sum(valid), sum(not v for v in valid)
        blocks.append(
            {
                "model": model,
                "condition": condition,
                "seed": seed,
                "observed": len(values),
                "valid": len(valid),
                "correct": right,
                "accuracy": statistics.mean(valid) if valid else None,
                "majority_correct": True
                if right >= 2
                else False
                if wrong >= 2
                else None,
            }
        )
    return blocks


def extract_main(source):
    checked = checked_main_excerpt_source(source)
    row = next(
        r
        for r in map(json.loads, (source / "branch.jsonl").read_text().splitlines())
        if r["id"] == BRANCH
    )
    result = row["result"]
    original = next(
        r
        for r in map(json.loads, (source / "initial.jsonl").read_text().splitlines())
        if r["payload"]["case_id"] == row["payload"]["case_id"]
        and r["payload"]["model"] == row["payload"]["model"]
    )
    if (
        hashlib.sha256(original["result"]["call"]["text"].encode()).hexdigest()
        != result["baseline_sha256"]
    ):
        raise ValueError("The arithmetic example lost its frozen initial answer")
    if (
        result["support_votes"] != 3
        or result["reject_votes"] != 0
        or any(
            b["status"] != "complete"
            or b["parsed"]["verdict"] != "CREATOR_SUPPORTED"
            or "117628.84" not in b["parsed"]["assessment"].replace(",", "")
            for b in result["ballots"]
        )
    ):
        raise ValueError("The selected arithmetic endorsement changed")
    fields = {
        "initial": (
            result["original_answer"]["explanation"],
            "/result/original_answer/explanation",
            "1084",
            None,
        ),
        "defence": (
            result["defence"]["parsed"]["explanation"],
            "/result/defence/parsed/explanation",
            "The requested",
            " The arithmetic",
        ),
        "juror": (
            result["ballots"][0]["parsed"]["assessment"],
            "/result/ballots/0/parsed/assessment",
            "Multiplying",
            None,
        ),
    }
    snippets = {
        key: freeze_span(
            value,
            filename="branch.jsonl",
            row=BRANCH,
            pointer=pointer,
            start=start,
            end=end,
        )
        for key, (value, pointer, start, end) in fields.items()
    }
    return {
        "artifact": checked["artifact"],
        "digest": checked["digest"],
        "files": checked["files"],
        "case_id": row["payload"]["case_id"],
        "branch_id": BRANCH,
        "model": row["payload"]["model"],
        "task_id": "finqa:GPN/2018/page_94.pdf-2",
        "baseline_sha256": result["baseline_sha256"],
        "branch_sha256": hashlib.sha256(
            json.dumps(row, sort_keys=True).encode()
        ).hexdigest(),
        "initial_confidence": result["original_answer"]["confidence_correct"],
        "p_original": result["defence"]["parsed"]["p_original_correct"],
        "p_jury": result["defence"]["parsed"]["p_jury_upholds"],
        "votes": [3, 0],
        "snippets": snippets,
    }


def extract_probe(source, main):
    register = json.loads((source / "download-register.json").read_text())
    for name, info in register["files"].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != info["sha256"]:
            raise ValueError("A downloaded diagnostic file changed")
    manifest = json.loads((source / "study.json").read_text())
    if (
        manifest["protocol"] != "arithmetic-context-v2-posthoc"
        or manifest["source_branch_sha256"] != main["branch_sha256"]
    ):
        raise ValueError("The diagnostic changed its frozen selected defence")
    rows = []
    expected = {
        (m, c, s, j)
        for m in JUDGES
        for c in CONDITIONS
        for s in range(101, 106)
        for j in (1, 2, 3)
    }
    expected.update(
        {("@cf/zai-org/glm-5.3", "author_checked", s, 0) for s in range(101, 106)}
    )
    for raw in map(json.loads, (source / "probe.jsonl").read_text().splitlines()):
        payload, result = raw["payload"], raw["result"] or {}
        key = tuple(payload[k] for k in ("model", "condition", "seed", "juror"))
        if key not in expected:
            raise ValueError("Unknown or duplicated diagnostic observation")
        expected.remove(key)
        parsed = result.get("parsed") or {}
        rows.append(
            {
                **payload,
                "id": raw["id"],
                "status": result.get("status", raw["status"]),
                "correct": standalone_call_correct(payload["condition"], parsed)
                if result.get("status") == "complete"
                else None,
                "parsed": parsed,
            }
        )
    return {
        "artifact": register["artifact"],
        "digest": register["digest"],
        "files": register["files"],
        "manifest": manifest,
        "progress": json.loads((source / "progress.json").read_text()),
        "unobserved": len(expected),
        "calls": rows,
        "blocks": block_summary(rows),
    }


def render(data, output):
    tables, figures = output / "tables", output / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    example = data["main"]
    snippets = example["snippets"]
    for snippet in snippets.values():
        if (
            hashlib.sha256(snippet["text"].encode()).hexdigest()
            != snippet["text_sha256"]
        ):
            raise ValueError("An arithmetic excerpt changed")

    def display(value):
        return tex_escape(value).translate(
            {
                0x202F: r"\,",
                0xD7: r"\ensuremath{\times}",
                0x2011: "-",
                0x2212: r"\ensuremath{-}",
            }
        )

    lines = [
        r"\begin{modelexample}[unbreakable]{Y1. Finance: the same false product, three endorsements}",
        r"\textbf{GLM original, 100\% confidence.} ``"
        + display(snippets["initial"]["text"])
        + "''",
        r"\par\textbf{Independent check.} $1084\times108.51=117624.84$, four less than the published product.",
        r"\tcblower",
        r"\textbf{Frozen audit defence.} ``"
        + display(snippets["defence"]["text"])
        + "''",
        r"\par\textbf{GPT-OSS juror 1.} ``" + display(snippets["juror"]["text"]) + "''",
        r"\par\textbf{Outcome.} All three jurors repeat the false product and uphold the original (3--0). The author forecasts 85\% original correctness and 80\% jury acceptance.",
        r"\par\smallskip{\footnotesize Source: \path{finqa:GPN/2018/page_94.pdf-2}; audit, defence seed 101. Selected after inspection; one fixed case. Source artifact and exact field offsets accompany the portable diagnostic snapshot.}",
        r"\end{modelexample}",
    ]
    (tables / "sector-arithmetic-case.tex").write_text("\n".join(lines) + "\n")
    probe = data.get("probe")
    if not probe:
        return
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["cmr10"],
            "mathtext.fontset": "cm",
            "axes.formatter.use_mathtext": True,
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=(6.5, 2.5), layout="constrained")
    summaries = []
    for model, color, marker, offset in (
        (JUDGES[1], COLORS[0], "o", -0.14),
        (JUDGES[0], COLORS[3], "D", 0.14),
    ):
        for i, condition in enumerate(CONDITIONS):
            blocks = [
                b
                for b in probe["blocks"]
                if b["model"] == model and b["condition"] == condition
            ]
            valid = [b["accuracy"] for b in blocks if b["accuracy"] is not None]
            for j, block in enumerate(blocks):
                if block["accuracy"] is not None:
                    ax.scatter(
                        i + offset + (j - 2) * 0.025,
                        100 * block["accuracy"],
                        s=15,
                        facecolors="none",
                        edgecolors=color,
                    )
            if valid:
                ax.scatter(
                    i + offset,
                    100 * statistics.mean(valid),
                    color=color,
                    marker=marker,
                    s=55,
                    label=MODELS[model] if i == 0 else None,
                    zorder=3,
                )
            summaries.append(
                {
                    "model": model,
                    "condition": condition,
                    "valid_calls": sum(b["valid"] for b in blocks),
                    "correct_calls": sum(b["correct"] for b in blocks),
                    "block_mean": statistics.mean(valid) if valid else None,
                    "block_sd": statistics.stdev(valid) if len(valid) > 1 else None,
                    "majority_correct": sum(
                        b["majority_correct"] is True for b in blocks
                    ),
                    "valid_majorities": sum(
                        b["majority_correct"] is not None for b in blocks
                    ),
                }
            )
    ax.set(
        xticks=range(4),
        xticklabels=["Calculate", "Claim only", "Defended", "Checked evidence"],
        ylabel="Correct calls (%)",
        ylim=(-6, 106),
    )
    ax.grid(axis="y", alpha=0.15)
    ax.legend(loc="center left", frameon=False)
    for extension in ("pdf", "png"):
        fig.savefig(
            figures / ("arithmetic-context." + extension), dpi=300, bbox_inches="tight"
        )
    plt.close(fig)
    data["probe"]["summary"] = summaries
    condition_names = dict(
        zip(CONDITIONS, ("Calculate", "Claim only", "Defended", "Checked"))
    )
    summary_rows = []
    for row in summaries:
        values = [
            MODELS[row["model"]],
            condition_names[row["condition"]],
            f"{row['correct_calls']}/{row['valid_calls']}",
            f"{100 * row['block_mean']:.1f}"
            if row["block_mean"] is not None
            else "N/A",
            f"{100 * row['block_sd']:.1f}" if row["block_sd"] is not None else "N/A",
            f"{row['majority_correct']}/{row['valid_majorities']}",
        ]
        summary_rows.append(" & ".join(values) + r" \\")
    (tables / "arithmetic-jurors.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{llrrrr}",
                r"\toprule",
                r"Family & Context & Correct calls & Block mean (\%) & SD (pp) & Correct majorities \\",
                r"\midrule",
                *summary_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )
    author_rows = []
    for row in sorted(
        (r for r in probe["calls"] if r["condition"] == "author_checked"),
        key=lambda r: r["seed"],
    ):
        parsed = row["parsed"]
        values = [
            str(row["seed"]),
            display(parsed.get("answer", "Unavailable")),
            "Yes"
            if row["correct"] is True
            else "No"
            if row["correct"] is False
            else "N/A",
            display(parsed.get("stance", "N/A")),
            "Yes"
            if parsed.get("original_still_supported") is True
            else "No"
            if parsed.get("original_still_supported") is False
            else "N/A",
            f"{100 * parsed['p_original_correct']:.0f}"
            if "p_original_correct" in parsed
            else "N/A",
            f"{100 * parsed['p_jury_upholds']:.0f}"
            if "p_jury_upholds" in parsed
            else "N/A",
        ]
        author_rows.append(" & ".join(values) + r" \\")
    (tables / "arithmetic-author.tex").write_text(
        "\n".join(
            [
                r"\begin{tabular}{rlrllrr}",
                r"\toprule",
                r"Seed & Current answer & Right & Stance & Supports old & $p_{old}$ (\%) & $p_{jury}$ (\%) \\",
                r"\midrule",
                *author_rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-source", type=Path)
    parser.add_argument("--probe-source", type=Path)
    parser.add_argument(
        "--snapshot", type=Path, default=ROOT / "report/data/arithmetic-diagnostic.json"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "report/epistemics")
    args = parser.parse_args()
    data = (
        {"main": extract_main(args.main_source), "probe": None}
        if args.main_source
        else json.loads(args.snapshot.read_text())
    )
    if args.probe_source:
        data["probe"] = extract_probe(args.probe_source, data["main"])
    data["analysis_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    render(data, args.output)
    args.snapshot.write_text(json.dumps(data, indent=2) + "\n")
    print(
        json.dumps(
            {
                "selected_branch": BRANCH,
                "diagnostic_calls": len(data["probe"]["calls"]) if data["probe"] else 0,
            }
        )
    )


if __name__ == "__main__":
    main()
