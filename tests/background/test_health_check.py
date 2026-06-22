"""Tests for background/health_check.py."""

import sys
from pathlib import Path

import pytest

from background import health_check


def _mock_panes(names: list[str]):
    return {n: "python3" for n in names}


def test_all_processes_running_reports_ok(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok
    assert len(problem_lines) == 0
    assert len(ok_lines) == len(health_check.EXPECTED_PANES) + 1  # +1 for staging


def test_missing_process_reported_as_problem(monkeypatch):
    present = {k: "python3" for k in health_check.EXPECTED_PANES if k != "dispatcher"}
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: present)
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert not all_ok
    assert any("dispatcher" in line for line in problem_lines)


def test_process_running_without_tmux_pane_still_passes(monkeypatch):
    present = {k: "python3" for k in health_check.EXPECTED_PANES if k != "dispatcher"}
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: present)
    monkeypatch.setattr(health_check, "_running_scripts", lambda: ["python3 background/dispatcher.py"])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok


def test_stale_staging_message_reported_as_problem(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: "Unactioned messages: from_rich_001.md (3.5h old)")

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert not all_ok
    assert any("from_rich_001.md" in line for line in problem_lines)


def test_main_returns_0_when_all_ok(monkeypatch, tmp_path):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    monkeypatch.setattr(health_check, "LOG_FILE", tmp_path / "health.md")
    monkeypatch.setattr(health_check, "send_ntfy", lambda *a, **k: None)
    monkeypatch.setattr(sys, "argv", ["health_check.py"])

    rc = health_check.main()
    assert rc == 0


def test_main_returns_1_and_sends_ntfy_on_failure(monkeypatch, tmp_path):
    present = {k: "python3" for k in health_check.EXPECTED_PANES if k != "dispatcher"}
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: present)
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    monkeypatch.setattr(health_check, "LOG_FILE", tmp_path / "health.md")
    monkeypatch.setattr(sys, "argv", ["health_check.py"])

    sent = []
    monkeypatch.setattr(health_check, "send_ntfy", lambda msg, **k: sent.append(msg))

    rc = health_check.main()
    assert rc == 1
    assert len(sent) == 1
    assert "DEGRADED" in sent[0]
