import json
import pytest
from pathlib import Path

from geosave.phase7_population_sampling import build_sample, ht_rate, stratified_ht_variance, terminal_success_ids, validate_sample


def frame():
    rows=[]
    for model in ("m1", "m2"):
        for condition in ("C0", "C1"):
            for i in range(6):
                rows.append({"run_id":f"{model}-{condition}-{i}","model_id":model,"condition":condition,"execution_state":"pending_zero_cost_authorization"})
    rows.extend({"run_id":f"na-{i}","execution_state":"not_applicable"} for i in range(2))
    return {"rows":rows}


def test_sampling_is_deterministic_and_weights_are_valid():
    # Validation's fixed 4,104 guard intentionally rejects this synthetic frame.
    one=build_sample(frame(), {"m1-C0-0"}, seed=7, per_stratum=2)
    two=build_sample(frame(), {"m1-C0-0"}, seed=7, per_stratum=2)
    assert one["probability_sample_units"] == two["probability_sample_units"]
    assert one["certainty_count"] + one["remaining_population_size"] == 24
    assert all(0 < x["inclusion_probability"] <= 1 for x in one["probability_sample_units"])
    assert any("provider population" in error for error in validate_sample(one, frame()))


def test_ht_and_variance_on_synthetic_population():
    sample=build_sample(frame(), {"m1-C0-0"}, seed=3, per_stratum=5)
    outcomes={unit["run_id"]: 1 for unit in sample["certainty_units"] + sample["probability_sample_units"]}
    assert ht_rate(sample, outcomes) == pytest.approx(1.0)
    assert stratified_ht_variance(sample, outcomes) == pytest.approx(0.0)


def test_terminal_successes_read_only_status_and_run_id(tmp_path: Path):
    p=tmp_path/"r"/"attempt_0001.json"; p.parent.mkdir()
    p.write_text(json.dumps({"run_id":"r","http_status":200,"status":"completed","selected_action_id":"DO_NOT_READ"}))
    assert terminal_success_ids(tmp_path) == {"r"}


def test_srs_estimator_is_approximately_unbiased_in_monte_carlo():
    population=frame()
    truth={row["run_id"]: int(row["run_id"].endswith(("0", "1", "2")))
           for row in population["rows"] if row["execution_state"] == "pending_zero_cost_authorization"}
    estimates=[]
    for seed in range(200):
        sample=build_sample(population, set(), seed=seed, per_stratum=3)
        observed={unit["run_id"]: truth[unit["run_id"]] for unit in sample["probability_sample_units"]}
        estimates.append(ht_rate(sample, observed))
    assert sum(estimates)/len(estimates) == pytest.approx(sum(truth.values())/len(truth), abs=0.03)
