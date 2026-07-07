"""Tests for tools/generate_saas_coverage_data.py (SAAS_COVERAGE_MAP.md:
SaaS Estate Coverage Map -- the A/B/C taxonomy of eliminated/recreated/
interfaced SaaS categories a real UK energy supplier assembles)."""
import json

from tools.generate_saas_coverage_data import (
    generate, OUT_PATH, DASHBOARD_PATH, CATEGORIES, PROJECT, _module_exists,
)


def test_every_category_has_a_valid_bucket():
    for c in CATEGORIES:
        assert c["bucket"] in ("A", "B", "C")


def test_every_category_has_leaders_and_a_name():
    for c in CATEGORIES:
        assert c["category"]
        assert c["market_leaders"]


def test_bucket_a_categories_either_claim_nothing_or_a_real_module():
    for c in CATEGORIES:
        if c["bucket"] == "A":
            for m in c["modules"]:
                assert _module_exists(m), (
                    "bucket A category cites a module that doesn't exist: " + c["category"]
                )


def test_bucket_b_categories_point_to_at_least_one_real_existing_module():
    for c in CATEGORIES:
        if c["bucket"] == "B":
            assert c["modules"], "bucket B category must name at least one module: " + c["category"]
            assert any(_module_exists(m) for m in c["modules"]), (
                "bucket B category names no real existing module: " + c["category"]
            )


def test_module_exists_true_for_real_file_false_for_fabricated():
    assert _module_exists("company/billing") is True
    assert _module_exists("this/path/does/not/exist.py") is False


def test_generate_writes_json_with_computed_bucket_breakdown(monkeypatch, tmp_path):
    fake_dashboard = tmp_path / "dashboard.json"
    payload = json.dumps({"meta": {"generated_at": "2026-07-07T00:00:00Z", "git_commit": "abc1234"}, "build": {"current_phase": "RW", "test_count": 15960}})
    fake_dashboard.write_text(payload)
    fake_out = tmp_path / "saas_coverage.json"
    monkeypatch.setattr("tools.generate_saas_coverage_data.DASHBOARD_PATH", fake_dashboard)
    monkeypatch.setattr("tools.generate_saas_coverage_data.OUT_PATH", fake_out)

    assert generate() is True
    data = json.loads(fake_out.read_text())
    assert data["phase"] == "RW"
    assert data["total_categories"] == len(CATEGORIES)
    assert sum(data["bucket_counts"].values()) == data["total_categories"]
    assert abs(sum(data["bucket_pct"].values()) - 100.0) < 1.0
    assert len(data["categories"]) == len(CATEGORIES)


def test_generate_handles_missing_dashboard_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr("tools.generate_saas_coverage_data.DASHBOARD_PATH", tmp_path / "nope.json")
    monkeypatch.setattr("tools.generate_saas_coverage_data.OUT_PATH", tmp_path / "out.json")
    assert generate() is True
    data = json.loads((tmp_path / "out.json").read_text())
    assert data["phase"] is None


def test_categories_modules_exist_field_matches_filesystem():
    generate()
    data = json.loads(OUT_PATH.read_text())
    for c in data["categories"]:
        for m in c["modules_exist"]:
            assert m["exists"] == (PROJECT / m["path"]).exists()
