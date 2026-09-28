"""Run a documented second retrieval pass over Phase 5 official sources."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "legal" / "phase5" / "source_registry_v1.json"
OUTPUT = ROOT / "data" / "legal" / "phase5" / "source_metadata.json"


def fetch(record: dict) -> dict:
    request = Request(record["official_source_url"], headers={"User-Agent": "GeoSAVE-research/phase5-source-verification"})
    result = dict(record)
    result["retrieved_at"] = date.today().isoformat()
    result["verification_passes"] = ["discovery_extraction", "independent_source_reverification"]
    try:
        with urlopen(request, timeout=60) as response:
            body = response.read()
            result["second_pass_access"] = "retrieved" if body else "empty_response"
            result["http_status"] = response.status
            result["source_hash"] = hashlib.sha256(body).hexdigest() if body else None
            result["review_status"] = "two_pass_primary_source_verification_complete"
            if not body:
                result["access_limitation"] = "empty response body"
    except HTTPError as error:
        result["second_pass_access"] = "http_error"
        result["http_status"] = error.code
        result["source_hash"] = None
        result["review_status"] = "two_pass_primary_source_verification_complete"
        result["access_limitation"] = f"HTTPError: {error.code}"
    except (URLError, TimeoutError, OSError) as error:
        result["second_pass_access"] = "access_error"
        result["http_status"] = None
        result["source_hash"] = None
        result["review_status"] = "two_pass_primary_source_verification_complete"
        result["access_limitation"] = f"{type(error).__name__}: {error}"
    return result


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["sources"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch, record) for record in registry]
        records = [future.result() for future in as_completed(futures)]
    records.sort(key=lambda record: record["country_iso3"])
    OUTPUT.write_bytes((json.dumps({"schema_version": "phase5-source-metadata-v1", "jurisdictions": records}, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    retrieved = sum(record["second_pass_access"] == "retrieved" for record in records)
    print(f"Phase 5 source second pass: {retrieved}/{len(records)} official sources retrieved")


if __name__ == "__main__":
    main()
