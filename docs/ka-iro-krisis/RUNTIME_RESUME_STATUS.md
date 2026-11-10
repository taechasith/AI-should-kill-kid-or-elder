# KA-IRO runtime resume status

Status: `QUOTA_WAIT` (operational quota gate; not a scientific blocker)

The canonical resume command ran after the prior eligibility time and stopped
when the Gemini route reached its durable quota gate. No provider request may
be sent before the newly recorded resume condition.

| Field | Durable value |
| --- | --- |
| Phase | K5 |
| K5 terminal / planned | 709 / 720 |
| K5 remaining | 11 |
| K6 terminal / planned | 1 / 480 |
| K6 remaining | 479 |
| Total HTTP attempts | 799 |
| Ambiguous transport outcomes | 2 (preserved; never replay automatically) |
| Quota-deferred observations | 1 |
| Provider inference cost | USD 0.00 |
| Resume not before (UTC) | 2026-11-11T07:59:59.440927Z |
| Resume not before (ICT) | 2026-11-11T14:59:59.440927+07:00 |
| Integrity audit | `PASS` — `data/ka-iro-krisis/v2/execution/audits/quota_wait_audit_20261110T2133Z.json` |
| Durable checkpoint | Pending publication commit |
| Canonical resume command | `bash scripts/kairo_resume.sh` |

The exact quota-deferred frozen observation is
`K5-M1-KAIRO-V2-LEAD_VEHICLE_BRAKE-009-STRICT_STRUCTURED_OUTPUT-TEXT_ONLY_EQUIVALENT_CONTEXT`.
Its quota metadata and prior attempts remain in the append-only execution
ledger. The offline integrity audit passed: all 1,200 manifest rows were
accounted for, all 799 attempt records were validated, and no raw-response
hash mismatch, unresolved started state, or retry-policy violation was found.
On the next Codespace session, read `AGENTS.md`, this status file, and the
ledger; validate frozen manifests and hashes, check credentials by presence
only, confirm `HEAD` matches `origin/ka-iro-krisis-v2`, and resume only through
the canonical command. The first provider request after the time gate must be
this exact deferred observation—not a probe or substitute. K6 may not dispatch
until all K5 observations are terminal.
