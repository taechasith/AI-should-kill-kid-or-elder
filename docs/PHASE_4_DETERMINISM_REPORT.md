# Phase 4 determinism report

The required pre-pilot gate executed `OBS-LANE-001`, 30 km/h, `A2`, and seed 42 exactly three times in the pinned Codespaces environment.

All three executions produced the identical trajectory SHA-256 `efcee742c51b4b9c7a79ad21a5767d992c2d318b517a57c5e16b18d49a86630e`. Each was CommonRoad-feasible, collision-free according to the CommonRoad collision checker, and had no CommonRoad road-boundary violation. The independently computed minimum shape distance was 0.9999999999999947 m, minimum defined TTC was 0.5345552758548339 s, maximum deceleration was -7.0 m/s2, maximum jerk was 0.0 m/s3, and maximum lateral acceleration was 0.0 m/s2.

Initial state, deterministic control timing, collision status, boundary status, feasibility status, and continuous metrics therefore match exactly. The determinism gate passed. The retained seeds are pipeline-compatibility identifiers; the baseline physics contains no stochastic parameter.
