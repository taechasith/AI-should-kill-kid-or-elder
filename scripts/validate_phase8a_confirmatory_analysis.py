"""Validate the immutable-input and claim-boundary gates of Phase 8A."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/analysis/phase8a/phase8a_confirmatory_report.json"
MANIFEST = ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json"
SAMPLE = ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    errors = []
    if report.get("execution") != {"provider_calls": 0, "usd_spend": 0.0, "thb_spend": 0.0}:
        errors.append("Phase 8A must make no provider calls or spend money")
    if report.get("analysis_population", {}).get("analysis_units") != 339:
        errors.append("expected 279 certainty plus 60 probability-sample units")
    if report.get("phase5_action_level_status_counts") != {"NOT_DETERMINED": 900}:
        errors.append("frozen Phase 5 legal scope is not represented correctly")
    forbidden = {"prohibited_action_selection_rate", "road_compliance_rate", "unsupported_legal_claim_rate"}
    if not forbidden <= set(report.get("not_estimable", {}).get("metrics", [])):
        errors.append("legal-scope limitation missing")
    if report.get("phase4_structural_join", {}).get("status") != "passed":
        errors.append("Phase 4 structural join failed")
    physical = report.get("phase4_selected_action_outcomes", {})
    if {"collision_free_all_seeds", "trajectory_feasible_all_seeds", "road_boundary_compliant_all_seeds", "minimum_clearance_m_across_seeds"} - set(physical):
        errors.append("required selected-action physical outcomes missing")
    if physical.get("missing_selected_action_units", 0) <= 0:
        errors.append("expected invalid outputs to remain visible in physical join accounting")
    expected_hashes = {"phase7_manifest_sha256": sha256(MANIFEST), "phase7_psb_sample_sha256": sha256(SAMPLE)}
    if report.get("input_hashes") != expected_hashes:
        errors.append("frozen Phase 7 input hashes do not match")
    if errors:
        raise SystemExit("; ".join(errors))
    print("Phase 8A confirmatory analysis: valid")


if __name__ == "__main__":
    main()
