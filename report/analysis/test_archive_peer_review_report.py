import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from archive_peer_review_report import (
    PARENT_ARTIFACT,
    PARENT_DIGEST,
    REPORT_ARTIFACT,
    REPORT_DIGEST,
    prepare_bundle,
    selected_files,
    verify_bundle,
)


class PeerReviewArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repository"
        self.destination = Path(self.directory.name) / "bundle"
        artifacts = {
            role: {
                "artifact": f"lbxa-corp/apart-epistemics-sprint/extension-{role}:v0",
                "digest": str(index) * 32,
                "run_id": f"run-{role}",
                "files": {"study.json": "1" * 64},
            }
            for index, role in enumerate(("revision", "judge", "execution_evidence"), 1)
        }
        artifacts["execution_evidence"]["files"] = {
            "evidence-register.json": "1" * 64,
            "executed-evidence.tar.gz": "2" * 64,
        }
        admission = {
            "schema": "peer-review-admission-v1",
            "status": "verified",
            "parent_artifact": PARENT_ARTIFACT,
            "parent_digest": PARENT_DIGEST,
            "artifacts": artifacts,
        }
        encoded_admission = json.dumps(admission)
        results = {
            "provenance": {
                "parent_artifact": PARENT_ARTIFACT,
                "parent_digest": PARENT_DIGEST,
                "admission_sha256": hashlib.sha256(
                    encoded_admission.encode()
                ).hexdigest(),
                "artifacts": artifacts,
                "revision_run": artifacts["revision"]["run_id"],
                "judge_run": artifacts["judge"]["run_id"],
            }
        }
        self.parents = {
            PARENT_ARTIFACT: PARENT_DIGEST,
            REPORT_ARTIFACT: REPORT_DIGEST,
            **{value["artifact"]: value["digest"] for value in artifacts.values()},
        }
        for name, content in {
            "report/epistemics/main.tex": "A reviewed paper",
            "report/epistemics/build/main.pdf": "PDF fixture",
            "report/epistemics/build/main.log": "Build output excluded",
            "report/epistemics/sections/results.tex": "Results",
            "report/epistemics/figures/result.pdf": "Figure",
            "report/data/sector-study.json": "{}",
            "report/data/peer-review-results.json": json.dumps(results),
            "report/data/private-calls.jsonl": "private response",
            "report/REPRODUCIBILITY.md": "Reproduction instructions",
            "report/analysis/sector_results.py": "# analysis",
            "tasks/catalog.json": '{"metadata": {"license_policy": "source-specific"}}',
            "harness/research/sector-expansion/peer-review/objection-protocol.md": "Protocol",
            "harness/research/sector-expansion/peer-review/admission.json": encoded_admission,
            "harness/research/sector-expansion/peer-review/adjudication/operator-only/join-key.json": "private key",
            "harness/research/sector-expansion/peer-review/adjudication/reviewer/stage-2/responses.json": "withheld responses",
            "website/README.md": "Unrelated",
            "media/movie.mp4": "Unrelated",
            ".env": "SECRET=private",
            "harness/results/recovery.sqlite": "Recovery",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def prepare(self, pages=17):
        with patch("archive_peer_review_report.pdf_page_count", return_value=pages):
            return prepare_bundle(
                self.root,
                self.destination,
                source_revision="b" * 40,
                parents=self.parents,
                main_pages=10,
            )

    def test_curates_report_and_excludes_private_and_unrelated_files(self):
        names = selected_files(self.root)
        self.assertIn("report/data/peer-review-results.json", names)
        self.assertIn("tasks/catalog.json", names)
        self.assertNotIn("report/data/private-calls.jsonl", names)
        self.assertFalse(any("operator-only" in name for name in names))
        self.assertFalse(any("stage-2" in name for name in names))
        self.assertFalse(any(name.startswith(("website/", "media/")) for name in names))
        manifest = self.prepare()
        self.assertEqual(manifest["pdf_pages"], 17)
        self.assertEqual(manifest["main_pages"], 10)
        self.assertFalse(manifest["public_release"])
        self.assertFalse(manifest["submission_authorized"])
        self.assertIn("main.pdf", manifest["files"])
        self.assertEqual(verify_bundle(self.destination), manifest)

    def test_refuses_to_replace_existing_bundle(self):
        original = self.prepare()
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(verify_bundle(self.destination), original)

    def test_accepts_execution_artifact_with_its_validated_helper_source(self):
        admission_path = (
            self.root / "harness/research/sector-expansion/peer-review/admission.json"
        )
        admission = json.loads(admission_path.read_text())
        admission["artifacts"]["execution_evidence"]["files"][
            "sector_revision_archive.py"
        ] = "a" * 64
        admission_path.write_text(json.dumps(admission))
        results_path = self.root / "report/data/peer-review-results.json"
        results = json.loads(results_path.read_text())
        results["provenance"]["artifacts"] = admission["artifacts"]
        results["provenance"]["admission_sha256"] = hashlib.sha256(
            admission_path.read_bytes()
        ).hexdigest()
        results_path.write_text(json.dumps(results))
        manifest = self.prepare()
        self.assertEqual(manifest["parents"], self.parents)
        verify_bundle(self.destination)

    def test_verification_rejects_tampering_and_extra_files(self):
        self.prepare()
        main = self.destination / "main.pdf"
        original = main.read_bytes()
        main.write_bytes(b"Changed after review")
        with self.assertRaisesRegex(ValueError, "hash"):
            verify_bundle(self.destination)
        main.write_bytes(original)
        (self.destination / ".env").write_text("not admitted")
        with self.assertRaisesRegex(ValueError, "file set"):
            verify_bundle(self.destination)

    def test_rejects_symlink_inside_allowlisted_source(self):
        path = self.root / "report/data/sector-study.json"
        path.unlink()
        path.symlink_to(self.root / ".env")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_completed_reviewer_form_and_preserves_no_partial_bundle(self):
        form = self.root / (
            "harness/research/sector-expansion/peer-review/adjudication/"
            "reviewer/stage-1/source-reviews.csv"
        )
        form.parent.mkdir(parents=True, exist_ok=True)
        form.write_text("review_task_id,reviewer_id,answer\nT001,Reviewer,42\n")
        with self.assertRaisesRegex(ValueError, "blank"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_invalid_pages_and_unversioned_parent(self):
        with self.assertRaisesRegex(ValueError, "page"):
            self.prepare(pages=7)
        with self.assertRaisesRegex(ValueError, "parent"):
            prepare_bundle(
                self.root,
                self.destination,
                source_revision="b" * 40,
                parents={"unversioned": "a" * 32},
                main_pages=1,
            )
        self.assertFalse(self.destination.exists())

    def test_manifest_is_hashed_and_does_not_mutate_parent_metadata(self):
        original = dict(self.parents)
        manifest = self.prepare()
        self.assertEqual(self.parents, original)
        registered = (self.destination / "manifest.sha256").read_text().split()[0]
        self.assertEqual(len(registered), 64)
        self.assertNotIn("manifest.json", manifest["files"])
        self.assertEqual(
            json.loads((self.destination / "manifest.json").read_text()), manifest
        )

    def test_verification_rejects_unmanifested_directory_symlink(self):
        self.prepare()
        (self.destination / "private").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            verify_bundle(self.destination)

    def test_known_environment_credential_cannot_enter_allowlisted_file(self):
        path = self.root / "report/REPRODUCIBILITY.md"
        path.write_text("known-private-credential-value")
        with (
            patch.dict(
                "os.environ", {"EXAMPLE_API_KEY": "known-private-credential-value"}
            ),
            self.assertRaisesRegex(ValueError, "Credential"),
        ):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_symlinked_source_directory_even_within_repository(self):
        original = self.root / "report/data"
        relocated = self.root / "report/private-data"
        original.rename(relocated)
        original.symlink_to(relocated, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_parent_digest_that_disagrees_with_admitted_results(self):
        self.parents = {name: "0" * 32 for name in self.parents}
        with self.assertRaisesRegex(ValueError, "parent"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_admission_changed_after_results_extraction(self):
        admission = (
            self.root / "harness/research/sector-expansion/peer-review/admission.json"
        )
        admission.write_text(admission.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "admission"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_verification_checks_parent_identity_beyond_file_hashes(self):
        manifest = self.prepare()
        manifest["parents"][PARENT_ARTIFACT] = "0" * 32
        encoded = json.dumps(manifest).encode()
        (self.destination / "manifest.json").write_bytes(encoded)
        (self.destination / "manifest.sha256").write_text(
            hashlib.sha256(encoded).hexdigest() + "  manifest.json\n"
        )
        with self.assertRaisesRegex(ValueError, "parent"):
            verify_bundle(self.destination)

    def test_rejects_misplaced_stage_two_json_in_stage_one_directory(self):
        path = self.root / (
            "harness/research/sector-expansion/peer-review/adjudication/"
            "reviewer/stage-1/responses.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"responses": [{"answer": "withheld"}]}')
        with self.assertRaisesRegex(ValueError, "Unexpected stage-1"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_renamed_response_csv_in_stage_one_directory(self):
        path = self.root / (
            "harness/research/sector-expansion/peer-review/adjudication/"
            "reviewer/stage-1/renamed-reviews.csv"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("review_response_id,answer\nR001,withheld\n")
        with self.assertRaisesRegex(ValueError, "Unexpected stage-1"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_rejects_optional_executed_evidence_with_wrong_hash(self):
        path = self.root / "report/data/peer-review-executed-evidence.tar.gz"
        path.write_bytes(b"Not the admitted receipt projection")
        with self.assertRaisesRegex(ValueError, "executed-evidence.*hash"):
            self.prepare()
        self.assertFalse(self.destination.exists())

    def test_includes_optional_executed_evidence_only_when_admitted_hash_matches(self):
        path = self.root / "report/data/peer-review-executed-evidence.tar.gz"
        path.write_bytes(b"Opaque admitted archive fixture")
        admission_path = self.root / (
            "harness/research/sector-expansion/peer-review/admission.json"
        )
        admission = json.loads(admission_path.read_text())
        admission["artifacts"]["execution_evidence"]["files"][
            "executed-evidence.tar.gz"
        ] = hashlib.sha256(path.read_bytes()).hexdigest()
        encoded = json.dumps(admission)
        admission_path.write_text(encoded)
        result_path = self.root / "report/data/peer-review-results.json"
        result = json.loads(result_path.read_text())
        result["provenance"]["artifacts"] = admission["artifacts"]
        result["provenance"]["admission_sha256"] = hashlib.sha256(
            encoded.encode()
        ).hexdigest()
        result_path.write_text(json.dumps(result))
        manifest = self.prepare()
        self.assertIn(
            "report/data/peer-review-executed-evidence.tar.gz", manifest["files"]
        )
        self.assertEqual(verify_bundle(self.destination), manifest)


if __name__ == "__main__":
    unittest.main()
