"""Outcome-blind finite-population sampling for the Phase 7 provider frame."""
from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import variance

PROVIDER_STATE = "pending_zero_cost_authorization"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def provider_rows(manifest: dict) -> list[dict]:
    return [row for row in manifest["rows"] if row["execution_state"] == PROVIDER_STATE]


def terminal_success_ids(attempts_root: Path) -> set[str]:
    """Read only completion status and run IDs, never substantive model fields."""
    completed: set[str] = set()
    for path in attempts_root.glob("**/*.json"):
        record = load_json(path)
        if record.get("http_status") == 200 and record.get("status") == "completed":
            completed.add(record["run_id"])
    return completed


def stratum_key(row: dict) -> str:
    return f"{row['model_id']}|{row['condition']}"


def build_sample(manifest: dict, certainty_ids: set[str], *, seed: int, per_stratum: int) -> dict:
    """Draw stratified SRSWOR from unobserved rows; completed rows are certainty units."""
    frame = provider_rows(manifest)
    frame_ids = {row["run_id"] for row in frame}
    certainty_ids = certainty_ids & frame_ids
    remaining = [row for row in frame if row["run_id"] not in certainty_ids]
    strata: dict[str, list[dict]] = defaultdict(list)
    for row in remaining:
        strata[stratum_key(row)].append(row)
    rng = random.Random(seed)
    selected: list[dict] = []
    allocations: list[dict] = []
    for key in sorted(strata):
        population = sorted(strata[key], key=lambda row: row["run_id"])
        n_h = min(per_stratum, len(population))
        chosen_ids = {row["run_id"] for row in rng.sample(population, n_h)}
        pi = n_h / len(population)
        allocations.append({"stratum": key, "remaining_population": len(population), "sample_size": n_h, "inclusion_probability": pi})
        for row in population:
            if row["run_id"] in chosen_ids:
                selected.append({
                    "run_id": row["run_id"], "stratum": key, "inclusion_probability": pi,
                    "base_weight": 1.0 / pi, "probability_sample": True, "contrast_panel": False,
                })
    certainty = [{"run_id": run_id, "inclusion_probability": 1.0, "base_weight": 1.0,
                  "probability_sample": False, "contrast_panel": False}
                 for run_id in sorted(certainty_ids)]
    result = {
        "schema_version": "phase7-psb-v1",
        "sampling_design": "stratified_simple_random_sampling_without_replacement",
        "rng_algorithm": "Python random.Random (Mersenne Twister)",
        "rng_seed": seed,
        "provider_population_size": len(frame),
        "full_manifest_size": len(manifest["rows"]),
        "not_applicable_size": sum(row["execution_state"] == "not_applicable" for row in manifest["rows"]),
        "certainty_count": len(certainty),
        "remaining_population_size": len(remaining),
        "probability_sample_size": len(selected),
        "strata": allocations,
        "certainty_units": certainty,
        "probability_sample_units": sorted(selected, key=lambda row: row["run_id"]),
        "contrast_panel_units": [],
    }
    result["population_frame_sha256"] = hashlib.sha256(canonical_bytes(frame)).hexdigest()
    result["selection_payload_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def validate_sample(sample: dict, manifest: dict) -> list[str]:
    errors: list[str] = []
    frame = provider_rows(manifest)
    frame_ids = {row["run_id"] for row in frame}
    if len(frame) != 4104:
        errors.append("provider population must equal 4104")
    if sample["provider_population_size"] != len(frame):
        errors.append("population size mismatch")
    if sample["certainty_count"] + sample["remaining_population_size"] != len(frame):
        errors.append("certainty and remaining population do not partition frame")
    observed: set[str] = set()
    for group in ("certainty_units", "probability_sample_units", "contrast_panel_units"):
        for unit in sample[group]:
            run_id = unit["run_id"]
            if run_id not in frame_ids:
                errors.append(f"unknown run id: {run_id}")
            if group != "contrast_panel_units" and run_id in observed:
                errors.append(f"duplicate run id: {run_id}")
            observed.add(run_id)
            if not 0 < unit["inclusion_probability"] <= 1:
                errors.append(f"invalid inclusion probability: {run_id}")
    if any(unit["inclusion_probability"] != 1 for unit in sample["certainty_units"]):
        errors.append("certainty units must have pi=1")
    if any(unit["base_weight"] != 1 / unit["inclusion_probability"] for unit in sample["probability_sample_units"]):
        errors.append("probability-sample weights are invalid")
    return errors


def ht_rate(sample: dict, outcomes: dict[str, int]) -> float:
    """Finite-population Horvitz--Thompson rate for supplied binary outcomes."""
    total = 0.0
    for unit in sample["certainty_units"] + sample["probability_sample_units"]:
        if unit["run_id"] not in outcomes:
            raise KeyError(f"missing outcome for {unit['run_id']}")
        total += outcomes[unit["run_id"]] / unit["inclusion_probability"]
    return total / sample["provider_population_size"]


def stratified_ht_variance(sample: dict, outcomes: dict[str, int]) -> float:
    """Unbiased SRSWOR variance estimator for the HT rate; certainty variance is zero."""
    by_stratum: dict[str, list[dict]] = defaultdict(list)
    for unit in sample["probability_sample_units"]:
        by_stratum[unit["stratum"]].append(unit)
    total_variance = 0.0
    allocation = {row["stratum"]: row for row in sample["strata"]}
    for key, units in by_stratum.items():
        n_h = len(units)
        N_h = allocation[key]["remaining_population"]
        if n_h < 2 or N_h <= 1:
            continue
        values = [outcomes[unit["run_id"]] for unit in units]
        total_variance += N_h**2 * (1 - n_h / N_h) * variance(values) / n_h
    return total_variance / sample["provider_population_size"]**2
