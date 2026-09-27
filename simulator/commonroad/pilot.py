"""Deterministic Phase 4 pilot runner; it never synthesizes outcome records."""
from __future__ import annotations

import json
from dataclasses import asdict
from math import atan2, cos, sin
from pathlib import Path
from typing import Any

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import box

from .integrator import integrate_step
from .ks_model import KSControl, KSState, clamp_control
from .vehicle_params import vehicle_params_v1

ROOT = Path(__file__).resolve().parents[2]
DT = 0.05
PARAMS = vehicle_params_v1()


def load_json_yaml(path: Path) -> dict[str, Any]:
    """All frozen .yaml files are JSON-compatible YAML, avoiding an unpinned parser."""
    return json.loads(path.read_text(encoding="utf-8"))


def action_control(action_id: str, state: KSState) -> KSControl:
    profiles = load_json_yaml(ROOT / "configs/simulator/actions_v1.yaml")["profiles"]
    profile = profiles[action_id]
    target = float(profile["steering_target_rad"])
    requested_rate = (target - state.steering_angle) / DT
    return clamp_control(KSControl(requested_rate, float(profile["acceleration_mps2"])), PARAMS)


def actor_state(scenario: dict[str, Any], t: float) -> dict[str, float]:
    actor = scenario["actor"]
    kind = actor["actor_type"]
    if kind == "static_vehicle":
        return {"x": actor["center_x_m"], "y": actor["center_y_m"], "orientation": 0.0, "vx": 0.0, "vy": 0.0}
    if kind == "generic_pedestrian":
        y = actor["start_y_m"] + actor["speed_mps"] * max(0.0, t - actor["trigger_time_s"])
        return {"x": actor["start_x_m"], "y": y, "orientation": np.pi / 2, "vx": 0.0, "vy": actor["speed_mps"]}
    elapsed = min(max(t - actor["cutin_start_s"], 0.0), actor["cutin_duration_s"])
    fraction = elapsed / actor["cutin_duration_s"]
    # Cosine easing gives a continuous lateral velocity at both ends.
    y = actor["start_y_m"] + (actor["target_y_m"] - actor["start_y_m"]) * (1 - cos(np.pi * fraction)) / 2
    vy = (actor["target_y_m"] - actor["start_y_m"]) * np.pi * sin(np.pi * fraction) / (2 * actor["cutin_duration_s"])
    return {"x": actor["start_x_m"] + actor["speed_mps"] * t, "y": y, "orientation": atan2(vy, actor["speed_mps"]), "vx": actor["speed_mps"], "vy": vy}


def footprint(x: float, y: float, orientation: float, length: float, width: float):
    return translate(rotate(box(-length / 2, -width / 2, length / 2, width / 2), orientation, use_radians=True), xoff=x, yoff=y)


