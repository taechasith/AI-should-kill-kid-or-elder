# Phase 4 and Phase 5 reproducibility

Phase 4 requires Linux x86_64 with Python 3.10 and the pinned packages in `requirements-commonroad-codespaces.txt`. GitHub Codespaces is the reference environment. GPU, CARLA, Docker, and native Windows CommonRoad execution are not required; the latter was historically blocked and Linux Codespaces resolved compatibility.

```bash
python scripts/verify_commonroad_environment.py
python -m pip check
python -m pytest -q
python scripts/generate_ks_validation.py
python scripts/finalize_commonroad_pilot.py validate
python scripts/finalize_commonroad_pilot.py summarize
python scripts/finalize_commonroad_pilot.py hash
python scripts/finalize_commonroad_pilot.py verify
```

The frozen physical source is commit `d52baab`; it must not be replaced by a rerun for summary generation. The canonical manifest is `data/simulator/commonroad/manifests/commonroad_pilot_v1.json` and the canonical data are the 180 corresponding outcome and trajectory artifacts. The 348 files/rows under `data/simulator/commonroad/attempts/` are retained debugging provenance and excluded from the analysis population.

For a fresh permitted execution only, generate the manifest before any outcomes and use the resumable runner:

```bash
python scripts/run_commonroad_pilot.py --write-manifest
python scripts/run_commonroad_pilot.py --execute
```

Do not use these commands to overwrite the frozen canonical pilot. Hash verification is the final integrity check.

## Phase 5 legal snapshot

The Phase 5 snapshot is separate from the immutable physical benchmark. It
collects WHO road-safety context, generates the query universe, performs a
documented two-pass official-source retrieval attempt, and deliberately keeps
action-level status as `NOT_DETERMINED` when a material legal predicate is not
provided by the frozen legal overlay.

```bash
python -m pip install -r requirements-phase5.txt
python scripts/collect_who_global_context.py
python scripts/build_phase5_query_universe.py
python scripts/verify_phase5_sources.py
python scripts/materialize_phase5_legal_snapshot.py
python scripts/validate_phase5_legal_snapshot.py
python scripts/finalize_phase5_legal_snapshot.py
python scripts/verify_phase5_hashes.py
python scripts/generate_phase5_docs.py
```

The raw WHO profile cache is deliberately ignored and reproducible from the
official URLs. The tracked processed context, source metadata, snapshot, and
hash manifest retain the data necessary to audit the released result. Do not
modify `phase5-legal-snapshot-v1` in place; create a new snapshot version for
any new legal facts, sources, or interpretation.

## Phase 6 offline dry run

The Phase 6 dry-run is intentionally offline and must not make a provider API
call. It rebuilds six deterministic initial-state bird's-eye packages, the
closed-book condition contexts, blocked manifests, and the planning cost
estimate. It then validates the input-information boundary, parser/adapters,
and accounting.

```bash
python scripts/build_phase6_dry_run.py
python scripts/validate_phase6_dry_run.py
python scripts/finalize_phase6_dry_run.py
python scripts/verify_phase6_dry_run_hashes.py
python -m pytest -q
```

`docs/PHASE_6_BLOCKER.md` records the authorization boundary. These commands
do not complete Phase 6 and must never be treated as permission to call a
provider. A future authorized pilot must preserve raw responses and use a new
versioned artifact if it changes the candidate panel, frozen inputs, or legal
snapshot.

## Phase 6 zero-cost preflight

`phase6-free-v1` is a separate, fail-closed preflight authorized only under a
USD 0.00 / THB 0.00 policy. It preserves the prior blocked dry-run and the
frozen Phase 4 and Phase 5 source artifacts. It contains no credentials and
makes no provider request.

```bash
python scripts/build_phase6_free_v1_preflight.py
python scripts/validate_phase6_free_v1_preflight.py
python scripts/finalize_phase6_free_v1_preflight.py
python scripts/verify_phase6_free_v1_preflight_hashes.py
python -m pytest -q tests/test_phase6_free_v1.py
```

The preflight remains non-executable until both provider credentials are placed
in an approved secret store and authenticated live checks establish a
billing-disabled Free Tier / Free Plan, exact model availability, image input,
and current rate-limit metadata. See `docs/PHASE_6_ZERO_COST_POLICY.md`.
