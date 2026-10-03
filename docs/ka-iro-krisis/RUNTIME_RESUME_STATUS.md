# KA-IRO runtime resume status

Status: `CODESPACE_RESTART_REQUIRED` (operational rollover; not a scientific blocker)

This checkpoint deliberately avoids holding Codespace compute open during the
recorded Gemini quota window. No provider request may be sent before the
recorded resume condition.

| Field | Durable value |
| --- | --- |
| Phase | K5 |
| K5 terminal / planned | 259 / 720 |
| K5 remaining | 461 |
| K6 terminal / planned | 1 / 480 |
| K6 remaining | 479 |
| Total HTTP attempts | 267 |
| Ambiguous transport outcomes | 2 (preserved; never replay automatically) |
| Provider inference cost | USD 0.00 |
| Resume not before (UTC) | 2026-10-03T23:59:59Z |
| Resume not before (ICT) | 2026-10-04T06:59:59+07:00 |
| Durable checkpoint | `d0224ce` |
| Canonical resume command | `bash scripts/kairo_resume.sh` |

The exact quota-deferred frozen observation is
`K5-M1-KAIRO-V2-VEHICLE_CUTIN-006-STRICT_STRUCTURED_OUTPUT-TEXT_ONLY_EQUIVALENT_CONTEXT`.
Its quota metadata and prior attempts remain in the append-only execution
ledger. On the next Codespace session, read `AGENTS.md`, this status file, and
the ledger; validate frozen manifests and hashes, check credentials by presence
only, confirm `HEAD` matches `origin/ka-iro-krisis-v2`, and resume only through
the canonical command. The first provider request after the time gate must be
this exact deferred observation—not a probe or substitute.
