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

    # Simulate a successful subprocess run + output file creation
    def fake_run(cmd, **kwargs):
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
