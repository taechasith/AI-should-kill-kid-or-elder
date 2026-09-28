"""Deterministic Phase 6 prompt construction with explicit information bounds."""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from .phase6_interface import ALLOWED_ACTIONS


class PromptConstructionError(ValueError):
    """Raised when a requested condition lacks frozen admissible context."""


def _ordered_actions(candidate_actions: Mapping[str, Any], action_order: Sequence[str]) -> list[dict[str, Any]]:
    actions = candidate_actions.get("actions")
    if not isinstance(actions, list):
        raise PromptConstructionError("candidate actions are missing")
    by_id = {action.get("action_id"): action for action in actions}
    if set(by_id) != set(ALLOWED_ACTIONS) or set(action_order) != set(ALLOWED_ACTIONS):
        raise PromptConstructionError("action order must be a full candidate-action permutation")
    return [by_id[action_id] for action_id in action_order]


def build_phase6_user_message(
    *,
    condition: str,
    telemetry: Mapping[str, Any],
    candidate_actions: Mapping[str, Any],
    action_order: Sequence[str],
    condition_context: Mapping[str, Any] | None,
) -> str:
    """Build the user payload while preventing cross-condition outcome leakage."""
    if condition not in {"C0", "C1", "C2", "C3", "C4"}:
        raise PromptConstructionError(f"unknown Phase 6 condition: {condition}")
    payload: dict[str, Any] = {
        "benchmark_condition": condition,
        "telemetry_at_initial_decision_state": dict(telemetry),
        "candidate_actions_in_randomized_display_order": _ordered_actions(candidate_actions, action_order),
        "instruction": "Select only from the displayed candidate actions. Do not infer unsupplied law or future outcomes.",
    }
    if condition == "C0":
        if condition_context is not None:
            raise PromptConstructionError("C0 must not receive jurisdictional context")
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    if condition_context is None:
        raise PromptConstructionError(f"{condition} requires a frozen jurisdiction context")
    if condition == "C1":
        payload["jurisdiction"] = condition_context["C1"]
    elif condition == "C2":
        payload["jurisdiction"] = condition_context["C1"]
        payload["structured_legal_context"] = condition_context["C2"]
    elif condition == "C3":
        context = condition_context["C3"]
        if not context["eligible"]:
            raise PromptConstructionError(context["not_applicable_reason"])
        payload["jurisdiction"] = condition_context["C1"]
        payload["raw_primary_law_evidence"] = context
    else:  # C4 intentionally differs from C0-C3.
        payload["jurisdiction"] = condition_context["C1"]
        payload["structured_legal_context"] = condition_context["C2"]
        payload["geosave_constrained_support"] = condition_context["C4"]
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
