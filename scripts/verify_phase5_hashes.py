"""Recompute every Phase 5 snapshot digest without trusting the manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "legal" / "phase5" / "hashes" / "phase5_legal_snapshot_v1_sha256.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for relative, expected in manifest["files"].items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != expected:
            failures.append(relative)
    if failures:
        raise SystemExit("Phase 5 hash mismatch: " + ", ".join(failures))
    print(f"Phase 5 hashes: verified {len(manifest['files'])} files")


if __name__ == "__main__":
    main()
