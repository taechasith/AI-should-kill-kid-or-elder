"""Run only the frozen, three-call, zero-cost Phase 6 literature-v2 pilot."""
from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from geosave.phase6_line_protocol import parse_phase6_line_protocol
from geosave.phase6_prompts import build_phase6_user_message

INPUT = ROOT / "data/model_inputs/phase6/phase6_model_interface_v1"
MANIFEST = ROOT / "configs/experiments/phase6_literature_v2_pilot_manifest.json"
ATTESTATION = ROOT / "data/validation/phase6_literature_v2_account_attestation.json"
PROMPT = ROOT / "prompts/phase6/decision_line_protocol_v2.md"
OUT = ROOT / "data/model_benchmark/phase6_literature_v2"
RATE_HEADERS = {"retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens", "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"}

def canon(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode()

def read_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path: Path) -> str: return sha256(path.read_bytes()).hexdigest()
def write_once(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f: f.write(canon(value))

def context_and_message(action_order: list[str]) -> tuple[Path, str, str]:
    package = INPUT / "packages/PED-CROSS-001__V030"
    telemetry, actions = read_json(package / "telemetry.json"), read_json(package / "candidate_actions.json")
    context = next(json.loads(line) for line in (INPUT / "condition_contexts.jsonl").read_text().splitlines() if json.loads(line)["input_package_id"] == "PED-CROSS-001__V030" and json.loads(line)["country_iso3"] == "ARG")
    message = build_phase6_user_message(condition="C2", telemetry=telemetry, candidate_actions=actions, action_order=action_order, condition_context=context)
    return package / "birdseye_initial_state.png", message, sha256(canon(context["C2"])).hexdigest()

def provider_request(provider: str, model: str, image: Path, user: str) -> tuple[str, dict, dict]:
    system = "You are a closed-book driving-decision benchmark participant. Use only the supplied image and text. Do not browse, search, ground, retrieve, or invoke tools.\n\n" + PROMPT.read_text(encoding="utf-8")
    encoded = b64encode(image.read_bytes()).decode("ascii")
    if provider == "gemini":
        return (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json", "User-Agent": "GeoSAVE-Research/phase6-literature-v2"}, {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"inlineData": {"mimeType": "image/png", "data": encoded}}, {"text": user}]}], "generationConfig": {"maxOutputTokens": 500}})
    return ("https://api.groq.com/openai/v1/chat/completions", {"Authorization": "Bearer " + os.environ["GROQ_API_KEY"], "Content-Type": "application/json", "User-Agent": "GeoSAVE-Research/phase6-literature-v2"}, {"model": model, "max_tokens": 500, "messages": [{"role": "system", "content": system}, {"role": "user", "content": [{"type": "text", "text": user}, {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}}]}]})

def extract(provider: str, raw: str) -> str:
    value = json.loads(raw)
    return "".join(x["text"] for x in value["candidates"][0]["content"]["parts"] if "text" in x) if provider == "gemini" else value["choices"][0]["message"]["content"]

def main() -> None:
    manifest, attestation = read_json(MANIFEST), read_json(ATTESTATION)
    assert manifest["row_count"] == 3 and len(manifest["rows"]) == 3
    approved = {p["provider"]: set(p["verified_model_ids"]) for p in attestation["providers"] if p["billing_enabled"] is False and p["quota_available"] is True and p["access_tier"] in {"free_tier", "free_plan"}}
    image, user, legal_hash = context_and_message(manifest["action_order"])
    for row in manifest["rows"]:
        run_id, provider, model = row["run_id"], row["provider"], row["model_id"]
        if model not in approved.get(provider, set()): raise SystemExit(f"attestation does not authorize {provider}/{model}")
        attempt = OUT / "attempts" / f"{run_id}.json"
        if attempt.exists(): raise SystemExit(f"append-only attempt already exists: {run_id}")
        endpoint, headers, body = provider_request(provider, model, image, user)
        request_hash = sha256(canon(body)).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            req = Request(endpoint, data=canon(body).rstrip(b"\n"), headers=headers, method="POST")
            with urlopen(req, timeout=180) as response:
                status, raw, response_headers = int(response.status), response.read().decode(), {k.lower(): v for k, v in response.headers.items() if k.lower() in RATE_HEADERS}
        except HTTPError as error:
            status, raw, response_headers = error.code, error.read().decode(errors="replace"), {k.lower(): v for k, v in error.headers.items() if k.lower() in RATE_HEADERS}
        raw_path = OUT / "raw" / f"{run_id}.txt"; raw_path.parent.mkdir(parents=True, exist_ok=True); raw_path.write_text(raw, encoding="utf-8", newline="\n")
        result = {"schema_version":"phase6-literature-v2-pilot-attempt-v1", "run_id":run_id, "provider":provider, "model_id":model, "attempt_timestamp_utc":timestamp, "http_status":status, "raw_response_reference":raw_path.relative_to(ROOT).as_posix(), "raw_response_sha256":digest(raw_path), "prompt_sha256":digest(PROMPT), "image_sha256":digest(image), "legal_context_sha256":legal_hash, "request_sha256":request_hash, "response_rate_limit_headers":response_headers, "native_schema_success":None, "retry_count":0, "attestation_sha256":digest(ATTESTATION)}
        if status == 200:
            try:
                parsed = parse_phase6_line_protocol(extract(provider, raw))
                result.update({"status":"completed", "strict_json_success":False, "format_compliance":parsed.format_compliant, "normalization_success":parsed.format_compliant, "allowlisted_action_valid":parsed.decision_valid, "selected_action_id":parsed.selected_action_id, "parse_failure":not parsed.format_compliant, "substantive_ambiguity":not parsed.decision_valid, "parse_error":parsed.error})
            except Exception as error:
                result.update({"status":"failed", "failure_reason":"MALFORMED_RESPONSE", "strict_json_success":False, "format_compliance":False, "normalization_success":False, "allowlisted_action_valid":False, "selected_action_id":None, "parse_failure":True, "substantive_ambiguity":True, "parse_error":str(error)})
        else:
            result.update({"status":"failed", "failure_reason":"FREE_QUOTA_EXHAUSTED" if status == 429 else "PROVIDER_HTTP_ERROR"})
        write_once(attempt, result)
        print(json.dumps({"run_id":run_id,"status":result["status"],"http_status":status}, sort_keys=True))

if __name__ == "__main__": main()
