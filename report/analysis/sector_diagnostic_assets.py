"""Typeset the intermediate evidence ledger and its exploratory diagnostics."""

import csv
import hashlib
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from epistemics_pilot import tex_escape
from matplotlib.lines import Line2D
from sector_results import ARMS, COLORS, DOMAINS, MODELS

ARM_NAMES = {
    "review": "Review",
    "pressure": "Pressure",
    "misleading": "False alt.",
    "audit": "Audit",
    "all": "All",
}
TRACE_TITLES = {
    "routine_support": "Routine support",
    "verification_rejects_mismatch": "A mismatch is rejected",
    "pressure_loss": "Pressure and a narrower reading",
    "repair_but_original_upheld": "Repair while the original is upheld",
    "matching_original_rejected": "Reference match, jury rejection",
    "withdrawal_without_grade_loss": "Qualification without grade loss",
}


def percent(value, digits=1):
    return "N/A" if value is None else f"{100 * value:.{digits}f}"


def fraction(numerator, denominator):
    return f"{numerator}/{denominator}" if denominator else "N/A"


def flatten(row, prefix=""):
    result = {}
    for key, value in row.items():
        name = prefix + key
        if isinstance(value, dict):
            result.update(flatten(value, name + "."))
        else:
            result[name] = json.dumps(value) if isinstance(value, list) else value
    return result


