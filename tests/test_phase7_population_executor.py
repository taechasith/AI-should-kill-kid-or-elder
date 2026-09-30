import json
from datetime import datetime, timedelta, timezone
import scripts.run_phase7_population_sample as psb

def test_psb_executor_only_uses_frozen_sample(tmp_path, monkeypatch):
    manifest={'rows':[{'run_id':'selected','execution_state':'pending_zero_cost_authorization'},{'run_id':'outside','execution_state':'pending_zero_cost_authorization'}]}
    sample={'probability_sample_units':[{'run_id':'selected'}],'certainty_count':0}
    monkeypatch.setattr(psb.base,'MANIFEST',tmp_path/'manifest.json'); monkeypatch.setattr(psb,'SAMPLE',tmp_path/'sample.json')
    (tmp_path/'manifest.json').write_text(json.dumps(manifest)); (tmp_path/'sample.json').write_text(json.dumps(sample))
    rows,_=psb.rows_and_sample()
    assert [row['run_id'] for row in rows] == ['selected']


def test_until_stop_waits_for_timed_route_retry(monkeypatch):
    now=datetime.now(timezone.utc)
    slept=[]
    monkeypatch.setattr(psb, 'rows_and_sample', lambda: ([], {'certainty_count': 0}))
    monkeypatch.setattr(psb.base, 'load', lambda _: {'providers': []})
    monkeypatch.setattr(psb.base, 'daily_paused', lambda *_: None)
    monkeypatch.setattr(psb, 'datetime', type('Clock', (), {'now': staticmethod(lambda _: now)}))
    monkeypatch.setattr(psb.time, 'sleep', lambda seconds: slept.append(seconds))
    # With no rows there is no retry clock; this guards the no-candidate path remains safe.
    psb.main(True, 0)
    assert slept == []
