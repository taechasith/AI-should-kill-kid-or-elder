"""Non-scalar Phase 5 output joining immutable physical evidence to a legal decision."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from .baseline import ActionEvidence
from .legal_schema import LegalDecision, LegalStatus

class PhysicalRiskCategory(str, Enum):
    PHYSICAL_RISK_ACCEPTABLE='PHYSICAL_RISK_ACCEPTABLE'
    PHYSICAL_RISK_ELEVATED='PHYSICAL_RISK_ELEVATED'
    PHYSICALLY_INFEASIBLE='PHYSICALLY_INFEASIBLE'
class SafetyLawRelation(str, Enum):
    PHYSICAL_RISK_ACCEPTABLE_AND_PERMITTED='PHYSICAL_RISK_ACCEPTABLE_AND_PERMITTED'
    PHYSICAL_RISK_ACCEPTABLE_BUT_PROHIBITED='PHYSICAL_RISK_ACCEPTABLE_BUT_PROHIBITED'
    PHYSICAL_RISK_ACCEPTABLE_LEGALITY_NOT_DETERMINED='PHYSICAL_RISK_ACCEPTABLE_LEGALITY_NOT_DETERMINED'
    PHYSICAL_RISK_ELEVATED_BUT_PERMITTED='PHYSICAL_RISK_ELEVATED_BUT_PERMITTED'
    PHYSICAL_RISK_ELEVATED_AND_PROHIBITED='PHYSICAL_RISK_ELEVATED_AND_PROHIBITED'
    PHYSICAL_RISK_ELEVATED_LEGALITY_NOT_DETERMINED='PHYSICAL_RISK_ELEVATED_LEGALITY_NOT_DETERMINED'
    PHYSICALLY_INFEASIBLE='PHYSICALLY_INFEASIBLE'
    LEGAL_EVIDENCE_CONFLICT='LEGAL_EVIDENCE_CONFLICT'
@dataclass(frozen=True)
class GeoSAVEOutput:
    action_id:str; physical_risk:PhysicalRiskCategory; legal_decision:LegalDecision; safety_law_relation:SafetyLawRelation
    physical_model_uncertainty:float; legal_evidence_uncertainty:str; legal_interpretation_uncertainty:str; jurisdiction_applicability_uncertainty:str; scenario_condition_uncertainty:str
    def to_dict(self):
        return {**asdict(self),'physical_risk':self.physical_risk.value,'safety_law_relation':self.safety_law_relation.value,'legal_decision':self.legal_decision.to_dict()}
def classify_physical_risk(action:ActionEvidence)->PhysicalRiskCategory:
    if not action.feasible:return PhysicalRiskCategory.PHYSICALLY_INFEASIBLE
    return PhysicalRiskCategory.PHYSICAL_RISK_ELEVATED if action.collision else PhysicalRiskCategory.PHYSICAL_RISK_ACCEPTABLE
def structure(action:ActionEvidence, legal:LegalDecision, *, physical_model_uncertainty:float=0., legal_interpretation_uncertainty:str='explicitly_preserved', jurisdiction_applicability_uncertainty:str='explicitly_preserved', scenario_condition_uncertainty:str='explicitly_preserved')->GeoSAVEOutput:
    physical=classify_physical_risk(action)
    if physical is PhysicalRiskCategory.PHYSICALLY_INFEASIBLE: relation=SafetyLawRelation.PHYSICALLY_INFEASIBLE
    elif legal.status is LegalStatus.CONFLICTING_AUTHORITIES: relation=SafetyLawRelation.LEGAL_EVIDENCE_CONFLICT
    elif legal.status in {LegalStatus.NOT_DETERMINED}: relation=SafetyLawRelation.PHYSICAL_RISK_ACCEPTABLE_LEGALITY_NOT_DETERMINED if physical is PhysicalRiskCategory.PHYSICAL_RISK_ACCEPTABLE else SafetyLawRelation.PHYSICAL_RISK_ELEVATED_LEGALITY_NOT_DETERMINED
    elif legal.status is LegalStatus.PROHIBITED: relation=SafetyLawRelation.PHYSICAL_RISK_ACCEPTABLE_BUT_PROHIBITED if physical is PhysicalRiskCategory.PHYSICAL_RISK_ACCEPTABLE else SafetyLawRelation.PHYSICAL_RISK_ELEVATED_AND_PROHIBITED
    else: relation=SafetyLawRelation.PHYSICAL_RISK_ACCEPTABLE_AND_PERMITTED if physical is PhysicalRiskCategory.PHYSICAL_RISK_ACCEPTABLE else SafetyLawRelation.PHYSICAL_RISK_ELEVATED_BUT_PERMITTED
    return GeoSAVEOutput(action.action_id,physical,legal,relation,physical_model_uncertainty,legal.evidence_sufficiency.value,legal_interpretation_uncertainty,jurisdiction_applicability_uncertainty,scenario_condition_uncertainty)
