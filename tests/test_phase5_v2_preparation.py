from geosave.phase5_v2 import required_fields


def test_lateral_actions_require_noninvented_geometry_to_law_mapping_facts():
    required = required_fields("PED-CROSS-001", "A3")
    assert "traffic_side" in required
    assert "steering_enters_opposing_traffic" in required


def test_non_lateral_action_does_not_claim_lane_crossing_fact():
    assert "steering_enters_opposing_traffic" not in required_fields("MOTO-CUTIN-001", "A2")
