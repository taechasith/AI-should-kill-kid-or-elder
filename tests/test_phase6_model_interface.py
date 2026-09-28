import json
from pathlib import Path

import pytest

from geosave.model_adapters import build_provider_request
from geosave.phase6_inputs import INPUT_ROOT
from geosave.phase6_interface import (
    ALLOWED_ACTIONS,
    deterministic_action_order,
    normalized_record,
    parse_phase6_response,
    persist_normalized_record,
    persist_raw_response,
)
from geosave.phase6_prompts import PromptConstructionError, build_phase6_user_message


VALID_RESPONSE = json.dumps(
    {
        "decision_status": "CHOOSE",
        "selected_action_id": "A2",
        "stated_factors": ["collision_avoidance", "legal_uncertainty"],
        "legal_claims": [
            {
                "claim_type": "uncertainty",
                "action_id": None,
                "statement": "The supplied legal evidence is unresolved.",
                "evidence_ids": [],
            }
        ],
        "evidence_ids_cited": [],
        "uncertainty_statement": "The legal status is not determined by the supplied context.",
        "short_rationale": "Brake to reduce immediate conflict exposure without claiming legal certainty.",
    }
)


def _package() -> tuple[dict, dict, dict, Path]:
    package_dir = INPUT_ROOT / "packages" / "PED-CROSS-001__V030"
    telemetry = json.loads((package_dir / "telemetry.json").read_text())
    actions = json.loads((package_dir / "candidate_actions.json").read_text())
    contexts = [json.loads(line) for line in (INPUT_ROOT / "condition_contexts.jsonl").read_text().splitlines()]
    context = next(item for item in contexts if item["context_id"] == "PED-CROSS-001__V030__ARG")
    return telemetry, actions, context, package_dir / "birdseye_initial_state.png"


def test_phase6_parser_is_strict_and_never_guesses_a_choice():
    valid = parse_phase6_response(VALID_RESPONSE)
    assert valid.status == "valid"
    assert valid.decision and valid.decision.selected_action_id == "A2"
    repaired = parse_phase6_response(f"```json\n{VALID_RESPONSE}\n```")
    assert repaired.status == "repaired" and repaired.repair_attempted
    invalid = parse_phase6_response('{"decision_status":"CHOOSE"}')
    assert invalid.status == "failed" and invalid.decision is None
    normalized = normalized_record(
        run_id="P6-test",
        model_id="model",
        model_revision="revision",
        prompt_version="v1",
        condition="C0",
        input_package_id="PED-CROSS-001__V030",
        country_iso3=None,
        law_snapshot="phase5-legal-snapshot-v1",
        action_order=ALLOWED_ACTIONS,
        raw_response_reference="data/model_benchmark/phase6/raw/P6-test.txt",
        result=invalid,
    )
    assert normalized["decision_status"] == "INVALID"
    assert normalized["selected_action_id"] is None


def test_phase6_raw_and_normalized_storage_is_append_only(tmp_path: Path):
    raw_path = tmp_path / "raw.txt"
    normal_path = tmp_path / "normalized.json"
    raw_hash = persist_raw_response(raw_path, VALID_RESPONSE)
    assert len(raw_hash) == 64
    with pytest.raises(FileExistsError):
        persist_raw_response(raw_path, VALID_RESPONSE)
    result = parse_phase6_response(VALID_RESPONSE)
    record = normalized_record(
        run_id="P6-storage",
        model_id="model",
        model_revision="revision",
        prompt_version="v1",
        condition="C0",
        input_package_id="PED-CROSS-001__V030",
        country_iso3=None,
        law_snapshot="phase5-legal-snapshot-v1",
        action_order=ALLOWED_ACTIONS,
        raw_response_reference="raw.txt",
        result=result,
    )
    assert len(persist_normalized_record(normal_path, record)) == 64
    with pytest.raises(FileExistsError):
        persist_normalized_record(normal_path, record)


def test_action_order_is_deterministic_and_complete():
    first = deterministic_action_order("P6-order")
    assert first == deterministic_action_order("P6-order")
    assert set(first) == set(ALLOWED_ACTIONS)


def test_prompt_conditions_preserve_information_boundary():
    telemetry, actions, context, _ = _package()
    c0 = build_phase6_user_message(
        condition="C0", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=None
    )
    assert "structured_legal_context" not in c0
    assert "geosave_constrained_support" not in c0
    c4 = build_phase6_user_message(
        condition="C4", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=context
    )
    assert "geosave_constrained_support" in c4
    with pytest.raises(PromptConstructionError):
        build_phase6_user_message(
            condition="C3", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=context
        )


def test_offline_provider_adapters_carry_image_without_tool_fields():
    telemetry, actions, _, image_path = _package()
    message = build_phase6_user_message(
        condition="C0", telemetry=telemetry, candidate_actions=actions, action_order=ALLOWED_ACTIONS, condition_context=None
    )
    for provider, model_id in (("openai", "gpt-4.1-2025-04-14"), ("anthropic", "claude-sonnet-5"), ("mistral", "mistral-large-2512")):
        request = build_provider_request(
            provider=provider,
            model_id=model_id,
            image_path=image_path,
            system_message="closed-book system",
            user_message=message,
            max_output_tokens=500,
        )
        serialized = json.dumps(request.body)
        assert "data:image/png;base64," in serialized or '"type": "base64"' in serialized
        assert '"tools"' not in serialized
        assert request.request_hash == request.request_hash
