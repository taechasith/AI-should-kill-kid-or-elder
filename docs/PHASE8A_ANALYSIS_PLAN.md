# Phase 8A frozen confirmatory analysis plan

Status: `FROZEN_PRE_RESULT_COMPUTATION`

## Scope and disclosure

Phase 8A is an offline analysis of the recovered Phase 7 population-sampled
snapshot `99551fa` (`phase7-population-sample-recovered-v1`). It neither sends
provider requests nor changes Phase 4, Phase 5, Phase 6, or Phase 7 data.

This is confirmatory relative to this frozen specification, but is not
strictly outcome-blind. Before this plan, the following aggregate information
was known: the 5,454/4,104/1,350 accounting totals; 279 certainty units; 60
probability-sample units; a valid-action HT estimate of 0.8238304094 with an
approximate interval of [0.7340288824, 0.9136319363]; and that Phase 5 legal
rates are not estimable. No additional Phase 8A outcome combination is used
to choose metrics, exclusions, comparisons, or uncertainty methods.

## Inputs and units

The design-accounted manifest has 5,454 rows: 1,350 C3 `not_applicable` rows
and a finite provider population of 4,104 rows. The analysis sample is 279
certainty observations (`pi=1`) plus 60 terminal stratified-SRSWOR probability
observations (`pi=n_h/N_h`) across model × condition strata. The 339 selected
units are not a simple random census.

Denominators are never substituted:

| Population label | Definition |
| --- | --- |
| `design_accounted` | all 5,454 manifest rows |
| `not_applicable` | 1,350 C3 rows |
| `provider_population` | 4,104 provider-execution rows |
| `analysis_selected` | 339 certainty plus probability-sample rows |
| `terminal_response` | selected units with a completed HTTP-200 record |
| `explicit_action` | terminal response with parser-reported explicit action token |
| `valid_allowlisted_action` | explicit action accepted by frozen parser |
| `physical_linked_action` | valid action with exactly five matching Phase 4 seed outcomes |

`quota_deferred`, HTTP failure, malformed/invalid action, no explicit action,
and missing physical linkage remain separate states. No missing decision or
legal status is imputed or repaired.

## Estimands and uncertainty

Population rates use the frozen finite-population Horvitz--Thompson estimator:
certainty contributions plus sampled-unit `1/pi` contributions, divided by
4,104. Stratified SRSWOR variance with finite-population correction is used
for scalar rates and bounded seed-mean physical outcomes; the report labels
the normal-approximation interval as approximate. No naive binomial interval
is used.

Overall valid action and overall selected-action physical metrics are
population estimands. Model, condition, scenario, and speed tables are
reported as design-weighted domains only where the applicable selected domain
has at least two probability units in each contributing sampled stratum;
otherwise they are descriptive selected-unit summaries and marked
`DOMAIN_UNCERTAINTY_NOT_ESTIMABLE`. No inferential model ranking, paired test,
or post-hoc subgroup hypothesis test is performed in Phase 8A.

Each valid model action maps to five frozen Phase 4 outcomes sharing scenario,
speed, and action ID and differing only by Phase 4 seed. The physical scalar
for that model action is the unweighted mean across those five seed outcomes.
This is a one-to-five audited linkage, not a legal determination.

## Confirmatory metrics

The machine-readable metric registry freezes interface accounting, weighted
action distributions, selected-action physical outcome rates, and selected-unit
scenario/speed descriptive tables. `strict_json_success` is always reported
separately from explicit valid-action extraction.

All jurisdictional legality, legal-vs-safe conflict, prohibited-action,
physical road-compliance-as-legality, jurisdiction ranking, and imputed-legal
metrics are `NOT_ESTIMABLE` because Phase 5 v1 action-level legal status is
`NOT_DETERMINED`.

## Comparisons and multiplicity

The comparison registry contains no Phase 8A inferential hypothesis tests.
It freezes descriptive model/scenario/condition domains and prohibits claiming
that a model is best, safest, ethical, lawful, or causally responsive. Because
no inferential comparison family is executed, multiplicity adjustment is not
applicable.

## Reproducibility gate

`scripts/run_phase8a_analysis.py` must validate frozen hashes, selected-unit
uniqueness, terminal records, parser fields, inclusion probabilities, Phase 4
join cardinality, and blocked legal metrics before emitting results. It uses
only the Python standard library and makes no network or simulation call.
