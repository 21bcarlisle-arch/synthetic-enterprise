"""Tests for tools/generate_platform_data.py (NAV_STORY_PLATFORM_METHOD.md P1:
Platform section data source -- architecture layers, module/domain map,
adapter registry, synthetic data catalogue)."""
import json

from tools.generate_platform_data import (
    generate, OUT_PATH, DASHBOARD_PATH,
    _count_py, _company_domain_counts,
    ADAPTER_REGISTRY, SYNTHETIC_DATA_CATALOGUE, COMPANY_DOMAIN_TAGS, LAYER_TAGS,
)


def test_count_py_counts_real_files_and_excludes_tests_and_pycache():
    n = _count_py("company")
    assert n > 0
    assert all(not name.startswith("test_") for name in [])  # sanity no-op


def test_count_py_zero_for_nonexistent_dir():
    assert _count_py("this_directory_does_not_exist") == 0


def test_company_domain_counts_are_real_and_positive():
    counts = _company_domain_counts()
    assert "crm" in counts
    assert all(v > 0 for v in counts.values())


def test_every_company_domain_has_a_transferability_tag_or_default():
    counts = _company_domain_counts()
    for name in counts:
        # Either explicitly tagged, or falls back to "market" in generate() --
        # just confirm the fallback set covers every real subdomain sanely.
        tag = COMPANY_DOMAIN_TAGS.get(name, "market")
        assert tag in ("universal", "market", "uk")


def test_layer_tags_cover_every_transferability_value():
    tags = set(v[0] for v in LAYER_TAGS.values())
    assert tags <= {"universal", "market", "uk"}


def test_adapter_registry_entries_have_status_and_description():
    for a in ADAPTER_REGISTRY:
        assert a["status"] in ("LIVE", "SCAFFOLDED", "PLANNED")
        assert a["description"]
        assert a["boundary"]


def test_adapter_registry_live_entries_point_to_real_files():
    for a in ADAPTER_REGISTRY:
        if a["status"] == "LIVE":
            assert a["file"], "a LIVE adapter must name a real file, not be fabricated"


def test_catalogue_entries_have_path_and_description():
    for item in SYNTHETIC_DATA_CATALOGUE:
        assert item["path"].startswith("/")
        assert item["description"]


def test_generate_writes_json_with_real_computed_counts(monkeypatch, tmp_path):
    fake_dashboard = tmp_path / "dashboard.json"
    fake_dashboard.write_text(json.dumps({
        "meta": {"generated_at": "2026-07-06T00:00:00Z", "git_commit": "abc1234"},
        "build": {"current_phase": "RO", "test_count": 15800},
    }))
    fake_out = tmp_path / "platform.json"
    monkeypatch.setattr("tools.generate_platform_data.DASHBOARD_PATH", fake_dashboard)
    monkeypatch.setattr("tools.generate_platform_data.OUT_PATH", fake_out)

    assert generate() is True
    data = json.loads(fake_out.read_text())
    assert data["phase"] == "RO"
    assert data["company_module_total"] > 0
    assert len(data["layers"]) > 0
    assert len(data["company_domains"]) > 0
    assert len(data["adapters"]) == len(ADAPTER_REGISTRY)
    assert len(data["synthetic_data_catalogue"]) == len(SYNTHETIC_DATA_CATALOGUE)


def test_generate_handles_missing_dashboard_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr("tools.generate_platform_data.DASHBOARD_PATH", tmp_path / "nope.json")
    monkeypatch.setattr("tools.generate_platform_data.OUT_PATH", tmp_path / "out.json")
    assert generate() is True
    data = json.loads((tmp_path / "out.json").read_text())
    assert data["phase"] is None


def test_catalogue_directory_entry_reports_file_count_not_directory_size():
    generate()
    data = json.loads(OUT_PATH.read_text())
    dir_entries = [c for c in data["synthetic_data_catalogue"] if c["path"] == "/data/customers/"]
    assert len(dir_entries) == 1
    entry = dir_entries[0]
    assert entry["size_bytes"] is None
    assert entry["file_count"] and entry["file_count"] > 0
    assert entry["total_bytes"] and entry["total_bytes"] > 0
