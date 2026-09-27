from pathlib import Path
import pytest
from geosave.model_interface import parse_response,persist_raw
VALID='{"selected_action":"A2","rationale":"bounded response","legal_assessment":{"A2":"unknown"}}'
def test_strict_valid_json_and_single_repair():
 assert parse_response(VALID).status=='valid'
 repaired=parse_response('```json\n'+VALID+'\n```'); assert repaired.status=='repaired' and repaired.repair_attempted
def test_invalid_or_extra_output_fails_without_guessing():
 assert parse_response('{"selected_action":"A9","rationale":"x"}').status=='failed'
 assert parse_response('{"selected_action":"A2","rationale":"x","extra":1}').status=='failed'
def test_raw_output_is_append_only(tmp_path:Path):
 target=tmp_path/'raw.txt'; persist_raw(target,VALID); assert target.read_text()==VALID
 with pytest.raises(FileExistsError): persist_raw(target,VALID)
