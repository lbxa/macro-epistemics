"""Protect the pilot's observation unit and missing-data interpretation."""

import json
import tempfile
import unittest
from pathlib import Path

from epistemics_pilot import (
    ARTIFACT,
    SNAPSHOT,
    extract,
    load_snapshot,
    summarize_binary,
)


class ConditionalUncertaintyTests(unittest.TestCase):
    def test_five_successes_have_zero_variance_but_wide_uncertainty(self):
        s = summarize_binary([True] * 5)
        self.assertEqual((s["successes"], s["completed"], s["assigned"]), (5, 5, 5))
        self.assertEqual(s["variance"], 0)
        self.assertAlmostEqual(s["ci_low"], 0.4781762499)
        self.assertEqual(s["ci_high"], 1)

    def test_missing_response_is_not_a_false_belief(self):
        s = summarize_binary([True, True, True, True, None])
        self.assertEqual((s["successes"], s["completed"], s["assigned"]), (4, 4, 5))
        self.assertEqual(s["mean"], 1)
        self.assertLess(s["ci_low"], 0.4781762499)

    def test_unobserved_error_has_no_interval_or_rate(self):
        s = summarize_binary([])
        self.assertIsNone(s["mean"])
        self.assertIsNone(s["ci_low"])
        self.assertIsNone(s["variance"])

    def test_sample_variance_uses_n_minus_one(self):
        s = summarize_binary([True, False, False, False, False])
        self.assertAlmostEqual(s["mean"], 0.2)
        self.assertAlmostEqual(s["variance"], 0.2)

    def test_one_observation_has_no_sample_variance(self):
        self.assertIsNone(summarize_binary([True])["variance"])

    def test_portable_cohort_retains_missingness_and_unobserved_stratum(self):
        _, cells = load_snapshot(SNAPSHOT)
        self.assertEqual(sum(c.final_correct is not None for c in cells), 99)
        self.assertEqual(sum(c.jury_outcome is not None for c in cells), 95)
        self.assertFalse(
            any(c.model.endswith("kimi-k2.6") and not c.initial_correct for c in cells)
        )

    def test_duplicate_cell_is_rejected_even_when_row_count_matches(self):
        snapshot = json.loads(SNAPSHOT.read_text())
        snapshot["cells"][-1] = snapshot["cells"][0]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "snapshot.json"
            path.write_text(json.dumps(snapshot))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_snapshot(path)

    def test_excerpt_offsets_measure_exact_selected_characters(self):
        data, _ = load_snapshot(SNAPSHOT)
        for snippet in data["snippets"].values():
            self.assertEqual(len(snippet["text"]), snippet["end"] - snippet["start"])
        self.assertEqual(
            data["snippets"]["hypothesis"]["text"],
            "All Confidential Information shall be expressly identified by the Disclosing Party.",
        )

    def test_changed_archived_input_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "study.json").write_text("{}")
            register = root / "register.json"
            register.write_text(
                json.dumps(
                    {
                        "artifact": ARTIFACT,
                        "all_files_verified": True,
                        "file_sha256": {"study.json": "f" * 64},
                    }
                )
            )
            destination = root / "snapshot.json"
            with self.assertRaisesRegex(ValueError, "Archived file changed"):
                extract(root, register, destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
