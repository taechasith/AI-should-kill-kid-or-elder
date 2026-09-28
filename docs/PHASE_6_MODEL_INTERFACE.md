# Phase 6 model-interface dry-run gate

Status: `BLOCKED_AUTHORIZATION` — the offline interface and input package are
validated, but no provider request has been sent and Phase 6 is not complete.

## Frozen dry-run boundary

The dry run is pinned to the immutable Phase 4 physical source commit
`d52baab` and the Phase 5 tag `phase5-legal-snapshot-v1`. It reads those
artifacts but neither edits nor reruns them. The six model-visible initial
states are the Cartesian product of the three core scenario families and
30/50 km/h. Seed and action variations are not additional initial scenes;
they are retained only in the physical benchmark and C4 support described
below.

Each base package contains a deterministic 512×512 bird's-eye PNG, telemetry
at `t = 0`, and the six candidate-action control descriptions. It deliberately
excludes trajectories, collision status, TTC, distance, final speed, road
boundary result, feasibility result, and all other future physical outcomes.
The source files and SHA-256 values are listed in:

`data/model_inputs/phase6/phase6_model_interface_v1/input_manifest.json`

Condition contexts are generated from the frozen Phase 5 snapshot. C0 receives
only initial-state scene information. C1 adds only jurisdiction identity. C2
adds structured legal status and evidence sufficiency. C3 is present in the
design but every current row is `not_applicable`: Phase 5 retained source
locators rather than action-level raw or working-translation provision text,
and a locator must not be misrepresented as raw legal evidence. C4 intentionally
adds candidate-action physical consequence summaries and legal uncertainty as
the GeoSAVE support condition; this is its documented, controlled exception to
the no-outcome-leakage boundary.

## Provider-independent contract

`schemas/v1/phase6_model_decision.schema.json` defines the normalized decision
record. The model-returned body contains exactly:

- `decision_status` (`CHOOSE`, `ABSTAIN`, or `INSUFFICIENT_INFORMATION`);
- `selected_action_id` or `null`;
- controlled `stated_factors`;
- structured `legal_claims` and cited evidence IDs;
- an uncertainty statement and short rationale.

The repository then attaches run provenance, parse state, and an append-only
`raw_response_reference`. Parse failure becomes `decision_status: INVALID`; the
parser never selects an action on a model's behalf. One fence-only repair is
allowed. Raw and normalized records reject overwrite attempts.

`geosave/model_adapters.py` supplies offline serializers for OpenAI Responses,
Anthropic Messages, and Mistral Chat. They embed the locally hashed PNG and
provide no `tools`, browser, search, retrieval, or web configuration. These
serializers are unit-tested only; they are not successful remote provider
pilots.

## Candidate panel and execution policy

The pre-result candidate panel is documented in
`configs/models/phase6_model_registry_dry_run_v1.json`:

| Slot | Provider | Exact model ID |
| --- | --- | --- |
| M1 | OpenAI | `gpt-4.1-2025-04-14` |
| M2 | Anthropic | `claude-sonnet-5` |
| M3 | Mistral AI | `mistral-large-2512` |

All three are recorded from official provider documentation as image-plus-text
API candidates. The registry has `execution_enabled: false`, no credentials,
and no authorization claim. It is a frozen dry-run selection to prevent
performance-based model choice; an authorized execution that requires a
different panel must use a new version rather than silently changing it.

## Frozen execution design

`data/model_benchmark/phase6/manifests/phase6_dry_run_v1.json` accounts for
5,454 planned condition rows:

- 54 deduplicated C0 rows;
- 4,050 jurisdictional C1/C2/C4 rows that would be provider-call eligible;
- 1,350 C3 rows explicitly `not_applicable`.

There are therefore 4,104 eligible provider calls for the full design, after
including three repeats. The stratified pilot contains 36 eligible calls: three
scenario/speed packages, C0/C1/C2/C4, three jurisdictions, and three candidate
models. The maximum retry policy is one retry only for transport, temporary
provider, rate-limit, or malformed-output failures; an unwanted selected action
is never retryable.

No model response, token usage, latency, cost charge, raw-output file, or
normalized decision record exists at this gate. `phase6-model-interface-v1` has
not been tagged because the remote adapter pilot has not occurred.
