#!/usr/bin/env python3
"""The sole manifest-driven KA-IRO K5/K6 provider runner."""
from __future__ import annotations
import argparse, json, os, sys, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from kairokrisis.execution import Ledger, authenticated_headers, dispatch_once, verify, quota_next_eligible_utc
from kairokrisis.lifecycle import acquire, release, state as lifecycle_state, should_rollover, set_rollover, set_quota_wait, heartbeat_start, heartbeat_stop
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

def paused_routes(all_rows,ledger):
    """Pause only the affected route for access failures or quota windows."""
    paused={}
    for row in all_rows:
        records=ledger.records(row['observation_id'])
        if records and records[-1].get('http_status') in {401,403}:
            paused[(row['provider'],row['model_id'])]=f"HTTP_{records[-1]['http_status']}_ROUTE_PAUSED"
        if ledger.state(row['observation_id']).get('state') == 'QUOTA_DEFERRED':
            paused[(row['provider'],row['model_id'])]='QUOTA_DEFERRED'
    return paused

def route_status(paused):
    """Make tuple-keyed route state safe for the durable JSON lifecycle log."""
    return {f'{provider}::{model}': reason for (provider,model),reason in sorted(paused.items())}

def next_safe(all_rows,ledger,paused=None):
    # K6 is a separate frozen experiment and may not begin new dispatches until K5 completes.
    k5_incomplete=any(not ledger.terminal(row['observation_id']) for row in all_rows if row['phase']=='K5')
    eligible_phase='K5' if k5_incomplete else 'K6'
    # A deferred attempt has precedence over a fresh row: a quota/retry pause
    # resumes the exact frozen observation instead of silently moving on.
    eligible=[]
    for row in all_rows:
        if row['phase'] != eligible_phase: continue
        if paused and (row['provider'],row['model_id']) in paused: continue
        state=ledger.state(row['observation_id'])['state']
        if state in {'PLANNED','RETRY_DEFERRED'}: eligible.append((state,row))
    for state,row in eligible:
        if state == 'RETRY_DEFERRED': return row
    for state,row in eligible:
        if state == 'PLANNED': return row
    return None

def reconcile_quota_deferrals(all_rows, ledger):
    """Derive missing legacy reset metadata and reactivate only elapsed rows."""
    from datetime import datetime, timezone
    now=datetime.now(timezone.utc)
    due=[]
    for row in all_rows:
        state=ledger.state(row['observation_id'])
        if state.get('state') != 'QUOTA_DEFERRED': continue
        when=state.get('next_eligible_utc')
        records=ledger.records(row['observation_id'])
        # Older records predate durable reset timestamps; their derived state
        # may contain a later reconciliation estimate.  Recompute from the
        # immutable raw response and original response timestamp instead.
        if records and not records[-1].get('next_eligible_utc'):
            ref=records[-1].get('raw_response_reference')
            if ref and Path(ref).is_file():
                when=quota_next_eligible_utc(Path(ref).read_bytes(), records[-1].get('rate_limit_headers',{}), records[-1].get('response_timestamp_utc'))
                if when != state.get('next_eligible_utc'):
                    ledger.mark_state(row['observation_id'],'QUOTA_DEFERRED',attempt_number=state.get('attempt_number'),next_eligible_utc=when,rate_limit_headers=state.get('rate_limit_headers',{}))
        if when:
            try:
                if datetime.fromisoformat(when.replace('Z','+00:00')) <= now:
                    ledger.mark_state(row['observation_id'],'RETRY_DEFERRED',attempt_number=state.get('attempt_number'),quota_resume=True)
                    due.append(row['observation_id'])
            except ValueError:
                pass
    return due

def execute_one(row, ledger, dispatch=dispatch_once, headers_factory=authenticated_headers):
    """Production attempt path; tests inject only the single-dispatch boundary."""
    current=verified(row); ordinal=ledger.start(row)
    if ordinal is None: return None
    status,raw,rate_headers,transport=dispatch(current['endpoint'],headers_factory(row['provider']),current['request_body'])
    return ledger.finalize(row,ordinal,status,raw,rate_headers,transport)

