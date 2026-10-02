# KA-IRO KRISIS executor and lifecycle protocol v1

This operational protocol is frozen separately from K1–K6 and does not alter scientific inputs, allocation, hypotheses, or execution keys. Direct `urllib` transport is used: one `dispatch_once` invocation performs at most one HTTP request and contains no retry middleware or provider SDK.

The durable sequence is `PLANNED → ATTEMPT_STARTED → RAW_RESPONSE_DURABLE → ATTEMPT_FINALIZED → PARSED → TERMINAL`. Attempts and raw responses are immutable; current observation state is atomically replaced. A restart never re-sends a terminal observation. An unresolved in-flight request is recorded as `AMBIGUOUS_TRANSPORT_OUTCOME` and is never blindly replayed. A durable finalized raw response can be parsed offline after a crash.

Terminal experimental states include `VALID_ACTION`, `VALID_RESPONSE_NO_ALLOWLISTED_ACTION`, `INVALID_STRUCTURED_OUTPUT`, `REFUSAL`, `CONTENT_BLOCKED`, `NON_RETRYABLE_PROVIDER_ERROR`, `RETRY_EXHAUSTED`, and `AMBIGUOUS_TRANSPORT_OUTCOME`. Invalid output and refusal are not retried. Only transient 429/5xx or known-not-accepted transport errors may receive bounded explicit attempts. Daily/free quota exhaustion is `QUOTA_DEFERRED`, not an experimental result. The long-wait operational threshold is 25 minutes. Codespace rollover begins at 10.5 hours and writes a non-sensitive local restart marker.

Canonical commands are `bash scripts/kairo_resume.sh`, `bash scripts/kairo_health.sh`, and `python scripts/run_kairo_krisis.py --dry-run`. The Windows Scheduled Task supervisor is operational infrastructure only; it starts only the named existing Codespace and resumes through the canonical command.

Runtime record: Python 3 direct stdlib `urllib`; no provider SDK participates in execution. Source SHA-256: `execution.py` `29d799bb4ef955ff3584e69d32b1eb7fa15ba048ec416a276c204ac8f186b25d`; `lifecycle.py` `c478830fc0896e1ffba035208ad18f633bad9a77c321afa89d2937446a972f4a`; `run_kairo_krisis.py` `6c09825bd8c900c976ec44958a996fb4699dbe1eb72595e637e21936557a277d`; `kairo_resume.sh` `b3effea94abe4144042411dbb6429373b5dd7a7610117a72d48149ebb332f082`; `kairo_health.sh` `6a1f3f5a69a514401fb3e1f02bb40fefef91a85079b0a7c03c9d3cca669298cb`.

Validation evidence before any K5/K6 generation: K4/K5/K6 and serialization validators pass; the 1,200-row dry run has zero dispatches; executor/lifecycle mocked suite passes; repository suite reports `128 passed, 5 subtests passed`; `pip check` reports no broken requirements.
