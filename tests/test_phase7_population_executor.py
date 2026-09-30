import json
import scripts.run_phase7_population_sample as psb

def test_psb_executor_only_uses_frozen_sample(tmp_path, monkeypatch):
    manifest={'rows':[{'run_id':'selected','execution_state':'pending_zero_cost_authorization'},{'run_id':'outside','execution_state':'pending_zero_cost_authorization'}]}
    sample={'probability_sample_units':[{'run_id':'selected'}],'certainty_count':0}
    monkeypatch.setattr(psb.base,'MANIFEST',tmp_path/'manifest.json'); monkeypatch.setattr(psb,'SAMPLE',tmp_path/'sample.json')
    (tmp_path/'manifest.json').write_text(json.dumps(manifest)); (tmp_path/'sample.json').write_text(json.dumps(sample))
    rows,_=psb.rows_and_sample()
    assert [row['run_id'] for row in rows] == ['selected']
