#!/usr/bin/env python3
"""Offline integrity audit for the append-only KA-IRO execution ledger.

This tool never dispatches a provider request and never repairs scientific
evidence.  Its JSON report is derived from the frozen manifests, attempt
ledger, raw response artifacts, and current observation states.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kairokrisis.execution import Ledger, TERMINAL_STATES, classify
from kairokrisis.serialization import serialized
from scripts.run_kairo_krisis import OUT, rows


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_ref(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def failures(report: dict, name: str) -> list:
    return report.setdefault("failures", {}).setdefault(name, [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write the JSON report atomically")
    args = parser.parse_args()

    all_rows = rows()
    by_id = {row["observation_id"]: row for row in all_rows}
    ledger = Ledger(OUT)
    report: dict = {
        "schema_version": "ka-iro-krisis-execution-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_requests": 0,
        "planned_observations": len(all_rows),
        "planned_by_phase": dict(Counter(row["phase"] for row in all_rows)),
        "failures": {},
    }
    attempts: list[dict] = []
    attempt_paths: set[Path] = set()
    states: dict[str, dict] = {}
    body_integrity_checked = 0
    raw_refs: dict[Path, list[str]] = defaultdict(list)
    terminal_count = 0
    terminal_by_observation: Counter[str] = Counter()
    http_200_by_observation: Counter[str] = Counter()
    parser_states: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()

    for row in all_rows:
        oid = row["observation_id"]
        state = ledger.state(oid)
        states[oid] = state
        state_counts[str(state.get("state", "PLANNED"))] += 1
        if ledger.terminal(oid):
            terminal_count += 1
            if not state.get("terminal_state"):
                failures(report, "terminal_observations_missing_parser_state").append(oid)
        records = ledger.records(oid)
        # Every dispatched observation must still reconstruct its exact amended body.
        if records:
            current = serialized(row, ROOT)
            for field in ("request_body_sha256", "request_body_bytes", "request_envelope_sha256"):
                if current[field] != row.get(field):
                    failures(report, "manifest_request_reconstruction_mismatch").append({"observation_id": oid, "field": field})
            body_integrity_checked += 1
        for record_path, record in zip(ledger.attempts(oid), records):
            attempt_paths.add(record_path.resolve())
            attempts.append(record)
            if record.get("observation_id") != oid:
                failures(report, "attempt_observation_id_mismatch").append(str(record_path))
            ordinal = record.get("attempt_number")
            if record_path.name != f"attempt_{int(ordinal):04}.json":
                failures(report, "attempt_filename_ordinal_mismatch").append(str(record_path))
            # Crash recovery can create a terminal ambiguity record after an
            # ATTEMPT_STARTED token survived a process loss.  There is then no
            # durable response and no proof that bytes reached a provider, so
            # it must not be retroactively populated with request hashes.
            recovered_ambiguity = (
                record.get("transport_result") == "AMBIGUOUS_TRANSPORT_OUTCOME"
                and not record.get("raw_response_reference")
                and record.get("recovery_reason")
            )
            for field in ("provider", "model_id", "request_body_sha256", "planning_object_sha256"):
                expected = row.get(field, row.get("final_request_payload_sha256") if field == "planning_object_sha256" else None)
                if expected is not None and record.get(field) != expected and not (recovered_ambiguity and field in {"request_body_sha256", "planning_object_sha256"}):
                    failures(report, "attempt_frozen_request_mismatch").append({"observation_id": oid, "field": field})
            status = record.get("http_status")
            if status == 200:
                http_200_by_observation[oid] += 1
            if record.get("terminal"):
                terminal_by_observation[oid] += 1
            parsed = str(record.get("parsed_terminal_state"))
            parser_states[parsed] += 1
            raw_ref = record.get("raw_response_reference")
            if raw_ref:
                raw_path = normalized_ref(str(raw_ref))
                raw_refs[raw_path.resolve()].append(str(record_path))
                if not raw_path.is_file():
                    failures(report, "missing_raw_response_artifacts").append(str(record_path))
                else:
                    actual = digest(raw_path)
                    if actual != record.get("raw_response_sha256"):
                        failures(report, "raw_response_hash_mismatches").append(str(record_path))
                    replayed, _ = classify(status, raw_path.read_bytes(), record.get("transport_result", "HTTP_RESPONSE"))
                    # RETRY_EXHAUSTED is a policy-derived terminal state; all other
                    # classifications must reproduce directly from preserved raw bytes.
                    if parsed != "RETRY_EXHAUSTED" and replayed != parsed:
                        failures(report, "offline_parser_mismatches").append({"observation_id": oid, "attempt": ordinal, "stored": parsed, "replayed": replayed})
            elif status is not None:
                failures(report, "ledger_entries_without_raw_artifacts").append(str(record_path))
            if record.get("terminal") and parsed not in TERMINAL_STATES:
                failures(report, "terminal_attempt_invalid_ontology").append(str(record_path))

    raw_files = {path.resolve() for path in (OUT / "raw").glob("**/attempt_*.json")}
    recorded_raw = set(raw_refs)
    report["raw_artifacts_without_ledger_entries"] = sorted(str(path) for path in raw_files - recorded_raw)
    if report["raw_artifacts_without_ledger_entries"]:
        failures(report, "raw_artifacts_without_ledger_entries").extend(report["raw_artifacts_without_ledger_entries"])
    duplicated_raw = {str(path): refs for path, refs in raw_refs.items() if len(refs) > 1}
    if duplicated_raw:
        failures(report, "raw_artifact_references_not_unique").append(duplicated_raw)

    # Discover orphaned attempt records rather than silently ignoring them.
    all_attempt_files = {path.resolve() for path in (OUT / "attempts").glob("**/attempt_*.json")}
    orphan_attempts = all_attempt_files - attempt_paths
    if orphan_attempts:
        failures(report, "out_of_manifest_or_orphan_attempts").extend(sorted(str(path) for path in orphan_attempts))

    duplicate_terminal = sorted(oid for oid, count in terminal_by_observation.items() if count > 1)
    duplicate_success = sorted(oid for oid, count in http_200_by_observation.items() if count > 1)
    if duplicate_terminal:
        failures(report, "duplicate_terminal_observations").extend(duplicate_terminal)
    if duplicate_success:
        failures(report, "observations_with_multiple_http_200").extend(duplicate_success)

    # A second attempt must follow an explicitly retryable predecessor.  Model
    # output classifications are terminal and therefore cannot justify a retry.
    retry_violations = []
    for oid in by_id:
        records = ledger.records(oid)
        for earlier, later in zip(records, records[1:]):
            # A free-quota exhaustion never consumes retry budget.  Resuming
            # that same durable observation after its recorded reset is the
            # expressly frozen scheduling policy, not a model-output retry.
            quota_resume = earlier.get("parsed_terminal_state") == "FREE_QUOTA_EXHAUSTED"
            if not earlier.get("retry_permitted") and not quota_resume:
                retry_violations.append({"observation_id": oid, "earlier_attempt": earlier.get("attempt_number"), "later_attempt": later.get("attempt_number"), "earlier_state": earlier.get("parsed_terminal_state")})
    if retry_violations:
        failures(report, "retry_policy_violations").extend(retry_violations)

    unresolved_started = sorted(oid for oid, state in states.items() if state.get("state") == "ATTEMPT_STARTED")
    report.update({
        "attempted_observations": sum(bool(ledger.records(oid)) for oid in by_id),
        "terminal_observations": terminal_count,
        "remaining_observations": len(all_rows) - terminal_count,
        "total_http_attempts": len(attempts),
        "attempts_per_observation": dict(sorted(Counter(record["observation_id"] for record in attempts).items())),
        "attempt_count_distribution": dict(sorted(Counter(len(ledger.records(oid)) for oid in by_id).items())),
        "http_statuses": dict(sorted(Counter(str(record.get("http_status")) for record in attempts).items())),
        "terminal_states": dict(sorted(parser_states.items())),
        "observation_states": dict(sorted(state_counts.items())),
        "duplicate_terminal_observations": duplicate_terminal,
        "observations_with_multiple_successful_provider_responses": duplicate_success,
        "missing_raw_response_artifacts": len(report["failures"].get("missing_raw_response_artifacts", [])),
        "raw_response_hash_mismatches": len(report["failures"].get("raw_response_hash_mismatches", [])),
        "ledger_entries_without_raw_artifacts": len(report["failures"].get("ledger_entries_without_raw_artifacts", [])),
        "parser_results_without_raw_response_provenance": len(report["failures"].get("offline_parser_mismatches", [])),
        "terminal_observations_missing_parser_state": len(report["failures"].get("terminal_observations_missing_parser_state", [])),
        "retry_deferred_observations": sum(state.get("state") == "RETRY_DEFERRED" for state in states.values()),
        "quota_deferred_observations": sum(state.get("state") == "QUOTA_DEFERRED" for state in states.values()),
        "ambiguous_transport_outcomes": parser_states.get("AMBIGUOUS_TRANSPORT_OUTCOME", 0),
        "unresolved_attempt_started_states": unresolved_started,
        "request_body_reconstructions_verified": body_integrity_checked,
        "raw_response_integrity": "PASS" if not any(key in report["failures"] for key in ("missing_raw_response_artifacts", "raw_response_hash_mismatches", "ledger_entries_without_raw_artifacts", "raw_artifacts_without_ledger_entries", "offline_parser_mismatches")) else "FAIL",
        "request_integrity": "PASS" if not any(key in report["failures"] for key in ("manifest_request_reconstruction_mismatch", "attempt_frozen_request_mismatch", "attempt_observation_id_mismatch")) else "FAIL",
    })
    report["integrity"] = "PASS" if not report["failures"] else "FAIL"
    if args.write:
        target = args.write if args.write.is_absolute() else ROOT / args.write
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(target.suffix + ".tmp")
        temp.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        temp.replace(target)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
