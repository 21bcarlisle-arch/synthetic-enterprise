"""Tests for background/health_check.py."""

import sys
from pathlib import Path

import pytest

from background import health_check


def _mock_panes(names: list[str]):
    return {n: "python3" for n in names}


class TestCheckPixelVerificationCapability:
    """ADVISOR_STEER_BROWSER_REGRESSION.md (2026-07-11): pixel-verification
    capability is a standing harness invariant -- if it breaks, it must be an
    alarmed health-check failure, not a silently-reasoned-around caveat."""

    def test_returns_none_when_playwright_available(self):
        # Real invocation -- this environment genuinely has Playwright
        # available (proven 2026-07-11 via a live pixel check on poesys.net),
        # so this is a real, not mocked, positive-path assertion.
        assert health_check._check_pixel_verification_capability() is None

    def test_returns_warning_on_nonzero_exit(self, monkeypatch):
        class _FakeResult:
            returncode = 1
            stderr = "some npx error"

        monkeypatch.setattr(
            health_check.subprocess, "run", lambda *a, **k: _FakeResult()
        )
        result = health_check._check_pixel_verification_capability()
        assert result is not None
        assert "unavailable" in result.lower()

    def test_returns_warning_on_file_not_found(self, monkeypatch):
        def _raise(*a, **k):
            raise FileNotFoundError("npx not found")

        monkeypatch.setattr(health_check.subprocess, "run", _raise)
        result = health_check._check_pixel_verification_capability()
        assert result is not None
        assert "npx not found" in result

    def test_returns_warning_on_timeout(self, monkeypatch):
        import subprocess as _subprocess

        def _raise(*a, **k):
            raise _subprocess.TimeoutExpired(cmd="npx", timeout=15)

        monkeypatch.setattr(health_check.subprocess, "run", _raise)
        result = health_check._check_pixel_verification_capability()
        assert result is not None
        assert "timed out" in result.lower()


def test_all_processes_running_reports_ok(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    monkeypatch.setattr(health_check, "_check_pixel_verification_capability", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok
    assert len(problem_lines) == 0
    assert len(ok_lines) == len(health_check.EXPECTED_PANES) + 2  # +1 staging, +1 pixel-verification


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


def test_all_expected_panes_are_checked():
    assert "dispatcher" in health_check.EXPECTED_PANES
    assert "sim-runner" in health_check.EXPECTED_PANES


def test_ok_lines_include_staging_check_when_clean(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, ok_lines, _ = health_check.run_health_check()
    assert any("staging" in line.lower() or "Staging" in line for line in ok_lines)


def test_multiple_missing_panes_reported(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: {})
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, _, problem_lines = health_check.run_health_check()

    assert not all_ok
    assert len(problem_lines) >= len(health_check.EXPECTED_PANES)


def test_main_writes_to_log_file(monkeypatch, tmp_path):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    log = tmp_path / "health.md"
    monkeypatch.setattr(health_check, "LOG_FILE", log)
    monkeypatch.setattr(health_check, "send_ntfy", lambda *a, **k: None)
    monkeypatch.setattr(__import__("sys"), "argv", ["health_check.py"])

    health_check.main()

    assert log.exists()


def test_expected_panes_count_is_nonzero():
    assert len(health_check.EXPECTED_PANES) > 0


def test_run_health_check_returns_three_values(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    result = health_check.run_health_check()
    assert len(result) == 3


def test_ok_lines_are_all_strings(monkeypatch):
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    all_ok, ok_lines, problem_lines = health_check.run_health_check()
    assert all(isinstance(line, str) for line in ok_lines)
    assert all(isinstance(line, str) for line in problem_lines)
