"""KA-IRO KRISIS append-only execution core.

This module deliberately uses only :mod:`urllib`: one invocation of
``dispatch_once`` is one HTTP attempt. Scheduling/retries are explicit ledger
concerns, never an SDK or transport convenience feature.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}
RETRYABLE_HTTP = {429, 500, 502, 503, 504}
TERMINAL_STATES = {"VALID_ACTION", "VALID_RESPONSE_NO_ALLOWLISTED_ACTION", "INVALID_STRUCTURED_OUTPUT", "REFUSAL", "CONTENT_BLOCKED", "NON_RETRYABLE_PROVIDER_ERROR", "RETRY_EXHAUSTED", "AMBIGUOUS_TRANSPORT_OUTCOME"}
VALID_ACTIONS = {"A0", "A1", "A2", "A3", "A4", "A6"}
MAX_TRANSIENT_ATTEMPTS = 3


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic(path: Path, data: bytes, *, replace: bool = True) -> None:
    """Durably write ``path``; immutable artifacts reject replacement."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not replace and path.exists():
        raise RuntimeError(f"IMMUTABLE_ARTIFACT_EXISTS:{path}")
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = handle.name
    os.replace(temporary, path)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_headers(headers: Any) -> dict[str, str]:
    return {str(k).lower(): str(v) for k, v in headers.items() if str(k).lower() in RATE_HEADERS}


def _response_text(raw: bytes) -> str | None:
    try:
        document = json.loads(raw)
        if "choices" in document:
            return document.get("choices", [{}])[0].get("message", {}).get("content")
        parts = document.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return None


def classify(status: int | None, raw: bytes, transport: str = "HTTP_RESPONSE") -> tuple[str, bool]:
    """Return terminal ontology state and whether it ends this observation."""
    if status is None:
        return ("TRANSIENT_TRANSPORT_FAILURE", False) if transport == "KNOWN_NOT_ACCEPTED" else ("AMBIGUOUS_TRANSPORT_OUTCOME", True)
    if status != 200:
        text = raw.decode("utf-8", errors="replace").lower()
        if status == 429:
            return ("FREE_QUOTA_EXHAUSTED", False) if any(token in text for token in ("quota_exceeded", "perday", "daily", "per_day")) else ("TRANSIENT_RATE_LIMIT", False)
        return "NON_RETRYABLE_PROVIDER_ERROR", status not in RETRYABLE_HTTP
    text = _response_text(raw)
    if not isinstance(text, str):
        return "INVALID_STRUCTURED_OUTPUT", True
    lowered = text.lower()
    if any(token in lowered for token in ("content blocked", "safety blocked", "content_blocked")):
        return "CONTENT_BLOCKED", True
    if any(token in lowered for token in ("cannot assist", "i cannot", "i can't", "refuse")):
        return "REFUSAL", True
    try:
        action = json.loads(text).get("selected_action_id")
    except (TypeError, json.JSONDecodeError):
        return "INVALID_STRUCTURED_OUTPUT", True
    return ("VALID_ACTION", True) if action in VALID_ACTIONS else ("VALID_RESPONSE_NO_ALLOWLISTED_ACTION", True)


