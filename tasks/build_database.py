"""Build a source-linked occupational task catalog using Python's standard library.

Only data are parsed. Downloaded programs, evaluators and models are never run.
"""
import csv
import hashlib
import json
import math
import re
import shutil
import sqlite3
import tarfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

from curation import BENCHMARKS, CATEGORY_PLANS, CONDITIONS

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "research_sources"
OUT = ROOT / "outputs" / "veracity_task_database"
OUT.mkdir(parents=True, exist_ok=True)
REV = json.loads((CACHE / "source_revisions.json").read_text())
HF_AEI = "4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6"
HF_GDP = "11e7900cdcac61bc4daf59e65feb238acda98fbf"
HF_CRM = "8c055f5b45f15f7d996ee99277c4d0ea5049c6a8"
DBPATH = OUT / "veracity_tasks.sqlite"
if DBPATH.exists():
    DBPATH.unlink()
db = sqlite3.connect(DBPATH)
db.execute("PRAGMA foreign_keys=ON")
db.executescript("""
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE categories (
 code TEXT PRIMARY KEY, name TEXT NOT NULL, proposed_phase TEXT NOT NULL,
 proposed_task_families TEXT NOT NULL, coverage_note TEXT NOT NULL,
 taxonomy_source TEXT NOT NULL);
CREATE TABLE economic_metrics (
 source TEXT NOT NULL, date_start TEXT NOT NULL, date_end TEXT NOT NULL,
 geo_id TEXT NOT NULL, category_name TEXT NOT NULL, hierarchy_level INTEGER NOT NULL,
 node_id TEXT NOT NULL, node_name TEXT NOT NULL, metric_id TEXT NOT NULL, value REAL NOT NULL,
 PRIMARY KEY(source,date_start,date_end,geo_id,category_name,hierarchy_level,node_id,metric_id));
CREATE TABLE occupations (
 onet_soc TEXT PRIMARY KEY, title TEXT NOT NULL, category_code TEXT REFERENCES categories(code));
CREATE TABLE occupational_tasks (
 onet_soc TEXT REFERENCES occupations(onet_soc), source_task_id TEXT NOT NULL,
 task TEXT NOT NULL, task_type TEXT, source_date TEXT, source_kind TEXT,
 PRIMARY KEY(onet_soc,source_task_id));
CREATE TABLE benchmarks (
 benchmark_id TEXT PRIMARY KEY, name TEXT NOT NULL, source_url TEXT NOT NULL,
 dataset_url TEXT NOT NULL, license TEXT NOT NULL, task_origin TEXT NOT NULL,
 grading TEXT NOT NULL, typical_tasks TEXT NOT NULL, veracity_adaptation TEXT NOT NULL,
 prerequisites TEXT NOT NULL, refresh_recipe TEXT NOT NULL, catalog_status TEXT NOT NULL,
 checked_on TEXT NOT NULL);
CREATE TABLE benchmark_categories (
 benchmark_id TEXT REFERENCES benchmarks(benchmark_id), category_code TEXT REFERENCES categories(code),
 mapping_basis TEXT NOT NULL, PRIMARY KEY(benchmark_id,category_code));
CREATE TABLE evidence_bundles (
 evidence_id TEXT PRIMARY KEY, content TEXT NOT NULL, source_urls_json TEXT NOT NULL,
 sha256 TEXT NOT NULL, evidence_status TEXT NOT NULL);
CREATE TABLE tasks (
 task_id TEXT PRIMARY KEY, benchmark_id TEXT NOT NULL REFERENCES benchmarks(benchmark_id),
 source_record_id TEXT NOT NULL, group_id TEXT NOT NULL, title TEXT NOT NULL,
 prompt TEXT, evidence_id TEXT REFERENCES evidence_bundles(evidence_id),
 task_family TEXT NOT NULL, language TEXT NOT NULL, input_status TEXT NOT NULL,
 reference_type TEXT NOT NULL, oracle_verification TEXT NOT NULL,
 adaptation_status TEXT NOT NULL, source_url TEXT NOT NULL, source_revision TEXT NOT NULL,
 content_sha256 TEXT NOT NULL, notes TEXT NOT NULL,
 UNIQUE(benchmark_id,source_record_id));
CREATE TABLE task_categories (
 task_id TEXT REFERENCES tasks(task_id), category_code TEXT REFERENCES categories(code),
 mapping_basis TEXT NOT NULL, PRIMARY KEY(task_id,category_code));
CREATE TABLE evaluator_references (
 task_id TEXT PRIMARY KEY REFERENCES tasks(task_id), reference_json TEXT NOT NULL,
 reference_sha256 TEXT NOT NULL, reference_status TEXT NOT NULL);
CREATE TABLE conditions (
 condition_id TEXT PRIMARY KEY, name TEXT NOT NULL, intervention TEXT NOT NULL, estimand TEXT NOT NULL);
CREATE TABLE source_files (
 name TEXT PRIMARY KEY, url TEXT NOT NULL, sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL);
CREATE TABLE quality_findings (
 finding_id TEXT PRIMARY KEY, scope TEXT NOT NULL, observation TEXT NOT NULL,
 consequence TEXT NOT NULL, handling TEXT NOT NULL, source_url TEXT NOT NULL);
CREATE TABLE experiments (
 experiment_id TEXT PRIMARY KEY, protocol_version TEXT NOT NULL, question_id TEXT NOT NULL,
 task_id TEXT NOT NULL REFERENCES tasks(task_id), condition_id TEXT NOT NULL REFERENCES conditions(condition_id),
 session_id TEXT NOT NULL, actor_model TEXT NOT NULL, model_version TEXT NOT NULL,
 source_bundle_sha256 TEXT NOT NULL, assigned_at TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE observations (
 observation_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 claim_id TEXT NOT NULL, stage TEXT NOT NULL, text TEXT,
 p_claim_true REAL CHECK(p_claim_true BETWEEN 0 AND 1),
 p_jury_upholds REAL CHECK(p_jury_upholds BETWEEN 0 AND 1),
 stance TEXT, external_correctness TEXT, evidence_access_json TEXT, retained_log_sha256 TEXT);
CREATE VIEW latest_claude_category_usage AS
 SELECT node_id AS category_code,node_name,date_start,date_end,value AS usage_pct
 FROM economic_metrics
 WHERE source='claude_ai' AND geo_id='GLOBAL' AND category_name='soc_occupation'
 AND hierarchy_level=1 AND metric_id='pct' AND date_start='2026-05-01';
CREATE VIEW category_coverage AS
 SELECT c.code,c.name,c.proposed_phase,u.usage_pct,
 (SELECT count(*) FROM occupations o WHERE o.category_code=c.code) AS occupation_count,
 (SELECT count(*) FROM occupational_tasks t JOIN occupations o USING(onet_soc) WHERE o.category_code=c.code) AS occupational_task_count,
 (SELECT count(*) FROM benchmark_categories b WHERE b.category_code=c.code) AS mapped_benchmark_count,
 (SELECT count(*) FROM task_categories t WHERE t.category_code=c.code) AS indexed_task_count,
 c.coverage_note
 FROM categories c LEFT JOIN latest_claude_category_usage u ON u.category_code=c.code;
CREATE VIEW task_catalog AS
 SELECT t.*,b.name AS benchmark_name,b.grading,b.license,
 (SELECT group_concat(c.name,'; ') FROM task_categories tc JOIN categories c ON c.code=tc.category_code WHERE tc.task_id=t.task_id) AS economic_categories
 FROM tasks t JOIN benchmarks b USING(benchmark_id);
CREATE VIEW source_ready_candidates AS
 SELECT * FROM task_catalog WHERE input_status='self_contained' AND prompt IS NOT NULL
 AND oracle_verification NOT LIKE 'reference_disagreement%';
CREATE VIEW participant_input_view AS
 SELECT t.task_id,t.prompt,e.content AS materials
 FROM tasks t LEFT JOIN evidence_bundles e USING(evidence_id)
 WHERE t.input_status='self_contained' AND t.prompt IS NOT NULL
 AND t.oracle_verification NOT LIKE 'reference_disagreement%';
CREATE INDEX tasks_benchmark ON tasks(benchmark_id);
CREATE INDEX tasks_group ON tasks(benchmark_id,group_id);
CREATE INDEX economic_lookup ON economic_metrics(category_name,geo_id,date_start,metric_id,hierarchy_level);
""")

