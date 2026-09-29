"""Resumable zero-cost Phase 7 executor; every HTTP request is append-only."""
from __future__ import annotations
import argparse, base64, json, os, re, sys, time
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from geosave.phase6_line_protocol import parse_phase6_line_protocol
from geosave.phase6_prompts import build_phase6_user_message
MANIFEST=ROOT/'data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json'; INPUT=ROOT/'data/model_inputs/phase6/phase6_model_interface_v1'; OUT=ROOT/'data/model_benchmark/phase7_literature_v2'; ATTESTATION=ROOT/'data/validation/phase6_literature_v2_account_attestation.json'; PROMPT=(ROOT/'prompts/phase6/decision_line_protocol_v2.md').read_text()
RATE={'retry-after','x-ratelimit-limit-requests','x-ratelimit-limit-tokens','x-ratelimit-remaining-requests','x-ratelimit-remaining-tokens','x-ratelimit-reset-requests','x-ratelimit-reset-tokens'}
def enc(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def load(p): return json.loads(p.read_text())
def route(r): return ('gemini' if r['provider']=='Google Gemini API' else 'groq',r['model_id'])
def attempt_files(run_id): return sorted(list((OUT/'attempts'/run_id).glob('attempt_*.json'))+list((OUT/'attempts').glob(run_id+'.json')))
def terminal(run_id): return any((x:=load(p)).get('http_status')==200 and x.get('status')=='completed' for p in attempt_files(run_id))
def classify_429(raw,headers):
 s=raw.lower()
 if 'perminute' in s and 'request' in s: return 'FREE_MINUTE_REQUEST_LIMIT'
 if 'tokens per minute' in s or 'input tokens per minute' in s: return 'FREE_MINUTE_TOKEN_LIMIT'
 if 'perday' in s or 'per day' in s or 'daily' in s: return 'FREE_DAILY_REQUEST_LIMIT'
 if any('day' in str(v).lower() for v in headers.values()): return 'FREE_DAILY_TOKEN_LIMIT'
 return 'TRANSIENT_RATE_LIMIT'
def delay_seconds(raw,headers):
 for v in (headers.get('retry-after'),headers.get('x-ratelimit-reset-tokens'),headers.get('x-ratelimit-reset-requests')):
  if v:
   m=re.search(r'([0-9.]+)',str(v));
   if m:return float(m.group(1))
 m=re.search(r'(?:retry in|try again in)\s*([0-9.]+)\s*s',raw,re.I)
 return float(m.group(1)) if m else 60.0
def ctx(r):
 p=INPUT/'packages'/r['input_package_id']; c=None
 if r['condition']!='C0': c=next(json.loads(x) for x in (INPUT/'condition_contexts.jsonl').read_text().splitlines() if json.loads(x)['input_package_id']==r['input_package_id'] and json.loads(x)['country_iso3']==r['country_iso3'])
 return p/'birdseye_initial_state.png',build_phase6_user_message(condition=r['condition'],telemetry=load(p/'telemetry.json'),candidate_actions=load(p/'candidate_actions.json'),action_order=r['action_order'],condition_context=c)
def prepared(r,img,msg):
 system='You are a closed-book driving-decision benchmark participant. Use only supplied image and text. Do not browse, search, ground, retrieve, or invoke tools.\n\n'+PROMPT; b=base64.b64encode(img.read_bytes()).decode()
 if r['provider']=='Google Gemini API': return f"https://generativelanguage.googleapis.com/v1beta/models/{r['model_id']}:generateContent",{'x-goog-api-key':os.environ['GEMINI_API_KEY'],'Content-Type':'application/json','User-Agent':'GeoSAVE-Research/phase7-literature-v2'},{'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'inlineData':{'mimeType':'image/png','data':b}},{'text':msg}]}],'generationConfig':{'maxOutputTokens':500}}
 return 'https://api.groq.com/openai/v1/chat/completions',{'Authorization':'Bearer '+os.environ['GROQ_API_KEY'],'Content-Type':'application/json','User-Agent':'GeoSAVE-Research/phase7-literature-v2'},{'model':r['model_id'],'max_tokens':500,'messages':[{'role':'system','content':system},{'role':'user','content':[{'type':'text','text':msg},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+b}}]}]}
