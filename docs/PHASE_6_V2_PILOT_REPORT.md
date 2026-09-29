# Phase 6 literature-v2 pilot report

Status: `SCIENTIFICALLY_USABLE_INTERFACE_GATE_PASSED`.

The frozen three-call, closed-book image-plus-text pilot was executed on
2026-09-29 after a non-secret account-owner attestation of Free Tier / Free
Plan access, disabled billing, and available quota. The authorized budget was
USD 0.00 / THB 0.00. No billing action, tier upgrade, credit purchase, paid
fallback, search, grounding, retrieval, or tool use was requested by the
executor. Provider billing records were not returned by these API responses;
this report does not independently infer charges.

## Frozen execution inputs

The pre-generation execution manifest is
`data/validation/phase6_literature_v2_execution_manifest_sha256.json`. It
fixes the v2 panel, line protocol, canonical action display order, input
package `PED-CROSS-001__V030`, condition `C2`, Argentina legal context, and
the exactly-three-call bound. Raw provider envelopes and attempt records are
append-only under `data/model_benchmark/phase6_literature_v2/`.

## Observed pilot outcomes

| Slot | Provider / exact model ID | HTTP | Strict JSON | Line-format compliant | Normalization | Exact allowlisted action | Outcome |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| M1 | Google Gemini API / `gemini-3.5-flash` | 200 | false | false | false | true (`A1`) | valid action token; response truncated before full protocol completion |
| M2 | Google Gemini API / `gemini-3.5-flash-lite` | 200 | false | true | true | true (`A0`) | complete line-protocol response |
| M3 | Groq / `qwen/qwen3.8-27b` | 200 | false | true | true | true (`A6`) | complete line-protocol response |

`native_schema_success` is `null` for all rows: native schema mode was not
requested because the frozen v2 interface is the plain-text decision-line
protocol. `strict_json_success` is false for every row for the same reason;
it is retained as a separately observed format measure and was not used to
reject a substantively unambiguous action.

## Gate decision

All three rows provided exactly one unambiguous allowlisted `ACTION` token.
The pilot therefore passes the Phase 6 substantive decision-interface gate.
Line-protocol normalization succeeded for two of three rows; the remaining
raw response remains immutable and is classified as a format/normalization
failure only. These pilot action selections are interface observations, not
benchmark performance, safety, or legal results.

No fourth generation call was made. Phase 7 is not authorized by this pilot
authorization and has not begun.
