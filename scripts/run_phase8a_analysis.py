"""Run the frozen, offline Phase 8A confirmatory analysis."""
from __future__ import annotations

import csv
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase8a_analysis import assert_unique, estimate_binary, ht_rate, load_json, sha256_file, write_json

OUT = ROOT / "data/analysis/phase8a"
RESULTS = OUT / "phase8a_results.json"
CSV = OUT / "phase8a_results.csv"


def physical_means(outcomes: dict[tuple[str, int, str], list[dict]], scenario: str, speed: int, action: str) -> dict:
    rows = outcomes[(scenario, speed, action)]
    if len(rows) != 5:
        raise ValueError(f"Phase 4 seed cardinality is not five for {scenario}/{speed}/{action}")
    return {
        "collision_mean": sum(bool(row["collision"]) for row in rows) / 5,
        "feasible_mean": sum(bool(row["trajectory_feasible"]) for row in rows) / 5,
        "road_compliant_mean": sum(bool(row["road_compliant"]) for row in rows) / 5,
        "minimum_distance_m_mean": sum(float(row["minimum_distance_m"]) for row in rows) / 5,
    }


def add_rate(rows: list[dict], metric_id: str, sample: dict, values: dict[str, int], **dimensions: str) -> dict:
    result = estimate_binary(sample, values)
    result.update({"result_id": metric_id, "kind": "finite_population_rate", "estimability": "ESTIMABLE", "dimensions": dimensions})
    rows.append(result)
    return result


