"""Build Phase 9's frozen input, claim, and prohibited-claim registries offline."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/analysis/phase9"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_ref(ref: str) -> str:
    return subprocess.check_output(["git", "rev-parse", ref], cwd=ROOT, text=True).strip()


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    phase8_hashes = ROOT / "data/analysis/phase8a/phase8a_hashes.sha256"
    expected_manifest_hash = "f02bd010286d6b3c965081b878419ccfde26e6106fc92709f983d7afcc7242a8"
    if digest(phase8_hashes) != expected_manifest_hash:
        raise SystemExit("Phase 8A manifest hash mismatch")
    mismatches = []
    for line in phase8_hashes.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        if digest(ROOT / relative) != expected:
            mismatches.append(relative)
    if mismatches:
        raise SystemExit("Phase 8A artifact hash mismatch: " + ", ".join(mismatches))
    results_path = ROOT / "data/analysis/phase8a/phase8a_results.json"
    results = json.loads(results_path.read_text(encoding="utf-8"))
    by_id = {row["result_id"]: row for row in results["results"]}
    inputs = {
        "schema_version": "phase9-input-manifest-v1",
        "offline_only": True,
        "phase4": {"canonical_data_commit": "d52baab", "tag": "commonroad-pilot-v1", "hash_manifest": "data/simulator/commonroad/hashes/commonroad_pilot_v1_sha256.json", "hash_manifest_sha256": digest(ROOT / "data/simulator/commonroad/hashes/commonroad_pilot_v1_sha256.json")},
        "phase5": {"tag": "phase5-legal-snapshot-v1", "commit": git_ref("phase5-legal-snapshot-v1"), "hash_manifest": "data/legal/phase5/hashes/phase5_legal_snapshot_v1_sha256.json", "hash_manifest_sha256": digest(ROOT / "data/legal/phase5/hashes/phase5_legal_snapshot_v1_sha256.json")},
        "phase6": {"tag": "phase6-literature-v2-pilot-v1", "commit": git_ref("phase6-literature-v2-pilot-v1"), "interface_report": "docs/PHASE_6_V2_PILOT_REPORT.md"},
        "phase7": {"recovered_tag": "phase7-population-sample-recovered-v1", "recovered_commit": git_ref("phase7-population-sample-recovered-v1"), "sampling_manifest": "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json", "execution_report": "data/model_benchmark/phase7_population_sample_v1/reports/phase7_psb_v1_execution_report.json"},
        "phase8a": {"tag": "phase8a-confirmatory-analysis-v1", "completion_commit": git_ref("phase8a-confirmatory-analysis-v1"), "analysis_plan_commit": "548132630503dd2e98159e2677d59ac6bd9cf407", "results": str(results_path.relative_to(ROOT)).replace("\\", "/"), "results_sha256": digest(results_path), "hash_manifest": str(phase8_hashes.relative_to(ROOT)).replace("\\", "/"), "hash_manifest_sha256": expected_manifest_hash},
        "phase6_7_qwen_provenance": {"provider": "Groq", "model": "qwen/qwen3.8-27b", "historical_protocol_validity": "RETAIN", "v2a_openrouter_compliance": "NOT_APPLICABLE_TO_HISTORICAL_RUN"},
        "software": results["software"],
    }
    def claim(claim_id: str, wording: str, result_id: str, claim_type: str, limitations: list[str]) -> dict:
        row = by_id[result_id]
        return {"claim_id": claim_id, "claim": wording, "claim_type": claim_type, "source_result_id": result_id, "source_file": "data/analysis/phase8a/phase8a_results.json", "population": "provider-execution population (4,104)" if row["kind"] != "blocked" else "not applicable", "raw_numerator": row.get("raw_numerator"), "raw_denominator": row.get("raw_denominator"), "weighted_or_unweighted": "weighted" if row.get("weighted_estimate") is not None else "not applicable", "estimate": row.get("weighted_estimate"), "interval": row.get("approximate_95_ci"), "analysis_design": row.get("estimator"), "allowed_strength": "descriptive population estimate" if row.get("estimability") == "ESTIMABLE" else row.get("estimability"), "limitations": limitations}
    claims = [
        claim("C-P9-001", "Models produced a valid allowlisted explicit action in an estimated 82.38% of the frozen provider-execution population.", "P8A-INTERFACE-003", "confirmatory", ["Design-weighted finite-population estimate, not a census.", "Approximate interval is design-based."]),
        claim("C-P9-002", "Strict JSON formatting was an independent secondary reliability metric, estimated at 62.37%.", "P8A-INTERFACE-004", "confirmatory", ["Strict JSON validity is not synonymous with explicit decision validity."]),
        claim("C-P9-003", "The valid-action-linked Phase 4 collision mean was 25.41%.", "P8A-PHYSICAL-COLLISION", "confirmatory", ["Each linked physical scalar is an arithmetic mean across five frozen Phase 4 seeds.", "This is not jurisdictional legal compliance."]),
        claim("C-P9-004", "The valid-action-linked Phase 4 physical-feasibility mean was 81.87%.", "P8A-PHYSICAL-FEASIBLE", "confirmatory", ["No physical scalar interval was pre-specified for this conditional quantity."]),
        claim("C-P9-005", "The valid-action-linked map/road-compliance mean was 82.07%.", "P8A-PHYSICAL-ROAD_COMPLIANT", "confirmatory", ["Map/road compliance is a physical benchmark metric and must not be called legal compliance."]),
        claim("C-P9-006", "The base-weighted conditional mean minimum distance for valid actions was 3.106 m.", "P8A-PHYSICAL-MIN-DISTANCE", "confirmatory", ["Descriptive conditional mean; no ratio-variance interval was pre-specified."]),
        claim("C-P9-007", "Jurisdictional legal-compliance quantities are not estimable from the frozen Phase 5 v1 scope.", "P8A-LEGAL-001", "scope_boundary", ["Phase 5 action-level legal determinations are NOT_DETERMINED; no imputation occurred."]),
    ]
    for action in ("A0", "A1", "A2", "A3", "A4", "A6"):
        row = by_id[f"P8A-ACTION-{action}"]
        claims.append(claim(f"C-P9-ACTION-{action}", f"The design-weighted joint selected-action rate for {action} was {100 * row['weighted_estimate']:.2f}%.", row["result_id"], "confirmatory", ["Joint with valid allowlisted extraction; invalid/no-action records are not reassigned."]))
    prohibited = {"schema_version": "phase9-prohibited-claims-v1", "rules": [
        {"category": "unavailable_legal_inference", "status": "PROHIBITED", "phrases": ["legally compliant", "violates the law", "illegal in", "lawful in", "jurisdiction ranking"], "reason": "Frozen Phase 5 v1 action-level legal status is NOT_DETERMINED."},
        {"category": "unsupported_model_ranking", "status": "PROHIBITED", "phrases": ["safest model", "most ethical model", "best model"], "reason": "Phase 8A has no model-ranking inferential design."},
        {"category": "demographic_moral_preference", "status": "PROHIBITED", "phrases": ["prefers children over elders", "proves moral preference"], "reason": "No demographic human-value weighting or Phase 8B audit is included."},
        {"category": "sampling_overstatement", "status": "PROHIBITED", "phrases": ["census", "all 4,104 responses"], "reason": "279 certainty units plus 60 probability-sampled units are not a census."},
        {"category": "format_semantics_conflation", "status": "PROHIBITED", "phrases": ["strict JSON failure equals decision failure"], "reason": "Frozen interface protocol separates formatting from explicit action validity."},
        {"category": "causality", "status": "PROHIBITED", "phrases": ["caused", "proves that"], "reason": "The frozen design supports descriptive estimates, not causal claims."}
    ]}
    write(OUT / "phase9_input_manifest.json", inputs)
    write(OUT / "phase9_claim_registry.json", {"schema_version": "phase9-claim-registry-v1", "claims": claims})
    write(OUT / "phase9_prohibited_claims.json", prohibited)
    print(f"Phase 9 scaffold written with {len(claims)} claims")

if __name__ == "__main__":
    main()
