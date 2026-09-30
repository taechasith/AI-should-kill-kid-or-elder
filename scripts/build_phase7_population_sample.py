"""Freeze an outcome-blind Phase 7 probability sample; never calls providers."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase7_population_sampling import build_sample, canonical_bytes, load_json, terminal_success_ids, validate_sample

MANIFEST = ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json"
ATTEMPTS = ROOT / "data/model_benchmark/phase7_literature_v2/attempts"
OUT = ROOT / "data/model_benchmark/phase7_population_sample_v1"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260930)
    parser.add_argument("--per-stratum", type=int, default=5)
    parser.add_argument("--output", type=Path, default=OUT / "manifests/phase7_psb_v1_sample.json")
    args = parser.parse_args()
    sample = build_sample(load_json(MANIFEST), terminal_success_ids(ATTEMPTS), seed=args.seed, per_stratum=args.per_stratum)
    errors = validate_sample(sample, load_json(MANIFEST))
    if errors:
        raise SystemExit("; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(sample) + b"\n")
    print(json.dumps({"output": str(args.output.relative_to(ROOT)), "certainty_count": sample["certainty_count"], "probability_sample_size": sample["probability_sample_size"], "sha256": sample["selection_payload_sha256"]}, sort_keys=True))

if __name__ == "__main__":
    main()
