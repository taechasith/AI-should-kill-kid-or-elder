"""Deterministic, non-secret K5/K6 provider request serialization."""
from __future__ import annotations
import base64, hashlib, json
from pathlib import Path

SERIALIZER_VERSION = "ka-iro-krisis-request-serialization-v1"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def _context_text(row: dict, root: Path) -> str:
    path = row.get("deterministic_text_asset_path")
    if path is None:
        # K5 image rows supplement their existing frozen PNG with the already
        # frozen same-scene text-equivalent asset; it was the only context
        # produced by the K5 generator and is therefore uniquely determined.
        asset = Path(row["input_asset_path"])
        path = str(asset.with_suffix(".txt")) if asset.suffix == ".png" else str(asset)
    return (root / path).read_text(encoding="utf-8")

def scientific_text(row: dict, root: Path) -> str:
    return row["prompt_template"] + "\n\nSTRUCTURED_PHYSICAL_CONTEXT\n" + _context_text(row, root)

def request_object(row: dict, root: Path) -> tuple[str, dict, dict]:
    text = scientific_text(row, root)
    image_path = row.get("image_asset_path") or (row["input_asset_path"] if row["representation_condition"].startswith("MULTIMODAL") else None)
    is_image = row["representation_condition"].startswith("MULTIMODAL")
    strict = row["interface_condition"] == "STRICT_STRUCTURED_OUTPUT"
    common = {"temperature": 0, "top_p": 1, "max_output_tokens": 256, "stream": False}
    if row["provider"] == "Google Gemini API":
        parts: list[dict] = [{"text": text}]
        if is_image:
            raw = (root / image_path).read_bytes()
            parts.insert(0, {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(raw).decode("ascii")}})
        config = {"temperature": 0, "topP": 1, "maxOutputTokens": 256, "candidateCount": 1, "responseMimeType": "application/json" if strict else "text/plain"}
        body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": config}
        endpoint = f"{GEMINI_BASE}/{row['model_id']}:generateContent"
        headers = {"content-type": "application/json"}
    else:
        if is_image:
            raw = (root / image_path).read_bytes()
            content: object = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(raw).decode("ascii")}}]
        else: content = text
        body = {"model": row["model_id"], "messages": [{"role": "user", "content": content}], "temperature": 0, "top_p": 1, "max_completion_tokens": 256, "stream": False, "stop": None, "reasoning_effort": "none"}
        if strict: body["response_format"] = {"type": "json_object"}
        endpoint = GROQ_ENDPOINT; headers = {"content-type": "application/json"}
    return endpoint, headers, body

def serialized(row: dict, root: Path) -> dict:
    endpoint, headers, body = request_object(row, root); raw = canonical_json(body)
    envelope = canonical_json({"method": "POST", "url": endpoint, "headers": headers, "body_sha256": sha256(raw)})
    return {"serializer_version": SERIALIZER_VERSION, "endpoint": endpoint, "nonsecret_headers": headers, "request_body_sha256": sha256(raw), "request_body_bytes": len(raw), "request_envelope_sha256": sha256(envelope), "request_body": raw}
