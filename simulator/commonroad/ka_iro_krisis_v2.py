"""Independent deterministic physical executor for KA-IRO KRISIS v2.

This module intentionally does not alter the frozen Phase 4 pilot runner.  It
uses the same KS model, fixed time step, action ontology, and CommonRoad
validators, while accepting the prospectively frozen K2 multi-actor grammar.
"""
from __future__ import annotations

from dataclasses import asdict
from math import atan2, cos, sin
from typing import Any

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import box

from .integrator import integrate_step
from .ks_model import KSControl, KSState, clamp_control
from .pilot import DT, action_control
from .vehicle_params import vehicle_params_v1

PARAMS = vehicle_params_v1()


def footprint(x: float, y: float, orientation: float, length: float, width: float):
    return translate(rotate(box(-length / 2, -width / 2, length / 2, width / 2), orientation, use_radians=True), xoff=x, yoff=y)


def actor_state(spec: dict[str, Any], time_s: float) -> dict[str, float | str]:
    motion = spec["motion"]
    if motion == "static":
        x, y, vx, vy = float(spec["x_m"]), float(spec["y_m"]), 0.0, 0.0
    elif motion == "crossing":
        trigger = float(spec.get("trigger_time_s", 0.0))
        x, y, vx, vy = float(spec["x_m"]), float(spec["start_y_m"]) + float(spec["velocity_y_m"]) * max(0.0, time_s - trigger), 0.0, float(spec["velocity_y_m"])
    elif motion == "longitudinal":
        vx = float(spec["velocity_x_mps"]); x, y, vy = float(spec["start_x_m"]) + vx * time_s, float(spec["y_m"]), 0.0
    elif motion == "cutin":
        start = float(spec.get("start_time_s", 0.0)); duration = float(spec["duration_s"])
        elapsed = min(max(time_s - start, 0.0), duration); fraction = elapsed / duration
        vx = float(spec["velocity_x_mps"])
        x = float(spec["start_x_m"]) + vx * time_s
        start_y, target_y = float(spec["start_y_m"]), float(spec["target_y_m"])
        y = start_y + (target_y - start_y) * (1 - cos(np.pi * fraction)) / 2
        vy = (target_y - start_y) * np.pi * sin(np.pi * fraction) / (2 * duration)
    else:
        raise ValueError(f"unsupported actor motion {motion}")
    orientation = atan2(vy, vx) if vx or vy else float(spec.get("orientation_rad", 0.0))
    return {"actor_id": str(spec["actor_id"]), "actor_type": str(spec["actor_type"]), "x": x, "y": y,
            "orientation": orientation, "vx": vx, "vy": vy, "length_m": float(spec["length_m"]), "width_m": float(spec["width_m"])}


def simulate(scene: dict[str, Any], action_id: str) -> tuple[list[dict[str, Any]], list[list[dict[str, Any]]]]:
    if action_id not in scene["applicable_actions"]:
        return [], []
    ego = scene["ego"]
    state = KSState(float(ego["x_m"]), float(ego["y_m"]), float(ego["steering_angle_rad"]), float(ego["initial_speed_kph"]) / 3.6, float(ego["orientation_rad"]))
    trajectory: list[dict[str, Any]] = []; actors: list[list[dict[str, Any]]] = []
    for index in range(round(float(scene["termination"]["maximum_duration_s"]) / DT) + 1):
        time_s = index * DT; control = action_control(action_id, state)
        trajectory.append({"time_step": index, "time_s": time_s, **asdict(state), **asdict(control)})
        actors.append([actor_state(spec, time_s) for spec in scene["actors"]])
        if index < round(float(scene["termination"]["maximum_duration_s"]) / DT):
            state = integrate_step(state, control, PARAMS, DT).state
    return trajectory, actors


def metrics(scene: dict[str, Any], trajectory: list[dict[str, Any]], actor_samples: list[list[dict[str, Any]]]) -> dict[str, Any]:
    distances: list[float] = []; ttcs: list[float] = []; collision_actor = None; collision_time = None
    for sample, actors in zip(trajectory, actor_samples):
        ego = footprint(sample["x"], sample["y"], sample["orientation"], PARAMS.length, PARAMS.width)
        for actor in actors:
            other = footprint(float(actor["x"]), float(actor["y"]), float(actor["orientation"]), float(actor["length_m"]), float(actor["width_m"]))
            distance = ego.distance(other); distances.append(distance)
            if ego.intersects(other) and collision_actor is None:
                collision_actor, collision_time = actor["actor_id"], sample["time_s"]
            dx, dy = float(actor["x"]) - sample["x"], float(actor["y"]) - sample["y"]
            separation = (dx*dx + dy*dy) ** .5
            closing = ((sample["velocity"] * cos(sample["orientation"]) - float(actor["vx"])) * dx + (sample["velocity"] * sin(sample["orientation"]) - float(actor["vy"])) * dy) / separation if separation else 0.0
            if closing > 0 and distance > 0: ttcs.append(distance / closing)
    lower, upper = scene["road"]["drivable_y_m"]; boundary_time = None
    for sample in trajectory:
        polygon = footprint(sample["x"], sample["y"], sample["orientation"], PARAMS.length, PARAMS.width)
        if polygon.bounds[1] < lower or polygon.bounds[3] > upper:
            boundary_time = sample["time_s"]; break
    accelerations = [x["acceleration"] for x in trajectory]
    lateral = [x["velocity"] ** 2 * np.tan(x["steering_angle"]) / PARAMS.wheelbase for x in trajectory]
    return {"sampled_collision": collision_actor is not None, "collision_actor_id": collision_actor, "collision_time_s": collision_time,
            "minimum_distance_m": min(distances), "minimum_ttc_s": min(ttcs) if ttcs else None, "ttc_defined": bool(ttcs),
            "road_compliant": boundary_time is None, "road_boundary_violation": boundary_time is not None,
            "first_boundary_violation_time_s": boundary_time, "max_deceleration_mps2": min(accelerations),
            "max_jerk_mps3": max([abs(b-a)/DT for a,b in zip(accelerations, accelerations[1:])] or [0.0]),
            "max_lateral_acceleration_mps2": max(abs(v) for v in lateral)}


def commonroad_collision(trajectory: list[dict[str, Any]], actor_samples: list[list[dict[str, Any]]]) -> bool:
    from commonroad_dc import pycrcc
    ego = pycrcc.TimeVariantCollisionObject(0)
    for sample in trajectory:
        ego.append_obstacle(pycrcc.RectOBB(PARAMS.length/2, PARAMS.width/2, sample["orientation"], sample["x"], sample["y"]))
    checker = pycrcc.CollisionChecker()
    actor_ids = sorted({str(actor["actor_id"]) for sample in actor_samples for actor in sample})
    for actor_id in actor_ids:
        obj = pycrcc.TimeVariantCollisionObject(0)
        for sample in actor_samples:
            actor = next(x for x in sample if x["actor_id"] == actor_id)
            obj.append_obstacle(pycrcc.RectOBB(float(actor["length_m"])/2, float(actor["width_m"])/2, float(actor["orientation"]), float(actor["x"]), float(actor["y"])))
        checker.add_collision_object(obj)
    return bool(checker.collide(ego))


def commonroad_trajectory_feasible(trajectory: list[dict[str, Any]]) -> bool:
    from .pilot import commonroad_trajectory_feasible as checker
    return checker(trajectory)
