"""Validate a frozen Phase 7 population-sampling manifest without provider access."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase7_population_sampling import load_json, validate_sample

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, default=ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json")
    args = parser.parse_args()
    manifest = load_json(ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json")
    errors = validate_sample(load_json(args.sample), manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    print("phase7 population-sampling manifest: valid")

if __name__ == "__main__":
    main()