class Ledger:
    """Append-only attempt/raw artifacts plus replaceable current observation state."""
    def __init__(self, root: Path, *, max_transient_attempts: int = MAX_TRANSIENT_ATTEMPTS):
        self.root, self.max_transient_attempts = root, max_transient_attempts

    def attempts(self, observation_id: str) -> list[Path]:
        return sorted((self.root / "attempts" / observation_id).glob("attempt_*.json"))

    def records(self, observation_id: str) -> list[dict[str, Any]]:
        return [load(path) for path in self.attempts(observation_id)]

    def state_path(self, observation_id: str) -> Path:
        return self.root / "observations" / f"{observation_id}.json"

    def state(self, observation_id: str) -> dict[str, Any]:
        path = self.state_path(observation_id)
        return load(path) if path.exists() else {"observation_id": observation_id, "state": "PLANNED"}

    def terminal(self, observation_id: str) -> bool:
        return self.state(observation_id).get("state") == "TERMINAL"

    def mark_state(self, observation_id: str, state: str, **extra: Any) -> dict[str, Any]:
        value = {"observation_id": observation_id, "state": state, "updated_at_utc": utcnow(), **extra}
        atomic(self.state_path(observation_id), canon(value))
        return value

    def inflight(self, observation_id: str | None = None) -> list[Path]:
        return sorted((self.root / "inflight").glob(f"{observation_id}__*.json" if observation_id else "*.json"))

    def recover(self) -> list[str]:
        """Persist unresolved in-flight dispatches as terminal ambiguity; never replay."""
        recovered: list[str] = []
        for token_path in self.inflight():
            token = load(token_path)
            oid, ordinal = token["observation_id"], token["attempt_number"]
            attempt_path = self.root / "attempts" / oid / f"attempt_{ordinal:04}.json"
            if not attempt_path.exists():
                record = {"schema_version": "ka-iro-krisis-attempt-v1", "observation_id": oid, "attempt_number": ordinal, "phase": token["phase"], "provider": token["provider"], "model_id": token["model_id"], "request_timestamp_utc": token["started_at_utc"], "response_timestamp_utc": None, "http_status": None, "raw_response_reference": None, "raw_response_sha256": None, "rate_limit_headers": {}, "transport_result": "AMBIGUOUS_TRANSPORT_OUTCOME", "parsed_terminal_state": "AMBIGUOUS_TRANSPORT_OUTCOME", "terminal": True, "retry_permitted": False, "recovery_reason": "process_interrupted_after_attempt_started"}
                atomic(attempt_path, canon(record), replace=False)
                terminal_state = "AMBIGUOUS_TRANSPORT_OUTCOME"
            else:
                record = load(attempt_path)
                # A durable response and finalized ledger can be parsed offline after a crash.
                raw_ref = record.get("raw_response_reference")
                if raw_ref and Path(raw_ref).exists():
                    terminal_state, _ = classify(record.get("http_status"), Path(raw_ref).read_bytes(), record.get("transport_result", "HTTP_RESPONSE"))
                else:
                    terminal_state = record.get("parsed_terminal_state", "AMBIGUOUS_TRANSPORT_OUTCOME")
            self.mark_state(oid, "TERMINAL", attempt_number=ordinal, terminal_state=terminal_state)
            token_path.unlink()
            recovered.append(oid)
        # Parser completed before an interruption: promote its durable result without redispatch.
        for path in (self.root / "observations").glob("*.json"):
            current = load(path)
            if current.get("state") == "PARSED":
                self.mark_state(current["observation_id"], "TERMINAL",
                                attempt_number=current.get("attempt_number"),
                                terminal_state=current.get("terminal_state"))
                recovered.append(current["observation_id"])
        return recovered

    def start(self, row: dict[str, Any]) -> int | None:
        oid = row["observation_id"]
        if self.terminal(oid): return None
        if self.inflight(oid): raise RuntimeError("AMBIGUOUS_TRANSPORT_OUTCOME: unresolved in-flight attempt")
        if self.state(oid).get("state") == "AMBIGUOUS_TRANSPORT_OUTCOME": raise RuntimeError("AMBIGUOUS_TRANSPORT_OUTCOME: replay prohibited")
        ordinal = len(self.attempts(oid)) + 1
        token = {"observation_id": oid, "attempt_number": ordinal, "phase": row["phase"], "provider": row["provider"], "model_id": row["model_id"], "started_at_utc": utcnow()}
        atomic(self.root / "inflight" / f"{oid}__{ordinal:04}.json", canon(token), replace=False)
        self.mark_state(oid, "ATTEMPT_STARTED", attempt_number=ordinal)
        return ordinal

    def finalize(self, row: dict[str, Any], ordinal: int, status: int | None, raw: bytes, headers: dict[str, str], transport: str = "HTTP_RESPONSE", *, crash_at: str | None = None) -> dict[str, Any]:
        """Finalize one explicit attempt. ``crash_at`` exists solely for mocked recovery tests."""
        oid, start_state = row["observation_id"], self.state(row["observation_id"])
        if crash_at == "after_started": raise RuntimeError("SIMULATED_CRASH_AFTER_ATTEMPT_STARTED")
        raw_path: Path | None = None
        if raw:
            raw_path = self.root / "raw" / oid / f"attempt_{ordinal:04}.json"
            atomic(raw_path, raw, replace=False)
        self.mark_state(oid, "RAW_RESPONSE_DURABLE", attempt_number=ordinal)
        if crash_at == "after_raw": raise RuntimeError("SIMULATED_CRASH_AFTER_RAW_RESPONSE_DURABLE")
        classification, terminal = classify(status, raw, transport)
        retry_permitted = not terminal and classification != "FREE_QUOTA_EXHAUSTED" and ordinal < self.max_transient_attempts
        if not terminal and classification != "FREE_QUOTA_EXHAUSTED" and not retry_permitted:
            classification, terminal = "RETRY_EXHAUSTED", True
        record = {"schema_version": "ka-iro-krisis-attempt-v1", "observation_id": oid, "attempt_number": ordinal, "phase": row["phase"], "provider": row["provider"], "model_id": row["model_id"], "request_timestamp_utc": start_state.get("updated_at_utc"), "response_timestamp_utc": utcnow(), "http_status": status, "raw_response_reference": str(raw_path) if raw_path else None, "raw_response_sha256": sha(raw) if raw else None, "rate_limit_headers": safe_headers(headers), "transport_result": transport, "parsed_terminal_state": classification, "terminal": terminal, "retry_permitted": retry_permitted, "planning_object_sha256": row.get("planning_object_sha256", row.get("final_request_payload_sha256")), "request_body_sha256": row.get("request_body_sha256"), "prompt_hash": row.get("prompt_sha256"), "input_hash": row.get("input_sha256")}
        atomic(self.root / "attempts" / oid / f"attempt_{ordinal:04}.json", canon(record), replace=False)
        self.mark_state(oid, "ATTEMPT_FINALIZED", attempt_number=ordinal)
        if crash_at == "after_finalized": raise RuntimeError("SIMULATED_CRASH_AFTER_ATTEMPT_FINALIZED")
        for token in self.inflight(oid): token.unlink()
        if terminal:
            self.mark_state(oid, "PARSED", attempt_number=ordinal, terminal_state=classification)
            if crash_at == "after_parsed": raise RuntimeError("SIMULATED_CRASH_AFTER_PARSED")
            self.mark_state(oid, "TERMINAL", attempt_number=ordinal, terminal_state=classification)
        elif classification == "FREE_QUOTA_EXHAUSTED":
            self.mark_state(oid, "QUOTA_DEFERRED", attempt_number=ordinal, next_eligible_utc=None, rate_limit_headers=safe_headers(headers))
        else:
            self.mark_state(oid, "RETRY_DEFERRED", attempt_number=ordinal)
        return record


