# Phase 8A Reproducibility

Run offline from the repository root:

```text
python scripts/build_phase8a_input_manifest.py
python scripts/run_phase8a_analysis.py
python scripts/generate_phase8a_docs.py
python scripts/validate_phase8a_analysis.py
```

These commands do not read environment secrets or make provider/network calls. The input builder fails closed when a frozen hash or selected raw-response reference disagrees with its provenance. The validator checks recovered Phase 7 accounting, duplicate IDs, the historical valid-action estimate, physical join cardinality, legal blocking, and output determinism.
