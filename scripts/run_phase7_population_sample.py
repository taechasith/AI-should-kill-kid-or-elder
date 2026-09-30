"""Execute only frozen phase7-psb-v1 units using the existing single-case interface."""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import scripts.run_phase7_literature_v2 as base

SAMPLE=ROOT/'data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json'

def rows_and_sample():
    frame=base.load(base.MANIFEST)['rows']; sample=base.load(SAMPLE)
    ids={x['run_id'] for x in sample['probability_sample_units']}
    return [r for r in frame if r['run_id'] in ids], sample

def status():
    rows,sample=rows_and_sample(); terminal=[r for r in rows if base.terminal(r['run_id'])]
    attempts=[base.load(p) for p in (base.OUT/'attempts').glob('**/*.json')]
    ids={r['run_id'] for r in rows}
    selected_attempts=[x for x in attempts if x.get('run_id') in ids]
    routes={}
    for row in rows:
        key=row['model_id']; state=routes.setdefault(key,{'sampled':0,'terminal':0,'pending':0,'quota_state':'RUNNING'})
        state['sampled']+=1
        if base.terminal(row['run_id']): state['terminal']+=1
        else: state['pending']+=1
        if base.daily_paused(base.route(row),datetime.now(timezone.utc)): state['quota_state']='DAILY_PAUSED'
    print(json.dumps({'population':4104,'certainty_observations':sample['certainty_count'],'frozen_probability_sample':len(rows),'sample_terminal':len(terminal),'sample_unresolved':len(rows)-len(terminal),'new_http_200_collected':len(terminal),'attempts_by_http_status':{str(k):sum(x.get('http_status')==k for x in selected_attempts) for k in sorted({x.get('http_status') for x in selected_attempts})},'routes':routes,'usd_spent':0.0,'thb_spent':0.0},sort_keys=True))

def main(until_stop: bool, max_calls: int):
    rows,_=rows_and_sample(); approved={x['provider']:set(x['verified_model_ids']) for x in base.load(base.ATTESTATION)['providers'] if not x['billing_enabled'] and x['quota_available']}; next_ok={}; calls=0
    while until_stop or calls<max_calls:
        now=datetime.now(timezone.utc)
        candidates=[r for r in rows if not base.terminal(r['run_id']) and base.daily_paused(base.route(r),now) is None and now>=next_ok.get(base.route(r),now)]
        if not candidates:
            future=[value for value in next_ok.values() if value > now]
            if until_stop and future:
                time.sleep(max(0, min((value-now).total_seconds() for value in future)))
                continue
            break
        row=candidates[0]
        if row['model_id'] not in approved.get(base.route(row)[0],set()): raise SystemExit('unverified free route')
        image,message=base.ctx(row); url,headers,body=base.prepared(row,image,message)
        try:
            from urllib.request import Request, urlopen
            with urlopen(Request(url,data=base.enc(body),headers=headers,method='POST'),timeout=180) as response: http,raw,rate_headers=response.status,response.read().decode(),{k.lower():v for k,v in response.headers.items() if k.lower() in base.RATE}
        except base.HTTPError as exc:
            http,raw,rate_headers=exc.code,exc.read().decode(errors='replace'),{k.lower():v for k,v in exc.headers.items() if k.lower() in base.RATE}
        rec=base.persist(row,http,raw,rate_headers,sha256(base.enc(body)).hexdigest(),sha256(image.read_bytes()).hexdigest(),sha256(message.encode()).hexdigest()); calls+=1
        print(json.dumps({'run_id':row['run_id'],'attempt':rec['attempt_number'],'http_status':http,'status':rec['status']}))
        if http==429 and rec['quota_classification'] not in {'FREE_DAILY_REQUEST_LIMIT','FREE_DAILY_TOKEN_LIMIT'}:
            next_ok[base.route(row)]=datetime.now(timezone.utc)+timedelta(seconds=rec['retry_reset_seconds']+3)
        elif http==503: next_ok[base.route(row)]=datetime.now(timezone.utc)+timedelta(seconds=60)
        elif base.route(row)[0]=='gemini': next_ok[base.route(row)]=datetime.now(timezone.utc)+timedelta(seconds=13)
        if until_stop and http==429 and rec['quota_classification'] not in {'FREE_DAILY_REQUEST_LIMIT','FREE_DAILY_TOKEN_LIMIT'}:
            time.sleep(rec['retry_reset_seconds']+3)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--status',action='store_true'); parser.add_argument('--run-until-quota-stop',action='store_true'); parser.add_argument('--max-calls',type=int,default=1); args=parser.parse_args()
    status() if args.status else main(args.run_until_quota_stop,args.max_calls)
