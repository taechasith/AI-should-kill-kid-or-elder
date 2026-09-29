import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from scripts.probe_phase6_free_access import USER_AGENT, probe


class _Response:
    status = 200
    headers = {"x-ratelimit-limit-requests": "1000", "authorization": "secret-is-not-retained"}

    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_metadata_probe_records_only_allowlisted_nonsecret_metadata(tmp_path):
    def opener(request, timeout):
        assert request.get_method() == "GET"
        assert request.get_header("User-agent") == USER_AGENT
        assert request.get_header("Accept") == "application/json"
        if "generativelanguage" in request.full_url:
            return _Response({"models": [{"name": "models/gemini-3.6-flash"}, {"name": "models/gemini-2.5-flash-lite"}]})
        return _Response({"data": [{"id": "qwen/qwen3.8-27b"}]})

    result = probe(environ={"GEMINI_API_KEY": "gemini-secret", "GROQ_API_KEY": "groq-secret"}, opener=opener, output_dir=tmp_path)
    assert result["all_target_models_listed"] is True
    assert result["model_generation_requests_made"] == 0
    assert result["metadata_http_requests_made"] == result["provider_calls_made"] == 2
    assert result["execution_status"] == "PREFLIGHT_BLOCKED_PENDING_ACCOUNT_TIER_ATTESTATION"
    assert result["free_tier_verified"] is False
    persisted = (tmp_path / Path(result["output_path"]).name).read_text(encoding="utf-8")
    assert "gemini-secret" not in persisted and "groq-secret" not in persisted
    assert "authorization" not in persisted.lower()
    assert "x-ratelimit-limit-requests" in persisted


def test_missing_credentials_make_no_http_requests(tmp_path):
    def opener(*args, **kwargs):
        pytest.fail("Missing credentials must not cause an HTTP request")

    result = probe(environ={}, opener=opener, output_dir=tmp_path)
    assert result["metadata_http_requests_made"] == 0
    assert result["execution_status"] == "PREFLIGHT_BLOCKED_MISSING_CREDENTIAL"


@pytest.mark.parametrize("status, expected", [(403, "HTTP_ERROR"), (429, "FREE_QUOTA_EXHAUSTED")])
def test_http_failures_preserve_status_without_retry_or_secret(tmp_path, status, expected):
    calls = []

    def opener(request, timeout):
        calls.append(request.get_method())
        raise HTTPError(request.full_url, status, "not-retained-secret", {"retry-after": "60", "authorization": "not-retained-secret"}, None)

    result = probe(environ={"GEMINI_API_KEY": "not-retained-secret", "GROQ_API_KEY": "not-retained-secret"}, opener=opener, output_dir=tmp_path)
    assert calls == ["GET", "GET"]
    assert result["execution_status"] == "PREFLIGHT_BLOCKED_PROVIDER_ACCESS"
    assert result["providers"][1]["probe_status"] == expected
    assert result["providers"][1]["rate_limit_metadata"] == {"retry-after": "60"}
    assert result["provider_calls_made"] == 2
    assert "not-retained-secret" not in Path(result["output_path"]).read_text()


@pytest.mark.parametrize("payload", [[], {}, {"data": None}, {"data": [None]}, {"data": [{"id": 1}]}])
def test_malformed_metadata_does_not_establish_access(tmp_path, payload):
    result = probe(environ={"GROQ_API_KEY": "test-secret"}, opener=lambda *args, **kwargs: _Response(payload), output_dir=tmp_path)
    assert result["providers"][1]["probe_status"] == "INVALID_METADATA_RESPONSE"
    assert result["all_target_models_listed"] is False


def test_repeated_probes_preserve_previous_evidence(tmp_path):
    first = probe(environ={}, output_dir=tmp_path)
    first_bytes = Path(first["output_path"]).read_bytes()
    second = probe(environ={}, output_dir=tmp_path)
    assert first["output_path"] != second["output_path"]
    assert Path(first["output_path"]).read_bytes() == first_bytes
