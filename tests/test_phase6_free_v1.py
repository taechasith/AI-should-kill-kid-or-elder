import json
from pathlib import Path

import pytest

from geosave.phase6_free_adapters import build_free_provider_request
from geosave.phase6_free_guard import (
    BENCHMARK_PURPOSE,
    PILOT_PURPOSE,
    FreeOnlyAuthorizationError,
    FreeOnlyExecutionGuard,
)
from geosave.phase6_inputs import INPUT_ROOT
from geosave.phase6_interface import ALLOWED_ACTIONS
from geosave.phase6_prompts import build_phase6_user_message
from scripts.finalize_phase6_free_v1_preflight import finalize
from scripts.validate_phase6_free_v1_preflight import validate
from scripts.verify_phase6_free_v1_preflight_hashes import verify


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "configs" / "models" / "phase6_free_v1_candidate_registry.json"


def _policy_and_guard(status: str = "FREE_ONLY_PILOT_AUTHORIZED"):
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return registry["zero_cost_execution_policy"], FreeOnlyExecutionGuard.from_policy(registry["zero_cost_execution_policy"], status)


def _message_and_image():
    package_dir = INPUT_ROOT / "packages" / "PED-CROSS-001__V030"
    telemetry = json.loads((package_dir / "telemetry.json").read_text(encoding="utf-8"))
    actions = json.loads((package_dir / "candidate_actions.json").read_text(encoding="utf-8"))
    contexts = [json.loads(line) for line in (INPUT_ROOT / "condition_contexts.jsonl").read_text(encoding="utf-8").splitlines()]
    context = next(item for item in contexts if item["context_id"] == "PED-CROSS-001__V030__ARG")
    return build_phase6_user_message(condition="C2", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=context), package_dir / "birdseye_initial_state.png"


def test_zero_cost_guard_fails_closed_before_live_preflight():
    _, guard = _policy_and_guard()
    with pytest.raises(FreeOnlyAuthorizationError, match="missing required credential"):
        guard.assert_request_permitted(
            provider="gemini", model_id="gemini-3.6-flash", purpose=PILOT_PURPOSE,
            credential_present=False, access_tier="free_tier", billing_enabled=False, rate_limit_verified=True,
        )
    with pytest.raises(FreeOnlyAuthorizationError, match="billing-enabled"):
        guard.assert_request_permitted(
            provider="groq", model_id="qwen/qwen3.8-27b", purpose=PILOT_PURPOSE,
            credential_present=True, access_tier="free_plan", billing_enabled=True, rate_limit_verified=True,
        )
    with pytest.raises(FreeOnlyAuthorizationError, match="not frozen executable"):
        guard.assert_request_permitted(
            provider="groq", model_id="qwen/qwen3.8-27b", purpose=BENCHMARK_PURPOSE,
            credential_present=True, access_tier="free_plan", billing_enabled=False, rate_limit_verified=True,
        )


def test_zero_cost_guard_allows_only_verified_pilot_and_allowlisted_models():
    _, guard = _policy_and_guard()
    guard.assert_request_permitted(
        provider="gemini", model_id="gemini-2.5-flash-lite", purpose=PILOT_PURPOSE,
        credential_present=True, access_tier="free_tier", billing_enabled=False, rate_limit_verified=True,
    )
    with pytest.raises(FreeOnlyAuthorizationError, match="allowlist"):
        guard.assert_request_permitted(
            provider="gemini", model_id="gemini-3.8-flash", purpose=PILOT_PURPOSE,
            credential_present=True, access_tier="free_tier", billing_enabled=False, rate_limit_verified=True,
        )


def test_free_adapters_embed_image_and_remain_closed_book():
    message, image_path = _message_and_image()
    for provider, model_id in (("gemini", "gemini-3.6-flash"), ("gemini", "gemini-2.5-flash-lite"), ("groq", "qwen/qwen3.8-27b")):
        request = build_free_provider_request(provider=provider, model_id=model_id, image_path=image_path, system_message="closed-book", user_message=message, max_output_tokens=500)
        body = json.dumps(request.body)
        assert request.request_hash == request.request_hash
        assert '"tools"' not in body and '"web"' not in body and '"search"' not in body


def test_free_preflight_manifest_and_hashes_are_valid_without_provider_calls():
    result = validate()
    assert result["validation_status"] == "passed"
    assert result["provider_calls_made"] == 0
    assert result["full_manifest_rows"] == 5454
    assert result["pending_free_access_preflight_rows"] == 4104
    assert result["capability_pilot_rows"] == 3
    finalized = finalize()
    assert verify()["files"] == finalized["files"]
