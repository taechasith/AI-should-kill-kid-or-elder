"""Fail-closed validator for the frozen K2 KA-IRO KRISIS scene grammar."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "ka-iro-krisis" / "v2" / "scenarios"

def digest_without_hash(scene: dict) -> str:
    clone = {k: v for k, v in scene.items() if k != "scene_hash"}
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main() -> None:
    manifest = json.loads((BASE / "ka_iro_krisis_v2_scene_manifest.json").read_text(encoding="utf-8"))
    assert manifest["scene_count"] == 120 and manifest["family_count"] == 12
    assert len(manifest["scenes"]) == 120 and len(manifest["families"]) == 12
    identifiers = set()
    for entry in manifest["scenes"]:
        scene = json.loads((BASE / f"{entry['base_scene_id']}.json").read_text(encoding="utf-8"))
        assert scene["base_scene_id"] == entry["base_scene_id"] and scene["scenario_family"] == entry["scenario_family"]
        assert scene["scene_hash"] == entry["scene_hash"] == digest_without_hash(scene)
        assert scene["model_input_policy"] == {"contains_action_answer": False, "contains_outcome_label": False, "human_semantic_label": "UNSPECIFIED"}
        assert scene["applicable_actions"] == ["A0", "A1", "A2", "A3", "A4", "A6"]
        assert scene["base_scene_id"] not in identifiers; identifiers.add(scene["base_scene_id"])
        # A conservative axis-aligned initial-overlap check; exact footprints are checked in K3.
        for actor in scene["actors"]:
            if actor["motion"] == "static":
                dx, dy = abs(actor["x_m"]), abs(actor["y_m"])
                assert dx > (4.3 + actor["length_m"]) / 2 or dy > (1.8 + actor["width_m"]) / 2
    print(json.dumps({"status": "passed", "scene_count": len(identifiers), "family_count": len(manifest["families"])}))

if __name__ == "__main__":
    main()
