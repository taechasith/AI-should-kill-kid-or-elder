# GeoSAVE legal data card

## Snapshot

- Snapshot: `phase5-legal-snapshot-v1`
- Jurisdiction selection: 25 frozen ISO3 entries
- Query unit: jurisdiction × scenario × initial speed × candidate action
- Query count: 900
- Physical dependency: immutable `commonroad-pilot-v1`; no physical result was
  modified or re-run for this legal snapshot.

## Layers

**Global context:** WHO *Global status report on road safety 2023* profiles.
The collector retrieved 172 country/territory profiles, with
62 explicit unavailable or unparseable attempts.
WHO fields are descriptive context and cannot establish candidate-action
legality.

**Deep-Law:** 25 official-source index records with provision locators, source
language, scope, retrieval state, and two-pass verification history. A missing
or access-limited source is kept explicit.

## Status semantics

`NOT_DETERMINED` means the snapshot does not have sufficient domestic
primary-law evidence plus all material scenario predicates to classify that
action. It never means `PERMITTED`. `CONFLICTING_AUTHORITIES` is reserved for
contradictory applicable evidence, which was not emitted in this snapshot.

## Limitations

All action-level decisions in this snapshot are `NOT_DETERMINED`; therefore it
must not be used as a resolved-law benchmark or to estimate jurisdictional
compliance. It is a frozen, provenance-backed record of the current legal
context boundary. Source-language text controls, no human legal-expert review
is claimed, and international instruments do not become domestic law by
default.

## Disclaimer

The GeoSAVE legal dataset is a research representation of selected
road-traffic rules and is not legal advice. Laws change and may contain
jurisdiction-specific exceptions not represented in the benchmark. Verify
current primary sources before use outside research.
