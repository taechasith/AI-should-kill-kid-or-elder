from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_snapshot_hashes_and_coverage_are_consistent() -> None:
    phase5 = ROOT / "data" / "legal" / "phase5"
    manifest_path = phase5 / "hashes" / "phase5_legal_snapshot_v1_sha256.json"
    assert manifest_path.is_file(), "run scripts/finalize_phase5_legal_snapshot.py first"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, expected in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    coverage = json.loads((phase5 / "phase5_coverage_v1.json").read_text(encoding="utf-8"))
    assert coverage["frozen_jurisdiction_count"] == 25
    assert coverage["query_count"] == coverage["decision_count"] == 900
    assert coverage["decision_status_counts"] == {"NOT_DETERMINED": 900}


def test_global_context_is_explicitly_nonlegal() -> None:
    manifest = json.loads((ROOT / "data" / "legal" / "phase5" / "global_context" / "who_road_safety_2023_acquisition_manifest.json").read_text(encoding="utf-8"))
    assert manifest["context_only"] is True
    assert manifest["action_level_legal_classification_prohibited"] is True
    assert manifest["collected_profile_count"] == 172


def test_snapshot_does_not_silently_use_who_or_unece_as_domestic_law() -> None:
    phase5 = ROOT / "data" / "legal" / "phase5"
    evidence = [json.loads(line) for line in (phase5 / "primary_evidence.jsonl").read_text(encoding="utf-8").splitlines()]
    decisions = [json.loads(line) for line in (phase5 / "legal_decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all("world health organization" not in f"{row['source_title']} {row['issuing_authority']}".lower() for row in evidence)
    assert all(row["authority_level"] != "international" for row in evidence)
    assert all(not row["supporting_evidence_ids"] for row in decisions)
