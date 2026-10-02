"""Fail-closed offline validation of K6 matched-pair invariance."""
from __future__ import annotations
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/ka-iro-krisis/v2/k6/execution/k6_execution_manifest.json'
def main():
 d=json.loads(P.read_text()); r=d['rows']; assert len(r)==480 and len({x['k6_observation_id'] for x in r})==480
 assert Counter(x['model_id'] for x in r)==Counter({'gemini-3.5-flash':160,'gemini-3.5-flash-lite':160,'qwen/qwen3.8-27b':160}); assert Counter(x['representation_condition'] for x in r)==Counter({'MULTIMODAL_IMAGE_PLUS_CONTEXT':240,'TEXT_ONLY_EQUIVALENT_CONTEXT':240}); assert Counter(x['pair_type'] for x in r)==Counter({'SEMANTIC_COUNTERFACTUAL':240,'NEGATIVE_CONTROL':240}); assert Counter(x['scenario_family'] for x in r)==Counter({'PED_CROSS':240,'PED_OCCLUDED':240})
 groups=defaultdict(list)
 for x in r:
  assert x['interface_condition']=='STRICT_STRUCTURED_OUTPUT' and x['status']=='PLANNED'; groups[(x['pair_id'],x['model_id'],x['representation_condition'])].append(x)
  for key in ('image_asset_path','deterministic_text_asset_path','input_asset_path'):
   assert (ROOT/x[key]).is_file()
 for key,v in groups.items():
  assert len(v)==2 and {x['arm_id'] for x in v}=={'ARM1','ARM2'}; assert len({x['physical_state_sha256'] for x in v})==len({x['image_sha256'] for x in v})==len({x['deterministic_text_sha256'] for x in v})==1; assert v[0]['semantic_label_or_neutral_identifier'] != v[1]['semantic_label_or_neutral_identifier']
 print(json.dumps({'status':'passed','rows':480,'matched_units':120}))
if __name__=='__main__': main()
