"""Freeze and typeset four visible trajectories from one immutable W&B artifact."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

from epistemics_pilot import tex_escape
from sector_results import MODELS

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "report/data/sector-excerpts.json"
ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v35"
DIGEST = "140e490593b5152b2a7759e70974d752"
SELECTION = (
    (
        "education",
        "21bbb14b26c3ab1cfbf710f36865",
        "X1. Education: praise, then correction",
    ),
    (
        "finance",
        "97bc5490ea4618f87ea91795b14e",
        "X2. Finance: resistance and a grading defect",
    ),
    (
        "legal",
        "c9b2012529d128ee2fe38565717b",
        "X3. Legal: the same omission, different inferences",
    ),
    (
        "science",
        "07e90469f31a095348a53e67d63f",
        "X4. Science: rejecting the objection, revising the claim",
    ),
)


def freeze_span(value, *, filename, row, pointer, start=None, end=None):
    first = value.index(start) if start else 0
    last = value.index(end, first) if end else len(value)
    text = value[first:last]
    return {
        "text": text,
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "field_sha256": hashlib.sha256(value.encode()).hexdigest(),
        "file": filename,
        "row_id": row,
        "pointer": pointer,
        "start": first,
        "end": last,
    }


def extract(source):
    register = json.loads((source / "download-register.json").read_text())
    if register["artifact"] != ARTIFACT or register["digest"] != DIGEST:
        raise ValueError("Use the pinned excerpt artifact")
    for name, entry in register["files"].items():
        content = (source / name).read_bytes()
        if (
            hashlib.sha256(content).hexdigest() != entry["sha256"]
            or base64.b64encode(
                hashlib.md5(content, usedforsecurity=False).digest()
            ).decode()
            != entry["wandb_digest"]
        ):
            raise ValueError(f"Changed archived input: {name}")
    study = json.loads((source / "study.json").read_text())
    if (
        hashlib.sha256((source / "cases.json").read_bytes()).hexdigest()
        != study["cases_sha256"]
    ):
        raise ValueError("The source case manifest changed")
    cases = {c["case_id"]: c for c in json.loads((source / "cases.json").read_text())}
    branches = {
        r["id"]: r
        for r in map(json.loads, (source / "branch.jsonl").read_text().splitlines())
    }
    originals = {
        (r["payload"]["case_id"], r["payload"]["model"]): r
        for r in map(json.loads, (source / "initial.jsonl").read_text().splitlines())
    }
    examples = []
    for key, branch_id, title in SELECTION:
        row = branches[branch_id]
        payload, result = row["payload"], row["result"]
        original = originals[(payload["case_id"], payload["model"])]
        call = original["result"]["call"]
        if (
            hashlib.sha256(call["text"].encode()).hexdigest()
            != result["baseline_sha256"]
        ):
            raise ValueError("The defence no longer shares the frozen initial answer")
        answer, defence = result["original_answer"], result["defence"]["parsed"]
        if answer != call["parsed"] or result["defence"]["status"] != "complete":
            raise ValueError("Selected visible answer is incomplete or changed")
        ballots = [b["parsed"] for b in result["ballots"]]
        counts = [
            sum(b["verdict"] == v for b in ballots)
            for v in ("CREATOR_SUPPORTED", "CHALLENGER_SUPPORTED")
        ]
        if (
            counts != [result["support_votes"], result["reject_votes"]]
            or sum(counts) != 3
        ):
            raise ValueError("Selected panel does not have three verified votes")
        snippets = {}
        fields = {
            "challenge": (result["challenge"], "/result/challenge"),
            "initial": (answer["explanation"], "/result/original_answer/explanation"),
            "defence": (defence["explanation"], "/result/defence/parsed/explanation"),
        }
        limits = {
            "education": {
                "initial": (None, " The target was"),
                "defence": ("The student's work", None),
            },
            "finance": {"defence": ("The challenger's figure", None)},
            "legal": {
                "defence": ("The definition further includes", None),
                "challenge": (
                    "Check numerical operations",
                    ". Identify exact evidence",
                ),
            },
            "science": {
                "initial": ("However, the abstract", None),
                "challenge": ("Only exact word-for-word", None),
                "defence": (None, " The material does support"),
            },
        }[key]
        for field, (value, pointer) in fields.items():
            start, end = limits.get(field, (None, None))
            snippets[field] = freeze_span(
                value,
                filename="branch.jsonl",
                row=branch_id,
                pointer=pointer,
                start=start,
                end=end,
            )
        if key == "legal":
            snippets["juror"] = freeze_span(
                ballots[1]["assessment"],
                filename="branch.jsonl",
                row=branch_id,
                pointer="/result/ballots/1/parsed/assessment",
                start="No clause requires",
            )
        case = cases[payload["case_id"]]
        examples.append(
            {
                "key": key,
                "title": title,
                "branch_id": branch_id,
                "initial_id": original["id"],
                "task_id": case["task_id"],
                "model": payload["model"],
                "arm": payload["arm"],
                "seed": payload["seed"],
                "reference": case["reference"],
                "initial_answer": answer["answer"],
                "initial_confidence": answer["confidence_correct"],
                "current_answer": defence["answer"],
                "p_original": defence["p_original_correct"],
                "p_jury": defence["p_jury_upholds"],
                "votes": counts,
                "baseline_sha256": result["baseline_sha256"],
                "snippets": snippets,
            }
        )
    return {
        "artifact": ARTIFACT,
        "digest": DIGEST,
        "selection": "Post hoc illustrative cases; no population or treatment-rate estimate",
        "visible_fields_only": True,
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "files": register["files"],
        "cutoff": json.loads((source / "progress.json").read_text())["updated_at"],
        "examples": examples,
    }


def render(data, output):
    if data["artifact"] != ARTIFACT or data["digest"] != DIGEST:
        raise ValueError("Excerpt snapshot belongs to a different artifact")
    if [e["key"] for e in data["examples"]] != [s[0] for s in SELECTION]:
        raise ValueError("Retain all four selected case panels")
    output.mkdir(parents=True, exist_ok=True)
    for example in data["examples"]:
        snippets = example["snippets"]
        for snippet in snippets.values():
            if (
                hashlib.sha256(snippet["text"].encode()).hexdigest()
                != snippet["text_sha256"]
                or len(snippet["text"]) != snippet["end"] - snippet["start"]
            ):
                raise ValueError("An excerpt changed after source validation")
        # Typography-only encoding; the snapshot retains exact original Unicode.
        display = {0x202F: r"\,", 0x2212: r"\ensuremath{-}", 0x2011: "-"}
        lines = [
            r"\begin{modelexample}[unbreakable,before upper={\setlength{\parskip}{4pt}}]{"
            + tex_escape(example["title"])
            + "}"
        ]
        lines.append(
            r"\textbf{"
            + tex_escape(MODELS[example["model"]])
            + r" original: "
            + tex_escape(example["initial_answer"])
            + f"; {100 * example['initial_confidence']:g}"
            + r"\% confidence.}"
        )
        if example["key"] != "legal":
            lines.append(
                "``" + tex_escape(snippets["initial"]["text"]).translate(display) + "''"
            )
        lines.append(
            r"\par\textbf{Scripted objection (excerpt).} ``"
            + tex_escape(snippets["challenge"]["text"]).translate(display)
            + "''"
        )
        lines.append(r"\tcblower")
        lines.append(
            r"\textbf{Defence: "
            + tex_escape(example["current_answer"])
            + r".} ``"
            + tex_escape(snippets["defence"]["text"]).translate(display)
            + "''"
        )
        if "juror" in snippets:
            lines.append(
                r"\par\textbf{Juror 2 (rejects).} ``"
                + tex_escape(snippets["juror"]["text"]).translate(display)
                + "''"
            )
        lines.append(
            r"\par\textbf{Forecasts and outcome.} Original-correct: "
            + f"{100 * example['p_original']:g}"
            + r"\%; jury-uphold: "
            + f"{100 * example['p_jury']:g}"
            + r"\%. Vote (uphold--reject): "
            + f"{example['votes'][0]}--{example['votes'][1]}."
        )
        lines.append(
            r"\par\smallskip{\footnotesize Source: \path{"
            + example["task_id"]
            + "}; "
            + tex_escape(example["arm"])
            + f", defence seed {example['seed']}. "
            + r"Reference: "
            + tex_escape(example["reference"])
            + ". "
            + r"Exact locators and hashes: Appendix~\ref{app:excerpt-provenance}.}"
        )
        lines.append(r"\end{modelexample}")
        (output / f"sector-case-{example['key']}.tex").write_text(
            "\n".join(lines) + "\n"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    data = extract(args.source) if args.source else json.loads(SNAPSHOT.read_text())
    if args.source:
        SNAPSHOT.write_text(json.dumps(data, indent=2) + "\n")
    render(data, ROOT / "report/epistemics/tables")


if __name__ == "__main__":
    main()
