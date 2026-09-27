# Phase 4 reproducibility

Phase 4 requires Linux x86_64 with Python 3.10 and the pinned packages in `requirements-commonroad-codespaces.txt`. GitHub Codespaces is the reference environment. GPU, CARLA, Docker, and native Windows CommonRoad execution are not required; the latter was historically blocked and Linux Codespaces resolved compatibility.

```bash
python scripts/verify_commonroad_environment.py
python -m pip check
python -m pytest -q
python scripts/generate_ks_validation.py
python scripts/finalize_commonroad_pilot.py validate
python scripts/finalize_commonroad_pilot.py summarize
python scripts/finalize_commonroad_pilot.py hash
python scripts/finalize_commonroad_pilot.py verify
```

The frozen physical source is commit `d52baab`; it must not be replaced by a rerun for summary generation. The canonical manifest is `data/simulator/commonroad/manifests/commonroad_pilot_v1.json` and the canonical data are the 180 corresponding outcome and trajectory artifacts. The 348 files/rows under `data/simulator/commonroad/attempts/` are retained debugging provenance and excluded from the analysis population.

For a fresh permitted execution only, generate the manifest before any outcomes and use the resumable runner:

```bash
python scripts/run_commonroad_pilot.py --write-manifest
python scripts/run_commonroad_pilot.py --execute
```

Do not use these commands to overwrite the frozen canonical pilot. Hash verification is the final integrity check.
