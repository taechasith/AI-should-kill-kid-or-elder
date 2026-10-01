import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_claims_trace_to_frozen_results():
    ids={r["result_id"] for r in json.loads((ROOT/"data/analysis/phase8a/phase8a_results.json").read_text())["results"]}
    claims=json.loads((ROOT/"data/analysis/phase9/phase9_claim_registry.json").read_text())["claims"]
    assert len(claims)==13 and all(c["source_result_id"] in ids for c in claims)
def test_legal_boundary_remains_blocked():
    results=json.loads((ROOT/"data/analysis/phase8a/phase8a_results.json").read_text())["results"]
    assert next(r for r in results if r["result_id"]=="P8A-LEGAL-001")["estimability"]=="NOT_ESTIMABLE"
def test_synthesis_is_offline_and_not_a_simulation_runner():
    source=(ROOT/"scripts/build_phase9_synthesis.py").read_text(encoding="utf-8")
    assert "requests" not in source and "urllib" not in source and "simulator.commonroad" not in source
