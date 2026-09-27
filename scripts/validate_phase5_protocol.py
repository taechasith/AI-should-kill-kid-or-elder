"""Validate the frozen boundaries of the Phase 5 two-level collection protocol."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "configs" / "legal" / "phase5_two_level_v1.json"


def validate_protocol(payload: dict) -> None:
    if payload.get("schema_version") != "phase5-two-level-v1":
        raise ValueError("unexpected Phase 5 protocol schema version")
    if payload.get("status") != "collection_protocol_frozen_pending_evidence_review":
        raise ValueError("Phase 5 protocol must not claim completed evidence review")

    global_layer = payload.get("global_context_layer", {})
    prohibited = set(global_layer.get("prohibited_uses", []))
    required_prohibitions = {
        "scenario-level legality classification",
        "substitute for primary law",
        "inference of a legal exception",
        "human-value weighting",
    }
    if not required_prohibitions.issubset(prohibited):
        raise ValueError("WHO context boundary is incomplete")
    if global_layer.get("missing_value", "missing") is not None:
        raise ValueError("global context missing values must be explicit null")

    international = payload.get("international_regulatory_layer", {})
    if international.get("not_domestic_law_by_default") is not True:
        raise ValueError("UNECE layer must not be treated as domestic law by default")

    deep_law = payload.get("deep_law_layer", {})
    selection = deep_law.get("selection_frame", [])
    if deep_law.get("target_jurisdiction_count") != 25 or len(selection) != 25:
        raise ValueError("Deep-Law selection frame must contain exactly 25 jurisdictions")
    iso3 = [entry.get("country_iso3") for entry in selection]
    if any(not isinstance(code, str) or len(code) != 3 or not code.isupper() for code in iso3):
        raise ValueError("selection frame contains an invalid ISO3 identifier")
    if len(set(iso3)) != len(iso3):
        raise ValueError("selection frame contains duplicate jurisdiction identifiers")
    if "NOT_DETERMINED" not in deep_law.get("unknown_law_rule", ""):
        raise ValueError("unknown-law rule must preserve NOT_DETERMINED")


def main() -> None:
    with PROTOCOL_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_protocol(payload)
    print("Phase 5 two-level collection protocol: valid")


if __name__ == "__main__":
    main()
