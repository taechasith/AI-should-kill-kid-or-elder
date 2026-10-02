"""Freeze the prospective KA-IRO KRISIS v2 K4 provider/interface panel.

The program is deliberately unable to call a model-generation endpoint.  It
only combines an append-only metadata probe with the non-secret account-owner
attestation already recorded in the repository.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "data" / "ka-iro-krisis" / "v2" / "model"
ATTESTATION_PATH = ROOT / "data" / "validation" / "phase6_literature_v2_account_attestation.json"
OUTPUT_PATH = MODEL_DIR / "k4_model_interface_manifest.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT_PATH.exists():
        raise SystemExit(f"refusing to overwrite frozen K4 manifest: {OUTPUT_PATH.relative_to(ROOT)}")
    candidates = sorted((MODEL_DIR / "k4_metadata_preflights").glob("*/k4_metadata_preflight.json"))
    if not candidates:
        raise SystemExit("no K4 metadata evidence found")
    metadata_path = candidates[-1]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    attestation = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))
    if not metadata["all_target_models_listed"] or metadata["model_generation_requests_made"] != 0:
        raise SystemExit("metadata evidence is not a successful zero-generation model-list preflight")

    attested = {row["provider"]: row for row in attestation["providers"]}
    expected = {
        "gemini": {"gemini-3.5-flash", "gemini-3.5-flash-lite"},
        "groq": {"qwen/qwen3.8-27b"},
    }
    for provider, models in expected.items():
        row = attested.get(provider)
        if not row or not row["quota_available"] or row["billing_enabled"]:
            raise SystemExit(f"free-only account attestation fails for {provider}")
        if set(row["verified_model_ids"]) != models:
            raise SystemExit(f"attested model set differs for {provider}")

    timestamp = datetime.now(timezone.utc).isoformat()
    panel = [
        {
            "slot": "M1",
            "provider": "Google Gemini API",
            "provider_key": "gemini",
            "model_id": "gemini-3.5-flash",
            "model_family": "Gemini 3.5 Flash",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
            "modality": {"input": ["text", "image"], "output": ["text"]},
            "strict_output_method": "responseMimeType=application/json; schema-free exact JSON contract",
        },
        {
            "slot": "M2",
            "provider": "Google Gemini API",
            "provider_key": "gemini",
            "model_id": "gemini-3.5-flash-lite",
            "model_family": "Gemini 3.5 Flash Lite",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
            "modality": {"input": ["text", "image"], "output": ["text"]},
            "strict_output_method": "responseMimeType=application/json; schema-free exact JSON contract",
        },
        {
            "slot": "M3",
            "provider": "Groq",
            "provider_key": "groq",
            "model_id": "qwen/qwen3.8-27b",
            "model_family": "Qwen 3.8 27B",
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "modality": {"input": ["text", "image"], "output": ["text"]},
            "strict_output_method": "response_format.type=json_object",
        },
    ]
    manifest = {
        "schema_version": "ka-iro-krisis-v2-k4-model-interface-manifest-v1",
        "project_id": "ka-iro-krisis-v2",
        "gate": "K4",
        "status": "FROZEN_BEFORE_K5_GENERATION",
        "frozen_at_utc": timestamp,
        "historical_missing_credential_record": "data/ka-iro-krisis/v2/model/k4_metadata_preflight.json",
        "metadata_preflight": {
            "path": metadata_path.relative_to(ROOT).as_posix(),
            "sha256": digest(metadata_path),
            "authenticated_exact_models_visible": True,
            "metadata_generation_requests": 0,
        },
        "account_plan_evidence": {
            "path": ATTESTATION_PATH.relative_to(ROOT).as_posix(),
            "sha256": digest(ATTESTATION_PATH),
            "status": "ACCOUNT_OWNER_ATTESTATION",
            "scope": "exact panel; Free Tier/Free Plan; billing disabled; quota available",
            "limitation": "provider metadata cannot independently certify account tier or a per-request monetary charge",
        },
        "monetary_policy": {
            "budget_usd": "0.00",
            "budget_thb": "0.00",
            "free_only": True,
            "paid_fallback": "PROHIBITED",
            "tier_upgrade": "PROHIBITED",
            "purchase_credits": "PROHIBITED",
            "on_payment_required": "record PAID_ACCESS_REQUIRED and stop that route",
            "on_quota_exhausted": "record FREE_QUOTA_EXHAUSTED and stop or wait for the free reset",
        },
        "panel": panel,
        "interfaces": {
            "NATURAL_EXPLICIT_ACTION": "one exact allowlisted action plus brief rationale in plain text",
            "STRICT_STRUCTURED_OUTPUT": "one JSON object with exactly selected_action_id and rationale fields; JSON validity and action validity are assessed separately",
        },
        "representations": ["MULTIMODAL_IMAGE_PLUS_CONTEXT", "TEXT_ONLY_EQUIVALENT_CONTEXT"],
        "generation_parameters": {"temperature": 0, "max_output_tokens": 256, "tools": "DISABLED", "grounding_search_retrieval": "DISABLED"},
        "retry_policy": {
            "automatic_transport_retries": 0,
            "maximum_explicit_attempts_per_run_id": 2,
            "retryable_states": ["HTTP_FAILURE", "TIMEOUT", "PROVIDER_REJECTION", "FREE_QUOTA_EXHAUSTED"],
            "rule": "Every HTTP request is a separate immutable attempt. Never retry based on content or regenerate a terminal HTTP-200 result.",
        },
        "replacement_rule": "No replacement after this freeze. Record endpoint unavailability and stop the affected stratum.",
        "next_gate": "K5 requires a prospective execution manifest, frozen rendered/image and text-equivalent inputs, and a probability-sampling plan if the 1,440-call target is infeasible under the free quotas.",
    }
    OUTPUT_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": manifest["status"], "path": OUTPUT_PATH.relative_to(ROOT).as_posix(), "generation_requests_made": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
