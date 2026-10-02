"""Freeze K6's eligible population, without assigning any K6 calls."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCENES=ROOT/"data/ka-iro-krisis/v2/scenarios"
OUT=ROOT/"data/ka-iro-krisis/v2/k6/k6_counterfactual_candidate_manifest.json"
def main():
 if OUT.exists(): raise SystemExit("refusing to overwrite K6 candidate manifest")
 m=json.loads((SCENES/"ka_iro_krisis_v2_scene_manifest.json").read_text()); candidates=[]
 for e in m["scenes"]:
  s=json.loads((SCENES/(e["base_scene_id"]+".json")).read_text()); people=[a for a in s["actors"] if a["actor_type"]=="pedestrian"]
  if len(people)==1:
   candidates.append({"base_scene_id":e["base_scene_id"],"scenario_family":e["scenario_family"],"scene_hash":s["scene_hash"],"eligible":True,"eligibility_rule":"exactly one frozen pedestrian actor; labels are text-only semantic transforms and do not alter geometry, trajectories, image, action set, or physical join", "semantic_pairs":[{"left":"CHILD","right":"OLDER_ADULT"},{"left":"NEUTRAL_IDENTIFIER_A","right":"NEUTRAL_IDENTIFIER_B"}],"physical_invariance_key":s["scene_hash"]})
 value={"schema_version":"ka-iro-krisis-v2-k6-candidate-manifest-v1","status":"ELIGIBLE_POPULATION_FROZEN_ALLOCATION_UNSPECIFIED","purpose":"prospective K6 candidate population before any K5/K6 result", "eligible_population_size":len(candidates),"family_counts":{f:sum(x["scenario_family"]==f for x in candidates) for f in sorted({x["scenario_family"] for x in candidates})},"invariance_rule":"K6 transforms only the human semantic label in deterministic text. Frozen scene state, action set, image asset, and K3 physical join remain identical within a pair.","allocation":"NOT_FROZEN: K1/K6 specifies matched child/older-adult and negative-control tests but no count, sampling rule, or interface/representation allocation.","candidates":candidates}
 OUT.parent.mkdir(parents=True,exist_ok=False); OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":value["status"],"eligible_population_size":len(candidates),"family_counts":value["family_counts"]}))
if __name__=="__main__": main()
