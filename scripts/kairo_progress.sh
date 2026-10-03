#!/usr/bin/env bash
# Non-scientific progress snapshot derived solely from durable KA-IRO artifacts.
set -euo pipefail
ROOT=/workspaces/ka-iro-krisis-v2-codespace
cd "$ROOT"
python - <<'PY'
import hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from scripts.run_kairo_krisis import rows, OUT
from kairokrisis.execution import Ledger

ledger=Ledger(OUT); all_rows=rows(); phase='PRELIVE'; counts={'K5':[720,0],'K6':[480,0]}; statuses={}; ambiguous=0
terminal_counts={}; raw_integrity=True; duplicate_terminal=0; resume_times=[]
for row in all_rows:
    recs=ledger.records(row['observation_id'])
    state=ledger.state(row['observation_id'])
    if ledger.terminal(row['observation_id']):
        counts[row['phase']][1]+=1
        terminal_counts[row['observation_id']]=0
    if state.get('state') == 'QUOTA_DEFERRED' and state.get('next_eligible_utc'):
        resume_times.append(state['next_eligible_utc'])
    for rec in recs:
        s=rec.get('http_status'); statuses[str(s)]=statuses.get(str(s),0)+1
        if rec.get('parsed_terminal_state')=='AMBIGUOUS_TRANSPORT_OUTCOME': ambiguous+=1
        if rec.get('terminal'):
            terminal_counts[row['observation_id']]=terminal_counts.get(row['observation_id'],0)+1
        ref=rec.get('raw_response_reference')
        if ref:
            raw=Path(ref) if Path(ref).is_absolute() else Path.cwd()/ref
            raw_integrity = raw_integrity and raw.is_file() and hashlib.sha256(raw.read_bytes()).hexdigest()==rec.get('raw_response_sha256')
state_path=Path('/tmp/ka-iro-lifecycle.json')
if state_path.exists():
    state=json.loads(state_path.read_text()); phase=state.get('phase', state.get('state','PRELIVE'))
if counts['K5'][1] < 720 and counts['K5'][1] > 0: phase='K5'
elif counts['K5'][1] == 720 and counts['K6'][1] < 480: phase='K6'
elif counts['K6'][1] == 480: phase='K7'
pid=None
# Foreground IDE execution holds the canonical runner lock; detached launchers
# may additionally write the historical autonomous PID file.
for pid_path in (Path('/tmp/ka-iro-runner.lock'), Path('/tmp/ka-iro-autonomous.pid')):
 if pid_path.exists():
  try:
   content=json.loads(pid_path.read_text()) if pid_path.name.endswith('.lock') else {'pid':pid_path.read_text().strip()}
   candidate=int(content['pid']); os.kill(candidate,0); pid=candidate; break
  except (ValueError,KeyError,json.JSONDecodeError,ProcessLookupError): pass
try: head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception: head=None
payload={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'phase':phase,'k5_planned':720,'k5_terminal':counts['K5'][1],'k5_remaining':720-counts['K5'][1],'k6_planned':480,'k6_terminal':counts['K6'][1],'k6_remaining':480-counts['K6'][1],'http_attempts':sum(statuses.values()),'http_200':statuses.get('200',0),'http_429':statuses.get('429',0),'http_5xx':sum(statuses.get(str(code),0) for code in (500,502,503,504)),'quota_deferred':len(resume_times),'ambiguous_transport':ambiguous,'duplicate_terminal_observations':sum(count>1 for count in terminal_counts.values()),'raw_response_integrity':'PASS' if raw_integrity else 'FAIL','manifest_integrity':'PASS' if len(all_rows)==1200 and len({r['observation_id'] for r in all_rows})==1200 else 'FAIL','cost_usd':0.0,'resume_not_before_utc':min(resume_times) if resume_times else None,'last_checkpoint':head,'head':head,'runner_pid':pid,'disk_free_bytes':shutil.disk_usage('.').free}
target=Path('runtime/ka-iro-progress.json'); target.parent.mkdir(parents=True,exist_ok=True); temp=target.with_suffix('.tmp'); temp.write_text(json.dumps(payload,sort_keys=True)+'\n'); os.replace(temp,target)
print(json.dumps(payload,sort_keys=True))
PY