def simulate(scenario: dict[str, Any], action_id: str, speed_kph: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return executable state/control samples and actor samples for one deterministic run."""
    if action_id not in scenario["applicable_actions"]:
        return [], []
    ego = scenario["ego"]
    state = KSState(ego["x_m"], ego["y_m"], ego["steering_angle_rad"], speed_kph / 3.6, ego["orientation_rad"])
    trajectory, actors = [], []
    duration = scenario["termination"]["maximum_duration_s"]
    for index in range(round(duration / DT) + 1):
        time_s = index * DT
        actor = actor_state(scenario, time_s)
        control = action_control(action_id, state)
        trajectory.append({"time_step": index, "time_s": time_s, **asdict(state), **asdict(control)})
        actors.append({"time_step": index, "time_s": time_s, **actor})
        if index < round(duration / DT):
            state = integrate_step(state, control, PARAMS, DT).state
    return trajectory, actors


def shapely_metrics(scenario: dict[str, Any], trajectory: list[dict[str, Any]], actors: list[dict[str, Any]]) -> dict[str, Any]:
    actor_spec = scenario["actor"]
    distances, collision_index, ttcs = [], None, []
    for sample, actor in zip(trajectory, actors):
        ego_shape = footprint(sample["x"], sample["y"], sample["orientation"], PARAMS.length, PARAMS.width)
        actor_shape = footprint(actor["x"], actor["y"], actor["orientation"], actor_spec["length_m"], actor_spec["width_m"])
        distance = ego_shape.distance(actor_shape)
        distances.append(distance)
        if ego_shape.intersects(actor_shape) and collision_index is None:
            collision_index = sample["time_step"]
        dx, dy = actor["x"] - sample["x"], actor["y"] - sample["y"]
        separation = (dx * dx + dy * dy) ** 0.5
        closing = ((sample["velocity"] * cos(sample["orientation"]) - actor["vx"]) * dx + (sample["velocity"] * sin(sample["orientation"]) - actor["vy"]) * dy) / separation if separation else 0.0
        if closing > 0 and distance > 0:
            ttcs.append(distance / closing)
    accelerations = [s["acceleration"] for s in trajectory]
    lateral = [s["velocity"] ** 2 * np.tan(s["steering_angle"]) / PARAMS.wheelbase for s in trajectory]
    return {
        "sampled_collision": collision_index is not None, "sampled_collision_time_s": None if collision_index is None else collision_index * DT,
        "minimum_distance_m": min(distances), "minimum_ttc_s": min(ttcs) if ttcs else None, "ttc_defined": bool(ttcs),
        "max_deceleration_mps2": min(accelerations), "max_jerk_mps3": max([abs(b - a) / DT for a, b in zip(accelerations, accelerations[1:])] or [0.0]),
        "max_lateral_acceleration_mps2": max(abs(x) for x in lateral),
    }


def road_compliance(scenario: dict[str, Any], trajectory: list[dict[str, Any]]) -> tuple[bool, float | None]:
    lower, upper = scenario["road"]["drivable_y_m"]
    for sample in trajectory:
        polygon = footprint(sample["x"], sample["y"], sample["orientation"], PARAMS.length, PARAMS.width)
        ymin, ymax = polygon.bounds[1], polygon.bounds[3]
        if ymin < lower or ymax > upper:
            return False, sample["time_s"]
    return True, None


def commonroad_collision(scenario: dict[str, Any], trajectory: list[dict[str, Any]], actors: list[dict[str, Any]]) -> bool:
    """Primary sampled occupancy check using the installed CommonRoad pycrcc API."""
    from commonroad_dc import pycrcc
    ego = pycrcc.TimeVariantCollisionObject(0)
    actor = pycrcc.TimeVariantCollisionObject(0)
    actor_spec = scenario["actor"]
    for sample, other in zip(trajectory, actors):
        ego.append_obstacle(pycrcc.RectOBB(PARAMS.length / 2, PARAMS.width / 2, sample["orientation"], sample["x"], sample["y"]))
        actor.append_obstacle(pycrcc.RectOBB(actor_spec["length_m"] / 2, actor_spec["width_m"] / 2, other["orientation"], other["x"], other["y"]))
    checker = pycrcc.CollisionChecker()
    checker.add_collision_object(actor)
    return bool(checker.collide(ego))


def commonroad_road_boundary_violation(scenario: dict[str, Any], trajectory: list[dict[str, Any]]) -> bool:
    """Use the installed CommonRoad road-boundary constructor as the authority."""
    from commonroad.scenario.lanelet import Lanelet
    from commonroad.scenario.scenario import Scenario
    from commonroad_dc import pycrcc
    from commonroad_dc.boundary.boundary import create_road_boundary_obstacle

    length = scenario["road"]["length_m"]
    lower, upper = scenario["road"]["drivable_y_m"]
    middle = (lower + upper) / 2
    scenario_cr = Scenario(DT)
    right = Lanelet(np.array([[0, lower], [length, lower]]), np.array([[0, 0], [length, 0]]), np.array([[0, 1.75], [length, 1.75]]), 1, adjacent_left=2, adjacent_left_same_direction=True)
    left = Lanelet(np.array([[0, 1.75], [length, 1.75]]), np.array([[0, middle], [length, middle]]), np.array([[0, upper], [length, upper]]), 2, adjacent_right=1, adjacent_right_same_direction=True)
    scenario_cr.add_objects([right, left])
    _, boundary = create_road_boundary_obstacle(scenario_cr, method="obb_rectangles")
    ego = pycrcc.TimeVariantCollisionObject(0)
    for sample in trajectory:
        ego.append_obstacle(pycrcc.RectOBB(PARAMS.length / 2, PARAMS.width / 2, sample["orientation"], sample["x"], sample["y"]))
    checker = pycrcc.CollisionChecker()
    checker.add_collision_object(boundary)
    return bool(checker.collide(ego))


def commonroad_trajectory_feasible(trajectory: list[dict[str, Any]]) -> bool:
    """Validate the generated trajectory with CommonRoad's installed KS checker."""
    from commonroad.common.solution import VehicleType
    from commonroad.scenario.state import KSState as CommonRoadKSState
    from commonroad.scenario.trajectory import Trajectory
    from commonroad_dc.feasibility.feasibility_checker import trajectory_feasibility
    from commonroad_dc.feasibility.vehicle_dynamics import VehicleDynamics

    states = [CommonRoadKSState(position=np.array([sample["x"], sample["y"]]), steering_angle=sample["steering_angle"], velocity=sample["velocity"], orientation=sample["orientation"], time_step=sample["time_step"]) for sample in trajectory]
    feasible, _ = trajectory_feasibility(Trajectory(0, states), VehicleDynamics.KS(VehicleType.FORD_ESCORT), DT)
    return bool(feasible)
