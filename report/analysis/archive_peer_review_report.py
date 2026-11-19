"""Prepare or verify a curated local report bundle; never uploads or submits."""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PEER_REVIEW = "harness/research/sector-expansion/peer-review"
SOURCE_DATE_EPOCH = 1794821400
PARENT_ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128"
PARENT_DIGEST = "7d7230ca4d18fc07c1bb8e0009cdbc1d"
REPORT_ARTIFACT = "lbxa-corp/apart-epistemics-sprint/sector-report-da7e42f28ba54247:v2"
REPORT_DIGEST = "5a6c61802b1b27fbbd717e7de8802630"


def selected_files(root: Path) -> tuple[str, ...]:
    """Own the report-only inclusion policy; operator and stage-2 data stay out."""
    stage_one = root / PEER_REVIEW / "adjudication/reviewer/stage-1"
    if stage_one.exists() and any(
        path.name not in {"sources.json", "source-reviews.csv"}
        for path in stage_one.iterdir()
    ):
        raise ValueError(
            "Unexpected stage-1 adjudication file; refusing report packaging"
        )
    patterns = (
        "report/epistemics/*.tex",
        "report/epistemics/README.md",
        "report/epistemics/review.md",
        "report/epistemics/sections/*.tex",
        "report/epistemics/tables/*.tex",
        "report/epistemics/figures/*.pdf",
        "report/epistemics/figures/*.png",
        "report/epistemics/sector-*.csv",
        "report/epistemics/*statistics.json",
        "report/analysis/sector*.py",
        "report/analysis/test_sector*.py",
        "report/analysis/peer_review*.py",
        "report/analysis/test_peer_review*.py",
        "report/analysis/epistemics_pilot.py",
        "report/analysis/test_epistemics_pilot.py",
        "report/analysis/arithmetic_probe.py",
        "report/analysis/test_arithmetic_probe.py",
        "report/analysis/archive_peer_review_report.py",
        "report/analysis/test_archive_peer_review_report.py",
        "report/data/sector-study.json",
        "report/data/sector-initial.json",
        "report/data/sector-excerpts.json",
        "report/data/sector-diagnostic-inputs.json",
        "report/data/sector-call-metadata.jsonl",
        "report/data/arithmetic-diagnostic.json",
        "report/data/epistemics-pilot.json",
        "report/data/peer-review*.json",
        "report/data/peer-review-executed-evidence.tar.gz",
        "report/requirements.txt",
        "report/requirements.lock",
        "report/Makefile",
        "report/trace-panels.tex",
        "report/REPRODUCIBILITY.md",
        "harness/pyproject.toml",
        "harness/uv.lock",
        "harness/src/veracity_harness/sector_*.py",
        "harness/tests/test_sector_*.py",
        "docs/reporting/*.md",
        "tasks/source_notices/ATTRIBUTION.md",
        "tasks/catalog.json",
        "tasks/source_notices/finqa_LICENSE.txt",
        "tasks/source_notices/tatqa_LICENSE.txt",
        "tasks/source_notices/contractnli_LICENSE.txt",
        "tasks/source_notices/scifact_LICENSE.txt",
        "harness/research/sector-expansion/source-audit.json",
        "harness/research/sector-expansion/report-publication*.json",
        f"{PEER_REVIEW}/*.md",
        f"{PEER_REVIEW}/reproduction.json",
        f"{PEER_REVIEW}/admission.json",
        f"{PEER_REVIEW}/judge-proofs.json",
        f"{PEER_REVIEW}/judge-source-manifest.json",
        f"{PEER_REVIEW}/build_adjudication_packet.py",
        f"{PEER_REVIEW}/test_adjudication_packet.py",
        f"{PEER_REVIEW}/adjudication/manifest.json",
        f"{PEER_REVIEW}/adjudication/reviewer/stage-1/sources.json",
        f"{PEER_REVIEW}/adjudication/reviewer/stage-1/source-reviews.csv",
    )
    return tuple(
        sorted(
            {
                str(path.relative_to(root))
                for pattern in patterns
                for path in root.glob(pattern)
            }
        )
    )


