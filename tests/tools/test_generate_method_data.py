"""Tests for tools/generate_method_data.py (NAV_STORY_PLATFORM_METHOD.md item 6:
Method section data source -- operating model, R1-R6 rules, live staging-loop
view, retrospective library)."""
import json

from tools.generate_method_data import (
    generate, OUT_PATH, DASHBOARD_PATH, STAGING_DIR, STAGING_DONE_DIR,
    STAGING_DRAFTS_DIR, RETRO_DIR,
    _staging_pending, _staging_done_recent, _staging_drafts_count, _retro_library,
    OPERATING_MODEL, RULES, METHOD_FRAMING,
)


def test_operating_model_has_roles_and_tiers():
    assert len(OPERATING_MODEL["roles"]) >= 3
    assert len(OPERATING_MODEL["tiers"]) == 3
    for r in OPERATING_MODEL["roles"]:
        assert r["name"] and r["description"]
    for t in OPERATING_MODEL["tiers"]:
        assert t["tier"] and t["name"] and t["description"]


def test_six_rules_each_with_a_real_incident():
    assert len(RULES) == 6
    ids = [r["id"] for r in RULES]
    assert ids == ["R1", "R2", "R3", "R4", "R5", "R6"]
    for r in RULES:
        assert r["name"] and r["description"] and r["incident"]
        assert len(r["incident"]) > 40, "incident should be a real summary, not a stub"


def test_method_framing_is_nonempty_prose():
    assert len(METHOD_FRAMING) > 80


def test_staging_pending_reads_real_root_md_files():
    pending = _staging_pending()
    assert isinstance(pending, list)
    for item in pending:
        assert item["filename"].endswith(".md")
        assert "modified_at" in item
        assert "size_bytes" in item


def test_staging_done_recent_sorted_newest_first_and_totalled(tmp_path, monkeypatch):
    done_dir = tmp_path / "done"
    done_dir.mkdir()
    import time
    for i, name in enumerate(["a.md", "b.md", "c.md"]):
        (done_dir / name).write_text("x")
        # ensure distinct mtimes
        import os
        os.utime(done_dir / name, (i, i))
    monkeypatch.setattr("tools.generate_method_data.STAGING_DONE_DIR", done_dir)
    recent, total = _staging_done_recent(limit=2)
    assert total == 3
    assert len(recent) == 2
    assert recent[0]["filename"] == "c.md"  # newest mtime first
    assert recent[1]["filename"] == "b.md"


def test_staging_done_recent_empty_when_dir_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.generate_method_data.STAGING_DONE_DIR", tmp_path / "nope")
    recent, total = _staging_done_recent()
    assert recent == []
    assert total == 0


def test_staging_drafts_count_real(tmp_path, monkeypatch):
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()
    (drafts_dir / "x.md").write_text("x")
    (drafts_dir / "y.md").write_text("y")
    monkeypatch.setattr("tools.generate_method_data.STAGING_DRAFTS_DIR", drafts_dir)
    assert _staging_drafts_count() == 2


def test_retro_library_reads_real_retrospectives_dir():
    lib = _retro_library()
    assert len(lib) >= 1
    for entry in lib:
        assert entry["filename"].endswith(".md")
        assert entry["title"]
        assert entry["path"].startswith("https://")
        assert entry["size_bytes"] > 0


def test_retro_library_parses_date_from_filename_prefix(tmp_path, monkeypatch):
    retro_dir = tmp_path / "retro"
    retro_dir.mkdir()
    (retro_dir / "2026-07-04-verification-week.md").write_text("# Retrospective: Verification Week\n")
    monkeypatch.setattr("tools.generate_method_data.RETRO_DIR", retro_dir)
    lib = _retro_library()
    assert len(lib) == 1
    assert lib[0]["date"] == "2026-07-04"
    assert lib[0]["title"] == "Retrospective: Verification Week"


def test_generate_writes_json_with_all_sections(monkeypatch, tmp_path):
    fake_dashboard = tmp_path / "dashboard.json"
    fake_dashboard.write_text(json.dumps({
        "meta": {"generated_at": "2026-07-06T00:00:00Z", "git_commit": "abc1234"},
        "build": {"current_phase": "RQ", "test_count": 15850},
    }))
    fake_out = tmp_path / "method.json"
    monkeypatch.setattr("tools.generate_method_data.DASHBOARD_PATH", fake_dashboard)
    monkeypatch.setattr("tools.generate_method_data.OUT_PATH", fake_out)

    assert generate() is True
    data = json.loads(fake_out.read_text())
    assert data["phase"] == "RQ"
    assert len(data["rules"]) == 6
    assert "operating_model" in data
    assert "staging_loop" in data
    assert "retro_library" in data
    assert data["method_framing"]


def test_generate_handles_missing_dashboard_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr("tools.generate_method_data.DASHBOARD_PATH", tmp_path / "nope.json")
    monkeypatch.setattr("tools.generate_method_data.OUT_PATH", tmp_path / "out.json")
    assert generate() is True
    data = json.loads((tmp_path / "out.json").read_text())
    assert data["phase"] is None
