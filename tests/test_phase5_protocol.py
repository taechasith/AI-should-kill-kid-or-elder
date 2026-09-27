from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_phase5_protocol import validate_protocol


ROOT = Path(__file__).resolve().parents[1]


def test_two_level_protocol_preserves_source_boundaries() -> None:
    with (ROOT / "configs" / "legal" / "phase5_two_level_v1.json").open(encoding="utf-8") as handle:
        payload = json.load(handle)

    validate_protocol(payload)
    assert payload["global_context_layer"]["authority"] == "World Health Organization"
    assert payload["international_regulatory_layer"]["not_domestic_law_by_default"] is True
    assert len(payload["deep_law_layer"]["selection_frame"]) == 25


def test_protocol_rejects_unsafe_who_or_unknown_law_boundary() -> None:
    payload = {
        "schema_version": "phase5-two-level-v1",
        "status": "collection_protocol_frozen_pending_evidence_review",
        "global_context_layer": {"prohibited_uses": [], "missing_value": None},
        "international_regulatory_layer": {"not_domestic_law_by_default": True},
        "deep_law_layer": {
            "target_jurisdiction_count": 25,
            "selection_frame": [{"country_iso3": f"A{index:02d}"} for index in range(25)],
            "unknown_law_rule": "unknown evidence is lawful",
        },
    }

    try:
        validate_protocol(payload)
    except ValueError as error:
        assert "WHO context boundary" in str(error)
    else:
        raise AssertionError("unsafe source boundary was accepted")
