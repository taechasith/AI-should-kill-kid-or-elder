from __future__ import annotations

import json
from pathlib import Path

from scripts.build_phase5_query_universe import build_queries


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_query_universe_is_exhaustive_and_preserves_unknown_context() -> None:
    config = load(ROOT / "configs" / "legal" / "phase5_two_level_v1.json")
    overlay = load(ROOT / "data" / "legal" / "phase5" / "legal_context_overlay_v1.json")
    rows = build_queries(config, overlay)

    assert len(rows) == 900
    assert len({row["query_id"] for row in rows}) == 900
    assert {row["country_iso3"] for row in rows} == {
        entry["country_iso3"] for entry in config["deep_law_layer"]["selection_frame"]
    }
    assert {row["initial_speed_kph"] for row in rows} == {30, 50}
    assert all(row["road_context"]["lane_marking_type"] == "not_specified" for row in rows)
    assert all(row["query_status"] == "pending_primary_source_verification" for row in rows)


def test_overlay_does_not_claim_unobserved_legal_facts() -> None:
    overlay = load(ROOT / "data" / "legal" / "phase5" / "legal_context_overlay_v1.json")
    assert overlay["physical_benchmark"]["read_only"] is True
    assert overlay["global_assumptions"]["posted_speed_limit"] == "not_specified"
    assert overlay["scenarios"]["PED-CROSS-001"]["legal_facts"]["pedestrian_crossing_designation"] == "not_specified"
