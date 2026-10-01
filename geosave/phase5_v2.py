"""Phase 5 v2 preparation helpers.

These helpers derive only metadata present in frozen Phase 4/Phase 6 inputs.
They are deliberately incapable of resolving an action to a legal conclusion.
"""
from __future__ import annotations

import json
from pathlib import Path


SCENARIOS = ("PED-CROSS-001", "OBS-LANE-001", "MOTO-CUTIN-001")
SPEEDS = (30, 50)
ACTIONS = ("A0", "A1", "A2", "A3", "A4", "A6")

UNKNOWN_FIELDS = {
    "road_type": "UNKNOWN", "urban_rural_classification": "UNKNOWN",
    "traffic_side": "UNKNOWN", "lane_marking_type": "UNKNOWN",
    "steering_crosses_lane_marking": "UNKNOWN", "steering_enters_opposing_traffic": "UNKNOWN",
    "steering_enters_shoulder_or_verge": "UNKNOWN", "pedestrian_crossing_designation": "UNKNOWN",
    "pedestrian_signal_state": "UNKNOWN", "posted_speed_limit_kph": "UNKNOWN",
    "locality": "UNKNOWN", "emergency_necessity": "UNKNOWN",
    "alternative_action_availability": "UNKNOWN", "traffic_signal_state": "UNKNOWN",
}


def package_id(scenario_id: str, speed: int) -> str:
    return f"{scenario_id}__V{speed:03d}"


def fact_id(scenario_id: str, speed: int, field: str) -> str:
    return f"P5V2F-{scenario_id}-V{speed:03d}-{field.upper()}"


def question_id(scenario_id: str, speed: int, action_id: str) -> str:
    return f"P5V2Q-{scenario_id}-V{speed:03d}-{action_id}"


def legal_categories(scenario_id: str, action_id: str) -> list[str]:
    categories = ["collision_avoidance_duty"]
    if scenario_id == "PED-CROSS-001":
        categories.append("pedestrian_priority")
    if scenario_id == "OBS-LANE-001":
        categories.extend(["stationary_obstacle", "lane_keeping_or_passing"])
    if scenario_id == "MOTO-CUTIN-001":
        categories.extend(["motorcycle_interaction", "safe_speed_or_following"])
    if action_id in {"A3", "A4"}:
        categories.extend(["lateral_maneuver", "lane_marking", "emergency_exception"])
    if action_id in {"A1", "A2", "A6"}:
        categories.append("braking_or_stopping")
    return categories


def required_fields(scenario_id: str, action_id: str) -> list[str]:
    fields = ["road_type", "traffic_side", "posted_speed_limit_kph", "emergency_necessity"]
    if scenario_id == "PED-CROSS-001":
        fields += ["pedestrian_crossing_designation", "pedestrian_signal_state"]
    if scenario_id == "OBS-LANE-001":
        fields += ["lane_marking_type", "traffic_signal_state"]
    if action_id in {"A3", "A4"}:
        fields += ["steering_crosses_lane_marking", "steering_enters_opposing_traffic", "steering_enters_shoulder_or_verge"]
    return sorted(set(fields))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
