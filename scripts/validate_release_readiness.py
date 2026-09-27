from __future__ import annotations
import json
from pathlib import Path
from geosave.release_readiness import assess
print(json.dumps(assess(Path(__file__).resolve().parents[1]),indent=2))
