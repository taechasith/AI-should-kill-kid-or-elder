"""Design-weighted Phase 7 PSB analysis from a post-freeze binary outcome map."""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase7_population_sampling import ht_rate, load_json, stratified_ht_variance

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--outcomes", type=Path, required=True, help="JSON object of binary scores keyed by run_id")
    args = parser.parse_args()
    sample, outcomes = load_json(args.sample), load_json(args.outcomes)
    estimate = ht_rate(sample, outcomes)
    se = math.sqrt(stratified_ht_variance(sample, outcomes))
    print(json.dumps({"estimator":"Horvitz-Thompson", "estimate":estimate,
                      "standard_error":se, "approximate_95_ci":[max(0, estimate-1.96*se), min(1, estimate+1.96*se)]}, sort_keys=True))

if __name__ == "__main__":
    main()
