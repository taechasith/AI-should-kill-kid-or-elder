"""Offline integrity checks for the Phase 9 evidence package."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data/analysis/phase9"
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def main():
    errors=[]; inputs=load(OUT/"phase9_input_manifest.json"); p8=ROOT/inputs["phase8a"]["results"]
    if hashlib.sha256((ROOT/inputs["phase8a"]["hash_manifest"]).read_bytes()).hexdigest()!=inputs["phase8a"]["hash_manifest_sha256"]: errors.append("Phase 8A hash manifest mismatch")
    results=load(p8); ids={x["result_id"] for x in results["results"]}; claims=load(OUT/"phase9_claim_registry.json")["claims"]
    if any(x["source_result_id"] not in ids for x in claims): errors.append("claim without a Phase 8A result")
    if len({x["claim_id"] for x in claims})!=len(claims): errors.append("duplicate claim ID")
    by_id={x["result_id"]:x for x in results["results"]}
    for claim in claims:
        source=by_id[claim["source_result_id"]]
        if claim["estimate"] != source.get("weighted_estimate") or claim["interval"] != source.get("approximate_95_ci"):
            errors.append(f"claim numeric evidence mismatch: {claim['claim_id']}")
    legal=next(x for x in results["results"] if x["result_id"]=="P8A-LEGAL-001")
    if legal["estimability"]!="NOT_ESTIMABLE": errors.append("legal metric not blocked")
    paper=(ROOT/"docs/PHASE9_PAPER_RESULTS.md").read_text(encoding="utf-8")
    expected_text=("82.38%", "73.40%", "91.36%", "62.37%", "25.41%", "81.87%", "82.07%", "3.106 m", "not estimable")
    if any(token not in paper for token in expected_text): errors.append("paper Results evidence lacks an expected frozen numeric/boundary claim")
    for line in (OUT/"phase9_hashes.sha256").read_text(encoding="utf-8").splitlines():
        expected,name=line.split("  ",1)
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected: errors.append(f"Phase 9 hash mismatch: {name}")
    for name in ("scripts/build_phase9_scaffold.py","scripts/build_phase9_synthesis.py"):
        source=(ROOT/name).read_text(encoding="utf-8")
        if "requests" in source or "urllib" in source or "simulator.commonroad" in source: errors.append(f"forbidden provider/simulation dependency: {name}")
    if errors: raise SystemExit("Phase 9 validation failed:\n"+"\n".join(errors))
    print(f"Phase 9 evidence package: valid ({len(claims)} claims)")
if __name__=="__main__": main()