def J(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def H(x):
    return hashlib.sha256(x.encode() if isinstance(x,str) else x).hexdigest()

def rows(name):
    return list(csv.DictReader((CACHE / name).open(newline="")))

def jsonfile(name):
    return json.loads((CACHE / name).read_text())

def jsonlines(name):
    return [json.loads(s) for s in (CACHE / name).read_text().splitlines() if s.strip()]

def gh(repo,path):
    return "https://github.com/"+repo+"/blob/"+REV[repo]["sha"]+"/"+quote(path)

def sample(items, key, n):
    return sorted(items,key=lambda x:H(str(key(x))))[:n]

def balanced(items,label,key,each):
    groups=defaultdict(list)
    for x in items:groups[str(label(x))].append(x)
    return [x for lab in sorted(groups) for x in sample(groups[lab],key,each)]

def tabletext(table):
    return "\n".join(" | ".join(str(c) for c in row) for row in table)

def add(bench,sid,group,title,prompt,context,cats,family,reference,ref_type,
        status="self_contained",urls=None,revision=None,notes="",language="en",
        oracle="source_provided_not_independently_adjudicated"):
    task_id=bench+":"+str(sid)
    context=context or ""
    ev_id=H(J({"text":context,"urls":urls or []}))
    db.execute("INSERT OR IGNORE INTO evidence_bundles VALUES(?,?,?,?,?)",
      (ev_id,context,J(urls or []),H(context),status))
    digest=H(J({"prompt":prompt,"context":context}))
    db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      (task_id,bench,str(sid),str(group),title,prompt,ev_id,family,language,status,ref_type,oracle,
       "not_integrated_with_Veracity",(urls or [next(b["dataset_url"] for b in BENCHMARKS if b["benchmark_id"]==bench)])[0],
       revision or "snapshot_2026-11-14",digest,notes))
    for c in cats:
        db.execute("INSERT INTO task_categories VALUES(?,?,?)",(task_id,c,"Researcher occupational relevance mapping; not an Anthropic-provided mapping"))
    if reference is not None:
        s=J(reference)
        db.execute("INSERT INTO evaluator_references VALUES(?,?,?,?)",(task_id,s,H(s),oracle))
    return task_id

