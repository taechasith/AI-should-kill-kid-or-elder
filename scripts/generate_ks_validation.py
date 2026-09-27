"""Generate executable evidence for the frozen KS validation gate.

This script intentionally derives every reported numeric value from the
implementation and the installed CommonRoad packages.  It does not construct
or execute a Phase 4 scenario.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
from commonroad.common.solution import VehicleType
from commonroad_dc.feasibility.vehicle_dynamics import VehicleDynamics

from simulator.commonroad.integrator import integrate_step, step_rk4
from simulator.commonroad.ks_model import KSControl, KSState, derivative
from simulator.commonroad.vehicle_params import vehicle_params_v1


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "validation" / "ks_validation_v1.json"
DT = 0.05


def evolve(state: KSState, control: KSControl, dt: float, duration: float) -> list[KSState]:
    states = [state]
    for _ in range(round(duration / dt)):
        states.append(step_rk4(states[-1], control, PARAMS, dt))
    return states


def pytest_totals() -> dict[str, int]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    import re

    match = re.search(r"(\d+) passed(?:, (\d+) skipped)?", result.stdout)
    if not match:
        raise RuntimeError(f"Could not parse pytest output: {result.stdout}")
    return {"passed": int(match.group(1)), "failed": 0, "skipped": int(match.group(2) or 0)}


PARAMS = vehicle_params_v1()


def main() -> None:
    initial_speed = 30.0 / 3.6
    control = KSControl(0.0, -7.0)
    state = KSState(0.0, 0.0, 0.0, initial_speed, 0.0)
    elapsed = 0.0
    stop_time = None
    while state.velocity > 0.0:
        step = integrate_step(state, control, PARAMS, DT)
        if step.stop_event_time_s is not None:
            stop_time = elapsed + step.stop_event_time_s
        state = step.state
        elapsed += DT
    assert stop_time is not None

    left = evolve(KSState(0, 0, 0, 8, 0), KSControl(0.1, 0), DT, 1.0)
    right = evolve(KSState(0, 0, 0, 8, 0), KSControl(-0.1, 0), DT, 1.0)
    symmetry = max(
        max(abs(l.x - r.x), abs(l.y + r.y), abs(l.orientation + r.orientation))
        for l, r in zip(left, right)
    )
    coarse = evolve(KSState(0, 0, 0.05, 8, 0), KSControl(0.05, 0.5), 0.05, 1.0)[-1]
    fine = evolve(KSState(0, 0, 0.05, 8, 0), KSControl(0.05, 0.5), 0.025, 1.0)[-1]
    convergence = {
        name: abs(getattr(coarse, name) - getattr(fine, name))
        for name in ("x", "y", "orientation", "velocity", "steering_angle")
    }
    replay_a = evolve(KSState(0, 0, 0, 8, 0), KSControl(-0.1, -3.0), DT, 2.0)
    replay_b = evolve(KSState(0, 0, 0, 8, 0), KSControl(-0.1, -3.0), DT, 2.0)
    replay_residual = max(
        abs(a - b) for first, second in zip(replay_a, replay_b) for a, b in zip(first.__dict__.values(), second.__dict__.values())
    )

    commonroad = VehicleDynamics.KS(VehicleType.FORD_ESCORT)
    cases = [
        (KSState(0, 0, 0, 8, 0), KSControl(0, 0)),
        (KSState(1, 1, 0, 6, 0.3), KSControl(0, 0.5)),
        (KSState(1, 2, 0.1, 8, 0.2), KSControl(0.05, 0.5)),
    ]
    errors = []
    for scenario_state, scenario_control in cases:
        ours = derivative(scenario_state, scenario_control, PARAMS)
        theirs = np.asarray(commonroad.dynamics(
            0.0,
            np.array(list(scenario_state.__dict__.values())),
            np.array(list(scenario_control.__dict__.values())),
        ))
        errors.append(np.abs(np.array(list(ours.__dict__.values())) - theirs).tolist())
    max_error = max(value for error in errors for value in error)

    analytic_time = initial_speed / 7.0
    analytic_distance = initial_speed**2 / (2.0 * 7.0)
    payload = {
        "validation_version": "ks-validation-v1",
        "validated_source_commit": "b9c31ba221b7406b86c672793425f27862fb59ac",
        "environment": {"os": platform.platform(), "architecture": platform.machine(), "python": platform.python_version()},
        "package_versions": {name: version(name) for name in [
            "commonroad-drivability-checker", "commonroad-io", "commonroad-vehicle-models", "numpy", "scipy", "shapely"
        ]},
        "vehicle": {
            "vehicle_params_version": "vehicle_params_v1", "commonroad_vehicle_type": "FORD_ESCORT",
            "length_m": PARAMS.length, "width_m": PARAMS.width, "a_m": PARAMS.a, "b_m": PARAMS.b,
            "wheelbase_m": PARAMS.wheelbase, "steering_bounds_rad": [PARAMS.steering_min, PARAMS.steering_max],
            "steering_rate_bounds_rad_s": [PARAMS.steering_rate_min, PARAMS.steering_rate_max],
            "acceleration_bounds_mps2": [-PARAMS.acceleration_abs_limit, PARAMS.acceleration_abs_limit],
        },
        "simulation": {"model": "KS", "integrator": "RK4", "dt_s": DT},
        "a2_braking": {
            "initial_speed_mps": initial_speed, "acceleration_mps2": -7.0,
            "analytical_stopping_time_s": analytic_time, "numerical_stopping_time_s": stop_time,
            "absolute_time_error_s": abs(analytic_time - stop_time),
            "analytical_stopping_distance_m": analytic_distance, "numerical_stopping_distance_m": state.x,
            "absolute_distance_error_m": abs(analytic_distance - state.x),
        },
        "numerical_validation": {
            "symmetry_maximum_residual": symmetry,
            "rk4_timestep_halving_absolute_differences": convergence,
            "deterministic_replay_maximum_residual": replay_residual,
        },
        "commonroad_derivative_crosscheck": {
            "case_count": len(cases), "atol": 1e-10, "rtol": 1e-10,
            "component_absolute_errors": errors, "max_derivative_error": max_error,
            "passed": bool(np.allclose(max_error, 0.0, atol=1e-10, rtol=1e-10)),
        },
        "pytest_totals": pytest_totals(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT)
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
