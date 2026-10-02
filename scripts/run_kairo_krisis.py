#!/usr/bin/env python3
"""The sole manifest-driven KA-IRO K5/K6 provider runner."""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from kairokrisis.execution import Ledger, authenticated_headers, dispatch_once, verify
from kairokrisis.lifecycle import acquire, release, state as lifecycle_state, should_rollover
from kairokrisis.serialization import serialized
K5 = ROOT / 'data/ka-iro-krisis/v2/request_serialization_v1/k5_execution_manifest.json'
K6 = ROOT / 'data/ka-iro-krisis/v2/request_serialization_v1/k6_execution_manifest.json'
OUT = ROOT / 'data/ka-iro-krisis/v2/execution'

def rows():
    result=[]
    for phase,path in (('K5',K5),('K6',K6)):
        for original in json.loads(path.read_text())['rows']:
            row=dict(original); row['phase']=phase
            if phase=='K6': row['observation_id']=row['k6_observation_id']
            result.append(row)
    ids=[row['observation_id'] for row in result]
    if len(ids)!=1200 or len(set(ids))!=1200: raise RuntimeError('FROZEN_MANIFEST_INTEGRITY_FAILURE')
    return sorted(result,key=lambda row:row['execution_order_key'])

def verified(row):
    verify(row,ROOT); current=serialized(row,ROOT)
    if any(current[key]!=row[key] for key in ('request_body_sha256','request_body_bytes','request_envelope_sha256')): raise RuntimeError('FROZEN_PAYLOAD_INTEGRITY_FAILURE')
    return current

def next_safe(all_rows,ledger):
    for row in all_rows:
        if ledger.state(row['observation_id'])['state'] in {'PLANNED','RETRY_DEFERRED'}: return row
    return None

def summary(all_rows,ledger):
    counts={'K5':{'planned':720,'terminal':0},'K6':{'planned':480,'terminal':0}}; attempts=0; statuses={}
    for row in all_rows:
        records=ledger.records(row['observation_id']); attempts+=len(records)
        if ledger.terminal(row['observation_id']): counts[row['phase']]['terminal']+=1
        for record in records:
            key=str(record.get('http_status','transport')); statuses[key]=statuses.get(key,0)+1
    return {'k5':counts['K5'],'k6':counts['K6'],'total_planned':1200,'total_terminal':counts['K5']['terminal']+counts['K6']['terminal'],'total_attempts':attempts,'http_statuses':statuses,'live_generation_calls':attempts}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--dry-run',action='store_true'); parser.add_argument('--status',action='store_true'); parser.add_argument('--run-one',action='store_true'); args=parser.parse_args()
    all_rows=rows(); ledger=Ledger(OUT)
    if args.status: print(json.dumps(summary(all_rows,ledger),sort_keys=True)); return 0
    if not acquire(): print(json.dumps({'runner':'ALREADY_RUNNING'})); return 0
    try:
        ledger.recover()
        if args.dry_run:
            for row in all_rows: verified(row)
            lifecycle_state('PRELIVE',verified_rows=len(all_rows)); print(json.dumps({'dry_run':True,'verified_rows':len(all_rows),'provider_requests':0})); return 0
        if should_rollover():
            lifecycle_state('ROLLOVER',reason='CODESPACE_ROLLOVER_REQUIRED'); Path('/tmp/KA_IRO_NEEDS_RESTART').write_text('rollover required; no scientific state changed\n'); return 75
        if not args.run_one or os.environ.get('KAIRO_LIVE_EXECUTION_ENABLED')!='1': raise RuntimeError('LIVE_EXECUTION_GATE_CLOSED')
        row=next_safe(all_rows,ledger)
        if row is None: lifecycle_state('DONE'); print(json.dumps(summary(all_rows,ledger),sort_keys=True)); return 0
        current=verified(row); ordinal=ledger.start(row)
        if ordinal is None: return 0
        status,raw,rate_headers,transport=dispatch_once(current['endpoint'],authenticated_headers(row['provider']),current['request_body'])
        record=ledger.finalize(row,ordinal,status,raw,rate_headers,transport)
        lifecycle_state('RUNNING',phase=row['phase'],observation_id=row['observation_id'])
        print(json.dumps({'observation_id':row['observation_id'],'attempt':ordinal,'terminal_state':record['parsed_terminal_state']})); return 0
    finally: release()

if __name__=='__main__': raise SystemExit(main())
