"""Build frozen Phase 6 dry-run inputs and manifests without calling a model."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_inputs import INPUT_ROOT, build_phase6_input_packages
from geosave.phase6_interface import canonical_json_bytes, deterministic_action_order


CONFIG_PATH = ROOT / "configs" / "experiments" / "phase6_model_interface_dry_run_v1.json"
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_model_registry_dry_run_v1.json"
OUTPUT_ROOT = ROOT / "data" / "model_benchmark" / "phase6"
MANIFEST_PATH = OUTPUT_ROOT / "manifests" / "phase6_dry_run_v1.json"
PILOT_PATH = OUTPUT_ROOT / "manifests" / "phase6_pilot_dry_run_v1.json"
COST_PATH = OUTPUT_ROOT / "phase6_dry_run_cost_estimate_v1.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256(payload).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _run_id(model_slot: str, input_package_id: str, country_iso3: str | None, condition: str, repeat_index: int) -> str:
    jurisdiction = country_iso3 or "GLOBAL"
    return f"P6-{model_slot}-{input_package_id}-{jurisdiction}-{condition}-R{repeat_index:02d}"


def _row(
    *,
    model: dict[str, Any],
    input_package_id: str,
    country_iso3: str | None,
    condition: str,
    repeat_index: int,
    execution_state: str,
    reason: str | None,
) -> dict[str, Any]:
    run_id = _run_id(model["panel_slot"], input_package_id, country_iso3, condition, repeat_index)
    return {
        "run_id": run_id,
        "model_slot": model["panel_slot"],
        "model_id": model["model_id"],
        "model_revision": model["model_revision"],
        "provider": model["provider"],
        "input_package_id": input_package_id,
        "country_iso3": country_iso3,
        "condition": condition,
        "repeat_index": repeat_index,
        "action_order": list(deterministic_action_order(run_id)),
        "execution_state": execution_state,
        "execution_reason": reason,
        "raw_response_reference": f"data/model_benchmark/phase6/raw/{run_id}.txt",
        "normalized_response_reference": f"data/model_benchmark/phase6/normalized/{run_id}.json",
    }


def _main_rows(config: dict[str, Any], registry: dict[str, Any], contexts: list[dict[str, Any]], package_ids: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    repeats = config["execution_settings"]["main_repeat_count"]
    models = registry["models"]
    context_index = {(item["input_package_id"], item["country_iso3"]): item for item in contexts}
    for model in models:
        for input_package_id in package_ids:
            for repeat_index in range(1, repeats + 1):
                rows.append(
                    _row(
                        model=model,
                        input_package_id=input_package_id,
                        country_iso3=None,
                        condition="C0",
                        repeat_index=repeat_index,
                        execution_state="blocked_authorization",
                        reason="No paid/provider call is authorized in the frozen dry run.",
                    )
                )
            for country_iso3 in sorted(country for package, country in context_index if package == input_package_id):
                context = context_index[(input_package_id, country_iso3)]
                for condition in ("C1", "C2", "C3", "C4"):
                    eligible = condition != "C3" or context["C3"]["eligible"]
                    for repeat_index in range(1, repeats + 1):
                        rows.append(
                            _row(
                                model=model,
                                input_package_id=input_package_id,
                                country_iso3=country_iso3,
                                condition=condition,
                                repeat_index=repeat_index,
                                execution_state="blocked_authorization" if eligible else "not_applicable",
                                reason=("No paid/provider call is authorized in the frozen dry run." if eligible else context["C3"]["not_applicable_reason"]),
                            )
                        )
    return rows


def _pilot_rows(config: dict[str, Any], registry: dict[str, Any]) -> list[dict[str, Any]]:
    pilot = config["pilot_stratification"]
    rows: list[dict[str, Any]] = []
    for model in registry["models"]:
        for input_package_id in pilot["input_package_ids"]:
            country_iso3 = pilot["jurisdiction_by_input_package"][input_package_id]
            for condition in pilot["eligible_conditions"]:
                rows.append(
                    _row(
                        model=model,
                        input_package_id=input_package_id,
                        country_iso3=None if condition == "C0" else country_iso3,
                        condition=condition,
                        repeat_index=1,
                        execution_state="blocked_authorization",
                        reason="No paid/provider call is authorized in the frozen dry run.",
                    )
                )
    return rows


def _cost_for_rows(rows: Iterable[dict[str, Any]], config: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    cost = config["cost_assumptions"]
    input_tokens = cost["planned_input_tokens_per_request"]
    output_tokens = cost["planned_output_tokens_per_request"]
    model_by_slot = {model["panel_slot"]: model for model in registry["models"]}
    eligible_rows = [row for row in rows if row["execution_state"] == "blocked_authorization"]
    counts = Counter(row["model_slot"] for row in eligible_rows)
    per_model: list[dict[str, Any]] = []
    for slot, count in sorted(counts.items()):
        model = model_by_slot[slot]
        rates = model["pricing_snapshot_usd_per_million_tokens"]
        per_request = input_tokens * rates["input"] / 1_000_000 + output_tokens * rates["output"] / 1_000_000
        per_model.append(
            {
                "model_slot": slot,
                "model_id": model["model_id"],
                "eligible_request_count": count,
                "estimated_usd_without_retry": round(count * per_request, 6),
                "estimated_usd_with_one_retry_per_request": round(count * per_request * 2, 6),
            }
        )
    total = sum(item["estimated_usd_without_retry"] for item in per_model)
    return {
        "eligible_request_count": len(eligible_rows),
        "not_applicable_row_count": sum(row["execution_state"] == "not_applicable" for row in rows),
        "planned_input_tokens_per_request": input_tokens,
        "planned_output_tokens_per_request": output_tokens,
        "per_model": per_model,
        "estimated_total_usd_without_retry": round(total, 6),
        "estimated_total_usd_with_one_retry_per_request": round(total * 2, 6),
        "estimate_limitations": "A planning allowance, not a billing guarantee. It includes one 512x512 image in the input allowance; any execution must retain provider-reported usage and may have different image-token accounting.",
    }


def build() -> dict[str, Any]:
    input_manifest = build_phase6_input_packages(INPUT_ROOT)
    config = _load_json(CONFIG_PATH)
    registry = _load_json(REGISTRY_PATH)
    contexts = _load_jsonl(ROOT / input_manifest["condition_contexts"]["path"])
    package_ids = [package["input_package_id"] for package in input_manifest["packages"]]
    rows = _main_rows(config, registry, contexts, package_ids)
    pilot_rows = _pilot_rows(config, registry)
    cost = {
        "schema_version": "phase6-dry-run-cost-v1",
        "status": "NOT_AUTHORIZED_FOR_EXECUTION",
        "price_retrieval_date": registry["selection_date"],
        "main_matrix": _cost_for_rows(rows, config, registry),
        "pilot": _cost_for_rows(pilot_rows, config, registry),
    }
    manifest = {
        "schema_version": "phase6-dry-run-manifest-v1",
        "manifest_id": config["experiment_id"],
        "status": "BLOCKED_AUTHORIZATION",
        "phase4_canonical_commit": config["phase4_canonical_commit"],
        "phase4_pilot_tag": config["phase4_pilot_tag"],
        "law_snapshot": config["law_snapshot"],
        "input_manifest": _relative(INPUT_ROOT / "input_manifest.json"),
        "candidate_model_registry": config["candidate_model_registry"],
        "condition_ids": [condition["condition_id"] for condition in config["conditions"]],
        "main_repeat_count": config["execution_settings"]["main_repeat_count"],
        "maximum_automatic_retries": config["execution_settings"]["maximum_automatic_retries"],
        "row_count": len(rows),
        "eligible_provider_call_count": sum(row["execution_state"] == "blocked_authorization" for row in rows),
        "not_applicable_row_count": sum(row["execution_state"] == "not_applicable" for row in rows),
        "rows": rows,
        "no_model_output_has_been_generated": True,
    }
    pilot_manifest = {
        "schema_version": "phase6-pilot-dry-run-manifest-v1",
        "manifest_id": "phase6-model-interface-pilot-v1-dry-run",
        "status": "BLOCKED_AUTHORIZATION",
        "row_count": len(pilot_rows),
        "eligible_provider_call_count": len(pilot_rows),
        "not_applicable_conditions": config["pilot_stratification"]["not_applicable_conditions"],
        "rows": pilot_rows,
        "no_model_output_has_been_generated": True,
    }
    _write_json(MANIFEST_PATH, manifest)
    _write_json(PILOT_PATH, pilot_manifest)
    _write_json(COST_PATH, cost)
    return {"inputs": input_manifest, "manifest": manifest, "pilot": pilot_manifest, "cost": cost}


if __name__ == "__main__":
    result = build()
    print(
        "Phase 6 dry run: "
        f"{result['inputs']['package_count']} initial-state packages; "
        f"{result['manifest']['row_count']} planned rows; "
        f"{result['manifest']['eligible_provider_call_count']} provider calls blocked; "
        f"{result['manifest']['not_applicable_row_count']} not applicable."
    )
