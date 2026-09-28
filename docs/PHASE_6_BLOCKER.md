# Phase 6 provider-execution blocker

Status: `BLOCKED_AUTHORIZATION`

The repository has completed and validated the offline Phase 6 dry-run:
deterministic scene packages, condition contexts, candidate model registry,
prompt contract, output parser, append-only raw/normalized storage contracts,
offline provider request serialization, run manifests, and a cost estimate.
No provider request was made during this work.

## Exact blocker

No user-authorized paid model API budget or verified quota/access exists for the
three-model Phase 6 pilot.

An environment-variable presence check is not proof of account ownership,
available quota, permission to spend, or authorization to call a provider. No
secret was read, printed, committed, or used. A real adapter pilot would send
external requests and may incur charges, so it is prohibited until this blocker
is explicitly resolved.

## What is required to unblock

1. An explicit authorization to use the frozen 36-call pilot, with a maximum
   spend at least covering its documented estimate (USD 0.225 planning estimate
   or USD 0.450 worst case with one retry per request), or confirmation that the
   selected provider accounts have an authorized non-billable quota.
2. Authorized API access for all three frozen candidate models, or an explicit
   instruction to replace the panel and create a new versioned registry and
   manifest before execution.
3. A decision whether the current C3 limitation should remain `not_applicable`
   or whether a new reviewed legal snapshot with admissible action-level source
   text should be created. The frozen Phase 5 snapshot must not be changed.

Until then, do not create `phase6-model-interface-v1`, do not claim that any
adapter pilot succeeded, and do not begin Phase 7, Phase 8, or Phase 9.
