from scripts.finalize_phase6_literature_v2 import FILES, build_manifest


def test_literature_v2_manifest_covers_required_pre_pilot_artifacts():
    manifest = build_manifest()
    assert manifest["failed_v1_panel_preserved"] is True
    assert set(manifest["files"]) == set(FILES)
    assert len(manifest["files"]) >= 12
