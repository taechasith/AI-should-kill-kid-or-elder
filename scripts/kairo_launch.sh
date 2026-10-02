#!/usr/bin/env bash
# Small remote launcher: supervisor never embeds nontrivial shell syntax.
set -euo pipefail
ROOT=/workspaces/ka-iro-krisis-v2-codespace
cd "$ROOT"
if [[ -f /tmp/ka-iro-autonomous.pid ]] && kill -0 "$(< /tmp/ka-iro-autonomous.pid)" 2>/dev/null; then exit 0; fi
flock -n /tmp/ka-iro-launch.lock bash -c 'nohup bash scripts/kairo_resume.sh >/tmp/ka-iro-autonomous.log 2>&1 & echo $! >/tmp/ka-iro-autonomous.pid' || true
