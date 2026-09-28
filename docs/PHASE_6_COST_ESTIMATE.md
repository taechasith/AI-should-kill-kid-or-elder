# Phase 6 dry-run cost estimate

Status: planning estimate only; no provider call was made.

The frozen full dry-run manifest has 5,454 rows. C3 is unavailable for all
1,350 jurisdictional rows because the frozen legal snapshot has no retained
action-level evidence text. The remaining 4,104 rows are the maximum eligible
provider calls for three models and three repeats. The stratified pilot has 36
eligible calls, one repeat each.

The estimate uses a conservative planning allowance of 2,000 input tokens and
500 output tokens per request, including one 512×512 image. It does not claim
that every provider bills images identically; actual provider-reported token
usage must be preserved if execution is authorized.

| Model | Pilot estimate | Full estimate | Full worst case with one retry per request |
| --- | ---: | ---: | ---: |
| `gpt-4.1-2025-04-14` | USD 0.096 | USD 10.944 | USD 21.888 |
| `claude-sonnet-5` | USD 0.108 | USD 12.312 | USD 24.624 |
| `mistral-large-2512` | USD 0.021 | USD 2.394 | USD 4.788 |
| **Total** | **USD 0.225** | **USD 25.650** | **USD 51.300** |

These values come from the dated pricing fields and official-source URLs in
`configs/models/phase6_model_registry_dry_run_v1.json`; they are not a promise
of current or future price, account eligibility, image-token accounting, or
available quota. No search, browser, retrieval, or tool use is budgeted for
benchmark model requests because the benchmark is closed-book.

The machine-readable calculation is
`data/model_benchmark/phase6/phase6_dry_run_cost_estimate_v1.json`.
