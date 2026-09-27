from geosave.baseline import ActionEvidence,evaluate
def a(name,**kw): return ActionEvidence(name,**kw)
def test_infeasible_action_is_rejected():
 d=evaluate([a('A3',feasible=False,collision=False,minimum_distance_m=9,legal_status='legal'),a('A2',feasible=True,collision=False,minimum_distance_m=2,legal_status='legal')]); assert d.selected_action=='A2' and 'physically_infeasible' in d.labels['A3']
def test_unknown_is_not_lawful():
 d=evaluate([a('A1',feasible=True,collision=False,minimum_distance_m=2,legal_status='unknown'),a('A2',feasible=True,collision=False,minimum_distance_m=2,legal_status='legal')]); assert d.selected_action=='A2' and 'law_unknown' in d.labels['A1']
def test_safe_illegal_remains_conflict_not_legal():
 d=evaluate([a('A3',feasible=True,collision=False,minimum_distance_m=4,legal_status='illegal'),a('A2',feasible=True,collision=True,minimum_distance_m=0,legal_status='legal')]); assert d.selected_action=='A3' and d.safety_law_conflict and 'legal_prohibition' in d.labels['A3']
