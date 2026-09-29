import json
from pathlib import Path

import pytest

from geosave.phase6_free_executor import AccountAttestation, Phase6PilotError, execute_pilot_row, load_attestation


VALID_DECISION = json.dumps({
    "decision_status": "CHOOSE", "selected_action_id": "A2", "stated_factors": ["collision_avoidance"],
    "legal_claims": [], "evidence_ids_cited": [], "uncertainty_statement": "Limited to supplied facts.", "short_rationale": "Brake."
})
VALID_RAW = json.dumps({"candidates": [{"content": {"parts": [{"text": VALID_DECISION}]}}]})
POLICY = {"budget_mode": "FREE_ONLY", "max_authorized_usd": 0, "max_authorized_thb": 0, "allow_paid_fallback": False, "allow_provider_upgrade": False, "allow_credit_purchase": False, "allow_automatic_billing": False}
ROW = {"run_id": "P6F-M1-PED-CROSS-001__V030-ARG-C2-R01", "model_id": "gemini-3.6-flash", "model_revision": "gemini-3.6-flash", "condition": "C2", "input_package_id": "PED-CROSS-001__V030", "country_iso3": "ARG", "action_order": ["A0", "A1", "A2", "A3", "A4", "A6"]}


def attestation():
    return AccountAttestation.from_mapping({"schema_version": "phase6-free-account-attestation-v1", "verification_timestamp_utc": "2026-09-29T00:00:00Z", "source": "account owner", "providers": [
        {"provider": "gemini", "access_tier": "free_tier", "billing_enabled": False, "quota_available": True, "verified_model_ids": ["gemini-3.6-flash", "gemini-2.5-flash-lite"]},
        {"provider": "groq", "access_tier": "free_plan", "billing_enabled": False, "quota_available": True, "verified_model_ids": ["qwen/qwen3.8-27b"]},
    ]})


def execute(tmp_path, send):
    return execute_pilot_row(row=ROW, provider="gemini", policy=POLICY, registry_status="FREE_ONLY_PILOT_AUTHORIZED", credential_present=True, attestation=attestation(), attestation_sha256="a" * 64, source_commit="b" * 40, raw_root=tmp_path / "raw", normalized_root=tmp_path / "normalized", attempt_root=tmp_path, send=send)


def test_success_preserves_raw_before_parse_and_is_append_only(tmp_path):
    result = execute(tmp_path, lambda: (200, VALID_RAW, {"x-ratelimit-remaining-requests": "99", "authorization": "secret"}))
    assert result["status"] == "completed"
    assert Path(result["raw_response_reference"]).read_text() == VALID_RAW
    assert json.loads(Path(result["normalized_response_reference"]).read_text())["selected_action_id"] == "A2"
    assert result["response_rate_limit_headers"] == {"x-ratelimit-remaining-requests": "99"}
    with pytest.raises(Phase6PilotError):
        execute(tmp_path, lambda: (200, VALID_RAW, {}))


def test_provider_failure_never_creates_fake_raw_or_normalized_response(tmp_path):
    result = execute(tmp_path, lambda: (429, "not-to-be-saved", {"retry-after": "60"}))
    assert result["status"] == "failed"
    assert result["failure_reason"] == "FREE_QUOTA_EXHAUSTED"
    assert result["raw_response_reference"] is None
    assert not (tmp_path / "raw").exists()


def test_invalid_attestation_or_guard_blocks_before_sender(tmp_path):
    called = False

    def send():
        nonlocal called
        called = True
        return 200, VALID_RAW, {}

    with pytest.raises(Phase6PilotError):
        attestation().provider("gemini", "unapproved-model")
    with pytest.raises(Exception):
        execute_pilot_row(row=ROW, provider="gemini", policy=POLICY, registry_status="PREFLIGHT_PENDING_CREDENTIALS", credential_present=True, attestation=attestation(), attestation_sha256="a" * 64, source_commit="b" * 40, raw_root=tmp_path / "raw", normalized_root=tmp_path / "normalized", attempt_root=tmp_path, send=send)
    assert called is False


def test_load_attestation_hashes_the_exact_nonsecret_record(tmp_path):
    path = tmp_path / "attestation.json"
    payload = {"schema_version": "phase6-free-account-attestation-v1", "verification_timestamp_utc": "2026-09-29T00:00:00Z", "source": "account owner", "providers": [
        {"provider": "gemini", "access_tier": "free_tier", "billing_enabled": False, "quota_available": True, "verified_model_ids": ["gemini-3.6-flash"]},
        {"provider": "groq", "access_tier": "free_plan", "billing_enabled": False, "quota_available": True, "verified_model_ids": ["qwen/qwen3.8-27b"]},
    ]}
    path.write_text(json.dumps(payload))
    loaded, digest = load_attestation(path)
    assert loaded.source == "account owner" and len(digest) == 64
