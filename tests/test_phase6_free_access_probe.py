import json

from scripts.probe_phase6_free_access import probe


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


def test_metadata_probe_records_only_allowlisted_nonsecret_metadata(tmp_path, monkeypatch):
    def opener(request, timeout):
        if "generativelanguage" in request.full_url:
            return _Response({"models": [{"name": "models/gemini-3.6-flash"}, {"name": "models/gemini-2.5-flash-lite"}]})
        return _Response({"data": [{"id": "qwen/qwen3.8-27b"}]})

    monkeypatch.setattr("scripts.probe_phase6_free_access.OUTPUT_PATH", tmp_path / "probe.json")
    result = probe(environ={"GEMINI_API_KEY": "gemini-secret", "GROQ_API_KEY": "groq-secret"}, opener=opener)
    assert result["all_target_models_listed"] is True
    assert result["model_generation_requests_made"] == 0
    assert result["free_tier_verified"] is False
    persisted = (tmp_path / "probe.json").read_text(encoding="utf-8")
    assert "gemini-secret" not in persisted and "groq-secret" not in persisted
    assert "authorization" not in persisted.lower()
    assert "x-ratelimit-limit-requests" in persisted
