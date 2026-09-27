from pathlib import Path

from simulator.commonroad.pilot import (
    DT, action_control, actor_state, commonroad_collision, commonroad_road_boundary_violation, load_json_yaml,
    road_compliance, shapely_metrics, simulate,
)
from simulator.commonroad.ks_model import KSState
from simulator.commonroad.vehicle_params import vehicle_params_v1


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "data" / "scenarios" / "commonroad" / "core"
P = vehicle_params_v1()


def scenario(name):
    return load_json_yaml(SCENARIOS / name)


def test_actions_are_bounded_and_mirrored():
    state = KSState(0, 0, 0, 8, 0)
    a0, a1, a2, left, right, a6 = [action_control(key, state) for key in ("A0", "A1", "A2", "A3", "A4", "A6")]
    assert (a0.steering_rate, a0.acceleration) == (0.0, 0.0)
    assert a1.acceleration == -3.0 and a2.acceleration == -7.0 and a6.acceleration == -4.0
    assert left.acceleration == right.acceleration and left.steering_rate == -right.steering_rate
    for control in (a0, a1, a2, left, right, a6):
        assert P.steering_rate_min <= control.steering_rate <= P.steering_rate_max
        assert -P.acceleration_abs_limit <= control.acceleration <= P.acceleration_abs_limit


def test_scenarios_are_deterministic_and_have_no_initial_overlap():
    for name in ("OBS-LANE-001.yaml", "PED-CROSS-001.yaml", "MOTO-CUTIN-001.yaml"):
        spec = scenario(name)
        first, actors = simulate(spec, "A2", 30, 42)
        second, _ = simulate(spec, "A2", 30, 42)
        assert first == second and first[0]["time_s"] == 0.0
        assert shapely_metrics(spec, first[:1], actors[:1])["minimum_distance_m"] > 0


def test_dynamic_actor_paths_are_continuous_and_road_compliance_is_detected():
    pedestrian = scenario("PED-CROSS-001.yaml")
    motorcycle = scenario("MOTO-CUTIN-001.yaml")
    assert actor_state(pedestrian, 0.0)["y"] < actor_state(pedestrian, DT)["y"]
    assert actor_state(motorcycle, 0.5)["y"] == motorcycle["actor"]["start_y_m"]
    assert actor_state(motorcycle, 2.0)["y"] == motorcycle["actor"]["target_y_m"]
    trajectory, _ = simulate(scenario("OBS-LANE-001.yaml"), "A2", 30, 42)
    assert road_compliance(scenario("OBS-LANE-001.yaml"), trajectory) == (True, None)
    assert not commonroad_road_boundary_violation(scenario("OBS-LANE-001.yaml"), trajectory)


def test_commonroad_collision_adapter_matches_known_static_collision():
    spec = scenario("OBS-LANE-001.yaml")
    trajectory, actors = simulate(spec, "A0", 30, 42)
    assert commonroad_collision(spec, trajectory, actors)
