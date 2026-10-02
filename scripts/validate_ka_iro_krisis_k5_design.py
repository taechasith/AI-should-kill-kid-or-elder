"""Offline integrity checks for the prospective K5 sampled design."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"data/ka-iro-krisis/v2/k5/k5_execution_manifest.json"
def main():
 d=json.loads(P.read_text()); r=d["rows"]; assert len(r)==720 and len({x["observation_id"] for x in r})==720
 scenes={x["base_scene_id"] for x in r}; assert len(scenes)==60
 assert Counter(x["scenario_family"] for x in r)==Counter({f:60 for f in {x["scenario_family"] for x in r}})
 assert Counter(x["base_scene_id"] for x in r)==Counter({s:12 for s in scenes})
 assert Counter(x["model_id"] for x in r)==Counter({"gemini-3.5-flash":240,"gemini-3.5-flash-lite":240,"qwen/qwen3.8-27b":240})
 assert Counter(x["interface_condition"] for x in r)==Counter({"NATURAL_EXPLICIT_ACTION":360,"STRICT_STRUCTURED_OUTPUT":360})
 assert Counter(x["representation_condition"] for x in r)==Counter({"MULTIMODAL_IMAGE_PLUS_CONTEXT":360,"TEXT_ONLY_EQUIVALENT_CONTEXT":360})
 for x in r:
  p=ROOT/x["input_asset_path"]; assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==x["input_sha256"] and x["status"]=="PLANNED"
 print(json.dumps({"status":"passed","scenes":60,"rows":720}))
if __name__=="__main__": main()
