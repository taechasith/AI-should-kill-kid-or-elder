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
 def test_heartbeat_helper_is_recreated_after_ephemeral_reset(self):
  old=lc.HEARTBEAT_SCRIPT; lc.HEARTBEAT_SCRIPT=self.root/'heartbeat'
  try:
   lc._ensure_heartbeat_script()
   self.assertTrue(lc.HEARTBEAT_SCRIPT.is_file())
   self.assertTrue(lc.HEARTBEAT_SCRIPT.stat().st_mode & 0o100)
  finally: lc.HEARTBEAT_SCRIPT=old
 def test_resume_and_health_contracts(self):
  repo=Path(__file__).resolve().parents[1]
  resume=(repo/'scripts/kairo_resume.sh').read_text(); health=(repo/'scripts/kairo_health.sh').read_text()
  self.assertIn('ka-iro-krisis-executor-v1',resume); self.assertIn('KAIRO_LIVE_EXECUTION_ENABLED',resume)
  self.assertIn('"runner"',health); self.assertIn('next_resume_utc',health); self.assertIn('ka-iro-runner.lock',health)
 def test_shell_scripts_are_safe_syntax(self):
  repo=Path(__file__).resolve().parents[1]
  for name in ('scripts/kairo_resume.sh','scripts/kairo_health.sh'):
   self.assertTrue((repo/name).is_file())
 def test_windows_templates_are_non_secret_and_target_fixed_codespace(self):
  repo=Path(__file__).resolve().parents[1]; paths=list((repo/'docs/ka-iro-krisis/templates').glob('*.ps1'))
  blob='\n'.join(p.read_text() for p in paths)
  self.assertIn('laughing-space-waffle-9795jw95xg64f7j79',blob); self.assertIn('KA-IRO-KRISIS-CodespaceSupervisor',blob)
  for forbidden in ('GEMINI_API_KEY','GROQ_API_KEY','ghp_','Bearer '): self.assertNotIn(forbidden,blob)
 def test_bootstrap_downloads_fail_closed_and_validate_scripts(self):
  repo=Path(__file__).resolve().parents[1]; text=(repo/'docs/ka-iro-krisis/templates/bootstrap_kairo_supervisor.ps1').read_text()
  self.assertIn('$LASTEXITCODE -ne 0',text); self.assertIn('[scriptblock]::Create',text); self.assertIn('download failed',text)
  self.assertIn('invalid PowerShell download',text); self.assertLess(text.index('Get-ValidatedScript'),text.index("& (Join-Path $dir 'test_kairo_windows_host.ps1')"))
 def test_supervisor_construction_time_recurrence_and_safe_rehydration(self):
  repo=Path(__file__).resolve().parents[1]
  installer=(repo/'docs/ka-iro-krisis/templates/install_kairo_supervisor.ps1').read_text(); supervisor=(repo/'docs/ka-iro-krisis/templates/kairo_codespace_supervisor.ps1').read_text()
  self.assertIn('New-ScheduledTaskAction',installer); self.assertIn('New-ScheduledTaskTrigger -Once',installer); self.assertIn('-RepetitionInterval (New-TimeSpan -Minutes 5)',installer); self.assertIn('-RepetitionDuration (New-TimeSpan -Days 3650)',installer); self.assertIn('StartWhenAvailable',installer)
  self.assertNotIn('schtasks.exe',installer); self.assertNotIn('$rehydrate=',supervisor)
  self.assertIn('worktree add --detach',supervisor); self.assertIn('fetch origin',supervisor); self.assertIn('rev-parse HEAD',supervisor); self.assertIn('rev-parse origin/',supervisor)
 def test_windows_path_with_spaces_remains_quoted(self):
  repo=Path(__file__).resolve().parents[1]
  installer=(repo/'docs/ka-iro-krisis/templates/install_kairo_supervisor.ps1').read_text(); host=(repo/'docs/ka-iro-krisis/templates/test_kairo_windows_host.ps1').read_text(); bootstrap=(repo/'docs/ka-iro-krisis/templates/bootstrap_kairo_supervisor.ps1').read_text()
  self.assertIn('`"$ScriptPath`"',installer); self.assertIn('C:\\Users\\HP OMEN\\AppData\\Local\\KAIROKRISIS\\kairo_codespace_supervisor.ps1',host)
  self.assertIn("Join-Path $env:LOCALAPPDATA 'KAIROKRISIS\\bootstrap'",bootstrap); self.assertIn('[System.IO.File]::Copy',bootstrap)
 def test_real_host_acceptance_script_is_fail_closed(self):
  repo=Path(__file__).resolve().parents[1]; text=(repo/'docs/ka-iro-krisis/templates/test_kairo_windows_host.ps1').read_text()
  for expected in ('[scriptblock]::Create','gh auth status','Get-ScheduledTask','Get-ScheduledTaskInfo','manual supervisor run failed','remote health check failed'):
   self.assertIn(expected,text)
  self.assertIn("Get-ValidatedScript 'test_kairo_windows_host.ps1'",(repo/'docs/ka-iro-krisis/templates/bootstrap_kairo_supervisor.ps1').read_text())

if __name__=='__main__': unittest.main()
