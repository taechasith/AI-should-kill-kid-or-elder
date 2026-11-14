# KA-IRO runtime resume status

Status: `QUOTA_WAIT` (operational quota gate; not a scientific blocker)

The prior canonical resume completed K5 and advanced K6 before stopping when
the Gemini route reached its durable quota gate. That recorded eligibility
time has elapsed; the canonical resume command may now continue the exact
deferred K6 observation. No probe, substitute, or ambiguous-outcome replay is
authorized.

| Field | Durable value |
| --- | --- |
| Phase | K6 |
| K5 terminal / planned | 720 / 720 |
| K5 remaining | 0 |
| K6 terminal / planned | 160 / 480 |
| K6 remaining | 320 |
| Total HTTP attempts | 984 |
| Ambiguous transport outcomes | 5 (preserved; never replay automatically) |
| Quota-deferred observations | 1 |
| Provider inference cost | USD 0.00 |
| Resume not before (UTC) | 2026-11-13T07:59:59.789330Z |
| Resume not before (ICT) | 2026-11-13T14:59:59.789330+07:00 |
| Integrity audit | `PASS` — `data/ka-iro-krisis/v2/execution/audits/quota_wait_audit_20261114T0817Z.json` |
| Durable checkpoint | Pending publication commit |
| Canonical resume command | `bash scripts/kairo_resume.sh` |

The exact quota-deferred frozen observation is
`K6-KAIRO-V2-PED_CROSS-005-SEMANTIC_COUNTERFACTUAL-ARM1-M1-TEXT_ONLY_EQUIVALENT_CONTEXT`.
Its quota metadata and prior attempts remain in the append-only execution
ledger. The offline integrity audit passed: all 1,200 manifest rows and all
984 attempt records were accounted for, with no raw-response hash mismatch,
unresolved started state, or retry-policy violation. The five ambiguous
transport outcomes remain preserved and must never be replayed automatically.
The canonical resume command must continue this exact quota-deferred K6 row
first; no K6 row may be substituted.
