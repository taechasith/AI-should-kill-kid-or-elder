# Phase 4 - Free Cloud Access Blocker

## Status

**Blocked before cloud CARLA execution on 2026-09-27.** This is an access gate,
not an assertion that free Lightning AI execution is unavailable in general.

## Baseline evidence

- Host inspected: local Windows, not a Linux Lightning AI Studio.
- Lightning access signals present: no API key, Studio marker, SSH host,
  teamspace, or workspace environment variable.
- Available cloud-control tools: none for Lightning AI or RunPod.
- The repository remote is configured, but no cloud runtime is attached.
- Existing local CARLA blocker remains preserved in
  `PHASE_4_PHYSICAL_OUTCOME_BLOCKER.md`.
- Unit-test baseline: 11 tests passed.
- No CARLA command, image pull, cloud job, paid infrastructure, or simulator
  data generation has occurred in this session.

## What succeeded

The repository Phase 4 protocol, outcome contract, non-executable template,
cloud setup guide, and local safety boundaries are present and testable.

## What failed

The agent has no Lightning AI Studio shell or non-secret connection method to
inspect a free account's actual GPU credits, hardware, persistent storage,
Docker/NVIDIA availability, or CARLA compatibility. Therefore it cannot select
or run a free execution path without guessing or creating infrastructure.

## Exact minimum user action required

1. Create or sign in to a free Lightning AI account.
2. Create one free Studio.
3. Attach its shell to this session or provide a non-secret SSH connection
   command/host. Do not provide a private-key body, token, password, or payment
   details.

Once connected, the agent will inspect entitlement and runtime facts before
pulling/launching the pinned `carlasim/carla:0.9.16` image. If paid spending is
required or CARLA cannot run, it will record the exact runtime evidence and
stop without fabricating outcomes.
