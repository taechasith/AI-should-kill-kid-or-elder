"""Record non-generative exact-model visibility for the Phase 6 v2 panel."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_literature_v2_candidate_registry.json"
OUTPUT_DIR = ROOT / "data" / "validation" / "phase6_literature_v2_access_probes"
TIMEOUT_SECONDS = 20
USER_AGENT = "GeoSAVE-Research/phase6-literature-v2"
RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}


def _safe_headers(headers: object) -> dict[str, str]:
    if not hasattr(headers, "keys"):
        return {}
    return {name.lower(): headers[name] for name in headers.keys() if name.lower() in RATE_HEADERS}


def _load_targets() -> dict[str, set[str]]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    targets: dict[str, set[str]] = {"gemini": set(), "groq": set()}
    for row in registry["models"]:
        targets["gemini" if row["provider"] == "Google Gemini API" else "groq"].add(row["model_id"])
    return targets


def _probe_provider(provider: str, models: set[str]) -> dict[str, object]:
    env_name = "GEMINI_API_KEY" if provider == "gemini" else "GROQ_API_KEY"
    secret = os.getenv(env_name)
    row: dict[str, object] = {"provider": provider, "credential_environment": env_name, "credential_present": bool(secret), "metadata_http_requests_made": 0, "model_generation_requests_made": 0, "models": [{"model_id": value, "listed": False} for value in sorted(models)], "rate_limit_metadata": {}}
    if not secret:
        row["probe_status"] = "MISSING_CREDENTIAL"
        return row
    url = "https://generativelanguage.googleapis.com/v1beta/models" if provider == "gemini" else "https://api.groq.com/openai/v1/models"
    auth = {"x-goog-api-key": secret} if provider == "gemini" else {"Authorization": f"Bearer {secret}"}
    row["metadata_http_requests_made"] = 1
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **auth}, method="GET")
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
            row["http_status"] = int(response.status)
            row["rate_limit_metadata"] = _safe_headers(response.headers)
    except HTTPError as error:
        row.update({"probe_status": "FREE_QUOTA_EXHAUSTED" if error.code == 429 else "HTTP_ERROR", "http_status": int(error.code), "rate_limit_metadata": _safe_headers(error.headers)})
        return row
    except (URLError, TimeoutError, OSError, ValueError, UnicodeError):
        row["probe_status"] = "TRANSPORT_OR_METADATA_ERROR"
        return row
    field, key = ("models", "name") if provider == "gemini" else ("data", "id")
    items = payload.get(field) if isinstance(payload, dict) else None
    if not isinstance(items, list):
        row["probe_status"] = "INVALID_METADATA_RESPONSE"
        return row
    available = {item[key].removeprefix("models/") if provider == "gemini" else item[key] for item in items if isinstance(item, dict) and isinstance(item.get(key), str)}
    row["models"] = [{"model_id": value, "listed": value in available} for value in sorted(models)]
    row["probe_status"] = "MODEL_LIST_VISIBLE"
    return row


def main() -> None:
    timestamp = datetime.now(timezone.utc)
    targets = _load_targets()
    providers = [_probe_provider(provider, targets[provider]) for provider in ("gemini", "groq")]
    all_listed = all(model["listed"] for provider in providers for model in provider["models"])
    result = {"schema_version": "phase6-literature-v2-access-probe-v1", "verification_timestamp_utc": timestamp.isoformat(), "purpose": "metadata-only exact-model availability probe; no inference request", "candidate_registry": REGISTRY_PATH.relative_to(ROOT).as_posix(), "providers": providers, "all_target_models_listed": all_listed, "account_tier_and_billing": "not inferred by metadata probe; prior user attestation remains separate evidence", "metadata_http_requests_made": sum(int(provider["metadata_http_requests_made"]) for provider in providers), "model_generation_requests_made": 0, "runtime_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(), "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(), "next_required_evidence": "If all models are visible, freeze the access evidence and obtain the explicit v2 pilot authorization required by the frozen v2 experiment config."}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"phase6_literature_v2_access_probe_{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"Phase 6 literature-v2 access probe: models_listed={all_listed}; metadata_requests={result['metadata_http_requests_made']}; model_generation_requests=0")
    print(f"Evidence: {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