def persist(r,status,raw,headers,request_sha256=None,image_sha256=None,input_sha256=None):
 history=attempt_files(r['run_id']); n=len(history)+1; d=OUT/'attempts'/r['run_id']; d.mkdir(parents=True,exist_ok=True); rawp=OUT/'raw'/r['run_id']/f'attempt_{n:04}.txt'; rawp.parent.mkdir(parents=True,exist_ok=True); rawp.write_text(raw,encoding='utf-8')
 try: raw_ref=rawp.relative_to(ROOT).as_posix()
 except ValueError: raw_ref=rawp.as_posix()
 usage={}
 try:
  body=json.loads(raw); usage=body.get('usageMetadata',{}) if r['provider']=='Google Gemini API' else body.get('usage',{})
 except (ValueError,TypeError): pass
 rec={'schema_version':'phase7-literature-v2-attempt-v2','run_id':r['run_id'],'attempt_number':n,'provider':r['provider'],'model_id':r['model_id'],'timestamp_utc':datetime.now(timezone.utc).isoformat(),'http_status':status,'retry_count':n-1,'raw_response_reference':raw_ref,'raw_response_sha256':sha256(rawp.read_bytes()).hexdigest(),'request_sha256':request_sha256,'image_sha256':image_sha256,'input_sha256':input_sha256,'prompt_sha256':sha256(PROMPT.encode()).hexdigest(),'usage_metadata':usage,'response_rate_limit_headers':headers,'quota_classification':classify_429(raw,headers) if status==429 else None,'retry_reset_seconds':delay_seconds(raw,headers) if status==429 else None}
 if status==200:
  try:
   t=''.join(x.get('text','') for x in json.loads(raw)['candidates'][0]['content']['parts']) if r['provider']=='Google Gemini API' else json.loads(raw)['choices'][0]['message']['content']; z=parse_phase6_line_protocol(t); rec.update(status='completed',allowlisted_action_valid=z.decision_valid,selected_action_id=z.selected_action_id,format_compliance=z.format_compliant,normalization_success=z.format_compliant,parse_error=z.error)
  except Exception as e: rec.update(status='failed',failure_reason='MALFORMED_RESPONSE',parse_error=str(e))
 else: rec.update(status='quota_deferred' if status==429 else 'failed',failure_reason='QUOTA_DEFERRED' if status==429 else 'PROVIDER_HTTP_ERROR')
 (d/f'attempt_{n:04}.json').write_bytes(enc(rec)+b'\n'); return rec
def main(until_stop=False,max_calls=1):
 approved={x['provider']:set(x['verified_model_ids']) for x in load(ATTESTATION)['providers'] if not x['billing_enabled'] and x['quota_available']}; rows=load(MANIFEST)['rows']; next_ok={}; calls=0
 while calls<max_calls:
  now=datetime.now(timezone.utc); candidate=next((r for r in rows if r['execution_state']=='pending_zero_cost_authorization' and not terminal(r['run_id']) and now>=next_ok.get(route(r),now)),None)
  if not candidate:
   future=[v for v in next_ok.values() if v>now]
   if until_stop and future:
    time.sleep(max(0,min((v-now).total_seconds() for v in future))); continue
   break
  if candidate['model_id'] not in approved.get(route(candidate)[0],set()): raise SystemExit('unverified free route')
  img,msg=ctx(candidate); url,h,b=prepared(candidate,img,msg)
  try:
   with urlopen(Request(url,data=enc(b),headers=h,method='POST'),timeout=180) as x: status,raw,heads=x.status,x.read().decode(),{k.lower():v for k,v in x.headers.items() if k.lower() in RATE}
  except HTTPError as e: status,raw,heads=e.code,e.read().decode(errors='replace'),{k.lower():v for k,v in e.headers.items() if k.lower() in RATE}
  rec=persist(candidate,status,raw,heads,sha256(enc(b)).hexdigest(),sha256(img.read_bytes()).hexdigest(),sha256(msg.encode()).hexdigest()); calls+=1
  if status==429:
   wait=rec['retry_reset_seconds']+3; next_ok[route(candidate)]=datetime.now(timezone.utc)+timedelta(seconds=wait)
   if not until_stop: break
   time.sleep(wait)
  elif status==503:
   next_ok[route(candidate)]=datetime.now(timezone.utc)+timedelta(seconds=60)
  elif route(candidate)[0]=='gemini': next_ok[route(candidate)]=datetime.now(timezone.utc)+timedelta(seconds=13)
  print(json.dumps({'run_id':candidate['run_id'],'attempt':rec['attempt_number'],'http_status':status,'status':rec['status']}))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--until-quota-stop',action='store_true'); p.add_argument('--run-until-daily-limit',action='store_true'); p.add_argument('--resume',action='store_true'); p.add_argument('--status',action='store_true'); p.add_argument('--max-calls',type=int,default=1); a=p.parse_args()
 if a.status:
  rows=load(MANIFEST)['rows']; attempts=[load(x) for x in (OUT/'attempts').glob('**/*.json')]; done={x['run_id'] for x in attempts if x.get('status')=='completed' and x.get('http_status')==200}; print(json.dumps({'manifest_rows':len(rows),'not_applicable':sum(r['execution_state']=='not_applicable' for r in rows),'provider_rows':sum(r['execution_state']=='pending_zero_cost_authorization' for r in rows),'terminal_http_200':len(done),'remaining':sum(r['execution_state']=='pending_zero_cost_authorization' and r['run_id'] not in done for r in rows),'attempts_by_http_status':{str(k):sum(x.get('http_status')==k for x in attempts) for k in sorted({x.get('http_status') for x in attempts})},'usd_spent':0.0,'thb_spent':0.0},sort_keys=True))
 else: main(a.until_quota_stop or a.run_until_daily_limit or a.resume, 4104 if (a.run_until_daily_limit or a.resume) else a.max_calls)
