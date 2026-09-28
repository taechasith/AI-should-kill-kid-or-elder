"""Hash the validated zero-cost Phase 6 preflight without enabling execution."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_interface import canonical_json_bytes

try:
    from scripts.validate_phase6_free_v1_preflight import validate
    from scripts.verify_phase6_dry_run_hashes import verify as verify_prior_dry_run
except ModuleNotFoundError:  # pragma: no cover
    from validate_phase6_free_v1_preflight import validate
    from verify_phase6_dry_run_hashes import verify as verify_prior_dry_run


HASH_PATH = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "hashes" / "phase6_free_v1_preflight_sha256.json"
INPUT_ROOT = ROOT / "data" / "model_inputs" / "phase6" / "phase6_model_interface_v1"


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _targets() -> list[Path]:
    fixed = [
        ROOT / "configs" / "experiments" / "phase6_free_v1_preflight.json",
        ROOT / "configs" / "models" / "phase6_free_v1_candidate_registry.json",
        ROOT / "schemas" / "v1" / "phase6_model_decision.schema.json",
        ROOT / "prompts" / "phase6" / "decision_prompt_v1.md",
        ROOT / "geosave" / "phase6_free_adapters.py",
        ROOT / "geosave" / "phase6_free_guard.py",
        ROOT / "geosave" / "phase6_interface.py",
        ROOT / "geosave" / "phase6_prompts.py",
        ROOT / "scripts" / "build_phase6_free_v1_preflight.py",
        ROOT / "scripts" / "validate_phase6_free_v1_preflight.py",
        ROOT / "scripts" / "finalize_phase6_free_v1_preflight.py",
        ROOT / "scripts" / "verify_phase6_free_v1_preflight_hashes.py",
        ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "manifests" / "phase6_free_v1_preflight_manifest.json",
        ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "manifests" / "phase6_free_v1_pilot_manifest.json",
        ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "phase6_free_v1_cost_policy.json",
        ROOT / "data" / "validation" / "phase6_free_v1_preflight_validation.json",
        ROOT / "data" / "model_benchmark" / "phase6" / "hashes" / "phase6_dry_run_v1_sha256.json",
        ROOT / "docs" / "PHASE_6_ZERO_COST_POLICY.md",
        ROOT / "docs" / "PHASE_6_FREE_V1_PREFLIGHT.md",
    ]
    return fixed + sorted(path for path in INPUT_ROOT.rglob("*") if path.is_file())


def finalize() -> dict[str, object]:
    validation = validate()
    if validation["validation_status"] != "passed":
        raise RuntimeError("Phase 6 free preflight validator did not pass")
    verify_prior_dry_run()
    targets = _targets()
    missing = [path for path in targets if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Phase 6 free preflight hash target(s): " + ", ".join(str(path) for path in missing))
    files = {_relative(path): _sha256(path) for path in sorted(set(targets))}
    manifest = {
        "schema_version": "phase6-free-preflight-hash-manifest-v1",
        "snapshot_id": "phase6-free-v1-preflight",
        "status": "PREFLIGHT_PENDING_CREDENTIALS",
        "phase4_canonical_commit": "d52baab",
        "phase5_snapshot_tag": "phase5-legal-snapshot-v1",
        "prior_phase6_dry_run_commit": "17b140206b6e147ca391fc587992aac57357fb96",
        "self_hash_excluded": True,
        "files": files,
    }
    HASH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASH_PATH.write_bytes(canonical_json_bytes(manifest))
    return manifest


if __name__ == "__main__":
    result = finalize()
    print(f"Phase 6 free preflight hashes: finalized {len(result['files'])} files")