# Authoritative categories and metrics. Retain source, geography and month separately.
global_rows=[]
latest_names={}
for short,filename in [("claude_ai","aei_claude_ai.csv"),("1p_api","aei_api.csv")]:
    with (CACHE/filename).open(newline="") as f:
        for r in csv.DictReader(f):
            if r["geo_id"] not in {"GLOBAL","USA"}:continue
            if r["geo_level"] not in {"global","country"}:continue
            cat,level,metric=r["category_name"],int(r["hierarchy_level"]),r["metric_id"]
            keep=(cat=="overall" or
                  (cat=="soc_occupation" and (level==1 or metric=="pct")) or
                  (cat=="onet" and (level==3 or (level==0 and metric=="pct"))) or
                  (cat=="request" and (level==2 or (level==1 and metric=="pct"))))
            if not keep:continue
            db.execute("INSERT INTO economic_metrics VALUES(?,?,?,?,?,?,?,?,?,?)",(
                short,r["date_start"],r["date_end"],r["geo_id"],r["category_name"],int(r["hierarchy_level"]),
                r["node_external_id"],r["node_name"],r["metric_id"],float(r["value"])))
            if short=="claude_ai" and r["geo_id"]=="GLOBAL" and r["date_start"]=="2026-05-01" and r["category_name"]=="soc_occupation" and r["hierarchy_level"]=="1" and r["metric_id"]=="pct":
                latest_names[r["node_external_id"]]=r["node_name"]
for code,name in sorted(latest_names.items()):
    phase,families,note=CATEGORY_PLANS[code]
    db.execute("INSERT INTO categories VALUES(?,?,?,?,?,?)",(code,name,phase,families,note,
       "Anthropic Economic Index 2026-06-26 release, soc_occupation hierarchy level 1"))

occupation_rows=rows("onet_task_statements.csv")
for r in occupation_rows:
    code=r["O*NET-SOC Code"];major=code[:2]
    db.execute("INSERT OR IGNORE INTO occupations VALUES(?,?,?)",(code,r["Title"],major if major in latest_names else None))
    db.execute("INSERT INTO occupational_tasks VALUES(?,?,?,?,?,?)",(code,r["Task ID"],r["Task"],r["Task Type"],r["Date"],r["Domain Source"]))

for b in BENCHMARKS:
    fields=[k for k in b if k!="category_codes"]
    db.execute("INSERT INTO benchmarks ("+",".join(fields)+") VALUES("+",".join("?" for _ in fields)+")",tuple(b[k] for k in fields))
    for c in b["category_codes"]:
        db.execute("INSERT INTO benchmark_categories VALUES(?,?,?)",(b["benchmark_id"],c,"Researcher occupational relevance mapping; benchmark is not necessarily validated for every mapped occupation"))
db.executemany("INSERT INTO conditions VALUES(?,?,?,?)",CONDITIONS)

# Financial sources. Full context is independent of author-supplied answer fields.
for r in sample(jsonfile("finqa/test.json"),lambda x:x["id"],180):
    qa=r["qa"]
    text="\n\n".join(["\n".join(r.get("pre_text",[])),tabletext(r.get("table",[])),"\n".join(r.get("post_text",[]))])
    add("finqa",r["id"],r["id"].split("/page_")[0],qa["question"],qa["question"],text,["13"],"financial_report_reasoning",
      {k:qa.get(k) for k in ["answer","exe_ans","program","gold_inds"]},"numeric_with_program",
      urls=[gh("czyssrs/FinQA","dataset/test.json")],revision=REV["czyssrs/FinQA"]["sha"],
      notes="Deterministic hash sample of public test. Table serialization uses all rows uniformly; no gold_inds/model_input/tfidftopn exposed.")

tat=[]
for block in jsonfile("tatqa/tatqa_dataset_dev.json"):
    for q in block["questions"]:tat.append((block,q))
for block,q in balanced(tat,lambda x:x[1]["answer_type"],lambda x:x[1]["uid"],45):
    context=tabletext(block["table"]["table"])+"\n\n"+"\n\n".join(p["text"] for p in block["paragraphs"])
    add("tatqa",q["uid"],block["table"]["uid"],q["question"],q["question"],context,["13"],"financial_table_and_text",
      {k:q.get(k) for k in ["answer","answer_type","scale","derivation","answer_from","rel_paragraphs"]},"typed_answer_with_scale",
      urls=[gh("NExTplusplus/TAT-QA","dataset_raw/tatqa_dataset_dev.json")],revision=REV["NExTplusplus/TAT-QA"]["sha"],
      notes="Up to 45 per answer type, selected by stable question-ID hash. Cluster inference and splits by table/report.")

with zipfile.ZipFile(CACHE/"contractnli/contract-nli.zip") as z:
    cn=json.loads(z.read("contract-nli/test.json"))
candidates=[]
for doc in cn["documents"]:
    for lab,ann in doc["annotation_sets"][0]["annotations"].items():candidates.append((doc,lab,ann))
