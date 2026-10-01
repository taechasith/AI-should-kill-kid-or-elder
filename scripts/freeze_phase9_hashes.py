"""Hash the deterministic Phase 9 evidence package, excluding this self-manifest."""
from __future__ import annotations
import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = [
 "data/analysis/phase9/phase9_input_manifest.json","data/analysis/phase9/phase9_claim_registry.json","data/analysis/phase9/phase9_prohibited_claims.json","data/analysis/phase9/phase9_final_results.json","data/analysis/phase9/phase9_final_results.csv","data/analysis/phase9/phase9_integrity_report.json","data/analysis/phase9/phase9_validation.json","data/analysis/phase9/tables/table1.csv","data/analysis/phase9/tables/table2.csv","data/analysis/phase9/tables/table3.csv","data/analysis/phase9/tables/table4.csv","data/analysis/phase9/tables/table5.csv","data/analysis/phase9/tables/table6.csv","data/analysis/phase9/tables/table7.csv","data/analysis/phase9/figures/figure1_population_flow.svg","data/analysis/phase9/figures/figure2_interface_reliability.svg","data/analysis/phase9/figures/figure3_action_distribution.svg","data/analysis/phase9/figures/figure4_estimability.svg","docs/PHASE9_SYNTHESIS.md","docs/PHASE9_PAPER_RESULTS.md","docs/PHASE9_PAPER_METHODS.md","docs/PHASE9_LIMITATIONS.md","docs/PHASE9_REPRODUCIBILITY.md","scripts/build_phase9_scaffold.py","scripts/build_phase9_synthesis.py","scripts/freeze_phase9_hashes.py","scripts/validate_phase9_synthesis.py","tests/test_phase9_synthesis.py"]
def main():
    output=ROOT/"data/analysis/phase9/phase9_hashes.sha256"; lines=[]
    for name in FILES:
        path=ROOT/name
        if not path.is_file(): raise SystemExit(f"missing Phase 9 artifact: {name}")
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}")
    output.write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    print(f"Phase 9 hashes written: {len(lines)} artifacts; self excluded")
if __name__=="__main__": main()
