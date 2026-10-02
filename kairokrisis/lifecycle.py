"""Non-scientific local lifecycle controls for restart-safe execution."""
from __future__ import annotations
import json, os, signal, subprocess
from datetime import datetime, timezone
from pathlib import Path

LOCK = Path('/tmp/ka-iro-runner.lock'); STATE = Path('/tmp/ka-iro-lifecycle.json'); HEARTBEAT_PID = Path('/tmp/ka-iro-heartbeat.pid'); SESSION = Path('/tmp/ka-iro-session.json'); QUOTA_WAIT = Path('/tmp/KA_IRO_EXTERNAL_QUOTA_WAIT'); ROLLOVER = Path('/tmp/KA_IRO_NEEDS_RESTART')
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
def set_quota_wait(next_resume_utc: str | None, provider: str) -> None:
    write(QUOTA_WAIT, {'state':'EXTERNAL_QUOTA_WAIT_REQUIRED','provider':provider,'next_resume_utc':next_resume_utc,'updated_utc':now()})
    state('QUOTA_WAIT', provider=provider, next_resume_utc=next_resume_utc)
def clear_quota_wait() -> None: QUOTA_WAIT.unlink(missing_ok=True)
def set_rollover(phase: str) -> None:
    write(ROLLOVER, {'state':'CODESPACE_ROLLOVER_REQUIRED','phase':phase,'updated_utc':now()}); state('ROLLOVER', phase=phase)
def heartbeat_start(repo: Path) -> int | None:
    if HEARTBEAT_PID.exists():
        try:
            existing=int(HEARTBEAT_PID.read_text().strip())
            if _alive(existing):
                command=subprocess.check_output(['ps','-p',str(existing),'-o','args='],text=True).strip()
                if str(os.getpid()) in command: return None
                os.kill(existing, signal.SIGTERM)
        except ValueError: pass
        HEARTBEAT_PID.unlink(missing_ok=True)
    proc=subprocess.Popen(['/tmp/ka-iro-heartbeat.sh',str(os.getpid())], cwd=repo, stdout=None, stderr=None, start_new_session=True)
    return proc.pid
def heartbeat_stop() -> None:
    try:
        pid=int(HEARTBEAT_PID.read_text().strip())
        if _alive(pid): os.kill(pid, signal.SIGTERM)
    except (FileNotFoundError,ValueError): pass
    HEARTBEAT_PID.unlink(missing_ok=True)
