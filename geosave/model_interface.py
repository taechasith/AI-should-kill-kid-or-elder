"""Offline-only, versioned model-interface contracts; no provider client is included."""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

ALLOWED_ACTIONS={'A0','A1','A2','A3','A4','A6'}
ParseStatus=Literal['valid','repaired','failed']
@dataclass(frozen=True)
class ModelSpec:
    model_id:str; revision:str; provider:str; execution_enabled:bool=False
@dataclass(frozen=True)
class PromptSpec:
    prompt_id:str; version:str; condition:str; template_path:str
@dataclass(frozen=True)
class ParsedDecision:
    selected_action:str; rationale:str; legal_assessment:dict[str,str]
@dataclass(frozen=True)
class ParseResult:
    status:ParseStatus; decision:ParsedDecision|None; error:str|None; repair_attempted:bool
    def to_dict(self): return asdict(self)

def _decode(text:str)->ParsedDecision:
    value=json.loads(text)
    if set(value)-{'selected_action','rationale','legal_assessment'}: raise ValueError('unexpected response key')
    if value.get('selected_action') not in ALLOWED_ACTIONS: raise ValueError('invalid selected_action')
    if not isinstance(value.get('rationale'),str): raise ValueError('rationale must be string')
    legal=value.get('legal_assessment',{})
    if not isinstance(legal,dict) or any(k not in ALLOWED_ACTIONS or v not in {'legal','illegal','conditionally_legal','not_applicable','unknown'} for k,v in legal.items()): raise ValueError('invalid legal_assessment')
    return ParsedDecision(value['selected_action'],value['rationale'],legal)
def parse_response(raw:str)->ParseResult:
    """Parse once; then make one deterministic fence-only repair attempt."""
    try:return ParseResult('valid',_decode(raw),None,False)
    except (ValueError,json.JSONDecodeError) as first:
        repaired=raw.strip()
        if repaired.startswith('```') and repaired.endswith('```'):
            repaired='\n'.join(repaired.splitlines()[1:-1]).strip()
            try:return ParseResult('repaired',_decode(repaired),None,True)
            except (ValueError,json.JSONDecodeError) as second:return ParseResult('failed',None,str(second),True)
        return ParseResult('failed',None,str(first),False)
def persist_raw(path:Path,raw:str)->None:
    """Raw responses are append-only: accidental overwrite is an error."""
    if path.exists(): raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(raw,encoding='utf-8')
