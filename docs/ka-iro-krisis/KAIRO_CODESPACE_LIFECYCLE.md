# Codespace lifecycle resilience

`bash scripts/kairo_resume.sh` is the canonical idempotent resume gate. It never resets or deletes execution state. Run `/tmp/ka-iro-heartbeat.sh` only while an active executor is running; it is local-only and must not be logged as research evidence. Before an expected Codespace rollover, stop new dispatch, persist and validate the ledger, push a checkpoint, write a non-sensitive `/tmp/KA_IRO_NEEDS_RESTART`, and exit with `CODESPACE_ROLLOVER_REQUIRED`. This is not a scientific blocker. Codespaces compute usage is operational cost and distinct from the USD 0 / THB 0 provider-inference policy.

The external Windows supervisor template is `docs/ka-iro-krisis/templates/kairo_codespace_supervisor.ps1` and must run on the researcher's local machine, never inside the Codespace.
