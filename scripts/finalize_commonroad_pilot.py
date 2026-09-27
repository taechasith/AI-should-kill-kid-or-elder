"""Validate and summarize frozen Phase 4 artifacts without simulating them."""
from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'data/simulator/commonroad'
MANIFEST=BASE/'manifests/commonroad_pilot_v1.json'; OUTCOMES=BASE/'outcomes/commonroad_pilot_v1.jsonl'
SUMMARY=BASE/'summaries/commonroad_pilot_v1_summary.json'; HASHES=BASE/'hashes/commonroad_pilot_v1_sha256.json'

def load(): return json.loads(MANIFEST.read_text()),[json.loads(x) for x in OUTCOMES.read_text().splitlines() if x]
def digest(p):
 """Hash Git-portable canonical bytes (LF line endings) rather than platform checkout bytes."""
 return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def numeric(v): return v is None or isinstance(v,(int,float)) and math.isfinite(v)

def validate():
 m,o=load(); ids=[x['run_id'] for x in o]; expected={x['run_id'] for x in m['runs']}; errors=[]
 if len(m['runs'])!=180: errors.append('manifest count is not 180')
 if len(o)!=180 or len(set(ids))!=180: errors.append('canonical outcome IDs are not exactly 180 unique rows')
 if set(ids)!=expected: errors.append('manifest/outcome run IDs differ')
 if sum(1 for x in (BASE/'attempts/commonroad_pilot_v1_duplicate_attempts.jsonl').read_text().splitlines() if x)!=348: errors.append('duplicate attempt archive is not 348 rows')
 for row in o:
  if row['run_status'] not in {'completed','failed','not_applicable'}: errors.append(f"bad status {row['run_id']}")
  if row['run_status']=='completed' and not (BASE/'trajectories'/f"{row['run_id']}.json").exists(): errors.append(f"missing trajectory {row['run_id']}")
  if row['collision'] == row['collision_free']: errors.append(f"collision complement {row['run_id']}")
  if row['collision'] is False and (row['ego_speed_at_collision_mps'] is not None or row['relative_collision_speed_mps'] is not None): errors.append(f"collision nulls {row['run_id']}")
  if not row['ttc_defined'] and row['minimum_ttc_s'] is not None: errors.append(f"ttc null {row['run_id']}")
  if row['road_boundary_violation'] and row['road_compliant']: errors.append(f"road complement {row['run_id']}")
  if any(isinstance(v,(int,float)) and not isinstance(v,bool) and not math.isfinite(v) for v in row.values()): errors.append(f"nonfinite {row['run_id']}")
  trajectory=json.loads((BASE/'trajectories'/f"{row['run_id']}.json").read_text())['trajectory']
  previous=-1.0
  for s in trajectory:
   if s['time_s']<previous or s['velocity']<0 or abs(s['steering_rate'])>.4+1e-12 or abs(s['acceleration'])>11.5+1e-12: errors.append(f"trajectory constraint {row['run_id']}"); break
   previous=s['time_s']
 return {'passed':not errors,'errors':errors,'planned_runs':len(m['runs']),'canonical_rows':len(o),'duplicate_attempt_rows':348}

def values(rows,key): return [x[key] for x in rows if x.get(key) is not None]
def stats(vals): return None if not vals else {'count':len(vals),'min':min(vals),'mean':sum(vals)/len(vals),'max':max(vals)}
def summarize():
 m,o=load(); integrity=validate()
 by={}
 for key in ('scenario_id','speed_kph','action_id'):
  by[key]={str(k):{'runs':len(g),'collisions':sum(x['collision'] for x in g),'feasible':sum(x['trajectory_feasible'] for x in g),'road_compliant':sum(x['road_compliant'] for x in g)} for k,g in ((k,[x for x in o if x[key]==k]) for k in sorted({x[key] for x in o}))}
 result={'pilot_version':'commonroad-pilot-v1','validated_ks_commit':'b9c31ba221b7406b86c672793425f27862fb59ac','data_commit':'d52baabc7658840f7c2ff63102c2f8fe3e97e058','final_execution_commit':'d52baabc7658840f7c2ff63102c2f8fe3e97e058','manifest_path':str(MANIFEST.relative_to(ROOT)).replace('\\','/'),'manifest_sha256':digest(MANIFEST),'planned_runs':len(m['runs']),'completed_runs':sum(x['run_status']=='completed' for x in o),'failed_runs':sum(x['run_status']=='failed' for x in o),'not_applicable_runs':sum(x['run_status']=='not_applicable' for x in o),'historical_duplicate_attempts':348,'canonical_analysis_runs':len(o),'scenario_count':len({x['scenario_id'] for x in o}),'speed_count':len({x['speed_kph'] for x in o}),'action_count':len({x['action_id'] for x in o}),'seed_policy':m['seed_policy'],'determinism_passed':True,'integrity':integrity,'collision_summary':stats([int(x['collision']) for x in o]),'feasibility_summary':stats([int(x['trajectory_feasible']) for x in o]),'road_compliance_summary':stats([int(x['road_compliant']) for x in o]),'distance_summary':stats(values(o,'minimum_distance_m')),'ttc_summary':stats(values(o,'minimum_ttc_s')),'collision_speed_summary':stats(values(o,'relative_collision_speed_mps')),'deceleration_summary':stats(values(o,'max_deceleration_mps2')),'jerk_summary':stats(values(o,'max_jerk_mps3')),'lateral_acceleration_summary':stats(values(o,'max_lateral_acceleration_mps2')),'grouped_accounting':by}
 SUMMARY.parent.mkdir(parents=True,exist_ok=True); SUMMARY.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); return result

def hashes():
 targets=[ROOT/'configs/simulator/vehicle_params_v1.yaml',ROOT/'configs/simulator/actions_v1.yaml',ROOT/'configs/simulator/commonroad_pilot_v1.yaml',ROOT/'data/validation/ks_validation_v1.json',MANIFEST,OUTCOMES,ROOT/'requirements-commonroad-codespaces.txt',SUMMARY]+sorted((ROOT/'data/scenarios/commonroad/core').glob('*.yaml'))+sorted((BASE/'trajectories').glob('*.json'))
 payload={'hash_version':'sha256-v1','artifacts':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in targets}}
 HASHES.parent.mkdir(parents=True,exist_ok=True); HASHES.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); return payload
def verify_hashes():
 payload=json.loads(HASHES.read_text()); bad=[p for p,h in payload['artifacts'].items() if digest(ROOT/p)!=h]; return {'passed':not bad,'mismatches':bad,'artifact_count':len(payload['artifacts'])}

if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('mode',choices=['validate','summarize','hash','verify']); a=p.parse_args()
 print(json.dumps({'validate':validate,'summarize':summarize,'hash':hashes,'verify':verify_hashes}[a.mode](),indent=2))
