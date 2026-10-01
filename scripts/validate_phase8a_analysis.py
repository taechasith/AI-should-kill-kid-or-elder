"""Offline validation for the frozen Phase 8A analysis outputs."""
from __future__ import annotations
import json, sys
import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase8a_analysis import load_json, sha256_file, verify_hash_manifest

def main() -> None:
    errors = []
    for name, revision in (("data/simulator/commonroad/hashes/commonroad_pilot_v1_sha256.json", "36deb29"), ("data/legal/phase5/hashes/phase5_legal_snapshot_v1_sha256.json", "phase5-legal-snapshot-v1"), ("data/model_benchmark/phase6_literature_v2/hashes/phase6_literature_v2_pilot_sha256.json", "phase6-literature-v2-pilot-v1"), ("data/model_benchmark/phase7_population_sample_v1/hashes/phase7_psb_v1_protocol_sha256.json", "99551fa")):
        errors.extend(verify_hash_manifest(ROOT, ROOT / name, revision=revision))
    inputs = load_json(ROOT / "data/analysis/phase8a/phase8a_input_manifest.json")
    result = load_json(ROOT / "data/analysis/phase8a/phase8a_results.json")
    a = result["accounting"]
    if a["design_accounted"] != a["provider_execution_population"] + a["not_applicable"]: errors.append("design accounting does not reconcile")
    if (a["certainty_observations"], a["probability_sample_observations"], a["analysis_observations"]) != (279, 60, 339): errors.append("sample accounting mismatch")
    if len({x["run_id"] for x in inputs["selected_observation_provenance"]}) != 339: errors.append("duplicate/missing selected IDs")
    valid = next(x for x in result["results"] if x["result_id"] == "P8A-INTERFACE-003")
    if abs(valid["weighted_estimate"] - 0.8238304093567251) > 1e-12: errors.append("valid-action estimate is not reproduced")
    legal = next(x for x in result["results"] if x["result_id"] == "P8A-LEGAL-001")
    if legal["estimability"] != "NOT_ESTIMABLE": errors.append("legal metrics are not blocked")
    checksum = ROOT / "data/analysis/phase8a/phase8a_hashes.sha256"
    if not checksum.is_file(): errors.append("missing Phase 8A hash manifest")
    else:
        for line in checksum.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest: errors.append(f"Phase 8A hash mismatch: {relative}")
    if any(x.get("result_id", "").startswith("P8A-PHYSICAL") and x.get("estimability") == "NOT_ESTIMABLE" for x in result["results"]): errors.append("unexpected physical blocking")
    if errors: raise SystemExit("Phase 8A validation failed:\n" + "\n".join(errors))
    print("Phase 8A frozen analysis: valid")

if __name__ == "__main__": main()
