import pytest
from geosave.experiment_manifest import ExperimentManifest,PlannedDecision,validate_manifest
def row(run_id='r1'): return PlannedDecision(run_id,'OBS-LANE-001__V030__A2__S042','TST','synthetic-v1','offline-fixture','v1','decision','v1','C0',42)
def test_draft_contract_and_duplicate_rejection():
 validate_manifest(ExperimentManifest('draft','v1','draft',(row(),)))
 with pytest.raises(ValueError): validate_manifest(ExperimentManifest('x','v1','draft',(row(),row())))
def test_frozen_requires_actual_rows():
 with pytest.raises(ValueError): validate_manifest(ExperimentManifest('x','v1','frozen',()))
