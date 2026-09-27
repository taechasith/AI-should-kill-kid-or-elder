"""Phase 7 preregistration contract; does not execute a model or experiment."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Condition=Literal['C0','C1','C2','C4']
@dataclass(frozen=True)
class PlannedDecision:
    run_id:str; physical_run_id:str; jurisdiction:str; law_snapshot:str; model_id:str; model_revision:str; prompt_id:str; prompt_version:str; condition:Condition; seed:int
@dataclass(frozen=True)
class ExperimentManifest:
    experiment_id:str; version:str; status:Literal['draft','frozen']; rows:tuple[PlannedDecision,...]
def validate_manifest(manifest:ExperimentManifest)->None:
    if not manifest.experiment_id or not manifest.version: raise ValueError('experiment_id and version are required')
    ids=[r.run_id for r in manifest.rows]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate run_id')
    for row in manifest.rows:
        if not row.physical_run_id or not row.jurisdiction or not row.law_snapshot: raise ValueError('physical run, jurisdiction, and legal snapshot are required')
        if row.seed<0: raise ValueError('seed must be nonnegative')
    if manifest.status=='frozen' and not manifest.rows: raise ValueError('frozen manifest cannot be empty')
