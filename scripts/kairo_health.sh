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
  [[ "$runner" == STOPPED ]] && runner="$local_state"
fi
heartbeat_age=null
if [[ -f /tmp/ka-iro-heartbeat.pid ]] && kill -0 "$(< /tmp/ka-iro-heartbeat.pid)" 2>/dev/null; then heartbeat_age=0; fi
next=null; [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT ]] && next=$(python -c 'import json; print(json.dumps(json.load(open("/tmp/KA_IRO_EXTERNAL_QUOTA_WAIT")).get("next_resume_utc")))')
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
