from scripts.validate_phase6_free_pilot import validate


def test_failed_free_pilot_is_complete_and_append_only() -> None:
    result = validate()
    assert result["validation_status"] == "passed"
    assert result["phase6_status"] == "BLOCKED_FROZEN_PANEL"
    assert result["planned_pilot_rows"] == 3
    assert result["model_generation_requests_attempted"] == 6
    assert result["completed_rows"] == 0
    assert result["failed_rows"] == 3
    assert result["no_model_response_fabricated"] is True
