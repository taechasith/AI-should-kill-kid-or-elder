"""Mocked/non-destructive operational lifecycle checks."""
from __future__ import annotations
import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import kairokrisis.lifecycle as lc

class LifecycleTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
  self.old=(lc.LOCK,lc.STATE,lc.SESSION)
  lc.LOCK=self.root/'lock'; lc.STATE=self.root/'state'; lc.SESSION=self.root/'session'
 def tearDown(self):
  lc.LOCK,lc.STATE,lc.SESSION=self.old; self.temp.cleanup()
 def test_singleton_and_stale_lock_recovery(self):
  self.assertTrue(lc.acquire()); self.assertFalse(lc.acquire()); lc.release(); self.assertTrue(lc.acquire()); lc.release()
  lc.LOCK.write_text('{"pid":99999999}'); self.assertTrue(lc.acquire()); lc.release()
 def test_state_persistence(self):
  lc.state('QUOTA_WAIT',next_resume_utc='2099-01-01T00:00:00Z'); self.assertEqual(lc.read_state()['state'],'QUOTA_WAIT')
 def test_rollover_threshold_mock(self):
  lc.SESSION.write_text(json.dumps({'started_utc':'2000-01-01T00:00:00+00:00'})); self.assertTrue(lc.should_rollover())
 def test_quota_wait_and_rollover_markers(self):
  oldq,oldr=lc.QUOTA_WAIT,lc.ROLLOVER; lc.QUOTA_WAIT=self.root/'quota'; lc.ROLLOVER=self.root/'rollover'
  try:
   lc.set_quota_wait('2099-01-01T00:00:00Z','Groq'); self.assertEqual(lc.read_state()['state'],'QUOTA_WAIT'); self.assertTrue(lc.QUOTA_WAIT.exists())
   lc.clear_quota_wait(); self.assertFalse(lc.QUOTA_WAIT.exists()); lc.set_rollover('K5'); self.assertEqual(lc.read_state()['state'],'ROLLOVER'); self.assertTrue(lc.ROLLOVER.exists())
  finally: lc.QUOTA_WAIT,lc.ROLLOVER=oldq,oldr
 def test_resume_and_health_contracts(self):
  repo=Path(__file__).resolve().parents[1]
  resume=(repo/'scripts/kairo_resume.sh').read_text(); health=(repo/'scripts/kairo_health.sh').read_text()
  self.assertIn('ka-iro-krisis-executor-v1',resume); self.assertIn('KAIRO_LIVE_EXECUTION_ENABLED',resume)
  self.assertIn('"runner"',health); self.assertIn('next_resume_utc',health)
 def test_shell_scripts_are_safe_syntax(self):
  repo=Path(__file__).resolve().parents[1]
  for name in ('scripts/kairo_resume.sh','scripts/kairo_health.sh'):
   self.assertTrue((repo/name).is_file())
 def test_windows_templates_are_non_secret_and_target_fixed_codespace(self):
  repo=Path(__file__).resolve().parents[1]; paths=list((repo/'docs/ka-iro-krisis/templates').glob('*.ps1'))
  blob='\n'.join(p.read_text() for p in paths)
  self.assertIn('laughing-space-waffle-9795jw95xg64f7j79',blob); self.assertIn('KA-IRO-KRISIS-CodespaceSupervisor',blob)
  for forbidden in ('GEMINI_API_KEY','GROQ_API_KEY','ghp_','Bearer '): self.assertNotIn(forbidden,blob)

if __name__=='__main__': unittest.main()
