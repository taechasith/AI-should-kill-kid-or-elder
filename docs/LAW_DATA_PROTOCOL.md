# GeoSAVE Law-Data Protocol

## Scope of the initial pilot

The `2026-09-27-pilot-v1` snapshot proves a data path with two narrowly scoped
pedestrian-crossing rules. It is not legal advice, a complete description of
New Zealand or Australian law, or sufficient coverage for a benchmark.

The records were derived from official legislation. New Zealand is national
(`NZL`); Australia is deliberately encoded as `AUS` plus `subnational_code:
NSW`, because the source is New South Wales law and must not be generalized to
all Australian jurisdictions.

## Verification status

Both records are `probable`: they use direct primary legislation, but the
accessed views are dated and neither has independent second-review validation.
Their review state is `solo_initial_extraction`. A later, delayed
re-verification against a current official view must update a new snapshot, not
mutate this one.

`effective_from` is `null` where this pilot did not establish an effective date
from the accessed source. The unknown is explicit rather than inferred.

## Snapshot rules

1. Rules live in a versioned snapshot directory.
2. A changed source, interpretation, translation, status, or effective date
   creates a new snapshot ID and manifest.
3. Raw copyrighted/restricted legal text is not copied into this repository;
   records retain a short normalized English statement and a stable locator.
4. `unknown`, `ambiguous`, `probable`, and `unresolved` statuses must remain
   visible to analysis. Only the exact status `legal` may count as verified-law
   compliance for a selected action.

## Global Law Map pilot

`data/global_law_map/processed/pilot_v1.csv` contains only WHO road-safety
context values for the same two ISO-3 jurisdictions. It deliberately does not
convert WHO context indicators into scenario-level legal labels. A later map
may add standardized legal indicators only with field-level provenance.