def main() -> None:
    input_manifest = load_json(OUT / "phase8a_input_manifest.json")
    if input_manifest["source_phase7_recovered_checkpoint"] != "99551fa86bf11e5771339fd68c035943a149d3ee":
        raise SystemExit("unexpected recovered Phase 7 checkpoint")
    sample = load_json(ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json")
    phase7 = load_json(ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json")
    allowlist = set(input_manifest["action_allowlist"])
    manifest_by_id = {row["run_id"]: row for row in phase7["rows"]}
    selected = input_manifest["selected_observation_provenance"]
    assert_unique(selected, "run_id")
    if len(selected) != 339:
        raise SystemExit("expected exactly 339 selected analysis observations")
    observations: list[dict] = []
    for source in selected:
        record = load_json(ROOT / source["attempt_path"])
        if sha256_file(ROOT / source["attempt_path"]) != source["attempt_sha256"]:
            raise SystemExit(f"attempt record hash changed: {source['run_id']}")
        row = manifest_by_id.get(source["run_id"])
        if row is None:
            raise SystemExit(f"selected ID absent from Phase 7 manifest: {source['run_id']}")
        if record.get("status") != "completed" or record.get("http_status") != 200:
            raise SystemExit(f"nonterminal selected observation: {source['run_id']}")
        selected_action = record.get("selected_action_id")
        explicit = selected_action in allowlist
        valid = record.get("allowlisted_action_valid") is True and explicit
        observations.append({"run_id": source["run_id"], "model_id": row["model_id"], "provider": row["provider"], "scenario_id": row["input_package_id"].split("__")[0], "speed_kph": int(row["input_package_id"].split("__V")[1]), "condition": row["condition"], "selection_role": "probability_sample" if source["selection"]["probability_sample"] else "certainty", "inclusion_probability": source["selection"]["inclusion_probability"], "base_weight": source["selection"]["base_weight"], "strict_json_valid": record.get("format_compliance") is True, "normalization_success": record.get("normalization_success") is True, "explicit_action": explicit, "valid_allowlisted_action": valid, "selected_action_id": selected_action if explicit else None})
    outcomes: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    with (ROOT / "data/simulator/commonroad/outcomes/commonroad_pilot_v1.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            outcomes[(row["scenario_id"], int(row["speed_kph"]), row["action_id"])].append(row)
    physical_linked = 0
    for row in observations:
        if row["valid_allowlisted_action"]:
            row.update(physical_means(outcomes, row["scenario_id"], row["speed_kph"], row["selected_action_id"]))
            physical_linked += 1
    if physical_linked != sum(row["valid_allowlisted_action"] for row in observations):
        raise SystemExit("physical join cardinality mismatch")
    ids = [row["run_id"] for row in observations]
    by_id = {row["run_id"]: row for row in observations}
    results: list[dict] = []
    accounting = {"design_accounted": len(phase7["rows"]), "not_applicable": sum(row["execution_state"] == "not_applicable" for row in phase7["rows"]), "provider_execution_population": sample["provider_population_size"], "certainty_observations": sample["certainty_count"], "probability_sample_observations": sample["probability_sample_size"], "analysis_observations": len(observations), "terminal_responses": len(observations), "explicit_actions": sum(row["explicit_action"] for row in observations), "valid_allowlisted_actions": sum(row["valid_allowlisted_action"] for row in observations), "physical_outcome_linked_actions": physical_linked}
    add_rate(results, "P8A-INTERFACE-001", sample, {run_id: 1 for run_id in ids}, metric_name="terminal_response_rate")
    add_rate(results, "P8A-INTERFACE-002", sample, {k: int(by_id[k]["explicit_action"]) for k in ids}, metric_name="explicit_decision_rate")
    valid = add_rate(results, "P8A-INTERFACE-003", sample, {k: int(by_id[k]["valid_allowlisted_action"]) for k in ids}, metric_name="allowlisted_action_validity_rate")
    add_rate(results, "P8A-INTERFACE-004", sample, {k: int(by_id[k]["strict_json_valid"]) for k in ids}, metric_name="strict_json_validity_rate")
    add_rate(results, "P8A-INTERFACE-005", sample, {k: int(not by_id[k]["explicit_action"]) for k in ids}, metric_name="invalid_or_no_action_rate")
    for action in input_manifest["action_allowlist"]:
        add_rate(results, f"P8A-ACTION-{action}", sample, {k: int(by_id[k]["valid_allowlisted_action"] and by_id[k]["selected_action_id"] == action) for k in ids}, metric_name="selected_action_joint_rate", action_id=action)
    frame = [row for row in phase7["rows"] if row["execution_state"] == "pending_zero_cost_authorization"]
    for dimension in ("model_id", "scenario_id", "speed_kph", "condition"):
        frame_counts: dict[str, int] = defaultdict(int)
        for source_row in frame:
            if dimension == "scenario_id":
                value = source_row["input_package_id"].split("__")[0]
            elif dimension == "speed_kph":
                value = str(int(source_row["input_package_id"].split("__V")[1]))
            else:
                value = str(source_row[dimension])
            frame_counts[value] += 1
        domain_values: dict[str, list[dict]] = defaultdict(list)
        for observation in observations:
            value = str(observation[dimension])
            domain_values[value].append(observation)
        for value, domain_rows in sorted(domain_values.items()):
            for action in input_manifest["action_allowlist"]:
                weighted_total = sum(row["base_weight"] * int(row["valid_allowlisted_action"] and row["selected_action_id"] == action) for row in domain_rows)
                results.append({"result_id": f"P8A-DOMAIN-{dimension.upper()}-{value}-{action}", "kind": "domain_weighted_action_rate", "metric_name": "selected_action_joint_rate", "estimability": "DOMAIN_UNCERTAINTY_NOT_ESTIMABLE", "raw_numerator": sum(int(row["valid_allowlisted_action"] and row["selected_action_id"] == action) for row in domain_rows), "raw_denominator": len(domain_rows), "weighted_estimate": weighted_total / frame_counts[value], "standard_error": None, "approximate_95_ci": None, "estimator": "domain Horvitz-Thompson point estimate; domain interval not prespecified", "dimensions": {dimension: value, "action_id": action, "population_domain_size": frame_counts[value]}})
    # Physical effects are joint finite-population rates: no outcome is assigned to invalid/no-action records.
    for label, field in (("collision", "collision_mean"), ("feasible", "feasible_mean"), ("road_compliant", "road_compliant_mean")):
        values = {k: (by_id[k].get(field, 0.0) if by_id[k]["valid_allowlisted_action"] else 0.0) for k in ids}
        estimate = {"result_id": f"P8A-PHYSICAL-{label.upper()}", "kind": "joint_finite_population_mean", "metric_name": f"valid_action_and_{label}_mean", "estimability": "ESTIMABLE", "raw_numerator": sum(values.values()), "raw_denominator": len(values), "weighted_estimate": ht_rate(sample, values), "standard_error": None, "approximate_95_ci": None, "estimator": "Horvitz-Thompson finite-population mean; scalar outcome is five-seed Phase 4 arithmetic mean; variance not prespecified for this conditional physical scalar", "dimensions": {}}
        results.append(estimate)
    # Conditional clearance is descriptive only because the frozen design did not pre-specify a ratio-variance estimator.
    linked_weight = sum(row["base_weight"] for row in observations if row["valid_allowlisted_action"])
    clearance = sum(row["base_weight"] * row["minimum_distance_m_mean"] for row in observations if row["valid_allowlisted_action"]) / linked_weight
    results.append({"result_id": "P8A-PHYSICAL-MIN-DISTANCE", "kind": "conditional_weighted_descriptive_mean", "metric_name": "minimum_distance_m_given_valid_action", "estimability": "DESCRIPTIVE_ONLY", "raw_numerator": sum(row["minimum_distance_m_mean"] for row in observations if row["valid_allowlisted_action"]), "raw_denominator": physical_linked, "weighted_estimate": clearance, "standard_error": None, "approximate_95_ci": None, "estimator": "base-weighted conditional mean; no prespecified ratio variance", "dimensions": {}})
    results.append({"result_id": "P8A-LEGAL-001", "kind": "blocked", "metric_name": "jurisdictional_legal_compliance", "estimability": "NOT_ESTIMABLE", "raw_numerator": None, "raw_denominator": None, "weighted_estimate": None, "standard_error": None, "approximate_95_ci": None, "estimator": None, "dimensions": {}, "reason": "Frozen Phase 5 v1 has no action-level legal determination; Phase 8A does not infer legality."})
    payload = {"schema_version": "phase8a-results-v1", "offline_only": True, "source_input_manifest_sha256": sha256_file(OUT / "phase8a_input_manifest.json"), "accounting": accounting, "known_phase7_valid_action_estimate_reproduced": valid, "results": results, "software": {"python": platform.python_version(), "implementation": platform.python_implementation()}}
    write_json(RESULTS, payload)
    with CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["result_id", "metric_name", "kind", "estimability", "raw_numerator", "raw_denominator", "weighted_estimate", "standard_error", "approximate_95_ci", "estimator", "dimensions"], lineterminator="\n")
        writer.writeheader()
        for row in results:
            writer.writerow({key: json.dumps(row[key], sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key) for key in writer.fieldnames})
    print(f"Phase 8A results written: {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
