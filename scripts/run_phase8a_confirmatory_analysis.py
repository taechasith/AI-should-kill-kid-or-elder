"""Generate the read-only, scope-limited Phase 8A analysis report."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geosave.phase7_population_sampling import ht_rate, stratified_ht_variance
from geosave.phase8_analysis import terminal_records, units_with_results, weighted_action_distribution

MANIFEST = ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json"
SAMPLE = ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json"
ATTEMPTS = ROOT / "data/model_benchmark/phase7_literature_v2/attempts"
LEGAL = ROOT / "data/legal/phase5/legal_decisions.jsonl"
PHYSICAL = ROOT / "data/simulator/commonroad/outcomes/commonroad_pilot_v1.jsonl"
OUTPUT = ROOT / "data/analysis/phase8a/phase8a_confirmatory_report.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_summary_by_action() -> dict[tuple[str, int, str], dict]:
    """Conservatively collapse frozen Phase 4 seeds for each candidate action."""
    grouped: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for line in PHYSICAL.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        grouped[(row["scenario_id"], row["speed_kph"], row["action_id"])].append(row)
    result = {}
    for key, rows in grouped.items():
        if not all(row["run_status"] == "completed" for row in rows):
            raise SystemExit(f"incomplete frozen Phase 4 outcome group: {key}")
        result[key] = {
            "seed_count": len(rows),
            "collision_free_all_seeds": all(bool(row["collision_free"]) for row in rows),
            "trajectory_feasible_all_seeds": all(bool(row["trajectory_feasible"]) for row in rows),
            "road_boundary_compliant_all_seeds": not any(bool(row["road_boundary_violation"]) for row in rows),
            "minimum_clearance_m_across_seeds": min(row["minimum_distance_m"] for row in rows),
        }
    return result


def main() -> None:
    manifest, sample = load(MANIFEST), load(SAMPLE)
    records = terminal_records(ATTEMPTS)
    units = units_with_results(sample, manifest, records)
    if len(units) != sample["certainty_count"] + sample["probability_sample_size"]:
        raise SystemExit("analysis units do not match frozen sample")

    outcomes = {unit["run_id"]: int(unit["allowlisted_action_valid"]) for unit in units}
    estimate = ht_rate(sample, outcomes)
    se = math.sqrt(stratified_ht_variance(sample, outcomes))

    legal_statuses = Counter()
    for line in LEGAL.read_text(encoding="utf-8").splitlines():
        legal_statuses[json.loads(line)["status"]] += 1
    if set(legal_statuses) != {"NOT_DETERMINED"}:
        raise SystemExit("frozen Phase 5 scope changed; legal claims require protocol review")

    by_model_condition: dict[str, list[dict]] = defaultdict(list)
    for unit in units:
        by_model_condition[f"{unit['model_id']}|{unit['condition']}"] .append(unit)
    distributions = {
        key: weighted_action_distribution(value)
        for key, value in sorted(by_model_condition.items())
    }
    scenario_ids = {unit["input_package_id"].split("__", 1)[0] for unit in units}
    missing_scenarios = sorted(
        scenario for scenario in scenario_ids
        if not (ROOT / "data/scenarios/commonroad/core" / f"{scenario}.yaml").exists()
    )
    if missing_scenarios:
        raise SystemExit(f"missing frozen Phase 4 scenario input(s): {missing_scenarios}")
    physical = physical_summary_by_action()
    physical_outcomes = {}
    for unit in units:
        if unit["selected_action_id"] is None:
            continue
        scenario, speed_token = unit["input_package_id"].split("__", 1)
        key = (scenario, int(speed_token.removeprefix("V")), unit["selected_action_id"])
        if key not in physical:
            raise SystemExit(f"missing frozen Phase 4 selected-action join: {key}")
        physical_outcomes[unit["run_id"]] = physical[key]
    physical_estimates = {"scope": "descriptive among observed rows with a parsed selected action; not a population rate because invalid outputs have no selected action to join"}
    for name in ("collision_free_all_seeds", "trajectory_feasible_all_seeds", "road_boundary_compliant_all_seeds"):
        count = sum(int(values[name]) for values in physical_outcomes.values())
        physical_estimates[name] = {
            "observed_selected_action_units": len(physical_outcomes),
            "count": count,
            "proportion": count / len(physical_outcomes),
        }
    physical_estimates["minimum_clearance_m_across_seeds"] = {
        "estimand": "mean of the minimum frozen Phase 4 clearance for each observed selected action",
        "estimate": sum(values["minimum_clearance_m_across_seeds"] for values in physical_outcomes.values()) / len(physical_outcomes),
        "confidence_interval": "not reported for this descriptive conditional summary",
    }
    physical_estimates["missing_selected_action_units"] = len(units) - len(physical_outcomes)

    report = {
        "schema_version": "phase8a-confirmatory-report-v1",
        "status": "COMPLETE_WITH_FROZEN_LEGAL_SCOPE_LIMITATION",
        "execution": {"provider_calls": 0, "usd_spend": 0.0, "thb_spend": 0.0},
        "input_hashes": {"phase7_manifest_sha256": sha256(MANIFEST), "phase7_psb_sample_sha256": sha256(SAMPLE)},
        "analysis_population": {
            "provider_frame": sample["provider_population_size"],
            "certainty_units": sample["certainty_count"],
            "probability_sample_units": sample["probability_sample_size"],
            "analysis_units": len(units),
            "not_applicable_rows_outside_provider_frame": sample["not_applicable_size"],
        },
        "primary_confirmatory_estimate": {
            "metric": "valid_allowlisted_action_rate",
            "estimand": "rate in the frozen 4,104-row provider frame",
            "estimator": "Horvitz-Thompson with stratified finite-population variance",
            "estimate": estimate,
            "standard_error": se,
            "approximate_95_ci": [max(0.0, estimate - 1.96 * se), min(1.0, estimate + 1.96 * se)],
        },
        "design_weighted_selected_action_distribution_by_model_condition": distributions,
        "observed_units_by_model": dict(sorted(Counter(unit["model_id"] for unit in units).items())),
        "observed_units_by_condition": dict(sorted(Counter(unit["condition"] for unit in units).items())),
        "phase4_selected_action_outcomes": physical_estimates,
        "phase4_structural_join": {"scenario_input_packages": sorted(scenario_ids), "status": "passed", "frozen_seed_groups_per_selected_action": 5},
        "phase5_action_level_status_counts": dict(sorted(legal_statuses.items())),
        "not_estimable": {
            "metrics": ["prohibited_action_selection_rate", "road_compliance_rate", "unsupported_legal_claim_rate", "law_responsive_differentiation_rate"],
            "reason": "All frozen Phase 5 action-level decisions are NOT_DETERMINED; no action-level legal label may be inferred.",
        },
        "paired_contrast_status": "not_confirmatory: the probability sample was not designed as a paired legal-contrast panel",
        "claim_boundary": "Behavioral, scenario-based results only; not evidence of legal understanding, culture, moral value, or safety certification.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "analysis_units": len(units), "output": str(OUTPUT.relative_to(ROOT))}, sort_keys=True))


if __name__ == "__main__":
    main()
