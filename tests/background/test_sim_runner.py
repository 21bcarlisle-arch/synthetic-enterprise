"""Tests for background/sim_runner.py."""

from pathlib import Path
from unittest.mock import MagicMock

from background import sim_runner


def test_run_simulation_creates_staging_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    # Simulate a successful subprocess run + output file creation.
    # Only write output files for the simulation cmd; other calls just get rc=0.
    def fake_run(cmd, **kwargs):
        if "annual_report" in " ".join(str(a) for a in cmd):
            out_json = next((Path(a) for a in cmd if a.endswith(".json")), None)
            if out_json:
                out_json.parent.mkdir(parents=True, exist_ok=True)
                out_json.write_text('{"test": true}')
            out_md = next((Path(a) for a in cmd if a.endswith(".md")), None)
            if out_md:
                out_md.write_text("# Report")
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    result = sim_runner.run_simulation()

    assert result is True
    markers = list((tmp_path / "staging").glob("run_complete_*.md"))
    assert len(markers) == 1
    content = markers[0].read_text()
    assert "Action required" in content
    assert "ANNUAL_REPORT.md" in content


def test_run_simulation_returns_false_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 1
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    result = sim_runner.run_simulation()

    assert result is False
    assert not list((tmp_path / "staging").glob("run_complete_*.md"))


def test_run_simulation_updates_latest_json(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    def fake_run(cmd, **kwargs):
        out_json = next((Path(a) for a in cmd if a.endswith(".json")), None)
        if out_json:
            out_json.parent.mkdir(parents=True, exist_ok=True)
            out_json.write_text('{"headline": "test"}')
        out_md = next((Path(a) for a in cmd if a.endswith(".md")), None)
        if out_md:
            out_md.write_text("# Report")
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    sim_runner.run_simulation()

    latest = tmp_path / "reports" / "run_output_latest.json"
    assert latest.exists()
    assert '"headline": "test"' in latest.read_text()


def test_between_run_pause_is_60():
    assert sim_runner.BETWEEN_RUN_PAUSE_SECONDS == 60


def test_git_head_returns_string(monkeypatch):
    monkeypatch.setattr(sim_runner.subprocess, "check_output", lambda *a, **k: "abc1234\n")
    result = sim_runner._git_head()
    assert isinstance(result, str)
    assert result == "abc1234"


def test_git_head_returns_unknown_on_exception(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("git not found")
    monkeypatch.setattr(sim_runner.subprocess, "check_output", boom)
    result = sim_runner._git_head()
    assert result == "unknown"


def test_log_creates_parent_directory(tmp_path, monkeypatch):
    log_file = tmp_path / "sub" / "dir" / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("test message")
    assert log_file.exists()


def test_log_writes_timestamp_and_message(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("hello world")
    text = log_file.read_text()
    assert "hello world" in text
    import re
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", text)


def test_run_simulation_staging_marker_name_format(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")
    from unittest.mock import MagicMock
    from pathlib import Path as _Path
    def fake_run(cmd, **kwargs):
        for a in cmd:
            a = str(a)
            if a.endswith(".json"):
                _Path(a).parent.mkdir(parents=True, exist_ok=True)
                _Path(a).write_text("{}")
            elif a.endswith(".md"):
                _Path(a).parent.mkdir(parents=True, exist_ok=True)
                _Path(a).write_text("# R")
        m = MagicMock(); m.returncode = 0; return m
    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)
    sim_runner.run_simulation()
    markers = list((tmp_path / "staging").glob("run_complete_*.md"))
    assert len(markers) == 1
    assert markers[0].name.startswith("run_complete_")

def test_log_appends_on_second_call(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("first")
    sim_runner.log("second")
    text = log_file.read_text()
    assert "first" in text
    assert "second" in text


def test_reports_dir_name_is_reports():
    assert sim_runner.REPORTS_DIR.name == "reports"


def test_staging_dir_name_is_staging():
    assert sim_runner.STAGING_DIR.name == "staging"


def test_log_file_is_under_project_dir():
    assert sim_runner.PROJECT_DIR in sim_runner.LOG_FILE.parents


def test_staging_dir_is_under_project_dir():
    assert sim_runner.PROJECT_DIR in sim_runner.STAGING_DIR.parents


def test_log_entry_has_timestamp(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("check timestamp")
    text = log_file.read_text()
    assert "20" in text and "UTC" in text


# --- _check_hold() -- no-orphan-transitions fix (2026-07-10,
# CLAIM_EQUALS_PIXEL.md/END_TO_END_VERIFICATION.md): a hold release must
# itself force a republish, not just stop skipping ---

def _setup_hold(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "HOLD_FLAG", tmp_path / ".sim_runner_hold")
    monkeypatch.setattr(sim_runner, "FORCE_REPUBLISH_FLAG", tmp_path / ".force_republish_once")
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")


def test_check_hold_no_flag_no_prior_hold_runs_normally(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    was_held, should_skip = sim_runner._check_hold(False)
    assert was_held is False
    assert should_skip is False
    assert not sim_runner.FORCE_REPUBLISH_FLAG.exists()


def test_check_hold_flag_present_skips_and_marks_held(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    sim_runner.HOLD_FLAG.touch()
    was_held, should_skip = sim_runner._check_hold(False)
    assert was_held is True
    assert should_skip is True


def test_check_hold_flag_still_present_stays_held_no_relog(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    sim_runner.HOLD_FLAG.touch()
    was_held, should_skip = sim_runner._check_hold(True)
    assert was_held is True
    assert should_skip is True


def test_check_hold_cleared_transition_touches_force_republish_flag(tmp_path, monkeypatch):
    """The exact regression: releasing a hold must force the next publish
    through, not just quietly stop skipping."""
    _setup_hold(tmp_path, monkeypatch)
    was_held, should_skip = sim_runner._check_hold(True)
    assert was_held is False
    assert should_skip is False
    assert sim_runner.FORCE_REPUBLISH_FLAG.exists()


def test_check_hold_no_prior_hold_does_not_touch_force_republish_flag(tmp_path, monkeypatch):
    """Only a real held->cleared transition forces a republish -- normal
    operation with no hold ever involved must not force anything."""
    _setup_hold(tmp_path, monkeypatch)
    sim_runner._check_hold(False)
    assert not sim_runner.FORCE_REPUBLISH_FLAG.exists()

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
