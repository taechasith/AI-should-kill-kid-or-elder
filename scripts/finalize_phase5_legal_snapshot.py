"""Create the immutable Phase 5 snapshot, coverage report, and hash manifest."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

try:  # Supports both `python scripts/...` and import from the test suite.
    from validate_phase5_legal_snapshot import ROOT, validate_snapshot
except ModuleNotFoundError:  # pragma: no cover - exercised by package import.
    from scripts.validate_phase5_legal_snapshot import ROOT, validate_snapshot


PHASE5 = ROOT / "data" / "legal" / "phase5"
SNAPSHOT_DIR = PHASE5 / "snapshot"
HASH_DIR = PHASE5 / "hashes"
SNAPSHOT = SNAPSHOT_DIR / "phase5_legal_snapshot_v1.json"
COVERAGE = PHASE5 / "phase5_coverage_v1.json"
HASHES = HASH_DIR / "phase5_legal_snapshot_v1_sha256.json"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def build_coverage() -> dict:
    queries = jsonl(PHASE5 / "legal_queries.jsonl")
    decisions = jsonl(PHASE5 / "legal_decisions.jsonl")
    evidence = jsonl(PHASE5 / "primary_evidence.jsonl")
    sources = json.loads((PHASE5 / "source_metadata.json").read_text(encoding="utf-8"))["jurisdictions"]
    global_manifest = json.loads((PHASE5 / "global_context" / "who_road_safety_2023_acquisition_manifest.json").read_text(encoding="utf-8"))
    return {
        "schema_version": "phase5-coverage-v1",
        "snapshot_id": "phase5-legal-snapshot-v1",
        "frozen_jurisdiction_count": len({row["country_iso3"] for row in queries}),
        "query_count": len(queries),
        "decision_count": len(decisions),
        "decision_status_counts": dict(sorted(Counter(row["status"] for row in decisions).items())),
        "decision_reason_counts": dict(sorted(Counter(row["reason_code"] for row in decisions).items())),
        "evidence_count": len(evidence),
        "evidence_sufficiency_counts": dict(sorted(Counter(row["evidence_sufficiency"] for row in evidence).items())),
        "source_second_pass_access_counts": dict(sorted(Counter(row["second_pass_access"] for row in sources).items())),
        "source_hash_available_count": sum(bool(row.get("source_hash")) for row in sources),
        "global_context_profile_count": global_manifest["collected_profile_count"],
        "global_context_unavailable_or_unparseable_count": global_manifest["unavailable_or_unparseable_count"],
        "interpretation": "All action-level decisions remain NOT_DETERMINED because material legal predicates were intentionally not invented in the frozen legal overlay. These counts must not be presented as action legality rates.",
    }


def main() -> None:
    validate_snapshot()
    coverage = build_coverage()
    write(COVERAGE, coverage)
    snapshot = {
        "schema_version": "phase5-legal-snapshot-v1",
        "snapshot_id": "phase5-legal-snapshot-v1",
        "status": "frozen",
        "created_at": "2026-09-28",
        "source_protocol_commit": "5e81bf1",
        "physical_benchmark_tag": "commonroad-pilot-v1",
        "legal_context_overlay": relative(PHASE5 / "legal_context_overlay_v1.json"),
        "global_context": relative(PHASE5 / "global_context" / "who_road_safety_2023_context_v1.csv"),
        "primary_evidence": relative(PHASE5 / "primary_evidence.jsonl"),
        "legal_queries": relative(PHASE5 / "legal_queries.jsonl"),
        "legal_decisions": relative(PHASE5 / "legal_decisions.jsonl"),
        "jurisdiction_metadata": relative(PHASE5 / "jurisdiction_metadata.json"),
        "source_metadata": relative(PHASE5 / "source_metadata.json"),
        "coverage": relative(COVERAGE),
        "legal_status_boundary": "NOT_DETERMINED is not permission and every non-unknown action-level conclusion would require sufficient domestic primary evidence and all material overlay predicates.",
        "who_boundary": "WHO context data is not action-level legal authority.",
        "unece_boundary": "UNECE instruments are not domestic law without documented applicability.",
    }
    write(SNAPSHOT, snapshot)
    hash_targets = [
        ROOT / "configs" / "legal" / "phase5_two_level_v1.json",
        ROOT / "configs" / "simulator" / "actions_v1.yaml",
        ROOT / "requirements-phase5.txt",
        ROOT / "scripts" / "build_phase5_query_universe.py",
        ROOT / "scripts" / "collect_who_global_context.py",
        ROOT / "scripts" / "verify_phase5_sources.py",
        ROOT / "scripts" / "materialize_phase5_legal_snapshot.py",
        ROOT / "scripts" / "validate_phase5_legal_snapshot.py",
        ROOT / "scripts" / "generate_phase5_docs.py",
        PHASE5 / "legal_context_overlay_v1.json",
        PHASE5 / "source_registry_v1.json",
        PHASE5 / "source_metadata.json",
        PHASE5 / "jurisdiction_metadata.json",
        PHASE5 / "primary_evidence.jsonl",
        PHASE5 / "legal_queries.jsonl",
        PHASE5 / "legal_decisions.jsonl",
        PHASE5 / "global_context" / "who_road_safety_2023_context_v1.csv",
        PHASE5 / "global_context" / "who_road_safety_2023_acquisition_manifest.json",
        PHASE5 / "global_context" / "who_road_safety_2023_collection_failures.jsonl",
        COVERAGE,
        SNAPSHOT,
        ROOT / "docs" / "PHASE_5_LEGAL_REVIEW.md",
        ROOT / "docs" / "PHASE_5_COVERAGE.md",
        ROOT / "docs" / "PHASE_5_SOURCES.md",
        ROOT / "docs" / "LEGAL_DATA_CARD.md",
    ]
    manifest = {
        "schema_version": "phase5-legal-hash-manifest-v1",
        "snapshot_id": "phase5-legal-snapshot-v1",
        "files": {relative(path): digest(path) for path in hash_targets},
        "self_hash_excluded": True,
    }
    write(HASHES, manifest)
    print(f"Finalized Phase 5 snapshot: {coverage['query_count']} decisions; {coverage['decision_status_counts']}")


if __name__ == "__main__":
    main()
