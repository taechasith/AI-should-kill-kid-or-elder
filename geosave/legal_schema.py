"""Typed, dependency-free legal-evidence contract for the deterministic GeoSAVE gate."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Mapping

class LegalStatus(str, Enum):
    PERMITTED='PERMITTED'; PROHIBITED='PROHIBITED'; REQUIRED='REQUIRED'; CONDITIONALLY_PERMITTED='CONDITIONALLY_PERMITTED'; NOT_DETERMINED='NOT_DETERMINED'; CONFLICTING_AUTHORITIES='CONFLICTING_AUTHORITIES'
class EvidenceSufficiency(str, Enum):
    SUFFICIENT_PRIMARY='SUFFICIENT_PRIMARY'; SUFFICIENT_OFFICIAL_SECONDARY='SUFFICIENT_OFFICIAL_SECONDARY'; PARTIAL='PARTIAL'; CONFLICTING='CONFLICTING'; INSUFFICIENT='INSUFFICIENT'; NO_EVIDENCE='NO_EVIDENCE'
class AuthorityLevel(str, Enum):
    INTERNATIONAL='international'; NATIONAL='national'; STATE_PROVINCE='state/province'; LOCAL='local'
class SourceType(str, Enum):
    STATUTE='statute'; REGULATION='regulation'; OFFICIAL_CODE='official_code'; COURT_DECISION='court_decision'; GOVERNMENT_GUIDANCE='government_guidance'; TREATY_CONVENTION='treaty/convention'; SECONDARY_OFFICIAL_DATASET='secondary_official_dataset'

PRIMARY_SOURCE_TYPES={SourceType.STATUTE,SourceType.REGULATION,SourceType.OFFICIAL_CODE,SourceType.COURT_DECISION,SourceType.TREATY_CONVENTION}

@dataclass(frozen=True)
class Jurisdiction:
    country_iso3:str; country_name:str; subnational_region:str|None=None

@dataclass(frozen=True)
class LegalQuery:
    jurisdiction:Jurisdiction; scenario_id:str; action_id:str; evaluation_date:date
    road_context:Mapping[str,str]=field(default_factory=dict); physical_context:Mapping[str,str]=field(default_factory=dict); relevant_conditions:Mapping[str,str]=field(default_factory=dict)

@dataclass(frozen=True)
class LegalEvidence:
    evidence_id:str; jurisdiction:Jurisdiction; authority_level:AuthorityLevel; source_type:SourceType
    source_title:str; source_authority:str; source_url:str; retrieved_at:date; language:str; original_text:str
    provision_identifier:str; normalized_rule:str; rule_category:str; legal_status_supported:LegalStatus
    evidence_strength:str; citation:str
    publication_date:date|None=None; effective_from:date|None=None; effective_to:date|None=None; translated_text:str|None=None
    applies_to:str='uncertain'; scenario_conditions:Mapping[str,str]=field(default_factory=dict); action_conditions:Mapping[str,str]=field(default_factory=dict)
    scenario_ids:tuple[str,...]=(); action_ids:tuple[str,...]=()
    exceptions:tuple[str,...]=(); interpretation_notes:str=''; instrument_applicability:str|None=None
    def to_dict(self):
        out=asdict(self)
        for key,value in list(out.items()):
            if isinstance(value,date): out[key]=value.isoformat()
        out['jurisdiction']=asdict(self.jurisdiction); out['authority_level']=self.authority_level.value; out['source_type']=self.source_type.value; out['legal_status_supported']=self.legal_status_supported.value
        return out

@dataclass(frozen=True)
class LegalDecision:
    jurisdiction:Jurisdiction; scenario_id:str; action_id:str; status:LegalStatus
    applicable_evidence_ids:tuple[str,...]; supporting_evidence_ids:tuple[str,...]; contradicting_evidence_ids:tuple[str,...]
    conditions:Mapping[str,str]; exceptions:tuple[str,...]; evidence_sufficiency:EvidenceSufficiency; reason_code:str; human_review_required:bool
    def to_dict(self):
        out=asdict(self); out['jurisdiction']=asdict(self.jurisdiction); out['status']=self.status.value; out['evidence_sufficiency']=self.evidence_sufficiency.value; return out
