"""Fetch pinned public research inputs. No benchmark code is executed."""
import concurrent.futures
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "research_sources"
CACHE.mkdir(exist_ok=True)
HF_REVISIONS = {
    "Anthropic/EconomicIndex": "4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6",
    "openai/gdpval": "11e7900cdcac61bc4daf59e65feb238acda98fbf",
}

def fetch(item):
    name, url = item
    dest = CACHE / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Veracity-research-catalog/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            temp = dest.with_suffix(dest.suffix + ".part")
            with temp.open("wb") as out:
                while chunk := response.read(1024 * 1024):
                    out.write(chunk)
            temp.replace(dest)
    b = dest.read_bytes()
    record = {"name": name, "url": url, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    print(json.dumps(record), flush=True)
    return record

def hf(repo, path):
    return "https://huggingface.co/datasets/" + repo + "/resolve/" + HF_REVISIONS[repo] + "/" + path

if __name__ == "__main__":
    items = [
        ("aei_documentation.md", hf("Anthropic/EconomicIndex", "release_2026_06_26/data_documentation.md")),
        ("aei_readme.md", hf("Anthropic/EconomicIndex", "README.md")),
        ("aei_claude_ai.csv", hf("Anthropic/EconomicIndex", "release_2026_06_26/data/aei_claude_ai_2026-06-26.csv")),
        ("aei_api.csv", hf("Anthropic/EconomicIndex", "release_2026_06_26/data/aei_1p_api_2026-06-26.csv")),
        ("onet_task_statements.csv", hf("Anthropic/EconomicIndex", "release_2025_02_10/onet_task_statements.csv")),
        ("soc_structure.csv", hf("Anthropic/EconomicIndex", "release_2025_02_10/SOC_Structure.csv")),
        ("gdpval.parquet", hf("openai/gdpval", "data/train-00000-of-00001.parquet")),
        ("gdpval_readme.md", hf("openai/gdpval", "README.md")),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, items))
    (CACHE / "download_manifest.json").write_text(json.dumps(records, indent=2))
