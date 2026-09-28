"""Offline request serializers for the proposed Phase 6 provider panel.

The serializers intentionally do not hold credentials or send HTTP requests.
They make the modality and closed-book policy testable before any authorized
provider pilot.  A future executor must use these payloads only after the
Phase 6 budget/access gate is explicitly resolved.
"""

from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .phase6_interface import PHASE6_SCHEMA_VERSION


PROHIBITED_TOOL_KEYS = {"tools", "tool_choice", "web_search", "web", "browser", "search", "retrieval"}


@dataclass(frozen=True)
class PreparedModelRequest:
    provider: str
    model_id: str
    endpoint: str
    body: dict[str, Any]

    @property
    def request_hash(self) -> str:
        canonical = json.dumps(self.body, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()


def image_data_uri(image_path: Path) -> str:
    payload = image_path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Phase 6 only accepts a PNG scene image: {image_path}")
    return "data:image/png;base64," + b64encode(payload).decode("ascii")


def _assert_closed_book(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key.lower() in PROHIBITED_TOOL_KEYS:
                raise ValueError(f"closed-book request contains prohibited key: {key}")
            _assert_closed_book(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_closed_book(nested)


def _schema_instruction() -> str:
    return (
        "Return JSON only following the Phase 6 contract "
        f"{PHASE6_SCHEMA_VERSION}. Do not invoke tools, browse, search, retrieve, "
        "or use information beyond the supplied image and text."
    )


def build_openai_responses_request(
    *, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    body = {
        "model": model_id,
        "instructions": system_message + "\n\n" + _schema_instruction(),
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": image_data_uri(image_path), "detail": "high"},
                    {"type": "input_text", "text": user_message},
                ],
            }
        ],
        "max_output_tokens": max_output_tokens,
    }
    _assert_closed_book(body)
    return PreparedModelRequest("openai", model_id, "https://api.openai.com/v1/responses", body)


def build_anthropic_messages_request(
    *, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    data_uri = image_data_uri(image_path)
    _, encoded = data_uri.split(",", 1)
    body = {
        "model": model_id,
        "max_tokens": max_output_tokens,
        "system": system_message + "\n\n" + _schema_instruction(),
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded}},
                    {"type": "text", "text": user_message},
                ],
            }
        ],
    }
    _assert_closed_book(body)
    return PreparedModelRequest("anthropic", model_id, "https://api.anthropic.com/v1/messages", body)


def build_mistral_chat_request(
    *, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    body = {
        "model": model_id,
        "max_tokens": max_output_tokens,
        "messages": [
            {"role": "system", "content": system_message + "\n\n" + _schema_instruction()},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": image_data_uri(image_path)},
                ],
            },
        ],
    }
    _assert_closed_book(body)
    return PreparedModelRequest("mistral", model_id, "https://api.mistral.ai/v1/chat/completions", body)


def build_provider_request(
    *, provider: str, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    factories = {
        "openai": build_openai_responses_request,
        "anthropic": build_anthropic_messages_request,
        "mistral": build_mistral_chat_request,
    }
    try:
        factory = factories[provider]
    except KeyError as error:
        raise ValueError(f"No Phase 6 adapter is registered for {provider}") from error
    return factory(
        model_id=model_id,
        image_path=image_path,
        system_message=system_message,
        user_message=user_message,
        max_output_tokens=max_output_tokens,
    )
