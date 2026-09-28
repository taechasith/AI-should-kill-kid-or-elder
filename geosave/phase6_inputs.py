"""Deterministic, initial-state-only multimodal input packages for Phase 6."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import struct
from typing import Any, Iterable
import zlib

from .phase6_interface import ALLOWED_ACTIONS, canonical_json_bytes


ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = ROOT / "data" / "model_inputs" / "phase6" / "phase6_model_interface_v1"
SCENARIO_ROOT = ROOT / "data" / "scenarios" / "commonroad" / "core"
ACTION_CONFIG = ROOT / "configs" / "simulator" / "actions_v1.yaml"
LEGAL_DECISIONS = ROOT / "data" / "legal" / "phase5" / "legal_decisions.jsonl"
LEGAL_EVIDENCE = ROOT / "data" / "legal" / "phase5" / "primary_evidence.jsonl"
JURISDICTIONS = ROOT / "data" / "legal" / "phase5" / "jurisdiction_metadata.json"
CANONICAL_OUTCOMES = ROOT / "data" / "simulator" / "commonroad" / "outcomes" / "commonroad_pilot_v1.jsonl"

INPUT_SCHEMA_VERSION = "phase6-multimodal-input-v1"
PHASE4_CANONICAL_COMMIT = "d52baab"
LAW_SNAPSHOT = "phase5-legal-snapshot-v1"
SPEEDS_KPH = (30, 50)
FUTURE_OUTCOME_KEYS = {
    "collision",
    "collision_actor_type",
    "collision_time_s",
    "final_speed_mps",
    "minimum_distance_m",
    "minimum_ttc_s",
    "road_boundary_violation",
    "trajectory_feasible",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256(payload).hexdigest()


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _png_rgb(width: int, height: int, pixels: bytes) -> bytes:
    rows = b"".join(b"\x00" + pixels[row * width * 3 : (row + 1) * width * 3] for row in range(height))
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + _png_chunk(b"IDAT", zlib.compress(rows, level=9)) + _png_chunk(b"IEND", b"")


class _Canvas:
    def __init__(self, width: int = 512, height: int = 512) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray((72, 125, 73) * width * height)

    def pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 3
            self.pixels[index : index + 3] = bytes(color)

    def rectangle(self, left: int, top: int, right: int, bottom: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, top), min(self.height, bottom + 1)):
            for x in range(max(0, left), min(self.width, right + 1)):
                self.pixel(x, y, color)

    def circle(self, cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius**2:
                    self.pixel(x, y, color)

    def png(self) -> bytes:
        return _png_rgb(self.width, self.height, bytes(self.pixels))


def _world_to_pixel(x_m: float, y_m: float, *, width: int = 512, height: int = 512) -> tuple[int, int]:
    x_min, x_max = -5.0, 35.0
    y_min, y_max = -5.5, 8.0
    px = round((y_m - y_min) / (y_max - y_min) * (width - 1))
    py = round((x_max - x_m) / (x_max - x_min) * (height - 1))
    return int(px), int(py)


def _world_rectangle(canvas: _Canvas, *, x_m: float, y_m: float, length_m: float, width_m: float, color: tuple[int, int, int]) -> None:
    corners = [
        _world_to_pixel(x_m - length_m / 2, y_m - width_m / 2),
        _world_to_pixel(x_m + length_m / 2, y_m + width_m / 2),
    ]
    left, right = sorted(point[0] for point in corners)
    top, bottom = sorted(point[1] for point in corners)
    canvas.rectangle(left, top, right, bottom, color)


def render_birdseye_initial_state(scenario: dict[str, Any]) -> bytes:
    """Render only geometry and state at t=0; no trajectory/outcome is read."""
    canvas = _Canvas()
    road = scenario["road"]
    road_left, road_right = road["drivable_y_m"]
    left_px, _ = _world_to_pixel(0.0, road_left)
    right_px, _ = _world_to_pixel(0.0, road_right)
    canvas.rectangle(min(left_px, right_px), 0, max(left_px, right_px), canvas.height - 1, (50, 54, 58))
    for boundary_y in (road_left, road_right):
        px, _ = _world_to_pixel(0.0, boundary_y)
        canvas.rectangle(px - 2, 0, px + 2, canvas.height - 1, (238, 238, 238))
    lane_divider = road_left + road["lane_width_m"]
    px, _ = _world_to_pixel(0.0, lane_divider)
    for top in range(0, canvas.height, 44):
        canvas.rectangle(px - 1, top, px + 1, min(top + 22, canvas.height - 1), (220, 210, 70))

    ego = scenario["ego"]
    _world_rectangle(canvas, x_m=ego["x_m"], y_m=ego["y_m"], length_m=4.3, width_m=1.8, color=(43, 124, 220))
    actor = scenario["actor"]
    actor_type = actor["actor_type"]
    if actor_type == "generic_pedestrian":
        px, py = _world_to_pixel(actor["start_x_m"], actor["start_y_m"])
        canvas.circle(px, py, 10, (252, 186, 3))
    else:
        _world_rectangle(
            canvas,
            x_m=actor.get("start_x_m", actor.get("center_x_m")),
            y_m=actor.get("start_y_m", actor.get("center_y_m")),
            length_m=actor["length_m"],
            width_m=actor["width_m"],
            color=(209, 60, 60) if actor_type == "static_vehicle" else (238, 130, 48),
        )
    return canvas.png()


def _initial_actor_state(actor: dict[str, Any]) -> dict[str, Any]:
    return {
        "actor_type": actor["actor_type"],
        "position_m": {
            "x": actor.get("start_x_m", actor.get("center_x_m")),
            "y": actor.get("start_y_m", actor.get("center_y_m")),
        },
        "speed_mps": actor.get("speed_mps", 0.0),
        "length_m": actor["length_m"],
        "width_m": actor["width_m"],
    }


def _base_package_id(scenario_id: str, speed_kph: int) -> str:
    return f"{scenario_id}__V{speed_kph:03d}"


def _base_telemetry(scenario: dict[str, Any], speed_kph: int) -> dict[str, Any]:
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "time_s": 0.0,
        "units": "SI",
        "scenario_id": scenario["scenario_id"],
        "scenario_version": scenario["scenario_version"],
        "initial_speed_kph": speed_kph,
        "ego": {
            "position_m": {"x": scenario["ego"]["x_m"], "y": scenario["ego"]["y_m"]},
            "orientation_rad": scenario["ego"]["orientation_rad"],
            "steering_angle_rad": scenario["ego"]["steering_angle_rad"],
            "speed_mps": speed_kph / 3.6,
        },
        "actor": _initial_actor_state(scenario["actor"]),
        "road": {
            "lane_width_m": scenario["road"]["lane_width_m"],
            "drivable_y_m": scenario["road"]["drivable_y_m"],
            "length_m": scenario["road"]["length_m"],
        },
        "future_actor_motion": "not_supplied",
        "excluded_information": sorted(FUTURE_OUTCOME_KEYS),
    }


def _candidate_actions(action_config: dict[str, Any], scenario: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = action_config["profiles"]
    actions: list[dict[str, Any]] = []
    for action_id in scenario["applicable_actions"]:
        profile = profiles[action_id]
        actions.append(
            {
                "action_id": action_id,
                "name": profile["name"],
                "control": {
                    "acceleration_mps2": profile["acceleration_mps2"],
                    "steering_target_rad": profile["steering_target_rad"],
                },
            }
        )
    if tuple(sorted(action["action_id"] for action in actions)) != tuple(sorted(ALLOWED_ACTIONS)):
        raise ValueError(f"{scenario['scenario_id']} does not expose the frozen candidate action set")
    return actions


def _load_outcome_groups() -> dict[tuple[str, int, str], list[dict[str, Any]]]:
    groups: dict[tuple[str, int, str], list[dict[str, Any]]] = {}
    for record in _read_jsonl(CANONICAL_OUTCOMES):
        key = (record["scenario_id"], record["speed_kph"], record["action_id"])
        groups.setdefault(key, []).append(record)
    expected_group_count = 3 * len(SPEEDS_KPH) * len(ALLOWED_ACTIONS)
    if len(groups) != expected_group_count or any(len(records) != 5 for records in groups.values()):
        raise ValueError("canonical Phase 4 outcomes do not provide 5 deterministic replicates per action")
    return groups


def _c4_action_summary(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    values = list(records)
    representative = next((record for record in values if record["seed"] == 42), values[0])
    summary_keys = (
        "collision",
        "trajectory_feasible",
        "road_boundary_violation",
        "minimum_distance_m",
        "minimum_ttc_s",
        "final_speed_mps",
    )
    for key in summary_keys:
        if any(record[key] != representative[key] for record in values):
            raise ValueError(f"deterministic Phase 4 replicate disagreement for {representative['run_id']}:{key}")
    return {
        "canonical_representative_run_id": representative["run_id"],
        "canonical_replicate_count": len(values),
        **{key: representative[key] for key in summary_keys},
    }


def _build_condition_contexts(base_packages: list[dict[str, Any]], output_root: Path) -> dict[str, Any]:
    decisions = _read_jsonl(LEGAL_DECISIONS)
    evidence = {record["evidence_id"]: record for record in _read_jsonl(LEGAL_EVIDENCE)}
    jurisdiction_records = _read_json(JURISDICTIONS)["jurisdictions"]
    outcomes = _load_outcome_groups()
    by_context: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for decision in decisions:
        by_context.setdefault((decision["country_iso3"], decision["scenario_id"], decision["initial_speed_kph"]), []).append(decision)

    records: list[dict[str, Any]] = []
    for package in base_packages:
        scenario_id = package["scenario_id"]
        speed_kph = package["initial_speed_kph"]
        for jurisdiction in jurisdiction_records:
            country_iso3 = jurisdiction["country_iso3"]
            selected = sorted(by_context[(country_iso3, scenario_id, speed_kph)], key=lambda item: item["action_id"])
            if tuple(item["action_id"] for item in selected) != ALLOWED_ACTIONS:
                raise ValueError(f"missing Phase 5 decision(s) for {country_iso3} {package['input_package_id']}")
            evidence_ids = sorted({evidence_id for item in selected for evidence_id in item["considered_evidence_ids"]})
            locators = [
                {
                    "evidence_id": evidence_id,
                    "source_title": evidence[evidence_id]["source_title"],
                    "official_source_url": evidence[evidence_id]["official_source_url"],
                    "provision_identifier": evidence[evidence_id]["provision_identifier"],
                    "source_language": evidence[evidence_id]["source_language"],
                    "raw_excerpt_available": bool(evidence[evidence_id]["short_original_excerpt"]),
                    "working_translation_available": bool(evidence[evidence_id]["translation"]),
                }
                for evidence_id in evidence_ids
            ]
            raw_evidence_available = any(locator["raw_excerpt_available"] or locator["working_translation_available"] for locator in locators)
            c4_actions = [
                {
                    "action_id": action_id,
                    "physical_candidate_consequence": _c4_action_summary(outcomes[(scenario_id, speed_kph, action_id)]),
                    "legal_status": next(item["status"] for item in selected if item["action_id"] == action_id),
                    "evidence_sufficiency": next(item["evidence_sufficiency"] for item in selected if item["action_id"] == action_id),
                }
                for action_id in ALLOWED_ACTIONS
            ]
            records.append(
                {
                    "schema_version": INPUT_SCHEMA_VERSION,
                    "context_id": f"{package['input_package_id']}__{country_iso3}",
                    "input_package_id": package["input_package_id"],
                    "country_iso3": country_iso3,
                    "country_name": jurisdiction["country_name"],
                    "law_snapshot": LAW_SNAPSHOT,
                    "C1": {"jurisdiction_identity": country_iso3},
                    "C2": {
                        "structured_legal_decisions": [
                            {
                                "action_id": item["action_id"],
                                "status": item["status"],
                                "evidence_sufficiency": item["evidence_sufficiency"],
                                "reason_code": item["reason_code"],
                                "evidence_ids": item["considered_evidence_ids"],
                            }
                            for item in selected
                        ]
                    },
                    "C3": {
                        "eligible": raw_evidence_available,
                        "source_locators": locators,
                        "not_applicable_reason": None
                        if raw_evidence_available
                        else "The frozen Phase 5 snapshot retains no action-level raw or working-translation evidence text; source locators are not a substitute for raw legal evidence.",
                    },
                    "C4": {
                        "intentional_candidate_consequence_disclosure": True,
                        "phase4_canonical_commit": PHASE4_CANONICAL_COMMIT,
                        "geosave_support": c4_actions,
                    },
                }
            )
    context_path = output_root / "condition_contexts.jsonl"
    payload = b"".join(canonical_json_bytes(record) for record in records)
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_bytes(payload)
    return {"path": context_path.relative_to(ROOT).as_posix(), "sha256": sha256(payload).hexdigest(), "record_count": len(records)}


def build_phase6_input_packages(output_root: Path = INPUT_ROOT) -> dict[str, Any]:
    """Regenerate the six initial-state packages and their condition contexts."""
    action_config = _read_json(ACTION_CONFIG)
    packages: list[dict[str, Any]] = []
    for scenario_path in sorted(SCENARIO_ROOT.glob("*.yaml")):
        scenario = _read_json(scenario_path)
        for speed_kph in SPEEDS_KPH:
            package_id = _base_package_id(scenario["scenario_id"], speed_kph)
            package_dir = output_root / "packages" / package_id
            image_path = package_dir / "birdseye_initial_state.png"
            telemetry_path = package_dir / "telemetry.json"
            actions_path = package_dir / "candidate_actions.json"
            metadata_path = package_dir / "metadata.json"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(render_birdseye_initial_state(scenario))
            _write_json(telemetry_path, _base_telemetry(scenario, speed_kph))
            _write_json(actions_path, {"action_version": action_config["action_version"], "actions": _candidate_actions(action_config, scenario)})
            metadata = {
                "schema_version": INPUT_SCHEMA_VERSION,
                "input_package_id": package_id,
                "scenario_id": scenario["scenario_id"],
                "scenario_version": scenario["scenario_version"],
                "initial_speed_kph": speed_kph,
                "image_view": "birdseye_initial_decision_state",
                "image_dimensions_px": [512, 512],
                "initial_state_only": True,
                "future_outcome_data_in_base_package": False,
                "excluded_information": sorted(FUTURE_OUTCOME_KEYS),
                "source_artifacts": {
                    "phase4_canonical_commit": PHASE4_CANONICAL_COMMIT,
                    "scenario_path": scenario_path.relative_to(ROOT).as_posix(),
                    "scenario_sha256": _hash_file(scenario_path),
                    "actions_path": ACTION_CONFIG.relative_to(ROOT).as_posix(),
                    "actions_sha256": _hash_file(ACTION_CONFIG),
                },
            }
            _write_json(metadata_path, metadata)
            packages.append(
                {
                    "input_package_id": package_id,
                    "scenario_id": scenario["scenario_id"],
                    "initial_speed_kph": speed_kph,
                    "files": {
                        "birdseye_image": {"path": image_path.relative_to(ROOT).as_posix(), "sha256": _hash_file(image_path)},
                        "telemetry": {"path": telemetry_path.relative_to(ROOT).as_posix(), "sha256": _hash_file(telemetry_path)},
                        "candidate_actions": {"path": actions_path.relative_to(ROOT).as_posix(), "sha256": _hash_file(actions_path)},
                        "metadata": {"path": metadata_path.relative_to(ROOT).as_posix(), "sha256": _hash_file(metadata_path)},
                    },
                }
            )
    if len(packages) != 6:
        raise ValueError(f"expected six Phase 6 base input packages, found {len(packages)}")
    contexts = _build_condition_contexts(packages, output_root)
    manifest = {
        "schema_version": INPUT_SCHEMA_VERSION,
        "input_package_version": "phase6-model-interface-v1",
        "phase4_canonical_commit": PHASE4_CANONICAL_COMMIT,
        "law_snapshot": LAW_SNAPSHOT,
        "package_count": len(packages),
        "packages": packages,
        "condition_contexts": contexts,
        "base_package_information_boundary": {
            "initial_state_only": True,
            "future_action_outcomes_excluded": True,
            "C4_intentionally_discloses_candidate_consequences": True,
        },
    }
    manifest_path = output_root / "input_manifest.json"
    _write_json(manifest_path, manifest)
    return manifest
