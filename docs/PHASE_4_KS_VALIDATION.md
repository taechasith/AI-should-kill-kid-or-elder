# Phase 4 KS validation

## Environment

Evidence was generated in GitHub Codespaces on Linux x86_64 with Python 3.10.18. The installed packages were `commonroad-drivability-checker` 2025.3.1, `commonroad-io` 2024.3, `commonroad-vehicle-models` 3.0.2, NumPy 2.2.6, SciPy 1.15.3, and Shapely 2.1.2.

## Vehicle model and conventions

`vehicle_params_v1` loads Vehicle 1 from `commonroad-vehicle-models` 3.0.2: length 4.298 m, width 1.674 m, `a=0.88392` m, `b=1.50876` m, and wheelbase 2.39268 m. The matching CommonRoad type is `VehicleType.FORD_ESCORT`.

The state ordering is `[x, y, steering_angle, velocity, orientation]`; the control ordering is `[steering_rate, longitudinal_acceleration]`. The custom generator implements the KS derivatives `x_dot=v cos(psi)`, `y_dot=v sin(psi)`, `delta_dot`, `v_dot`, and `psi_dot=v tan(delta)/wheelbase`, using fixed-step RK4 at 0.05 s. Controls are clipped to Vehicle 1 acceleration and steering-rate limits; steering is saturated at its configured bounds.

## Stop event and A2 reference

The integrator detects an in-step zero-velocity event, integrates only the fractional interval to the event, sets velocity to zero, and prevents reverse travel under subsequent braking. With `u=30/3.6` m/s and `a=-7.0` m/s², executed evidence reports:

| Quantity | Analytical | Numerical | Absolute error |
|---|---:|---:|---:|
| Stop time (s) | 1.1904761904761905 | 1.1904761904761914 | 8.881784197001252e-16 |
| Stop distance (m) | 4.960317460317461 | 4.960317460317465 | 3.552713678800501e-15 |

The time error is below 0.05 s and the distance error is below 0.02 m.

## Numerical checks

Left/right steering symmetry had maximum residual 0. RK4 timestep-halving (`0.05` vs `0.025` s) gave maximum state difference `1.0364407998508796e-08` (x coordinate). Deterministic replay had maximum residual 0.

## CommonRoad cross-check

Three unsaturated, nonzero-velocity cases were evaluated with `VehicleDynamics.KS(VehicleType.FORD_ESCORT)`. At `rtol=1e-10` and `atol=1e-10`, all component-wise derivative differences were 0, so the maximum derivative error was 0 and the cross-check passed.

## Tests and artifact integrity

The executed full repository suite reported 19 passed, 0 failed, and 0 skipped; its KS subset reported 8 passed. The SHA-256 digest of the executable validation artifact is `4c30a24ad06aad63408568d4d91997f39c000c9336d544ddabec82bbcc1762f9`.

## Known limitations

This is a kinematic model, without tire slip, road-surface friction modeling, suspension dynamics, deformation, or crash biomechanics. A collision does not imply injury or fatality. CommonRoad validation here is model-level interoperability validation, not real-vehicle certification.