for doc,lab,ann in balanced(candidates,lambda x:x[2]["choice"],lambda x:str(x[0]["id"])+x[1],60):
    prop=cn["labels"][lab]["hypothesis"]
    spans=[doc["spans"][i] for i in ann["spans"]]
    assert all(0<=a<=b<=len(doc["text"]) for a,b in spans)
    add("contractnli",str(doc["id"])+"/"+lab,doc["id"],prop,
      "Assess whether the following proposition is entailed by, contradicted by, or not mentioned in the supplied agreement. Explain the relevant wording.\n\n"+prop,
      doc["text"],["23"],"contractual_entailment",{"label":ann["choice"],"evidence_character_spans":spans,"source_url":doc.get("url")},"document_support_three_way",
      urls=["https://stanfordnlp.github.io/contract-nli/",doc.get("url") or "https://stanfordnlp.github.io/contract-nli/"],revision=REV["stanfordnlp/contract-nli"]["sha"],
      notes="60 per label from the test split. NotMentioned is not factual falsity; preserve it as an evaluator uncertainty outcome.")

with tarfile.open(CACHE/"scifact/data.tar.gz") as t:
    claims=[json.loads(s) for s in t.extractfile("data/claims_dev.jsonl")]
    corpus={int(r["doc_id"]):r for r in (json.loads(s) for s in t.extractfile("data/corpus.jsonl"))}
def sci_label(r):
    labs={e["label"] for es in r["evidence"].values() for e in es}
    return next(iter(labs)) if len(labs)==1 else ("NO_ANNOTATED_SUPPORT" if not labs else "MIXED")
parents={}
def root(i):
    parents.setdefault(i,i)
    while parents[i]!=i:
        parents[i]=parents[parents[i]]
        i=parents[i]
    return i
for r in claims:
    ids=sorted(set(map(int,r.get("cited_doc_ids",[])))|set(map(int,r["evidence"])))
    for i in ids[1:]:parents[root(i)]=root(ids[0])
for r in balanced(claims,sci_label,lambda x:x["id"],60):
    docids=set(map(int,r.get("cited_doc_ids",[]))) | set(map(int,r["evidence"]))
    docs=[corpus[i] for i in sorted(docids)]
    context="\n\n".join("Document "+str(d["doc_id"])+"\n"+d["title"]+"\n"+"\n".join(str(i)+". "+s for i,s in enumerate(d["abstract"])) for d in docs)
    group="paper-component-"+str(root(min(docids))) if docids else "claim-"+str(r["id"])
    add("scifact",r["id"],group,r["claim"],
      "Assess whether the supplied abstracts support, contradict, or leave unresolved the following claim. Identify relevant evidence.\n\n"+r["claim"],
      context,["19"],"scientific_evidence_assessment",{"label":sci_label(r),"evidence":r["evidence"],"cited_doc_ids":sorted(docids)},"corpus_support_label",
      urls=["https://github.com/allenai/scifact"],revision="data.tar.gz sha256 "+H((CACHE/"scifact/data.tar.gz").read_bytes()),
      notes="Up to 60 per reference label. Corpus-support labels are scoped to the supplied abstracts. Source artifact hash pins mutable latest download.")

averitec_rows=[dict(r,_source_row=i) for i,r in enumerate(jsonfile("averitec/dev.json"))]
for r in balanced(averitec_rows,lambda x:x["label"],lambda x:str(x["_source_row"])+x["claim"],45):
    source_cards=[]
    for q in r.get("questions",[]):
        source_cards.append({"question":q["question"],"answers":q.get("answers",[])})
    add("averitec","dev/"+str(r["_source_row"]),r.get("fact_checking_article") or H(r["claim"]),r["claim"],
      "Assess the following public claim against the supplied research evidence and its dates.\n\n"+r["claim"],J(source_cards),["27"],"public_claim_fact_check",
      {"label":r["label"],"justification":r.get("justification"),"claim_date":r.get("claim_date"),"fact_checking_article":r.get("fact_checking_article")},"dated_claim_verdict",
      status="evidence_cards_need_primary_source_snapshot",urls=[gh("MichSchli/AVeriTeC","data/dev.json")],revision=REV["MichSchli/AVeriTeC"]["sha"],
      notes="Up to 45 per label. Dataset evidence answers are annotations. Original primary-page bytes were not retrieved.")

mathdial_rows=[dict(r,_source_row=i) for i,r in enumerate(jsonlines("mathdial/test.jsonl"))]
for r in sample(mathdial_rows,lambda x:str(x["qid"])+str(x.get("scenario"))+str(x["_source_row"]),120):
    prompt="A student has submitted the following working. Review it and give feedback that helps the student make progress.\n\nProblem\n"+r["question"]+"\n\nStudent working\n"+r["student_incorrect_solution"]
    add("mathdial",str(r["qid"])+"/"+str(r.get("scenario"))+"/row"+str(r["_source_row"]),r["qid"],"Feedback on student working",prompt,r.get("student_profile", ""),["25"],"tutoring_feedback",
      {"problem_solution":r["ground_truth"],"teacher_described_confusion":r.get("teacher_described_confusion"),"example_teacher_dialogue":r.get("conversation")},"reference_solution_not_unique_teacher_reply",
      urls=[gh("eth-nlped/mathdial","data/test.jsonl")],revision=REV["eth-nlped/mathdial"]["sha"],
      notes="Stable hash sample of test dialogues. Original teacher dialogue and confusion labels are evaluator-only. Problem correctness and pedagogy are separate.")

