"""Upload an existing validated receipt bundle without regenerating its files."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv


def main():
    import wandb

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dotenv", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(args.dotenv, override=False)
    register_path = args.source / "evidence-register.json"
    register = json.loads(register_path.read_text())
    if register["status"] != "validated" or register["run_id"] != "6cffaa22ee0c470a":
        raise ValueError("Upload requires the validated numerical replication register")
    names = ("executed-evidence.tar.gz", "evidence-register.json", "sector_revision_archive.py")
    files = {}
    needles = tuple(
        os.getenv(key, "").encode()
        for key in (
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_API_TOKEN",
            "WANDB_API_KEY",
        )
        if os.getenv(key)
    )
    for name in names:
        data = (args.source / name).read_bytes()
        if any(needle in data for needle in needles):
            raise ValueError("Credential material in a proposed admission upload")
        files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        if name != "evidence-register.json" and files[name] != register["bundle_files"][name]:
            raise ValueError("Validated bundle bytes changed before upload")
    intent_path = args.source / "upload-intent.json"
    if intent_path.exists():
        intent = json.loads(intent_path.read_text())
        if intent["files"] != files:
            raise ValueError("An upload retry cannot change its validated files")
    else:
        intent = {"producer_run_id": uuid4().hex[:16], "files": files}
        intent_path.write_text(json.dumps(intent, indent=2) + "\n")
    source_artifact = "lbxa-corp/apart-epistemics-sprint/sector-study-6cffaa22ee0c470a:v20"
    config = {key: value for key, value in register.items() if key != "files"}
    config.update(source_artifact=source_artifact, uploaded_file_sha256=files)
    with wandb.init(
        entity="lbxa-corp",
        project="apart-epistemics-sprint",
        id=intent["producer_run_id"],
        resume="allow",
        job_type="sector-objection-evidence-admission",
        config=config,
        settings=wandb.Settings(base_url=os.getenv("WANDB_BASE_URL") or "https://api.wandb.ai"),
    ) as run:
        parent = run.use_artifact(source_artifact)
        if parent.digest != "179811a3578576b63d2d3c313f08a5e9":
            raise ValueError("The immutable source artifact digest changed")
        artifact = wandb.Artifact(
            "sector-objection-executed-evidence-" + register["run_id"],
            type="sector-executed-evidence",
            metadata=config,
        )
        for name in names:
            artifact.add_file(str(args.source / name), name=name)
        logged = run.log_artifact(artifact)
        logged.wait()
        tracking = {
            "producer_run_id": run.id,
            "url": run.url,
            "artifact": "lbxa-corp/apart-epistemics-sprint/" + logged.name,
            "digest": logged.digest,
            "source_artifact": source_artifact,
            "source_digest": parent.digest,
            "files": files,
        }
        (args.source / "tracking.json").write_text(json.dumps(tracking, indent=2) + "\n")
        run.summary.update({"status": "validated", "counts": register["counts"]})
    print(json.dumps(tracking))


if __name__ == "__main__":
    main()
