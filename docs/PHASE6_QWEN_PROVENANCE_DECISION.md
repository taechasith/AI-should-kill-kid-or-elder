# Phase 6 Qwen provenance decision

Decision date: 2026-10-02
Status: `RETAIN_HISTORICAL_GROQ_EXECUTION_WITH_LIMITATION`

## Decision

Retain the historical Phase 6 and Phase 7 Qwen evidence. Do not initiate a
corrective Qwen-only rerun solely because of the prospective OpenRouter v2a
amendment.

## Rationale

1. The historical provider was Groq, not OpenRouter.
2. The immutable records preserve the exact model identity
   `qwen/qwen3.8-27b`.
3. Groq's public rate-limit documentation lists that exact identifier under
   Free Plan Limits.
4. The historical account record attests Free Plan access, disabled billing,
   and available quota.
5. No record establishes use of OpenRouter's priced endpoint.
6. `58f10b9` is a prospective OpenRouter endpoint amendment; it was never
   adopted for the historical Groq execution route.
7. No transaction-level provider billing ledger was preserved.

## Cost-provenance classification

```text
cost_status = FREE_PLAN_ELIGIBLE_WITH_ACCOUNT_ATTESTATION
billing_evidence = PLAN_LEVEL_SUPPORTED_TRANSACTION_LEVEL_UNVERIFIED
```

This classification supports eligibility under the study's zero-cost policy.
It must not be reported as a provider-certified, per-request $0 transaction
ledger.

## Consequences

* The historical Phase 6 pilot and its downstream Phase 7 Groq stratum are
  retained.
* No Qwen rerun, invalidation, deletion, or tag rewrite is required solely by
  the OpenRouter endpoint distinction.
* The 11 completed M3 Phase 7 observations, 8 quota-deferred M3 attempts, and
  1 HTTP-429 M3 attempt remain preserved as historical provenance.
* `backup/phase6-v2a-amendment` and `phase6-v2a-amendment-local` remain
  protected, non-adopted prospective amendment pointers.

## Limitations and reporting language

Use this statement in provenance reporting:

> The executions used Groq with `qwen/qwen3.8-27b` through an account recorded
> as Free Plan with billing disabled. Groq documents the exact model under Free
> Plan limits. No independent transaction-level billing ledger was preserved.

Do not state that Groq independently certified a zero-dollar charge for each
historical request.

The evidentiary audit is recorded in
`docs/PHASE6_REMOTE_PROVENANCE_AUDIT.md`.
