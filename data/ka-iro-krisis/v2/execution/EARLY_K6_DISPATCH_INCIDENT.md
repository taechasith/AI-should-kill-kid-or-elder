# K6 execution-order incident

At 2026-10-02 UTC, the first IDE-only runner release sorted K5 and K6 together by their independently frozen execution keys. Before the defect was detected it preserved four explicit provider attempts: two terminal K5 observations, one K5 HTTP 503 attempt, and one terminal K6 observation. No selection, prompt, payload, model, scientific input, K3 outcome, or analysis rule was changed using any response.

The runner was stopped immediately. All original attempt ledgers and raw responses remain immutable. The scheduler was then corrected to dispatch only K5 while any K5 observation remains non-terminal; it will dispatch additional K6 observations only after K5 terminal accounting completes. The one already-terminal K6 observation remains part of its frozen K6 manifest and is never regenerated.
