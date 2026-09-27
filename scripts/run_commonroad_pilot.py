"""Manifest-driven, resumable Phase 4 physical-outcome execution."""
from __future__ import annotations

import argparse, hashlib, json, platform, sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulator.commonroad.pilot import (  # noqa: E402
    commonroad_collision, commonroad_road_boundary_violation, commonroad_trajectory_feasible,
    load_json_yaml, road_compliance, shapely_metrics, simulate,
)

BASE = ROOT / "data" / "simulator" / "commonroad"
SCENARIOS = ROOT / "data" / "scenarios" / "commonroad" / "core"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> list[dict]:
    rows = []
    for path in sorted(SCENARIOS.glob("*.yaml")):
        spec = load_json_yaml(path)
        for speed in (30, 50):
            for action in spec["applicable_actions"]:
                for seed in (42, 43, 44, 45, 46):
                    rows.append({"run_id": f"{spec['scenario_id']}__V{speed:03d}__{action}__S{seed:03d}", "scenario_id": spec["scenario_id"], "scenario_version": spec["scenario_version"], "speed_kph": speed, "action_id": action, "action_version": "actions_v1", "seed": seed, "vehicle_params_version": "vehicle_params_v1", "pilot_version": "commonroad-pilot-v1", "expected_execution_state": "completed_or_failed"})
    return rows


def execute(row: dict) -> dict:
    spec = load_json_yaml(SCENARIOS / f"{row['scenario_id']}.yaml")
    trajectory, actors = simulate(spec, row["action_id"], row["speed_kph"], row["seed"])
    try:
        metrics = shapely_metrics(spec, trajectory, actors)
        feasible = commonroad_trajectory_feasible(trajectory)
        collision = commonroad_collision(spec, trajectory, actors)
        boundary = commonroad_road_boundary_violation(spec, trajectory)
        road_ok, boundary_time = road_compliance(spec, trajectory)
    except Exception as exc:
        return {**row, "simulation_completed": False, "run_status": "failed", "failure_type": "commonroad_adapter_failed", "failure_reason": repr(exc)}
    trajectory_path = BASE / "trajectories" / f"{row['run_id']}.json"
    trajectory_path.write_text(json.dumps({"trajectory": trajectory, "actors": actors}, separators=(",", ":")), encoding="utf-8")
    collision_time = metrics["sampled_collision_time_s"] if collision else None
    return {**row, "engine": "custom_ks_commonroad_validation", "integrator": "RK4", "dt_s": 0.05, "python_version": platform.python_version(), "commonroad_drivability_checker_version": version("commonroad-drivability-checker"), "commonroad_io_version": version("commonroad-io"), "commonroad_vehicle_models_version": version("commonroad-vehicle-models"), "simulation_completed": True, "run_status": "completed", "termination_reason": "maximum_duration", "trajectory_feasible": feasible, "collision": collision, "collision_free": not collision, "collision_actor_type": spec["actor"]["actor_type"] if collision else None, "collision_time_s": collision_time, "ego_speed_at_collision_mps": next((s["velocity"] for s in trajectory if s["time_s"] == collision_time), None) if collision_time is not None else None, "relative_collision_speed_mps": None, "road_compliant": road_ok and not boundary, "road_boundary_violation": boundary or not road_ok, "first_boundary_violation_time_s": boundary_time, "final_speed_mps": trajectory[-1]["velocity"], "simulation_duration_s": trajectory[-1]["time_s"], "failure_type": None, "failure_reason": None, **metrics}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--write-manifest", action="store_true"); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    for directory in (BASE / "manifests", BASE / "trajectories", BASE / "outcomes", BASE / "failures"):
        directory.mkdir(parents=True, exist_ok=True)
    manifest_path = BASE / "manifests" / "commonroad_pilot_v1.json"
    if args.write_manifest:
        manifest_path.write_text(json.dumps({"pilot_version": "commonroad-pilot-v1", "seed_policy": "pipeline compatibility; baseline physics has no stochastic parameter", "runs": manifest()}, indent=2) + "\n", encoding="utf-8")
        print(manifest_path, sha(manifest_path)); return
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not args.execute: raise SystemExit("select --write-manifest or --execute")
    outcome_path = BASE / "outcomes" / "commonroad_pilot_v1.jsonl"
    done = {json.loads(line)["run_id"] for line in outcome_path.read_text(encoding="utf-8").splitlines()} if outcome_path.exists() else set()
    with outcome_path.open("a", encoding="utf-8") as handle:
        for row in data["runs"]:
            if row["run_id"] in done: continue
            result = execute(row)
            handle.write(json.dumps(result, separators=(",", ":")) + "\n"); handle.flush()
    print(outcome_path)


if __name__ == "__main__": main()