def admitted_parents(root: Path) -> dict[str, str]:
    """Bind report lineage to the verified admission and its retained analysis."""
    admission_bytes = (root / PEER_REVIEW / "admission.json").read_bytes()
    admission = json.loads(admission_bytes)
    results = json.loads((root / "report/data/peer-review-results.json").read_text())
    provenance = results.get("provenance", {})
    if (
        admission.get("schema") != "peer-review-admission-v1"
        or admission.get("status") != "verified"
        or provenance.get("admission_sha256")
        != hashlib.sha256(admission_bytes).hexdigest()
    ):
        raise ValueError(
            "Extension admission is unverified or differs from the results"
        )
    if (
        admission.get("parent_artifact") != PARENT_ARTIFACT
        or admission.get("parent_digest") != PARENT_DIGEST
        or provenance.get("parent_artifact") != PARENT_ARTIFACT
        or provenance.get("parent_digest") != PARENT_DIGEST
    ):
        raise ValueError("Extension parent differs from the frozen v128 anchor")
    artifacts = admission.get("artifacts")
    if (
        not isinstance(artifacts, dict)
        or set(artifacts) != {"revision", "judge", "execution_evidence"}
        or provenance.get("artifacts") != artifacts
    ):
        raise ValueError("Extension artifact parents differ from the admitted results")
    parents = {PARENT_ARTIFACT: PARENT_DIGEST, REPORT_ARTIFACT: REPORT_DIGEST}
    for role, record in artifacts.items():
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("artifact"), str)
            or not re.fullmatch(
                r"lbxa-corp/apart-epistemics-sprint/[^\s:]+:v\d+", record["artifact"]
            )
            or not isinstance(record.get("digest"), str)
            or not re.fullmatch(r"[0-9a-f]{32}", record["digest"])
            or not isinstance(record.get("run_id"), str)
            or not re.fullmatch(r"[a-z0-9_-]+", record["run_id"])
            or not isinstance(record.get("files"), dict)
            or not record["files"]
            or any(
                not isinstance(name, str)
                or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                for name, digest in record["files"].items()
            )
        ):
            raise ValueError("Invalid admitted artifact parent: " + role)
        if role in {"revision", "judge"} and (
            provenance.get(role + "_run") != record["run_id"]
        ):
            raise ValueError("Results run differs from its admitted parent: " + role)
        if role == "execution_evidence" and not {
            "evidence-register.json",
            "executed-evidence.tar.gz",
        }.issubset(record["files"]):
            raise ValueError(
                "Executed-evidence parent must retain its archive and register"
            )
        parents[record["artifact"]] = record["digest"]
    if len(parents) != 5:
        raise ValueError("The report requires five distinct admitted artifact parents")
    projection = root / "report/data/peer-review-executed-evidence.tar.gz"
    if projection.exists():
        with projection.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if (
            digest
            != artifacts["execution_evidence"]["files"]["executed-evidence.tar.gz"]
        ):
            raise ValueError(
                "Optional executed-evidence archive hash differs from admission"
            )
    return parents


