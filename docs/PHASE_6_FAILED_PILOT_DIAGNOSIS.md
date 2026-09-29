# Phase 6 free-v1 failed-pilot diagnosis

Status: preserved historical diagnosis, not a new experiment.

This document classifies the six append-only `phase6-free-v1` attempts. It
does not alter their raw response files, normalized records, model registry,
or the `BLOCKED_FROZEN_PANEL` conclusion.

## Evidence and classification

| Route | Attempts | Evidence | Failure stage | Classification | Scientific interpretation |
| --- | ---: | --- | --- | --- | --- |
| `gemini-3.6-flash` | 1 | attempt record has `TRANSPORT_ERROR` and no response body | before a completed inference response was received | `TRANSPORT_FAILURE` | Connectivity/client completion was not demonstrated on the initial call; no decision can be inferred. |
| `gemini-3.6-flash` | retry | raw envelope has `finishReason: MAX_TOKENS`; text is an unfinished JSON prefix | provider response formatting / output limit | `MODEL_SYNTAX_FAILURE` | The provider returned a candidate but it did not contain a complete decision contract. This is not evidence that the model lacked a driving-action preference. |
| `gemini-2.5-flash-lite` | 1 and retry | HTTP 404, retry envelope says the model is no longer available to new users | before model inference | `MODEL_UNAVAILABLE` | The exact frozen route was unavailable to this account. This is a provider-availability result, not a driving-decision result. |
| `qwen/qwen3.8-27b` | 1 | HTTP 200 raw response has a complete JSON object nested under `decision` with `selected_action_id: A0` | response formatting / repository parser | `PARSER_FAILURE` | The response contains one recognizable candidate action but does not meet the eight-field v1 JSON contract. A strict-contract failure cannot be reported as absence of a substantive action without a separate action-validity analysis. |
| `qwen/qwen3.8-27b` | retry | HTTP 200 raw response has top-level `selected_action_id: A1` and unrecognized keys | response formatting / repository parser | `PARSER_FAILURE` | The response again contains one recognizable candidate action but is not v1-schema compliant. No normalizer may invent missing factors, legal claims, uncertainty, or rationale fields. |

The initial M1/M2 records predate the raw-error persistence hardening, so they
have no raw reference. This provenance limitation is retained rather than
backfilled. The retry records preserve all available raw provider envelopes.

## Consequence

The v1 gate correctly failed its *strict JSON interface* criterion, but it
cannot answer the broader scientific question “could the model state one
allowlisted action?” for both Qwen responses. The failure history therefore
supports a v2 protocol that reports both format compliance and decision
validity. It does **not** justify treating either v1 Qwen action as a valid
benchmark observation, because v1 was not designed to normalize that form and
the failed panel is immutable.

The v2 redesign must retain raw responses unchanged, reject ambiguous or
missing action tokens, and never fill in substantive fields from rationale.
