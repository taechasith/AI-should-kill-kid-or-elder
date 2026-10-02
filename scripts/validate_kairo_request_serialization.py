"""Offline byte-exact reconstruction validator for amended K5/K6 requests."""
from __future__ import annotations
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'data/ka-iro-krisis/v2/request_serialization_v1'
sys.path.insert(0,str(ROOT))
from kairokrisis.serialization import serialized
def check(name,count):
 d=json.loads((BASE/f'{name}_execution_manifest.json').read_text()); assert len(d['rows'])==count
 for row in d['rows']:
  x=serialized(row,ROOT)
  for key in ('serializer_version','endpoint','nonsecret_headers','request_body_sha256','request_body_bytes','request_envelope_sha256'): assert row[key]==x[key]
  assert 'api_key' not in x['request_body'].decode('utf-8').lower()
 return d['rows']
def main():
 k5=check('k5',720); k6=check('k6',480)
 assert len({x['observation_id'] for x in k5})==720 and len({x['observation_id'] for x in k6})==480
 groups=defaultdict(list)
 for x in k6: groups[(x['pair_id'],x['model_id'],x['representation_condition'])].append(x)
 for values in groups.values():
  assert len(values)==2
  a,b=values; assert a['image_sha256']==b['image_sha256'] and a['deterministic_text_sha256']==b['deterministic_text_sha256'] and a['physical_state_sha256']==b['physical_state_sha256']
 print(json.dumps({'status':'passed','k5':len(k5),'k6':len(k6),'provider_generation_calls':0}))
if __name__=='__main__':main()
