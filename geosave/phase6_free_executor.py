"""Fail-closed execution helpers for the three-call Phase 6 free pilot.

This module deliberately accepts a sender callback so that every persistence and
failure path can be tested without network access.  The command wrapper is the
only component that constructs authenticated HTTP requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .phase6_free_guard import FreeOnlyExecutionGuard, PILOT_PURPOSE
from .phase6_interface import (
    canonical_json_bytes,
    normalized_record,
    parse_phase6_response,
    persist_normalized_record,
    persist_raw_response,
)


class Phase6PilotError(RuntimeError):
    """Raised when the bounded free pilot cannot proceed safely."""


@dataclass(frozen=True)
class AccountAttestation:
    verification_timestamp_utc: str
    provider_access: Mapping[str, Mapping[str, Any]]
    source: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AccountAttestation":
        expected = {"schema_version", "verification_timestamp_utc", "source", "providers"}
        if set(value) != expected or value["schema_version"] != "phase6-free-account-attestation-v1":
            raise Phase6PilotError("account attestation schema is invalid")
        if not isinstance(value["verification_timestamp_utc"], str) or not value["verification_timestamp_utc"]:
            raise Phase6PilotError("account attestation timestamp is required")
        if not isinstance(value["source"], str) or not value["source"]:
            raise Phase6PilotError("account attestation source is required")
        providers = value["providers"]
        if not isinstance(providers, list):
            raise Phase6PilotError("account attestation providers must be a list")
        parsed: dict[str, Mapping[str, Any]] = {}
        for provider in providers:
            if not isinstance(provider, Mapping) or set(provider) != {"provider", "access_tier", "billing_enabled", "quota_available", "verified_model_ids"}:
                raise Phase6PilotError("account attestation provider fields are invalid")
            provider_id = provider["provider"]
            if provider_id not in {"gemini", "groq"} or provider_id in parsed:
                raise Phase6PilotError("account attestation provider is invalid or duplicated")
            if provider["access_tier"] not in {"free_tier", "free_plan"}:
                raise Phase6PilotError("account attestation must explicitly confirm free access")
            if provider["billing_enabled"] is not False or provider["quota_available"] is not True:
                raise Phase6PilotError("account attestation must confirm billing disabled and free quota available")
            models = provider["verified_model_ids"]
            if not isinstance(models, list) or not models or any(not isinstance(model, str) for model in models):
                raise Phase6PilotError("account attestation must list verified model IDs")
            parsed[provider_id] = dict(provider)
        if set(parsed) != {"gemini", "groq"}:
            raise Phase6PilotError("account attestation must cover Gemini and Groq")
        return cls(value["verification_timestamp_utc"], parsed, value["source"])

    def provider(self, provider: str, model_id: str) -> Mapping[str, Any]:
        details = self.provider_access[provider]
        if model_id not in details["verified_model_ids"]:
            raise Phase6PilotError(f"account attestation does not verify {provider}/{model_id}")
        return details


def load_attestation(path: Path) -> tuple[AccountAttestation, str]:
    payload = path.read_bytes()
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as error:
        raise Phase6PilotError("account attestation is not valid JSON") from error
    if not isinstance(decoded, Mapping):
        raise Phase6PilotError("account attestation must be an object")
    return AccountAttestation.from_mapping(decoded), sha256(payload).hexdigest()


def _write_once_json(path: Path, value: Mapping[str, Any]) -> str:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_bytes(dict(value))
    with path.open("xb") as handle:
        handle.write(payload)
    return sha256(payload).hexdigest()


def pilot_result_path(root: Path, run_id: str) -> Path:
    return root / "attempts" / f"{run_id}.json"


def _extract_provider_text(provider: str, raw_response: str) -> str:
    """Extract provider-generated text from a retained raw response envelope."""
    try:
        payload = json.loads(raw_response)
        if provider == "gemini":
            candidates = payload["candidates"]
            parts = candidates[0]["content"]["parts"]
            text = "".join(part["text"] for part in parts if isinstance(part.get("text"), str))
        elif provider == "groq":
            text = payload["choices"][0]["message"]["content"]
        else:
            raise KeyError(provider)
    except (TypeError, KeyError, IndexError, json.JSONDecodeError) as error:
        raise Phase6PilotError("provider response does not contain a text candidate") from error
    if not isinstance(text, str) or not text:
        raise Phase6PilotError("provider response text is missing")
    return text


def execute_pilot_row(
    *,
    row: Mapping[str, Any],
    provider: str,
    policy: Mapping[str, Any],
    registry_status: str,
    credential_present: bool,
    attestation: AccountAttestation,
    attestation_sha256: str,
    source_commit: str,
    raw_root: Path,
    normalized_root: Path,
    attempt_root: Path,
    repository_root: Path | None = None,
    send: Callable[[], tuple[int, str, Mapping[str, str]]],
) -> Mapping[str, Any]:
    """Perform exactly one guarded request for one pilot row.

    A provider error is preserved as a failure record.  A successful HTTP
    response is stored raw before parsing; neither output can be overwritten.
    """
    run_id = str(row["run_id"])
    output_path = pilot_result_path(attempt_root, run_id)
    if output_path.exists():
        raise Phase6PilotError(f"pilot run already has an append-only result: {run_id}")
    account = attestation.provider(provider, str(row["model_id"]))
    guard = FreeOnlyExecutionGuard.from_policy(policy, registry_status)
    guard.assert_request_permitted(
        provider=provider,
        model_id=str(row["model_id"]),
        purpose=PILOT_PURPOSE,
        credential_present=credential_present,
        access_tier=str(account["access_tier"]),
        billing_enabled=bool(account["billing_enabled"]),
        rate_limit_verified=bool(account["quota_available"]),
    )
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        http_status, raw, response_headers = send()
    except Exception as error:  # Sender deliberately hides credential material.
        result = {
            "schema_version": "phase6-free-pilot-attempt-v1",
            "run_id": run_id,
            "provider": provider,
            "model_id": row["model_id"],
            "attempt_timestamp_utc": timestamp,
            "status": "failed",
            "failure_reason": "TRANSPORT_ERROR",
            "http_status": None,
            "raw_response_reference": None,
            "normalized_response_reference": None,
            "attestation_sha256": attestation_sha256,
            "source_commit": source_commit,
        }
        _write_once_json(output_path, result)
        return result
    if http_status != 200:
        result = {
            "schema_version": "phase6-free-pilot-attempt-v1",
            "run_id": run_id,
            "provider": provider,
            "model_id": row["model_id"],
            "attempt_timestamp_utc": timestamp,
            "status": "failed",
            "failure_reason": "FREE_QUOTA_EXHAUSTED" if http_status == 429 else "PROVIDER_HTTP_ERROR",
            "http_status": http_status,
            "raw_response_reference": None,
            "normalized_response_reference": None,
            "response_rate_limit_headers": {key: value for key, value in response_headers.items() if key.lower().startswith("x-ratelimit") or key.lower() == "retry-after"},
            "attestation_sha256": attestation_sha256,
            "source_commit": source_commit,
        }
        _write_once_json(output_path, result)
        return result
    raw_path = raw_root / f"{run_id}.txt"
    raw_sha256 = persist_raw_response(raw_path, raw)
    try:
        model_text = _extract_provider_text(provider, raw)
        parsed = parse_phase6_response(model_text)
    except Phase6PilotError as error:
        parsed = parse_phase6_response("")
        parsed = parsed.__class__("failed", None, str(error), False)
    normalized_path = normalized_root / f"{run_id}.json"
    raw_reference = raw_path.relative_to(repository_root).as_posix() if repository_root else raw_path.as_posix()
    normalized_reference = normalized_path.relative_to(repository_root).as_posix() if repository_root else normalized_path.as_posix()
    normalized = normalized_record(
        run_id=run_id,
        model_id=str(row["model_id"]),
        model_revision=str(row["model_revision"]),
        prompt_version="phase6-decision-prompt-v1",
        condition=str(row["condition"]),
        input_package_id=str(row["input_package_id"]),
        country_iso3=row["country_iso3"],
        law_snapshot="phase5-legal-snapshot-v1",
        action_order=tuple(row["action_order"]),
        raw_response_reference=raw_reference,
        result=parsed,
    )
    normalized_sha256 = persist_normalized_record(normalized_path, normalized)
    result = {
        "schema_version": "phase6-free-pilot-attempt-v1",
        "run_id": run_id,
        "provider": provider,
        "model_id": row["model_id"],
        "attempt_timestamp_utc": timestamp,
        "status": "completed" if parsed.status in {"valid", "repaired"} else "failed",
        "failure_reason": None if parsed.status in {"valid", "repaired"} else "MALFORMED_RESPONSE",
        "http_status": http_status,
        "raw_response_reference": raw_reference,
        "raw_response_sha256": raw_sha256,
        "normalized_response_reference": normalized_reference,
        "normalized_response_sha256": normalized_sha256,
        "parse_status": parsed.status,
        "response_rate_limit_headers": {key: value for key, value in response_headers.items() if key.lower().startswith("x-ratelimit") or key.lower() == "retry-after"},
        "attestation_sha256": attestation_sha256,
        "source_commit": source_commit,
    }
    _write_once_json(output_path, result)
    return result