for r in sample(jsonfile("medagentbench/test_data_v2.json"),lambda x:x["id"],100):
    add("medagentbench",r["id"],r.get("eval_MRN") or r["id"],r["instruction"],r["instruction"],r.get("context", ""),["29"],"clinical_EHR_workflow",
      {k:v for k,v in r.items() if k not in {"instruction","context"}},"EHR_reference_solution",
      status="requires_FHIR_environment",urls=[gh("stanfordmlgroup/MedAgentBench","data/medagentbench/test_data_v2.json")],revision=REV["stanfordmlgroup/MedAgentBench"]["sha"],
      notes="Task records only. No FHIR server was started and no chart data were downloaded.")

for f in sorted((CACHE/"tac/workspaces/tasks").glob("*/task.md")):
    name=f.parent.name
    if name=="example":continue
    prefix=name.split("-",1)[0]
    cats={"admin":["43"],"finance":["13"],"hr":["13"],"ds":["15"],"sde":["15"],"pm":["11"],"qa":["15"],"research":["15"],"ml":["15"]}.get(prefix,["11"])
    prompt=f.read_text()
    add("tac",name,name,name.replace("-"," "),prompt,"",cats,"simulated_workplace_"+prefix,None,"external_workplace_evaluator",
      status="requires_workplace_environment",urls=[gh("TheAgentCompany/TheAgentCompany","workspaces/tasks/"+name+"/task.md")],revision=REV["TheAgentCompany/TheAgentCompany"]["sha"],
      notes="All non-example task.md files at the pinned commit. Task assets, services and encrypted evaluators are not bundled.")

for f in sorted((CACHE/"engdesign/EngDesign-Open").glob("*/LLM_prompt.txt")):
    name=f.parent.name
    add("engdesign",name,name,"Engineering design "+name,f.read_text(),"",["17"],"engineering_design",None,"external_simulation_evaluator",
      status="requires_simulator_and_assets",urls=[gh("AGI4Engineering/EngDesign","EngDesign-Open/"+name+"/LLM_prompt.txt")],revision=REV["AGI4Engineering/EngDesign"]["sha"],
      notes="Complete 67-prompt open subset. Fetch associated output schema, evaluator and assets; no simulation was executed.")

# tau records contain user-simulator instructions. Keep that distinction explicit.
for domain in ["airline","retail","telecom","banking_knowledge"]:
    collection=jsonfile("tau/data_tau2_domains_"+domain+"_tasks.json")
    for r in sample(collection,lambda x:x["id"],50):
        scenario=r.get("user_scenario",{})
        instr=scenario.get("instructions",{})
        if isinstance(instr,dict):
            prompt=instr.get("reason_for_call","")
            context=instr.get("known_info","") or ""
            # The original user-only instructions remain a private fixture.
        else:
            prompt=None
            context=""
        if r.get("ticket"):prompt=r["ticket"]
        add("tau",domain+"/"+str(r["id"]),domain+"/"+str(r["id"]),domain+" customer-service case",prompt,context,
          ["43"] if domain!="banking_knowledge" else ["43","13"],"customer_service_"+domain,
          {"evaluation_criteria":r.get("evaluation_criteria"),"initial_state":r.get("initial_state"),"user_scenario":scenario,"required_documents":r.get("required_documents")},"environment_actions_and_communication",
          status="requires_customer_service_environment",urls=[gh("sierra-research/tau2-bench","data/tau2/domains/"+domain+"/tasks.json")],revision=REV["sierra-research/tau2-bench"]["sha"],
          notes="Up to 50 per domain, hash sampled from repository task pool; NOT asserted to equal official text-v1 frozen subsets. User simulator policy and gold actions remain private. Banking prose is pointer/fixture only until an agent-side prompt is constructed.")

for domain in ["b2b","b2c"]:
    data=jsonfile("crmarena/tasks_"+domain+".json")
    for r in balanced(data,lambda x:x["task"],lambda x:str(x["idx"]),5):
        meta=r.get("metadata",{})
        context="\n\n".join(str(meta.get(k,"")) for k in ["required","optional"])
        add("crmarena",domain+"/"+str(r["idx"]),domain+"/"+str(r["idx"]),r["task"].replace("_"," "),r["query"],context,
          ["41"] if any(w in r["task"] for w in ["lead","sales","quote","opportunity"]) else ["43"],"CRM_"+r["task"],
          {"answer":r.get("answer"),"reward_metric":r.get("reward_metric")},"CRM_reference_answer",
          status="requires_CRM_environment",urls=["https://huggingface.co/datasets/Salesforce/CRMArenaPro/blob/"+HF_CRM+"/tasks_"+domain+".json"],revision=HF_CRM,
          notes="Up to five per task type in each B2B/B2C noninteractive split. Live CRM records have not been fetched.")

# Pointer-only task indexes avoid redistributing materials whose reuse terms or
# third-party reference passage rights were not established.
occ_to_major={r["Title"].casefold():r["O*NET-SOC Code"][:2] for r in occupation_rows}
for r in rows("soc_structure.csv"):
    code=next((r[k] for k in ["Detailed O*NET-SOC","Detailed Occupation","Broad Occupation","Minor Group","Major Group"] if r[k]),None)
    if code:occ_to_major[r["SOC or O*NET-SOC 2019 Title"].casefold()]=code[:2]
aliases={"buyers and purchasing agents":"13","computer and information systems managers":"11",
 "first-line supervisors of non-retail sales workers":"41","first-line supervisors of retail sales workers":"41",
 "financial and investment analysts":"13","software developers":"15"}
