"""Materialize conservative Phase 5 evidence and decisions from reviewed source metadata.

The frozen scenario overlay deliberately leaves several legal predicates
unspecified. This generator therefore makes the scientifically valid decision
`NOT_DETERMINED` instead of inventing a road marking, crossing designation,
traffic control, local jurisdiction, or legal exception.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE5 = ROOT / "data" / "legal" / "phase5"
CONFIG = ROOT / "configs" / "legal" / "phase5_two_level_v1.json"
SOURCES = PHASE5 / "source_metadata.json"
QUERIES = PHASE5 / "legal_queries.jsonl"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_bytes("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows).encode("utf-8"))


def evidence_from_source(source: dict) -> dict:
    retrievable = source["second_pass_access"] == "retrieved" and bool(source.get("source_hash"))
    return {
        "schema_version": "phase5-legal-evidence-v1",
        "evidence_id": source["source_record_id"].replace("P5S-", "P5E-"),
        "country_iso3": source["country_iso3"],
        "country_name": source["country_name"],
        "subnational_code": source["subnational_code"],
        "authority_level": source["authority_level"],
        "source_type": source["source_type"],
        "source_title": source["source_title"],
        "issuing_authority": source["issuing_authority"],
        "official_source_url": source["official_source_url"],
        "provision_identifier": "; ".join(source["provision_identifiers"]),
        "source_language": source["source_language"],
        "short_original_excerpt": None,
        "excerpt_status": "not_retained_to_avoid_unnecessary_copyrighted_text_copying",
        "translation": None,
        "translation_method": "not_applicable_no_action_level_translation_or_inference",
        "translation_uncertainty": "not_assessed_because_no_action-level translated claim is emitted",
        "publication_date": None,
        "effective_from": None,
        "effective_to": None,
        "effective_date_status": "not_established",
        "retrieved_at": source["retrieved_at"],
        "source_hash": source.get("source_hash"),
        "source_hash_status": "retrieved_and_hashed" if retrievable else "not_preserved_due_access_limitation",
        "rule_category": "scenario_relevant_traffic_rule_index",
        "normalized_rule": "Official provision indexed for scenario-relevant review; no action-level conclusion is emitted while material overlay predicates remain unspecified.",
        "scenario_conditions": {},
        "action_conditions": {},
        "exceptions": [],
        "applies_to": "human_driver",
        "supported_legal_status": "NOT_DETERMINED",
        "evidence_sufficiency": "INSUFFICIENT",
        "review_status": "two_pass_primary_source_verified" if retrievable else "two_pass_primary_source_access_limited",
        "review_notes": source["notes"],
        "human_review_required": True,
        "verification_passes": source["verification_passes"],
        "admission_status": source["admission_status"],
        "scope_status": source["scope_status"],
    }


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    source_metadata = json.loads(SOURCES.read_text(encoding="utf-8"))["jurisdictions"]
    sources = {source["country_iso3"]: source for source in source_metadata}
    expected = {entry["country_iso3"] for entry in config["deep_law_layer"]["selection_frame"]}
    if set(sources) != expected:
        raise ValueError("source metadata does not cover the frozen selection")
    evidence = [evidence_from_source(source) for source in sorted(source_metadata, key=lambda item: item["country_iso3"])]
    evidence_by_country = {row["country_iso3"]: row["evidence_id"] for row in evidence}
    queries = jsonl(QUERIES)
    decisions: list[dict] = []
    for query in queries:
        evidence_id = evidence_by_country[query["country_iso3"]]
        source = sources[query["country_iso3"]]
        decisions.append({
            "schema_version": "phase5-legal-decision-v1",
            "decision_id": query["query_id"].replace("P5Q-", "P5D-"),
            "query_id": query["query_id"],
            "country_iso3": query["country_iso3"],
            "scenario_id": query["scenario_id"],
            "initial_speed_kph": query["initial_speed_kph"],
            "action_id": query["action_id"],
            "status": "NOT_DETERMINED",
            "considered_evidence_ids": [evidence_id],
            "supporting_evidence_ids": [],
            "contradicting_evidence_ids": [],
            "evidence_sufficiency": "INSUFFICIENT",
            "reason_code": "material_legal_predicates_not_specified_in_frozen_overlay",
            "reason_detail": "No marked-crossing type, traffic control, posted speed limit, lane-marking type, traffic side, local scope, or statutory exception may be inferred from Phase 4 physics.",
            "review_status": "two_pass_primary_source_verification_complete",
            "human_review_required": True,
            "legal_snapshot_candidate": "phase5-legal-snapshot-v1",
            "source_access_state": source["second_pass_access"],
        })
    jurisdiction_metadata = {
        "schema_version": "phase5-jurisdiction-metadata-v1",
        "jurisdictions": [
            {
                "country_iso3": entry["country_iso3"],
                "country_name": entry["country"],
                "review_status": "two_pass_primary_source_verification_complete",
                "verification_passes": ["discovery_extraction", "independent_source_reverification"],
                "source_record_ids": [sources[entry["country_iso3"]]["source_record_id"]],
                "admitted_action_level_evidence_count": 0,
                "query_count": 36,
                "not_determined_query_count": 36,
            }
            for entry in config["deep_law_layer"]["selection_frame"]
        ],
    }
    write_jsonl(PHASE5 / "primary_evidence.jsonl", evidence)
    write_jsonl(PHASE5 / "legal_decisions.jsonl", decisions)
    (PHASE5 / "jurisdiction_metadata.json").write_bytes((json.dumps(jurisdiction_metadata, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(f"Materialized {len(evidence)} evidence records and {len(decisions)} NOT_DETERMINED decisions")


if __name__ == "__main__":
    main()
