"""Conservative deterministic classification over explicitly supplied evidence."""
from __future__ import annotations
from .legal_schema import EvidenceSufficiency,LegalDecision,LegalEvidence,LegalQuery,LegalStatus,PRIMARY_SOURCE_TYPES

def _conditions_match(expected,query):
    context={**query.road_context,**query.physical_context,**query.relevant_conditions}
    return all(context.get(key)==value for key,value in expected.items())
def _applicable(e,query):
    if e.jurisdiction.country_iso3 != query.jurisdiction.country_iso3:return False
    if e.jurisdiction.subnational_region and e.jurisdiction.subnational_region != query.jurisdiction.subnational_region:return False
    if e.scenario_ids and query.scenario_id not in e.scenario_ids:return False
    if e.action_ids and query.action_id not in e.action_ids:return False
    if e.effective_from and query.evaluation_date < e.effective_from:return False
    if e.effective_to and query.evaluation_date > e.effective_to:return False
    return _conditions_match(e.scenario_conditions,query) and _conditions_match(e.action_conditions,query)
def classify(query:LegalQuery,evidence:list[LegalEvidence])->LegalDecision:
    applicable=[e for e in evidence if _applicable(e,query)]
    ids=tuple(e.evidence_id for e in applicable)
    if not applicable:return LegalDecision(query.jurisdiction,query.scenario_id,query.action_id,LegalStatus.NOT_DETERMINED,(),(),(),dict(query.relevant_conditions),(),EvidenceSufficiency.NO_EVIDENCE,'no_applicable_evidence',True)
    statuses={e.legal_status_supported for e in applicable}
    if len(statuses)>1:
        return LegalDecision(query.jurisdiction,query.scenario_id,query.action_id,LegalStatus.CONFLICTING_AUTHORITIES,ids,(),ids,dict(query.relevant_conditions),(),EvidenceSufficiency.CONFLICTING,'unresolved_evidence_conflict',True)
    status=next(iter(statuses)); primary=all(e.source_type in PRIMARY_SOURCE_TYPES for e in applicable)
    sufficient=EvidenceSufficiency.SUFFICIENT_PRIMARY if primary else EvidenceSufficiency.SUFFICIENT_OFFICIAL_SECONDARY
    return LegalDecision(query.jurisdiction,query.scenario_id,query.action_id,status,ids,ids,(),dict(query.relevant_conditions),tuple(x for e in applicable for x in e.exceptions),sufficient,'supported_by_applicable_evidence',False)
