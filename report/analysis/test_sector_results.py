import unittest

from sector_results import (
    audited_numeric_grade,
    cluster_summary,
    confidence_discrimination,
    forecast_scores,
    paired_arm_values,
    quotation_diagnostic,
    validate_baselines,
)


class SectorStatisticsTests(unittest.TestCase):
    def test_confidence_discrimination_respects_ties_and_missing_outcomes(self):
        self.assertEqual(
            confidence_discrimination([(True, 0.9), (False, 0.2)])["auc"], 1
        )
        self.assertEqual(
            confidence_discrimination([(True, 0.9), (False, 0.9)])["auc"], 0.5
        )
        self.assertIsNone(confidence_discrimination([(True, 0.9)])["auc"])
        self.assertEqual(
            confidence_discrimination([(None, 0.9), (True, None)])["correct"], 0
        )

    def test_literal_quote_check_does_not_become_an_inference_grade(self):
        source = "Revenue was 10\n million. Forecasts are uncertain."
        self.assertEqual(
            quotation_diagnostic(source, ["Revenue was 10 million."]),
            {"citations": 1, "nonmatching": 0},
        )
        self.assertEqual(
            quotation_diagnostic(source, ["Revenue was 100 million."]),
            {"citations": 1, "nonmatching": 1},
        )
        self.assertEqual(
            quotation_diagnostic(source, []), {"citations": 0, "nonmatching": 0}
        )

    def test_seed_clones_do_not_increase_source_group_count(self):
        values = [("a", "x", 0.0)] * 50 + [("b", "x", 1.0)] * 50
        result = cluster_summary(values, resamples=1000)
        self.assertEqual(result["groups"], 2)
        self.assertEqual(result["completed"], 100)
        self.assertEqual(result["mean"], 0.5)
        self.assertEqual((result["ci_low"], result["ci_high"]), (0, 1))

    def test_missing_response_is_excluded_but_retained_in_denominator(self):
        result = cluster_summary([("a", "x", 1.0), ("b", "x", None)])
        self.assertEqual(result["assigned"], 2)
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["mean"], 1)

    def test_empty_stratum_does_not_become_zero(self):
        result = cluster_summary([("a", "x", None)])
        self.assertIsNone(result["mean"])
        self.assertIsNone(result["ci_low"])

    def test_truth_and_jury_forecasts_have_different_targets(self):
        scores = forecast_scores(False, True, 0.9, 0.9)
        self.assertAlmostEqual(scores["source_brier"], 0.81)
        self.assertAlmostEqual(scores["jury_brier"], 0.01)

    def test_tampered_frozen_answer_hash_is_rejected(self):
        initials = [{"case_id": "a", "model": "m", "baseline_sha256": "original"}]
        branches = [{"case_id": "a", "model": "m", "baseline_sha256": "changed"}]
        with self.assertRaisesRegex(ValueError, "frozen"):
            validate_baselines(initials, branches)

    def test_source_audit_equivalent_units_and_reported_precision(self):
        unit = {
            "kind": "adapter_unit_handling",
            "expected_base": "70000000",
            "default_answer_scale": "million",
        }
        self.assertTrue(audited_numeric_grade(unit, "70", "million"))
        self.assertFalse(audited_numeric_grade(unit, "70", "thousand"))
        self.assertFalse(audited_numeric_grade(unit, "0", "billion"))
        mean = {
            "expected_numerator": "503000",
            "expected_denominator": "298",
            "default_answer_scale": "",
        }
        self.assertTrue(audited_numeric_grade(mean, "1688", ""))
        self.assertTrue(audited_numeric_grade(mean, "1687.92", ""))
        self.assertFalse(audited_numeric_grade(mean, "1689", ""))

    def test_percentage_audit_uses_a_fraction_as_base_quantity(self):
        audit = {
            "expected_numerator": "-8.6",
            "expected_denominator": "33.6",
            "default_answer_scale": "percent",
        }
        self.assertTrue(audited_numeric_grade(audit, "-25.6", "percent"))
        self.assertFalse(audited_numeric_grade(audit, "-0.26", "percent"))

    def test_arm_contrast_matches_seeds_before_averaging_sources(self):
        rows = [
            {"case_id": "a", "seed": 1, "arm": "review", "value": 0},
            {"case_id": "a", "seed": 1, "arm": "audit", "value": 1},
            {"case_id": "a", "seed": 2, "arm": "review", "value": 0},
            {"case_id": "a", "seed": 2, "arm": "audit", "value": None},
            {"case_id": "b", "seed": 1, "arm": "audit", "value": 1},
        ]
        self.assertEqual(
            paired_arm_values(rows, "review", "audit", lambda r: r["value"]), {"a": 1}
        )


if __name__ == "__main__":
    unittest.main()
