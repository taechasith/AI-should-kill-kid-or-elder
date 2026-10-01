# Phase 6 remote provenance audit

Status: `RETAIN_WITH_LIMITATION`
Audit date: 2026-10-02
Audit mode: read-only Git-object inspection; no checkout, merge, rebase, push,
provider request, or simulation rerun.

## Scope

The audited remote reference is `origin/phase4-ks-validation` at
`ccc75232f29709fa8f9f1a0648e6d8322a9c1a75`. The local prospective amendment
is protected at both `backup/phase6-v2a-amendment` and
`phase6-v2a-amendment-local`, each resolving to `58f10b9`.

The shared history is:

```text
498e62a  Phase 6 v2 metadata-preflight record
58f10b9  prospective v2a OpenRouter :free amendment
04fab96  remote Phase 6 v2 pilot completion
c135911  remote Phase 7 preregistration
...       remote Phase 7 execution/provenance commits
ccc7523  remote terminal-executor stop
```

## Phase 6 execution provenance

Remote commit `04fab96` creates exactly three Phase 6 pilot attempts. Its
frozen manifest and M3 attempt record state:

```text
run_id:    P6V2-M3-PED-CROSS-001__V030-ARG-C2-R01
provider:  groq
model_id:  qwen/qwen3.8-27b
HTTP:      200
```

The immutable raw M3 envelope also records `model` as
`qwen/qwen3.8-27b`, an `x_groq` request identifier, and `service_tier` as
`on_demand`. The runner source at the same commit routes a non-Gemini row to
`https://api.groq.com/openai/v1/chat/completions` using `GROQ_API_KEY`.

The contemporaneous account-attestation artifact says that this Groq model was
available under a Free Plan with billing disabled and quota available. No
provider billing record is present in the preserved response, so the artifact
does not independently prove a zero monetary charge.

### Endpoint determination

| Question | Determination |
| --- | --- |
| Was OpenRouter used for the accepted Phase 6 Qwen call? | No. |
| Was `qwen/qwen3.8-27b:free` requested? | No. |
| Was the paid OpenRouter `qwen/qwen3.8-27b` endpoint requested? | Not established; the provider was Groq, not OpenRouter. |
| Does the call comply with the prospective v2a OpenRouter `:free` route? | No. It used the superseded Groq v2 route. |
| Is original Groq free-plan eligibility independently demonstrated by provider billing data? | No; it is account-owner-attested, not provider-billing-proven. |

OpenRouter's current price distinction must not be transferred across provider
identities. It establishes that the two *OpenRouter* endpoint slugs differ;
it does not prove what Groq charged. Groq's current rate-limit documentation
lists the exact Qwen identifier under Free Plan Limits, while its model page
independently confirms the same model identifier and text-plus-image input.
Those public facts support the historical Free Plan eligibility classification,
but do not create transaction-level billing evidence.

External source verification performed on 2026-10-02:

* https://console.groq.com/docs/rate-limits
* https://console.groq.com/docs/model/qwen/qwen3.8-27b

## Phase 7 dependency trace

The tagged `geosave-phase7-preregistration-v1` points to `c135911`, whose
manifest declares the Phase 6 pilot tag
`phase6-literature-v2-pilot-v1` (pointing to `04fab96`). Every M3 manifest row
uses the same original route:

```text
provider: Groq
model_id: qwen/qwen3.8-27b
```

There are 1,818 M3 manifest rows: 1,368 provider-execution rows and 450
not-applicable rows. At the audited remote tip, 20 M3 attempt records exist:

| M3 attempt result | Count |
| --- | ---: |
| completed, HTTP 200 | 11 |
| quota deferred, HTTP 429 | 8 |
| failed, HTTP 429 | 1 |
| OpenRouter or `:free` attempt records | 0 |

Thus 11 accepted Phase 7 Qwen observations and 9 nonterminal/failed Qwen
attempts depend on the original Groq route. Gemini observations are a distinct
stratum and contain no Qwen endpoint dependency.

## Tags and affected artifacts

The tags containing `04fab96` are:

* `phase6-literature-v2-pilot-v1` — directly points to `04fab96`;
* `geosave-phase7-preregistration-v1` — is downstream at `c135911`.

Affected remote paths include:

* `configs/experiments/phase6_literature_v2_pilot_manifest.json`;
* `data/model_benchmark/phase6_literature_v2/attempts/P6V2-M3-PED-CROSS-001__V030-ARG-C2-R01.json`;
* `data/model_benchmark/phase6_literature_v2/raw/P6V2-M3-PED-CROSS-001__V030-ARG-C2-R01.txt`;
* `data/model_benchmark/phase7_literature_v2/manifests/phase7_literature_v2_manifest.json`;
* all `data/model_benchmark/phase7_literature_v2/attempts/P7V2-M3-*` and
  corresponding raw-response paths.

## Conclusion

The remote lineage is **not evidence that OpenRouter's explicit free endpoint
was used**. It is also **not evidence that OpenRouter's priced endpoint was
used**: the actual provider was Groq. The historical zero-cost claim is
supported at the plan level by (1) the preserved Free Plan/billing-disabled
account attestation and (2) Groq's public Free Plan listing for the exact
model. It is not supported by a preserved transaction-level billing ledger.

The audit classification is therefore:

```text
historical_provider = GROQ
historical_model = qwen/qwen3.8-27b
exact_model_identity = CONFIRMED
free_plan_availability = EXTERNALLY_SUPPORTED
account_free_plan_status = ATTESTED
billing_evidence = PLAN_LEVEL_SUPPORTED_TRANSACTION_LEVEL_UNVERIFIED
historical_protocol_validity = RETAIN
v2a_openrouter_compliance = NOT_APPLICABLE_TO_HISTORICAL_RUN
```

No historical data should be deleted, rewritten, or rerun solely because of
the later prospective OpenRouter amendment. The separate decision record
`docs/PHASE6_QWEN_PROVENANCE_DECISION.md` defines the disposition of that
amendment and this historical lineage.
