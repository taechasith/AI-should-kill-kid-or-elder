"""Create the K3 SHA-256 manifest from canonical physical artifacts."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "ka-iro-krisis" / "v2" / "physical"
def main() -> None:
    files = sorted(x for x in BASE.rglob("*") if x.is_file() and x.name != "sha256_manifest.json")
    records = [{"path": x.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(x.read_bytes()).hexdigest()} for x in files]
    path = BASE / "sha256_manifest.json"
    path.write_text(json.dumps({"algorithm": "sha256", "file_count": len(records), "files": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": len(records), "manifest": path.as_posix()}))
if __name__ == "__main__": main()
