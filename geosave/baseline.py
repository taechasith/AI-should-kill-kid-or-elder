"""Phase 5 deterministic GeoSAVE baseline with separable, auditable gates."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

LegalStatus=Literal['legal','illegal','conditionally_legal','not_applicable','unknown']
@dataclass(frozen=True)
class ActionEvidence:
 action_id:str; feasible:bool; collision:bool; minimum_distance_m:float; legal_status:LegalStatus; uncertainty:float=0.; controllability_cost:float=0.; emergency_exception:bool=False
@dataclass(frozen=True)
class Decision:
 selected_action:str|None; labels:dict[str,tuple[str,...]]; safety_law_conflict:bool

def evaluate(actions:list[ActionEvidence]) -> Decision:
 """Apply feasibility, risk, law, conflict, then uncertainty lexicographically."""
 labels={a.action_id:[] for a in actions}; feasible=[]
 for a in actions:
  if not a.feasible: labels[a.action_id].append('physically_infeasible'); continue
  feasible.append(a)
 if not feasible:return Decision(None,{k:tuple(v) for k,v in labels.items()},False)
 risk=min((int(a.collision),-a.minimum_distance_m) for a in feasible)
 safest=[a for a in feasible if (int(a.collision),-a.minimum_distance_m)==risk]
 lawful=[a for a in safest if a.legal_status in {'legal','conditionally_legal','not_applicable'} or a.emergency_exception]
 conflict=not lawful and bool(safest)
 if conflict:
  for a in safest: labels[a.action_id].append('safety_law_conflict')
  pool=safest
 else: pool=lawful
 for a in feasible:
  if a.legal_status=='unknown': labels[a.action_id].append('law_unknown')
  elif a.legal_status=='illegal' and not a.emergency_exception: labels[a.action_id].append('legal_prohibition')
 selected=min(pool,key=lambda a:(a.uncertainty,a.controllability_cost,a.action_id))
 return Decision(selected.action_id,{k:tuple(v) for k,v in labels.items()},conflict)
