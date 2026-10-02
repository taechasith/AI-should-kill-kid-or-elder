"""Materialize the prospective K5/K6 request-serialization amendment offline."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kairokrisis.serialization import serialized, sha256
OUT=ROOT/'data/ka-iro-krisis/v2/request_serialization_v1'
SOURCES=((ROOT/'data/ka-iro-krisis/v2/k5/k5_execution_manifest.json','k5'),(ROOT/'data/ka-iro-krisis/v2/k6/execution/k6_execution_manifest.json','k6'))
def main():
 if OUT.exists(): raise SystemExit('refusing to overwrite amendment')
 OUT.mkdir(parents=True)
 for source,name in SOURCES:
  doc=json.loads(source.read_text()); rows=[]
  for row in doc['rows']:
   row=dict(row)
   if name=='k6': row['observation_id']=row['k6_observation_id']
   value=serialized(row,ROOT); value.pop('request_body'); row['planning_object_sha256']=row['final_request_payload_sha256']; row.update(value); row['serialization_amendment_version']='v1'; rows.append(row)
  doc['schema_version']=f'ka-iro-krisis-v2-{name}-request-serialization-amendment-v1';doc['parent_manifest']=source.relative_to(ROOT).as_posix();doc['rows']=rows
  (OUT/f'{name}_execution_manifest.json').write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps({'k5':720,'k6':480,'generation_requests':0}))
if __name__=='__main__':main()
