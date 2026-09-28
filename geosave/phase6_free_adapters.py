"""Offline serializers for the separately versioned zero-cost Phase 6 panel.

They intentionally have no HTTP client and cannot read credentials.  A future
executor must pass the independent ``FreeOnlyExecutionGuard`` before using a
prepared payload.
"""

from __future__ import annotations

from pathlib import Path

from .model_adapters import PreparedModelRequest, _assert_closed_book, _schema_instruction, image_data_uri


def build_gemini_generate_content_request(
    *, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    data_uri = image_data_uri(image_path)
    _, encoded = data_uri.split(",", 1)
    body = {
        "systemInstruction": {"parts": [{"text": system_message + "\n\n" + _schema_instruction()}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inlineData": {"mimeType": "image/png", "data": encoded}},
                    {"text": user_message},
                ],
            }
        ],
        "generationConfig": {"maxOutputTokens": max_output_tokens, "responseMimeType": "application/json"},
    }
    _assert_closed_book(body)
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
    return PreparedModelRequest("gemini", model_id, endpoint, body)


def build_groq_chat_request(
    *, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    body = {
        "model": model_id,
        "max_tokens": max_output_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_message + "\n\n" + _schema_instruction()},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": image_data_uri(image_path)}},
                ],
            },
        ],
    }
    _assert_closed_book(body)
    return PreparedModelRequest("groq", model_id, "https://api.groq.com/openai/v1/chat/completions", body)


def build_free_provider_request(
    *, provider: str, model_id: str, image_path: Path, system_message: str, user_message: str, max_output_tokens: int
) -> PreparedModelRequest:
    factories = {"gemini": build_gemini_generate_content_request, "groq": build_groq_chat_request}
    try:
        factory = factories[provider]
    except KeyError as error:
        raise ValueError(f"No Phase 6 free-panel adapter is registered for {provider}") from error
    return factory(
        model_id=model_id,
        image_path=image_path,
        system_message=system_message,
        user_message=user_message,
        max_output_tokens=max_output_tokens,
    )
