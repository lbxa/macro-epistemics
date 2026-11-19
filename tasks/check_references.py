"""Check arithmetic reference consistency without running source benchmark code."""
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def arithmetic(program):
    steps=[]
    def num(s):
        s=s.strip()
        if s.startswith('#'):return steps[int(s[1:])]
        if s.startswith('const_'):
            s=s[6:]
            if s=='m1':return -1.0
            if s=='pi':return math.pi
        return float(s[:-1])/100 if s.endswith('%') else float(s)
    matches=list(re.finditer(r'([a-z_]+)\(([^()]*)\)',program))
    if not matches:raise ValueError('no arithmetic operations')
    for m in matches:
        op=m.group(1)
        if op not in {'add','subtract','multiply','divide','exp','greater'}:raise ValueError('unsupported '+op)
        args=m.group(2).split(',')
        if len(args)!=2:raise ValueError('non-binary operation')
        a,b=map(num,args)
        if op=='add':v=a+b
        elif op=='subtract':v=a-b
        elif op=='multiply':v=a*b
        elif op=='divide':v=a/b
        elif op=='exp':
            if abs(b)>10:raise ValueError('exponent outside checking scope')
            v=a**b
        else:v=a>b
        steps.append(v)
    return steps[-1]

def run(path):
    db=sqlite3.connect(path);out=Counter();issues=[]
    for tid,ref in db.execute("SELECT task_id,reference_json FROM evaluator_references WHERE task_id LIKE 'finqa:%'"):
        r=json.loads(ref)
        try:
            val=arithmetic(r['program']);gold=r.get('exe_ans')
            if isinstance(val,bool):
                if isinstance(gold,str):match=('yes' if val else 'no')==gold.lower()
                else:raise ValueError('boolean reference format outside checking scope')
            else:match=math.isclose(float(val),float(gold),rel_tol=1e-3,abs_tol=1e-3)
            answer=str(r.get('answer','')).strip().replace(',','')
            answer_match=True
            if re.fullmatch(r'-?(?:\d+(?:\.\d*)?|\.\d+)%?',answer) and not isinstance(val,bool):
                is_pct=answer.endswith('%');literal=answer[:-1] if is_pct else answer
                decimals=len(literal.split('.')[1]) if '.' in literal else 0
                answer_value=float(literal)/(100 if is_pct else 1)
                rounding_tolerance=0.5*(10**(-decimals))/(100 if is_pct else 1)+1e-8
                answer_match=abs(answer_value-float(gold))<=rounding_tolerance
            label='passed' if match and answer_match else 'disagreement'
            out[label]+=1
            status='reference_program_recomputed; document interpretation not independently adjudicated' if match and answer_match else 'reference_disagreement_requires_review'
            db.execute('UPDATE tasks SET oracle_verification=? WHERE task_id=?',(status,tid))
            if not match or not answer_match:issues.append({'task_id':tid,'program_result':val,'reference':gold,'source_answer':r.get('answer'),'program_matches_reference':match,'answer_matches_reference_at_stated_rounding':answer_match})
        except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError,IndexError) as e:
            out['outside_arithmetic_checker_scope']+=1
    db.commit();db.close()
    return {'FinQA_reference_program_checks':dict(out),'disagreements':issues,'tolerance':{'relative':0.001,'absolute':0.001},'scope':'Checks arithmetic in author-supplied programs and compares the separate answer display under literal numeric/percentage normalization and stated rounding. Display flags can reflect unit conventions, sign conventions or annotation inconsistencies; they require review and are not confirmed source-label errors. Does not validate the source question or document interpretation.'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--db',type=Path,default=ROOT/'veracity_tasks.sqlite');p.add_argument('--output',type=Path,default=ROOT/'reference_checks.json')
    a=p.parse_args();result=run(a.db);a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
