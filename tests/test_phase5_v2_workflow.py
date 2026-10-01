import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v2_workflow_preserves_unreviewed_and_final_status_distinction():
    workflow = json.loads((ROOT / "configs/legal/phase5_v2_collection_workflow.json").read_text(encoding="utf-8"))
    assert workflow["unreviewed_status"] == "NOT_DETERMINED"
    assert "EXPLICITLY_PERMITTED" in workflow["final_outcome_ontology"]
    assert "NOT_DETERMINED" not in workflow["final_outcome_ontology"]


def test_v2_workflow_never_treats_international_context_as_domestic_law():
    workflow = json.loads((ROOT / "configs/legal/phase5_v2_collection_workflow.json").read_text(encoding="utf-8"))
    assert "never a substitute" in workflow["international_instrument_boundary"]
