"""Deterministic candidate-action gating for scenario packages."""

from __future__ import annotations

from typing import Any, Mapping


def action_gate(scenario: Mapping[str, Any], action_id: str) -> tuple[bool, str | None]:
    """Return eligibility and a machine-readable rejection reason, if any."""
    constraints = scenario["action_constraints"]
    if action_id not in scenario["candidate_actions"]:
        return False, "not_a_candidate_action"
    if action_id in constraints.get("physically_infeasible_actions", []):
        return False, "physically_infeasible"
    if action_id in constraints.get("unstable_actions", []):
        return False, "stability_failure_risk"
    return True, None


def eligible_actions(scenario: Mapping[str, Any]) -> list[str]:
    """Return scenario actions surviving the feasibility and stability gates."""
    return [action for action in scenario["candidate_actions"] if action_gate(scenario, action)[0]]
