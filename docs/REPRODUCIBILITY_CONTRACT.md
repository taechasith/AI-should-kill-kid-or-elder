# GeoSAVE Reproducibility Contract v1

This contract applies before collection or execution. Each artifact validates
against its matching document in `schemas/v1/`; `geosave.contracts` provides the
dependency-free enforcement used by the initial tests.

## Artifact identities

| Artifact | Required identity/provenance fields |
|---|---|
| Deep-Law rule | schema version, rule ID, ISO-3 jurisdiction, effective date when known (otherwise explicit null), retrieval date, category, status, source title/URL/type |
| Scenario | schema version, scenario ID/family/version, split, candidate actions |
| Physical outcome | schema version, scenario/variant/action/seed, physical metrics, completion/failure state |
| Model decision | run ID, scenario, ISO-3 country, law snapshot, model/revision, prompt, condition, seed, action order, raw/parsed status |
| Experiment config | experiment ID, law snapshot, scenario/jurisdiction/model sets, conditions, seed, repetitions |
| Frozen manifest | release, law snapshot, scenario set, models, commit, SHA-256 artifact map |

## Non-overwrite rule

Raw model outputs and frozen results are append-only/versioned. A correction,
new law snapshot, prompt revision, scenario edit, or changed experiment
configuration creates a new artifact version and manifest; it does not replace
the earlier record.

## Determinism rule

The canonical JSON serialization of a valid experiment configuration is hashed
with SHA-256. The same configuration must yield the same fingerprint; a changed
seed, model, scenario, prompt, condition, or law snapshot must yield a new one.
