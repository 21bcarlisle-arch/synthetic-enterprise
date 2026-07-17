"""Tests for OPS1 sub-step 2 (G-L2): the declared-process manifest + reconciler.

These are the R15/MAKE_IT_STICK mechanisms that make the single-declaration guarantee stick:
the manifest is the ONE source (start_worker + health_check derive from it), state
distinguishes intended-down from failed, and today's incident (a HELD daemon resurrected) is
a permanent invariant here — incidents become invariants."""
from __future__ import annotations

from pathlib import Path

import pytest

from background import process_reconciler as R


def _status(results, session):
    return next(r for r in results if r["session"] == session)


def test_manifest_loads_and_is_shaped():
    procs = R.load_manifest()
    assert procs
    for p in procs:
        assert {"session", "command", "match", "owner", "state"} <= set(p), p
        assert p["state"] in R.VALID_STATES
        if p["state"] != "enabled":
            assert p.get("reason") and p.get("flip"), f"{p['session']} missing reason/flip"


def test_start_worker_has_no_hardcoded_daemon_list_left():
    """Exit-test criterion 1: start_worker.sh must NOT carry a hardcoded launch list any
    more — it derives from the manifest. The only `_start_session` token allowed is the
    function DEFINITION and the derived loop's single call; no `_start_session "daemon"`
    literal launchers survive (that was the third source of truth)."""
    text = (Path(R.__file__).resolve().parent / "start_worker.sh").read_text()
    import re
    literal_launchers = re.findall(r'^\s*_start_session\s+"[a-z-]+"', text, re.MULTILINE)
    assert literal_launchers == [], f"hardcoded launchers still present: {literal_launchers}"


def test_startlist_is_enabled_and_dark_owned_by_start_worker():
    names = [s for s, _ in R.startlist()]
    assert "sim-runner" in names            # enabled
    assert "executor-daemon" in names       # dark: launched (as a no-op) by start_worker
    assert "supervisor" not in names        # HELD: not launched — that IS the hold
    assert "deadmans-switch" not in names   # HELD
    assert "claude" not in names            # worker seat: owned by session-watchdog, not start_worker
    assert "autonomous-runner" not in names # retired


def test_health_checked_excludes_held_dark_retired_includes_enabled():
    """THE cure: held/dark/retired are excluded from the health-checked set, so a
    deliberately-held daemon never reads as a fault (the false-DEGRADED class)."""
    hc = R.health_checked_map()
    assert "naive-organ" in hc                 # the gap the old EXPECTED_PANES had
    for held in ("supervisor", "deadmans-switch", "session-watchdog", "claude"):
        assert held not in hc                  # held -> not a fault when down
    assert "executor-daemon" not in hc         # dark
    assert "autonomous-runner" not in hc       # retired
    for enabled in ("sim-runner", "token-proxy", "file-api", "background-worker"):
        assert enabled in hc


def test_incident_held_down_silent_held_running_is_HELD_VIOLATED():
    """THE 2026-07-17 incident as a permanent invariant: a HELD daemon that is DOWN is
    silent (no false DEGRADED); a HELD daemon found RUNNING is HELD_VIOLATED and alarms —
    exactly the deadman the worker resurrected. Incidents become invariants."""
    down = R.reconcile(panes={}, ps_lines=[])
    assert _status(down, "deadmans-switch")["status"] == "HELD"
    assert _status(down, "deadmans-switch")["alarm"] is False
    resurrected = R.reconcile(panes={"deadmans-switch": "python3"}, ps_lines=[])
    assert _status(resurrected, "deadmans-switch")["status"] == "HELD_VIOLATED"
    assert _status(resurrected, "deadmans-switch")["alarm"] is True


def test_enabled_missing_alarms_enabled_running_ok():
    down = R.reconcile(panes={}, ps_lines=[])
    assert _status(down, "sim-runner")["status"] == "MISSING"
    assert _status(down, "sim-runner")["alarm"] is True
    up = R.reconcile(panes={"sim-runner": "python3"}, ps_lines=[])
    assert _status(up, "sim-runner")["status"] == "OK"


def test_dark_absent_ok_dark_running_reports_no_alarm():
    down = R.reconcile(panes={}, ps_lines=[])
    assert _status(down, "executor-daemon")["status"] == "DARK"
    assert _status(down, "executor-daemon")["alarm"] is False
    active = R.reconcile(panes={"executor-daemon": "python3"}, ps_lines=[])
    assert _status(active, "executor-daemon")["status"] == "DARK_ACTIVE"
    assert _status(active, "executor-daemon")["alarm"] is False   # director-authorised


def test_retired_running_alarms():
    down = R.reconcile(panes={}, ps_lines=[])
    assert _status(down, "autonomous-runner")["status"] == "OK"
    running = R.reconcile(panes={"autonomous-runner": "python3"}, ps_lines=[])
    assert _status(running, "autonomous-runner")["status"] == "RETIRED_RUNNING"
    assert _status(running, "autonomous-runner")["alarm"] is True


def test_running_detected_via_ps_token_too():
    ps = ["python3 background/sim_runner.py"]
    res = R.reconcile(panes={}, ps_lines=ps)
    assert _status(res, "sim-runner")["status"] == "OK"


def test_undeclared_background_daemon_flagged_console_never():
    panes = {
        "rogue-daemon": "python3 background/rogue.py",  # undeclared bg daemon -> UNEXPECTED
        "work": "bash",                                  # a director console shell -> ignored
    }
    res = R.reconcile(panes=panes, ps_lines=[])
    assert _status(res, "rogue-daemon")["status"] == "UNEXPECTED"
    assert not any(r["session"] == "work" for r in res)  # console never flagged


def test_reconcile_is_report_only_no_kill_key():
    """G-R3 structural: every result carries only status/report fields — there is no
    action/kill field, so a caller cannot be handed a 'kill this' instruction."""
    for r in R.reconcile(panes={}, ps_lines=[]):
        assert set(r) == {"session", "state", "running", "status", "alarm", "reason", "flip"}
        assert "kill" not in r and "action" not in r


def test_empty_manifest_is_fail_closed(tmp_path):
    bad = tmp_path / "empty.yaml"
    bad.write_text("processes: []\n")
    with pytest.raises(R.ManifestError):
        R.load_manifest(bad)


def test_loader_rejects_held_without_reason_or_flip(tmp_path):
    bad = tmp_path / "m.yaml"
    bad.write_text("processes:\n  - {session: s, command: x, match: s, owner: o, state: held, flip: later}\n")
    with pytest.raises(R.ManifestError, match="reason"):
        R.load_manifest(bad)


def test_health_check_expected_panes_is_derived_and_excludes_held():
    """The consumer binding: EXPECTED_PANES == the enabled map, and a HELD daemon
    (supervisor) is NOT in it — the false-DEGRADED cure, verified end-to-end."""
    from background import health_check
    assert health_check.EXPECTED_PANES == R.health_checked_map()
    assert "naive-organ" in health_check.EXPECTED_PANES
    assert "supervisor" not in health_check.EXPECTED_PANES
