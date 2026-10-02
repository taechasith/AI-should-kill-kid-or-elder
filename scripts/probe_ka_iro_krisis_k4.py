"""Append-only K4 metadata probe for the KA-IRO KRISIS v2 model panel.

This program calls provider *model-list* endpoints only.  It never sends a
generation request, never writes credentials, and persists a separate raw
metadata response plus a SHA-256 reference for every HTTP request.
"""

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
OUTPUT_ROOT = ROOT / "data" / "ka-iro-krisis" / "v2" / "model" / "k4_metadata_preflights"
TIMEOUT_SECONDS = 20
USER_AGENT = "KA-IRO-KRISIS-v2/K4-metadata-only"
SAFE_HEADERS = {
    "retry-after",
    "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
}
ROUTES = (
    ("gemini", "Google Gemini API", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/models", ("gemini-3.5-flash", "gemini-3.5-flash-lite")),
    ("groq", "Groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1/models", ("qwen/qwen3.8-27b",)),
)


def _safe_headers(headers: object) -> dict[str, str]:
    if not hasattr(headers, "keys"):
        return {}
    return {key.lower(): headers[key] for key in headers.keys() if key.lower() in SAFE_HEADERS}


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _probe(route: tuple[str, str, str, str, tuple[str, ...]], output_dir: Path) -> dict[str, object]:
    short_name, provider, env_name, url, target_models = route
    secret = os.getenv(env_name)
    result: dict[str, object] = {
        "provider": provider,
        "credential_environment": env_name,
        "credential_present": bool(secret),
        "endpoint_purpose": "model-list metadata only",
        "metadata_http_requests_made": 0,
        "model_generation_requests_made": 0,
        "target_models": [{"model_id": model_id, "listed": False} for model_id in target_models],
        "sanitized_rate_limit_headers": {},
    }
    if not secret:
        result["probe_status"] = "MISSING_CREDENTIAL"
        return result

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    headers["x-goog-api-key" if short_name == "gemini" else "Authorization"] = secret if short_name == "gemini" else f"Bearer {secret}"
    result["metadata_http_requests_made"] = 1
    try:
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw_body = response.read()
            result["http_status"] = int(response.status)
            result["sanitized_rate_limit_headers"] = _safe_headers(response.headers)
    except HTTPError as error:
        raw_body = error.read()
        result.update({
            "http_status": int(error.code),
            "sanitized_rate_limit_headers": _safe_headers(error.headers),
            "probe_status": "FREE_QUOTA_EXHAUSTED" if error.code == 429 else "HTTP_ERROR",
        })
    except (URLError, TimeoutError, OSError) as error:
        result.update({"probe_status": "TRANSPORT_OR_METADATA_ERROR", "error_class": type(error).__name__})
        return result

    raw_path = output_dir / f"{short_name}_model_list_raw.json"
    raw_path.write_bytes(raw_body)
    result["raw_response_reference"] = raw_path.relative_to(ROOT).as_posix()
    result["raw_response_sha256"] = sha256(raw_body).hexdigest()
    if result.get("http_status") != 200:
        return result
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        result["probe_status"] = "INVALID_METADATA_RESPONSE"
        return result
    collection_name, id_name = ("models", "name") if short_name == "gemini" else ("data", "id")
    collection = payload.get(collection_name) if isinstance(payload, dict) else None
    if not isinstance(collection, list):
        result["probe_status"] = "INVALID_METADATA_RESPONSE"
        return result
    listed = {
        row[id_name].removeprefix("models/") if short_name == "gemini" else row[id_name]
        for row in collection
        if isinstance(row, dict) and isinstance(row.get(id_name), str)
    }
    result["target_models"] = [{"model_id": model_id, "listed": model_id in listed} for model_id in target_models]
    result["probe_status"] = "MODEL_LIST_VISIBLE"
    return result


def main() -> None:
    timestamp = datetime.now(timezone.utc)
    output_dir = OUTPUT_ROOT / timestamp.strftime("%Y%m%dT%H%M%S%fZ")
    output_dir.mkdir(parents=True, exist_ok=False)
    providers = [_probe(route, output_dir) for route in ROUTES]
    all_target_models_listed = all(
        row["listed"] for provider in providers for row in provider["target_models"]
    )
    evidence = {
        "schema_version": "ka-iro-krisis-v2-k4-metadata-preflight-v1",
        "project_id": "ka-iro-krisis-v2",
        "gate": "K4",
        "verification_timestamp_utc": timestamp.isoformat(),
        "purpose": "authenticated metadata-only exact-model availability probe; no inference request",
        "providers": providers,
        "all_target_models_listed": all_target_models_listed,
        "account_plan_and_billing": "NOT_INFERRED_BY_METADATA_PROBE",
        "metadata_http_requests_made": sum(int(provider["metadata_http_requests_made"]) for provider in providers),
        "model_generation_requests_made": 0,
        "runtime_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "next_required_evidence": "Record current non-secret account-plan and billing-disabled attestation before freezing K4 or sending a generation request.",
    }
    _write_json(output_dir / "k4_metadata_preflight.json", evidence)
    print(json.dumps({
        "all_target_models_listed": all_target_models_listed,
        "metadata_http_requests_made": evidence["metadata_http_requests_made"],
        "model_generation_requests_made": 0,
        "evidence": (output_dir / "k4_metadata_preflight.json").relative_to(ROOT).as_posix(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
