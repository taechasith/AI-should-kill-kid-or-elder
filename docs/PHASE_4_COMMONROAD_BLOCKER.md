# Phase 4 CommonRoad Blocker

## Status

**Checker installation resolved via GitHub Codespaces on 2026-09-27.** The
native-Windows failure below is preserved as historical evidence. Phase 4 itself
remains unexecuted: no simulator outcome, trajectory, metric, or result summary
has been generated.

## Working local environment

- OS: Windows 10.0.26200.
- Python: 3.10.4 in `.venv-commonroad`.
- Free disk after installation attempts: 21.66 GiB on `C:`.
- Installed and importable: `commonroad-io==2026.1`,
  `commonroad-vehicle-models==3.0.2`, `numpy==2.2.6`, `scipy==1.15.3`,
  `pandas==2.3.3`, `shapely==2.1.2`, and `PyYAML==6.0.3`.

## Required component that failed

`commonroad-drivability-checker` is not installed. This component is required
by the frozen Phase 4 method for CommonRoad collision, road-boundary, and
trajectory-feasibility checking.

Attempts and evidence:

1. Current package release `2025.4.0`: no Windows binary distribution was
   available. Source extraction failed with `WinError 123` because test archive
   paths contain `:` characters, which are invalid in Windows filenames.
2. Compatible fallback `2024.1`: source build was retried with `TEMP` and
   `TMP` set to `C:\\crtmp`. CMake/Visual Studio reached the FCL dependency
   fetch, then failed with `Filename too long` for FCL headers despite the short
   temporary root.

No package was substituted, no collision result was approximated, and no
physical outcome was manually created.

## Minimum safe resolution

Provide a Windows-compatible binary/wheel for the pinned Drivability Checker
stack, or execute the same pipeline in the explicitly authorized GitHub
Codespaces Linux x86_64 environment. WSL is not authorized. A system-wide
Windows long-path policy change may also be evaluated only with explicit
authorization. Until the checker imports successfully in a recorded Linux
execution environment, Phase 4 cannot satisfy its collision/road-boundary/
feasibility exit criteria.

## Authorized resolution path (not yet executed)

GitHub Codespaces on Linux x86_64, CPU-only, is authorized as the reference
execution environment. The repository provides `.devcontainer/devcontainer.json`
and `requirements-commonroad-codespaces.txt`, which request the official
`commonroad-drivability-checker==2025.3.1` manylinux wheel without a source
build. The exact distribution, architecture, Python, resolved package versions,
Git commit, and resolution date must be appended here only after the checker
imports there successfully.

## STATUS: RESOLVED VIA GITHUB CODESPACES

- Linux distribution: Debian GNU/Linux 12 (bookworm).
- Architecture: x86_64.
- Python: 3.10.18.
- Checker: `commonroad-drivability-checker==2025.3.1` (programmatically
  importable).
- CommonRoad packages: `commonroad-io==2024.3`,
  `commonroad-vehicle-models==3.0.2`, `numpy==2.2.6`, `scipy==1.15.3`, and
  `shapely==2.1.2`.
- Git commit: `61c4a5bdf32953bfd6b1571b6c33c0bef34b63c8`.
- Resolution date: 2026-09-27.

The checker was installed from its official CPython 3.10 manylinux wheel. Its
declared `polygon3` dependency built locally because that dependency did not
publish a compatible wheel; the checker itself was not built from source.