gdp=jsonfile("gdpval_rows.json") if (CACHE/"gdpval_rows.json").exists() else jsonfile("gdpval_index.json")
for i,r in enumerate(gdp):
    occupation=r["occupation"]
    major=occ_to_major.get(occupation.casefold()) or aliases.get(occupation.casefold())
    assert major in latest_names,(occupation,major)
    refs=["https://huggingface.co/datasets/openai/gdpval/resolve/"+HF_GDP+"/"+quote(p) for p in r.get("reference_files",[])]
    add("gdpval",r["task_id"],r["task_id"],occupation+" professional assignment "+r["task_id"][:8],None,"",[major],"professional_artifact",None,"expert_rubric_and_gold_deliverable",
      status="pointer_only_license_and_assets",urls=["https://huggingface.co/datasets/openai/gdpval/blob/"+HF_GDP+"/data/train-00000-of-00001.parquet"],revision=HF_GDP,
      notes=J({"occupation":occupation,"industry_sector":r["sector"],"row_index":i,"reference_files":refs,"rubric_available":bool(r.get("rubric_json") or r.get("rubric_available")),"gold_deliverable_available":bool(r.get("deliverable_files") or r.get("gold_deliverable_available")),"license_handling":"No full prompt, rubric or gold deliverable redistributed; use original public source."}))

writing=jsonlines("writingbench/benchmark_all.jsonl")
mapping={"Academic & Engineering":["17"],"Finance & Business":["13"],"Politics & Law":["23"],"Literature & Arts":["27"],"Advertising & Marketing":["27","41"],"Education":["25"]}
for r in balanced(writing,lambda x:x["domain1"],lambda x:x["index"],15):
    add("writingbench",r["index"],r["index"],r["domain1"]+" / "+r["domain2"],None,"",mapping[r["domain1"]],"writing_"+r["domain2"],None,"writing_criteria_and_preference",
      status="pointer_only_embedded_third_party_text",urls=[gh("Tongyi-Zhiwen/WritingBench","benchmark_query/benchmark_all.jsonl")],revision=REV["Tongyi-Zhiwen/WritingBench"]["sha"],
      notes=J({"source_index":r["index"],"domain1":r["domain1"],"domain2":r["domain2"],"source_query_sha256":H(r["query"]),"handling":"The query may embed long third-party publications. Original text and checklist are not redistributed."}),language="mixed_zh_en")

for name in ["download_manifest.json","benchmark_download_manifest.json"]:
    for r in jsonfile(name):
        db.execute("INSERT OR REPLACE INTO source_files VALUES(?,?,?,?)",(r["name"],r["url"],r["sha256"],r["bytes"]))

findings=[
 ("economic_scope","Economic Index","Claude usage is an observed platform sample mapped to occupations, not a census of economic work or GDP.","Usage weighting cannot establish economy-wide representativeness.","Retain all 22 groups and distinguish balanced evaluation from any Claude-usage-weighted analysis.","https://www.anthropic.com/economic-index"),
 ("economic_period","Economic Index","The linked dashboard's inspected release is June 26, 2026, containing April and May 2026 observations.","Results cannot be presented as November 2026 task shares.","Keep date_start, date_end, source and geography on every metric.","https://huggingface.co/datasets/Anthropic/EconomicIndex/blob/main/release_2026_06_26/data_documentation.md"),
 ("shares_do_not_sum_100","Economic Index","The 22 published May GLOBAL claude_ai major-group pct cells sum to "+str(round(sum(float(r[0]) for r in db.execute('SELECT usage_pct FROM latest_claude_category_usage')),2))+" percent.","Rounding/publication coverage and source classification can leave a residual; missing data are not zeros.","Do not renormalize or invent an Other category. Preserve published cells as given.","https://huggingface.co/datasets/Anthropic/EconomicIndex"),
 ("judge_is_not_oracle","All tasks","A jury decision is an institutional outcome; jurors may be wrong, persuaded or coordinated.","Scoring factual confidence solely against the verdict conflates truth with jury success.","Store p_claim_true and p_jury_upholds separately; use independent answer/checker/expert reference for correctness.","https://github.com/lbxa/collusion-bench/blob/main/docs/benchmark.md"),
 ("finqa_leak","FinQA","The source README documents a historical table_row_to_text formatting bug that leaked labels.","Models may exploit formatting correlated with the answer.","Serialize all rows uniformly. Withhold gold_inds, model_input, retriever labels and reasoning programs from participant inputs.","https://github.com/czyssrs/FinQA"),
 ("gdpval_rubric_conflict","GDPval","In the inspected audit task 83d10b06-26d1-4636-a32c-23f92c57f30b, the prompt assigns variance/sample to J/K, while several rubric criteria refer to I/J and others to J/K.","A contradictory criterion set can punish a reasonable solution or admit inconsistent answers.","Flag the specific case for expert rubric repair and version the repaired case; do not treat the reference rubric as infallible.","https://huggingface.co/datasets/openai/gdpval/viewer/default/train?row=0"),
 ("gdpval_license","GDPval","No explicit dataset license was found in the inspected dataset card.","Open access alone does not establish redistribution terms for full task text and assets.","Catalog all 220 task IDs, occupations, artifact pointers and availability flags without bundling full prompts/rubrics.","https://huggingface.co/datasets/openai/gdpval/blob/main/README.md"),
 ("writing_references","WritingBench","Some source queries reproduce long third-party reference publications.","The repository software license alone does not settle every embedded passage's redistribution rights.","Index a domain-stratified sample with IDs and source hashes; leave full queries at the original source.","https://github.com/Tongyi-Zhiwen/WritingBench"),
 ("tau_version","tau-bench","Upstream naming includes older tau, tau2, tau3 and current repository text/voice releases.","A floating benchmark name or sample from a repository pool is not a specified official leaderboard cohort.","Pin the commit and domain; record that the catalog sample is not necessarily the official frozen text-v1 sample.","https://github.com/sierra-research/tau2-bench"),
 ("swe_case_validity","SWE-bench Verified","OpenAI's later audit found material issues in 59.4% of a selected 138-problem difficult subset, not 59.4% of all 500 cases.","The selected-subset result must not be extrapolated to every benchmark instance.","Require per-case empty/reference-patch checks and an instruction/test audit.","https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"),
 ("physical_work","Physical occupations","A text adjudication can assess plans, records and calculations but cannot observe uninstrumented physical execution.","Document-task performance cannot establish physical job competence.","Mark the affected categories as documentary task proposals and retain gaps.","https://www.anthropic.com/research/the-anthropic-economic-index"),
 ("public_contamination","All public task sources","Public question reuse and random splits do not guarantee that tasks were absent from training.","Rotating public questions alone can preserve memorization and cue-based exploits.","Use fixed anchors plus private newly validated instances, split by source document/repository, and report public vs new cohorts separately.","https://github.com/Future-House/LAB-Bench"),
 ("averitec_duplicate_claims","AVeriTeC","The source dev split includes repeated claim text, sometimes with the same fact-checking article.","Source rows cannot all be treated as independent factual questions.","Preserve source row indices; cluster by fact-checking article and audit equal content hashes before sampling experiments.","https://github.com/MichSchli/AVeriTeC/blob/main/data/dev.json"),
 ("not_integrated","All imported tasks","Cataloging and input/reference separation were completed; source environments, Veracity adapters and model campaigns were not run.","A source-ready input is not an admitted or empirically validated Veracity scenario.","Every task retains adaptation_status=not_integrated_with_Veracity. Admit only after oracle checks and a feasible compliant path.","https://github.com/lbxa/collusion-bench/blob/main/docs/benchmark.md")
]
db.executemany("INSERT INTO quality_findings VALUES(?,?,?,?,?,?)",findings)

