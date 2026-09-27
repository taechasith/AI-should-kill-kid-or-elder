"""Non-public Phase 9 readiness assessment; it cannot publish or submit anything."""
from __future__ import annotations
import json
from pathlib import Path

def assess(root:Path)->dict:
    required=['docs/REPRODUCIBILITY.md','docs/PHASE_4_RESULTS_SUMMARY.md','data/simulator/commonroad/hashes/commonroad_pilot_v1_sha256.json','docs/STATISTICAL_ANALYSIS_PLAN.md']
    present={p:(root/p).exists() for p in required}
    template=json.loads((root/'configs/experiments/phase7_preregistration_template.json').read_text())
    blockers=[]
    if template['status']!='frozen': blockers.append('Phase 7 benchmark manifest is intentionally unfrozen')
    if not template.get('models',[]): blockers.append('No authorized non-empty model registry exists')
    blockers += ['No reviewed benchmark-scale legal snapshot is frozen','No Phase 7 model benchmark has been executed','No independent clean reproduction has been performed']
    return {'status':'NOT_RELEASE_READY','required_artifacts_present':present,'blockers':blockers,'publication_or_submission_authorized':False}
