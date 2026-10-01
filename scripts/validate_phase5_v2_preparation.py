"""Fail-closed validator for the non-final Phase 5 v2 preparation dataset."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/legal/phase5_v2"


def jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    facts, questions, matrix = jsonl("scenario_facts_v2.jsonl"), jsonl("legal_questions_v2.jsonl"), jsonl("action_matrix_v2.jsonl")
    errors = []
    if len(questions) != 36 or len(matrix) != 900:
        errors.append("v2 requires 36 questions and 900 planned records")
    fact_ids, question_ids = {row["fact_id"] for row in facts}, {row["legal_question_id"] for row in questions}
    if any(not set(row["facts_required"]) <= fact_ids for row in questions): errors.append("question references unknown fact")
    if any(row["legal_question_id"] not in question_ids for row in matrix): errors.append("matrix references unknown question")
    if {row.get("legal_snapshot_date") for row in matrix} != {"2026-10-01"}: errors.append("matrix lacks a single frozen evaluation date")
    for row in matrix:
        if row["final_adjudication"] or row["review_state"] != "AI_PREPARED": errors.append("preparation data must not claim final human review")
        if row["status"] != "NOT_DETERMINED" or row["reason_code"] != "PRIMARY_SOURCE_SEARCH_PENDING": errors.append("unreviewed record must fail closed")
        if row["evidence_ids"] or row["applicable_rule_ids"]: errors.append("unreviewed record cannot claim law evidence")
        if row.get("final_legal_status") is not None or row.get("reviewer_status") != "NOT_REVIEWED": errors.append("unreviewed record has a final legal conclusion")
        if any(row.get(field) for field in ("source_search_completed", "primary_authority_cited", "explicit_no_authority_found_recorded", "applicability_assessed", "formalisation_traceable_to_evidence")):
            errors.append("unreviewed record claims an unperformed completion-gate step")
    if not any(row["value"] == "UNKNOWN" for row in facts): errors.append("scenario-fact unknowns must remain explicit")
    queue = DATA / "review_queue_v2.csv"
    packets = list((DATA / "review_packets").glob("*.md"))
    if not queue.is_file() or len(packets) != 25: errors.append("review queue or jurisdiction packets missing")
    if errors: raise SystemExit("; ".join(sorted(set(errors))))
    print("Phase 5 v2 preparation: valid and non-final")


if __name__ == "__main__":
    main()
