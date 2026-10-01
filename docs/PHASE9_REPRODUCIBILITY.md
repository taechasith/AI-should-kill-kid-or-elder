# Phase 9 Reproducibility

Phase 9 requires no network, provider, API, simulation, or random sampling operation. From the repository root:

```text
python scripts/build_phase9_scaffold.py
python scripts/build_phase9_synthesis.py
python scripts/freeze_phase9_hashes.py
python scripts/validate_phase9_synthesis.py
```

Inputs are the frozen Phase 8A results and hash manifest, with the required Phase 8A hash-manifest digest recorded in `phase9_input_manifest.json`. The scripts use Python standard-library modules only. The Phase 7 sampling RNG seed remains a frozen input (`20260930`); Phase 9 does not resample.
