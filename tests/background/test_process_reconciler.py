"""Tests for OPS1 sub-step 2 (G-L2): the declared-process manifest + reconciler.

These are the mutation/anti-drift MECHANISMS (R15, MAKE_IT_STICK) that make the
single-declaration guarantee stick: they fail on the exact defect the manifest exists to
prevent (a health-checked daemon silently dropping out of the declared set, or the two
declarations drifting apart — the state that hid naive-organ from the health check).
"""
from __future__ import annotations

import pytest

from background import process_reconciler as R


def test_manifest_loads_and_is_shaped():
    procs = R.load_manifest()
    assert procs, "manifest must declare processes"
    for p in procs:
        assert {"session", "match", "kind", "health_checked", "purpose"} <= set(p), p
        assert isinstance(p["health_checked"], bool)


def test_manifest_and_start_worker_do_not_drift():
    """ANTI-DRIFT MECHANISM: the manifest's declared session set must EQUAL the set
    start_worker.sh actually launches. If a daemon is added to one and not the other,
    this fails — which is exactly the drift that previously hid naive-organ from the
    health check. (Mutation-proof: drop any entry from the manifest and this goes red.)"""
    assert R.declared_sessions() == R.start_worker_launched_sessions()


def test_health_checked_set_includes_naive_organ_and_excludes_dark_and_services():
    """Regression guard on the EXACT drift found: naive-organ was missing from the old
    hand-maintained EXPECTED_PANES. It must be health-checked now; the dark-gated
    executor-daemon (correct to be absent) and the support services must NOT be."""
    hc = R.health_checked_map()
    assert "naive-organ" in hc
    assert "executor-daemon" not in hc      # dark-gated: absence is expected, not a fault
    assert "token-proxy" not in hc          # support service: informational only
    assert "file-api" not in hc
    # the core loop daemons are all health-checked
    for core in ("supervisor", "session-watchdog", "sim-runner", "deadmans-switch"):
        assert core in hc


def test_reconcile_flags_a_missing_health_checked_daemon():
    """R15 mutation: a health-checked daemon that is not running appears in `missing`."""
    # nothing running at all
    report = R.reconcile(panes={}, ps_lines=[])
    assert "supervisor" in report["missing"]
    assert "deadmans-switch" in report["missing"]


def test_reconcile_does_not_fault_on_dark_daemon_absence():
    """The dark-gated executor-daemon absent is EXPECTED — informational, never a fault."""
    report = R.reconcile(panes={}, ps_lines=[])
    assert "executor-daemon" not in report["missing"]
    assert "executor-daemon" in report["informational_absent"]


def test_reconcile_sees_a_running_daemon_via_pane_or_ps():
    entries = R.load_manifest()
    all_up_panes = {e["session"]: e["match"] for e in entries}
    report = R.reconcile(panes=all_up_panes, ps_lines=[])
    assert report["missing"] == []
    # and via ps lines instead of a pane
    ps = [f"python3 background/{e['match']}" for e in entries]
    report2 = R.reconcile(panes={}, ps_lines=ps)
    # health-checked ones matched by ps token are not missing
    assert "supervisor" not in report2["missing"]


def test_reconcile_flags_an_undeclared_background_daemon_but_not_a_console():
    """An undeclared background python daemon is surfaced; a console seat is NOT (this
    module must never point a kill mechanism at the director's console — see the blackout)."""
    panes = {
        "rogue-daemon": "python3 background/rogue.py",  # undeclared background daemon
        "claude": "node",                                # the managed console seat
        "work": "bash",                                  # a director console shell
    }
    report = R.reconcile(panes=panes, ps_lines=[])
    assert "rogue-daemon" in report["undeclared_daemons"]
    assert "claude" not in report["undeclared_daemons"]
    assert "work" not in report["undeclared_daemons"]


def test_reconcile_is_report_only():
    """Structural: reconcile returns only report keys — there is no action/kill key,
    so a caller cannot be handed a 'kill this' instruction by construction (G-R3)."""
    report = R.reconcile(panes={}, ps_lines=[])
    assert set(report) == {"missing", "informational_absent", "undeclared_daemons"}


def test_empty_manifest_is_fail_closed(tmp_path):
    """An unreadable/empty declaration is a hard error, never a silently-empty set."""
    bad = tmp_path / "empty.yaml"
    bad.write_text("processes: []\n")
    with pytest.raises(ValueError):
        R.load_manifest(bad)


def test_health_check_expected_panes_is_derived_from_manifest():
    """The consumer binding: health_check.EXPECTED_PANES == the manifest's health-checked
    map (single declared source), and it now includes the previously-missing naive-organ."""
    from background import health_check
    assert health_check.EXPECTED_PANES == R.health_checked_map()
    assert "naive-organ" in health_check.EXPECTED_PANES
