# Phase 7 population-sampling analysis plan

Population: 4,104 frozen provider-evaluable rows. The 5,454-row manifest is
reported separately; its 1,350 C3 `not_applicable` rows are never provider
responses or errors.

Primary estimands, only when deterministic frozen scoring is available, are
row-weighted benchmark-population rates of prohibited-action selection,
valid-action selection, physical feasibility, collision-selected action,
road compliance, unsupported legal claim, and invalid output. Per-model and
per-condition estimates are reported only with their actual design-based
uncertainty. Jurisdiction-specific estimates are not presumed precise.

The `phase7-psb-v1` primary sample is stratified SRSWOR by model and condition.
For each sampled unit in stratum `h`, `pi_i = n_h/N_h` and `w_i=1/pi_i`.
Pre-amendment completed rows have `pi_i=1`. The analysis reports HT estimates,
finite-population-corrected stratified variance, 95% intervals, sampling
fraction, weights, and effective sample size where meaningful. No unweighted
Wald interval is used.

Prospective worst-case (`p=.5`) normal-approximation half-widths for a simple
random sample from 4,104, shown only for planning, are approximately: n=60,
12.5 percentage points; n=100, 9.7; n=150, 7.9; n=200, 6.8; n=300, 5.5.
Actual stratification, certainty units, and outcome variation determine the
reported uncertainty; these values do not promise precision.

Paired C0–C1, C1–C2, C2–C4, legal-difference, and legal-equivalent-control
contrasts are a separate objective. Contrast-only rows are marked and excluded
from population prevalence estimators. There is no outcome-dependent
sequential stopping. Phase 8 must distinguish probability-sampled rate
inference, certainty observations, and limited paired contrast inference.

Before any new execution, run the sample validator and all tests, hash and
commit the generated manifest, and obtain separate explicit execution
authorization. Budget remains USD 0.00 / THB 0.00.
