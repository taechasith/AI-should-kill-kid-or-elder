"""Validate the zero-cost Phase 6 preflight without making a provider call."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_free_adapters import build_free_provider_request
from geosave.phase6_free_guard import ALLOWED_PROVIDER_MODELS, FreeOnlyExecutionGuard
from geosave.phase6_inputs import INPUT_ROOT
from geosave.phase6_interface import ALLOWED_ACTIONS, canonical_json_bytes
from geosave.phase6_prompts import build_phase6_user_message


CONFIG_PATH = ROOT / "configs" / "experiments" / "phase6_free_v1_preflight.json"
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_free_v1_candidate_registry.json"
MANIFEST_PATH = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "manifests" / "phase6_free_v1_preflight_manifest.json"
PILOT_PATH = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "manifests" / "phase6_free_v1_pilot_manifest.json"
POLICY_PATH = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "phase6_free_v1_cost_policy.json"
VALIDATION_PATH = ROOT / "data" / "validation" / "phase6_free_v1_preflight_validation.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate() -> dict[str, Any]:
    config = _read_json(CONFIG_PATH)
    registry = _read_json(REGISTRY_PATH)
    manifest = _read_json(MANIFEST_PATH)
    pilot = _read_json(PILOT_PATH)
    policy = _read_json(POLICY_PATH)
    input_manifest = _read_json(INPUT_ROOT / "input_manifest.json")

    _assert(config["status"] == "PREFLIGHT_PENDING_CREDENTIALS", "preflight config status changed")
    _assert(registry["status"] == "PREFLIGHT_PENDING_CREDENTIALS", "candidate registry became executable without a pilot")
    guard = FreeOnlyExecutionGuard.from_policy(registry["zero_cost_execution_policy"], registry["status"])
    _assert(guard.budget_mode == "FREE_ONLY", "zero-cost mode changed")
    _assert(guard.max_authorized_usd == 0.0 and guard.max_authorized_thb == 0.0, "monetary budget must remain zero")
    _assert(not any((guard.allow_paid_fallback, guard.allow_provider_upgrade, guard.allow_credit_purchase, guard.allow_automatic_billing)), "a paid route is enabled")
    expected = {"gemini": {"gemini-3.6-flash", "gemini-2.5-flash-lite"}, "groq": {"qwen/qwen3.8-27b"}}
    declared: dict[str, set[str]] = {"gemini": set(), "groq": set()}
    for model in registry["models"]:
        provider = "gemini" if model["provider"] == "Google Gemini API" else "groq"
        declared[provider].add(model["model_id"])
        _assert(model["model_id"] in ALLOWED_PROVIDER_MODELS[provider], f"unallowlisted free model {model['model_id']}")
        _assert(model["input_modalities"] == ["text", "image"], f"invalid modalities for {model['model_id']}")
        _assert(model["provider_access_status"] == "provider_documented_account_unverified", "account access must remain unverified before credential preflight")
        _assert(bool(model["official_sources"]), f"no official source for {model['model_id']}")
    _assert(declared == expected, "free candidate panel differs from the authorized pre-result panel")

    _assert(input_manifest["package_count"] == 6, "frozen input package count changed")
    _assert(manifest["phase4_canonical_commit"] == "d52baab", "Phase 4 provenance changed")
    _assert(manifest["law_snapshot"] == "phase5-legal-snapshot-v1", "Phase 5 provenance changed")
    _assert(manifest["row_count"] == 5454 == len(manifest["rows"]), "free manifest row count is wrong")
    _assert(manifest["pending_provider_execution_count"] == 4104, "free provider call count is wrong")
    _assert(manifest["not_applicable_row_count"] == 1350, "free not-applicable count is wrong")
    state_counts = Counter(row["execution_state"] for row in manifest["rows"])
    _assert(state_counts == Counter({"pending_free_access_preflight": 4104, "not_applicable": 1350}), "unexpected free preflight states")
    run_ids = [row["run_id"] for row in manifest["rows"]]
    _assert(len(run_ids) == len(set(run_ids)), "duplicate free manifest run IDs")
    for row in manifest["rows"]:
        _assert(set(row["action_order"]) == set(ALLOWED_ACTIONS) and len(row["action_order"]) == 6, "invalid action ordering")
        if row["condition"] == "C0":
            _assert(row["country_iso3"] is None, "C0 deduplication changed")
        if row["condition"] == "C3":
            _assert(row["execution_state"] == "not_applicable", "C3 requires retained raw legal evidence")
    _assert(pilot["row_count"] == 3 == len(pilot["rows"]), "free capability pilot must be exactly three calls")
    _assert({row["model_id"] for row in pilot["rows"]} == {"gemini-3.6-flash", "gemini-2.5-flash-lite", "qwen/qwen3.8-27b"}, "pilot panel mismatch")
    _assert(all(row["execution_state"] == "pending_free_access_preflight" for row in pilot["rows"]), "pilot must not contain invented responses")
    _assert(policy["monetary_cost_usd"] == 0.0 and policy["monetary_cost_thb"] == 0.0, "cost policy is not zero")
    _assert(policy["provider_calls_made"] == 0, "preflight must not contain provider calls")
    # This validator freezes planning artifacts.  After the pilot begins, its
    # append-only raw/normalized directories are expected to coexist with this
    # preflight and must be validated by the pilot-result validator instead.

    package_dir = INPUT_ROOT / "packages" / "PED-CROSS-001__V030"
    telemetry = _read_json(package_dir / "telemetry.json")
    actions = _read_json(package_dir / "candidate_actions.json")
    message = build_phase6_user_message(condition="C2", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=next(json.loads(line) for line in (INPUT_ROOT / "condition_contexts.jsonl").read_text(encoding="utf-8").splitlines() if 'PED-CROSS-001__V030__ARG' in line))
    image_path = package_dir / "birdseye_initial_state.png"
    for provider, model_id in (("gemini", "gemini-3.6-flash"), ("gemini", "gemini-2.5-flash-lite"), ("groq", "qwen/qwen3.8-27b")):
        request = build_free_provider_request(provider=provider, model_id=model_id, image_path=image_path, system_message="Closed-book system message.", user_message=message, max_output_tokens=500)
        serialized = json.dumps(request.body)
        _assert(request.request_hash == request.request_hash, "request hash is unstable")
        _assert('"tools"' not in serialized and '"web"' not in serialized and '"search"' not in serialized, "closed-book payload includes tools")

    result = {
        "schema_version": "phase6-free-preflight-validation-v1",
        "validation_status": "passed",
        "phase_status": "preflight_pending_credentials",
        "provider_calls_made": 0,
        "full_manifest_rows": 5454,
        "pending_free_access_preflight_rows": 4104,
        "not_applicable_rows": 1350,
        "capability_pilot_rows": 3,
        "zero_cost_guard_status": "passed_offline",
        "notes": "This verifies only the versioned offline preflight. Credentials, account tier, rate limits, image acceptance, parser success on a live response, and zero monetary charge require the later live gate."
    }
    VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.write_bytes(canonical_json_bytes(result))
    return result


if __name__ == "__main__":
    result = validate()
    print(
        "Phase 6 free preflight: valid; "
        f"{result['full_manifest_rows']} planned rows, "
        f"{result['capability_pilot_rows']} unsent pilot requests, "
        f"{result['provider_calls_made']} provider calls."
    )
