from datetime import date
from geosave.legal_classifier import classify
from geosave.legal_schema import *

J=Jurisdiction('TST','TEST-JURISDICTION-A'); Q=lambda **k: LegalQuery(J,'TEST-SCENARIO','A3',date(2026,1,1),relevant_conditions=k)
def e(id,status=LegalStatus.PERMITTED,**k):
 return LegalEvidence(id,J,AuthorityLevel.NATIONAL,k.pop('source_type',SourceType.STATUTE),'Synthetic statute','Synthetic authority','https://example.invalid',date(2026,1,1),'en','synthetic','s1','synthetic rule','lane',status,'synthetic',id,**k)
def test_no_evidence_never_permitted():
 d=classify(Q(),[]); assert d.status is LegalStatus.NOT_DETERMINED and d.evidence_sufficiency is EvidenceSufficiency.NO_EVIDENCE
def test_permission_prohibition_and_requirement():
 assert classify(Q(),[e('p')]).status is LegalStatus.PERMITTED
 assert classify(Q(),[e('x',LegalStatus.PROHIBITED)]).status is LegalStatus.PROHIBITED
 assert classify(Q(),[e('r',LegalStatus.REQUIRED)]).status is LegalStatus.REQUIRED
def test_conditional_and_unsatisfied_conditions():
 rule=e('c',LegalStatus.CONDITIONALLY_PERMITTED,action_conditions={'obstacle':'present'})
 assert classify(Q(obstacle='present'),[rule]).status is LegalStatus.CONDITIONALLY_PERMITTED
 assert classify(Q(obstacle='absent'),[rule]).status is LegalStatus.NOT_DETERMINED
def test_scenario_and_action_relation_is_explicit():
 rule=e('bound',scenario_ids=('TEST-SCENARIO',),action_ids=('A3',))
 assert classify(Q(),[rule]).status is LegalStatus.PERMITTED
 assert classify(LegalQuery(J,'OTHER','A3',date(2026,1,1)),[rule]).status is LegalStatus.NOT_DETERMINED
def test_conflicting_authorities_are_not_resolved_arbitrarily():
 d=classify(Q(),[e('permit'),e('prohibit',LegalStatus.PROHIBITED,source_type=SourceType.GOVERNMENT_GUIDANCE)])
 assert d.status is LegalStatus.CONFLICTING_AUTHORITIES and d.human_review_required
def test_temporal_and_jurisdiction_isolation():
 assert classify(Q(),[e('future',effective_from=date(2027,1,1))]).status is LegalStatus.NOT_DETERMINED
 assert classify(Q(),[e('expired',effective_to=date(2025,1,1))]).status is LegalStatus.NOT_DETERMINED
 other=LegalEvidence(**{**e('other').__dict__,'jurisdiction':Jurisdiction('TSB','TEST-JURISDICTION-B')})
 assert classify(Q(),[other]).status is LegalStatus.NOT_DETERMINED
def test_subnational_evidence_is_not_national():
 state=LegalEvidence(**{**e('state').__dict__,'jurisdiction':Jurisdiction('TST','TEST-JURISDICTION-A','X')})
 assert classify(Q(),[state]).status is LegalStatus.NOT_DETERMINED
def test_serialization_and_replay_are_deterministic():
 evidence=e('one'); a=classify(Q(),[evidence]); b=classify(Q(),[evidence]); assert a==b and a.to_dict()['status']=='PERMITTED' and evidence.to_dict()['evidence_id']=='one'