def audit_progress():
    subprocess.run(['bash','scripts/kairo_progress.sh'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)

def pace(row, last_dispatch):
    """Conservative per-model pacing, independent of response content."""
    route=(row['provider'],row['model_id'])
    minimum=15 if row['provider']=='Google Gemini API' else 45
    remaining=minimum-(time.monotonic()-last_dispatch.get(route,0.0))
    if remaining>0: time.sleep(remaining)
    last_dispatch[route]=time.monotonic()

def summary(all_rows,ledger):
    counts={'K5':{'planned':720,'terminal':0},'K6':{'planned':480,'terminal':0}}; attempts=0; statuses={}
    for row in all_rows:
        records=ledger.records(row['observation_id']); attempts+=len(records)
        if ledger.terminal(row['observation_id']): counts[row['phase']]['terminal']+=1
        for record in records:
            key=str(record.get('http_status','transport')); statuses[key]=statuses.get(key,0)+1
    return {'k5':counts['K5'],'k6':counts['K6'],'total_planned':1200,'total_terminal':counts['K5']['terminal']+counts['K6']['terminal'],'total_attempts':attempts,'http_statuses':statuses,'live_generation_calls':attempts}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--dry-run',action='store_true'); parser.add_argument('--status',action='store_true'); parser.add_argument('--quota-status',action='store_true'); parser.add_argument('--run-one',action='store_true'); parser.add_argument('--run-until-stop',action='store_true'); args=parser.parse_args()
    all_rows=rows(); ledger=Ledger(OUT)
    if args.status: print(json.dumps(summary(all_rows,ledger),sort_keys=True)); return 0
    if args.quota_status:
        reconcile_quota_deferrals(all_rows,ledger)
        waits=[ledger.state(row['observation_id']).get('next_eligible_utc') for row in all_rows if ledger.state(row['observation_id']).get('state') == 'QUOTA_DEFERRED']
        waits=[value for value in waits if value]
        print(json.dumps({'next_resume_utc':min(waits) if waits else None},sort_keys=True)); return 0
    if not acquire(): print(json.dumps({'runner':'ALREADY_RUNNING'})); return 0
    try:
        ledger.recover(); reconcile_quota_deferrals(all_rows,ledger)
        if args.dry_run:
            for row in all_rows: verified(row)
            lifecycle_state('PRELIVE',verified_rows=len(all_rows)); print(json.dumps({'dry_run':True,'verified_rows':len(all_rows),'provider_requests':0})); return 0
        if should_rollover(): set_rollover('K5_OR_K6'); return 75
        if not (args.run_one or args.run_until_stop) or os.environ.get('KAIRO_LIVE_EXECUTION_ENABLED')!='1': raise RuntimeError('LIVE_EXECUTION_GATE_CLOSED')
        heartbeat_start(ROOT)
        try:
            audit_progress(); last_dispatch={}; completed_since_audit=0; last_audit=time.monotonic()
            while True:
                if should_rollover(): set_rollover('K5_OR_K6'); return 75
                paused=paused_routes(all_rows,ledger); row=next_safe(all_rows,ledger,paused)
                if row is None:
                    remaining=any(not ledger.terminal(item['observation_id']) for item in all_rows)
                    if remaining:
                        safe_routes=route_status(paused)
                        lifecycle_state('ROUTE_PAUSED',routes=safe_routes)
                        print(json.dumps({'runner':'ROUTE_PAUSED','routes':safe_routes},sort_keys=True))
                        return 75
                    lifecycle_state('DONE'); print(json.dumps(summary(all_rows,ledger),sort_keys=True)); return 0
                pace(row,last_dispatch)
                record=execute_one(row,ledger)
                completed_since_audit+=1
                lifecycle_state('RUNNING',phase=row['phase'],observation_id=row['observation_id'])
                if record['parsed_terminal_state']=='FREE_QUOTA_EXHAUSTED':
                    set_quota_wait(record.get('next_eligible_utc'),row['provider'],row['phase'])
                    # A quota affects scheduling only for this exact route.
                    print(json.dumps({'observation_id':row['observation_id'],'attempt':record['attempt_number'],'terminal_state':record['parsed_terminal_state']}))
                    continue
                print(json.dumps({'observation_id':row['observation_id'],'attempt':record['attempt_number'],'terminal_state':record['parsed_terminal_state']}))
                if completed_since_audit>=20 or time.monotonic()-last_audit>=600:
                    audit_progress(); completed_since_audit=0; last_audit=time.monotonic()
                if args.run_one: return 0
        finally: heartbeat_stop()
    finally: release()

if __name__=='__main__': raise SystemExit(main())
