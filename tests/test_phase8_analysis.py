from geosave.phase8_analysis import weighted_action_distribution


def test_weighted_action_distribution_uses_design_weights():
    units = [
        {"base_weight": 9.0, "selected_action_id": "A0"},
        {"base_weight": 1.0, "selected_action_id": "A1"},
    ]
    assert weighted_action_distribution(units) == {"A0": 0.9, "A1": 0.1}
