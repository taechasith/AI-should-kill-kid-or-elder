"""Validate the append-only, failed Phase 6 free-pilot evidence."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "model_benchmark" / "phase6_free_v1"
ATTEMPTS = BASE / "attempts"
OUTPUT = ROOT / "data" / "validation" / "phase6_free_v1_pilot_validation.json"

EXPECTED = {
    "P6F-M1-PED-CROSS-001__V030-ARG-C2-R01": ("gemini-3.6-flash", "TRANSPORT_ERROR", None, None),
    "P6F-M1-PED-CROSS-001__V030-ARG-C2-R01__retry1": ("gemini-3.6-flash", "MALFORMED_RESPONSE", 200, "failed"),
    "P6F-M2-PED-CROSS-001__V030-ARG-C2-R01": ("gemini-2.5-flash-lite", "PROVIDER_HTTP_ERROR", 404, None),
    "P6F-M2-PED-CROSS-001__V030-ARG-C2-R01__retry1": ("gemini-2.5-flash-lite", "PROVIDER_HTTP_ERROR", 404, None),
    "P6F-M3-PED-CROSS-001__V030-ARG-C2-R01": ("qwen/qwen3.8-27b", "MALFORMED_RESPONSE", 200, "failed"),
    "P6F-M3-PED-CROSS-001__V030-ARG-C2-R01__retry1": ("qwen/qwen3.8-27b", "MALFORMED_RESPONSE", 200, "failed"),
}


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _assert_hash(path: Path, expected: str) -> None:
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Missing or mismatched append-only artifact: {_relative(path)}")


def validate() -> dict[str, object]:
    paths = {path.stem: path for path in ATTEMPTS.glob("*.json")}
    if set(paths) != set(EXPECTED):
        raise ValueError("Phase 6 pilot attempt set is incomplete or contains an unexpected row")
    summary: list[dict[str, object]] = []
    for attempt_id, expected in sorted(EXPECTED.items()):
        model_id, failure_reason, http_status, parse_status = expected
        record = _load(paths[attempt_id])
        if record.get("model_id") != model_id or record.get("failure_reason") != failure_reason or record.get("http_status") != http_status:
            raise ValueError(f"Unexpected result classification: {attempt_id}")
        if record.get("status") != "failed" or record.get("run_id") != attempt_id.removesuffix("__retry1"):
            raise ValueError(f"Attempt result is not an explicit failed record: {attempt_id}")
        if attempt_id.endswith("__retry1"):
            if record.get("attempt_id") != attempt_id or record.get("attempt_number") != 2:
                raise ValueError(f"Retry provenance is invalid: {attempt_id}")
        raw_reference = record.get("raw_response_reference")
        if raw_reference is not None:
            _assert_hash(ROOT / str(raw_reference), str(record.get("raw_response_sha256")))
        normalized_reference = record.get("normalized_response_reference")
        if parse_status is None:
            if normalized_reference is not None:
                raise ValueError(f"Unexpected normalized output: {attempt_id}")
        else:
            normalized = ROOT / str(normalized_reference)
            _assert_hash(normalized, str(record.get("normalized_response_sha256")))
            normalized_record = _load(normalized)
            if normalized_record.get("parse_status") != parse_status or normalized_record.get("decision_status") != "INVALID":
                raise ValueError(f"Malformed output was not normalized safely: {attempt_id}")
        summary.append({"attempt_id": attempt_id, "model_id": model_id, "failure_reason": failure_reason, "http_status": http_status})
    return {
        "schema_version": "phase6-free-pilot-validation-v1",
        "validation_status": "passed",
        "phase6_status": "BLOCKED_FROZEN_PANEL",
        "planned_pilot_rows": 3,
        "model_generation_requests_attempted": 6,
        "completed_rows": 0,
        "failed_rows": 3,
        "retry_attempts": 3,
        "not_applicable_rows": 0,
        "raw_response_files": 4,
        "normalized_record_files": 3,
        "no_model_response_fabricated": True,
        "records": summary,
        "next_permitted_step": "Create a new explicitly authorized Phase 6 panel and manifest; do not alter this frozen failed pilot.",
    }


if __name__ == "__main__":
    result = validate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Phase 6 free pilot validation: {result['validation_status']}; {result['failed_rows']} failed rows, {result['retry_attempts']} retries")
