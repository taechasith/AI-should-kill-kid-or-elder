import json
from pathlib import Path
import scripts.run_phase7_literature_v2 as runner
from datetime import datetime, timezone

def test_quota_classification_and_reset_evidence():
    assert runner.classify_429('QuotaId GenerateRequestsPerMinutePerProjectPerModel-FreeTier', {}) == 'FREE_MINUTE_REQUEST_LIMIT'
    assert runner.classify_429('input tokens per minute', {}) == 'FREE_MINUTE_TOKEN_LIMIT'
    assert runner.delay_seconds('try again in 24.5s', {}) == 24.5
    assert runner.delay_seconds('', {'retry-after': '30'}) == 30

def test_historical_429_is_not_terminal(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    p=tmp_path/'attempts'/'r.json'; p.parent.mkdir(parents=True); p.write_text(json.dumps({'http_status':429,'status':'failed'}))
    assert not runner.terminal('r')

def test_completed_http_200_is_terminal(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    p=tmp_path/'attempts'/'r'/'attempt_0001.json'; p.parent.mkdir(parents=True); p.write_text(json.dumps({'http_status':200,'status':'completed'}))
    assert runner.terminal('r')

def test_attempts_are_numbered_and_append_only(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    row={'run_id':'r','provider':'Groq','model_id':'qwen/qwen3.8-27b'}
    a=runner.persist(row,429,'input tokens per minute',{'retry-after':'2'})
    b=runner.persist(row,429,'input tokens per minute',{'retry-after':'2'})
    assert (a['attempt_number'],b['attempt_number']) == (1,2)
    assert len(list((tmp_path/'attempts'/'r').glob('*.json'))) == 2

def test_daily_pause_is_reconstructed_from_immutable_attempt(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    row={'run_id':'r','provider':'Google Gemini API','model_id':'gemini-3.5-flash'}
    raw='QuotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier'
    record=runner.persist(row,429,raw,{})
    assert record['quota_classification']=='FREE_DAILY_REQUEST_LIMIT'
    assert runner.daily_paused(('gemini','gemini-3.5-flash'),datetime.now(timezone.utc))
    assert not runner.daily_paused(('gemini','gemini-3.5-flash-lite'),datetime.now(timezone.utc))
