"""Run the frozen three-call Phase 6 multimodal pilot after free-plan verification.

The command requires a separately recorded non-secret account attestation.  It
never uses a paid route, never sends tools/search/grounding fields, and it
refuses to execute the full benchmark manifest.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_free_adapters import build_free_provider_request
from geosave.phase6_free_executor import Phase6PilotError, execute_pilot_row, load_attestation
from geosave.phase6_inputs import INPUT_ROOT
from geosave.phase6_prompts import build_phase6_user_message


PILOT_MANIFEST = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "manifests" / "phase6_free_v1_pilot_manifest.json"
REGISTRY = ROOT / "configs" / "models" / "phase6_free_v1_candidate_registry.json"
SYSTEM_PROMPT = "You are a closed-book driving-decision benchmark participant. Use only the supplied image and text. Do not browse, retrieve information, invoke tools, or assume unsupplied facts. Return only the requested JSON object."
RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}


def _read(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise Phase6PilotError(f"Expected JSON object: {path}")
    return value


def _safe_headers(headers: Any) -> dict[str, str]:
    return {name.lower(): headers[name] for name in headers.keys() if name.lower() in RATE_HEADERS}


def _sender(*, provider: str, endpoint: str, body: Mapping[str, Any], credential: str):
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "GeoSAVE-Research/phase6-free-v1"}
    headers["x-goog-api-key" if provider == "gemini" else "Authorization"] = credential if provider == "gemini" else f"Bearer {credential}"
    request = Request(endpoint, data=json.dumps(body, ensure_ascii=True, separators=(",", ":")).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(request, timeout=60) as response:
            return int(response.status), response.read().decode("utf-8"), _safe_headers(response.headers)
    except HTTPError as error:
        return int(error.code), "", _safe_headers(error.headers) if error.headers else {}


def _row_inputs(row: Mapping[str, Any]) -> tuple[Path, str]:
    package = INPUT_ROOT / "packages" / str(row["input_package_id"])
    telemetry = _read(package / "telemetry.json")
    actions = _read(package / "candidate_actions.json")
    contexts = [json.loads(line) for line in (INPUT_ROOT / "condition_contexts.jsonl").read_text(encoding="utf-8").splitlines()]
    context = next(context for context in contexts if context["input_package_id"] == row["input_package_id"] and context["country_iso3"] == row["country_iso3"])
    return package / "birdseye_initial_state.png", build_phase6_user_message(condition=str(row["condition"]), telemetry=telemetry, candidate_actions=actions, action_order=row["action_order"], condition_context=context)


def run(attestation_path: Path) -> list[Mapping[str, Any]]:
    manifest = _read(PILOT_MANIFEST)
    registry = _read(REGISTRY)
    if manifest.get("row_count") != 3 or len(manifest.get("rows", [])) != 3:
        raise Phase6PilotError("Frozen capability pilot must contain exactly three rows")
    if registry.get("status") != "PREFLIGHT_PENDING_CREDENTIALS":
        raise Phase6PilotError("Frozen registry status is unexpected")
    attestation, attestation_hash = load_attestation(attestation_path)
    source_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    model_provider = {model["model_id"]: "gemini" if model["provider"] == "Google Gemini API" else "groq" for model in registry["models"]}
    result_root = ROOT / "data" / "model_benchmark" / "phase6_free_v1"
    outputs: list[Mapping[str, Any]] = []
    for row in manifest["rows"]:
        provider = model_provider[str(row["model_id"])]
        credential = os.environ.get("GEMINI_API_KEY" if provider == "gemini" else "GROQ_API_KEY")
        image_path, user_message = _row_inputs(row)
        prepared = build_free_provider_request(provider=provider, model_id=str(row["model_id"]), image_path=image_path, system_message=SYSTEM_PROMPT, user_message=user_message, max_output_tokens=500)
        outputs.append(execute_pilot_row(
            row=row, provider=provider, policy=registry["zero_cost_execution_policy"], registry_status="FREE_ONLY_PILOT_AUTHORIZED", credential_present=bool(credential), attestation=attestation, attestation_sha256=attestation_hash, source_commit=source_commit,
            raw_root=result_root / "raw", normalized_root=result_root / "normalized", attempt_root=result_root, repository_root=ROOT,
            send=lambda prepared=prepared, credential=credential, provider=provider: _sender(provider=provider, endpoint=prepared.endpoint, body=prepared.body, credential=credential or ""),
        ))
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-attestation", type=Path, required=True, help="Non-secret, manually verified Free Tier/Free Plan record.")
    args = parser.parse_args()
    results = run(args.account_attestation)
    print(json.dumps({"pilot_rows": len(results), "status_counts": {status: sum(result["status"] == status for result in results) for status in sorted({result["status"] for result in results})}, "model_generation_requests_attempted": len(results)}, sort_keys=True))
