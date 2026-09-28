"""Validate Phase 6 dry-run artifacts without making provider calls."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.model_adapters import build_provider_request
from geosave.phase6_inputs import FUTURE_OUTCOME_KEYS, INPUT_ROOT
from geosave.phase6_interface import ALLOWED_ACTIONS, canonical_json_bytes
from geosave.phase6_prompts import build_phase6_user_message


CONFIG_PATH = ROOT / "configs" / "experiments" / "phase6_model_interface_dry_run_v1.json"
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_model_registry_dry_run_v1.json"
MANIFEST_PATH = ROOT / "data" / "model_benchmark" / "phase6" / "manifests" / "phase6_dry_run_v1.json"
PILOT_PATH = ROOT / "data" / "model_benchmark" / "phase6" / "manifests" / "phase6_pilot_dry_run_v1.json"
COST_PATH = ROOT / "data" / "model_benchmark" / "phase6" / "phase6_dry_run_cost_estimate_v1.json"
VALIDATION_PATH = ROOT / "data" / "validation" / "phase6_dry_run_validation_v1.json"
OUTPUT_SCHEMA_PATH = ROOT / "schemas" / "v1" / "phase6_model_decision.schema.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n") or payload[12:16] != b"IHDR":
        raise ValueError(f"not a PNG initial-state image: {path}")
    return struct.unpack(">II", payload[16:24])


def _forbidden_outcome_key(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in FUTURE_OUTCOME_KEYS:
                return key
            forbidden = _forbidden_outcome_key(nested)
            if forbidden:
                return forbidden
    elif isinstance(value, list):
        for nested in value:
            forbidden = _forbidden_outcome_key(nested)
            if forbidden:
                return forbidden
    return None


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate() -> dict[str, Any]:
    config = _read_json(CONFIG_PATH)
    registry = _read_json(REGISTRY_PATH)
    output_schema = _read_json(OUTPUT_SCHEMA_PATH)
    input_manifest = _read_json(INPUT_ROOT / "input_manifest.json")
    contexts = _read_jsonl(ROOT / input_manifest["condition_contexts"]["path"])
    manifest = _read_json(MANIFEST_PATH)
    pilot = _read_json(PILOT_PATH)
    cost = _read_json(COST_PATH)

    _assert(config["status"] == "FROZEN_DRY_RUN_PENDING_AUTHORIZATION", "dry-run config status changed")
    _assert(output_schema["properties"]["schema_version"]["const"] == "phase6-model-decision-v1", "output schema version changed")
    _assert(
        {"decision_status", "selected_action_id", "stated_factors", "legal_claims", "evidence_ids_cited", "uncertainty_statement", "short_rationale", "raw_response_reference"}.issubset(output_schema["required"]),
        "output schema no longer enforces the Phase 6 contract",
    )
    _assert(registry["execution_policy"]["execution_enabled"] is False, "registry unexpectedly enables execution")
    _assert(registry["execution_policy"]["provider_calls_permitted"] is False, "registry unexpectedly permits provider calls")
    _assert(len(registry["models"]) == 3, "candidate panel must contain exactly three models")
    _assert(len({model["provider"] for model in registry["models"]}) >= 2, "panel lacks provider diversity")
    for model in registry["models"]:
        _assert(model["vision_enabled"] is True, f"{model['model_id']} is not marked vision-capable")
        _assert(model["input_modalities"] == ["text", "image"], f"{model['model_id']} has an invalid modality declaration")
        _assert(model["provider_access_status"] == "not_authorized_for_execution", "access status is not conservative")
        _assert(bool(model["official_sources"]), f"{model['model_id']} has no official source")

    _assert(input_manifest["package_count"] == 6 and len(input_manifest["packages"]) == 6, "must have six unique initial-state packages")
    _assert(input_manifest["base_package_information_boundary"]["future_action_outcomes_excluded"] is True, "base inputs leak outcomes")
    _assert(len(contexts) == 150, "must have six packages across 25 jurisdictions")
    context_by_id = {item["context_id"]: item for item in contexts}
    _assert(len(context_by_id) == len(contexts), "condition context IDs are not unique")
    for package in input_manifest["packages"]:
        files = package["files"]
        for record in files.values():
            path = ROOT / record["path"]
            _assert(path.exists(), f"missing input artifact {record['path']}")
            _assert(_hash(path) == record["sha256"], f"hash mismatch for {record['path']}")
        image_path = ROOT / files["birdseye_image"]["path"]
        _assert(_png_dimensions(image_path) == (512, 512), f"unexpected image dimensions for {package['input_package_id']}")
        telemetry = _read_json(ROOT / files["telemetry"]["path"])
        candidate_actions = _read_json(ROOT / files["candidate_actions"]["path"])
        metadata = _read_json(ROOT / files["metadata"]["path"])
        _assert(_forbidden_outcome_key(telemetry) is None, f"base telemetry leaks {_forbidden_outcome_key(telemetry)}")
        _assert(metadata["initial_state_only"] is True and metadata["future_outcome_data_in_base_package"] is False, "base metadata violates initial-state boundary")
        _assert({item["action_id"] for item in candidate_actions["actions"]} == set(ALLOWED_ACTIONS), "candidate action set changed")
        context = context_by_id[f"{package['input_package_id']}__ARG"]
        message_c0 = build_phase6_user_message(
            condition="C0", telemetry=telemetry, candidate_actions=candidate_actions, action_order=ALLOWED_ACTIONS, condition_context=None
        )
        message_c4 = build_phase6_user_message(
            condition="C4", telemetry=telemetry, candidate_actions=candidate_actions, action_order=ALLOWED_ACTIONS, condition_context=context
        )
        _assert("geosave_constrained_support" not in message_c0 and "structured_legal_context" not in message_c0, "C0 context leakage")
        _assert("geosave_constrained_support" in message_c4, "C4 support missing")
        for model in registry["models"]:
            request = build_provider_request(
                provider={"OpenAI": "openai", "Anthropic": "anthropic", "Mistral AI": "mistral"}[model["provider"]],
                model_id=model["model_id"],
                image_path=image_path,
                system_message="Closed-book test system message.",
                user_message=message_c0,
                max_output_tokens=config["execution_settings"]["max_output_tokens"],
            )
            _assert(request.request_hash, "adapter did not produce a deterministic request hash")

    _assert(all(item["C3"]["eligible"] is False for item in contexts), "C3 must be unavailable without retained action-level evidence text")
    _assert(all(item["C4"]["intentional_candidate_consequence_disclosure"] is True for item in contexts), "C4 disclosure flag missing")
    _assert(manifest["status"] == "BLOCKED_AUTHORIZATION", "manifest status changed")
    _assert(manifest["row_count"] == 5454 == len(manifest["rows"]), "full dry-run row count is wrong")
    _assert(manifest["eligible_provider_call_count"] == 4104, "eligible call count is wrong")
    _assert(manifest["not_applicable_row_count"] == 1350, "not-applicable count is wrong")
    run_ids = [row["run_id"] for row in manifest["rows"]]
    _assert(len(run_ids) == len(set(run_ids)), "duplicate Phase 6 run IDs")
    state_counts = Counter(row["execution_state"] for row in manifest["rows"])
    _assert(state_counts == Counter({"blocked_authorization": 4104, "not_applicable": 1350}), "unexpected execution-state counts")
    for row in manifest["rows"]:
        _assert(set(row["action_order"]) == set(ALLOWED_ACTIONS) and len(row["action_order"]) == len(ALLOWED_ACTIONS), "invalid action order")
        if row["condition"] == "C0":
            _assert(row["country_iso3"] is None, "C0 was not deduplicated across jurisdictions")
        else:
            _assert(row["country_iso3"] is not None, "jurisdictional condition lacks a jurisdiction")
        if row["condition"] == "C3":
            _assert(row["execution_state"] == "not_applicable", "C3 must not be executed without raw evidence")
    _assert(pilot["row_count"] == 36 == len(pilot["rows"]), "pilot call count is wrong")
    _assert(pilot["eligible_provider_call_count"] == 36, "pilot eligible count is wrong")
    _assert(all(row["execution_state"] == "blocked_authorization" for row in pilot["rows"]), "pilot should not simulate provider output")
    _assert(cost["main_matrix"]["eligible_request_count"] == 4104, "cost manifest does not match main call count")
    _assert(cost["pilot"]["eligible_request_count"] == 36, "cost manifest does not match pilot call count")
    _assert(cost["main_matrix"]["estimated_total_usd_without_retry"] > 0, "cost estimate must be positive")
    _assert(not (ROOT / "data" / "model_benchmark" / "phase6" / "raw").exists(), "raw response directory must not exist before a real call")

    result = {
        "schema_version": "phase6-dry-run-validation-v1",
        "validation_status": "passed",
        "phase_status": "blocked_authorization",
        "base_input_package_count": 6,
        "condition_context_count": 150,
        "full_manifest_rows": 5454,
        "eligible_provider_calls": 4104,
        "not_applicable_rows": 1350,
        "pilot_eligible_provider_calls": 36,
        "provider_calls_made": 0,
        "notes": "This validates offline serialization, parsing contracts, information boundaries, and planning artifacts only. It is not a successful provider pilot and does not complete Phase 6."
    }
    VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.write_bytes(canonical_json_bytes(result))
    return result


if __name__ == "__main__":
    result = validate()
    print(
        "Phase 6 dry-run artifacts: valid; "
        f"{result['base_input_package_count']} packages, "
        f"{result['full_manifest_rows']} planned rows, "
        f"{result['provider_calls_made']} provider calls."
    )
