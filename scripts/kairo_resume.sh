#!/usr/bin/env bash
# Canonical, idempotent operational entry point. It never deletes state.
set -euo pipefail
ROOT=/workspaces/ka-iro-krisis-v2-codespace
# A linked Git worktree stores .git as a file, while a primary checkout uses a directory.
[[ -e "$ROOT/.git" ]] || { echo '{"runner":"BLOCKED","reason":"AUTHORITATIVE_WORKTREE_MISSING"}'; exit 2; }
cd "$ROOT"
if [[ "$(git branch --show-current)" != ka-iro-krisis-v2 ]]; then
  # Supervisor rehydration intentionally uses a detached worktree pinned to origin.
  [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/ka-iro-krisis-v2)" ]] || { echo '{"runner":"BLOCKED","reason":"WRONG_BRANCH_OR_HEAD"}'; exit 2; }
fi
[[ "$(git remote get-url origin)" == *taechasith/AI-should-kill-kid-or-elder* ]] || { echo '{"runner":"BLOCKED","reason":"UNEXPECTED_REMOTE"}'; exit 2; }
for tag in ka-iro-krisis-k4-v2 ka-iro-krisis-k5-design-v1 ka-iro-krisis-k6-design-v1 ka-iro-krisis-request-serialization-v1; do
  git rev-parse -q --verify "$tag^{}" >/dev/null || { echo "{\"runner\":\"BLOCKED\",\"reason\":\"MISSING_TAG\",\"tag\":\"$tag\"}"; exit 2; }
done
python scripts/run_kairo_krisis.py --dry-run >/dev/null
for key in GEMINI_API_KEY GROQ_API_KEY; do
  [[ -n "${!key:-}" ]] || { echo "{\"runner\":\"PRELIVE\",\"credential\":\"$key\",\"presence\":\"MISSING\"}"; exit 3; }
done
if [[ -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT ]]; then
  quota_status=$(python scripts/run_kairo_krisis.py --quota-status)
  # Preserve derived provider reset metadata for health/audit without storing
  # credentials or response content.
  python - "$quota_status" <<'PY'
import json
from pathlib import Path
path=Path('/tmp/KA_IRO_EXTERNAL_QUOTA_WAIT')
current=json.loads(path.read_text())
candidate=json.loads(__import__('sys').argv[1]).get('next_resume_utc')
if candidate:
    current['next_resume_utc']=candidate
    path.write_text(json.dumps(current,sort_keys=True)+'\n')
PY
  gate=$(python - "$quota_status" <<'PY'
import json
import sys
from datetime import datetime, timezone
v=json.loads(sys.argv[1]); when=v.get('next_resume_utc')
if not when: print('WAIT')
else:
    try: print('READY' if datetime.fromisoformat(when.replace('Z','+00:00')) <= datetime.now(timezone.utc) else 'WAIT')
    except ValueError: print('WAIT')
PY
)
  [[ "$gate" == READY ]] || { echo '{"runner":"QUOTA_WAIT"}'; exit 0; }
  rm -f /tmp/KA_IRO_EXTERNAL_QUOTA_WAIT
fi
git rev-parse -q --verify 'ka-iro-krisis-executor-v1^{}' >/dev/null || { echo '{"runner":"PRELIVE","state":"EXECUTOR_FREEZE_REQUIRED"}'; exit 0; }
exec env KAIRO_LIVE_EXECUTION_ENABLED=1 python scripts/run_kairo_krisis.py --run-until-stop
