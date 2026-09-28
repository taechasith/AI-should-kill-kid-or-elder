"""Validate a frozen Phase 5 legal snapshot without inferring missing law.

This validator intentionally rejects a snapshot that merely has complete rows.
Every non-unknown decision must trace to reviewed domestic primary evidence;
every unknown decision must remain explicit rather than becoming permission.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PHASE5 = ROOT / "data" / "legal" / "phase5"
CONFIG = ROOT / "configs" / "legal" / "phase5_two_level_v1.json"
QUERY_PATH = PHASE5 / "legal_queries.jsonl"
EVIDENCE_PATH = PHASE5 / "primary_evidence.jsonl"
DECISION_PATH = PHASE5 / "legal_decisions.jsonl"
JURISDICTION_PATH = PHASE5 / "jurisdiction_metadata.json"
SOURCE_PATH = PHASE5 / "source_metadata.json"

STATUSES = {
    "PERMITTED", "PROHIBITED", "REQUIRED", "CONDITIONALLY_PERMITTED",
    "NOT_DETERMINED", "CONFLICTING_AUTHORITIES",
}
SUFFICIENCY = {
    "SUFFICIENT_PRIMARY", "SUFFICIENT_OFFICIAL_SECONDARY", "PARTIAL",
    "CONFLICTING", "INSUFFICIENT", "NO_EVIDENCE",
}
PRIMARY_DOMESTIC_TYPES = {"statute", "regulation", "official_code", "court_decision"}
DOMESTIC_LEVELS = {"national", "state/province", "local"}
TWO_PASS = {"discovery_extraction", "independent_source_reverification"}


class SnapshotValidationError(ValueError):
    """Raised when a legal snapshot violates a research-integrity invariant."""


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def require(record: dict, *fields: str) -> None:
    missing = [field for field in fields if field not in record or record[field] in ("", None)]
    if missing:
        raise SnapshotValidationError(f"missing required fields {missing}")


def validate_date(value: object, field: str, *, allow_null: bool = False) -> None:
    if value is None and allow_null:
        return
    if not isinstance(value, str):
        raise SnapshotValidationError(f"{field} must be an ISO date")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise SnapshotValidationError(f"{field} must be an ISO date") from error


def expected_jurisdictions(config: dict) -> set[str]:
    return {item["country_iso3"] for item in config["deep_law_layer"]["selection_frame"]}


def validate_queries(rows: Iterable[dict], jurisdictions: set[str]) -> dict[str, dict]:
    rows = list(rows)
    if len(rows) != 900:
        raise SnapshotValidationError(f"expected 900 legal queries, found {len(rows)}")
    indexed: dict[str, dict] = {}
    for row in rows:
        require(row, "query_id", "country_iso3", "scenario_id", "initial_speed_kph", "action_id", "evaluation_date", "overlay_id")
        if row["query_id"] in indexed:
            raise SnapshotValidationError(f"duplicate query_id {row['query_id']}")
        if row["country_iso3"] not in jurisdictions:
            raise SnapshotValidationError(f"unauthorized query jurisdiction {row['country_iso3']}")
        if row["initial_speed_kph"] not in {30, 50}:
            raise SnapshotValidationError("legal query uses an unfrozen initial speed")
        validate_date(row["evaluation_date"], "evaluation_date")
        indexed[row["query_id"]] = row
    if {row["country_iso3"] for row in rows} != jurisdictions:
        raise SnapshotValidationError("query jurisdiction coverage differs from frozen selection")
    return indexed


def validate_jurisdiction_metadata(metadata: object, jurisdictions: set[str]) -> None:
    if not isinstance(metadata, dict) or not isinstance(metadata.get("jurisdictions"), list):
        raise SnapshotValidationError("jurisdiction metadata must contain a jurisdictions list")
    records = metadata["jurisdictions"]
    observed = {record.get("country_iso3") for record in records}
    if observed != jurisdictions or len(records) != len(jurisdictions):
        raise SnapshotValidationError("jurisdiction metadata does not match frozen selection")
    for record in records:
        require(record, "country_iso3", "country_name", "review_status", "verification_passes")
        if set(record["verification_passes"]) != TWO_PASS:
            raise SnapshotValidationError(f"{record['country_iso3']} lacks two-pass source verification")
        if record["review_status"] != "two_pass_primary_source_verification_complete":
            raise SnapshotValidationError(f"{record['country_iso3']} has an incomplete review status")


def validate_source_metadata(records: object, jurisdictions: set[str]) -> None:
    if isinstance(records, dict):
        records = records.get("jurisdictions")
    if not isinstance(records, list):
        raise SnapshotValidationError("source metadata must be a list")
    seen: set[str] = set()
    covered: set[str] = set()
    for record in records:
        require(record, "source_record_id", "country_iso3", "source_title", "official_source_url", "retrieved_at", "verification_passes")
        if record["source_record_id"] in seen:
            raise SnapshotValidationError(f"duplicate source record {record['source_record_id']}")
        seen.add(record["source_record_id"])
        if record["country_iso3"] not in jurisdictions:
            raise SnapshotValidationError("source metadata has an unauthorized jurisdiction")
        if not record["official_source_url"].startswith(("https://", "http://")):
            raise SnapshotValidationError("source metadata needs an HTTP(S) official URL")
        validate_date(record["retrieved_at"], "source_metadata.retrieved_at")
        if set(record["verification_passes"]) != TWO_PASS:
            raise SnapshotValidationError("source metadata lacks two-pass verification")
        covered.add(record["country_iso3"])
    if covered != jurisdictions:
        raise SnapshotValidationError("at least one official-source search record is required per jurisdiction")


def validate_evidence(rows: Iterable[dict], jurisdictions: set[str]) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for row in rows:
        require(
            row, "evidence_id", "country_iso3", "authority_level", "source_type",
            "source_title", "issuing_authority", "official_source_url", "provision_identifier",
            "source_language", "retrieved_at", "rule_category", "normalized_rule",
            "supported_legal_status", "evidence_sufficiency", "review_status", "verification_passes",
        )
        evidence_id = row["evidence_id"]
        if evidence_id in indexed:
            raise SnapshotValidationError(f"duplicate evidence_id {evidence_id}")
        if row["country_iso3"] not in jurisdictions:
            raise SnapshotValidationError(f"unauthorized evidence jurisdiction {row['country_iso3']}")
        if row["supported_legal_status"] not in STATUSES:
            raise SnapshotValidationError("evidence has an invalid legal status")
        if row["evidence_sufficiency"] not in SUFFICIENCY:
            raise SnapshotValidationError("evidence has invalid sufficiency")
        if not row["official_source_url"].startswith(("https://", "http://")):
            raise SnapshotValidationError("evidence needs an HTTP(S) official source URL")
        validate_date(row["retrieved_at"], "evidence.retrieved_at")
        validate_date(row.get("effective_from"), "evidence.effective_from", allow_null=True)
        validate_date(row.get("effective_to"), "evidence.effective_to", allow_null=True)
        if row.get("effective_date_status") not in {"known", "unknown", "historical_view", "not_established"}:
            raise SnapshotValidationError("evidence needs an explicit effective-date status")
        if row.get("effective_date_status") == "known" and row.get("effective_from") is None:
            raise SnapshotValidationError("known effective date requires effective_from")
        if set(row["verification_passes"]) != TWO_PASS:
            raise SnapshotValidationError("evidence lacks two-pass verification")
        if row["review_status"] not in {
            "two_pass_primary_source_verified",
            "two_pass_primary_source_access_limited",
        }:
            raise SnapshotValidationError("evidence is not marked as two-pass verified")
        if row["review_status"] == "two_pass_primary_source_access_limited":
            if row["supported_legal_status"] != "NOT_DETERMINED" or row["evidence_sufficiency"] != "INSUFFICIENT":
                raise SnapshotValidationError("access-limited evidence cannot support an action-level conclusion")
        if row.get("translation_method") in {None, ""}:
            raise SnapshotValidationError("evidence needs an explicit translation_method")
        title_and_authority = f"{row['source_title']} {row['issuing_authority']}".lower()
        if "world health organization" in title_and_authority or row["source_type"] == "secondary_official_dataset":
            if row["supported_legal_status"] != "NOT_DETERMINED":
                raise SnapshotValidationError("WHO or other context data cannot support action-level legality")
        if row["authority_level"] == "international" and row["supported_legal_status"] != "NOT_DETERMINED":
            if row.get("instrument_applicability") not in {"documented_domestic_incorporation", "documented_direct_applicability"}:
                raise SnapshotValidationError("international instrument lacks documented domestic applicability")
        indexed[evidence_id] = row
    return indexed


def is_domestic_primary(evidence: dict) -> bool:
    return (
        evidence["authority_level"] in DOMESTIC_LEVELS
        and evidence["source_type"] in PRIMARY_DOMESTIC_TYPES
        and evidence["evidence_sufficiency"] == "SUFFICIENT_PRIMARY"
    )


def validate_decisions(rows: Iterable[dict], queries: dict[str, dict], evidence: dict[str, dict]) -> None:
    rows = list(rows)
    if len(rows) != len(queries):
        raise SnapshotValidationError("decision count does not equal legal query count")
    indexed: set[str] = set()
    for row in rows:
        require(row, "decision_id", "query_id", "country_iso3", "scenario_id", "initial_speed_kph", "action_id", "status", "evidence_sufficiency", "reason_code", "review_status")
        query_id = row["query_id"]
        if query_id not in queries or query_id in indexed:
            raise SnapshotValidationError(f"invalid or duplicate decision query link {query_id}")
        indexed.add(query_id)
        query = queries[query_id]
        for field in ("country_iso3", "scenario_id", "initial_speed_kph", "action_id"):
            if row[field] != query[field]:
                raise SnapshotValidationError(f"decision/query mismatch for {query_id}: {field}")
        if row["status"] not in STATUSES or row["evidence_sufficiency"] not in SUFFICIENCY:
            raise SnapshotValidationError("decision has invalid status or sufficiency")
        considered = tuple(row.get("considered_evidence_ids", []))
        supporting = tuple(row.get("supporting_evidence_ids", []))
        contradicting = tuple(row.get("contradicting_evidence_ids", []))
        for evidence_id in considered + supporting + contradicting:
            if evidence_id not in evidence:
                raise SnapshotValidationError(f"decision cites unknown evidence {evidence_id}")
            if evidence[evidence_id]["country_iso3"] != row["country_iso3"]:
                raise SnapshotValidationError("decision cites another jurisdiction's evidence")
        if row["status"] == "NOT_DETERMINED":
            if row["evidence_sufficiency"] not in {"NO_EVIDENCE", "INSUFFICIENT", "PARTIAL"}:
                raise SnapshotValidationError("NOT_DETERMINED must preserve inadequate evidence")
            if supporting:
                raise SnapshotValidationError("NOT_DETERMINED may not silently use supporting law")
        else:
            if not supporting:
                raise SnapshotValidationError("non-unknown decision lacks supporting evidence")
            if not all(is_domestic_primary(evidence[evidence_id]) for evidence_id in supporting):
                raise SnapshotValidationError("action-level conclusion lacks sufficient domestic primary law")
            if row["status"] == "CONFLICTING_AUTHORITIES" and not contradicting:
                raise SnapshotValidationError("conflicting decision lacks contradicting evidence")
        if row["review_status"] != "two_pass_primary_source_verification_complete":
            raise SnapshotValidationError("decision lacks completed two-pass review")
    if indexed != set(queries):
        raise SnapshotValidationError("one or more legal queries have no decision")


def validate_snapshot(root: Path = ROOT) -> None:
    phase5 = root / "data" / "legal" / "phase5"
    config = load_json(root / "configs" / "legal" / "phase5_two_level_v1.json")
    jurisdictions = expected_jurisdictions(config)
    queries = validate_queries(load_jsonl(phase5 / "legal_queries.jsonl"), jurisdictions)
    validate_jurisdiction_metadata(load_json(phase5 / "jurisdiction_metadata.json"), jurisdictions)
    validate_source_metadata(load_json(phase5 / "source_metadata.json"), jurisdictions)
    evidence = validate_evidence(load_jsonl(phase5 / "primary_evidence.jsonl"), jurisdictions)
    validate_decisions(load_jsonl(phase5 / "legal_decisions.jsonl"), queries, evidence)


def main() -> None:
    validate_snapshot()
    print("Phase 5 legal snapshot: valid")


if __name__ == "__main__":
    main()
