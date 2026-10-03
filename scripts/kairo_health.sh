#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspaces/ka-iro-krisis-v2-codespace
cd "$ROOT"
runner=STOPPED
for pidfile in /tmp/ka-iro-runner.lock /tmp/ka-iro-autonomous.pid; do
  if [[ -f "$pidfile" ]]; then
    candidate=$(python - "$pidfile" <<'PY'
import json,sys
try:
    value=open(sys.argv[1]).read().strip()
    print(json.loads(value).get('pid','') if sys.argv[1].endswith('.lock') else value)
except Exception: pass
PY
)
    if [[ -n "$candidate" ]] && kill -0 "$candidate" 2>/dev/null; then runner=RUNNING; break; fi
  fi
done
if [[ -f /tmp/KA_IRO_NEEDS_RESTART ]]; then runner=ROLLOVER; fi
# A quota marker may coexist with an active, route-isolated runner that is
# legitimately progressing another frozen model route.
if [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT && "$runner" == STOPPED ]]; then runner=QUOTA_WAIT; fi
if [[ -f /tmp/ka-iro-lifecycle.json ]]; then
  local_state=$(python -c 'import json; print(json.load(open("/tmp/ka-iro-lifecycle.json")).get("state","STOPPED"))')
  # RUNNING is authoritative only when a currently live PID established it.
  # A Codespace/session interruption can leave the durable local state behind;
  # never let that stale marker suppress safe recovery on the next audit.
  if [[ "$runner" == STOPPED ]]; then
    case "$local_state" in
      DONE|BLOCKED|QUOTA_WAIT|ROLLOVER|PRELIVE) runner="$local_state" ;;
    esac
  fi
fi
heartbeat_age=null
if [[ -f /tmp/ka-iro-heartbeat.pid ]] && kill -0 "$(< /tmp/ka-iro-heartbeat.pid)" 2>/dev/null; then heartbeat_age=0; fi
next=null; [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT ]] && next=$(python -c 'import json; print(json.dumps(json.load(open("/tmp/KA_IRO_EXTERNAL_QUOTA_WAIT")).get("next_resume_utc")))')
# /tmp lifecycle markers are deliberately ephemeral and can disappear during a
# Codespace restart. The append-only execution ledger is the durable source
# of truth: surface an outstanding quota deferral even after that ephemeral
# marker has vanished. This only reports state; it never reactivates a row.
durable_quota=$(python - <<'PY'
import json
from scripts.run_kairo_krisis import OUT, rows
from kairokrisis.execution import Ledger
ledger=Ledger(OUT)
waits=[]
for row in rows():
    state=ledger.state(row['observation_id'])
    if state.get('state') == 'QUOTA_DEFERRED':
        waits.append(state.get('next_eligible_utc'))
waits=[value for value in waits if value]
print(json.dumps(min(waits) if waits else None))
PY
)
if [[ ( "$runner" == STOPPED || "$runner" == PRELIVE ) && "$durable_quota" != null ]]; then runner=QUOTA_WAIT; fi
if [[ "$next" == null && "$durable_quota" != null ]]; then next="$durable_quota"; fi
phase=$(python - <<'PY'
from scripts.run_kairo_krisis import OUT, rows
from kairokrisis.execution import Ledger
ledger=Ledger(OUT); all_rows=rows()
k5=sum(ledger.terminal(r['observation_id']) for r in all_rows if r['phase']=='K5')
k6=sum(ledger.terminal(r['observation_id']) for r in all_rows if r['phase']=='K6')
print('K5' if k5 < 720 else ('K6' if k6 < 480 else 'K7'))
PY
)
printf '{"runner":"%s","phase":"%s","heartbeat_age_seconds":%s,"last_checkpoint":"%s","next_resume_utc":%s,"head":"%s","branch":"%s"}\n' "$runner" "$phase" "$heartbeat_age" "$(git rev-parse --short HEAD)" "$next" "$(git rev-parse HEAD)" "$(git branch --show-current)"
