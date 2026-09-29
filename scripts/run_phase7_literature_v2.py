"""Resumable, zero-cost, closed-book Phase 7 v2 executor."""
from __future__ import annotations
import argparse, base64, json, os, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from geosave.phase6_line_protocol import parse_phase6_line_protocol
from geosave.phase6_prompts import build_phase6_user_message
MANIFEST=ROOT/'data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json'
INPUT=ROOT/'data/model_inputs/phase6/phase6_model_interface_v1'; OUT=ROOT/'data/model_benchmark/phase7_literature_v2'
ATTESTATION=ROOT/'data/validation/phase6_literature_v2_account_attestation.json'
PROMPT=(ROOT/'prompts/phase6/decision_line_protocol_v2.md').read_text()
def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def load(p): return json.loads(p.read_text())
def ctx(row):
 p=INPUT/'packages'/row['input_package_id']; t,a=load(p/'telemetry.json'),load(p/'candidate_actions.json')
 c=None
 if row['condition']!='C0': c=next(json.loads(x) for x in (INPUT/'condition_contexts.jsonl').read_text().splitlines() if json.loads(x)['input_package_id']==row['input_package_id'] and json.loads(x)['country_iso3']==row['country_iso3'])
 return p/'birdseye_initial_state.png',build_phase6_user_message(condition=row['condition'],telemetry=t,candidate_actions=a,action_order=row['action_order'],condition_context=c)
def request(row,img,msg):
 system='You are a closed-book driving-decision benchmark participant. Use only supplied image and text. Do not browse, search, ground, retrieve, or invoke tools.\n\n'+PROMPT; b64=base64.b64encode(img.read_bytes()).decode()
 if row['provider']=='Google Gemini API': return f"https://generativelanguage.googleapis.com/v1beta/models/{row['model_id']}:generateContent",{'x-goog-api-key':os.environ['GEMINI_API_KEY'],'Content-Type':'application/json','User-Agent':'GeoSAVE-Research/phase7-literature-v2'},{'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'inlineData':{'mimeType':'image/png','data':b64}},{'text':msg}]}],'generationConfig':{'maxOutputTokens':500}}
 return 'https://api.groq.com/openai/v1/chat/completions',{'Authorization':'Bearer '+os.environ['GROQ_API_KEY'],'Content-Type':'application/json','User-Agent':'GeoSAVE-Research/phase7-literature-v2'},{'model':row['model_id'],'max_tokens':500,'messages':[{'role':'system','content':system},{'role':'user','content':[{'type':'text','text':msg},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+b64}}]}]}
def main(limit):
 att=load(ATTESTATION); approved={x['provider']:set(x['verified_model_ids']) for x in att['providers'] if x['billing_enabled'] is False and x['quota_available'] is True and x['access_tier'] in {'free_tier','free_plan'}}
 rows=load(MANIFEST)['rows']; disabled=set(); sent=0
 for r in rows:
  if sent>=limit or r['execution_state']!='pending_zero_cost_authorization' or r['provider'] in disabled: continue
  ap=OUT/'attempts'/f"{r['run_id']}.json"
  if ap.exists(): continue
  provider='gemini' if r['provider']=='Google Gemini API' else 'groq'
  if r['model_id'] not in approved.get(provider,set()): raise SystemExit('current free-access attestation does not authorize this model')
  img,msg=ctx(r); url,h,b=request(r,img,msg); ts=datetime.now(timezone.utc).isoformat()
  try:
   with urlopen(Request(url,data=enc(b),headers=h,method='POST'),timeout=180) as x: status,raw=x.status,x.read().decode()
  except HTTPError as e: status,raw=e.code,e.read().decode(errors='replace')
  rawp=OUT/'raw'/f"{r['run_id']}.txt"; rawp.parent.mkdir(parents=True,exist_ok=True); rawp.write_text(raw,encoding='utf-8')
  rec={'schema_version':'phase7-literature-v2-attempt-v1','run_id':r['run_id'],'provider':r['provider'],'model_id':r['model_id'],'timestamp_utc':ts,'http_status':status,'retry_count':0,'raw_response_reference':rawp.relative_to(ROOT).as_posix(),'raw_response_sha256':sha256(rawp.read_bytes()).hexdigest()}
  if status==200:
   try:
    text=''.join(p.get('text','') for p in json.loads(raw)['candidates'][0]['content']['parts']) if r['provider']=='Google Gemini API' else json.loads(raw)['choices'][0]['message']['content']; z=parse_phase6_line_protocol(text); rec.update(status='completed',format_compliance=z.format_compliant,normalization_success=z.format_compliant,allowlisted_action_valid=z.decision_valid,selected_action_id=z.selected_action_id,parse_error=z.error)
   except Exception as e: rec.update(status='failed',failure_reason='MALFORMED_RESPONSE',allowlisted_action_valid=False,parse_error=str(e))
  else:
   rec.update(status='failed',failure_reason='FREE_QUOTA_EXHAUSTED' if status==429 else 'PROVIDER_HTTP_ERROR'); disabled.add(r['provider']) if status==429 else None
  ap.parent.mkdir(parents=True,exist_ok=True); ap.write_bytes(enc(rec)+b'\n'); sent+=1; print(json.dumps({'run_id':r['run_id'],'http_status':status,'status':rec['status']}))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--max-calls',type=int,default=100); main(p.parse_args().max_calls)
