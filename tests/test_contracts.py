import hashlib
import json
from pathlib import Path
import unittest

from geosave.action_constraints import action_gate, eligible_actions
from geosave.contracts import (
    ContractError,
    configuration_fingerprint,
    is_verified_lawful,
    validate_legal_rule,
    validate_model_decision,
    validate_physical_outcome,
    validate_scenario,
)


LEGAL_RULE = {
    "schema_version": "v1",
    "rule_id": "THA-LANE-001",
    "jurisdiction": "THA",
    "effective_from": "2026-01-01",
    "retrieved_at": "2026-09-27",
    "category": "lane_marking",
    "rule_status": "unresolved",
    "source": {"title": "Official source", "url": "https://example.org/rule", "source_type": "official_statute"},
}


class ContractTests(unittest.TestCase):
    def test_legal_rule_requires_jurisdiction_and_source(self):
        invalid = dict(LEGAL_RULE)
        invalid.pop("jurisdiction")
        with self.assertRaises(ContractError):
            validate_legal_rule(invalid)

    def test_legal_rule_rejects_invalid_date_and_status(self):
        invalid = dict(LEGAL_RULE, effective_from="2026-99-99")
        with self.assertRaises(ContractError):
            validate_legal_rule(invalid)

    def test_legal_rule_allows_explicit_unknown_effective_date(self):
        unknown_date = dict(LEGAL_RULE, effective_from=None)
        validate_legal_rule(unknown_date)
        invalid = dict(LEGAL_RULE, rule_status="certain")
        with self.assertRaises(ContractError):
            validate_legal_rule(invalid)

    def test_unknown_law_never_becomes_compliant(self):
        decision = {
            "schema_version": "v1", "run_id": "run-001", "scenario_id": "SC01",
            "country_iso3": "THA", "law_snapshot": "2026-10-15", "model_id": "local-model",
            "model_revision": "v1", "prompt_version": "v001", "condition": "C2", "seed": 1,
            "action_order": ["A1", "A2"], "parse_status": "valid", "selected_action": "A2",
            "legal_assessment": {"A2": "unknown"},
        }
        validate_model_decision(decision)
        self.assertEqual(decision["legal_assessment"]["A2"], "unknown")
        self.assertFalse(is_verified_lawful(decision["legal_assessment"]["A2"]))

    def test_scenario_rejects_invalid_action(self):
        with self.assertRaises(ContractError):
            validate_scenario({
                "schema_version": "v1", "scenario_id": "SC01", "family": "crossing", "version": "1",
                "split": "development", "candidate_actions": ["A9"], "physical_parameters": {},
                "legal_dimensions": ["pedestrian_priority"], "uncertainty": {}, "metrics": ["collision"],
                "action_constraints": {},
            })

    def test_same_configuration_has_same_fingerprint(self):
        config = {
            "schema_version": "v1", "experiment_id": "pilot", "law_snapshot": "2026-10-15",
            "scenarios": "pilot_v1", "jurisdictions": "pilot_v1", "models": ["local-model"],
            "conditions": ["C0"], "generation": {"seed": 42, "repetitions": 1},
        }
        self.assertEqual(configuration_fingerprint(config), configuration_fingerprint(dict(config)))
        changed = dict(config, generation={"seed": 43, "repetitions": 1})
        self.assertNotEqual(configuration_fingerprint(config), configuration_fingerprint(changed))

    def test_pilot_deep_law_records_validate_and_keep_nsw_subnational(self):
        root = Path(__file__).resolve().parents[1]
        nsw_record = None
        for rules_path in (root / "data" / "deep_law" / "snapshots" / "2026-09-27-pilot-v1").glob("*/rules.json"):
            for record in json.loads(rules_path.read_text(encoding="utf-8")):
                validate_legal_rule(record)
                if record["rule_id"] == "AUS-NSW-PED-081":
                    nsw_record = record
        self.assertEqual(nsw_record["jurisdiction"], "AUS")
        self.assertEqual(nsw_record["subnational_code"], "NSW")

    def test_pilot_snapshot_hashes_match_rule_files(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = root / "data" / "deep_law" / "snapshots" / "2026-09-27-pilot-v1"
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        for relative_path, expected_hash in manifest["sha256"].items():
            actual_hash = hashlib.sha256((snapshot / relative_path).read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash)

    def test_scenario_pilot_validates_and_spans_all_splits(self):
        root = Path(__file__).resolve().parents[1]
        scenarios = [json.loads(path.read_text(encoding="utf-8")) for path in (root / "data" / "scenarios" / "pilot_v1").glob("*.json")]
        for scenario in scenarios:
            validate_scenario(scenario)
        self.assertEqual({scenario["split"] for scenario in scenarios}, {"development", "validation", "frozen_test"})

    def test_action_gate_rejects_infeasible_and_unstable_actions(self):
        root = Path(__file__).resolve().parents[1]
        pedestrian = json.loads((root / "data" / "scenarios" / "pilot_v1" / "SC-PED-001.json").read_text(encoding="utf-8"))
        lane = json.loads((root / "data" / "scenarios" / "pilot_v1" / "SC-LANE-001.json").read_text(encoding="utf-8"))
        self.assertEqual(action_gate(pedestrian, "A3"), (False, "physically_infeasible"))
        self.assertEqual(action_gate(lane, "A4"), (False, "stability_failure_risk"))
        self.assertIn("A2", eligible_actions(pedestrian))

    def test_physical_outcome_completed_fixture_and_failure_representation(self):
        root = Path(__file__).resolve().parents[1]
        completed = json.loads((root / "tests" / "fixtures" / "physical_outcome_completed.json").read_text(encoding="utf-8"))
        validate_physical_outcome(completed)
        failure = {
            "schema_version": "v1", "scenario_id": "SC-PED-001", "variant_id": "v1",
            "action_id": "A2", "seed": 101, "run_status": "failed",
            "failure_reason": "simulator_connection_refused",
        }
        validate_physical_outcome(failure)
        with self.assertRaises(ContractError):
            validate_physical_outcome(dict(failure, failure_reason=""))


if __name__ == "__main__":
    unittest.main()