def verify(row: dict[str, Any], repository_root: Path) -> None:
    asset = repository_root / row["input_asset_path"]
    if not asset.is_file() or sha(asset.read_bytes()) != row["input_sha256"]: raise RuntimeError("FROZEN_PAYLOAD_INTEGRITY_FAILURE:input")
    if sha(row["prompt_template"].encode("utf-8")) != row["prompt_sha256"]: raise RuntimeError("FROZEN_PAYLOAD_INTEGRITY_FAILURE:prompt")
    if row.get("phase") not in {"K5", "K6"}: raise RuntimeError("FROZEN_PAYLOAD_INTEGRITY_FAILURE:phase")


def dispatch_once(url: str, headers: dict[str, str], body: bytes, timeout: int = 180) -> tuple[int | None, bytes, dict[str, str], str]:
    """Exactly one urllib request; there is intentionally no retry wrapper."""
    try:
        with urlopen(Request(url, data=body, headers=headers, method="POST"), timeout=timeout) as response:
            return response.status, response.read(), safe_headers(response.headers), "HTTP_RESPONSE"
    except HTTPError as error:
        return error.code, error.read(), safe_headers(error.headers), "HTTP_RESPONSE"
    except URLError:
        return None, b"", {}, "KNOWN_NOT_ACCEPTED"
    except (TimeoutError, OSError):
        return None, b"", {}, "AMBIGUOUS_TRANSPORT_OUTCOME"


def authenticated_headers(provider: str) -> dict[str, str]:
    """Inject runtime-only authentication after frozen body/envelope verification."""
    if provider == "Google Gemini API":
        key = os.environ.get("GEMINI_API_KEY")
        if not key: raise RuntimeError("MISSING_GEMINI_API_KEY")
        return {"content-type": "application/json", "x-goog-api-key": key}
    key = os.environ.get("GROQ_API_KEY")
    if not key: raise RuntimeError("MISSING_GROQ_API_KEY")
    return {"content-type": "application/json", "authorization": "Bearer " + key}