def pdf_page_count(path: Path) -> int:
    """Read page metadata with the installed Poppler parser."""
    result = subprocess.run(
        ["pdfinfo", str(path)], capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        key, _, value = line.partition(":")
        if key == "Pages":
            return int(value)
    raise ValueError("pdfinfo did not return a page count")


def prepare_bundle(
    root: Path,
    destination: Path,
    *,
    source_revision: str,
    parents: dict[str, str],
    main_pages: int,
) -> dict:
    """Publish a manifest last, refuse replacement and clean failed preparations."""
    root, destination = root.resolve(), destination.absolute()
    if destination.exists():
        raise FileExistsError("Refusing to replace an existing report bundle")
    if not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ValueError("A full source revision is required")
    if (
        not isinstance(parents, dict)
        or not parents
        or any(
            not isinstance(name, str)
            or not re.fullmatch(r"[^\s:]+/[^\s:]+/[^\s:]+:v\d+", name)
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{32}", digest)
            for name, digest in parents.items()
        )
    ):
        raise ValueError("Every parent needs a versioned artifact name and digest")
    if parents != admitted_parents(root):
        raise ValueError("Report parent metadata differs from the admitted results")
    pdf = root / "report/epistemics/build/main.pdf"
    pages = pdf_page_count(pdf)
    if type(main_pages) is not int or not 1 <= main_pages <= pages:
        raise ValueError(
            "Main-page count must be positive and within the PDF page count"
        )
    sources = {name: root / name for name in selected_files(root)}
    sources["main.pdf"] = pdf
    if "report/epistemics/main.tex" not in sources:
        raise ValueError("The active manuscript source is missing")
    credentials = tuple(
        value.encode()
        for name, value in os.environ.items()
        if re.search(r"KEY|TOKEN|SECRET|PASSWORD", name) and len(value) >= 12
    )
    destination.mkdir(parents=True, exist_ok=False)
    try:
        files = {}
        for name, source in sorted(sources.items()):
            if (
                source.is_symlink()
                or any(
                    parent.is_symlink()
                    for parent in source.parents
                    if parent.is_relative_to(root)
                )
                or not source.resolve().is_relative_to(root)
            ):
                raise ValueError("Refusing an allowlisted symlink: " + name)
            if not source.is_file():
                raise ValueError("Missing report file: " + name)
            raw = source.read_bytes()
            if any(secret in raw for secret in credentials):
                raise ValueError(
                    "Credential scan rejected an allowlisted file: " + name
                )
            if name.endswith("source-reviews.csv"):
                with source.open(newline="") as stream:
                    if any(
                        value
                        for row in csv.DictReader(stream)
                        for field, value in row.items()
                        if field != "review_task_id"
                    ):
                        raise ValueError(
                            "Only blank source-review forms may be bundled"
                        )
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            files[name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        manifest = {
            "schema": 1,
            "source_revision": source_revision,
            "source_worktree_modified": True,
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "archive_operation_only": True,
            "new_model_calls": 0,
            "public_release": False,
            "submission_authorized": False,
            "review_status": "independent-human-adjudication-pending",
            "distribution": "research-reproduction; not a blinded reviewer packet",
            "parents": dict(parents),
            "peer_review_snapshot_sha256": files[
                "report/data/peer-review-results.json"
            ]["sha256"],
            "pdf_pages": pages,
            "main_pages": main_pages,
            "files": files,
        }
        encoded = (json.dumps(manifest, indent=2) + "\n").encode()
        (destination / "manifest.json").write_bytes(encoded)
        (destination / "manifest.sha256").write_text(
            hashlib.sha256(encoded).hexdigest() + "  manifest.json\n"
        )
        verify_bundle(destination)
        return manifest
    except BaseException:
        shutil.rmtree(destination)
        raise


def verify_bundle(
    destination: Path, expected_manifest_sha256: str | None = None
) -> dict:
    """Check the exact file set and all hashes before remote admission."""
    paths = tuple(destination.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Refusing a bundled file or directory symlink")
    raw = (destination / "manifest.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    registered = (destination / "manifest.sha256").read_text().split()[0]
    if digest != registered or expected_manifest_sha256 not in (None, digest):
        raise ValueError("Report manifest hash differs from its registered value")
    manifest = json.loads(raw)
    if manifest.get("schema") != 1 or not isinstance(manifest.get("files"), dict):
        raise ValueError("Unsupported report manifest")
    actual = {str(path.relative_to(destination)) for path in paths if path.is_file()}
    expected = {*manifest["files"], "manifest.json", "manifest.sha256"}
    if actual != expected:
        raise ValueError("Report bundle file set changed after preparation")
    for name, record in manifest["files"].items():
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])
            or type(record.get("bytes")) is not int
            or record["bytes"] < 0
        ):
            raise ValueError("Invalid file hash record: " + name)
        path = destination / name
        if path.is_symlink() or not path.resolve().is_relative_to(
            destination.resolve()
        ):
            raise ValueError("Refusing a bundled symlink or escaped path")
        raw = path.read_bytes()
        if (
            hashlib.sha256(raw).hexdigest() != record["sha256"]
            or len(raw) != record["bytes"]
        ):
            raise ValueError("Report file hash changed: " + name)
    if manifest.get("parents") != admitted_parents(destination):
        raise ValueError("Report parent metadata differs from the bundled admission")
    if (
        manifest.get("peer_review_snapshot_sha256")
        != manifest["files"]["report/data/peer-review-results.json"]["sha256"]
    ):
        raise ValueError("Report result snapshot hash differs from the bundled results")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--metadata", type=Path, help="JSON with parents and main_pages"
    )
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--expected-manifest-sha256")
    args = parser.parse_args()
    if args.verify:
        manifest = verify_bundle(args.destination, args.expected_manifest_sha256)
    else:
        if args.metadata is None:
            parser.error("--metadata is required when preparing a bundle")
        metadata = json.loads(args.metadata.read_text())
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=args.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        manifest = prepare_bundle(
            args.root,
            args.destination,
            source_revision=revision,
            parents=metadata["parents"],
            main_pages=metadata["main_pages"],
        )
    print(
        json.dumps(
            {
                "pdf_pages": manifest["pdf_pages"],
                "payload_files": len(manifest["files"]),
            }
        )
    )


if __name__ == "__main__":
    main()
