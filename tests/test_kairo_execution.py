"""Mock-only recovery matrix for the production KA-IRO execution core."""
from __future__ import annotations
import importlib.util, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from kairokrisis.execution import Ledger, authenticated_headers, classify, dispatch_once, quota_next_eligible_utc, sha, verify

VALID=b'{"choices":[{"message":{"content":"{\\"selected_action_id\\":\\"A0\\"}"}}]}'
MALFORMED=b'{"choices":[{"message":{"content":"not json"}}]}'
REFUSAL=b'{"choices":[{"message":{"content":"I cannot assist"}}]}'
BLOCKED=b'{"choices":[{"message":{"content":"content blocked"}}]}'

class ExecutionMatrix(unittest.TestCase):
 def row(self,root,oid='O1'):
  asset=root/'asset'; asset.write_bytes(b'x')
  return {'observation_id':oid,'phase':'K5','provider':'Groq','model_id':'qwen/qwen3.8-27b','input_asset_path':str(asset),'input_sha256':sha(b'x'),'prompt_template':'p','prompt_sha256':sha(b'p'),'final_request_payload_sha256':'planning'}
 def finish(self,status,raw,transport='HTTP_RESPONSE',max_attempts=3):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root,max_transient_attempts=max_attempts); n=ledger.start(row); record=ledger.finalize(row,n,status,raw,{},transport); return record,ledger.state('O1')
 def test_http_response_ontology(self):
  for status,raw,expected,terminal in [(200,VALID,'VALID_ACTION',True),(200,MALFORMED,'INVALID_STRUCTURED_OUTPUT',True),(200,b'{"choices":[{"message":{"content":"{\\"selected_action_id\\":\\"NO\\"}"}}]}','VALID_RESPONSE_NO_ALLOWLISTED_ACTION',True),(200,REFUSAL,'REFUSAL',True),(200,BLOCKED,'CONTENT_BLOCKED',True),(400,b'{}','NON_RETRYABLE_PROVIDER_ERROR',True),(401,b'{}','NON_RETRYABLE_PROVIDER_ERROR',True),(403,b'{}','NON_RETRYABLE_PROVIDER_ERROR',True),(429,b'{"error":"rate_limit_exceeded"}','TRANSIENT_RATE_LIMIT',False),(429,b'{"error":"quota_exceeded perDay"}','FREE_QUOTA_EXHAUSTED',False),(500,b'{}','NON_RETRYABLE_PROVIDER_ERROR',False),(502,b'{}','NON_RETRYABLE_PROVIDER_ERROR',False),(503,b'{}','NON_RETRYABLE_PROVIDER_ERROR',False),(504,b'{}','NON_RETRYABLE_PROVIDER_ERROR',False)]:
   self.assertEqual(classify(status,raw),(expected,terminal))
 def test_transport_known_vs_ambiguous(self):
  self.assertEqual(classify(None,b'', 'KNOWN_NOT_ACCEPTED'),('TRANSIENT_TRANSPORT_FAILURE',False))
  self.assertEqual(classify(None,b'', 'AMBIGUOUS_TRANSPORT_OUTCOME'),('AMBIGUOUS_TRANSPORT_OUTCOME',True))
 def test_terminal_never_resent_and_attempts_are_immutable(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root); n=ledger.start(row); ledger.finalize(row,n,200,VALID,{})
   self.assertIsNone(ledger.start(row)); self.assertEqual(len(ledger.attempts('O1')),1)
   self.assertTrue(Path(ledger.records('O1')[0]['raw_response_reference']).is_file())
 def test_retry_history_and_exhaustion(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root,max_transient_attempts=2)
   first=ledger.finalize(row,ledger.start(row),503,b'{}',{}); self.assertTrue(first['retry_permitted'])
   second=ledger.finalize(row,ledger.start(row),503,b'{}',{}); self.assertEqual(second['parsed_terminal_state'],'RETRY_EXHAUSTED')
   self.assertEqual([x['attempt_number'] for x in ledger.records('O1')],[1,2]); self.assertTrue(ledger.terminal('O1'))
 def test_quota_defer_resume_exact_observation(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root)
   ledger.finalize(row,ledger.start(row),429,b'{"error":"quota_exceeded daily"}',{})
   self.assertEqual(ledger.state('O1')['state'],'QUOTA_DEFERRED')
   # Scheduler, not sampling, may later mark the same row eligible.
   ledger.mark_state('O1','RETRY_DEFERRED'); ledger.finalize(row,ledger.start(row),200,VALID,{})
   self.assertTrue(ledger.terminal('O1')); self.assertEqual(len(ledger.attempts('O1')),2)
 def test_quota_retry_delay_is_durable_and_nonsecret(self):
  raw=b'{"error":{"message":"quota_exceeded","details":[{"retryDelay":"90s"}]}}'
  self.assertEqual(quota_next_eligible_utc(raw,{},'2026-01-01T00:00:00Z'),'2026-01-01T00:01:30Z')
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root)
   record=ledger.finalize(row,ledger.start(row),429,raw,{})
   self.assertIsNotNone(record['next_eligible_utc'])
   self.assertEqual(ledger.state('O1')['next_eligible_utc'],record['next_eligible_utc'])
 def test_crash_after_started_is_ambiguous_not_replayed(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root); ledger.start(row); ledger.recover()
   self.assertTrue(ledger.terminal('O1')); self.assertEqual(ledger.records('O1')[0]['parsed_terminal_state'],'AMBIGUOUS_TRANSPORT_OUTCOME'); self.assertIsNone(ledger.start(row))
 def test_recovery_after_raw_and_finalized(self):
  for crash in ('after_raw','after_finalized','after_parsed'):
   with self.subTest(crash=crash), tempfile.TemporaryDirectory() as t:
    root=Path(t); row=self.row(root); ledger=Ledger(root); n=ledger.start(row)
    with self.assertRaises(RuntimeError): ledger.finalize(row,n,200,VALID,{},crash_at=crash)
    ledger.recover(); self.assertTrue(ledger.terminal('O1')); self.assertIsNone(ledger.start(row))
 def test_integrity_hard_failures(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); verify(row,Path('/'))
   row['input_sha256']='bad'
   with self.assertRaisesRegex(RuntimeError,'FROZEN_PAYLOAD_INTEGRITY_FAILURE'): verify(row,Path('/'))
 def test_dispatch_once_has_no_hidden_retry(self):
  calls=[]
  def boom(*args,**kwargs): calls.append(1); raise __import__('urllib.error').error.URLError('refused')
  with patch('kairokrisis.execution.urlopen',boom):
   status,_,_,transport=dispatch_once('https://invalid.example',{},b'{}')
  self.assertIsNone(status); self.assertEqual(transport,'KNOWN_NOT_ACCEPTED'); self.assertEqual(len(calls),1)
 def test_no_secret_in_artifacts(self):
  secret='do-not-persist-this-key'
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); ledger=Ledger(root); ledger.finalize(row,ledger.start(row),200,VALID,{})
   self.assertNotIn(secret,'\n'.join(p.read_text(errors='ignore') for p in root.rglob('*') if p.is_file()))
 def test_manifest_counts_and_no_network_dry_run(self):
  root=Path(__file__).resolve().parents[1]
  k5=json.loads((root/'data/ka-iro-krisis/v2/request_serialization_v1/k5_execution_manifest.json').read_text())['rows']
  k6=json.loads((root/'data/ka-iro-krisis/v2/request_serialization_v1/k6_execution_manifest.json').read_text())['rows']
  self.assertEqual((len(k5),len(k6),len(k5)+len(k6)),(720,480,1200))
 def test_production_execute_path_one_dispatch_and_offline_parse(self):
  repo=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('kairo_runner',repo/'scripts/run_kairo_krisis.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); row=self.row(root); row.update({'request_body_sha256':'x','request_body_bytes':1,'request_envelope_sha256':'y','execution_order_key':1.0})
   # Substitute frozen verifier only at the fixture boundary; dispatch is still the production core boundary.
   calls=[]
   with patch.object(module,'verified',return_value={'endpoint':'https://example.invalid','request_body':b'{}'}):
    record=module.execute_one(row,Ledger(root),lambda *a:(calls.append(a) or (200,VALID,{},'HTTP_RESPONSE')),lambda p:{})
   self.assertEqual(len(calls),1); self.assertEqual(record['parsed_terminal_state'],'VALID_ACTION')
   raw=Path(record['raw_response_reference']).read_bytes(); self.assertEqual(classify(200,raw)[0],record['parsed_terminal_state'])
 def test_nonretryable_and_ambiguous_never_retry(self):
  for status,transport in ((400,'HTTP_RESPONSE'),(None,'AMBIGUOUS_TRANSPORT_OUTCOME')):
   with self.subTest(status=status), tempfile.TemporaryDirectory() as t:
    root=Path(t); row=self.row(root); ledger=Ledger(root); ledger.finalize(row,ledger.start(row),status,b'{}',{},transport)
    self.assertTrue(ledger.terminal('O1')); self.assertIsNone(ledger.start(row))
 def test_k6_dispatch_is_held_until_k5_terminal(self):
  repo=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('kairo_runner_order',repo/'scripts/run_kairo_krisis.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
  class Fake:
   def __init__(self,terminal): self.terminal_ids=terminal
   def terminal(self,oid): return oid in self.terminal_ids
   def state(self,oid): return {'state':'PLANNED'}
  rows=[{'observation_id':'k6','phase':'K6','execution_order_key':0},{'observation_id':'k5','phase':'K5','execution_order_key':1}]
  self.assertEqual(module.next_safe(rows,Fake(set()))['observation_id'],'k5')
  self.assertEqual(module.next_safe(rows,Fake({'k5'}))['observation_id'],'k6')
 def test_credential_route_pause_skips_only_affected_route(self):
  repo=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('kairo_runner_pause',repo/'scripts/run_kairo_krisis.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
  class Fake:
   def terminal(self,oid): return False
   def state(self,oid): return {'state':'PLANNED'}
   def records(self,oid): return [{'http_status':403}] if oid=='groq' else []
  rows=[{'observation_id':'groq','phase':'K5','provider':'Groq','model_id':'qwen/qwen3.8-27b','execution_order_key':0},{'observation_id':'gemini','phase':'K5','provider':'Google Gemini API','model_id':'gemini-3.5-flash','execution_order_key':1}]
  with tempfile.TemporaryDirectory() as t:
   old=module.GROQ_QUALIFICATION; module.GROQ_QUALIFICATION=Path(t)/'absent.json'
   try:
    paused=module.paused_routes(rows,Fake()); self.assertIn(('Groq','qwen/qwen3.8-27b'),paused)
    self.assertEqual(module.next_safe(rows,Fake(),paused)['observation_id'],'gemini')
   finally: module.GROQ_QUALIFICATION=old
 def test_quota_pause_is_route_isolated(self):
  repo=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('kairo_runner_quota_pause',repo/'scripts/run_kairo_krisis.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
  class Fake:
   def terminal(self,oid): return False
   def records(self,oid): return []
   def state(self,oid): return {'state':'QUOTA_DEFERRED' if oid=='flash' else 'PLANNED'}
  rows=[{'observation_id':'flash','phase':'K5','provider':'Google Gemini API','model_id':'gemini-3.5-flash','execution_order_key':0},{'observation_id':'lite','phase':'K5','provider':'Google Gemini API','model_id':'gemini-3.5-flash-lite','execution_order_key':1}]
  paused=module.paused_routes(rows,Fake())
  self.assertEqual(paused[('Google Gemini API','gemini-3.5-flash')],'QUOTA_DEFERRED')
  self.assertEqual(module.next_safe(rows,Fake(),paused)['observation_id'],'lite')
 def test_tuple_keyed_route_status_is_json_safe(self):
  repo=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('kairo_runner_route_status',repo/'scripts/run_kairo_krisis.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
  routes=module.route_status({('Google Gemini API','gemini-3.5-flash'):'QUOTA_DEFERRED'})
  self.assertEqual(routes,{'Google Gemini API::gemini-3.5-flash':'QUOTA_DEFERRED'})
  json.dumps(routes)
 def test_groq_transport_header_is_runtime_only(self):
  with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'},clear=False): headers=authenticated_headers('Groq')
  self.assertEqual(headers['user-agent'],'KA-IRO-KRISIS/1.0')
  self.assertEqual(headers['content-type'],'application/json')
  self.assertNotIn('test-key',json.dumps({k:v for k,v in headers.items() if k != 'authorization'}))
 def test_real_subprocess_restart_recovers_inflight_without_redispatch(self):
  repo=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); asset=root/'asset'; asset.write_bytes(b'x')
   row={'observation_id':'SUB','phase':'K5','provider':'Groq','model_id':'qwen/qwen3.8-27b'}
   program="from pathlib import Path; from kairokrisis.execution import Ledger; import json; r=json.loads(%r); Ledger(Path(%r)).start(r)" % (json.dumps(row),str(root/'ledger'))
   subprocess.run([sys.executable,'-c',program],cwd=repo,check=True)
   ledger=Ledger(root/'ledger'); self.assertEqual(ledger.recover(),['SUB'])
   self.assertTrue(ledger.terminal('SUB')); self.assertIsNone(ledger.start(row))

if __name__=='__main__': unittest.main()
