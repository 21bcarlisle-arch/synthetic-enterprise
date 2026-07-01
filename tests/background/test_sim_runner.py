"""Tests for background/sim_runner.py."""

from pathlib import Path
from unittest.mock import MagicMock

from background import sim_runner


def test_run_simulation_creates_staging_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "send_ntfy", lambda *a, **k: None)
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
    monkeypatch.setattr(sim_runner, "send_ntfy", lambda *a, **k: None)
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
    monkeypatch.setattr(sim_runner, "send_ntfy", lambda *a, **k: None)
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
    monkeypatch.setattr(sim_runner, "send_ntfy", lambda *a, **k: None)
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
