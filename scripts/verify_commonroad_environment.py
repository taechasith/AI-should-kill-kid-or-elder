"""Report the Phase 4 CommonRoad execution environment without creating data."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform


PACKAGES = (
    "commonroad-drivability-checker",
    "commonroad-io",
    "commonroad-vehicle-models",
    "numpy",
    "scipy",
    "shapely",
)


def package_version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-checker", action="store_true")
    args = parser.parse_args()
    checker_importable = importlib.util.find_spec("commonroad_dc") is not None
    report = {
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "checker_importable": checker_importable,
        "packages": {package: package_version(package) for package in PACKAGES},
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if checker_importable or not args.require_checker else 1


if __name__ == "__main__":
    raise SystemExit(main())
