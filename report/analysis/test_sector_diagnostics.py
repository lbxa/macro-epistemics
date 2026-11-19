import hashlib
import json
import unittest
from pathlib import Path

from sector_diagnostics import (
    citation_class,
    confidence_bin,
    joint_verdicts,
    prefix_excerpt,
    project_call,
    seed_stability,
    transition_counts,
)


class IntermediateEvidenceTests(unittest.TestCase):
    def test_frozen_census_reconciles_branches_and_source_seed_groups(self):
        root = Path(__file__).resolve().parents[1]
        study = json.loads((root / "data/sector-study.json").read_text())
        diagnostics = json.loads(
            (root / "epistemics/sector-diagnostic-statistics.json").read_text()
        )
        rows = study["branches"]
        counts = transition_counts(rows)
        self.assertEqual(counts["assigned"], 12000)
        self.assertEqual(counts["initial_unavailable"], 380)
        self.assertEqual(counts["defence_unavailable"], 137)
        self.assertEqual(sum(counts.values()) - counts["assigned"], 12000)
        jury = joint_verdicts(rows)
        self.assertEqual(jury["settled"], 11469)
        self.assertEqual(jury["unsettled"], 151)
        ledger = diagnostics["source_arm_ledger"]
        self.assertEqual(len(ledger), 2400)
        identities = {(r["case_id"], r["model"], r["arm"]) for r in ledger}
        self.assertEqual(len(identities), len(ledger))
        for field in ("final_correct", "original_supported", "jury_upheld"):
            self.assertEqual(sum(len(r[field]) for r in ledger), 12000)
            self.assertTrue(all(set(r[field]) <= {"0", "1", "-"} for r in ledger))
        self.assertEqual(sum(r["jury_upheld"].count("-") for r in ledger), 380 + 151)

    def test_transition_table_accounts_for_missing_stages_without_grading_them(self):
        rows = [
            {"initial_correct": a, "final_correct": b}
            for a, b in [
                (True, True),
                (True, False),
                (False, True),
                (False, False),
                (True, None),
                (None, None),
            ]
        ]
        self.assertEqual(
            transition_counts(rows),
            {
                "assigned": 6,
                "match_kept": 1,
                "match_lost": 1,
                "mismatch_repaired": 1,
                "mismatch_kept": 1,
                "defence_unavailable": 1,
                "initial_unavailable": 1,
            },
        )
        with self.assertRaisesRegex(ValueError, "initial"):
            transition_counts([{"initial_correct": None, "final_correct": True}])

    def test_seed_histogram_does_not_promote_partial_groups_to_five_replicates(self):
        rows = [
            {
                "model": "m",
                "case_id": "a",
                "arm": "review",
                "seed": s,
                "initial_correct": False,
                "final_correct": s == 101,
            }
            for s in range(101, 106)
        ]
        rows += [
            {
                "model": "m",
                "case_id": "b",
                "arm": "review",
                "seed": s,
                "initial_correct": False,
                "final_correct": True if s < 105 else None,
            }
            for s in range(101, 106)
        ]
        result = seed_stability(rows, False)
        self.assertEqual(result["histogram"], [0, 1, 0, 0, 0, 0])
        self.assertEqual((result["complete_groups"], result["partial_groups"]), (1, 1))
        with self.assertRaisesRegex(ValueError, "seed"):
            seed_stability(rows + [rows[0]], False)

    def test_probability_bin_includes_certainty_and_rejects_invalid_values(self):
        self.assertEqual([confidence_bin(x) for x in [0, 0.1, 0.9, 1]], [0, 1, 9, 9])
        self.assertIsNone(confidence_bin(None))
        for x in [-0.1, 1.1, float("nan")]:
            with self.assertRaises(ValueError):
                confidence_bin(x)

    def test_jury_is_scored_against_the_original_and_aborts_remain_missing(self):
        rows = [
            {"initial_correct": False, "final_correct": True, "jury_upheld": True},
            {"initial_correct": True, "final_correct": False, "jury_upheld": False},
            {"initial_correct": True, "final_correct": True, "jury_upheld": None},
        ]
        result = joint_verdicts(rows)
        self.assertEqual(result["mismatch_upheld"], 1)
        self.assertEqual(result["match_rejected"], 1)
        self.assertEqual(result["repaired_original_upheld"], 1)
        self.assertEqual(result["unsettled"], 1)
        self.assertEqual(result["settled"], 2)

    def test_absent_quotes_are_distinct_from_literal_matches(self):
        self.assertEqual(citation_class({"citations": 0, "nonmatching": 0}), "none")
        self.assertEqual(
            citation_class({"citations": 2, "nonmatching": 0}), "all_literal"
        )
        self.assertEqual(
            citation_class({"citations": 2, "nonmatching": 1}), "nonliteral"
        )
        with self.assertRaises(ValueError):
            citation_class({"citations": 0, "nonmatching": 1})

    def test_call_projection_keeps_usage_without_exposing_reply_or_error_bodies(self):
        call = {
            "status": "provider_error",
            "text": "VISIBLE",
            "reasoning": "PRIVATE",
            "error": "SECRET",
            "error_type": "PermissionError",
            "http_status": 403,
            "usage": {"input_tokens": 12, "output_tokens": 4},
        }
        result = project_call(
            call, identity="job", model="m", role="answer", phase="main"
        )
        self.assertEqual((result["input_tokens"], result["output_tokens"]), (12, 4))
        self.assertEqual(result["visible_chars"], 7)
        self.assertFalse({"text", "reasoning", "error", "messages"} & result.keys())
        unknown = project_call(
            {}, identity="job", model="m", role="answer", phase="main"
        )
        self.assertIsNone(unknown["output_tokens"])

    def test_visible_excerpt_retains_exact_offsets_and_hashes(self):
        value = "First statement. Second statement with Unicode − and π."
        result = prefix_excerpt(value, row="id", pointer="/result/defence", limit=27)
        self.assertEqual(value[result["start"] : result["end"]], result["text"])
        self.assertEqual(
            result["field_sha256"], hashlib.sha256(value.encode()).hexdigest()
        )
        self.assertEqual(
            result["text_sha256"], hashlib.sha256(result["text"].encode()).hexdigest()
        )
        self.assertTrue(result["truncated"])


if __name__ == "__main__":
    unittest.main()
