"""Deterministic, offline analysis helpers for the frozen Phase 8A snapshot."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import variance


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def git_blob_bytes(root: Path, revision: str, relative: str) -> bytes:
    result = subprocess.run(["git", "show", f"{revision}:{relative}"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout


def verify_hash_manifest(root: Path, manifest_path: Path, *, revision: str | None = None) -> list[str]:
    manifest = load_json(manifest_path)
    expected = manifest.get("artifacts", manifest.get("files", {}))
    errors: list[str] = []
    for relative, digest in sorted(expected.items()):
        try:
            actual = hashlib.sha256(git_blob_bytes(root, revision, relative)).hexdigest() if revision else sha256_file(root / relative)
        except (OSError, subprocess.CalledProcessError):
            errors.append(f"missing hashed artifact: {relative}")
            continue
        if actual != digest:
            errors.append(f"hash mismatch: {relative}")
    return errors


def ht_rate(sample: dict, values: dict[str, float]) -> float:
    total = sum(values[unit["run_id"]] / unit["inclusion_probability"]
                for group in ("certainty_units", "probability_sample_units")
                for unit in sample[group])
    return total / sample["provider_population_size"]


def stratified_ht_variance(sample: dict, values: dict[str, float]) -> float:
    """SRSWOR HT variance for a finite-population mean; certainty term is zero."""
    allocations = {row["stratum"]: row for row in sample["strata"]}
    groups: dict[str, list[dict]] = defaultdict(list)
    for unit in sample["probability_sample_units"]:
        groups[unit["stratum"]].append(unit)
    total = 0.0
    for key, units in groups.items():
        n_h = len(units)
        n_population = allocations[key]["remaining_population"]
        if n_h > 1 and n_population > 1:
            y = [values[unit["run_id"]] for unit in units]
            total += n_population ** 2 * (1 - n_h / n_population) * variance(y) / n_h
    return total / sample["provider_population_size"] ** 2


def estimate_binary(sample: dict, values: dict[str, int]) -> dict:
    estimate = ht_rate(sample, values)
    standard_error = math.sqrt(stratified_ht_variance(sample, values))
    return {
        "estimator": "Horvitz-Thompson finite-population rate; stratified SRSWOR variance with FPC",
        "raw_numerator": sum(values.values()),
        "raw_denominator": len(values),
        "weighted_estimate": estimate,
        "standard_error": standard_error,
        "approximate_95_ci": [max(0.0, estimate - 1.96 * standard_error), min(1.0, estimate + 1.96 * standard_error)],
    }


def assert_unique(records: list[dict], field: str) -> None:
    seen: set[object] = set()
    for record in records:
        value = record[field]
        if value in seen:
            raise ValueError(f"duplicate {field}: {value}")
        seen.add(value)
