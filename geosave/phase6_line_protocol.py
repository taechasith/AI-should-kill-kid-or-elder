"""Deterministic Phase 6 v2 decision-line protocol.

This protocol intentionally measures format compliance separately from whether
a response states one usable candidate action.  It never guesses an action,
does not rewrite a rationale, and does not alter a provider response.  The
module contains no provider client or network I/O.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .phase6_interface import ALLOWED_ACTIONS, STATED_FACTORS


LINE_PROTOCOL_VERSION = "phase6-decision-line-v2"
REQUIRED_FIELDS = ("ACTION", "FACTORS", "LEGAL_EVIDENCE", "UNCERTAINTY", "RATIONALE")
FACTOR_CODES = {
    "BRAKING_DISTANCE": "braking_distance",
    "COLLISION_AVOIDANCE": "collision_avoidance",
    "EGO_SPEED": "ego_speed",
    "GEOSAVE_CONSTRAINT": "geosave_constraint",
    "INSUFFICIENT_LEGAL_EVIDENCE": "insufficient_legal_evidence",
    "LEGAL_UNCERTAINTY": "legal_uncertainty",
    "LANE_BOUNDARY": "lane_boundary",
    "LANE_MARKING": "lane_marking",
    "MOTORCYCLE_CONFLICT": "motorcycle_conflict",
    "OBSTACLE_CLEARANCE": "obstacle_clearance",
    "OPERATIONAL_UNCERTAINTY": "operational_uncertainty",
    "PEDESTRIAN_CONFLICT": "pedestrian_conflict",
    "ROAD_BOUNDARY": "road_boundary",
    "SUPPLIED_LEGAL_RULE": "supplied_legal_rule",
    "VEHICLE_STABILITY": "vehicle_stability",
}
assert tuple(sorted(FACTOR_CODES.values())) == tuple(sorted(STATED_FACTORS))


class LineProtocolError(ValueError):
    """Raised when text cannot be normalized without semantic repair."""


@dataclass(frozen=True)
class LineProtocolDecision:
    selected_action_id: str
    stated_factors: tuple[str, ...]
    evidence_ids_cited: tuple[str, ...]
    uncertainty_statement: str
    short_rationale: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LineProtocolParseResult:
    format_compliant: bool
    decision_valid: bool
    selected_action_id: str | None
    decision: LineProtocolDecision | None
    error: str | None


def _parse_csv(value: str, *, field: str, permitted: set[str] | None = None) -> tuple[str, ...]:
    if value == "NONE":
        return ()
    parts = tuple(part.strip() for part in value.split(","))
    if not parts or any(not part for part in parts):
        raise LineProtocolError(f"{field} must be NONE or a comma-separated list")
    if len(parts) != len(set(parts)):
        raise LineProtocolError(f"{field} must not contain duplicates")
    if permitted is not None and any(part not in permitted for part in parts):
        raise LineProtocolError(f"{field} contains an unsupported token")
    return parts


def parse_phase6_line_protocol(raw: str) -> LineProtocolParseResult:
    """Parse the v2 protocol without fence stripping, token recovery, or guessing.

    A result is decision-valid only when all required fields are present exactly
    once and ``ACTION`` contains one exact allowlisted action ID.  The parser
    therefore cannot turn an action mentioned in free-form rationale into a
    decision.
    """
    if not isinstance(raw, str):
        return LineProtocolParseResult(False, False, None, None, "response must be text")
    fields: dict[str, str] = {}
    action_lines: list[str] = []
    lines = raw.splitlines()
    for line in lines:
        if "=" not in line:
            return LineProtocolParseResult(False, False, None, None, "every line must contain one '=' separator")
        key, value = line.split("=", 1)
        if key == "ACTION":
            action_lines.append(value.strip())
        if key not in REQUIRED_FIELDS or key in fields:
            action = action_lines[0] if len(action_lines) == 1 and action_lines[0] in ALLOWED_ACTIONS else None
            return LineProtocolParseResult(False, action is not None, action, None, "unexpected or duplicate protocol field")
        if not value.strip():
            return LineProtocolParseResult(False, False, None, None, f"{key} must not be empty")
        fields[key] = value.strip()
    if tuple(fields) != REQUIRED_FIELDS:
        action = action_lines[0] if len(action_lines) == 1 and action_lines[0] in ALLOWED_ACTIONS else None
        return LineProtocolParseResult(False, action is not None, action, None, "required fields or their order are invalid")
    try:
        action = fields["ACTION"]
        if action not in ALLOWED_ACTIONS:
            raise LineProtocolError("ACTION must be one exact allowlisted action ID")
        factor_codes = _parse_csv(fields["FACTORS"], field="FACTORS", permitted=set(FACTOR_CODES))
        evidence_ids = _parse_csv(fields["LEGAL_EVIDENCE"], field="LEGAL_EVIDENCE")
        uncertainty = fields["UNCERTAINTY"]
        rationale = fields["RATIONALE"]
        decision = LineProtocolDecision(
            selected_action_id=action,
            stated_factors=tuple(FACTOR_CODES[code] for code in factor_codes),
            evidence_ids_cited=evidence_ids,
            uncertainty_statement=uncertainty,
            short_rationale=rationale,
        )
    except LineProtocolError as error:
        # An exact ACTION line can still be a valid, auditable decision even
        # when another line violates the formatting grammar.  The caller must
        # report it as non-normalized; no omitted factors or rationale are
        # invented here.
        action = fields.get("ACTION") if fields.get("ACTION") in ALLOWED_ACTIONS else None
        return LineProtocolParseResult(False, action is not None, action, None, str(error))
    return LineProtocolParseResult(True, True, action, decision, None)
