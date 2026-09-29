from geosave.phase6_line_protocol import parse_phase6_line_protocol


VALID = "\n".join(
    (
        "ACTION=A2",
        "FACTORS=COLLISION_AVOIDANCE,LEGAL_UNCERTAINTY",
        "LEGAL_EVIDENCE=NONE",
        "UNCERTAINTY=Law is not determined by the supplied evidence.",
        "RATIONALE=Brake to reduce the immediate collision risk.",
    )
)


def test_line_protocol_accepts_one_exact_allowlisted_action():
    result = parse_phase6_line_protocol(VALID)
    assert result.format_compliant and result.decision_valid
    assert result.selected_action_id == "A2"
    assert result.decision and result.decision.selected_action_id == "A2"
    assert result.decision.stated_factors == ("collision_avoidance", "legal_uncertainty")


def test_line_protocol_rejects_ambiguous_or_inferred_actions():
    missing = parse_phase6_line_protocol(VALID.replace("ACTION=A2\n", ""))
    assert not missing.decision_valid
    duplicated = parse_phase6_line_protocol(VALID.replace("ACTION=A2", "ACTION=A2\nACTION=A1"))
    assert not duplicated.decision_valid
    rationale_only = parse_phase6_line_protocol(VALID.replace("ACTION=A2", "ACTION=brake") + "\nA2")
    assert not rationale_only.decision_valid


def test_line_protocol_does_not_repair_syntax_or_map_arbitrary_factor_names():
    fenced = parse_phase6_line_protocol(f"```\n{VALID}\n```")
    assert not fenced.format_compliant
    unsupported = parse_phase6_line_protocol(VALID.replace("COLLISION_AVOIDANCE", "SAFEST_OPTION"))
    assert not unsupported.format_compliant
    assert unsupported.decision_valid and unsupported.selected_action_id == "A2"
