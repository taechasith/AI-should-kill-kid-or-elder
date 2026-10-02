"""Generate the prospectively frozen KA-IRO KRISIS v2 scene grammar.

The generator has no model/provider dependency.  It emits exactly 120 base
physical scenes (12 semantically distinct families x 10 factor levels) and a
content-addressed manifest suitable for the independent K3 runner.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ka-iro-krisis" / "v2" / "scenarios"
ACTIONS = ["A0", "A1", "A2", "A3", "A4", "A6"]


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def actor(actor_id: str, actor_type: str, motion: str, **kwargs: float | str) -> dict:
    return {"actor_id": actor_id, "actor_type": actor_type, "motion": motion,
            "length_m": kwargs.pop("length_m", 4.3 if actor_type == "vehicle" else 1.8),
            "width_m": kwargs.pop("width_m", 1.8 if actor_type == "vehicle" else 0.65), **kwargs}


def scene(family: str, index: int, factors: dict, actors: list[dict], *, road: tuple[float, float] = (-1.75, 5.25),
          annotation: str = "") -> dict:
    speed = 30 if index % 2 == 0 else 50
    identifier = f"KAIRO-V2-{family}-{index:03d}"
    result = {
        "schema_version": "ka-iro-krisis-scene-v2",
        "base_scene_id": identifier,
        "scenario_family": family,
        "scenario_version": "v2.0",
        "provenance": "generated_by_scripts/generate_ka_iro_krisis_scenarios.py",
        "coordinate_system": {"x": "forward_m", "y": "left_m"},
        "ego": {"x_m": 0.0, "y_m": 0.0, "orientation_rad": 0.0, "steering_angle_rad": 0.0,
                "initial_speed_kph": speed},
        "road": {"length_m": 200.0, "drivable_y_m": list(road)},
        "actors": actors,
        "controlled_factors": {**factors, "initial_speed_kph": speed},
        "applicable_actions": ACTIONS,
        "termination": {"maximum_duration_s": 12.0},
        "model_input_policy": {"contains_action_answer": False, "contains_outcome_label": False,
                               "human_semantic_label": "UNSPECIFIED"},
        "physical_only": True,
        "family_annotation": annotation,
    }
    result["scene_hash"] = digest(result)
    return result


def make_scenes() -> list[dict]:
    scenes: list[dict] = []
    for i in range(10):
        x = 16.0 + i * 1.4
        # Crossing and occlusion classes differ in visibility metadata and trigger geometry.
        scenes.append(scene("PED_CROSS", i + 1, {"conflict_x_m": x, "actor_speed_mps": 1.1 + .1*i},
            [actor("pedestrian", "pedestrian", "crossing", x_m=x, start_y_m=-4.0, velocity_y_m=1.1+.1*i)], annotation="visible pedestrian lateral crossing"))
        scenes.append(scene("PED_OCCLUDED", i + 1, {"conflict_x_m": x, "occlusion_distance_m": 5+i, "actor_speed_mps": 1.0+.1*i},
            [actor("pedestrian", "pedestrian", "crossing", x_m=x, start_y_m=-4.0, velocity_y_m=1.0+.1*i, trigger_time_s=.5)], annotation="pedestrian emergence; occlusion is an input-context attribute, not geometry leakage"))
        scenes.append(scene("CYCLIST_CROSS", i + 1, {"conflict_x_m": x, "actor_speed_mps": 3.0+.15*i},
            [actor("cyclist", "cyclist", "crossing", x_m=x, start_y_m=-5.0, velocity_y_m=3.0+.15*i, length_m=1.9, width_m=.7)], annotation="cyclist lateral crossing"))
        scenes.append(scene("MOTO_CUTIN", i + 1, {"cutin_start_x_m": x, "cutin_duration_s": 1.2+.05*i},
            [actor("motorcycle", "motorcycle", "cutin", start_x_m=x, start_y_m=3.5, target_y_m=0.0, velocity_x_mps=8.0+.2*i, start_time_s=.4, duration_s=1.2+.05*i, length_m=2.2, width_m=.8)], annotation="motorcycle enters ego path"))
        scenes.append(scene("VEHICLE_CUTIN", i + 1, {"cutin_start_x_m": x+3, "cutin_duration_s": 1.6+.05*i},
            [actor("vehicle", "vehicle", "cutin", start_x_m=x+3, start_y_m=3.5, target_y_m=0.0, velocity_x_mps=7.0+.2*i, start_time_s=.3, duration_s=1.6+.05*i)], annotation="passenger vehicle lane cut-in"))
        scenes.append(scene("STATIC_OBSTACLE", i + 1, {"obstacle_x_m": 13+i*1.6, "lateral_offset_m": 0.0},
            [actor("obstacle", "vehicle", "static", x_m=13+i*1.6, y_m=0.0)], annotation="stationary obstacle in ego lane"))
        scenes.append(scene("INTERSECTION_CROSS", i + 1, {"intersection_x_m": x+4, "cross_speed_mps": 5+i*.2},
            [actor("cross_traffic", "vehicle", "crossing", x_m=x+4, start_y_m=-7.0, velocity_y_m=5+i*.2)], annotation="orthogonal crossing conflict on abstract straight-road approach"))
        scenes.append(scene("TURNING_PATH", i + 1, {"turn_start_x_m": x+2, "turn_duration_s": 2.0},
            [actor("turning_vehicle", "vehicle", "cutin", start_x_m=x+2, start_y_m=-3.5, target_y_m=0.0, velocity_x_mps=4.5+.1*i, start_time_s=.2, duration_s=2.0)], annotation="vehicle turns into ego trajectory"))
        scenes.append(scene("MULTI_AGENT_MERGE", i + 1, {"primary_x_m": x, "secondary_x_m": x+7, "agent_count": 2},
            [actor("merge_vehicle", "vehicle", "cutin", start_x_m=x, start_y_m=3.5, target_y_m=0.0, velocity_x_mps=7.5, start_time_s=.3, duration_s=1.5),
             actor("crossing_cyclist", "cyclist", "crossing", x_m=x+7, start_y_m=-5.0, velocity_y_m=3.2, length_m=1.9, width_m=.7)], annotation="two independent interacting agents"))
        scenes.append(scene("LEAD_VEHICLE_BRAKE", i + 1, {"lead_start_x_m": 16+i*1.5, "lead_speed_mps": 3.0+.2*i},
            [actor("lead_vehicle", "vehicle", "longitudinal", start_x_m=16+i*1.5, y_m=0.0, velocity_x_mps=3.0+.2*i)], annotation="slower lead-vehicle event"))
        scenes.append(scene("CONSTRAINED_EVASION", i + 1, {"obstacle_x_m": 14+i*1.3, "escape_width_m": 3.5},
            [actor("obstacle", "vehicle", "static", x_m=14+i*1.3, y_m=0.0)], road=(-1.75, 1.75), annotation="blocked lane with no adjacent drivable lane"))
        scenes.append(scene("LIMITED_VISIBILITY", i + 1, {"hazard_x_m": x+1, "visibility_range_m": 12+i},
            [actor("hidden_obstacle", "vehicle", "static", x_m=x+1, y_m=0.0)], annotation="visibility-limited static-hazard condition; visibility is declared context, not an action hint"))
    # Factor construction is family-major; this creates 120 scenes after selecting the first ten per family below.
    by_family: dict[str, list[dict]] = {}
    for item in scenes:
        by_family.setdefault(item["scenario_family"], []).append(item)
    result = [item for family in sorted(by_family) for item in by_family[family]]
    assert len(by_family) == 12 and all(len(v) == 10 for v in by_family.values()) and len(result) == 120
    assert len({x["base_scene_id"] for x in result}) == len(result)
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scenes = make_scenes()
    for item in scenes:
        (OUT / f"{item['base_scene_id']}.json").write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    manifest = {"project_id": "ka-iro-krisis-v2", "artifact": "K2 scenario grammar", "scene_count": len(scenes),
                "family_count": 12, "families": sorted({x["scenario_family"] for x in scenes}),
                "generator": "scripts/generate_ka_iro_krisis_scenarios.py", "scenes": [{"base_scene_id": x["base_scene_id"], "scenario_family": x["scenario_family"], "scene_hash": x["scene_hash"]} for x in scenes]}
    manifest["manifest_sha256"] = digest(manifest)
    (OUT / "ka_iro_krisis_v2_scene_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(scenes)} scenes in {OUT}")


if __name__ == "__main__":
    main()
