"""Manifest-driven K3 executor for KA-IRO KRISIS v2.

It consumes only frozen K2 scenes and writes one append-only canonical outcome
per base_scene_id/action.  CommonRoad validator failures are explicit records,
never synthesized successful data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulator.commonroad.ka_iro_krisis_v2 import commonroad_collision, commonroad_trajectory_feasible, metrics, simulate  # noqa: E402

SCENES = ROOT / "data" / "ka-iro-krisis" / "v2" / "scenarios"
BASE = ROOT / "data" / "ka-iro-krisis" / "v2" / "physical"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows() -> list[dict]:
    manifest = load(SCENES / "ka_iro_krisis_v2_scene_manifest.json")
    return [{"outcome_id": f"{entry['base_scene_id']}__{action}", "base_scene_id": entry["base_scene_id"],
             "scenario_family": entry["scenario_family"], "scene_hash": entry["scene_hash"], "action_id": action,
             "expected_execution_state": "completed_or_failed"}
            for entry in manifest["scenes"] for action in ("A0", "A1", "A2", "A3", "A4", "A6")]


def execute(row: dict) -> dict:
    scene = load(SCENES / f"{row['base_scene_id']}.json")
    try:
        trajectory, actors = simulate(scene, row["action_id"])
        if not trajectory:
            return {**row, "run_status": "not_applicable", "simulation_completed": False, "failure_type": None,
                    "failure_reason": "action_not_applicable"}
        calculated = metrics(scene, trajectory, actors)
        cr_collision = commonroad_collision(trajectory, actors)
        feasible = commonroad_trajectory_feasible(trajectory)
        if cr_collision != calculated["sampled_collision"]:
            return {**row, "run_status": "failed", "simulation_completed": False, "failure_type": "collision_validator_disagreement",
                    "failure_reason": f"sampled={calculated['sampled_collision']}; commonroad={cr_collision}"}
    except Exception as exc:
        return {**row, "run_status": "failed", "simulation_completed": False, "failure_type": "commonroad_adapter_failed", "failure_reason": repr(exc)}
    trajectory_path = BASE / "trajectories" / f"{row['outcome_id']}.json"
    trajectory_path.write_text(json.dumps({"base_scene_id": row["base_scene_id"], "action_id": row["action_id"],
                                           "trajectory": trajectory, "actor_samples": actors}, separators=(",", ":")), encoding="utf-8")
    return {**row, "engine": "custom_ks_commonroad_validation", "integrator": "RK4", "dt_s": 0.05,
            "python_version": platform.python_version(), "commonroad_drivability_checker_version": version("commonroad-drivability-checker"),
            "commonroad_io_version": version("commonroad-io"), "commonroad_vehicle_models_version": version("commonroad-vehicle-models"),
            "run_status": "completed", "simulation_completed": True, "trajectory_path": trajectory_path.relative_to(ROOT).as_posix(),
            "trajectory_sha256": sha(trajectory_path), "trajectory_feasible": feasible, "collision": cr_collision,
            "collision_free": not cr_collision, "physical_feasible": feasible, "final_speed_mps": trajectory[-1]["velocity"],
            "simulation_duration_s": trajectory[-1]["time_s"], "failure_type": None, "failure_reason": None, **calculated}


def verify_determinism(all_rows: list[dict]) -> dict:
    subset = [all_rows[i] for i in (0, 119, 240, 359, 480, 599, 719)]
    checks = []
    for row in subset:
        scene = load(SCENES / f"{row['base_scene_id']}.json")
        digests = []
        for _ in range(3):
            trajectory, actors = simulate(scene, row["action_id"])
            digests.append(hashlib.sha256(json.dumps({"trajectory": trajectory, "actors": actors}, separators=(",", ":")).encode()).hexdigest())
        checks.append({"outcome_id": row["outcome_id"], "replay_hashes": digests, "passed": len(set(digests)) == 1})
    return {"subset_size": len(checks), "checks": checks, "passed": all(x["passed"] for x in checks)}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--write-manifest", action="store_true"); ap.add_argument("--execute", action="store_true"); ap.add_argument("--verify-determinism", action="store_true")
    args = ap.parse_args(); BASE.mkdir(parents=True, exist_ok=True); (BASE / "trajectories").mkdir(exist_ok=True)
    physical_manifest = BASE / "ka_iro_krisis_physical_v2_manifest.json"
    all_rows = rows()
    if args.write_manifest:
        document = {"project_id": "ka-iro-krisis-v2", "benchmark_version": "ka-iro-krisis-physical-v2", "scene_manifest_sha256": sha(SCENES / "ka_iro_krisis_v2_scene_manifest.json"), "planned_outcome_count": len(all_rows), "runs": all_rows}
        physical_manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8"); print(physical_manifest, sha(physical_manifest)); return
    if args.verify_determinism:
        report = verify_determinism(all_rows); path = BASE / "determinism_report.json"; path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8"); print(path, report["passed"]); return
    if not args.execute:
        raise SystemExit("select --write-manifest, --execute, or --verify-determinism")
    manifest = load(physical_manifest)
    output = BASE / "ka_iro_krisis_physical_v2_outcomes.jsonl"
    done = set()
    if output.exists():
        for line in output.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            if item["outcome_id"] in done: raise RuntimeError("duplicate canonical outcome ID; fail closed")
            done.add(item["outcome_id"])
    with output.open("a", encoding="utf-8") as handle:
        for row in manifest["runs"]:
            if row["outcome_id"] not in done:
                handle.write(json.dumps(execute(row), separators=(",", ":")) + "\n"); handle.flush()
    print(output, len(manifest["runs"]))


if __name__ == "__main__":
    main()
