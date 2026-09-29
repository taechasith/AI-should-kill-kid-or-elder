# Phase 7 payload-equivalence and quota audit

Status: `NO_PROVIDER_CALL_AUDIT_COMPLETE`. The audit covers the 4,087 rows
still pending after checkpoint `d35fd12`; it made zero provider requests.

## Preserved 429 evidence

| Provider / model | Derived classification | Reset evidence | Interpretation |
| --- | --- | --- | --- |
| Gemini / `gemini-3.5-flash` | `FREE_MINUTE_REQUEST_LIMIT` | `retryDelay: 29s`; `GenerateRequestsPerMinutePerProjectPerModel-FreeTier`; limit 5 | a documented free-tier per-minute request quota, not evidence of a daily limit |
| Groq / `qwen/qwen3.8-27b` | `FREE_MINUTE_TOKEN_LIMIT` | error states input-tokens-per-minute limit 7,000 and retry after 24.471 seconds | a short-term input-token limit, not evidence of a daily limit |

The historical attempts remain immutable. The original runner did incorrectly
map every HTTP 429 to `FREE_QUOTA_EXHAUSTED` and used one provider-wide stop;
that is insufficient for model-specific short-term limits. It used Python
`urllib`, which has no automatic retry behavior; each persisted attempt maps to
one actual HTTP request. Future executor records will retain the sanitized
rate-limit headers and derived quota classification.

## Model-visible payload equivalence

Of 4,087 pending rows, 4,075 canonical request-payload hashes are unique.
There are 12 duplicate equivalence classes, each of size two (12 additional
rows). The audit excludes only filesystem/run bookkeeping by hashing the exact
provider body. Duplicates arise from coincident randomized candidate-action
orders under otherwise identical scene, condition, jurisdiction, and model
input; two classes span Gemini slots because model selection is endpoint-level,
not visible in the image/text body. They are retained: they are planned model
repetitions, not a basis for silent deduplication or a manifest change.

## Execution strategy

Use independent model-route queues. On a 429, persist the raw body, sanitized
headers, and derived short-term classification; defer only that route until its
provider-supplied reset delay. Continue other routes without busy-looping.
No daily reset is inferred from the available evidence. Free-plan quota and the
USD 0 / THB 0 constraint remain mandatory.

## Offline work

Phase 4/5 join validators, analysis/figure code using explicitly synthetic
fixtures, data dictionary, benchmark-card skeleton, and reproduction scripts
can proceed without new provider calls. A quota-constrained replacement study
is not activated: it would not complete the frozen full manifest, and is not
scientifically necessary until actual free-quota delay is publication-critical.
