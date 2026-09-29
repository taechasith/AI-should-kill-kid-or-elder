# Phase 7 analysis plan

Status: `FROZEN_PENDING_MAIN_EXECUTION_AUTHORIZATION`. This plan was frozen
before any Phase 7 provider response exists.

The unit of analysis is the planned model-decision row, with paired comparisons
clustered by model, input package, jurisdiction, condition, and repeat. The
five deterministic Phase 4 seeds are not independent physical samples.

Primary outcomes: valid allowlisted action selection; selected-action collision
and trajectory-feasibility status after joining frozen Phase 4 data;
prohibited-action selection and `NOT_DETERMINED` handling after joining frozen
Phase 5 data. Secondary outcomes: road-boundary compliance, abstention,
invalid/format failure, jurisdiction and condition sensitivity, evidence use,
unsupported legal claims, safety-law conflict, and explanation-behavior
agreement.

The primary comparisons are C0–C2, C1–C2, C2–C4, and paired jurisdiction
changes at fixed scenario/speed/model/repeat. C3 is retained only as
`not_applicable` where frozen source text is unavailable and is never silently
treated as an executable row. Parse/format failure remains an outcome; it is
excluded only from action-dependent metrics and reported in every denominator.

Report paired changes, effect sizes, and 95% confidence intervals. Use McNemar
or exact/permutation tests for paired binary outcomes and cluster-aware
bootstrap intervals where applicable. Apply Benjamini–Hochberg correction
within the prespecified primary and secondary comparison families. Any result
outside this plan is labeled exploratory/post hoc. No result is interpreted as
model cognition, legal advice, human worth, injury, or fatality.
