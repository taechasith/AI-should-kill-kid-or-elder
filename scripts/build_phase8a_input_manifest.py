"""Inventory and hash the immutable Phase 8A inputs without provider access."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geosave.phase8a_analysis import load_json, sha256_file, verify_hash_manifest, write_json

OUT = ROOT / "data/analysis/phase8a/phase8a_input_manifest.json"
HASH_MANIFESTS = [
    ("data/simulator/commonroad/hashes/commonroad_pilot_v1_sha256.json", "36deb29"),
    ("data/legal/phase5/hashes/phase5_legal_snapshot_v1_sha256.json", "phase5-legal-snapshot-v1"),
    ("data/model_benchmark/phase6_literature_v2/hashes/phase6_literature_v2_pilot_sha256.json", "phase6-literature-v2-pilot-v1"),
    ("data/model_benchmark/phase7_population_sample_v1/hashes/phase7_psb_v1_protocol_sha256.json", "99551fa"),
]


def main() -> None:
    errors = [error for name, revision in HASH_MANIFESTS for error in verify_hash_manifest(ROOT, ROOT / name, revision=revision)]
    if errors:
        raise SystemExit("frozen input verification failed:\n" + "\n".join(errors))
    sample = load_json(ROOT / "data/model_benchmark/phase7_population_sample_v1/manifests/phase7_psb_v1_sample.json")
    execution = load_json(ROOT / "data/model_benchmark/phase7_population_sample_v1/reports/phase7_psb_v1_execution_report.json")
    phase7 = load_json(ROOT / "data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json")
    actions = load_json(ROOT / "configs/simulator/actions_v1.yaml")
    selected = sample["certainty_units"] + sample["probability_sample_units"]
    records = []
    for unit in selected:
        root = ROOT / "data/model_benchmark/phase7_literature_v2/attempts"
        candidates = [root / f"{unit['run_id']}.json", *sorted((root / unit["run_id"]).glob("*.json"))]
        candidates = [candidate for candidate in candidates if candidate.is_file()]
        completed = [candidate for candidate in candidates if (record := load_json(candidate)).get("status") == "completed" and record.get("http_status") == 200]
        if len(completed) != 1:
            raise SystemExit(f"expected one terminal selected Phase 7 record for {unit['run_id']}; found {len(completed)}")
        path = completed[0]
        record = load_json(path)
        raw = ROOT / record["raw_response_reference"]
        from geosave.phase8a_analysis import git_blob_bytes
        if not raw.is_file() or __import__("hashlib").sha256(git_blob_bytes(ROOT, "99551fa", record["raw_response_reference"])).hexdigest() != record["raw_response_sha256"]:
            raise SystemExit(f"raw-response provenance mismatch: {unit['run_id']}")
        records.append({"run_id": unit["run_id"], "selection": unit, "attempt_path": str(path.relative_to(ROOT)).replace("\\", "/"), "attempt_sha256": sha256_file(path), "raw_response_reference": record["raw_response_reference"], "raw_response_sha256": record["raw_response_sha256"]})
    if len({row["run_id"] for row in records}) != len(records):
        raise SystemExit("duplicate selected observation id")
    manifest = {
        "schema_version": "phase8a-input-manifest-v1",
        "offline_only": True,
        "source_phase7_recovered_checkpoint": "99551fa86bf11e5771339fd68c035943a149d3ee",
        "source_phase7_recovered_tag": "phase7-population-sample-recovered-v1",
        "source_phase4_canonical_data_commit": phase7["source_phase4_commit"],
        "source_phase4_hash_normalization_commit": "36deb29",
        "source_phase4_tag": "commonroad-pilot-v1",
        "source_phase5_snapshot": phase7["law_snapshot"],
        "source_phase5_tag": "phase5-legal-snapshot-v1",
        "source_phase6_tag": phase7["phase6_pilot_tag"],
        "phase7_sampling_amendment": "docs/PHASE_7_POPULATION_SAMPLING_AMENDMENT.md",
        "parser_interface": "prompts/phase6/decision_line_protocol_v2.md",
        "action_allowlist": sorted(actions["profiles"]),
        "physical_outcome_schema": "commonroad-pilot-v1 outcomes JSONL",
        "frozen_counts": {"design_accounted": len(phase7["rows"]), "provider_execution_population": sample["provider_population_size"], "not_applicable": sample["not_applicable_size"], "certainty": sample["certainty_count"], "probability_sample": sample["probability_sample_size"], "attempted": len(records), "terminal": sum(1 for row in records if load_json(ROOT / row["attempt_path"])["status"] == "completed")},
        "model_provider_identities": sorted({f"{row['model_id']} | {row['provider']}" for row in phase7["rows"]}),
        "sampling": {key: sample[key] for key in ("sampling_design", "rng_algorithm", "rng_seed", "strata", "selection_payload_sha256", "population_frame_sha256")},
        "frozen_hash_manifests": {name: {"revision": revision, "working_copy_sha256": sha256_file(ROOT / name)} for name, revision in HASH_MANIFESTS},
        "selected_observation_provenance": records,
        "phase7_execution_report_sha256": sha256_file(ROOT / "data/model_benchmark/phase7_population_sample_v1/reports/phase7_psb_v1_execution_report.json"),
    }
    write_json(OUT, manifest)
    print(f"Phase 8A input manifest written: {OUT.relative_to(ROOT)} ({len(records)} selected observations)")


if __name__ == "__main__":
    main()
