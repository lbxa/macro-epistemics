import copy
import json
import tempfile
import unittest
from pathlib import Path

from sector_excerpts import (
    ARTIFACT,
    DIGEST,
    ROOT,
    SNAPSHOT,
    extract,
    freeze_span,
    render,
)


class VisibleExcerptTests(unittest.TestCase):
    def test_selected_text_is_contiguous_with_original_offsets(self):
        value = "Earlier. Exact model explanation. Later."
        span = freeze_span(
            value,
            filename="branch.jsonl",
            row="example",
            pointer="/result/defence/parsed/explanation",
            start="Exact",
            end=" Later",
        )
        self.assertEqual(span["text"], value[span["start"] : span["end"]])
        self.assertEqual(span["text"], "Exact model explanation.")

    def test_altered_excerpt_is_rejected_before_publication(self):
        data = copy.deepcopy(json.loads(SNAPSHOT.read_text()))
        data["examples"][0]["snippets"]["initial"]["text"] += " invented"
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ValueError, "excerpt changed"),
        ):
            render(data, Path(directory))

    def test_four_real_panels_retain_black_box_environment(self):
        data = json.loads(SNAPSHOT.read_text())
        with tempfile.TemporaryDirectory() as directory:
            render(data, Path(directory))
            files = list(Path(directory).glob("sector-case-*.tex"))
            self.assertEqual(len(files), 4)
            for path in files:
                self.assertIn(r"\begin{modelexample}[unbreakable,", path.read_text())
                self.assertIn(r"\tcblower", path.read_text())

    def test_archived_file_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cases.json").write_text("changed")
            (root / "download-register.json").write_text(
                json.dumps(
                    {
                        "artifact": ARTIFACT,
                        "digest": DIGEST,
                        "files": {
                            "cases.json": {
                                "sha256": "0" * 64,
                                "wandb_digest": "invalid",
                            }
                        },
                    }
                )
            )
            with self.assertRaisesRegex(ValueError, "Changed archived input"):
                extract(root)

    def test_all_four_panels_are_in_the_main_results(self):
        results = (ROOT / "report/epistemics/sections/results.tex").read_text()
        for domain in ("education", "finance", "legal", "science"):
            self.assertIn(r"\input{tables/sector-case-" + domain + "}", results)


if __name__ == "__main__":
    unittest.main()
