# Phase 6 free v1 pilot result

Status: `BLOCKED_FROZEN_PANEL`

The separate zero-cost access preflight succeeded: the account owner attested
to a billing-disabled Gemini Free Tier and Groq Free Plan, and authenticated
metadata checks listed all three frozen model IDs. The frozen three-route pilot
then made three generation requests. Each failed and received its one permitted
retry using the same model ID, image, prompt, condition, action order, legal
snapshot, and zero-cost policy.

| Frozen route | Initial result | Retry result | Gate result |
| --- | --- | --- | --- |
| `gemini-3.6-flash` | transport timeout | HTTP 200, malformed truncated JSON | failed |
| `gemini-2.5-flash-lite` | HTTP 404 | HTTP 404; provider states it is unavailable to new users | failed |
| `qwen/qwen3.8-27b` | HTTP 200, output did not meet the strict contract | same result | failed |

The provider responses and error envelopes are preserved append-only under
`data/model_benchmark/phase6_free_v1/`. The pilot contains six attempt records,
four raw response/error files, and three normalized invalid records. There are
zero valid decisions, zero completed pilot rows, and no manually generated
model response.

Run `python scripts/validate_phase6_free_pilot.py` to recompute the exact
three-row/two-attempt accounting and SHA-256 references. The resulting
`data/validation/phase6_free_v1_pilot_validation.json` records
`BLOCKED_FROZEN_PANEL` without mutating the prior Phase 6 dry-run artifacts.

The frozen `phase6-free-v1` panel cannot pass. Its Gemini 2.5 route is
unavailable to the current account, and all retries are exhausted. A future
attempt needs a new explicitly authorized model panel, manifest, and version;
it must preserve this failed pilot unchanged.
