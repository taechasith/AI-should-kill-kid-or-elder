from scripts.probe_phase6_literature_v2_access import _load_targets


def test_literature_v2_probe_targets_frozen_candidate_panel_only():
    assert _load_targets() == {
        "gemini": {"gemini-3.5-flash", "gemini-3.5-flash-lite"},
        "groq": {"qwen/qwen3.8-27b"},
    }
