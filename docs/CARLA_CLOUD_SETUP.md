# CARLA 0.9.16 Cloud Setup

## Purpose

Cloud execution replaces the documented local path because the local system has
only 4.59 GiB free and cannot safely host CARLA. Lightning AI is the preferred
free path; actual credits, GPU availability, and storage must be inspected per
account before use. The research repository, not the container image, remains
the source of truth.

## Provisioning requirements

- Provider: Lightning AI Studio or an equivalent truly free Linux environment.
- Image: exactly `carlasim/carla:0.9.16`; never `latest` or 0.10.x.
- GPU: RTX A5000, RTX 3090, RTX 4090, or equivalent 24 GB GPU.
- Storage: at least 50 GB; 70 GB persistent workspace is preferred.
- Repository location: `/workspace/AI-should-kill-kid-or-elder`.

Do not put access tokens, SSH private keys, cloud credentials, CARLA binaries,
model caches, virtual environments, videos, or image sequences in Git.

## Bootstrap after a pod is provided

```bash
nvidia-smi
df -h
find / -name CarlaUE4.sh 2>/dev/null
git clone <repository-ssh-or-authenticated-url> /workspace/AI-should-kill-kid-or-elder
cd /workspace/AI-should-kill-kid-or-elder
python3.10 -m venv .venv-carla
. .venv-carla/bin/activate
```

Use the CARLA Python API shipped by the pinned image/server. Before any run,
programmatically require both client and server versions to equal `0.9.16`.

Start the server from the discovered CARLA root:

```bash
./CarlaUE4.sh -RenderOffScreen -nosound -quality-level=Low -carla-rpc-port=2000
```

The client and server must remain on the same pod and use `localhost:2000`.
Use Town05 only. Do not install AdditionalMaps for this pilot.

## Persistent-output and shutdown rules

Write each completed/failed run and trajectory to persistent workspace storage
before moving to the next run. Preserve failures with a structured type and
message. Stop the pod after artifacts are flushed and synchronize only the
repository-safe outputs; never commit secrets or heavyweight CARLA assets.

## Current external blocker

This session has no attached Lightning AI Studio, endpoint, SSH host, or
Lightning control/API credential. Create a free Studio and attach its shell or
provide a non-secret connection method before executing the commands above.
