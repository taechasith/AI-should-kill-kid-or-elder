# Phase 4 Codespaces Execution Record

GitHub Codespaces on Linux x86_64, CPU-only, is the reference execution
environment authorized for Phase 4. It replaces only the blocked native Windows
execution path. WSL, CARLA, paid compute, and Phase 5 work are out of scope.

## Create the environment

Create a Codespace from the repository's `main` branch after the Phase 4 files
are present on that branch. The supplied `.devcontainer/devcontainer.json` uses
Python 3.10 and installs only binary wheels from
`requirements-commonroad-codespaces.txt`; it must not build the checker from
source.

At the Codespace terminal, record:

```bash
git status
git rev-parse HEAD
python --version
uname -a
df -h
python scripts/verify_commonroad_environment.py --require-checker
python -m unittest discover -s tests -v
```

The last command in the first block both checks `commonroad_dc` programmatically
and prints the package versions needed for the blocker-resolution record.

## Resolution boundary

Append `STATUS: RESOLVED VIA GITHUB CODESPACES` to
`PHASE_4_COMMONROAD_BLOCKER.md` only when the checker import, package-version
record, and baseline tests have succeeded in that Linux environment. Include
the Linux distribution, architecture, Python version, Git commit, checker and
CommonRoad package versions, and date. Retain the native-Windows failure
evidence.

Do not generate any trajectory or pilot outcome until all Phase 4 implementation
and determinism gates in `PHASE_4_PILOT_PROTOCOL.md` pass.
