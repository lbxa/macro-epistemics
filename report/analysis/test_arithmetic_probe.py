import unittest

from arithmetic_probe import block_summary, standalone_call_correct


class ArithmeticDiagnosticTests(unittest.TestCase):
    def test_judge_support_is_not_the_correct_arithmetic_target(self):
        self.assertFalse(
            standalone_call_correct("defended", {"verdict": "CREATOR_SUPPORTED"})
        )
        self.assertTrue(
            standalone_call_correct("defended", {"verdict": "CHALLENGER_SUPPORTED"})
        )

    def test_calculation_and_author_use_their_declared_units(self):
        self.assertTrue(
            standalone_call_correct("calculate", {"answer": "117624.84", "scale": ""})
        )
        self.assertFalse(
            standalone_call_correct("calculate", {"answer": "117628.84", "scale": ""})
        )
        self.assertTrue(
            standalone_call_correct(
                "author_checked", {"answer": "117624.84", "scale": "thousand"}
            )
        )
        self.assertTrue(
            standalone_call_correct(
                "author_checked", {"answer": "117624.84", "scale": ""}
            )
        )

    def test_one_valid_call_does_not_create_a_three_call_majority(self):
        rows = [{"model": "m", "condition": "defended", "seed": 101, "correct": True}]
        block = block_summary(rows)[0]
        self.assertEqual(block["valid"], 1)
        self.assertEqual(block["accuracy"], 1)
        self.assertIsNone(block["majority_correct"])

    def test_missing_calls_are_not_false_judgments(self):
        rows = [
            {"model": "m", "condition": "defended", "seed": 101, "correct": x}
            for x in (True, True, None)
        ]
        block = block_summary(rows)[0]
        self.assertEqual(block["valid"], 2)
        self.assertTrue(block["majority_correct"])


if __name__ == "__main__":
    unittest.main()
