"""Download public benchmark material for cataloging, without executing it."""
import concurrent.futures
import json
import urllib.parse
import urllib.request
from pathlib import Path
from download_sources import CACHE, fetch

REVISIONS = json.loads((CACHE / "source_revisions.json").read_text())
TREES = json.loads((CACHE / "github_trees.json").read_text())

def raw(repo, path):
    rev = REVISIONS[repo]["sha"]
    return "https://raw.githubusercontent.com/" + repo + "/" + rev + "/" + urllib.parse.quote(path)

def run():
    items = []
    specs = {
        "finqa": ("czyssrs/FinQA", ["dataset/test.json", "LICENSE"]),
        "tatqa": ("NExTplusplus/TAT-QA", ["dataset_raw/tatqa_dataset_dev.json", "LICENSE"]),
        "contractnli": ("stanfordnlp/contract-nli", ["resources/contract-nli.zip", "LICENSE"]),
        "averitec": ("MichSchli/AVeriTeC", ["data/dev.json"]),
        "medagentbench": ("stanfordmlgroup/MedAgentBench", ["data/medagentbench/test_data_v2.json", "LICENSE"]),
        "writingbench": ("Tongyi-Zhiwen/WritingBench", ["benchmark_query/benchmark_all.jsonl", "LICENSE"]),
        "mathdial": ("eth-nlped/mathdial", ["data/test.jsonl", "README.md"]),
        "tau": ("sierra-research/tau2-bench", ["README.md", "LICENSE", "data/tau2/benchmarks/text.json", "data/tau2/domains/airline/tasks.json", "data/tau2/domains/retail/tasks.json", "data/tau2/domains/telecom/tasks.json", "data/tau2/domains/banking_knowledge/tasks.json"]),
    }
    for short, (repo, paths) in specs.items():
        for path in paths:
            local_name = path.replace("/", "_") if short == "tau" else Path(path).name
            items.append((short + "/" + local_name, raw(repo, path)))
    items.append(("scifact/data.tar.gz", "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"))
    items.append(("scifact/LICENSE.md", raw("allenai/scifact", "LICENSE.md")))
    for key, repo, expr in [
        ("tac", "TheAgentCompany/TheAgentCompany", lambda p: p.startswith("workspaces/tasks/") and p.endswith("/task.md") and "/example/" not in p),
        ("engdesign", "AGI4Engineering/EngDesign", lambda p: p.startswith("EngDesign-Open/") and p.endswith("/LLM_prompt.txt")),
    ]:
        for entry in TREES[key]["tree"]:
            path = entry["path"]
            if entry["type"] == "blob" and expr(path):
                items.append((key + "/" + path, raw(repo, path)))
        items.append((key + "/LICENSE", raw(repo, "LICENSE")))
    crm_rev = "8c055f5b45f15f7d996ee99277c4d0ea5049c6a8"
    for path in ["tasks_b2b.json", "tasks_b2c.json", "README.md"]:
        items.append(("crmarena/" + path, "https://huggingface.co/datasets/Salesforce/CRMArenaPro/resolve/" + crm_rev + "/" + path))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, items))
    (CACHE / "benchmark_download_manifest.json").write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    run()
