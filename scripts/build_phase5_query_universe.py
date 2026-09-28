"""Build the exhaustive Phase 5 legal-query universe without assigning law."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "legal" / "phase5_two_level_v1.json"
OVERLAY = ROOT / "data" / "legal" / "phase5" / "legal_context_overlay_v1.json"
OUTPUT = ROOT / "data" / "legal" / "phase5" / "legal_queries.jsonl"
EVALUATION_DATE = "2026-09-28"
SPEEDS = (30, 50)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_queries(config: dict, overlay: dict) -> list[dict]:
    jurisdictions = config["deep_law_layer"]["selection_frame"]
    actions = overlay["actions"]
    scenarios = overlay["scenarios"]
    rows: list[dict] = []
    for jurisdiction in jurisdictions:
        for scenario_id, scenario in scenarios.items():
            for speed_kph in SPEEDS:
                for action_id, action in actions.items():
                    query_id = f"P5Q-{jurisdiction['country_iso3']}-{scenario_id}-V{speed_kph:03d}-{action_id}"
                    rows.append({
                        "schema_version": "phase5-legal-query-v1",
                        "query_id": query_id,
                        "country_iso3": jurisdiction["country_iso3"],
                        "country_name": jurisdiction["country"],
                        "subnational_code": None,
                        "scenario_id": scenario_id,
                        "scenario_version": "v1",
                        "initial_speed_kph": speed_kph,
                        "action_id": action_id,
                        "action_label": action["label"],
                        "legal_maneuver": action["legal_maneuver"],
                        "evaluation_date": EVALUATION_DATE,
                        "overlay_id": overlay["overlay_id"],
                        "road_context": overlay["global_assumptions"],
                        "scenario_legal_facts": scenario["legal_facts"],
                        "question_categories": scenario["question_categories"],
                        "query_status": "pending_primary_source_verification",
                    })
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows).encode("utf-8"))


def main() -> None:
    # Reject a malformed frozen date before a data artifact is written.
    date.fromisoformat(EVALUATION_DATE)
    rows = build_queries(load_json(CONFIG), load_json(OVERLAY))
    if len(rows) != 25 * 3 * 2 * 6:
        raise ValueError(f"expected 900 Phase 5 legal queries, got {len(rows)}")
    write_jsonl(OUTPUT, rows)
    print(f"Wrote {len(rows)} Phase 5 legal queries to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
