# KA-IRO KRISIS K5 quota-wait checkpoint — 2026-10-03

This is an operational and reproducibility checkpoint only. It does not
amend K1–K6, change membership, interpret model outputs, or authorize paid
inference.

## Durable accounting

- Frozen observations: 1,200 (K5 720; K6 480).
- K5 terminal: 259; K5 remaining: 461.
- K6 terminal: 1; K6 remaining: 479. No additional K6 dispatch may begin
  until K5 is terminal.
- Attempted observations: 261; explicit HTTP attempts: 267.
- HTTP accounting: 200 = 256; 429 = 2; 403 = 2; 503 = 5; ambiguous transport
  records = 2.
- Current durable state: 260 `TERMINAL`, 1 `QUOTA_DEFERRED`, 939 `PLANNED`.
- Provider inference spend remains USD 0.00 / THB 0.00.

## Integrity audit

The machine-readable audit is
`data/ka-iro-krisis/v2/execution/audits/quota_wait_audit_20261003T0901Z.json`.
It reports `PASS` for ledger/raw-response integrity and frozen-request
reconstruction. Specifically, it found no duplicate terminal observation, no
observation with multiple HTTP-200 responses, no missing raw artifact, no raw
hash mismatch, no orphaned raw/ledger artifact, no parser replay mismatch, no
unresolved `ATTEMPT_STARTED` state, and no retry-policy violation.

Two terminal `AMBIGUOUS_TRANSPORT_OUTCOME` records remain preserved as such;
they were not replayed. A quota-exhausted request resumed only as the same
frozen observation after reset scheduling, as permitted by the frozen policy.

The amended K5/K6 manifests retain the parent manifests' observation IDs,
model/provider/interface/representation allocation, and execution-order keys.
All 1,200 request bodies reconstruct from frozen assets and serializers.

## Resume condition

The only current quota-deferred observation is:

`K5-M1-KAIRO-V2-VEHICLE_CUTIN-006-STRICT_STRUCTURED_OUTPUT-TEXT_ONLY_EQUIVALENT_CONTEXT`

Its recorded earliest eligible time is `2026-10-03T23:59:59.092744Z` (UTC),
derived from the preserved Gemini quota response. The canonical resume command
is:

```bash
bash scripts/kairo_resume.sh
```

The command validates frozen manifests and credentials by presence only, reads
the durable ledger, and resumes this exact frozen row only once the recorded
quota condition is eligible. It never re-sends a terminal row.
