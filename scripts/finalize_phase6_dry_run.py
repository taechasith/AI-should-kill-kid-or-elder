"""Hash the validated Phase 6 offline dry-run without claiming completion."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_interface import canonical_json_bytes

try:  # Supports both `python scripts/...` and package import under pytest.
    from scripts.validate_phase6_dry_run import validate
except ModuleNotFoundError:  # pragma: no cover - exercised by direct script use.
    from validate_phase6_dry_run import validate


HASH_PATH = ROOT / "data" / "model_benchmark" / "phase6" / "hashes" / "phase6_dry_run_v1_sha256.json"
INPUT_ROOT = ROOT / "data" / "model_inputs" / "phase6" / "phase6_model_interface_v1"


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _targets() -> list[Path]:
    fixed = [
        ROOT / "configs" / "experiments" / "phase6_model_interface_dry_run_v1.json",
        ROOT / "configs" / "models" / "phase6_model_registry_dry_run_v1.json",
        ROOT / "schemas" / "v1" / "phase6_model_decision.schema.json",
        ROOT / "prompts" / "phase6" / "decision_prompt_v1.md",
        ROOT / "geosave" / "model_adapters.py",
        ROOT / "geosave" / "phase6_inputs.py",
        ROOT / "geosave" / "phase6_interface.py",
        ROOT / "geosave" / "phase6_prompts.py",
        ROOT / "scripts" / "build_phase6_dry_run.py",
        ROOT / "scripts" / "validate_phase6_dry_run.py",
        ROOT / "scripts" / "finalize_phase6_dry_run.py",
        ROOT / "scripts" / "verify_phase6_dry_run_hashes.py",
        ROOT / "data" / "model_benchmark" / "phase6" / "manifests" / "phase6_dry_run_v1.json",
        ROOT / "data" / "model_benchmark" / "phase6" / "manifests" / "phase6_pilot_dry_run_v1.json",
        ROOT / "data" / "model_benchmark" / "phase6" / "phase6_dry_run_cost_estimate_v1.json",
        ROOT / "data" / "validation" / "phase6_dry_run_validation_v1.json",
        ROOT / "data" / "legal" / "phase5" / "hashes" / "phase5_legal_snapshot_v1_sha256.json",
        ROOT / "docs" / "PHASE_6_MODEL_INTERFACE.md",
        ROOT / "docs" / "PHASE_6_COST_ESTIMATE.md",
        ROOT / "docs" / "PHASE_6_BLOCKER.md",
    ]
    dynamic = sorted(path for path in INPUT_ROOT.rglob("*") if path.is_file())
    return fixed + dynamic


def finalize() -> dict[str, object]:
    validation = validate()
    if validation["validation_status"] != "passed":
        raise RuntimeError("Phase 6 dry-run validator did not pass")
    targets = _targets()
    missing = [path for path in targets if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Phase 6 hash target(s): " + ", ".join(str(path) for path in missing))
    files = {_relative(path): _sha256(path) for path in sorted(set(targets))}
    manifest = {
        "schema_version": "phase6-dry-run-hash-manifest-v1",
        "snapshot_id": "phase6-model-interface-v1-dry-run",
        "status": "FROZEN_DRY_RUN_PENDING_AUTHORIZATION",
        "phase4_canonical_commit": "d52baab",
        "phase5_snapshot_tag": "phase5-legal-snapshot-v1",
        "self_hash_excluded": True,
        "files": files,
    }
    HASH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASH_PATH.write_bytes(canonical_json_bytes(manifest))
    return manifest


if __name__ == "__main__":
    result = finalize()
    print(f"Phase 6 dry-run hashes: finalized {len(result['files'])} files")
