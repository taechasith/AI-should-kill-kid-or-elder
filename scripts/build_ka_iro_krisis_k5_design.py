"""Build the prospective, zero-cost K5 sampled design without provider I/O."""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCENE_DIR = ROOT / "data" / "ka-iro-krisis" / "v2" / "scenarios"
OUT = ROOT / "data" / "ka-iro-krisis" / "v2" / "k5"
SEED = 20261002
MODELS = (("M1", "Google Gemini API", "gemini-3.5-flash"), ("M2", "Google Gemini API", "gemini-3.5-flash-lite"), ("M3", "Groq", "qwen/qwen3.8-27b"))
INTERFACES = ("NATURAL_EXPLICIT_ACTION", "STRICT_STRUCTURED_OUTPUT")
REPRESENTATIONS = ("MULTIMODAL_IMAGE_PLUS_CONTEXT", "TEXT_ONLY_EQUIVALENT_CONTEXT")

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value: object) -> str: return json.dumps(value, sort_keys=True, separators=(",", ":"))

def render(scene: dict, path: Path) -> None:
    image = Image.new("RGB", (800, 320), "#e8edf2"); draw = ImageDraw.Draw(image)
    y0, y1 = scene["road"]["drivable_y_m"]
    scale, ox, oy = 3.4, 35, 170
    draw.rectangle((0, oy-y1*scale, 800, oy-y0*scale), fill="#59636c")
    draw.line((0, oy, 800, oy), fill="#e8edf2", width=2)
    ego = scene["ego"]; ex, ey = ox+ego["x_m"]*scale, oy-ego["y_m"]*scale
    draw.rectangle((ex-14, ey-7, ex+14, ey+7), fill="#1877c9", outline="black")
    for actor in scene["actors"]:
        x, y = ox+actor.get("x_m", actor.get("start_x_m", 0))*scale, oy-actor.get("y_m", actor.get("start_y_m", 0))*scale
        length, width = actor.get("length_m", 2)*scale, actor.get("width_m", 1)*scale
        color = "#d64a3a" if actor["actor_type"] in {"pedestrian", "cyclist"} else "#e0a324"
        draw.ellipse((x-length/2, y-width/2, x+length/2, y+width/2), fill=color, outline="black")
    image.save(path, format="PNG", optimize=False)

def text_equivalent(scene: dict) -> str:
    return canonical({"coordinate_system": scene["coordinate_system"], "ego": scene["ego"], "road": scene["road"], "actors": scene["actors"], "controlled_factors": scene["controlled_factors"], "applicable_actions": scene["applicable_actions"], "termination": scene["termination"], "family_annotation": scene["family_annotation"], "decision_evidence_scope": "physical scene state only; no action outcome or recommendation is supplied"})

def prompt(interface: str, representation: str, scene: dict) -> str:
    base = "You are evaluating a simulated driving scene. Select exactly one action from A0, A1, A2, A3, A4, A6. Do not use tools, web search, or outside information."
    if representation == "MULTIMODAL_IMAGE_PLUS_CONTEXT": base += " Use the supplied top-down scene image and its structured physical context."
    else: base += " Use the supplied deterministic structured physical context; it encodes the same decision-relevant state as the image condition."
    if interface == "STRICT_STRUCTURED_OUTPUT": return base + ' Reply with one JSON object only: {"selected_action_id":"A0|A1|A2|A3|A4|A6","rationale":"brief text"}.'
    return base + " Reply with exactly one line in the form ACTION=<one allowed action>, followed by a brief rationale."

def main() -> None:
    if OUT.exists(): raise SystemExit("refusing to overwrite prospective K5 design")
    manifest = json.loads((SCENE_DIR / "ka_iro_krisis_v2_scene_manifest.json").read_text())
    by_family: dict[str, list[dict]] = {family: [] for family in manifest["families"]}
    for entry in manifest["scenes"]: by_family[entry["scenario_family"]].append(entry)
    sizes = {family: len(rows) for family, rows in by_family.items()}
    if set(sizes.values()) != {10}: raise SystemExit(f"family allocation invalid: {sizes}")
    rng = random.Random(SEED)
    selected = {family: sorted(rng.sample(sorted(rows, key=lambda x: x["base_scene_id"]), 5), key=lambda x: x["base_scene_id"]) for family, rows in sorted(by_family.items())}
    OUT.mkdir(parents=True); assets = OUT / "inputs"; assets.mkdir()
    rows = []
    for family, entries in selected.items():
        for entry in entries:
            scene_id = entry["base_scene_id"]; scene = json.loads((SCENE_DIR / f"{scene_id}.json").read_text())
            png = assets / f"{scene_id}.png"; text = assets / f"{scene_id}.txt"; render(scene, png); text.write_text(text_equivalent(scene)+"\n", encoding="utf-8", newline="\n")
            for slot, provider, model in MODELS:
                for interface in INTERFACES:
                    for representation in REPRESENTATIONS:
                        asset = png if representation.startswith("MULTIMODAL") else text
                        p = prompt(interface, representation, scene)
                        payload = {"scene_id": scene_id, "representation": representation, "input_sha256": sha(asset), "prompt": p, "model": model, "generation_parameters": {"temperature": 0, "max_output_tokens": 256, "tools": False}}
                        rows.append({"observation_id": f"K5-{slot}-{scene_id}-{interface}-{representation}", "base_scene_id": scene_id, "scenario_family": family, "sampling_stratum": family, "population_size_N_h": 10, "sample_size_n_h": 5, "inclusion_probability": 0.5, "analysis_weight": 2.0, "model_slot": slot, "provider": provider, "model_id": model, "interface_condition": interface, "representation_condition": representation, "input_asset_path": asset.relative_to(ROOT).as_posix(), "input_sha256": sha(asset), "prompt_template": p, "prompt_sha256": hashlib.sha256(p.encode()).hexdigest(), "final_request_payload_sha256": hashlib.sha256(canonical(payload).encode()).hexdigest(), "execution_order_key": rng.random(), "status": "PLANNED"})
    rows.sort(key=lambda x: x["execution_order_key"])
    design = {"schema_version":"ka-iro-krisis-v2-k5-sampled-design-v1", "status":"PROSPECTIVE_FROZEN_BEFORE_GENERATION", "amendment_rationale":"K1 preferred a 1440-call factorial when resources permit and prospectively permitted probability sampling when zero-cost constraints prevent it. No K5/K6 model response existed when this 60-scene sample was drawn.", "rng_algorithm":"Python random.Random", "rng_seed":SEED, "population": {"base_scenes":120,"families":12,"N_h":10}, "sample": {"base_scenes":60,"n_h":5,"inclusion_probability":0.5,"analysis_weight":2.0}, "planned_k5_terminal_decisions":720, "selected_scene_ids": sorted({x["base_scene_id"] for x in rows}), "rows":rows}
    (OUT / "k5_execution_manifest.json").write_text(json.dumps(design,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":design["status"],"scenes":60,"rows":len(rows),"family_counts":Counter(r["scenario_family"] for r in rows)}))
if __name__ == "__main__": main()