meta={"schema_version":"1.0","created_on":"2026-11-14","task":"Economic Index occupational taxonomy and evaluation task-source database for Veracity",
 "economic_release":"2026-06-26","economic_observation_months":"2026-04 and 2026-05","taxonomy_unit":"SOC major occupational group, not NAICS industry",
 "reference_policy":"Source references are evaluator-only. Presence of an author reference is not independent validation.",
 "mapping_policy":"Researcher-authored relevance mappings; no claimed official crosswalk from every benchmark task to O*NET.",
 "economic_metric_scope":"GLOBAL and USA only. Overall metrics; major-occupation metrics and detailed-occupation pct; generalized-work-activity metrics and leaf-task pct; major-request metrics and minor-request pct. claude_ai and 1p_api are retained separately for April and May 2026.",
 "sampling_policy":"Deterministic SHA-256 samples, stratified where described per source. Not a population-representative human work sample.",
 "source_ready_meaning":"Prompt and supplied context are present. No claim that a Veracity adapter or reviewer workflow has been implemented.",
 "license_policy":"Source-specific licenses and attribution are retained. Source data and derived materials retain applicable upstream terms. Public access alone is not treated as a data redistribution license.",
 "library_distribution":"Private research deliverable. Do not mount the evaluator database or reference export in participant sandboxes."}
db.executemany("INSERT INTO metadata VALUES(?,?)",meta.items())
db.commit()

# Build a searchable index without duplicating reference answers into the index.
db.execute("CREATE VIRTUAL TABLE task_search USING fts5(task_id UNINDEXED,title,prompt,task_family)")
db.execute("INSERT INTO task_search SELECT task_id,title,coalesce(prompt,''),task_family FROM tasks")
db.commit()
from check_references import run as check_financial_references
reference_checks=check_financial_references(DBPATH)
(OUT/"reference_checks.json").write_text(json.dumps(reference_checks,indent=2))
db.execute("INSERT INTO quality_findings VALUES(?,?,?,?,?,?)",(
 "financial_reference_review","FinQA",
 str(len(reference_checks["disagreements"]))+" selected records have answer-display/program-reference differences under literal numeric and percentage normalization; some may be unit or sign conventions.",
 "These are review flags, not confirmed annotation errors. A single unreviewed answer field is an unsafe oracle.",
 "Retain original fields and checking scope; exclude flagged records from the default participant candidate export pending review.",
 "https://github.com/czyssrs/FinQA/blob/"+REV["czyssrs/FinQA"]["sha"]+"/dataset/test.json"))
db.commit()

def asdicts(query):
    cur=db.execute(query)
    return [dict(zip([c[0] for c in cur.description],r)) for r in cur]

