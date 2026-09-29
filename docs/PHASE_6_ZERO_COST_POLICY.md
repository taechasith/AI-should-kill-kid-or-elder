# Phase 6 zero-cost execution policy

Status: `PREFLIGHT_PENDING_CREDENTIALS`

This is a separately versioned Phase 6 execution candidate, `phase6-free-v1`.
It does not alter the earlier blocked dry-run at commit
`17b140206b6e147ca391fc587992aac57357fb96`, which remains preserved as
provenance. No Phase 6 model response existed before this candidate panel was
selected.

## Frozen monetary boundary

| Policy field | Value |
| --- | --- |
| Budget mode | `FREE_ONLY` |
| Maximum authorized USD | `0.00` |
| Maximum authorized THB | `0.00` |
| Paid fallback | prohibited |
| Provider upgrade | prohibited |
| Credit purchase | prohibited |
| Automatic billing | prohibited |
| Provider grounding, web, search, retrieval, tools | prohibited |

Any provider indication that a request requires billing activation, paid
credits, a card, a paid tier, pay-as-you-go, or a paid fallback terminates that
provider's execution. It does not authorize a workaround or a charge.

## Pre-result candidate panel

| Slot | Provider | Exact model ID | Required access |
| --- | --- | --- | --- |
| M1 | Google Gemini API | `gemini-3.6-flash` | Google Free Tier |
| M2 | Google Gemini API | `gemini-2.5-flash-lite` | Google Free Tier |
| M3 | Groq | `qwen/qwen3.8-27b` | Groq Free Plan |

The panel was re-frozen before any model response because the experiment has a
USD 0 compute/API budget, not because of observed model performance. Google
currently documents Gemini 3.6 Flash and Gemini 2.5 Flash-Lite free-tier
pricing and multimodal support; it also documents that 2.5-model availability
can be limited to accounts that have used those models previously. Groq
currently documents image input for Qwen 3.8 27B and publishes Free Plan rate
limits. These statements are provider documentation, not proof of this
project's account access.

Official sources consulted on 2026-09-28:

- [Gemini models](https://ai.google.dev/gemini-api/docs/models)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Groq vision models](https://console.groq.com/docs/vision)
- [Groq rate limits](https://console.groq.com/docs/rate-limits)

## Required live gate

The registry stays non-executable until both secret names are present only in a
secret store:

```text
GEMINI_API_KEY
GROQ_API_KEY
```

Their values must never be printed, committed, stored in a manifest, or placed
in `.env.example`. Before any request, record only the provider, exact model
ID, free tier/plan, billing-disabled result, account rate-limit metadata, and
verification timestamp. A credential's presence alone is insufficient.

Once those checks pass, exactly three closed-book multimodal capability-pilot
requests are allowed—one per model. Each must accept the frozen image and text,
return parseable text, preserve its raw response, record model/provider IDs,
and demonstrate no monetary charge. Only then may a new executable registry and
main benchmark manifest be frozen.

`429` or quota exhaustion is `FREE_QUOTA_EXHAUSTED`: persist completed work,
stop that provider, and resume in a future free-quota window. Never pay to
resume.

The capability pilot permits one retry per initial row only for a transport
error, a provider HTTP error, or a malformed response. A retry uses the same
model ID, frozen image, prompt, condition, action order, and free-only policy.
It receives a distinct append-only attempt ID; it must never overwrite the
initial attempt or substitute a model.

## Data-use boundary

Gemini's Free Tier documentation states that content may be used to improve
Google products. The permitted benchmark payload is restricted to controlled
simulation scenes, public legal evidence, and structured research data. It
must never contain credentials, personal confidential data, or private source
material. Applicable Groq account terms will be recorded at live preflight.
