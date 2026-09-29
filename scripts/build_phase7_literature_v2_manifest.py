"""Build the Phase 7 v2 manifest without sending provider requests."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/model_benchmark/phase6_free_v1/manifests/phase6_free_v1_preflight_manifest.json'
OUT=ROOT/'data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json'
MODELS={'M1':('gemini-3.5-flash','Google Gemini API'),'M2':('gemini-3.5-flash-lite','Google Gemini API'),'M3':('qwen/qwen3.8-27b','Groq')}
def main():
 s=json.loads(SOURCE.read_text()); rows=[]
 for old in s['rows']:
  row=dict(old); model,provider=MODELS[row['model_slot']]; row.update(model_id=model,model_revision=model,provider=provider)
  row['run_id']=old['run_id'].replace('P6F-','P7V2-')
  row['raw_response_reference']=f"data/model_benchmark/phase7_literature_v2/raw/{row['run_id']}.txt"
  row['normalized_response_reference']=f"data/model_benchmark/phase7_literature_v2/normalized/{row['run_id']}.json"
  if row['execution_state']!='not_applicable':
   row['execution_state']='pending_zero_cost_authorization'; row['execution_reason']='Phase 7 provider execution requires separately authorized zero-cost quota.'
  rows.append(row)
 payload={'schema_version':'phase7-literature-v2-manifest-v1','experiment_id':'geosave-model-benchmark-v1','status':'FROZEN_PENDING_MAIN_EXECUTION_AUTHORIZATION','source_phase4_commit':'d52baab','law_snapshot':'phase5-legal-snapshot-v1','phase6_pilot_tag':'phase6-literature-v2-pilot-v1','prompt':'prompts/phase6/decision_line_protocol_v2.md','row_count':len(rows),'pending_provider_execution_count':sum(r['execution_state']=='pending_zero_cost_authorization' for r in rows),'not_applicable_row_count':sum(r['execution_state']=='not_applicable' for r in rows),'rows':rows}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n')
 print(f"Phase 7 v2 manifest: {payload['row_count']} rows; {payload['pending_provider_execution_count']} pending; {payload['not_applicable_row_count']} not_applicable")
if __name__=='__main__': main()
