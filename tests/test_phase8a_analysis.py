import json
from pathlib import Path

from geosave.phase8a_analysis import estimate_binary, ht_rate

ROOT = Path(__file__).resolve().parents[1]

def test_ht_rate_uses_inclusion_probabilities():
    sample = {"provider_population_size": 4, "certainty_units": [{"run_id": "a", "inclusion_probability": 1.0}], "probability_sample_units": [{"run_id": "b", "inclusion_probability": 0.5}], "strata": [{"stratum": "s", "remaining_population": 2, "sample_size": 1}]}
    assert ht_rate(sample, {"a": 1, "b": 1}) == 0.75

def test_estimate_preserves_strict_and_action_as_separate_values():
    sample = {"provider_population_size": 2, "certainty_units": [{"run_id": "a", "inclusion_probability": 1.0}, {"run_id": "b", "inclusion_probability": 1.0}], "probability_sample_units": [], "strata": []}
    assert estimate_binary(sample, {"a": 1, "b": 0})["weighted_estimate"] == 0.5


def test_recovered_sample_accounting_and_unique_observations():
    sample = json.loads((ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json").read_text())
    units = sample["certainty_units"] + sample["probability_sample_units"]
    assert (sample["full_manifest_size"], sample["provider_population_size"], sample["not_applicable_size"]) == (5454, 4104, 1350)
    assert len(units) == len({unit["run_id"] for unit in units}) == 339


def test_frozen_result_reproduces_known_rate_and_blocks_law():
    result = json.loads((ROOT / "data/analysis/phase8a/phase8a_results.json").read_text())
    rows = {row["result_id"]: row for row in result["results"]}
    assert abs(rows["P8A-INTERFACE-003"]["weighted_estimate"] - 0.8238304093567251) < 1e-12
    assert rows["P8A-LEGAL-001"]["estimability"] == "NOT_ESTIMABLE"


def test_phase8a_runner_has_no_provider_or_simulator_dependency():
    source = (ROOT / "scripts/run_phase8a_analysis.py").read_text(encoding="utf-8")
    assert "requests" not in source and "urllib" not in source
    assert "simulator.commonroad" not in source
