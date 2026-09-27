"""Small dependency-free validation contracts for pre-data GeoSAVE artifacts."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from typing import Any, Mapping


LEGAL_STATUSES = {"legal", "illegal", "conditionally_legal", "not_applicable", "unknown"}
RULE_STATUSES = {"verified", "probable", "ambiguous", "unresolved"}
SPLITS = {"development", "validation", "frozen_test"}
ACTIONS = {
    "A0",
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
}


class ContractError(ValueError):
    """Raised when an artifact fails its minimal, safety-relevant contract."""


def _required(record: Mapping[str, Any], *fields: str) -> None:
    missing = [field for field in fields if record.get(field) in (None, "")]
    if missing:
        raise ContractError(f"missing required field(s): {', '.join(missing)}")


def _date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ContractError(f"{field} must be an ISO-8601 date") from error


def _optional_date(value: Any, field: str) -> None:
    if value is not None:
        _date(value, field)


def _choice(value: str, choices: set[str], field: str) -> None:
    if value not in choices:
        raise ContractError(f"{field} must be one of {sorted(choices)}")


def _schema_v1(record: Mapping[str, Any]) -> None:
    if record.get("schema_version") != "v1":
        raise ContractError("schema_version must be v1")


def is_verified_lawful(status: str) -> bool:
    """Only an explicit legal label counts as verified compliance."""
    return status == "legal"


def validate_legal_rule(record: Mapping[str, Any]) -> None:
    _required(
        record,
        "schema_version",
        "rule_id",
        "jurisdiction",
        "retrieved_at",
        "category",
        "rule_status",
        "source",
    )
    if "effective_from" not in record:
        raise ContractError("missing required field(s): effective_from")
    _schema_v1(record)
    if len(record["jurisdiction"]) != 3 or not record["jurisdiction"].isupper():
        raise ContractError("jurisdiction must be an ISO-3 uppercase code")
    if "subnational_code" in record and record["subnational_code"] is not None:
        if not isinstance(record["subnational_code"], str) or not record["subnational_code"]:
            raise ContractError("subnational_code must be a non-empty string or null")
    _optional_date(record["effective_from"], "effective_from")
    _date(record["retrieved_at"], "retrieved_at")
    _choice(record["rule_status"], RULE_STATUSES, "rule_status")
    source = record["source"]
    if not isinstance(source, Mapping):
        raise ContractError("source must be an object")
    _required(source, "title", "url", "source_type")
    if not str(source["url"]).startswith(("https://", "http://")):
        raise ContractError("source.url must be an HTTP(S) URL")


def validate_scenario(record: Mapping[str, Any]) -> None:
    _required(
        record,
        "schema_version",
        "scenario_id",
        "family",
        "version",
        "split",
        "candidate_actions",
        "physical_parameters",
        "legal_dimensions",
        "uncertainty",
        "metrics",
        "action_constraints",
    )
    _schema_v1(record)
    _choice(record["split"], SPLITS, "split")
    actions = record["candidate_actions"]
    if not isinstance(actions, list) or not actions:
        raise ContractError("candidate_actions must be a non-empty list")
    for action in actions:
        _choice(action, ACTIONS, "candidate action")
    for field in ("physical_parameters", "uncertainty", "action_constraints"):
        if not isinstance(record[field], Mapping):
            raise ContractError(f"{field} must be an object")
    for field in ("legal_dimensions", "metrics"):
        if not isinstance(record[field], list) or not record[field]:
            raise ContractError(f"{field} must be a non-empty list")

    constraints = record["action_constraints"]
    for key in ("physically_infeasible_actions", "unstable_actions"):
        values = constraints.get(key, [])
        if not isinstance(values, list):
            raise ContractError(f"action_constraints.{key} must be a list")
        for action in values:
            _choice(action, ACTIONS, f"action_constraints.{key} action")

    forbidden = set(constraints.get("physically_infeasible_actions", [])) | set(constraints.get("unstable_actions", []))
    if not set(actions) - forbidden:
        raise ContractError("action constraints must leave at least one eligible candidate action")


def validate_physical_outcome(record: Mapping[str, Any]) -> None:
    _required(
        record,
        "schema_version",
        "scenario_id",
        "variant_id",
        "action_id",
        "seed",
        "run_status",
    )
    _schema_v1(record)
    _choice(record["action_id"], ACTIONS, "action_id")
    if not isinstance(record["seed"], int):
        raise ContractError("seed must be an integer")
    if record["run_status"] not in {"completed", "failed"}:
        raise ContractError("run_status must be completed or failed")
    if record["run_status"] == "failed":
        _required(record, "failure_reason")
        return
    _required(record, "collision", "minimum_ttc_s", "minimum_distance_m", "stability_failure")


def validate_model_decision(record: Mapping[str, Any]) -> None:
    _required(
        record,
        "schema_version",
        "run_id",
        "scenario_id",
        "country_iso3",
        "law_snapshot",
        "model_id",
        "model_revision",
        "prompt_version",
        "condition",
        "seed",
        "action_order",
        "parse_status",
    )
    _schema_v1(record)
    if record["parse_status"] not in {"valid", "repaired", "failed"}:
        raise ContractError("parse_status must be valid, repaired, or failed")
    if record["parse_status"] == "failed":
        return
    _required(record, "selected_action", "legal_assessment")
    _choice(record["selected_action"], ACTIONS, "selected_action")
    if not isinstance(record["legal_assessment"], Mapping):
        raise ContractError("legal_assessment must be an object")
    for action, status in record["legal_assessment"].items():
        _choice(action, ACTIONS, "legal_assessment action")
        _choice(status, LEGAL_STATUSES, "legal_assessment status")


def validate_experiment_config(record: Mapping[str, Any]) -> None:
    _required(record, "schema_version", "experiment_id", "law_snapshot", "scenarios", "jurisdictions", "models", "conditions", "generation")
    _schema_v1(record)
    if not isinstance(record["models"], list) or not record["models"]:
        raise ContractError("models must be a non-empty list")
    if not isinstance(record["conditions"], list) or not record["conditions"]:
        raise ContractError("conditions must be a non-empty list")
    generation = record["generation"]
    if not isinstance(generation, Mapping):
        raise ContractError("generation must be an object")
    _required(generation, "seed", "repetitions")


def validate_result_manifest(record: Mapping[str, Any]) -> None:
    _required(record, "schema_version", "release", "law_snapshot", "scenario_set", "models", "git_commit", "sha256")
    _schema_v1(record)
    if not isinstance(record["models"], list):
        raise ContractError("models must be a list")
    if not isinstance(record["sha256"], Mapping):
        raise ContractError("sha256 must be an object")


def configuration_fingerprint(record: Mapping[str, Any]) -> str:
    """Return a deterministic identifier for an unchanged validated config."""
    validate_experiment_config(record)
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()
