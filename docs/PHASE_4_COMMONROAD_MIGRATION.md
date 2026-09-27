# Phase 4 CommonRoad Migration

## Active decision

Phase 4 now targets a local CommonRoad-compatible physical benchmark using a
Kinematic Single-Track vehicle model. The study requires controlled comparison
of candidate trajectories, collision states, geometric road-boundary compliance,
and vehicle-dynamics feasibility; it does not require photorealistic perception
simulation.

This is a scientific scope selection, not a claim that CARLA succeeded or a
claim that CommonRoad predicts injury, survival, or human value. CARLA remains a
future optional higher-fidelity external-validation path. The CARLA and
free-cloud blockers are preserved as historical records.

## Intended physical outputs

The active pipeline is:

```text
scenario x action x seed
-> KS forward trajectory
-> shape collision / road-boundary / feasibility checks
-> physical-outcome record
```

The resulting matrix will later be joined to legal and model-decision layers;
it contains no country-law score or demographic value field.

## Current implementation status

`commonroad-io` and `commonroad-vehicle-models` install and import under Python
3.10 on this host. The required native Drivability Checker did not install;
therefore no CommonRoad simulation, trajectory, collision result, or physical
outcome has been generated. See `PHASE_4_COMMONROAD_BLOCKER.md`.

GitHub Codespaces Linux x86_64 is now the authorized reference execution
environment for the checker. It replaces native Windows only for execution;
it does not alter the scientific method, authorize WSL, or make an unexecuted
installation a successful result. The repository's dev-container requests the
official `commonroad-drivability-checker==2025.3.1` wheel, with resolved
versions recorded only after its programmatic import succeeds.

## Citation

M. Althoff, M. Koschi, and S. Manzinger, “CommonRoad: Composable Benchmarks
for Motion Planning on Roads,” *IEEE Intelligent Vehicles Symposium*, 2017.
