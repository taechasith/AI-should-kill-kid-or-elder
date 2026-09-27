# Phase 5 deterministic GeoSAVE baseline

## Purpose and contract

GeoSAVE is a deterministic overlay over immutable Phase 4 physical inputs. Its pipeline is physical candidate action, feasibility, physical-risk characterization, jurisdiction-specific legal evidence, legal-status classification, safety-law relationship, evidence sufficiency/uncertainty, and structured output. These stages are never collapsed into a scalar score.

The baseline consumes explicit physical outcomes and explicitly supplied legal evidence. It does not collect, infer, or invent law; it contains no model call or demographic value weighting.

## Legal evidence and decisions

`LegalEvidence`, `LegalQuery`, and `LegalDecision` are frozen dependency-free dataclasses. Evidence retains jurisdiction (including subnational region), authority/source type, dates, language/original and translated text, provision, normalized rule, scenario/action conditions, exceptions, status supported, strength, citation, and optional treaty-instrument applicability. Queries require jurisdiction, scenario, action, road/physical context, conditions, and an evaluation date. Decisions retain evidence IDs, status, conditions, exceptions, evidence sufficiency, reason code, and human-review flag.

Legal status values are `PERMITTED`, `PROHIBITED`, `REQUIRED`, `CONDITIONALLY_PERMITTED`, `NOT_DETERMINED`, and `CONFLICTING_AUTHORITIES`. Absence of evidence is `NOT_DETERMINED`, never permission. Sufficiency values are `SUFFICIENT_PRIMARY`, `SUFFICIENT_OFFICIAL_SECONDARY`, `PARTIAL`, `CONFLICTING`, `INSUFFICIENT`, and `NO_EVIDENCE`.

## Source hierarchy, time, and jurisdiction

Future evidence collection prefers statutes/road codes, regulations, official legal databases, binding decisions, and applicable treaty instruments. WHO and other official intergovernmental datasets may support discovery or context but cannot silently replace operative primary evidence. UNECE/Vienna/WP.1/WP.29 instruments are represented separately and require explicit applicability.

The classifier filters jurisdiction, subnational reach, scenario/action relation, effective dates, and supplied conditions before classifying. Contradictory applicable evidence returns `CONFLICTING_AUTHORITIES` with human review rather than applying an invented universal conflict hierarchy.

## Safety-law relationship and limitations

Physical-risk classification and legality remain separate. The existing baseline preserves physical infeasibility, safety-law conflict, safe-but-prohibited, unsafe-but-permitted, and legality-not-determined states without claiming survival, injury, or human worth. The deterministic baseline is not legal advice; classifications depend on sourced evidence, local law may differ, treaty applicability varies, and expert review may be required.

Only synthetic `TEST-JURISDICTION-*` fixtures are used in this gate. No real-world law dataset, global collection, AI benchmark, or psychological analysis is included.
