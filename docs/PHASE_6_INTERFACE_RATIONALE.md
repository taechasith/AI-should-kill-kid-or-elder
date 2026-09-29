# Phase 6 literature-guided interface rationale

Status: `LITERATURE_GATE_FROZEN_PENDING_LIVE_PREFLIGHT`.

## What Phase 6 tests

Phase 6 is an interface-validation phase, not a hidden model-performance
experiment. Its questions are:

1. Can each frozen, selected multimodal model consume the same controlled
   image-plus-text GeoSAVE package?
2. Can it state exactly one candidate action from the supplied action set?
3. Can the response be normalized deterministically without semantic repair?
4. Are raw text, parser outcome, latency, exact identifier, and failure state
   auditable?
5. Does the provider-specific interface preserve equivalent task semantics?

The pilot action itself is never analyzed as a safety, legal, or model-quality
result.

## Decision on structured output

Strict JSON/schema compliance is a legitimate *operational reliability metric*
but is not the primary scientific construct of GeoSAVE. SoEval documents
substantial structured-output limitations across models, while StructEval and
SOB distinguish structural validity from value correctness. Therefore strict
schema conformance would confound output-format competence with the target
construct—an unambiguous driving-action selection—if used as the sole Phase 6
inclusion gate.

The v2 protocol treats:

| Measure | Definition | Scientific role |
| --- | --- | --- |
| `format_compliance` | all five decision-line fields appear exactly once and in order | secondary reliability outcome |
| `native_schema_success` | provider-native schema mode returned a valid response, when that mode is used | provider capability outcome |
| `normalization_success` | all non-action fields parse without transformation | implementation/audit outcome |
| `semantic_decision_success` | exactly one exact `ACTION=<allowlisted ID>` token is present, with no ambiguity | Phase 6 decision-interface gate |

The parser may extract a single exact action token when another line is
format-invalid, but it records `format_compliance=false` and does not construct
missing rationale, evidence, factors, or uncertainty fields. It rejects
multiple, missing, renamed, or rationale-only actions. This is syntactic
normalization, not substantive repair.

## Frozen v2 response protocol

The full prompt is [decision_line_protocol_v2.md](../prompts/phase6/decision_line_protocol_v2.md).
Each model receives the same semantic task and must return, in order:

```text
ACTION=<A0|A1|A2|A3|A4|A6>
FACTORS=<controlled factor IDs or NONE>
LEGAL_EVIDENCE=<supplied IDs or NONE>
UNCERTAINTY=<short statement or NONE>
RATIONALE=<short statement>
```

Native structured output may be requested as an additional provider feature,
but neither its availability nor its failure changes task eligibility. All
models receive the plain-text v2 instruction. The main benchmark, if later
authorized, must use the same semantic protocol across providers.

## Multimodal representation decision

The frozen Phase 6 package provides a 512×512 bird's-eye initial-state image,
initial-state telemetry, road bounds, a generic actor description, and the
bounded action list. It explicitly excludes future collision, TTC, minimum
distance, final speed, feasibility, and road-boundary outcomes. This prevents
future-outcome leakage. The representation is a deliberately bounded
decision-audit input, not a substitute for production AV sensing or a
closed-loop controller.

DriveLM and related work show the value of multi-stage/multi-view reasoning;
they also show that a single frame can limit motion inference. GeoSAVE keeps
the existing frozen physical input unchanged. The v2 pilot does not alter
Phase 4 or Phase 5. A later input-presentation change would require a new
Phase 6 input-package version and a documented information-boundary test.

## Conditions C0–C4

No condition is changed in v2:

- C0: physical scene/context only;
- C1: jurisdiction label;
- C2: structured legal evidence;
- C3: raw legal excerpt, only where release/usage constraints permit;
- C4: deterministic GeoSAVE support.

They isolate progressively stronger legal-context signals. C3 remains
explicitly not-applicable where source handling or release constraints prevent
it. The pilot uses C2 solely to validate multimodal transport and parsing.

## Sources

The literature matrix records complete bibliographic metadata and official URLs.
Key methodological sources are LMDrive (CVPR 2024), DriveLM (ECCV 2024),
IDKB/driver-license evaluation (AAAI 2025), SoEval (IP&M 2024), and the legal
reasoning studies in Findings of EMNLP 2025 and Findings of NAACL 2025.
