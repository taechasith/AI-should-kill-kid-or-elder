# Phase 7 population-sampled execution report

Status: `COMPLETE_WITH_FROZEN_LEGAL_SCOPE_LIMITATION`

The amended `phase7-psb-v1` execution observed all 60 frozen probability-sample
units and preserved 279 pre-amendment certainty observations. The finite
provider-response population remains 4,104 rows; the full manifest remains
5,454 rows with 1,350 C3 `not_applicable` rows. This report does not claim a
census of the provider population.

- Sample terminal / unresolved: 60 / 0
- Provider attempts in the sampled execution: 60 HTTP 200, 18 HTTP 429, 12
  HTTP 503
- Spend: USD 0.00; THB 0.00
- Sampling design: stratified SRSWOR by model × condition
- Primary estimator: Horvitz--Thompson with certainty units and sampled-unit
  inclusion weights
- Primary machine-scored estimate: valid allowlisted-action rate = 0.8238;
  approximate 95% interval = [0.7340, 0.9136]

This interval uses the frozen stratified finite-population variance estimator.
The frozen Phase 5 action-level legal labels are `NOT_DETERMINED`; therefore
prohibited-action selection, road-compliance, and unsupported-legal-claim rates
are not estimable from this snapshot and are not reported.

Validation passed: sample invariants, terminal uniqueness, raw-response hashes,
parser outputs, structural Phase 4 input-package joins, Phase 5 hashes, `pip
check`, and 100 repository tests. The machine-readable report is
`data/model_benchmark/phase7_population_sample_v1/reports/phase7_psb_v1_execution_report.json`.
