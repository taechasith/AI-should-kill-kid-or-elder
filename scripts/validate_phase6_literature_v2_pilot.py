"""Validate the bounded, append-only Phase 6 literature-v2 pilot artifacts."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/experiments/phase6_literature_v2_pilot_manifest.json"
OUT = ROOT / "data/model_benchmark/phase6_literature_v2"

def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    rows = manifest["rows"]
    if manifest["row_count"] != 3 or len(rows) != 3:
        raise SystemExit("v2 pilot must contain exactly three frozen rows")
    attempts = []
    for row in rows:
        path = OUT / "attempts" / f"{row['run_id']}.json"
        if not path.is_file(): raise SystemExit(f"missing attempt: {row['run_id']}")
        record = json.loads(path.read_text())
        if record["model_id"] != row["model_id"] or record["provider"] != row["provider"]: raise SystemExit("provider/model mismatch")
        raw = ROOT / record["raw_response_reference"]
        if not raw.is_file() or sha256(raw.read_bytes()).hexdigest() != record["raw_response_sha256"]: raise SystemExit("raw-response hash mismatch")
        if record["http_status"] != 200 or record["retry_count"] != 0: raise SystemExit("pilot must retain one HTTP 200, zero-retry outcome per row")
        if record["allowlisted_action_valid"] is not True: raise SystemExit("pilot action is not unambiguous and allowlisted")
        attempts.append(record)
    if len(list((OUT / "attempts").glob("*.json"))) != 3: raise SystemExit("a fourth pilot attempt exists")
    print("Phase 6 literature-v2 pilot: validated 3 bounded attempts; 3 valid actions; 2 normalized responses")

if __name__ == "__main__": main()
