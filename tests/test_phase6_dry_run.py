import json
from pathlib import Path

from scripts.finalize_phase6_dry_run import finalize
from scripts.validate_phase6_dry_run import validate
from scripts.verify_phase6_dry_run_hashes import verify


ROOT = Path(__file__).resolve().parents[1]


def test_phase6_dry_run_validator_and_manifest_accounting():
    result = validate()
    assert result["validation_status"] == "passed"
    assert result["provider_calls_made"] == 0
    assert result["full_manifest_rows"] == 5454
    assert result["eligible_provider_calls"] == 4104
    assert result["not_applicable_rows"] == 1350


def test_phase6_hash_manifest_rebuilds_and_verifies():
    finalized = finalize()
    verified = verify()
    assert finalized["files"] == verified["files"]
    assert len(verified["files"]) >= 46
    cost = json.loads((ROOT / "data" / "model_benchmark" / "phase6" / "phase6_dry_run_cost_estimate_v1.json").read_text())
    assert cost["main_matrix"]["estimated_total_usd_without_retry"] == 25.65
