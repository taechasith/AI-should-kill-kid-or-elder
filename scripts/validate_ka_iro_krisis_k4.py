"""Fail-closed offline validator for the frozen KA-IRO KRISIS v2 K4 panel."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "data" / "ka-iro-krisis" / "v2" / "model"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    path = MODEL_DIR / "k4_model_interface_manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_BEFORE_K5_GENERATION"
    assert value["monetary_policy"]["free_only"] is True
    assert value["monetary_policy"]["budget_usd"] == "0.00"
    assert value["monetary_policy"]["budget_thb"] == "0.00"
    assert value["metadata_preflight"]["metadata_generation_requests"] == 0
    metadata_path = ROOT / value["metadata_preflight"]["path"]
    attestation_path = ROOT / value["account_plan_evidence"]["path"]
    assert digest(metadata_path) == value["metadata_preflight"]["sha256"]
    assert digest(attestation_path) == value["account_plan_evidence"]["sha256"]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["all_target_models_listed"] is True and metadata["model_generation_requests_made"] == 0
    panel = value["panel"]
    assert [row["model_id"] for row in panel] == ["gemini-3.5-flash", "gemini-3.5-flash-lite", "qwen/qwen3.8-27b"]
    assert len({row["provider"] for row in panel}) == 2
    assert all(row["modality"]["input"] == ["text", "image"] for row in panel)
    assert set(value["interfaces"]) == {"NATURAL_EXPLICIT_ACTION", "STRICT_STRUCTURED_OUTPUT"}
    print(json.dumps({"status": "passed", "panel_size": len(panel), "generation_requests_made": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
