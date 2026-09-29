"""Verify Phase 6 literature-v2 pre-pilot frozen artifacts."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "validation" / "phase6_literature_v2_preflight_sha256.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "LITERATURE_GATE_FROZEN_PENDING_LIVE_PREFLIGHT":
        raise SystemExit("Phase 6 literature-v2 manifest status is invalid")
    if manifest.get("failed_v1_panel_preserved") is not True:
        raise SystemExit("Phase 6 literature-v2 manifest does not preserve v1")
    for relative, expected in manifest["files"].items():
        actual = sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"hash mismatch: {relative}")
    print(f"Phase 6 literature-v2 hashes: verified {len(manifest['files'])} files")


if __name__ == "__main__":
    main()
