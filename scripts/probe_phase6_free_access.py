"""Probe Phase 6 free-panel metadata without invoking model inference.

Only authenticated model-list endpoints are queried.  Credential values, raw
responses, URLs containing credentials, and unallowlisted headers are never
persisted or printed.  A successful probe proves model-list visibility only;
it cannot attest that billing is disabled or that an account is on a free tier.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "validation" / "phase6_free_v1_access_probes"
TIMEOUT_SECONDS = 20
ALLOWED_RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}
TARGETS = {
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/models", {"gemini-3.6-flash", "gemini-2.5-flash-lite"}),
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1/models", {"qwen/qwen3.8-27b"}),
}


def _safe_rate_headers(headers: Any) -> dict[str, str]:
    return {name.lower(): headers[name] for name in headers.keys() if name.lower() in ALLOWED_RATE_HEADERS}


def _request_json(url: str, headers: dict[str, str], opener: Callable[..., Any]) -> tuple[int, dict[str, Any], dict[str, str]]:
    request = Request(url, headers=headers, method="GET")
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
        "model_generation_request_made": False,
        "models": [{"model_id": model_id, "listed": False, "image_input_live_tested": False} for model_id in sorted(expected_models)],
    }
    if not secret_present:
        record["probe_status"] = "MISSING_CREDENTIAL"
        return record
    headers = {"x-goog-api-key": secret} if provider == "gemini" else {"Authorization": f"Bearer {secret}"}
    try:
        status, payload, rate_headers = _request_json(url, headers, opener)
    except HTTPError as error:
        record["probe_status"] = "HTTP_ERROR"
        record["http_status"] = int(error.code)
        return record
    except (URLError, TimeoutError, OSError):
        record["probe_status"] = "TRANSPORT_ERROR"
        return record
    record["probe_status"] = "MODEL_LIST_VISIBLE" if status == 200 else "HTTP_ERROR"
    record["http_status"] = status
    record["rate_limit_metadata"] = rate_headers
    listed = {item.get("name", "").removeprefix("models/") for item in payload.get("models", [])} if provider == "gemini" else {item.get("id", "") for item in payload.get("data", [])}
    record["models"] = [
        {"model_id": model_id, "listed": model_id in listed, "image_input_live_tested": False}
        for model_id in sorted(expected_models)
    ]
    return record


def probe(
    *, environ: dict[str, str] | None = None, opener: Callable[..., Any] = urlopen, output_dir: Path = OUTPUT_DIR
) -> dict[str, Any]:
    environment = os.environ if environ is None else environ
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    providers = [
        _provider_record(provider, bool(environment.get(env_name)), environment.get(env_name), opener)
        for provider, (env_name, _, _) in TARGETS.items()
    ]
    result = {
        "schema_version": "phase6-free-access-probe-v1",
        "verification_timestamp_utc": timestamp.isoformat(),
        "purpose": "metadata-only exact-model availability probe; no inference request",
        "providers": providers,
        "all_target_models_listed": all(model["listed"] for provider in providers for model in provider["models"]),
        "free_tier_verified": False,
        "billing_disabled_verified": False,
        "rate_limits_fully_verified": False,
        "provider_calls_made": 0,
        "model_generation_requests_made": 0,
        "execution_status": "PREFLIGHT_BLOCKED_PENDING_ACCOUNT_TIER_ATTESTATION",
        "next_required_evidence": "Authenticated account/dashboard confirmation of Free Tier or Free Plan, billing disabled, and current quota limits; then one guarded multimodal capability-pilot request per model.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"phase6_free_v1_access_probe_{timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite prior access-probe evidence: {output_path}")
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        f"model_generation_requests={result['model_generation_requests_made']}."
    )
