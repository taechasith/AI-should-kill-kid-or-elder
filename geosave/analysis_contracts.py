"""Phase 8 analysis contracts; deterministic utilities only, with no benchmark data."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class CounterfactualPair:
    pair_id:str; baseline_run_id:str; counterfactual_run_id:str; manipulation:str; baseline_action:str; counterfactual_action:str; parse_status:str
    @property
    def flipped(self)->bool:return self.baseline_action!=self.counterfactual_action
def flip_rate(pairs:Iterable[CounterfactualPair])->dict[str,float|int]:
    usable=[p for p in pairs if p.parse_status in {'valid','repaired'}]
    return {'eligible_pairs':len(usable),'flips':sum(p.flipped for p in usable),'flip_rate':sum(p.flipped for p in usable)/len(usable) if usable else 0.0}
def benjamini_hochberg(p_values:dict[str,float])->dict[str,float]:
    """Return monotone BH adjusted q-values keyed by supplied hypothesis ID."""
    if any(not 0<=p<=1 for p in p_values.values()):raise ValueError('p-values must lie in [0,1]')
    ordered=sorted(p_values.items(),key=lambda item:item[1]); n=len(ordered); adjusted={}; previous=1.0
    for rank,(key,p) in reversed(list(enumerate(ordered,start=1))):
        previous=min(previous,p*n/rank); adjusted[key]=min(1.0,previous)
    return adjusted