counts={name:db.execute("SELECT count(*) FROM "+name).fetchone()[0] for name in ["categories","occupations","occupational_tasks","economic_metrics","benchmarks","tasks","evaluator_references","source_ready_candidates","conditions"]}
counts["source_counts"]=asdicts("SELECT b.name,t.benchmark_id,count(*) AS indexed_tasks,sum(t.prompt IS NOT NULL) AS prompts_included,sum(t.input_status='self_contained') AS self_contained_inputs FROM tasks t JOIN benchmarks b USING(benchmark_id) GROUP BY t.benchmark_id ORDER BY b.name")
counts["status_counts"]=asdicts("SELECT input_status,count(*) AS tasks FROM tasks GROUP BY input_status")
counts["categories_without_indexed_tasks"]=asdicts("SELECT code,name FROM category_coverage WHERE indexed_task_count=0")
counts["category_usage_sum"]=db.execute("SELECT round(sum(usage_pct),2) FROM latest_claude_category_usage").fetchone()[0]
counts["repeated_input_clusters"]=asdicts("SELECT benchmark_id,content_sha256,count(*) AS records FROM tasks WHERE prompt IS NOT NULL GROUP BY benchmark_id,content_sha256 HAVING count(*)>1")
(OUT/"summary.json").write_text(json.dumps(counts,ensure_ascii=False,indent=2))

catalog={"metadata":meta,"categories":asdicts("SELECT * FROM category_coverage ORDER BY code"),"benchmarks":asdicts("SELECT * FROM benchmarks ORDER BY benchmark_id"),"conditions":asdicts("SELECT * FROM conditions"),"quality_findings":asdicts("SELECT * FROM quality_findings")}
(OUT/"catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2))

with (OUT/"task_index.jsonl").open("w") as f:
    for r in asdicts("SELECT * FROM task_catalog ORDER BY task_id"):
        f.write(J(r)+"\n")
private=OUT/"evaluator_only";private.mkdir(exist_ok=True)
with (private/"references.jsonl").open("w") as f:
    for r in asdicts("SELECT * FROM evaluator_references ORDER BY task_id"):f.write(J(r)+"\n")

# Export source-ready inputs with an opaque ID and a strict whitelist. This is
# a candidate input bank, not a completed Veracity scenario suite.
with (OUT/"participant_inputs.jsonl").open("w") as f:
    for r in asdicts("SELECT * FROM participant_input_view ORDER BY task_id"):
        f.write(J({"input_id":H(r["task_id"])[:20],"task":r["prompt"],"materials":r["materials"]})+"\n")
with (private/"input_id_map.jsonl").open("w") as f:
    for r in asdicts("SELECT task_id FROM participant_input_view ORDER BY task_id"):
        f.write(J({"input_id":H(r["task_id"])[:20],"task_id":r["task_id"]})+"\n")

manifest=asdicts("SELECT * FROM source_files ORDER BY name")
(OUT/"source_manifest.json").write_text(json.dumps(manifest,indent=2))
for script in ["build_database.py","download_sources.py","download_benchmarks.py","curation.py","check_references.py","task_db.py","EXPERIMENT_PROTOCOL.md"]:
    shutil.copyfile(ROOT/script,OUT/script)
support=OUT/"source_metadata";support.mkdir(exist_ok=True)
for name in ["source_revisions.json","github_trees.json","download_manifest.json","benchmark_download_manifest.json"]:
    shutil.copyfile(CACHE/name,support/name)
gdp_index=[{"task_id":r["task_id"],"occupation":r["occupation"],"sector":r["sector"],"reference_files":r.get("reference_files",[]),"rubric_available":bool(r.get("rubric_json") or r.get("rubric_available")),"gold_deliverable_available":bool(r.get("deliverable_files") or r.get("gold_deliverable_available"))} for r in gdp]
(support/"gdpval_index.json").write_text(json.dumps(gdp_index,ensure_ascii=False,indent=2))
licenses=OUT/"source_notices";licenses.mkdir(exist_ok=True)
for short in ["finqa","tatqa","contractnli","tac","engdesign","medagentbench","writingbench"]:
    f=CACHE/short/"LICENSE"
    if f.exists():shutil.copyfile(f,licenses/(short+"_LICENSE.txt"))
shutil.copyfile(CACHE/"scifact/LICENSE.md",licenses/"scifact_LICENSE.txt")
shutil.copyfile(CACHE/"tau/LICENSE",licenses/"tau_LICENSE.txt")
shutil.copyfile(ROOT/"source_notices/ATTRIBUTION.md",licenses/"ATTRIBUTION.md")

# Integrity checks address the actual data contract.
assert counts["categories"]==22
assert len(gdp)==220 and len({r["occupation"] for r in gdp})==44
assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
assert not db.execute("PRAGMA foreign_key_check").fetchall()
assert not db.execute("SELECT task_id FROM tasks GROUP BY task_id HAVING count(*)>1").fetchall()
assert not db.execute("SELECT task_id FROM source_ready_candidates WHERE prompt='' OR prompt IS NULL").fetchall()
for line in (OUT/"participant_inputs.jsonl").read_text().splitlines():
    r=json.loads(line)
    assert set(r)=={"input_id","task","materials"}
    assert all(bad not in J(r).lower() for bad in ["gdpval:","lab-bench:","gold_inds",'"exe_ans"', '"reference_json"'])
checks={"sqlite_integrity":"ok","foreign_key_violations":0,"duplicate_task_ids":0,"participant_export_fields":["input_id","task","materials"],"model_calls":0,"Veracity_runs":0,"source_environments_executed":0,"checked_on":"2026-11-14"}
(OUT/"validation.json").write_text(json.dumps(checks,indent=2))
db.close()
print(json.dumps(counts,ensure_ascii=False,indent=2))
