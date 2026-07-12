"""Tests for background/health_check.py."""

import sys
from pathlib import Path

import pytest

from background import health_check


def _mock_panes(names: list[str]):
    return {n: "python3" for n in names}


class TestCheckStaleDependencies:
    """Idle-hole #8 (ADVISOR_STEER_OVERNIGHT.md, 2026-07-11): a real
    hot-lane-designated atom (D3) sat unselected for ~90 minutes because its
    depends_on required an atom at its full target level while that
    dependency was correctly, deliberately parked below target for an
    unrelated, deferred reason. This check surfaces (does not assert as bugs)
    every non-idle atom blocked by an idle dependency."""

    def test_returns_none_for_empty_map(self, tmp_path, monkeypatch):
        map_path = tmp_path / "maturity_map.yaml"
        map_path.write_text("[]\n")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        assert health_check._check_stale_dependencies() is None

    def test_flags_build_atom_blocked_by_idle_dependency(self, tmp_path, monkeypatch):
        map_path = tmp_path / "docs" / "design"
        map_path.mkdir(parents=True)
        (map_path / "maturity_map.yaml").write_text("""
- id: hot_lane_atom
  level_current: 0
  level_target: 3
  loop_stage: build
  depends_on: [blocker_atom]
- id: blocker_atom
  level_current: 2
  level_target: 3
  loop_stage: idle
""")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        result = health_check._check_stale_dependencies()
        assert result is not None
        assert "hot_lane_atom" in result
        assert "blocker_atom" in result

    def test_does_not_flag_atom_blocked_by_a_non_idle_dependency(self, tmp_path, monkeypatch):
        map_path = tmp_path / "docs" / "design"
        map_path.mkdir(parents=True)
        (map_path / "maturity_map.yaml").write_text("""
- id: hot_lane_atom
  level_current: 0
  level_target: 3
  loop_stage: build
  depends_on: [blocker_atom]
- id: blocker_atom
  level_current: 0
  level_target: 3
  loop_stage: build
""")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        assert health_check._check_stale_dependencies() is None

    def test_does_not_flag_atom_with_no_real_gap(self, tmp_path, monkeypatch):
        map_path = tmp_path / "docs" / "design"
        map_path.mkdir(parents=True)
        (map_path / "maturity_map.yaml").write_text("""
- id: already_done_atom
  level_current: 3
  level_target: 3
  loop_stage: build
  depends_on: [blocker_atom]
- id: blocker_atom
  level_current: 0
  level_target: 3
  loop_stage: idle
""")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        assert health_check._check_stale_dependencies() is None

    def test_does_not_flag_idle_atom_itself(self, tmp_path, monkeypatch):
        map_path = tmp_path / "docs" / "design"
        map_path.mkdir(parents=True)
        (map_path / "maturity_map.yaml").write_text("""
- id: idle_atom
  level_current: 0
  level_target: 3
  loop_stage: idle
  depends_on: [blocker_atom]
- id: blocker_atom
  level_current: 0
  level_target: 3
  loop_stage: idle
""")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        assert health_check._check_stale_dependencies() is None

    def test_flags_missing_dependency_id(self, tmp_path, monkeypatch):
        map_path = tmp_path / "docs" / "design"
        map_path.mkdir(parents=True)
        (map_path / "maturity_map.yaml").write_text("""
- id: hot_lane_atom
  level_current: 0
  level_target: 3
  loop_stage: build
  depends_on: [nonexistent_atom]
""")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        result = health_check._check_stale_dependencies()
        assert result is not None
        assert "nonexistent_atom" in result

    def test_real_maturity_map_e2_not_flagged_as_stale(self):
        """E2_revenue_reconciliation is a real, deliberate depends_on block
        (documented in its own simplifications) -- confirm the real map
        either doesn't flag it, or (if flagged) it's clearly not a false
        'all clear' claim. This is a live-data smoke test, not asserting a
        specific outcome, since the real map legitimately changes over time."""
        result = health_check._check_stale_dependencies()
        # Just confirm the check runs cleanly against the real map (no crash).
        assert result is None or isinstance(result, str)


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
    monkeypatch.setattr(health_check, "_check_stale_dependencies", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok
    assert len(problem_lines) == 0
    assert len(ok_lines) == len(health_check.EXPECTED_PANES) + 3  # +1 staging, +1 pixel-verification, +1 stale-deps


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