def render(stats, inputs, existing, destination):
    tables, figures = destination / "tables", destination / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    rows = {}
    bank = inputs["bank"]
    rows["diagnostic-bank-categories"] = [
        [
            tex_escape(r["name"]),
            str(r["occupations"]),
            str(r["onet_tasks"]),
            str(r["records"]),
            str(r["frame_records"]),
            str(r["mapped_benchmarks"]),
            str(r["selected_groups"]),
        ]
        for r in bank["categories"]
    ]
    rows["diagnostic-bank-benchmarks"] = [
        [
            tex_escape(r["name"]),
            str(r["records"]),
            str(r["self_contained"]),
            str(r["frame_records"]),
            str(r["frame_groups"]),
            str(r["selected_groups"]),
        ]
        for r in bank["benchmarks"]
    ]
    all_cells = [r for r in stats["cells"] if r["arm"] == "all"]
    sums = lambda section, key: sum(r[section][key] for r in all_cells)
    rows["diagnostic-flow"] = [
        ["Catalog task records", str(bank["totals"]["tasks"])],
        [
            "Self-contained records before reference exclusions",
            str(bank["self_contained"]),
        ],
        [
            "Joined text/evidence/reference frame after exclusions",
            str(bank["frame_records"]),
        ],
        ["Selected source groups", str(len(stats["source_ledger"]))],
        ["Initial attempts", str(sum(r["assigned"] for r in stats["initial"]))],
        [
            "Strict initial schema successes",
            str(sum(r["strict"] for r in stats["initial"])),
        ],
        [
            "Additional lossless interpretations",
            str(sum(r["normalized"] for r in stats["initial"])),
        ],
        ["Usable initial answers", str(sum(r["usable"] for r in stats["initial"]))],
        ["Assigned primary branches", str(sums("transitions", "assigned"))],
        [
            "Structurally unavailable branches",
            str(sums("transitions", "initial_unavailable")),
        ],
        [
            "Unavailable defences after a usable initial",
            str(sums("transitions", "defence_unavailable")),
        ],
        ["Valid primary defences", str(sum(r["valid_defences"] for r in all_cells))],
        ["Settled primary verdicts", str(sums("jury", "settled"))],
        ["Unsettled executed primary episodes", str(sums("jury", "unsettled"))],
        [
            "Full three-ballot primary panels",
            str(sum(r["full_panels"] for r in all_cells)),
        ],
        [
            "Settled two-ballot primary panels",
            str(sum(r["two_ballot_settlements"] for r in all_cells)),
        ],
    ]
    rows["diagnostic-initial-format"] = []
    rows["diagnostic-high-confidence"] = []
    for r in stats["initial"]:
        names = [DOMAINS[r["domain"]], MODELS[r["model"]]]
        rows["diagnostic-initial-format"].append(
            names
            + [str(r[k]) for k in ("assigned", "strict", "normalized", "usable")]
            + [str(r["assigned"] - r["usable"])]
        )
        rows["diagnostic-high-confidence"].append(
            names
            + [
                str(r["usable"]),
                fraction(r["high_errors"], r["high_n"]),
                fraction(r["certain_errors"], r["certain_n"]),
                percent(r["confidence_match"]),
                percent(r["confidence_mismatch"]),
            ]
        )
    rows["diagnostic-transitions"] = []
    for r in stats["cells"]:
        if r["arm"] == "all":
            continue
        t = r["transitions"]
        rows["diagnostic-transitions"].append(
            [DOMAINS[r["domain"]], MODELS[r["model"]], ARM_NAMES[r["arm"]]]
            + [
                str(t[k])
                for k in (
                    "match_kept",
                    "match_lost",
                    "mismatch_repaired",
                    "mismatch_kept",
                    "initial_unavailable",
                    "defence_unavailable",
                )
            ]
        )
    for endpoint in ("concession", "correction"):
        values = []
        for r in stats["paired"]:
            if r["endpoint"] != endpoint:
                continue
            cells = []
            for arm in ("pressure", "misleading", "audit"):
                c = r["comparisons"][arm]
                cells.append(
                    "N/A"
                    if c["mean"] is None
                    else r"\shortstack{"
                    + f"{100 * c['mean']:+.1f} [{100 * c['ci_low']:.1f}, {100 * c['ci_high']:.1f}]"
                    + r"\\"
                    + f"g={c['eligible_groups']}"
                    + "}"
                )
            values.append([DOMAINS[r["domain"]], MODELS[r["model"]]] + cells)
        rows["diagnostic-paired-" + endpoint] = values
    rows["diagnostic-jury"] = []
    rows["diagnostic-support"] = []
    rows["diagnostic-citations"] = []
    for r in all_cells:
        names = [DOMAINS[r["domain"]], MODELS[r["model"]]]
        j = r["jury"]
        rows["diagnostic-jury"].append(
            names
            + [
                str(j[k])
                for k in (
                    "match_upheld",
                    "match_rejected",
                    "mismatch_upheld",
                    "mismatch_rejected",
                    "unsettled",
                )
            ]
            + [str(r["full_panels"]), str(r["two_ballot_settlements"])]
        )
        counts = [
            sum(n for key, n in r["support"].items() if key.startswith(s + ":"))
            for s in ("maintain", "qualify", "retract")
        ]
        rows["diagnostic-support"].append(
            names
            + list(map(str, counts))
            + [
                fraction(r["match_withdrawn"], r["match_n"]),
                fraction(r["mismatch_supported"], r["mismatch_n"]),
                str(r["maintain_withdrawn"]),
                str(r["repair_still_supported"]),
            ]
        )
        initial = next(
            x
            for x in stats["initial"]
            if x["model"] == r["model"] and x["domain"] == r["domain"]
        )
        rows["diagnostic-citations"].append(
            names
            + [
                str(initial["citations"].get(k, 0))
                for k in ("none", "all_literal", "nonliteral")
            ]
            + [
                str(r["quotes"].get(k, 0))
                for k in ("none", "all_literal", "nonliteral")
            ]
            + [
                str(r["literal_quote_persistent"]),
                fraction(
                    r["literal_quote_persistent_upheld"],
                    r["literal_quote_persistent_settled"],
                ),
            ]
        )
    rows["diagnostic-vote-patterns"] = [
        [
            DOMAINS[r["domain"]],
            tex_escape(r["pattern"]),
            str(r["n"]),
            fraction(r["original_matches"], r["n"]),
            percent(r["mean_original_forecast"]),
            percent(r["mean_jury_forecast"]),
        ]
        for r in stats["vote_patterns"]
    ]
    rows["diagnostic-forecast-bases"] = []
    for r in stats["forecasts"]:
        for target, short in (
            ("source", "Original"),
            ("current", "Current"),
            ("jury", "Jury"),
        ):
            rows["diagnostic-forecast-bases"].append(
                [
                    DOMAINS[r["domain"]],
                    MODELS[r["model"]],
                    short,
                    str(r["n"]),
                    percent(r[target + "_rate"]),
                    percent(r["p_" + target]),
                    f"{r['brier_' + target]:.3f}"
                    if r["brier_" + target] is not None
                    else "N/A",
                ]
            )
    rows["diagnostic-seed-stability"] = [
        [
            DOMAINS[r["domain"]],
            MODELS[r["model"]],
            "M" if r["initial_correct"] else "X",
            str(r["partial_groups"]),
        ]
        + list(map(str, r["histogram"]))
        for r in stats["seeds"]
    ]
    rows["diagnostic-resource-profile"] = [
        [
            "probe" if r["phase"] == "diagnostic" else tex_escape(r["phase"]),
            MODELS[r["model"]],
            tex_escape(r["role"]),
            str(r["requests"]),
            str(r["usage_available"]),
            f"{r['input_tokens'] / 1e6:.3f}",
            f"{r['output_tokens'] / 1e6:.3f}",
            f"{r['output_p50']:.0f}" if r["output_p50"] is not None else "N/A",
            f"{r['output_p90']:.0f}" if r["output_p90"] is not None else "N/A",
            str(r["finish_reasons"].get("length", 0)),
            str(r["requests"] - r["statuses"].get("complete", 0)),
        ]
        for r in stats["resources"]
    ]
    rows["diagnostic-grade-sensitivity"] = []
    for r in all_cells:
        model, domain = r["model"], r["domain"]
        old = existing["branches"][model]["domain:" + domain]
        pairs = []
        for arm, literal, audited in (
            ("pressure", "literal_concession", "concession"),
            ("audit", "literal_correction", "correction"),
            ("all", "literal_wrong_upheld", "wrong_upheld"),
        ):
            a, b = old[arm][literal], old[arm][audited]
            pairs.append(
                r"\shortstack{"
                + percent(a["mean"])
                + r" $\to$ "
                + percent(b["mean"])
                + r"\\$N$: "
                + str(a["completed"])
                + r" $\to$ "
                + str(b["completed"])
                + "}"
            )
        rows["diagnostic-grade-sensitivity"].append(
            [DOMAINS[domain], MODELS[model]] + pairs
        )
    for domain in DOMAINS:
        records = []
        for r in stats["source_ledger"]:
            if r["domain"] != domain:
                continue
            source_id = r["task_id"].split(":", 1)[1]
            if r["benchmark"] == "tatqa":
                source_id = source_id[:8]
            else:
                source_id = source_id.replace("/page_", " p").replace(".pdf", "")
            grades = []
            for model in MODELS:
                g = r["grades"][model]
                grades.append(
                    "--"
                    if g["audited"] is None
                    else str(int(g["audited"]))
                    if g["audited"] == g["literal"]
                    else r"$"
                    + str(int(g["literal"]))
                    + r"\to"
                    + str(int(g["audited"]))
                    + "$"
                )
            records.append(
                [r["code"], r"\path{" + source_id + "}"]
                + grades
                + [
                    fraction(r["pressure_lost"], r["pressure_n"]),
                    fraction(r["audit_repaired"], r["audit_n"]),
                    fraction(r["mismatch_upheld"], r["mismatch_settled"]),
                ]
            )
        rows["diagnostic-ledger-" + domain] = records
    rows["diagnostic-reliability"] = []
    for r in stats["reliability"]:
        a = r["accuracy"]
        interval = (
            "N/A"
            if a["mean"] is None
            else f"[{100 * a['ci_low']:.1f}, {100 * a['ci_high']:.1f}]"
        )
        rows["diagnostic-reliability"].append(
            [
                MODELS[r["model"]],
                f"{r['bin'] / 10:.1f}--{(r['bin'] + 1) / 10:.1f}",
                str(a["completed"]),
                percent(r["confidence"]),
                percent(a["mean"]),
                interval,
                str(a.get("valid_bootstrap_replicates", 0)),
            ]
        )
    for name, values in rows.items():
        (tables / (name + ".tex")).write_text(
            "\n".join(" & ".join(r) + r" \\" for r in values) + "\n"
        )
    exports = {
        "sector-intermediate-cells": stats["cells"],
        "sector-source-ledger": stats["source_ledger"],
        "sector-source-arm-ledger": stats["source_arm_ledger"],
        "sector-confidence-bins": stats["reliability"],
        "sector-call-profile": stats["resources"],
        "sector-initial-diagnostics": stats["initial"],
        "sector-forecast-bases": stats["forecasts"],
        "sector-seed-stability": stats["seeds"],
        "sector-vote-patterns": stats["vote_patterns"],
        "sector-paired-contrasts": [
            {
                "model": r["model"],
                "domain": r["domain"],
                "endpoint": r["endpoint"],
                "contrast": comparison,
                **values,
            }
            for r in stats["paired"]
            for comparison, values in r["comparisons"].items()
        ],
    }
    for name, records in exports.items():
        flat = [flatten(r) for r in records]
        fields = list(dict.fromkeys(k for r in flat for k in r))
        with (destination / (name + ".csv")).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, restval=0)
            writer.writeheader()
            writer.writerows(flat)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["cmr10"],
            "mathtext.fontset": "cm",
            "axes.formatter.use_mathtext": True,
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    def save(fig, name):
        fig.savefig(
            figures / (name + ".pdf"),
            bbox_inches="tight",
            metadata={"CreationDate": None, "ModDate": None},
        )
        fig.savefig(figures / (name + ".png"), dpi=300, bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(6.5, 5), layout="constrained")
    for i, (model, name) in enumerate(MODELS.items()):
        ax = axes.flat[i]
        ax.plot([0, 100], [0, 100], color=".65", ls="--", lw=0.8)
        for r in (x for x in stats["reliability"] if x["model"] == model):
            s = r["accuracy"]
            if s["mean"] is None:
                continue
            x, y = 100 * r["confidence"], 100 * s["mean"]
            ax.errorbar(
                x,
                y,
                yerr=[
                    [max(0, y - 100 * s["ci_low"])],
                    [max(0, 100 * s["ci_high"] - y)],
                ],
                color=COLORS[i],
                marker="o",
                ms=4,
                capsize=2,
                lw=0.8,
            )
            ax.annotate(
                str(s["completed"]),
                (x, y),
                xytext=(-3, 5),
                textcoords="offset points",
                fontsize=7,
            )
        ax.set(
            xlim=(-3, 105),
            ylim=(-3, 108),
            title=name,
            xlabel="Mean confidence (%)",
            ylabel="Reference agreement (%)",
        )
        ax.grid(alpha=0.15)
    axes.flat[-1].axis("off")
    axes.flat[-1].text(
        0,
        0.75,
        "Fixed probability bins\nPoint labels: valid answers\nIntervals: source bootstrap\nEmpty bins have no point\nDashed: agreement = confidence",
        va="top",
        linespacing=1.7,
    )
    save(fig, "diagnostic-reliability")
    for initial_grade, suffix in ((True, "match"), (False, "mismatch")):
        fig, axes = plt.subplots(
            2, 2, figsize=(6.5, 4.8), sharey=True, layout="constrained"
        )
        bounds = []
        for ax, (domain, title) in zip(axes.flat, DOMAINS.items()):
            for i, model in enumerate(MODELS):
                for j, arm in enumerate(ARMS):
                    cell = next(
                        r
                        for r in stats["cells"]
                        if r["model"] == model
                        and r["domain"] == domain
                        and r["arm"] == arm
                    )
                    s = cell["updates"][str(initial_grade)]
                    if s["mean"] is None:
                        continue
                    bounds.extend([100 * s["ci_low"], 100 * s["ci_high"]])
                    y = 100 * s["mean"]
                    ax.errorbar(
                        j + (i - 2) * 0.13,
                        y,
                        yerr=[
                            [max(0, y - 100 * s["ci_low"])],
                            [max(0, 100 * s["ci_high"] - y)],
                        ],
                        color=COLORS[i],
                        marker=["o", "s", "^", "D", "P"][i],
                        ms=4,
                        capsize=2,
                        lw=0.8,
                    )
            ax.axhline(0, color=".5", lw=0.7)
            ax.set(
                xticks=range(4),
                xticklabels=["Review", "Pressure", "False alt.", "Audit"],
                title=title,
                ylabel="Original-correct forecast change (pp)",
            )
            ax.grid(axis="y", alpha=0.15)
        if bounds:
            for ax in axes.flat:
                ax.set_ylim(
                    5 * np.floor(min(0, min(bounds)) / 5) - 2,
                    5 * np.ceil(max(0, max(bounds)) / 5) + 2,
                )
        handles = [
            Line2D(
                [],
                [],
                color=COLORS[i],
                marker=["o", "s", "^", "D", "P"][i],
                ls="",
                label=name,
            )
            for i, name in enumerate(MODELS.values())
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=5, frameon=False)
        save(fig, "diagnostic-confidence-" + suffix)
    for domain, labels in (
        ("legal", ("Entailment", "Contradiction", "NotMentioned")),
        ("science", ("Supported", "Contradicted", "InsufficientEvidence")),
    ):
        fig, axes = plt.subplots(2, 3, figsize=(6.5, 5), layout="constrained")
        for i, (model, name) in enumerate(MODELS.items()):
            ax = axes.flat[i]
            records = [
                r
                for r in stats["categorical_confusions"]
                if r["model"] == model and r["domain"] == domain
            ]
            predictions = (
                (*labels, "Other")
                if any(r["answer"] not in labels for r in records)
                else labels
            )
            matrix = np.zeros((3, len(predictions)), dtype=int)
            for r in records:
                matrix[
                    labels.index(r["reference"]),
                    predictions.index(r["answer"]) if r["answer"] in labels else 3,
                ] += 1
            ax.imshow(matrix, vmin=0, vmax=10, cmap="Blues", aspect="equal")
            for (j, k), value in np.ndenumerate(matrix):
                ax.text(
                    k,
                    j,
                    str(value),
                    ha="center",
                    va="center",
                    color="white" if value >= 6 else "black",
                    fontsize=9,
                )
            ax.set(
                xticks=range(len(predictions)),
                xticklabels=["E", "C", "N", "Other"][: len(predictions)]
                if domain == "legal"
                else ["S", "C", "I", "Other"][: len(predictions)],
                yticks=range(3),
                yticklabels=["E", "C", "N"] if domain == "legal" else ["S", "C", "I"],
                title=f"{name} (n={len(records)})",
                xlabel="Initial answer",
                ylabel="Reference",
            )
        axes.flat[-1].axis("off")
        axes.flat[-1].text(
            0,
            0.8,
            (
                "E: Entailment\nC: Contradiction\nN: NotMentioned"
                if domain == "legal"
                else "S: Supported\nC: Contradicted\nI: InsufficientEvidence"
            )
            + "\n\nCounts, not percentages\nMissing outputs excluded",
            va="top",
            linespacing=1.7,
        )
        save(fig, "diagnostic-confusion-" + domain)
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.2), layout="constrained")
    for ax, correct, title in zip(
        axes, (True, False), ("Initially matching", "Initially mismatching")
    ):
        matrix = np.array(
            [
                [
                    sum(
                        r["histogram"][k]
                        for r in stats["seeds"]
                        if r["model"] == model and r["initial_correct"] is correct
                    )
                    for k in range(6)
                ]
                for model in MODELS
            ]
        )
        ax.imshow(matrix, cmap="Blues", aspect="auto")
        maximum = max(1, matrix.max())
        for (j, k), value in np.ndenumerate(matrix):
            ax.text(
                k,
                j,
                str(value),
                ha="center",
                va="center",
                color="white" if value > maximum * 0.55 else "black",
                fontsize=8,
            )
        ax.set(
            xticks=range(6),
            xticklabels=range(6),
            yticks=range(5),
            yticklabels=list(MODELS.values()),
            title=title,
            xlabel="Matching current answers among five",
        )
    save(fig, "diagnostic-seed-distribution")
    for index, trace in enumerate(inputs["traces"], 1):
        example = trace["example"]
        if example is None:
            continue
        snippets = example["snippets"]
        for s in snippets.values():
            if (
                hashlib.sha256(s["text"].encode()).hexdigest() != s["text_sha256"]
                or len(s["text"]) != s["end"] - s["start"]
            ):
                raise ValueError("Changed intermediate trace excerpt")
        display = lambda s: tex_escape(s).translate(
            {
                0x202F: r"\,",
                0x2212: r"\ensuremath{-}",
                0x2011: "-",
                0xD7: r"\ensuremath{\times}",
            }
        )
        parts = [
            r"\begin{modelexample}[unbreakable,before upper={\setlength{\parskip}{4pt}}]{Z"
            + str(index)
            + ". "
            + tex_escape(TRACE_TITLES[trace["pattern"]])
            + "}",
            r"\textbf{"
            + tex_escape(MODELS[example["model"]])
            + " original: "
            + display(example["original_answer"])
            + ".} ``"
            + display(snippets["initial"]["text"])
            + (r"\ldots" if snippets["initial"]["truncated"] else "")
            + "''",
            r"\par\textbf{Objection.} ``"
            + display(snippets["challenge"]["text"])
            + (r"\ldots" if snippets["challenge"]["truncated"] else "")
            + "''",
            r"\tcblower",
            r"\textbf{Current: "
            + display(example["answer"])
            + "; "
            + tex_escape(example["stance"])
            + ".} ``"
            + display(snippets["defence"]["text"])
            + (r"\ldots" if snippets["defence"]["truncated"] else "")
            + "''",
            r"\par\textbf{Juror 1.} ``"
            + display(snippets["juror"]["text"])
            + (r"\ldots" if snippets["juror"]["truncated"] else "")
            + "''",
            r"\par\textbf{Structured outputs.} Original support: "
            + ("yes" if example["original_still_supported"] else "no")
            + "; original-correct forecast "
            + percent(example["confidence_original"])
            + r"\%; jury-uphold forecast "
            + percent(example["jury_forecast"])
            + r"\%. Vote "
            + f"{example['support_votes']}--{example['reject_votes']}.",
            r"\par\smallskip{\footnotesize "
            + r"\path{"
            + example["task_id"]
            + "}; "
            + tex_escape(example["arm"])
            + f", seed {example['seed']}. Reference grades: original "
            + ("match" if example["initial_correct"] else "mismatch")
            + ", current "
            + ("match" if example["final_correct"] else "mismatch")
            + ". Exact field offsets and hashes are retained in the intermediate snapshot.}",
            r"\end{modelexample}",
        ]
        (tables / f"diagnostic-trace-{index}.tex").write_text("\n".join(parts) + "\n")
