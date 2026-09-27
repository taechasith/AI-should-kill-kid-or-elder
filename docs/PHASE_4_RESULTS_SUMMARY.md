# Phase 4 CommonRoad physical benchmark results

## Provenance and environment

The canonical physical-source commit is `d52baab`. It contains the frozen 180-row manifest, 180 canonical outcome records, and 180 raw trajectory files. The reference execution environment was Linux x86_64, Python 3.10.18, `commonroad-drivability-checker` 2025.3.1, `commonroad-io` 2024.3, and `commonroad-vehicle-models` 3.0.2. The generator was the explicit Vehicle 1 Kinematic Single-Track model with fixed-step RK4 at 0.05 s; CommonRoad supplied independent feasibility, collision, and road-boundary validation.

## Accounting and determinism

All 180 planned rows completed; there were 0 failed and 0 not-applicable rows. The determinism gate passed. The five seed values are retained for protocol compatibility, not treated as independent stochastic trials because this baseline has no stochastic parameter.

There are 348 historical duplicate execution attempts in `data/simulator/commonroad/attempts/`. They are retained solely as debugging provenance and are excluded from every statistic in this report and from the canonical 180-row outcome file.

## Physical characterization

Canonical collision count was 80/180 (44.44%); feasibility count was 120/180 (66.67%); and road-compliant count was 135/180 (75.00%). By scenario, collisions were 5/60 for `MOTO-CUTIN-001`, 55/60 for `OBS-LANE-001`, and 20/60 for `PED-CROSS-001`. At 30 km/h there were 30 collisions in 90 records; at 50 km/h there were 50 in 90 records.

Minimum shape distance ranged from 0 to 10.978843678044809 m (mean 4.103714033463779 m). Defined TTC ranged from 0.00112190644977524 to 33.97415470802763 s (mean 5.632556813441006 s). Collision-speed metrics are null because the current frozen record set does not derive relative collision speed; null is retained rather than inventing a value.

The stored deceleration convention is signed longitudinal acceleration: its range is -7.0 to 0.0 m/s2 (mean -4.0 m/s2). Maximum jerk was 0.0 m/s3 under the frozen constant-control profile convention. Maximum lateral-acceleration magnitude ranged from 0 to 12.126797498160135 m/s2 (mean 2.5067128854961025 m/s2).

## Integrity and reproducibility

The final dataset validator confirmed unique canonical run IDs, exact manifest membership, valid state accounting, existing trajectories, monotonic timestamps, nonnegative velocity, bounded controls, finite numeric values, and separation of the 348 attempt records. SHA-256 verification covered 191 artifacts, including every canonical trajectory.

## Limitations

These are controlled synthetic Kinematic Single-Track physical risk proxies, not injury, fatality, survival, legal, or moral predictions. They omit tire slip, friction-circle effects, suspension, deformation, biomechanics, and detailed actor dynamics. Collision does not imply injury or fatality; road-boundary compliance is not legal compliance. CARLA and real-world/high-fidelity validation remain future work.
