"""Strict, provider-independent Phase 6 decision-output contract.

This module deliberately contains no provider client and performs no network
I/O.  It validates only model-returned JSON and preserves the raw response
before attaching repository-controlled provenance fields to a normalized row.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Any, Literal, Mapping


PHASE6_SCHEMA_VERSION = "phase6-model-decision-v1"
ALLOWED_ACTIONS = ("A0", "A1", "A2", "A3", "A4", "A6")
DECISION_STATUSES = ("CHOOSE", "ABSTAIN", "INSUFFICIENT_INFORMATION", "INVALID")
PARSE_STATUSES = ("valid", "repaired", "failed")
STATED_FACTORS = (
    "braking_distance",
    "collision_avoidance",
    "ego_speed",
    "geosave_constraint",
    "insufficient_legal_evidence",
    "legal_uncertainty",
    "lane_boundary",
    "lane_marking",
    "motorcycle_conflict",
    "obstacle_clearance",
    "operational_uncertainty",
    "pedestrian_conflict",
    "road_boundary",
    "supplied_legal_rule",
    "vehicle_stability",
)
LEGAL_CLAIM_TYPES = ("duty", "exception", "lawfulness", "uncertainty")

ParseStatus = Literal["valid", "repaired", "failed"]


class Phase6ContractError(ValueError):
    """Raised when a provider response does not meet the frozen contract."""


@dataclass(frozen=True)
class ParsedPhase6Decision:
    decision_status: str
    selected_action_id: str | None
    stated_factors: tuple[str, ...]
    legal_claims: tuple[dict[str, Any], ...]
    evidence_ids_cited: tuple[str, ...]
    uncertainty_statement: str
    short_rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_status": self.decision_status,
            "selected_action_id": self.selected_action_id,
            "stated_factors": list(self.stated_factors),
            "legal_claims": list(self.legal_claims),
            "evidence_ids_cited": list(self.evidence_ids_cited),
            "uncertainty_statement": self.uncertainty_statement,
            "short_rationale": self.short_rationale,
        }


@dataclass(frozen=True)
class Phase6ParseResult:
    status: ParseStatus
    decision: ParsedPhase6Decision | None
    error: str | None
    repair_attempted: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


MODEL_RESPONSE_FIELDS = {
    "decision_status",
    "selected_action_id",
    "stated_factors",
    "legal_claims",
    "evidence_ids_cited",
    "uncertainty_statement",
    "short_rationale",
}


def canonical_json_bytes(value: Any) -> bytes:
    """Encode a repository artifact in a platform-independent form."""
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def _nonempty_string(value: Any, field: str, *, maximum: int = 1_000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Phase6ContractError(f"{field} must be a non-empty string")
    if len(value) > maximum:
        raise Phase6ContractError(f"{field} exceeds {maximum} characters")
    return value


def _string_list(value: Any, field: str, *, allowed: tuple[str, ...] | None = None) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise Phase6ContractError(f"{field} must be a list of strings")
    if len(value) != len(set(value)):
        raise Phase6ContractError(f"{field} must not contain duplicates")
    if allowed is not None and any(item not in allowed for item in value):
        raise Phase6ContractError(f"{field} contains an unsupported value")
    return tuple(value)


def _validate_legal_claims(value: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        raise Phase6ContractError("legal_claims must be a list")
    normalized: list[dict[str, Any]] = []
    for index, claim in enumerate(value):
        if not isinstance(claim, Mapping):
            raise Phase6ContractError(f"legal_claims[{index}] must be an object")
        expected = {"claim_type", "action_id", "statement", "evidence_ids"}
        if set(claim) != expected:
            raise Phase6ContractError(f"legal_claims[{index}] must contain exactly {sorted(expected)}")
        claim_type = claim["claim_type"]
        if claim_type not in LEGAL_CLAIM_TYPES:
            raise Phase6ContractError(f"legal_claims[{index}].claim_type is unsupported")
        action_id = claim["action_id"]
        if action_id is not None and action_id not in ALLOWED_ACTIONS:
            raise Phase6ContractError(f"legal_claims[{index}].action_id is invalid")
        statement = _nonempty_string(claim["statement"], f"legal_claims[{index}].statement")
        evidence_ids = _string_list(claim["evidence_ids"], f"legal_claims[{index}].evidence_ids")
        normalized.append(
            {
                "claim_type": claim_type,
                "action_id": action_id,
                "statement": statement,
                "evidence_ids": list(evidence_ids),
            }
        )
    return tuple(normalized)


def decode_phase6_response(raw: str) -> ParsedPhase6Decision:
    """Decode a model response without guessing a missing decision."""
    if not isinstance(raw, str):
        raise Phase6ContractError("raw response must be text")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise Phase6ContractError(f"invalid JSON: {error.msg}") from error
    if not isinstance(value, Mapping):
        raise Phase6ContractError("response must be a JSON object")
    if set(value) != MODEL_RESPONSE_FIELDS:
        raise Phase6ContractError(f"response must contain exactly {sorted(MODEL_RESPONSE_FIELDS)}")

    decision_status = value["decision_status"]
    if decision_status not in DECISION_STATUSES:
        raise Phase6ContractError("decision_status is unsupported")
    selected_action_id = value["selected_action_id"]
    if decision_status == "CHOOSE":
        if selected_action_id not in ALLOWED_ACTIONS:
            raise Phase6ContractError("CHOOSE requires an allowed selected_action_id")
    elif selected_action_id is not None:
        raise Phase6ContractError("non-CHOOSE responses must set selected_action_id to null")
    if decision_status == "INVALID":
        raise Phase6ContractError("a provider may not self-classify a response as INVALID")

    return ParsedPhase6Decision(
        decision_status=decision_status,
        selected_action_id=selected_action_id,
        stated_factors=_string_list(value["stated_factors"], "stated_factors", allowed=STATED_FACTORS),
        legal_claims=_validate_legal_claims(value["legal_claims"]),
        evidence_ids_cited=_string_list(value["evidence_ids_cited"], "evidence_ids_cited"),
        uncertainty_statement=_nonempty_string(value["uncertainty_statement"], "uncertainty_statement"),
        short_rationale=_nonempty_string(value["short_rationale"], "short_rationale"),
    )


def _fence_only_repair(raw: str) -> str | None:
    """Return content from one complete Markdown fence, otherwise None."""
    stripped = raw.strip()
    if not (stripped.startswith("```") and stripped.endswith("```")):
        return None
    lines = stripped.splitlines()
    if len(lines) < 3 or not lines[0].startswith("```") or lines[-1] != "```":
        return None
    return "\n".join(lines[1:-1]).strip()


def parse_phase6_response(raw: str) -> Phase6ParseResult:
    """Parse once, then make one deterministic fence-only repair attempt."""
    try:
        return Phase6ParseResult("valid", decode_phase6_response(raw), None, False)
    except Phase6ContractError as first_error:
        repaired = _fence_only_repair(raw)
        if repaired is None:
            return Phase6ParseResult("failed", None, str(first_error), False)
        try:
            return Phase6ParseResult("repaired", decode_phase6_response(repaired), None, True)
        except Phase6ContractError as second_error:
            return Phase6ParseResult("failed", None, str(second_error), True)


def normalized_record(
    *,
    run_id: str,
    model_id: str,
    model_revision: str,
    prompt_version: str,
    condition: str,
    input_package_id: str,
    country_iso3: str | None,
    law_snapshot: str,
    action_order: tuple[str, ...],
    raw_response_reference: str,
    result: Phase6ParseResult,
) -> dict[str, Any]:
    """Attach repository provenance after, never before, raw preservation."""
    if not raw_response_reference:
        raise Phase6ContractError("raw_response_reference is required")
    if tuple(sorted(action_order)) != tuple(sorted(ALLOWED_ACTIONS)):
        raise Phase6ContractError("action_order must be a permutation of the candidate actions")
    record: dict[str, Any] = {
        "schema_version": PHASE6_SCHEMA_VERSION,
        "run_id": run_id,
        "model_id": model_id,
        "model_revision": model_revision,
        "prompt_version": prompt_version,
        "condition": condition,
        "input_package_id": input_package_id,
        "country_iso3": country_iso3,
        "law_snapshot": law_snapshot,
        "action_order": list(action_order),
        "raw_response_reference": raw_response_reference,
        "parse_status": result.status,
        "repair_attempted": result.repair_attempted,
    }
    if result.decision is None:
        record.update(
            {
                "decision_status": "INVALID",
                "selected_action_id": None,
                "stated_factors": [],
                "legal_claims": [],
                "evidence_ids_cited": [],
                "uncertainty_statement": "Parser rejected the provider response; no decision is inferred.",
                "short_rationale": "",
                "parse_error": result.error,
            }
        )
    else:
        record.update(result.decision.to_dict())
        record["parse_error"] = None
    return record


NORMALIZED_RECORD_FIELDS = {
    "schema_version",
    "run_id",
    "model_id",
    "model_revision",
    "prompt_version",
    "condition",
    "input_package_id",
    "country_iso3",
    "law_snapshot",
    "action_order",
    "raw_response_reference",
    "parse_status",
    "repair_attempted",
    "decision_status",
    "selected_action_id",
    "stated_factors",
    "legal_claims",
    "evidence_ids_cited",
    "uncertainty_statement",
    "short_rationale",
    "parse_error",
}


def validate_normalized_record(record: Mapping[str, Any]) -> None:
    """Validate the repository-owned normalized form before persistence."""
    if set(record) != NORMALIZED_RECORD_FIELDS:
        raise Phase6ContractError("normalized record has missing or unexpected fields")
    if record["schema_version"] != PHASE6_SCHEMA_VERSION:
        raise Phase6ContractError("normalized record schema_version is invalid")
    for field in ("run_id", "model_id", "model_revision", "prompt_version", "input_package_id", "law_snapshot", "raw_response_reference"):
        _nonempty_string(record[field], field)
    if record["condition"] not in {"C0", "C1", "C2", "C3", "C4"}:
        raise Phase6ContractError("normalized record condition is invalid")
    country_iso3 = record["country_iso3"]
    if country_iso3 is not None and (not isinstance(country_iso3, str) or len(country_iso3) != 3 or not country_iso3.isupper()):
        raise Phase6ContractError("normalized record country_iso3 is invalid")
    if tuple(sorted(record["action_order"])) != tuple(sorted(ALLOWED_ACTIONS)):
        raise Phase6ContractError("normalized record action_order is invalid")
    if record["parse_status"] not in PARSE_STATUSES or not isinstance(record["repair_attempted"], bool):
        raise Phase6ContractError("normalized record parse metadata is invalid")
    if record["parse_status"] == "failed":
        if record["decision_status"] != "INVALID" or record["selected_action_id"] is not None:
            raise Phase6ContractError("failed parse must normalize to INVALID without a selected action")
        if not isinstance(record["parse_error"], str) or not record["parse_error"]:
            raise Phase6ContractError("failed parse must retain parse_error")
        return
    if record["parse_error"] is not None:
        raise Phase6ContractError("successful parse may not retain parse_error")
    model_fields = {field: record[field] for field in MODEL_RESPONSE_FIELDS}
    decode_phase6_response(json.dumps(model_fields, ensure_ascii=True))


def persist_raw_response(path: Path, raw: str) -> str:
    """Persist raw provider text exactly once and return its SHA-256 hash."""
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = raw.encode("utf-8")
    path.write_bytes(payload)
    return sha256(payload).hexdigest()


def persist_normalized_record(path: Path, record: Mapping[str, Any]) -> str:
    """Persist a normalized record append-only in canonical JSON bytes."""
    if path.exists():
        raise FileExistsError(path)
    validate_normalized_record(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_bytes(dict(record))
    path.write_bytes(payload)
    return sha256(payload).hexdigest()


def deterministic_action_order(run_id: str) -> tuple[str, ...]:
    """Randomize action display order reproducibly without a global RNG."""
    if not run_id:
        raise Phase6ContractError("run_id is required for action ordering")
    actions = list(ALLOWED_ACTIONS)
    seed = int.from_bytes(sha256(run_id.encode("utf-8")).digest()[:16], "big")
    random.Random(seed).shuffle(actions)
    return tuple(actions)
