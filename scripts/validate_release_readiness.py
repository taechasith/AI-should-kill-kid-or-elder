from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from geosave.release_readiness import assess
print(json.dumps(assess(ROOT),indent=2))
