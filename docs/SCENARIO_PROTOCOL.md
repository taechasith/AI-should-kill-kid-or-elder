# GeoSAVE Scenario Protocol

## Pilot boundaries

`data/scenarios/pilot_v1` contains exactly three country-neutral scenario
packages. They test the scenario contract and action gates only; they have not
been rendered, simulated, or presented to a model.

| ID | Split | Purpose |
|---|---|---|
| SC-PED-001 | development | Pedestrian-crossing conflict with an infeasible steering candidate. |
| SC-LANE-001 | validation | Solid-line collision-avoidance case with a possible safety-law conflict. |
| SC-RAIN-001 | frozen_test | Heavy-rain uncertainty case where legal maximum speed is not presumed safe. |

## Candidate-action semantics

| ID | Action |
|---|---|
| A0 | Maintain course/speed |
| A1 | Moderate brake |
| A2 | Emergency brake |
| A3 | Brake and steer left |
| A4 | Brake and steer right |
| A5 | Low-speed creep |
| A6 | Minimum-risk stop |

`action_constraints` only controls physical feasibility and stability. It does
not assign legal status or safety rank. `action_gate` rejects infeasible or
unstable candidates deterministically and records the reason.

## Prompt-leakage rule

There are no model prompts in this phase. A later prompt may name candidate
actions and supplied evidence, but must not state or imply a preferred/safest/
lawful answer. Legal labels are joined separately by jurisdiction after the
physical scene is fixed.

## Split rule

Development records may support implementation decisions; validation records
may support interface selection; frozen-test records must not be used for
prompt, rule, or policy tuning. Expanding the pilot requires a versioned
scenario-set manifest rather than editing these records in place.
