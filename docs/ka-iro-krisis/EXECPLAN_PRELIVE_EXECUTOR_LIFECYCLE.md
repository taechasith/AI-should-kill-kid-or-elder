# Pre-live executor and lifecycle ExecPlan

Purpose: finish the operational KA-IRO executor/lifecycle stack without changing frozen K1–K6 science. Current state: K5=720, K6=480, direct urllib transport, zero live calls, and a partial mock suite. Milestones are: durable manifest-only runner and ledger; retry/defer/recovery matrix; heartbeat/locking/rollover/quota-wait lifecycle; external Windows supervisor stack; integrated validation; commit/push/tag; durable Windows bootstrap action record.

Acceptance criteria: all frozen hashes validate; dry run verifies 1,200 rows with zero dispatches; recovery, idempotency, lifecycle, and supervisor mock coverage pass; K4–K6 validators, `pytest`, and `pip check` pass; no tracked secrets; Phase 7 and K1–K6 stay unchanged; executor tag is visible on origin. Checkpoint after durable operational milestones, never force-push. Decision log: direct urllib is used to avoid hidden SDK retries; long quota wait threshold is 25 minutes; Codespace rollover is operational, not scientific.

Commands: `python scripts/run_kairo_krisis.py --dry-run`; `bash scripts/kairo_health.sh`; `bash scripts/kairo_resume.sh`; K4/K5/K6 validators; `pytest -q`; `pip check`.

## Progress checklist

- [x] K4–K6 frozen; zero provider calls
- [x] K5/K6 manifest dry run verifies 1,200 rows
- [x] Durable production executor/recovery matrix: mocked HTTP ontology, retries, raw persistence, crash recovery, ambiguity, hash hard-stops, and zero hidden urllib retry.
- [x] Lifecycle and supervisor test matrix: local singleton/stale-lock, rollover, state, shell and safe-template checks pass. Windows runtime execution remains a bootstrap self-test because this Linux Codespace has no Windows host.
- [ ] Corrected executor/lifecycle checkpoint and remote tag
- [x] Windows bootstrap action record committed and pushed
- [ ] WINDOWS_BOOTSTRAP_REQUIRED

**THIS EXECPLAN IS NOT COMPLETE UNTIL WINDOWS_BOOTSTRAP_REQUIRED IS READY.**
