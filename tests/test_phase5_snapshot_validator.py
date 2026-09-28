from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_phase5_legal_snapshot import SnapshotValidationError, validate_decisions


def query() -> dict:
    return {"P5Q-TST-PED-CROSS-001-V030-A2": {"country_iso3": "TST", "scenario_id": "PED-CROSS-001", "initial_speed_kph": 30, "action_id": "A2"}}


def evidence() -> dict:
    return {
        "P5E-TST-001": {
            "country_iso3": "TST",
            "authority_level": "national",
            "source_type": "statute",
            "evidence_sufficiency": "SUFFICIENT_PRIMARY",
        }
    }


def decision(**overrides: object) -> dict:
    record = {
        "decision_id": "P5D-TST-001",
        "query_id": "P5Q-TST-PED-CROSS-001-V030-A2",
        "country_iso3": "TST",
        "scenario_id": "PED-CROSS-001",
        "initial_speed_kph": 30,
        "action_id": "A2",
        "status": "NOT_DETERMINED",
        "evidence_sufficiency": "NO_EVIDENCE",
        "reason_code": "no_applicable_evidence",
        "review_status": "two_pass_primary_source_verification_complete",
        "supporting_evidence_ids": [],
        "contradicting_evidence_ids": [],
    }
    record.update(overrides)
    return record


def test_unknown_law_stays_explicit() -> None:
    validate_decisions([decision()], query(), evidence())
    with pytest.raises(SnapshotValidationError, match="NOT_DETERMINED"):
        validate_decisions([decision(evidence_sufficiency="SUFFICIENT_PRIMARY")], query(), evidence())


def test_action_conclusion_requires_domestic_primary_evidence() -> None:
    resolved = decision(
        status="REQUIRED",
        evidence_sufficiency="SUFFICIENT_PRIMARY",
        supporting_evidence_ids=["P5E-TST-001"],
    )
    validate_decisions([resolved], query(), evidence())
    nonprimary = evidence()
    nonprimary["P5E-TST-001"]["source_type"] = "secondary_official_dataset"
    with pytest.raises(SnapshotValidationError, match="domestic primary"):
        validate_decisions([resolved], query(), nonprimary)


def test_cross_jurisdiction_evidence_is_rejected() -> None:
    resolved = decision(
        status="REQUIRED",
        evidence_sufficiency="SUFFICIENT_PRIMARY",
        supporting_evidence_ids=["P5E-TST-001"],
    )
    other = evidence()
    other["P5E-TST-001"]["country_iso3"] = "OTH"
    with pytest.raises(SnapshotValidationError, match="another jurisdiction"):
        validate_decisions([resolved], query(), other)
