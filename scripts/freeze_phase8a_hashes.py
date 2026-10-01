"""Write SHA-256 checksums for the generated Phase 8A snapshot (self excluded)."""
from __future__ import annotations
import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "data/analysis/phase8a/phase8a_input_manifest.json", "data/analysis/phase8a/phase8a_known_before_analysis.json", "data/analysis/phase8a/phase8a_metric_registry.json", "data/analysis/phase8a/phase8a_comparison_registry.json", "data/analysis/phase8a/phase8a_blocked_legal_metrics.json", "data/analysis/phase8a/phase8a_results.json", "data/analysis/phase8a/phase8a_results.csv", "data/analysis/phase8a/phase8a_validation.json", "data/analysis/phase8a/figures/phase8a_overall_action_distribution.svg", "docs/PHASE8A_ANALYSIS_PLAN.md", "docs/PHASE8A_RESULTS.md", "docs/PHASE8A_LIMITATIONS.md", "docs/PHASE8A_REPRODUCIBILITY.md", "geosave/phase8a_analysis.py", "scripts/build_phase8a_input_manifest.py", "scripts/run_phase8a_analysis.py", "scripts/generate_phase8a_docs.py", "scripts/validate_phase8a_analysis.py", "scripts/freeze_phase8a_hashes.py", "tests/test_phase8a_analysis.py",
]
def main() -> None:
    output = ROOT / "data/analysis/phase8a/phase8a_hashes.sha256"
    rows = []
    for name in FILES:
        path = ROOT / name
        if not path.is_file(): raise SystemExit(f"missing Phase 8A artifact: {name}")
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}")
    output.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"Phase 8A hashes written: {output.relative_to(ROOT)} ({len(rows)} artifacts; self excluded)")
if __name__ == "__main__": main()
