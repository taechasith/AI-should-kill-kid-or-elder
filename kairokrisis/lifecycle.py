"""Non-scientific local lifecycle controls for restart-safe execution."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path

LOCK = Path('/tmp/ka-iro-runner.lock'); STATE = Path('/tmp/ka-iro-lifecycle.json'); HEARTBEAT_PID = Path('/tmp/ka-iro-heartbeat.pid'); SESSION = Path('/tmp/ka-iro-session.json')
LONG_WAIT_SECONDS = 25 * 60; ROLLOVER_SECONDS = int(10.5 * 60 * 60)
def now() -> str: return datetime.now(timezone.utc).isoformat()
def write(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp'); temporary.write_text(json.dumps(value, sort_keys=True) + '\n', encoding='utf-8'); os.replace(temporary, path)
def _alive(pid: int) -> bool:
    try: os.kill(pid, 0); return True
    except (ProcessLookupError, PermissionError): return False
def acquire() -> bool:
    if LOCK.exists():
        try:
            if _alive(int(json.loads(LOCK.read_text())['pid'])): return False
        except (ValueError, KeyError, json.JSONDecodeError): pass
        LOCK.unlink(missing_ok=True)
    write(LOCK, {'pid': os.getpid(), 'started_utc': now(), 'boot_id': _boot_id()}); return True
def release() -> None:
    try:
        if int(json.loads(LOCK.read_text()).get('pid', -1)) == os.getpid(): LOCK.unlink()
    except (FileNotFoundError, ValueError, json.JSONDecodeError): pass
def _boot_id() -> str:
    try: return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    except OSError: return 'unavailable'
def state(kind: str, **extra: object) -> None: write(STATE, {'state': kind, 'updated_utc': now(), **extra})
def read_state() -> dict:
    try: return json.loads(STATE.read_text())
    except (OSError, json.JSONDecodeError): return {'state': 'STOPPED'}
def session_age_seconds() -> int:
    if not SESSION.exists(): write(SESSION, {'started_utc': now()}); return 0
    try: return max(0, int((datetime.now(timezone.utc) - datetime.fromisoformat(json.loads(SESSION.read_text())['started_utc'])).total_seconds()))
    except Exception: return 0
def should_rollover() -> bool: return session_age_seconds() >= ROLLOVER_SECONDS
