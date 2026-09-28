# Phase 6 free-panel preflight

Status: `PREFLIGHT_PENDING_CREDENTIALS` — no provider request has been made.

`phase6-free-v1` preserves the frozen Phase 4 physical benchmark (`d52baab`),
the frozen Phase 5 legal snapshot (`phase5-legal-snapshot-v1`), the existing
Phase 6 dry-run, and the original three-repeat main-matrix policy.

## Current verification record

| Check | Result |
| --- | --- |
| `GEMINI_API_KEY` presence | not present in this execution environment |
| `GROQ_API_KEY` presence | not present in this execution environment |
| Account Free Tier / Free Plan | not verifiable without authenticated access |
| Billing disabled | not verifiable without authenticated access |
| Exact model access | provider-documented, account-unverified |
| Image-plus-text live acceptance | not tested |
| Current account rate limits | not verifiable without authenticated access |
| Provider calls | 0 |
| Monetary expenditure | USD 0.00 / THB 0.00 |

The absence of these credentials is not converted into a failed benchmark row;
no benchmark execution has started. It blocks only the three-call capability
pilot.

## Frozen planning artifacts

The offline preflight generates:

- 5,454 planned rows;
- 4,104 rows pending free-access preflight;
- 1,350 C3 rows correctly `not_applicable` because retained action-level raw
  legal text is absent;
- exactly 3 unsent multimodal capability-pilot rows; and
- zero provider outputs, raw responses, normalized decisions, or charges.

Run the offline checks:

```text
python scripts/build_phase6_free_v1_preflight.py
python scripts/validate_phase6_free_v1_preflight.py
python scripts/finalize_phase6_free_v1_preflight.py
python scripts/verify_phase6_free_v1_preflight_hashes.py
```

The preflight is not Phase 6 completion. The next permitted step is a live
account-access verification after both user-managed secret names exist in the
authorized Codespace environment.
