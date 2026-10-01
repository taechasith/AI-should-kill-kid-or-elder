# Phase 8A Frozen Confirmatory Results

Generated only by `python scripts/run_phase8a_analysis.py` followed by `python scripts/generate_phase8a_docs.py`. All estimates are from frozen Phase 4–7 artifacts; no network, provider, or simulator operation is used.

## Accounting

| Quantity | Count |
| --- | ---: |
| Design-accounted Phase 7 rows | 5454 |
| Not applicable (C3) | 1350 |
| Provider-execution population | 4104 |
| Certainty observations | 279 |
| Probability-sample observations | 60 |
| Terminal analysis observations | 339 |
| Explicit actions | 323 |
| Valid allowlisted actions | 323 |
| Phase 4-linked valid actions | 323 |

## Interface reliability

The primary valid-action estimate is 82.38% (approximate 95% CI 73.40%–91.36%); it is a Horvitz–Thompson finite-population estimate with stratified SRSWOR variance and finite-population correction. Strict JSON is separately 62.37%. A valid explicit action is not treated as synonymous with strict JSON.

## Weighted selected-action joint rates

| Action | Weighted rate | Approximate 95% CI | Raw selected observations |
| --- | ---: | ---: | ---: |
| A0 | 6.86% | 1.67%–12.05% | 99 |
| A1 | 42.27% | 29.81%–54.73% | 172 |
| A2 | 30.48% | 19.58%–41.37% | 30 |
| A3 | 0.41% | 0.23%–0.60% | 11 |
| A4 | 0.10% | 0.10%–0.10% | 4 |
| A6 | 2.27% | 0.00%–6.40% | 7 |

Each action rate is joint with a valid allowlisted action and therefore preserves invalid/no-action observations rather than silently reassigning them.

## Physical linkage

Physical result identifiers `P8A-PHYSICAL-*` link a valid selected action to the existing Phase 4 scenario/speed/action cell and calculate an arithmetic mean across its five frozen seeds. `road_compliant` remains a Phase 4 map/road-boundary metric, not a jurisdictional legal conclusion. Conditional clearance is descriptive because no ratio-variance estimator was frozen.

| Metric | Estimate | Status |
| --- | ---: | --- |
| valid_action_and_collision_mean | 0.254094 | ESTIMABLE |
| valid_action_and_feasible_mean | 0.818713 | ESTIMABLE |
| valid_action_and_road_compliant_mean | 0.820663 | ESTIMABLE |
| minimum_distance_m_given_valid_action | 3.106032 | DESCRIPTIVE_ONLY |

The domain-level action rows in `phase8a_results.json` cover the pre-specified model, scenario, speed, and condition dimensions. Their point estimates are design-weighted; intervals are intentionally omitted where a domain variance estimator was not pre-specified.

## Legal outcome status

All jurisdictional legal-compliance, legality-ranking, and legal-versus-safety metrics are **NOT_ESTIMABLE**. Frozen Phase 5 v1 does not provide action-level determinations; no inference or imputation was performed.
