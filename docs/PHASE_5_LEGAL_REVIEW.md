# Phase 5 legal review

## Frozen snapshot

`phase5-legal-snapshot-v1` freezes the legal-context overlay, 25-jurisdiction
source review, 900 legal queries, 900 decisions, global WHO context, and the
associated hash manifest. The snapshot is a research representation, not legal
advice or a claim of complete national traffic-law coverage.

## Verification method

Each frozen jurisdiction underwent two source passes: (1) source
discovery/extraction and (2) an independent retrieval attempt against the
official endpoint on 2026-09-28. This is **two-pass primary-source
verification**, not expert legal review. The second pass retrieved 13
of 25 endpoint bodies and recorded all remaining access limitations explicitly
(access_error: 4, empty_response: 1, http_error: 7, retrieved: 13).

## Action-level result boundary

All 900 action-level decisions are `NOT_DETERMINED`. The
frozen physical scenarios do not establish material legal predicates such as a
marked-crossing type, signal state, posted speed, lane-marking type, traffic
side, local jurisdiction, or a statutory exception. Those facts were not
invented to force a result. Consequently, this snapshot must not be reported as
a jurisdictional legality-rate comparison. It is an auditable uncertainty
result and a constraint on any later benchmark claim.

## Source hierarchy and language

Only official statutes, regulations, codes, or government legal databases were
retained as Deep-Law source candidates. Source-language text controls. No
machine translation is presented as official, and no action-level translation
claim is emitted in this snapshot. WHO data is global context only; UNECE
instruments remain international context unless domestic applicability is
recorded.

## Required next legal-scope version

A later snapshot can make action-level conclusions only by introducing a new,
versioned legal overlay that supplies the missing predicates and by repeating
source review. It must never mutate this snapshot or its hashes.
