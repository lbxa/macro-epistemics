"""Read and export the Veracity task-source catalog. No model calls are made."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db",type=Path,default=Path(__file__).with_name("veracity_tasks.sqlite"))
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("stats")
    sub.add_parser("categories")
    s=sub.add_parser("search");s.add_argument("words");s.add_argument("--limit",type=int,default=10)
    s=sub.add_parser("show");s.add_argument("task_id");s.add_argument("--with-reference",action="store_true")
    s=sub.add_parser("export-inputs");s.add_argument("--benchmark",required=True)
    s.add_argument("--limit",type=int,default=20);s.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    db=sqlite3.connect(a.db.resolve().as_uri()+"?mode=ro",uri=True);db.row_factory=sqlite3.Row
    def query(sql,args=()):return [dict(r) for r in db.execute(sql,args)]
    if a.command=="stats":
        data=query("SELECT benchmark_id,count(*) AS task_records,sum(input_status='self_contained') AS self_contained_inputs FROM tasks GROUP BY benchmark_id ORDER BY benchmark_id")
    elif a.command=="categories":
        data=query("SELECT code,name,usage_pct,proposed_phase,indexed_task_count,coverage_note FROM category_coverage ORDER BY usage_pct DESC")
    elif a.command=="search":
        # Quote each search term so user text is not interpreted as FTS syntax.
        terms=" AND ".join('"'+s.replace('"','""')+'"' for s in a.words.split())
        data=query("SELECT t.task_id,t.title,t.benchmark_id,t.input_status,t.task_family FROM task_search s JOIN tasks t USING(task_id) WHERE task_search MATCH ? LIMIT ?",(terms,max(1,min(a.limit,100))))
    elif a.command=="show":
        data=query("SELECT t.*,e.content AS materials,e.source_urls_json FROM task_catalog t LEFT JOIN evidence_bundles e USING(evidence_id) WHERE task_id=?",(a.task_id,))
        if not data:p.error("No matching task ID")
        if a.with_reference:
            data[0]["evaluator_only_reference"]=query("SELECT reference_json,reference_status FROM evaluator_references WHERE task_id=?",(a.task_id,))
    elif a.command=="export-inputs":
        data=query("SELECT t.task_id,t.prompt,e.content AS materials,t.content_sha256 FROM tasks t JOIN evidence_bundles e USING(evidence_id) WHERE t.benchmark_id=? AND t.input_status='self_contained' AND t.prompt IS NOT NULL AND t.oracle_verification NOT LIKE 'reference_disagreement%' ORDER BY t.task_id",(a.benchmark,))
        seen=set();selected=[]
        for r in data:
            if r["content_sha256"] in seen:continue
            seen.add(r["content_sha256"]);selected.append(r)
            if len(selected)>=a.limit:break
        if not selected:p.error("No self-contained input candidates for this benchmark")
        if a.output.resolve()==a.db.resolve():p.error("Output cannot overwrite the database")
        with a.output.open("w") as f:
            for r in selected:
                out={"input_id":hashlib.sha256(r["task_id"].encode()).hexdigest()[:20],"task":r["prompt"],"materials":r["materials"]}
                f.write(json.dumps(out,ensure_ascii=False)+"\n")
        data={"written":len(selected),"output":str(a.output),"status":"Input candidates only; a Veracity adapter and scenario admission are still required"}
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
