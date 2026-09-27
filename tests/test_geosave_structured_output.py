from datetime import date
from geosave.baseline import ActionEvidence
from geosave.legal_classifier import classify
from geosave.legal_schema import *
from geosave.structured_output import *
J=Jurisdiction('TST','TEST'); Q=LegalQuery(J,'S','A3',date(2026,1,1))
def evidence(status): return LegalEvidence('e',J,AuthorityLevel.NATIONAL,SourceType.STATUTE,'x','x','https://example.invalid',date(2026,1,1),'en','x','x','x','x',status,'synthetic','x')
def action(**kwargs): return ActionEvidence('A3',minimum_distance_m=2,legal_status='unknown',**kwargs)
def test_safe_but_prohibited_is_explicit():
 out=structure(action(feasible=True,collision=False),classify(Q,[evidence(LegalStatus.PROHIBITED)])); assert out.safety_law_relation is SafetyLawRelation.PHYSICAL_RISK_ACCEPTABLE_BUT_PROHIBITED
def test_elevated_but_permitted_is_explicit():
 out=structure(action(feasible=True,collision=True),classify(Q,[evidence(LegalStatus.PERMITTED)])); assert out.safety_law_relation is SafetyLawRelation.PHYSICAL_RISK_ELEVATED_BUT_PERMITTED
def test_unknown_conflict_and_infeasible_remain_separate():
 unknown=structure(action(feasible=True,collision=False),classify(Q,[])); assert unknown.safety_law_relation is SafetyLawRelation.PHYSICAL_RISK_ACCEPTABLE_LEGALITY_NOT_DETERMINED
 conflict=classify(Q,[evidence(LegalStatus.PERMITTED),LegalEvidence(**{**evidence(LegalStatus.PROHIBITED).__dict__,'evidence_id':'x'})]); assert structure(action(feasible=True,collision=False),conflict).safety_law_relation is SafetyLawRelation.LEGAL_EVIDENCE_CONFLICT
 assert structure(action(feasible=False,collision=False),classify(Q,[])).physical_risk is PhysicalRiskCategory.PHYSICALLY_INFEASIBLE
def test_output_is_deterministically_serializable():
 out=structure(action(feasible=True,collision=False),classify(Q,[evidence(LegalStatus.PERMITTED)])); assert out.to_dict()==out.to_dict()
