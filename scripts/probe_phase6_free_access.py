"""Probe Phase 6 free-panel metadata without invoking model inference.

Only authenticated model-list endpoints are queried.  Credential values, raw
responses, URLs containing credentials, and unallowlisted headers are never
persisted or printed.  A successful probe proves model-list visibility only;
it cannot attest that billing is disabled or that an account is on a free tier.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "validation" / "phase6_free_v1_access_probes"
TIMEOUT_SECONDS = 20
USER_AGENT = "GeoSAVE-Research/phase6-free-v1"
ALLOWED_RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}
TARGETS = {
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/models", {"gemini-3.6-flash", "gemini-2.5-flash-lite"}),
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1/models", {"qwen/qwen3.8-27b"}),
}


def _safe_rate_headers(headers: Any) -> dict[str, str]:
    return {name.lower(): headers[name] for name in headers.keys() if name.lower() in ALLOWED_RATE_HEADERS}


def _request_json(url: str, headers: dict[str, str], opener: Callable[..., Any]) -> tuple[int, dict[str, Any], dict[str, str]]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **headers}, method="GET")
    with opener(request, timeout=TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return int(response.status), payload, _safe_rate_headers(response.headers)


def _provider_record(provider: str, secret_present: bool, secret: str | None, opener: Callable[..., Any]) -> dict[str, Any]:
    env_name, url, expected_models = TARGETS[provider]
    record: dict[str, Any] = {
        "provider": provider,
        "credential_environment": env_name,
        "credential_present": secret_present,
        "access_tier": "unverified",
        "billing_enabled": "unverified",
        "rate_limit_metadata": {},
        "metadata_http_requests_made": 0,
        "model_generation_request_made": False,
        "models": [{"model_id": model_id, "listed": False, "image_input_live_tested": False} for model_id in sorted(expected_models)],
    }
    if not secret_present:
        record["probe_status"] = "MISSING_CREDENTIAL"
        return record
    headers = {"x-goog-api-key": secret} if provider == "gemini" else {"Authorization": f"Bearer {secret}"}
    record["metadata_http_requests_made"] = 1
    try:
        status, payload, rate_headers = _request_json(url, headers, opener)
    except HTTPError as error:
        record["probe_status"] = "FREE_QUOTA_EXHAUSTED" if error.code == 429 else "HTTP_ERROR"
        record["http_status"] = int(error.code)
        record["rate_limit_metadata"] = _safe_rate_headers(error.headers) if error.headers else {}
        return record
    except (URLError, TimeoutError, OSError):
        record["probe_status"] = "TRANSPORT_ERROR"
        return record
    except (ValueError, UnicodeError):
        record["probe_status"] = "INVALID_METADATA_RESPONSE"
        return record
    record["probe_status"] = "MODEL_LIST_VISIBLE" if status == 200 else "HTTP_ERROR"
    record["http_status"] = status
    record["rate_limit_metadata"] = rate_headers
    field = "models" if provider == "gemini" else "data"
    if not isinstance(payload, dict) or not isinstance(payload.get(field), list):
        record["probe_status"] = "INVALID_METADATA_RESPONSE"
        return record
    items = payload[field]
    key = "name" if provider == "gemini" else "id"
    if any(not isinstance(item, dict) or not isinstance(item.get(key), str) for item in items):
        record["probe_status"] = "INVALID_METADATA_RESPONSE"
        return record
    listed = {item[key].removeprefix("models/") if provider == "gemini" else item[key] for item in items}
    record["models"] = [
        {"model_id": model_id, "listed": model_id in listed, "image_input_live_tested": False}
        for model_id in sorted(expected_models)
    ]
    return record


def probe(
    *, environ: dict[str, str] | None = None, opener: Callable[..., Any] = urlopen, output_dir: Path = OUTPUT_DIR
) -> dict[str, Any]:
    environment = os.environ if environ is None else environ
    timestamp = datetime.now(timezone.utc)
    providers = [
        _provider_record(provider, bool(environment.get(env_name)), environment.get(env_name), opener)
        for provider, (env_name, _, _) in TARGETS.items()
    ]
    all_models_listed = all(model["listed"] for provider in providers for model in provider["models"])
    if not all(provider["credential_present"] for provider in providers):
        execution_status = "PREFLIGHT_BLOCKED_MISSING_CREDENTIAL"
    elif not all_models_listed:
        execution_status = "PREFLIGHT_BLOCKED_PROVIDER_ACCESS"
    else:
        execution_status = "PREFLIGHT_BLOCKED_PENDING_ACCOUNT_TIER_ATTESTATION"
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    result = {
        "schema_version": "phase6-free-access-probe-v2",
        "verification_timestamp_utc": timestamp.isoformat(),
        "purpose": "metadata-only exact-model availability probe; no inference request",
        "providers": providers,
        "all_target_models_listed": all_models_listed,
        "runtime": {"system": platform.system(), "architecture": platform.machine(), "python": platform.python_version(), "source_commit": commit},
        "probe_script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "user_agent": USER_AGENT,
        "free_tier_verified": False,
        "billing_disabled_verified": False,
        "rate_limits_fully_verified": False,
        "provider_calls_made": sum(provider["metadata_http_requests_made"] for provider in providers),
        "metadata_http_requests_made": sum(provider["metadata_http_requests_made"] for provider in providers),
        "model_generation_requests_made": 0,
        "execution_status": execution_status,
        "next_required_evidence": "Authenticated account/dashboard confirmation of Free Tier or Free Plan, billing disabled, and current quota limits; then one guarded multimodal capability-pilot request per model.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"phase6_free_v1_access_probe_{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    with output_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    try:
        result["output_path"] = output_path.relative_to(ROOT).as_posix()
    except ValueError:  # Test callers may direct output outside the repository.
        result["output_path"] = str(output_path)
    return result


if __name__ == "__main__":
    result = probe()
    print(
        "Phase 6 free access probe: "
        f"models_listed={result['all_target_models_listed']}; "
        f"free_tier_verified={result['free_tier_verified']}; "
        f"metadata_requests={result['metadata_http_requests_made']}; "
        f"model_generation_requests={result['model_generation_requests_made']}."
    )
    print(f"Evidence: {result['output_path']}")
