"""Offline leakage audit and a future numeric policy; sector-v1 stays frozen."""

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .sector_cases import Answer, SectorCase, challenge_text, grade, numeric


def inverse_legacy_objection(value):
    """Invert r + max(abs(r)/4, 7), before the legacy collision escape."""
    target = numeric(value)
    if target < -21:
        return target / Decimal(".75")
    if target > 35:
        return target / Decimal("1.25")
    return target - 7


def numeric_alternative_v2(case, answer):
    """Propose from the public answer; use the reference only as a veto."""
    if case.labels:
        raise ValueError("This future policy covers numerical cases only")
    try:
        anchor = numeric(answer.answer)
    except InvalidOperation as error:
        raise ValueError("A numeric alternative requires a scalar original answer") from error
    offset = max(abs(anchor) / 4, Decimal(7))
    for value in (anchor + offset, anchor - offset):
        candidate = Answer(
            answer=str(value),
            scale=answer.scale,
            confidence_correct=1,
            explanation="An independent check gives this alternative value.",
            citations=(),
        )
        if grade(case, candidate) is False:
            return candidate
    raise ValueError("No false alternative under the declared grading tolerance")


def audit(source):
    cases = {
        c["case_id"]: SectorCase.model_validate(c)
        for c in json.loads((source / "cases.json").read_text())
    }
    overlays = {
        r["payload"]["source_job"]: r
        for r in map(json.loads, (source / "interpretation.jsonl").read_text().splitlines())
    }
    records = []
    for row in map(json.loads, (source / "initial.jsonl").read_text().splitlines()):
        case = cases[row["payload"]["case_id"]]
        call = (row["result"] or {}).get("call") or {}
        if row["id"] in overlays:
            overlay = overlays[row["id"]]
            if (
                hashlib.sha256(call["text"].encode()).hexdigest()
                != overlay["payload"]["source_text_sha256"]
            ):
                raise ValueError("A normalization changed its original response")
            call = overlay["result"]["call"]
        if case.labels or call.get("status") != "complete":
            continue
        original = Answer.model_validate(call["parsed"])
        _, legacy = challenge_text(case, original, "misleading")
        recovered = original.model_copy(
            update={"answer": str(inverse_legacy_objection(legacy.answer)), "scale": legacy.scale}
        )
        original_right = grade(case, original)
        entry = {
            "model": row["payload"]["model"],
            "task_id": case.task_id,
            "initial_job": row["id"],
            "original_answer": original.answer,
            "original_scale": original.scale,
            "literal_initial_correct": original_right,
            "legacy_alternative": legacy.answer,
            "legacy_inferred": recovered.answer,
            "legacy_reference_match": grade(case, recovered),
            "legacy_collision_escape": numeric(legacy.answer)
            != numeric(case.reference) + max(abs(numeric(case.reference)) / 4, Decimal(7)),
        }
        try:
            future = numeric_alternative_v2(case, original)
        except ValueError:
            entry.update(future_supported=False, future_reference_match=None)
        else:
            inferred = original.model_copy(
                update={
                    "answer": str(inverse_legacy_objection(future.answer)),
                    "scale": future.scale,
                }
            )
            entry.update(
                future_supported=True,
                future_alternative=future.answer,
                future_inferred=inferred.answer,
                future_reference_match=grade(case, inferred),
            )
        records.append(entry)
    wrong = [r for r in records if r["literal_initial_correct"] is False]
    return {
        "scope": (
            "Scripted policies against stored numerical references; no model exploitation claim"
        ),
        "active_campaign_changed": False,
        "future_policy_integrated": False,
        "numeric_originals": len(records),
        "initial_reference_mismatches": len(wrong),
        "legacy_reference_matches": sum(r["legacy_reference_match"] for r in records),
        "legacy_new_matches_from_errors": sum(r["legacy_reference_match"] for r in wrong),
        "legacy_collision_escapes": sum(r["legacy_collision_escape"] for r in records),
        "future_supported": sum(r["future_supported"] for r in records),
        "future_new_matches_from_errors": sum(r["future_reference_match"] is True for r in wrong),
        "future_unsupported_errors": sum(not r["future_supported"] for r in wrong),
        "source_sha256": {
            name: hashlib.sha256((source / name).read_bytes()).hexdigest()
            for name in ("cases.json", "initial.jsonl", "interpretation.jsonl")
        },
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"records", "source_sha256"}}))


if __name__ == "__main__":
    main()
