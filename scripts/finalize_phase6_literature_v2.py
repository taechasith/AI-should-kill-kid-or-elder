"""Write the append-only Phase 6 literature-v2 pre-pilot hash manifest."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "validation" / "phase6_literature_v2_preflight_sha256.json"
FILES = (
    "data/literature/phase6_literature_matrix.csv",
    "data/models/phase6_candidate_model_review.csv",
    "docs/LITERATURE_REVIEW_PHASE6.md",
    "docs/PHASE_6_GAP_ANALYSIS.md",
    "docs/PHASE_6_FAILED_PILOT_DIAGNOSIS.md",
    "docs/PHASE_6_INTERFACE_RATIONALE.md",
    "docs/PHASE_6_MODEL_SELECTION.md",
    "configs/models/phase6_literature_v2_candidate_registry.json",
    "configs/experiments/phase6_literature_v2_pilot.json",
    "prompts/phase6/decision_line_protocol_v2.md",
    "geosave/phase6_line_protocol.py",
    "scripts/probe_phase6_literature_v2_access.py",
    "tests/test_phase6_line_protocol.py",
    "tests/test_phase6_literature_v2_access_probe.py",
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, object]:
    missing = [item for item in FILES if not (ROOT / item).is_file()]
    if missing:
        raise SystemExit(f"missing frozen literature-v2 artifact(s): {missing}")
    return {
        "schema_version": "phase6-literature-v2-preflight-hash-manifest-v1",
        "snapshot_id": "phase6-literature-v2-preflight",
        "status": "LITERATURE_GATE_FROZEN_PENDING_LIVE_PREFLIGHT",
        "phase4_canonical_commit": "d52baab",
        "phase5_snapshot_tag": "phase5-legal-snapshot-v1",
        "failed_v1_panel_preserved": True,
        "files": {item: digest(ROOT / item) for item in FILES},
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_manifest(), sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Phase 6 literature-v2 hashes: finalized {len(FILES)} files")


if __name__ == "__main__":
    main()
