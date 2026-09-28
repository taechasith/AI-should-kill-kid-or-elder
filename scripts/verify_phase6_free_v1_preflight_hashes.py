"""Verify the hash manifest for the zero-cost Phase 6 preflight."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASH_PATH = ROOT / "data" / "model_benchmark" / "phase6_free_v1" / "hashes" / "phase6_free_v1_preflight_sha256.json"


def verify() -> dict[str, object]:
    manifest = json.loads(HASH_PATH.read_text(encoding="utf-8"))
    if manifest.get("self_hash_excluded") is not True:
        raise ValueError("Phase 6 free preflight hash manifest must exclude itself")
    mismatches: list[str] = []
    for relative, expected in manifest["files"].items():
        path = ROOT / relative
        actual = sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != expected:
            mismatches.append(relative)
    if mismatches:
        raise ValueError("Phase 6 free preflight hash mismatch: " + ", ".join(mismatches))
    return manifest


if __name__ == "__main__":
    manifest = verify()
    print(f"Phase 6 free preflight hashes: verified {len(manifest['files'])} files")
