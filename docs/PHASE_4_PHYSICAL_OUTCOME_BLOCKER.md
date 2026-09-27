# Phase 4 - Physical Outcome Matrix Blocker

## Status

**Blocked before simulation execution on 2026-09-27.**

## Local preflight evidence

- Python 3.10 is available.
- Docker CLI is installed, but its daemon is unavailable.
- No CARLA Python module, CARLA process, local CARLA image, or repository
  simulator asset was found.
- The repository contains three validated pilot scenarios but no simulator
  adapter, CARLA version pin, map assets, or executable server endpoint.

## Authorized-installation preflight, 2026-09-27

The user authorized the official Windows x64 CARLA `0.9.16` prebuilt binary,
Town05, synchronous 0.05-second stepping, and the bounded `carla-pilot-v1`
matrix. The official CARLA release page exposes a Windows `CARLA_0.9.16.zip`
artifact. The only local volume (`C:`) has **4.59 GiB free** and no alternate
local volume is available. This is not a safe target for downloading and
extracting the server binary, so no partial download or installation was
started.

The canonical execution specification is preserved in
`docs/PHASE_4_PILOT_PROTOCOL.md`. The configuration remains the non-executable
template until an installation has actually passed programmatic verification.

No CARLA package/image was downloaded, no server was started, and no physical
outcome was produced.

## Cloud-execution blocker, 2026-09-27

Local execution is superseded by an authorized RunPod cloud pilot using the
pinned `carlasim/carla:0.9.16` image. This session has no provisioned RunPod
pod, RunPod API key, pod ID, endpoint, SSH host, or RunPod control capability.
No matching tool is available in this runtime. Therefore no cloud bootstrap,
CARLA connection, or simulator run can be attempted yet.

**Exact action required:** provision a persistent RunPod pod with the pinned
image and at least 50 GB storage, then connect it to this session or provide a
non-secret SSH/agent-access method. Once available, the frozen cloud protocol
and health gates can be executed without changing the pilot scope.

## Free-cloud supersession, 2026-09-27

The preferred no-paid-spending route is now Lightning AI Studio. The RunPod
section remains historical evidence only and is not an instruction to create
paid infrastructure. See `PHASE_4_FREE_CLOUD_BLOCKER.md` for the current
Lightning access gate. No cloud execution has yet occurred.

## Prepared, non-executable assets

- `configs/simulator/carla_pilot_v1.template.json` lists the required run
  identity and metrics but sets `configuration_status` to
  `template_not_executable`.
- `geosave.contracts.validate_physical_outcome` accepts completed records only
  with required metrics and accepts failed records only with a failure reason.
- `tests/fixtures/physical_outcome_completed.json` is schema smoke-test data
  only, not research evidence.

## What is needed to unblock

1. A user-approved, version-pinned CARLA server and matching Python API.
2. A functioning local Docker daemon or another explicitly approved local CARLA
   installation path.
3. A CARLA map/vehicle/sensor adapter and a reproducible scenario-to-CARLA
   mapping.
4. For any scale beyond the single pilot, explicit approval of the planned
   `scene x action x seed` count and compute/storage estimate.

After these prerequisites are available, run one local pilot first, preserve
both completed and failed records, and validate joins using
`scenario_id x variant_id x action_id x seed`.
