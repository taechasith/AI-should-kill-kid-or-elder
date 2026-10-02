#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspaces/ka-iro-krisis-v2-codespace
cd "$ROOT"
runner=STOPPED
if [[ -f /tmp/ka-iro-autonomous.pid ]] && kill -0 "$(< /tmp/ka-iro-autonomous.pid)" 2>/dev/null; then runner=RUNNING; fi
if [[ -f /tmp/KA_IRO_NEEDS_RESTART ]]; then runner=ROLLOVER; fi
if [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT ]]; then runner=QUOTA_WAIT; fi
if [[ -f /tmp/KA_IRO_WINDOWS_BOOTSTRAP_REQUIRED ]]; then runner=PRELIVE; fi
if [[ -f /tmp/ka-iro-lifecycle.json ]]; then
  local_state=$(python -c 'import json; print(json.load(open("/tmp/ka-iro-lifecycle.json")).get("state","STOPPED"))')
  [[ "$runner" == STOPPED ]] && runner="$local_state"
fi
heartbeat_age=null
if [[ -f /tmp/ka-iro-heartbeat.pid ]] && kill -0 "$(< /tmp/ka-iro-heartbeat.pid)" 2>/dev/null; then heartbeat_age=0; fi
next=null; [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT ]] && next=$(python -c 'import json; print(json.dumps(json.load(open("/tmp/KA_IRO_EXTERNAL_QUOTA_WAIT")).get("next_resume_utc")))')
printf '{"runner":"%s","phase":"K5_K6_PRELIVE","heartbeat_age_seconds":%s,"last_checkpoint":"%s","next_resume_utc":%s,"head":"%s","branch":"%s"}\n' "$runner" "$heartbeat_age" "$(git rev-parse --short HEAD)" "$next" "$(git rev-parse HEAD)" "$(git branch --show-current)"
