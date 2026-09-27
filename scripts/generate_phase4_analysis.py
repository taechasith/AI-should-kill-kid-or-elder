"""Regenerate descriptive Phase 4 analysis and figures from canonical outcomes."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'data/simulator/commonroad'
OUT=BASE/'outcomes/commonroad_pilot_v1.jsonl'; FIG=ROOT/'docs/figures/phase4'; REPORT=ROOT/'docs/PHASE_4_ANALYSIS.md'

def rows(): return [json.loads(x) for x in OUT.read_text().splitlines() if x]
def grouped(data,key): return {v:[x for x in data if x[key]==v] for v in sorted({x[key] for x in data})}
def rate(group,key): return sum(x[key] for x in group)/len(group)
def main():
 d=rows(); FIG.mkdir(parents=True,exist_ok=True)
 for key,label,metric,name in [('scenario_id','Scenario','collision','collision_by_scenario'),('action_id','Action','collision','collision_by_action'),('speed_kph','Initial speed (km/h)','road_compliant','road_compliance_by_speed')]:
  g=grouped(d,key); plt.figure(figsize=(7,4)); plt.bar(list(g),[rate(v,metric) for v in g.values()],color='#176B87'); plt.ylim(0,1); plt.ylabel(f'{metric.replace("_"," ")} rate'); plt.xlabel(label); plt.tight_layout(); plt.savefig(FIG/f'{name}.png',dpi=180); plt.close()
 g=grouped(d,'action_id'); plt.figure(figsize=(7,4)); plt.boxplot([[x['minimum_distance_m'] for x in v] for v in g.values()],labels=g.keys()); plt.ylabel('Minimum shape distance (m)'); plt.xlabel('Action'); plt.tight_layout(); plt.savefig(FIG/'minimum_distance_by_action.png',dpi=180); plt.close()
 collision=sum(x['collision'] for x in d); feasible=sum(x['trajectory_feasible'] for x in d); road=sum(x['road_compliant'] for x in d)
 lines=['# Phase 4 descriptive analysis','',f'Generated from exactly {len(d)} canonical outcome records; the 348 duplicate-attempt records are excluded.','',f'- Collision: {collision}/{len(d)} ({collision/len(d):.2%}).',f'- Trajectory feasible: {feasible}/{len(d)} ({feasible/len(d):.2%}).',f'- Road compliant: {road}/{len(d)} ({road/len(d):.2%}).','', '## Scenario accounting','']
 for k,v in grouped(d,'scenario_id').items(): lines.append(f'- `{k}`: {len(v)} records; collision {sum(x["collision"] for x in v)}/{len(v)}; feasible {sum(x["trajectory_feasible"] for x in v)}/{len(v)}; road-compliant {sum(x["road_compliant"] for x in v)}/{len(v)}.')
 lines += ['', '## Interpretation boundary', '', 'These are descriptive physical-characterization results from a synthetic Kinematic Single-Track model. They are not injury, fatality, moral, legal-compliance, or real-world safety predictions.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__': main()
