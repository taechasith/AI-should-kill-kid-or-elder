# Phase 8A — confirmatory analysis

Phase 8A is a read-only analysis of the frozen Phase 4, Phase 5, and completed
Phase 7 population-sampled artifacts. It performs no provider calls and has a
hard cost of USD 0.00 / THB 0.00.

The analysis population is the immutable 4,104-row provider frame. It uses 279
pre-amendment certainty observations and 60 frozen stratified probability-sample
observations, with the original inclusion probabilities. Population estimates
use the Horvitz--Thompson estimator and the frozen finite-population variance
method.

The frozen Phase 5 action-level decisions are all `NOT_DETERMINED`. Therefore
Phase 8A must not present prohibited-action, road-compliance, unsupported-legal-
claim, or law-responsive-differentiation rates as estimates. Those outcomes are
explicitly represented as not estimable in the machine-readable report.

Run:

```bash
python scripts/run_phase8a_confirmatory_analysis.py
python scripts/validate_phase8a_confirmatory_analysis.py
```

The report retains only defensible outputs: design-weighted valid-action and
selected-action summaries, structural Phase 4 joins, sampling provenance, and
the claim boundary. Physical outcomes are reported only descriptively among
outputs that parsed to an action; invalid outputs remain explicit and are never
assigned a physical outcome. It does not authorize Phase 8B or any new model
execution.
