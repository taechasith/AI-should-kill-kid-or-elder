"""Build a zero-cost Phase 6 preflight manifest without provider I/O.

The existing paid-panel dry-run remains untouched.  This separate artifact
preserves its Phase 4/5 inputs and repeat policy while recording that free-tier
account verification and the three-call capability pilot have not occurred.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_interface import canonical_json_bytes, deterministic_action_order


CONFIG_PATH = ROOT / "configs" / "experiments" / "phase6_free_v1_preflight.json"
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_free_v1_candidate_registry.json"
INPUT_ROOT = ROOT / "data" / "model_inputs" / "phase6" / "phase6_model_interface_v1"
OUTPUT_ROOT = ROOT / "data" / "model_benchmark" / "phase6_free_v1"
MANIFEST_PATH = OUTPUT_ROOT / "manifests" / "phase6_free_v1_preflight_manifest.json"
PILOT_PATH = OUTPUT_ROOT / "manifests" / "phase6_free_v1_pilot_manifest.json"
POLICY_PATH = OUTPUT_ROOT / "phase6_free_v1_cost_policy.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256(payload).hexdigest()


def _run_id(slot: str, package_id: str, country: str | None, condition: str, repeat: int) -> str:
    return f"P6F-{slot}-{package_id}-{country or 'GLOBAL'}-{condition}-R{repeat:02d}"


def _row(
    *, model: dict[str, Any], package_id: str, country: str | None, condition: str, repeat: int, state: str, reason: str
) -> dict[str, Any]:
    run_id = _run_id(model["panel_slot"], package_id, country, condition, repeat)
    return {
        "run_id": run_id,
        "model_slot": model["panel_slot"],
        "provider": model["provider"],
        "model_id": model["model_id"],
        "model_revision": model["model_revision"],
        "input_package_id": package_id,
        "country_iso3": country,
        "condition": condition,
        "repeat_index": repeat,
        "action_order": list(deterministic_action_order(run_id)),
        "execution_state": state,
        "execution_reason": reason,
        "raw_response_reference": f"data/model_benchmark/phase6_free_v1/raw/{run_id}.txt",
        "normalized_response_reference": f"data/model_benchmark/phase6_free_v1/normalized/{run_id}.json",
    }


def build() -> dict[str, Any]:
    config = _read_json(CONFIG_PATH)
    registry = _read_json(REGISTRY_PATH)
    input_manifest = _read_json(INPUT_ROOT / "input_manifest.json")
    contexts = _read_jsonl(ROOT / input_manifest["condition_contexts"]["path"])
    package_ids = [item["input_package_id"] for item in input_manifest["packages"]]
    context_index = {(item["input_package_id"], item["country_iso3"]): item for item in contexts}
    rows: list[dict[str, Any]] = []
    pending_reason = "Free-tier credential, account tier, model availability, and quota verification have not completed. No provider request is permitted."
    for model in registry["models"]:
        for package_id in package_ids:
            for repeat in range(1, config["execution_settings"]["main_repeat_count"] + 1):
                rows.append(_row(model=model, package_id=package_id, country=None, condition="C0", repeat=repeat, state="pending_free_access_preflight", reason=pending_reason))
            countries = sorted(country for package, country in context_index if package == package_id)
            for country in countries:
                context = context_index[(package_id, country)]
                for condition in ("C1", "C2", "C3", "C4"):
                    for repeat in range(1, config["execution_settings"]["main_repeat_count"] + 1):
                        if condition == "C3" and not context["C3"]["eligible"]:
                            rows.append(_row(model=model, package_id=package_id, country=country, condition=condition, repeat=repeat, state="not_applicable", reason=context["C3"]["not_applicable_reason"]))
                        else:
                            rows.append(_row(model=model, package_id=package_id, country=country, condition=condition, repeat=repeat, state="pending_free_access_preflight", reason=pending_reason))

    pilot_rows = [
        _row(
            model=model,
            package_id=config["pilot"]["input_package_id"],
            country=config["pilot"]["country_iso3"],
            condition=config["pilot"]["condition"],
            repeat=1,
            state="pending_free_access_preflight",
            reason=pending_reason,
        )
        for model in registry["models"]
    ]
    manifest = {
        "schema_version": "phase6-free-preflight-manifest-v1",
        "manifest_id": config["experiment_id"],
        "status": config["status"],
        "phase4_canonical_commit": config["phase4_canonical_commit"],
        "phase4_pilot_tag": config["phase4_pilot_tag"],
        "law_snapshot": config["law_snapshot"],
        "input_package_version": input_manifest["input_package_version"],
        "input_manifest_path": "data/model_inputs/phase6/phase6_model_interface_v1/input_manifest.json",
        "candidate_model_registry": config["candidate_model_registry"],
        "row_count": len(rows),
        "pending_provider_execution_count": sum(row["execution_state"] == "pending_free_access_preflight" for row in rows),
        "not_applicable_row_count": sum(row["execution_state"] == "not_applicable" for row in rows),
        "rows": rows,
        "provider_calls_made": 0,
        "no_model_output_has_been_generated": True,
    }
    pilot = {
        "schema_version": "phase6-free-pilot-manifest-v1",
        "manifest_id": "phase6-free-v1-multimodal-capability-pilot",
        "status": config["status"],
        "purpose": config["pilot"]["purpose"],
        "row_count": len(pilot_rows),
        "rows": pilot_rows,
        "provider_calls_made": 0,
        "no_model_output_has_been_generated": True,
    }
    policy = {
        "schema_version": "phase6-free-cost-policy-v1",
        "status": config["status"],
        "hard_budget": registry["zero_cost_execution_policy"],
        "planned_main_provider_execution_count": manifest["pending_provider_execution_count"],
        "planned_pilot_provider_execution_count": pilot["row_count"],
        "monetary_cost_usd": 0.0,
        "monetary_cost_thb": 0.0,
        "cost_basis": "Only documented Free Tier / Free Plan quota may be used. If a provider requests payment, billing activation, a paid tier, credits, or a card, that provider must not be called.",
        "provider_calls_made": 0,
    }
    _write_json(MANIFEST_PATH, manifest)
    _write_json(PILOT_PATH, pilot)
    _write_json(POLICY_PATH, policy)
    return {"manifest": manifest, "pilot": pilot, "policy": policy}


if __name__ == "__main__":
    result = build()
    print(
        "Phase 6 free preflight: "
        f"{result['manifest']['row_count']} planned rows; "
        f"{result['manifest']['pending_provider_execution_count']} pending free-access verification; "
        f"{result['pilot']['row_count']} pilot requests not sent."
    )
