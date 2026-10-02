# Phase 9 Linux Clean-Reproduction and Submission-Readiness Validation

**Validation date:** 2026-10-02
**Source commit:** `3eac34c84900faf0c24e4fbe033ecdf8233ef677` (`phase9-final-synthesis`)
**Result:** `CLEAN_REPRODUCTION_PASSED`; `SUBMISSION_READINESS_CONDITIONAL_NO_GO`

## Scope and isolation

Validation used a fresh file-protocol Git clone under Ubuntu WSL2 in `/tmp`, not
the working checkout. The clone was clean before and after validation. The
environment was Linux x86_64 with CPython 3.10.21 and the pinned CommonRoad
stack: `commonroad-drivability-checker` 2025.3.1, `commonroad-io` 2024.3,
`commonroad-vehicle-models` 3.0.2, NumPy 2.2.6, SciPy 1.15.3, and Shapely
2.1.2. `pip check` reported no broken requirements.

No model API, provider metadata, legal-source, or other research-network call
was made. No simulator execution, sampling execution, legal-data collection,
or modification of a frozen artifact was performed. Phase 4 was reproduced as
the documented frozen-artifact integrity verification, not by overwriting its
canonical physical-outcome matrix.

## Reproduction evidence

| Gate | Result |
| --- | --- |
| CommonRoad environment and checker import | PASS |
| Phase 4 canonical integrity | PASS: 180 planned/canonical rows; 348 preserved duplicate attempts |
| Phase 4 hash manifest | PASS: 191 artifacts, no mismatch |
| Phase 5 protocol, legal snapshot, and hashes | PASS: 25 hashed files |
| Phase 6 literature-v2 pilot and hashes | PASS: 3 bounded attempts; 3 valid actions; 2 normalized responses; 14 hashed files |
| Phase 7 population-sampling manifest | PASS |
| Phase 8A frozen analysis | PASS |
| Phase 9 evidence package | PASS: 13 claims with valid Phase 8A sources |
| Full test suite | PASS: 108 passed |

Commands were run in the clean clone with its isolated virtual environment:

```text
python scripts/verify_commonroad_environment.py --require-checker
python scripts/finalize_commonroad_pilot.py validate
python scripts/finalize_commonroad_pilot.py verify
python scripts/validate_phase5_protocol.py
python scripts/validate_phase5_legal_snapshot.py
python scripts/verify_phase5_hashes.py
python scripts/validate_phase6_literature_v2_pilot.py
python scripts/verify_phase6_literature_v2_hashes.py
python scripts/validate_phase7_population_sample.py
python scripts/validate_phase8a_analysis.py
python scripts/validate_phase9_synthesis.py
python -m pytest -q
```

## Claim and submission gates

The reproducibility gate is passed. The preserved Phase 7 design accounts for
5,454 manifest rows: 1,350 structurally not applicable and a 4,104-row
provider population. Its inference remains based on 279 certainty observations
and 60 probability-sampled terminal observations; it is not a provider census.
Jurisdiction-specific legal-compliance metrics remain `NOT_ESTIMABLE` because
the frozen Phase 5 snapshot does not contain action-level determinations.

The repository is therefore ready for evidence-preserving manuscript support,
not for submission. Before any IEEE IV 2027 submission, a human author must
verify the current official author instructions, including the currently
in-progress 2027 CFP, double-blind requirements, formatting, and LLM-authorship
policy. The official 2027 site lists the conference dates and schedule, but its
CFP page remains marked "In progress"; the prior 2026 author page cannot be
treated as the final 2027 policy.

## Remaining external gates

- Current IEEE IV 2027 author/instructions page and submission-portal rules.
- Human authorship, anonymity, conflict-of-interest, and final manuscript
  compliance review.
- A claim review that preserves the recorded `NOT_ESTIMABLE` legal scope and
  the non-census Phase 7 sampling interpretation.
