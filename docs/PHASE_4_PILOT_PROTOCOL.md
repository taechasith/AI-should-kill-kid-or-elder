# Phase 4 - Frozen CommonRoad Pilot Protocol

**Protocol ID:** `commonroad-pilot-v1`
**Status:** active protocol, blocked before execution pending the authorized
GitHub Codespaces Linux checker verification documented in
`PHASE_4_COMMONROAD_BLOCKER.md`.
**Engine:** CommonRoad-compatible local forward simulation.
**Vehicle model:** Kinematic Single-Track (KS).

## Objective and boundary

This pilot creates an action-outcome matrix:

```text
scenario x initial_speed x action x seed
-> KS forward trajectory
-> collision / road-boundary / feasibility checks
-> machine-readable physical outcome
```

It measures physical collision outcomes, trajectory feasibility, and geometric
road-boundary compliance. It does not measure legal compliance, injury,
survival, moral worth, country law, or model behavior.

## Frozen configuration

| Setting | Value |
|---|---|
| Timestep | `0.05` s (20 Hz) |
| Maximum duration | `15.0` s |
| Speeds | `30`, `50` km/h |
| Seeds | `42`, `43`, `44`, `45`, `46` |
| Rendering | Off by default; one representative render per scenario only after validation |
| Weather | Not modelled |
| Reference execution environment | GitHub Codespaces, Linux x86_64, CPU-only |
| External services | None during simulation; Codespaces is execution infrastructure only |

All internal calculations use SI units. The speed inputs convert to
8.333333... m/s and 13.888888... m/s respectively.

## Scenario families and actions

| ID | Physical setup |
|---|---|
| `PED-CROSS-001` | Generic pedestrian-shaped dynamic obstacle crosses a deterministic straight-road ego trajectory. |
| `OBS-LANE-001` | Stationary vehicle-shaped obstacle blocks the ego lane while an adjacent lateral space supports controlled evasive trajectories. |
| `MOTO-CUTIN-001` | Motorcycle-shaped dynamic obstacle performs a deterministic cut-in. |

The canonical actions are `A0` maintain, `A1` moderate brake, `A2` emergency
brake, `A3` brake-and-steer left, `A4` brake-and-steer right, and `A6`
minimum-risk stop. Each action must be a frozen deterministic control profile;
an inapplicable action is marked `not_applicable`, never forced.

## Determinism gate

Before the matrix, execute `OBS-LANE-001`, 30 km/h, `A2`, seed 42 exactly three
times. Initial state, control profile, collision state, road-boundary status,
feasibility status, and termination reason must match exactly. Position,
velocity, and continuous metrics must agree within tolerances specified before
inspection. Any material mismatch stops the phase.

## Data and failure rules

Each run records trajectory states, control state, collision/partner,
minimum TTC where defined, minimum shape distance, deceleration, jerk, lateral
acceleration, road-boundary state, feasibility, final speed, duration, seed,
engine/package versions, and Git commit. Undefined values are `null`.

Every manifest row ends exactly once as `completed`, `failed`, or
`not_applicable`. Failed rows retain structured failure type and reason. No
trajectory or physical outcome may be manually authored.

## Completion gate

Only after the environment imports the required checker, all three scenarios
instantiate, actions and metrics pass unit tests, the determinism gate passes,
and every pre-generated manifest row is accounted for may the resulting
artifacts be frozen as `commonroad-pilot-v1`. The pipeline remains
Linux-generic even though Codespaces is its reference environment. CARLA is an
optional future higher-fidelity validation path and is not an active requirement.
