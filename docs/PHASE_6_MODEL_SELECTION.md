# Phase 6 literature-v2 model selection

Status: `LITERATURE_GATE_FROZEN_PENDING_LIVE_PREFLIGHT`.

The candidate registry is [phase6_literature_v2_candidate_registry.json](../configs/models/phase6_literature_v2_candidate_registry.json). The review table is [phase6_candidate_model_review.csv](../data/models/phase6_candidate_model_review.csv).

## Sampling frame

The study has a hard USD 0 / THB 0 API budget. The sampling frame is current, provider-documented free-access multimodal APIs available to the research account, not all frontier models. Candidates require text-plus-image input, a current exact identifier, reproducible API access, no browsing/grounding, plain-text output, and documented free access.

The proposed three-slot panel is:

1. `gemini-3.5-flash`;
2. `gemini-3.5-flash-lite`;
3. `qwen/qwen3.8-27b`.

This offers two model families and two providers. It is not a representative sample of every commercial or open-weight multimodal model. Google documents text-and-image input and structured output for 3.5 Flash-Lite and a free tier for 3.x Flash offerings. Groq documents image-plus-text support, JSON modes, and free-plan rate-limit listings for Qwen 3.8 27B. This establishes a candidate sampling frame only; live preflight must reconfirm account-specific access without generation.

## v1 separation

`gemini-2.5-flash-lite` is excluded because the preserved v1 retry reports it unavailable to new users. `gemini-3.6-flash` is excluded because its retry ended at `MAX_TOKENS`, and v2 uses the current 3.5 stable family with a plain-text line protocol. Qwen is retained for documented modality and provider diversity, not because of either v1 action.

No valid benchmark decision outputs from the failed v1 panel were used to select v2 models. The v1 history remains immutable.

## Stop rule

Before a v2 pilot, record non-generative availability for each exact route, account tier, billing-disabled state, quota status, and timestamp. If a route lacks free access, Phase 6 v2 is `NO-GO` under this panel. It must not be replaced after pilot execution begins; replacement needs a new versioned selection review.
