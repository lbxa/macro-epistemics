"""Package the built task bank with its authored documentation and uv project."""

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "veracity_task_database"
summary = json.loads((OUT / "summary.json").read_text())

for name in (
    "README.md",
    "example_queries.sql",
    "EXPERIMENT_PROTOCOL.md",
    "source_notices/ATTRIBUTION.md",
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    ".gitignore",
    "package_database.py",
):
    destination = OUT / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, destination)
support = OUT / "source_metadata"
support.mkdir(exist_ok=True)
shutil.copyfile(
    ROOT / "source_metadata" / "imported_bundle_checksums.json",
    support / "imported_bundle_checksums.json",
)

# Exclude the manifest itself, including when packaging an existing output again.
manifest_path = OUT / "bundle_checksums.json"
files = sorted(
    p
    for p in OUT.rglob("*")
    if p.is_file()
    and not {".venv", "__pycache__", "research_sources", "outputs"}.intersection(
        p.relative_to(OUT).parts
    )
    and p != manifest_path
)
manifest = {
    str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
}
manifest_path.write_text(json.dumps(manifest, indent=2))
archive = ROOT / "outputs" / "Veracity_Task_Database.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
    for path in [*files, manifest_path]:
        bundle.write(
            path, arcname="Veracity_Task_Database/" + str(path.relative_to(OUT))
        )
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
print(
    json.dumps(
        {
            "archive": str(archive),
            "bytes": archive.stat().st_size,
            "files": len(files) + 1,
            "tasks": summary["tasks"],
            "candidate_inputs": summary["source_ready_candidates"],
        },
        indent=2,
    )
)
