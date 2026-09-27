# Phase 5 Two-Level Legal Dataset Protocol

## Status

**Collection protocol frozen; evidence review not complete.** This document
does not claim that the 25 planned jurisdictions have been legally reviewed.
The existing `2026-09-27-pilot-v1` remains a two-record provenance pilot and
is not modified by this protocol.

## Dataset layers

### Global context layer

The broad layer is `WHO Global Road-Safety Context v1`, sourced from the WHO
*Global status report on road safety 2023: country and territory profiles*.
WHO reports profiles for 170 Member States and 2 territories and nearly 100
indicators per profile. Each Global Law Map value is a country-level,
source-attributed contextual indicator. It is not an operative traffic-law
interpretation and cannot determine whether a candidate driving action is
permitted, prohibited, or required.

### Deep-Law layer

`deep-law-v1` is a planned 25-jurisdiction, primary-law review subset. It
contains only rules relevant to the frozen Phase 4 action set and scenario
families: pedestrian priority, lane markings, overtaking,
collision-avoidance/necessity exceptions, and stopped or disabled vehicles.
The selection frame is in
`configs/legal/phase5_two_level_v1.json`; it is a review queue, not a claim of
legal coverage.

A reviewed rule must retain its official source URL and stable locator, source
language, retrieval date, effective-date state, scenario/action conditions,
translation method where required, review state, and uncertainty state. A
record may be added to the analytical Deep-Law snapshot only after those fields
are complete. Unavailable, ambiguous, stale, conflicting, or inapplicable law
must remain explicit and classify as `NOT_DETERMINED` (or a documented
conflict), never as permission.

## International layer

UNECE instruments are recorded separately as international regulatory context.
They are not domestic law by default. A Deep-Law decision may use such an
instrument only where its version and domestic applicability are explicitly
documented in the relevant rule record.

## Frozen boundaries

- WHO indicators may support descriptive global context and pre-specified
  exploratory association analysis only.
- WHO indicators may not substitute for primary law or imply an exception.
- No demographic attribute is a legal, safety, or human-value weight.
- Phase 4 physical data and `commonroad-pilot-v1` are immutable; later
  jurisdictional evaluation joins to those outcomes and never reruns physics.
- The Deep-Law subset is frozen only after source review and snapshot hashing.

## Completion evidence for Phase 5

Phase 5 is complete only when a versioned Global Law Map has source-level
provenance and explicit missingness, the selected Deep-Law subset has reviewed
primary-law records and a frozen manifest, all records validate, and the
resulting status classifications preserve unknown and conflict states. Until
then, this repository has a Phase 5 collection protocol and a two-record
pilot—not a completed legal benchmark.

## Disclaimer

The GeoSAVE legal dataset is a research representation of selected road-traffic
rules and is not legal advice. Laws change and may contain jurisdiction-specific
exceptions not represented in the benchmark. Verify current primary sources
before use outside research.
