"""Collect reproducible WHO 2023 country-profile context without classifying law.

The collector writes processed values and per-profile SHA-256 hashes. Downloaded
PDFs are a regenerable local cache and intentionally are not a benchmark legal
source; the result is explicitly context-only.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "data" / "legal" / "phase5" / "global_context"
RAW = OUTDIR / "raw"
COUNTRY_API = "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues?%24top=500&%24format=json"
PROFILE_URL = "https://cdn.who.int/media/docs/default-source/country-profiles/road-safety/road-safety-2023-{iso3}.pdf?download=true"
MASTER_SOURCE = "https://www.who.int/publications/i/item/9789240087712"
RETRIEVED_AT = date.today().isoformat()


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "GeoSAVE-research/phase5 (public-source collector)"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.split())
    return None if value in {"", "-", "N/A", "- N/A"} else value


def capture(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return clean(match.group(1)) if match else None


def parse_profile(pdf: bytes, country: dict) -> dict[str, str | None]:
    text = PdfReader(io.BytesIO(pdf)).pages[0].extract_text() or ""
    estimated_fatalities = capture(
        text,
        r"WHO estimated road traffic fatalities \(95% CI\) \(year\)\s+([0-9 ][0-9 ]*)\s+\(95%",
    )
    estimated_rate = capture(text, r"WHO estimated rate per 100 000 population \(year\)\s+([^\n]+?)\s*\(\d{4}\)")
    return {
        "iso3": country["Code"],
        "country": country["Title"],
        "who_region": country.get("ParentTitle"),
        "profile_url": PROFILE_URL.format(iso3=country["Code"].lower()),
        "source_sha256": hashlib.sha256(pdf).hexdigest(),
        "profile_available": "true",
        "profile_reference_year": "2023",
        "who_estimated_road_traffic_fatalities": estimated_fatalities,
        "who_estimated_rate_per_100k": estimated_rate,
        "national_speed_limit_law": capture(text, r"National law setting a speed limit\s+([^\n]+)"),
        "max_urban_speed_kph": capture(text, r"Maximum urban speed limit\s+([^\n]+)"),
        "max_rural_speed_kph": capture(text, r"Maximum rural speed limit\s+([^\n]+)"),
        "max_motorway_speed_kph": capture(text, r"Maximum motorway speed limit\s+([^\n]+)"),
        "national_drink_driving_law": capture(text, r"National law on drink-driving\s+([^\n]+)"),
        "national_seat_belt_law": capture(text, r"National seat-belt law\s+([^\n]+)"),
        "national_child_restraint_law": capture(text, r"National child restraints use law\s+([^\n]+)"),
        "national_motorcycle_helmet_law": capture(text, r"National motorcycle helmet law\s+([^\n]+)"),
        "retrieved_at": RETRIEVED_AT,
        "context_only": "true",
    }


def collect_one(country: dict) -> tuple[dict, dict | None]:
    url = PROFILE_URL.format(iso3=country["Code"].lower())
    try:
        pdf = fetch(url)
        RAW.mkdir(parents=True, exist_ok=True)
        (RAW / f"road-safety-2023-{country['Code'].lower()}.pdf").write_bytes(pdf)
        return {"iso3": country["Code"], "status": "collected", "url": url}, parse_profile(pdf, country)
    except (HTTPError, URLError, TimeoutError, ValueError, IndexError) as error:
        return {
            "iso3": country["Code"], "status": "unavailable_or_unparseable", "url": url,
            "error_type": type(error).__name__, "error": str(error), "retrieved_at": RETRIEVED_AT,
        }, None


def write_json(path: Path, payload: object) -> None:
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    countries = json.loads(fetch(COUNTRY_API))["value"]
    countries = sorted(countries, key=lambda country: country["Code"])
    results: list[dict] = []
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(collect_one, country): country["Code"] for country in countries}
        for future in as_completed(futures):
            result, row = future.result()
            results.append(result)
            if row is not None:
                rows.append(row)
    rows.sort(key=lambda row: row["iso3"])
    results.sort(key=lambda item: item["iso3"])
    fieldnames = list(rows[0]) if rows else []
    with (OUTDIR / "who_road_safety_2023_context_v1.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    failures = "".join(json.dumps(result, sort_keys=True) + "\n" for result in results if result["status"] != "collected")
    (OUTDIR / "who_road_safety_2023_collection_failures.jsonl").write_bytes(failures.encode("utf-8"))
    write_json(OUTDIR / "who_road_safety_2023_acquisition_manifest.json", {
        "schema_version": "phase5-who-global-context-v1",
        "authority": "World Health Organization",
        "master_source_url": MASTER_SOURCE,
        "country_dimension_api": COUNTRY_API,
        "profile_url_pattern": PROFILE_URL,
        "retrieved_at": RETRIEVED_AT,
        "context_only": True,
        "action_level_legal_classification_prohibited": True,
        "country_dimension_count": len(countries),
        "collected_profile_count": len(rows),
        "unavailable_or_unparseable_count": len(results) - len(rows),
        "processed_file": "who_road_safety_2023_context_v1.csv",
        "raw_cache": "raw/ (not committed; regenerate with this script)",
    })
    print(f"WHO global context: {len(rows)} profiles collected; {len(results) - len(rows)} unavailable or unparseable")


if __name__ == "__main__":
    sys.exit(main())
