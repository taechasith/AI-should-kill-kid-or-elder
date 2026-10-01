"""Read-only Phase 8A analysis helpers for the frozen Phase 7 PSB dataset.

This module deliberately contains no provider client or request logic.  It
keeps design-weighted population estimates separate from descriptive summaries
of the observed units and refuses to turn ``NOT_DETERMINED`` legal records into
legal-compliance labels.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def terminal_records(attempts_root: Path) -> dict[str, dict[str, Any]]:
    """Return the one successful terminal record for each completed run ID."""
    found: dict[str, dict[str, Any]] = {}
    for path in attempts_root.glob("**/*.json"):
        import json
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("http_status") != 200 or record.get("status") != "completed":
            continue
        run_id = record["run_id"]
        if run_id in found:
            raise ValueError(f"multiple terminal records for {run_id}")
        found[run_id] = record
    return found


def units_with_results(sample: dict[str, Any], manifest: dict[str, Any], records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Join frozen manifest metadata, sampling units, and terminal outputs."""
    by_id = {row["run_id"]: row for row in manifest["rows"]}
    units = sample["certainty_units"] + sample["probability_sample_units"]
    result: list[dict[str, Any]] = []
    for unit in units:
        run_id = unit["run_id"]
        if run_id not in by_id or run_id not in records:
            raise ValueError(f"missing frozen manifest or terminal result for {run_id}")
        row, record = by_id[run_id], records[run_id]
        result.append({
            "run_id": run_id,
            "model_id": row["model_id"],
            "provider": row["provider"],
            "condition": row["condition"],
            "country_iso3": row["country_iso3"],
            "input_package_id": row["input_package_id"],
            "repeat_index": row["repeat_index"],
            "inclusion_probability": unit["inclusion_probability"],
            "base_weight": unit["base_weight"],
            "sampling_role": "probability_sample" if unit["probability_sample"] else "certainty",
            "selected_action_id": record.get("selected_action_id"),
            "allowlisted_action_valid": bool(record.get("allowlisted_action_valid")),
            "format_compliance": bool(record.get("format_compliance")),
            "normalization_success": bool(record.get("normalization_success")),
        })
    return result


def weighted_action_distribution(units: list[dict[str, Any]]) -> dict[str, float]:
    """HT action shares for a known finite domain represented by *units*."""
    total_weight = sum(unit["base_weight"] for unit in units)
    if total_weight <= 0:
        raise ValueError("empty weighted domain")
    totals: dict[str, float] = defaultdict(float)
    for unit in units:
        action = unit["selected_action_id"]
        if action is not None:
            totals[action] += unit["base_weight"]
    return {action: value / total_weight for action, value in sorted(totals.items())}


def observed_counts(units: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(unit[key]) for unit in units).items()))
