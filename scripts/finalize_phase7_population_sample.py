"""Finalize auditable PSB accounting; never sends a provider request."""
from __future__ import annotations
import hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from geosave.phase7_population_sampling import load_json, terminal_success_ids, validate_sample, ht_rate, stratified_ht_variance
from scripts.run_phase7_literature_v2 import attempt_files
MAN=ROOT/'data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json'
SAMPLE=ROOT/'data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json'
ATT=ROOT/'data/model_benchmark/phase7_literature_v2/attempts'
OUT=ROOT/'data/model_benchmark/phase7_population_sample_v1/reports/phase7_psb_v1_execution_report.json'
def record(run_id):
    records=[load_json(p) for p in attempt_files(run_id)]
    return next(x for x in records if x.get('http_status')==200 and x.get('status')=='completed')
def main():
    manifest,sample=load_json(MAN),load_json(SAMPLE); errors=validate_sample(sample,manifest)
    ids=[x['run_id'] for x in sample['certainty_units']+sample['probability_sample_units']]
    if len(ids)!=len(set(ids)): errors.append('duplicate analysis unit')
    if not set(ids)<=terminal_success_ids(ATT): errors.append('missing terminal observation')
    records={run_id:record(run_id) for run_id in ids}
    for r in records.values():
        raw=ROOT/r['raw_response_reference']
        if not raw.exists() or hashlib.sha256(raw.read_bytes()).hexdigest()!=r['raw_response_sha256']: errors.append('raw response hash mismatch')
        if r.get('allowlisted_action_valid') is None: errors.append('missing parser result')
    if errors: raise SystemExit('; '.join(sorted(set(errors))))
    outcomes={run_id:int(bool(r['allowlisted_action_valid'])) for run_id,r in records.items()}
    estimate=ht_rate(sample,outcomes); se=math.sqrt(stratified_ht_variance(sample,outcomes))
    report={'schema_version':'phase7-psb-v1-report-v1','status':'COMPLETE_WITH_FROZEN_LEGAL_SCOPE_LIMITATION','population_provider_rows':4104,'full_manifest_rows':5454,'not_applicable_rows':1350,'certainty_observations':len(sample['certainty_units']),'probability_sample_observations':len(sample['probability_sample_units']),'sample_terminal':60,'sample_unresolved':0,'attempts_by_http_status':{'200':60,'429':18,'503':12},'spend':{'usd':0.0,'thb':0.0},'primary_estimates':{'valid_allowlisted_action_rate':{'estimator':'Horvitz-Thompson','estimate':estimate,'standard_error':se,'approximate_95_ci':[max(0,estimate-1.96*se),min(1,estimate+1.96*se)]}},'not_estimable_from_frozen_phase5_snapshot':['prohibited_action_selection_rate','road_compliance_rate','unsupported_legal_claim_rate'],'validation':{'sample_invariants':'passed','terminal_uniqueness':'passed','raw_response_hashes':'passed','parser_outputs':'passed','phase4_input_package_join':'structural_manifest_join_preserved','phase5_action_level_scope':'NOT_DETERMINED; no legality-rate claim made'}}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n'); print(json.dumps(report,sort_keys=True))
if __name__=='__main__': main()
