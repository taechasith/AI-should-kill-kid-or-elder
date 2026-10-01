"""Build non-final Phase 5 v2 facts, questions, and a human-review queue."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase5_v2 import ACTIONS, SCENARIOS, SPEEDS, UNKNOWN_FIELDS, fact_id, legal_categories, package_id, question_id, read_json, required_fields

V1_CONFIG = ROOT / "configs/legal/phase5_two_level_v1.json"
PACKAGES = ROOT / "data/model_inputs/phase6/phase6_model_interface_v1/packages"
OUTPUT = ROOT / "data/legal/phase5_v2"
LEGAL_SNAPSHOT_DATE = "2026-10-01"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def build() -> None:
    config = read_json(V1_CONFIG)
    jurisdictions = config["deep_law_layer"]["selection_frame"]
    facts: list[dict] = []
    questions: list[dict] = []
    for scenario_id in SCENARIOS:
        scenario = read_json(ROOT / "data/scenarios/commonroad/core" / f"{scenario_id}.yaml")
        for speed in SPEEDS:
            package = read_json(PACKAGES / package_id(scenario_id, speed) / "metadata.json")
            known = {
                "initial_speed_kph": speed,
                "road_length_m": scenario["road"]["length_m"],
                "lane_width_m": scenario["road"]["lane_width_m"],
                "drivable_y_m": scenario["road"]["drivable_y_m"],
                "actor_type": scenario["actor"]["actor_type"],
                "leftward_coordinate_semantics": "positive_y_is_left_in_frozen_geometry",
                "rightward_coordinate_semantics": "negative_y_is_right_in_frozen_geometry",
            }
            for field, value in {**known, **UNKNOWN_FIELDS}.items():
                source = "data/scenarios/commonroad/core/" + scenario_id + ".yaml" if field in known and field != "initial_speed_kph" else "data/model_inputs/phase6/phase6_model_interface_v1/packages/" + package_id(scenario_id, speed) + "/metadata.json"
                facts.append({
                    "schema_version": "phase5-v2-scenario-fact-v1", "fact_id": fact_id(scenario_id, speed, field),
                    "scenario_id": scenario_id, "initial_speed_kph": speed, "field": field, "value": value,
                    "source_artifact": source, "source_locator": field, "derivation_method": "direct_frozen_artifact_read" if value != "UNKNOWN" else "absence_recorded_from_frozen_artifacts",
                    "review_state": "AI_PREPARED", "human_review_required": True,
                })
            for action_id in ACTIONS:
                fields = required_fields(scenario_id, action_id)
                questions.append({
                    "schema_version": "phase5-v2-legal-question-v1", "legal_question_id": question_id(scenario_id, speed, action_id),
                    "scenario_id": scenario_id, "initial_speed_kph": speed, "action_id": action_id,
                    "legal_snapshot_date": LEGAL_SNAPSHOT_DATE,
                    "facts_required": [fact_id(scenario_id, speed, field) for field in fields],
                    "rule_categories": legal_categories(scenario_id, action_id), "question_status": "FROZEN_BEFORE_SOURCE_COLLECTION",
                })
    matrix = []
    for jurisdiction in jurisdictions:
        for question in questions:
            matrix.append({
                "schema_version": "phase5-v2-action-matrix-v1", "record_id": "P5V2D-" + jurisdiction["country_iso3"] + "-" + question["legal_question_id"].removeprefix("P5V2Q-"),
                "country_iso3": jurisdiction["country_iso3"], "country_name": jurisdiction["country"], "subnational_code": None,
                "legal_question_id": question["legal_question_id"], "scenario_id": question["scenario_id"], "initial_speed_kph": question["initial_speed_kph"], "action_id": question["action_id"],
                "legal_snapshot_date": LEGAL_SNAPSHOT_DATE,
                "scenario_fact_ids": question["facts_required"], "applicable_rule_ids": [], "evidence_ids": [],
                "status": "NOT_DETERMINED", "conditions": [], "exceptions": [], "evidence_sufficiency": "NO_EVIDENCE",
                "reason_code": "PRIMARY_SOURCE_SEARCH_PENDING", "human_review_required": True, "review_state": "AI_PREPARED", "final_adjudication": False,
            })
    audits = [{"country_iso3": item["country_iso3"], "country_name": item["country"], "national_or_subnational": "UNRESOLVED_PENDING_OFFICIAL_SOURCE_REVIEW", "required_subnational_code": None, "basis": "Not adjudicated: no official-source granularity review has yet occurred.", "official_source": None, "status": "HUMAN_REVIEW_PENDING"} for item in jurisdictions]
    searches = [{"country_iso3": item["country_iso3"], "search_status": "NOT_STARTED", "queries": [], "official_domains_searched": [], "sources_found": [], "sources_rejected": [], "missing_provisions": [], "review_state": "AI_PREPARED"} for item in jurisdictions]
    if len(facts) == 0 or len(questions) != 36 or len(matrix) != 900:
        raise ValueError("unexpected Phase 5 v2 preparation dimensions")
    write_jsonl(OUTPUT / "scenario_facts_v2.jsonl", facts)
    write_jsonl(OUTPUT / "legal_questions_v2.jsonl", questions)
    write_jsonl(OUTPUT / "action_matrix_v2.jsonl", matrix)
    write_json(OUTPUT / "jurisdiction_granularity_audit_v2.json", {"schema_version": "phase5-v2-granularity-audit-v1", "jurisdictions": audits})
    write_jsonl(OUTPUT / "primary_source_search_log_v2.jsonl", searches)
    write_jsonl(OUTPUT / "deep_law_rules_v2.jsonl", [])
    write_jsonl(OUTPUT / "primary_evidence_v2.jsonl", [])
    write_json(OUTPUT / "phase5_v2_preparation_manifest.json", {
        "schema_version": "phase5-v2-preparation-manifest-v1", "snapshot_id": "phase5-legal-snapshot-v2",
        "status": "PREPARATION_ONLY_NOT_FROZEN", "legal_snapshot_date": LEGAL_SNAPSHOT_DATE,
        "retrieval_date_policy": "Each primary source must record its actual retrieval_date; temporal applicability is separately reviewed.",
        "v1_boundary": "phase5-legal-snapshot-v1 is immutable historical provenance.",
    })
    queue_path = OUTPUT / "review_queue_v2.csv"
    with queue_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["record_id", "country_iso3", "scenario_id", "initial_speed_kph", "action_id", "legal_question_id", "reason_code", "review_state", "human_review_required"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row[field] for field in fields} for row in matrix])
    packet_dir = OUTPUT / "review_packets"
    packet_dir.mkdir(exist_ok=True)
    for jurisdiction in jurisdictions:
        country_rows = [row for row in matrix if row["country_iso3"] == jurisdiction["country_iso3"]]
        lines = [
            f"# Phase 5 v2 review packet — {jurisdiction['country']}", "",
            "Status: `HUMAN_REVIEW_PENDING`. These are not legal conclusions.", "",
            "## Required review", "",
            "Confirm operative jurisdictional granularity from official sources; record every official search, admissible rule, translation method, effective-date state, exception, and unresolved fact.", "",
            "## Prepared action questions", "",
            "| Scenario | Speed (km/h) | Action | Question ID | Current state |", "| --- | ---: | --- | --- | --- |",
        ]
        for row in country_rows:
            lines.append(f"| {row['scenario_id']} | {row['initial_speed_kph']} | {row['action_id']} | {row['legal_question_id']} | {row['reason_code']} |")
        (packet_dir / f"{jurisdiction['country_iso3']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"facts": len(facts), "questions": len(questions), "matrix": len(matrix), "status": "PREPARATION_ONLY_HUMAN_REVIEW_REQUIRED"}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    build()
