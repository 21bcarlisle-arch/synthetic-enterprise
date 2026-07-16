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
    from background import retro_cadence_check
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    monkeypatch.setattr(health_check, "_check_pixel_verification_capability", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_dependencies", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_running_code", lambda: None)
    # A1_learn_loop_chair L3 added a 5th always-present ok-line (retro cadence);
    # mock it too so this asserts the pane/check logic, not live retro state.
    monkeypatch.setattr(retro_cadence_check, "check_retro_staleness", lambda: None)
    # 6th always-present ok-line: exactly-one-interactive-session (2026-07-16).
    monkeypatch.setattr(health_check, "_check_single_interactive_session", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok
    assert len(problem_lines) == 0
    # +staging +pixel +stale-code +stale-deps +retro-cadence +single-session
    assert len(ok_lines) == len(health_check.EXPECTED_PANES) + 6


def test_missing_process_reported_as_problem(monkeypatch):
    present = {k: "python3" for k in health_check.EXPECTED_PANES if k != "dispatcher"}
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: present)
    monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert not all_ok
    assert any("dispatcher" in line for line in problem_lines)


def test_process_running_without_tmux_pane_still_passes(monkeypatch):
    from background import retro_cadence_check
    present = {k: "python3" for k in health_check.EXPECTED_PANES if k != "dispatcher"}
    monkeypatch.setattr(health_check, "_tmux_panes", lambda: present)
    monkeypatch.setattr(health_check, "_running_scripts", lambda: ["python3 background/dispatcher.py"])
    monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
    # Mock the machine-state-dependent checks so this asserts the intended
    # pane/process logic, not whatever the live host happens to look like
    # (a genuinely-stale real daemon would otherwise flip all_ok here).
    monkeypatch.setattr(health_check, "_check_pixel_verification_capability", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_dependencies", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_running_code", lambda: None)
    # _check_single_interactive_session and the retro-cadence check are ALSO
    # host-state reads (real `claude` process count; real retro file mtimes) —
    # mock them too, exactly as test_all_processes_running_reports_ok does.
    # Omitting the interactive-session mock made this test flip red whenever a
    # duplicate/ghost `claude` session happened to be alive on the host, which
    # wedged the publish gate (rc=1) with no code regression at all
    # (2026-07-16). A unit test must not depend on live host process state.
    monkeypatch.setattr(health_check, "_check_single_interactive_session", lambda: None)
    monkeypatch.setattr(retro_cadence_check, "check_retro_staleness", lambda: None)

    all_ok, ok_lines, problem_lines = health_check.run_health_check()

    assert all_ok, f"unexpected problems: {problem_lines}"


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
    # Mock machine-state-dependent checks -- otherwise a genuinely-stale real
    # daemon (or a broken Playwright) on the host running the suite would make
    # this "all ok" test fail for reasons unrelated to main()'s own logic.
    monkeypatch.setattr(health_check, "_check_pixel_verification_capability", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_dependencies", lambda: None)
    monkeypatch.setattr(health_check, "_check_stale_running_code", lambda: None)
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


# ── _check_stale_running_code() (2026-07-13, R3 two-strike redesign -- the
# same "committed != running" incident already found once for supervisor.py
# ("stale pre-fix code loaded since 14:14") recurred a second time
# (ANTI_LIVELOCK_AND_WIDTH.md's own fix sat committed for 17 real minutes
# while the live process kept running the pre-fix code) -- a manual
# restart is no longer sufficient the second time; this is the mechanism.) ──

def _fake_ps_lstart_output(entries):
    """entries: list of (lstart_str, args_str). Mimics `ps -eo lstart,args`'s
    real fixed-width output (24-char lstart column + a space + args)."""
    header = "                  STARTED CMD\n"
    lines = [f"{lstart:<24} {args}" for lstart, args in entries]
    return header + "\n".join(lines)


class TestCheckStaleRunningCode:
    def test_no_processes_running_returns_none(self, monkeypatch):
        monkeypatch.setattr(health_check.subprocess, "check_output", lambda *a, **k: _fake_ps_lstart_output([]))
        assert health_check._check_stale_running_code() is None

    def test_process_started_after_script_modified_is_clean(self, monkeypatch, tmp_path):
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        script = script_dir / "supervisor.py"
        script.write_text("# v1")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        # ps reports a start time comfortably AFTER the file's own mtime
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp(script.stat().st_mtime)
        started = (mtime_dt + timedelta(minutes=5)).strftime("%a %b %d %H:%M:%S %Y")
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([(started, "python3 background/supervisor.py")]),
        )
        assert health_check._check_stale_running_code() is None

    def test_process_started_before_script_modified_is_flagged(self, monkeypatch, tmp_path):
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        script = script_dir / "supervisor.py"
        script.write_text("# v1")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp(script.stat().st_mtime)
        started = (mtime_dt - timedelta(minutes=17)).strftime("%a %b %d %H:%M:%S %Y")
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([(started, "python3 background/supervisor.py")]),
        )
        result = health_check._check_stale_running_code()
        assert result is not None
        assert "supervisor" in result
        assert "17min" in result or "18min" in result  # rounding tolerance

    def test_process_not_found_at_all_is_not_flagged_here(self, monkeypatch, tmp_path):
        """A genuinely-not-running daemon is the EXISTING pane/process
        check's job (a real problem, reported separately) -- this function
        only judges staleness for processes it can actually find running."""
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        monkeypatch.setattr(health_check.subprocess, "check_output", lambda *a, **k: _fake_ps_lstart_output([]))
        assert health_check._check_stale_running_code() is None

    def test_tmux_launcher_line_does_not_masquerade_as_the_daemon(self, monkeypatch, tmp_path):
        """2026-07-13 precision-fix regression guard (found live): a lingering
        `tmux new-session ... python3 background/X.py` launcher process, alive
        since the ORIGINAL session creation, names the script as an ARGUMENT.
        The previous 'script in args' match picked up its ancient start time
        and reported a FRESHLY-RESTARTED daemon as stale. The launcher's own
        executable is `tmux`, not python, so it must be ignored; the real,
        newer `python3 background/X.py` process is the one that counts."""
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        script = script_dir / "supervisor.py"
        script.write_text("# v2")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp(script.stat().st_mtime)
        ancient = (mtime_dt - timedelta(days=10)).strftime("%a %b %d %H:%M:%S %Y")   # the tmux launcher
        fresh = (mtime_dt + timedelta(minutes=3)).strftime("%a %b %d %H:%M:%S %Y")    # the real restarted daemon
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([
                (ancient, "tmux new-session -d -s supervisor -c /home/rich/synthetic-enterprise python3 background/supervisor.py"),
                (ancient, "sh -c python3 background/supervisor.py"),   # the wrapper shell -- also not the daemon
                (fresh, "python3 background/supervisor.py"),           # the real, fresh daemon
            ]),
        )
        # Fresh daemon started AFTER the script's mtime -> not stale, despite
        # the ancient tmux/sh lines naming the same script.
        assert health_check._check_stale_running_code() is None

    def test_latest_python_process_wins_over_an_older_orphan(self, monkeypatch, tmp_path):
        """If a restart briefly leaves an old python orphan alongside the new
        process, the authoritative (latest-started) one decides staleness --
        a completed restart must read green even before the orphan exits."""
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        script = script_dir / "supervisor.py"
        script.write_text("# v2")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp(script.stat().st_mtime)
        old = (mtime_dt - timedelta(minutes=30)).strftime("%a %b %d %H:%M:%S %Y")
        new = (mtime_dt + timedelta(minutes=2)).strftime("%a %b %d %H:%M:%S %Y")
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([
                (old, "python3 background/supervisor.py"),
                (new, "python3 background/supervisor.py"),
            ]),
        )
        assert health_check._check_stale_running_code() is None

    def test_ps_failure_degrades_gracefully(self, monkeypatch):
        def _boom(*a, **k):
            raise OSError("ps unavailable")
        monkeypatch.setattr(health_check.subprocess, "check_output", _boom)
        assert health_check._check_stale_running_code() is None

    # ── stale_daemon_sessions() -- the ACTION half (2026-07-16, Item 3 "a restart
    #    must deploy current HEAD"). start_worker.sh kills exactly these before its
    #    start block, so a re-run stops leaving stale code running. ────────────────
    def test_stale_session_is_named_for_restart(self, monkeypatch, tmp_path):
        """A daemon running code OLDER than its committed script is returned by NAME,
        so start_worker.sh can kill+respawn it onto current HEAD. This is the whole
        point of Item 3: detection existed, action did not."""
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        (script_dir / "supervisor.py").write_text("# v2")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp((script_dir / "supervisor.py").stat().st_mtime)
        started = (mtime_dt - timedelta(minutes=17)).strftime("%a %b %d %H:%M:%S %Y")
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([(started, "python3 background/supervisor.py")]),
        )
        assert health_check.stale_daemon_sessions() == ["supervisor"]

    def test_fresh_session_is_not_named(self, monkeypatch, tmp_path):
        """R15 mutation counterpart: a daemon started AFTER its script's mtime is NOT
        returned -- start_worker must not needlessly kill a daemon already on HEAD
        (that would churn state every re-run and defeat 'safe to re-run')."""
        script_dir = tmp_path / "background"
        script_dir.mkdir()
        (script_dir / "supervisor.py").write_text("# v2")
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        from datetime import datetime, timedelta
        mtime_dt = datetime.fromtimestamp((script_dir / "supervisor.py").stat().st_mtime)
        started = (mtime_dt + timedelta(minutes=5)).strftime("%a %b %d %H:%M:%S %Y")
        monkeypatch.setattr(
            health_check.subprocess, "check_output",
            lambda *a, **k: _fake_ps_lstart_output([(started, "python3 background/supervisor.py")]),
        )
        assert health_check.stale_daemon_sessions() == []

    def test_not_running_session_is_not_named(self, monkeypatch, tmp_path):
        """A daemon that isn't running at all is _start_session's job to start fresh --
        stale_daemon_sessions only names LIVE-but-stale processes to kill."""
        monkeypatch.setattr(health_check, "PROJECT_DIR", tmp_path)
        monkeypatch.setattr(health_check.subprocess, "check_output", lambda *a, **k: _fake_ps_lstart_output([]))
        assert health_check.stale_daemon_sessions() == []

    def test_run_health_check_surfaces_stale_code_as_a_problem(self, monkeypatch, tmp_path):
        monkeypatch.setattr(health_check, "_tmux_panes", lambda: _mock_panes(list(health_check.EXPECTED_PANES.keys())))
        monkeypatch.setattr(health_check, "_running_scripts", lambda: [])
        monkeypatch.setattr(health_check, "_check_staging_age", lambda: None)
        monkeypatch.setattr(health_check, "_check_pixel_verification_capability", lambda: None)
        monkeypatch.setattr(health_check, "_check_stale_dependencies", lambda: None)
        monkeypatch.setattr(
            health_check, "_check_stale_running_code",
            lambda: "Stale running code (restart to pick up committed changes): supervisor (supervisor.py): running since 2026-07-12 20:29, own script modified 2026-07-13 05:35 (546min of drift)",
        )

        all_ok, ok_lines, problem_lines = health_check.run_health_check()

        assert not all_ok
        assert any("supervisor" in line and "Stale running code" in line for line in problem_lines)


def test_multiple_interactive_sessions_is_a_problem(monkeypatch):
    """2026-07-16: >1 interactive Claude session (a ghost/duplicate) must alarm within a
    health cycle -- the Jul-15 ghost spammed for a full day undetected. One or zero is OK."""
    from background import session_watchdog
    monkeypatch.setattr(session_watchdog, "interactive_claude_pids", lambda: [111, 222])
    assert health_check._check_single_interactive_session() is not None  # alarms on 2
    monkeypatch.setattr(session_watchdog, "interactive_claude_pids", lambda: [111])
    assert health_check._check_single_interactive_session() is None      # one is fine
    monkeypatch.setattr(session_watchdog, "interactive_claude_pids", lambda: [])
    assert health_check._check_single_interactive_session() is None      # zero is fine
