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


# The autonomy migration is COMPLETE — the LIVE manifest has no `held` daemon any more (all three
# migrated to systemd). So the held/dark/retired MAPPING is exercised against a SYNTHETIC manifest
# (stable regardless of the live posture); the live posture is asserted separately.
_MAP_MANIFEST = """version: 2
processes:
  - {session: en, command: python3 background/en.py, match: en.py, owner: systemd, launched_by: systemd, state: enabled}
  - {session: hl, command: python3 background/hl.py, match: hl.py, owner: systemd, launched_by: systemd, state: held, reason: r, flip: f}
  - {session: dk, command: python3 background/dk.py, match: dk.py, owner: systemd, launched_by: systemd, state: dark, reason: r, flip: f}
  - {session: rt, command: python3 background/rt.py, match: rt.py, owner: none, state: retired, reason: r, flip: f}
"""


@pytest.fixture
def map_manifest(tmp_path):
    p = tmp_path / "map_manifest.yaml"
    p.write_text(_MAP_MANIFEST)
    return p


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


def test_startlist_is_enabled_dark_and_not_yet_migrated():
    # OPS1 sub-step 4: startlist = daemons start_worker.sh still TMUX-launches (owner==systemd,
    # enabled|dark, NOT migrated to systemd). A migrated daemon LEAVES this set.
    names = [s for s, _ in R.startlist()]
    assert "executor-daemon" in names       # dark: installed (no-op) unit, still tmux
    # 2026-08-09: sim-runner MOVED to the migrated side. Its unit was installed+enabled+ACTIVE
    # and stamping boot SHAs, while `launched_by` still said tmux — the same half-done cutover
    # that hit staging-watcher and ntfy-responder on 2026-07-29, left un-flipped on seven more
    # rows. See test_systemd_owned_sessions_are_only_the_migrated_ones below.
    assert "sim-runner" not in names        # MIGRATED to systemd (launched_by) — left the tmux set
    assert "background-worker" not in names  # MIGRATED to systemd (launched_by) — left the tmux set
    assert "supervisor" not in names        # MIGRATED to systemd (launched_by) — left the tmux set
    assert "deadmans-switch" not in names   # MIGRATED to systemd (launched_by) — left the tmux set
    assert "claude" not in names            # worker seat: owned by worker-seat-manager, not systemd
    assert "worker-seat-manager" not in names  # MIGRATED to systemd (launched_by) — left the tmux set
    assert "autonomous-runner" not in names # retired


def test_migrated_daemon_leaves_startlist_but_generate_units_still_has_it():
    """The atomic-migration invariant: a daemon flipped to launched_by=systemd LEAVES start_worker's
    tmux launch set (never two launchers) but stays a declared systemd unit (its .service exists)."""
    names = [s for s, _ in R.startlist()]
    assert "worker-seat-manager" not in names
    from background import generate_units as G
    assert "worker-seat-manager.service" in G.regenerate()   # still a real systemd unit


def _user_systemd_available() -> bool:
    import subprocess
    try:
        return subprocess.run(["systemctl", "--user", "is-system-running"],
                              capture_output=True).returncode in (0, 1)
    except Exception:
        return False


@pytest.mark.real_subprocess   # the claim is about the LIVE box; a stub cannot make it
@pytest.mark.skipif(not _user_systemd_available(), reason="no --user systemd on this host")
def test_manifest_launched_by_agrees_with_the_observed_world():
    """R10 CLASS CLOSURE for the half-done cutover, replacing the hardcoded migrated-set test that
    `_systemd_owned_sessions` used to back (that selector is deleted — PW1, 2026-08-09).

    History: on 2026-07-29 the two-launcher defect was diagnosed precisely and TWO rows were
    patched while SEVEN identical ones were left standing. The instance test could not see them,
    because it asserted a hand-written list against the same hand-written manifest — a tautology
    (R15). This one compares the DECLARATION against the OBSERVED world, so the next half-done
    cutover reds on its own, without anyone remembering to extend a list.

    The second-order cost is why this matters more than double-launching: an un-flipped row also
    removed its daemon from the staleness detector's population, which is how sim-runner and
    background-worker ran pre-cure code for ~10h through the second publish wedge while the drift
    check reported clean."""
    misdeclared = R.evaluate_boot_sha_drift()["misdeclared"]
    assert misdeclared == [], (
        "manifest `launched_by` disagrees with the observed launcher for: "
        + ", ".join(f"{m['session']} (declared {m['declared']}, observed {m['observed']})"
                    for m in misdeclared))


def test_health_checked_includes_all_migrated_autonomy_daemons():
    """dark/retired excluded from the health-checked set; the now-live autonomy layer — all three
    migrated (worker-seat-manager + seat + supervisor + deadmans, enabled) — is included."""
    hc = R.health_checked_map()
    assert "naive-organ" in hc                 # the gap the old EXPECTED_PANES had
    for migrated in ("worker-seat-manager", "claude", "supervisor", "deadmans-switch"):
        assert migrated in hc                  # MIGRATED live (enabled) — the autonomy layer
    assert "executor-daemon" not in hc         # dark
    assert "autonomous-runner" not in hc       # retired
    assert "file-api" not in hc                # systemd-owned service, not a tmux daemon (sub-step 3)
    for enabled in ("sim-runner", "token-proxy", "background-worker"):
        assert enabled in hc


# OPS1 sub-step 4: reconcile reads SYSTEMD unit state (injected unit_states) + the worker-seat
# tmux flag (seat_active), NOT tmux panes / ps. `unit_states` = {session: {"active", "substate"}}.
_DOWN = dict(unit_states={}, seat_active=False)


def _up(session, **extra):
    return dict(unit_states={session: {"active": True, **extra}}, seat_active=False)


def test_incident_held_down_silent_held_running_is_HELD_VIOLATED(map_manifest):
    """THE 2026-07-17 incident as a permanent invariant: a HELD daemon that is DOWN is
    silent (no false DEGRADED); a HELD daemon found RUNNING is HELD_VIOLATED and alarms —
    exactly the deadman the worker resurrected. Incidents become invariants. (Exercised on the
    synthetic manifest now that the live one has no held daemon — the invariant survives the
    migration.)"""
    down = R.reconcile(unit_states={}, seat_active=False, path=map_manifest)
    assert _status(down, "hl")["status"] == "HELD"
    assert _status(down, "hl")["alarm"] is False
    resurrected = R.reconcile(unit_states={"hl": {"active": True}}, seat_active=False, path=map_manifest)
    assert _status(resurrected, "hl")["status"] == "HELD_VIOLATED"
    assert _status(resurrected, "hl")["alarm"] is True


def test_dark_and_retired_mapping_on_synthetic_manifest(map_manifest):
    down = R.reconcile(unit_states={}, seat_active=False, path=map_manifest)
    assert _status(down, "dk")["status"] == "DARK" and _status(down, "dk")["alarm"] is False
    assert _status(down, "rt")["status"] == "OK"
    active = R.reconcile(unit_states={"dk": {"active": True}, "rt": {"active": True}},
                         seat_active=False, path=map_manifest)
    assert _status(active, "dk")["status"] == "DARK_ACTIVE" and _status(active, "dk")["alarm"] is False
    assert _status(active, "rt")["status"] == "RETIRED_RUNNING" and _status(active, "rt")["alarm"] is True


def test_enabled_missing_alarms_enabled_running_ok():
    down = R.reconcile(**_DOWN)
    assert _status(down, "sim-runner")["status"] == "MISSING"
    assert _status(down, "sim-runner")["alarm"] is True
    up = R.reconcile(**_up("sim-runner"))
    assert _status(up, "sim-runner")["status"] == "OK"


def test_dark_absent_ok_dark_running_reports_no_alarm():
    down = R.reconcile(**_DOWN)
    assert _status(down, "executor-daemon")["status"] == "DARK"
    assert _status(down, "executor-daemon")["alarm"] is False
    active = R.reconcile(**_up("executor-daemon"))
    assert _status(active, "executor-daemon")["status"] == "DARK_ACTIVE"
    assert _status(active, "executor-daemon")["alarm"] is False   # director-authorised


def test_retired_running_alarms():
    down = R.reconcile(**_DOWN)
    assert _status(down, "autonomous-runner")["status"] == "OK"
    running = R.reconcile(**_up("autonomous-runner"))
    assert _status(running, "autonomous-runner")["status"] == "RETIRED_RUNNING"
    assert _status(running, "autonomous-runner")["alarm"] is True


def test_unit_failed_and_crashlooping_alarm_regardless_of_declared_state():
    """G-L3 / the 32,707 case: a SubState=failed unit -> UNIT_FAILED; auto-restart ->
    UNIT_CRASHLOOPING. Both alarm whatever the declared state — a silent systemd crash-loop
    is the same disease as the invisible cron, now caught by the same reconcile."""
    failed = R.reconcile(unit_states={"sim-runner": {"active": False, "substate": "failed"}},
                         seat_active=False)
    assert _status(failed, "sim-runner")["status"] == "UNIT_FAILED"
    assert _status(failed, "sim-runner")["alarm"] is True
    looping = R.reconcile(unit_states={"staging-watcher": {"active": False, "substate": "auto-restart"}},
                          seat_active=False)
    assert _status(looping, "staging-watcher")["status"] == "UNIT_CRASHLOOPING"
    assert _status(looping, "staging-watcher")["alarm"] is True


def test_worker_seat_detected_via_seat_flag_not_a_unit():
    """The seat is the ONE entry systemd can't own: detected by `seat_active` (the `claude`
    tmux session), never a unit. Now ENABLED (live): down -> MISSING, up -> OK."""
    down = R.reconcile(unit_states={}, seat_active=False)
    assert _status(down, "claude")["status"] == "MISSING"   # enabled + seat down = a fault
    up = R.reconcile(unit_states={}, seat_active=True)
    assert _status(up, "claude")["status"] == "OK"


def test_unmigrated_daemon_running_via_tmux_is_OK_not_MISSING():
    """Transition-correctness: an enabled daemon still launched by tmux (not migrated) reads OK
    when present in tmux/ps, even though its systemd unit is inactive/absent. Without the OR it
    would false-alarm MISSING for every base-infra daemon during the migration."""
    res = R.reconcile(unit_states={}, seat_active=False, tmux_running={"sim-runner"})
    assert _status(res, "sim-runner")["status"] == "OK"
    # and a genuinely-down enabled daemon still alarms
    assert _status(res, "staging-watcher")["status"] == "MISSING"


def test_migrated_daemon_running_via_systemd_is_OK():
    res = R.reconcile(unit_states={"worker-seat-manager": {"active": True}},
                      seat_active=True, tmux_running=set())
    assert _status(res, "worker-seat-manager")["status"] == "OK"
    assert _status(res, "claude")["status"] == "OK"


def test_reconcile_reads_no_tmux_panes_so_a_console_can_never_be_flagged():
    """G-L1-adjacent, structural: the old UNEXPECTED tmux-pane scan is GONE (absorbed into
    schedule_reconciler's unit view). reconcile now classifies only DECLARED entries from
    systemd/seat state — it cannot even see, let alone flag, the director's console pane."""
    res = R.reconcile(**_DOWN)
    assert {r["session"] for r in res} == R.declared_sessions()  # only declared entries, nothing else


def test_reconcile_is_report_only_no_kill_key():
    """G-R3 structural: every result carries only status/report fields — there is no
    action/kill field, so a caller cannot be handed a 'kill this' instruction."""
    for r in R.reconcile(**_DOWN):
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
    assert "executor-daemon" not in health_check.EXPECTED_PANES   # dark -> excluded (not a fault when down)


def test_no_reaper_or_interactive_claude_kill_path_exists_anywhere():
    """OPS1 sub-step 4 / SUBSTEP4 §9 permanent invariant: the exit-143 console-kill vector is
    impossible by CONSTRUCTION (absence), not inference. Grep proves no background module carries
    the reaper or any process-kill CALL (os.kill / signal.SIGTERM|SIGKILL) — so no code path can
    ever SIGTERM an interactive claude. The word may appear in docstrings/OOM-classification
    strings; only an actual call pattern is a regression."""
    import re
    import glob
    kill_call = re.compile(r"os\.kill\s*\(|signal\.SIGTERM|signal\.SIGKILL")
    here = Path(R.__file__).resolve().parent
    for path in glob.glob(str(here / "*.py")):
        src = Path(path).read_text()
        assert "def reap_orphan" not in src, f"{path}: the reaper was reintroduced"
        m = kill_call.search(src)
        assert m is None, f"{path}: a process-kill call reappeared: {src[m.start():m.start()+50]!r}"

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# --- DOUBLE_LAUNCH: R10 class fix (2026-07-29, DIRECTOR_RULING_FIX_DOUBLE_MESSAGING) ---
# One director NTFY became TWO queued instructions because ntfy-responder had TWO launchers:
# an installed+enabled+ACTIVE systemd unit AND start_worker.sh's tmux launch (the cutover
# installed the unit but never flipped `launched_by: systemd`). staging-watcher was the same
# defect, and produced the doubled staged-file doorbell the director also reported.

def test_double_launch_alarms_when_both_launchers_run(map_manifest):
    """R15 MUTATION-CATCH half: a daemon up on BOTH systemd and tmux is a DOUBLE_LAUNCH alarm.
    Delete the `unit_active and tmux_present` branch in reconcile() and this reds -- the entry
    falls through to plain OK, which is exactly what the reconciler reported for hours while
    two responders each staged the director's message."""
    both = R.reconcile(unit_states={"en": {"active": True}}, seat_active=False,
                       tmux_running={"en"}, path=map_manifest)
    assert _status(both, "en")["status"] == "DOUBLE_LAUNCH"
    assert _status(both, "en")["alarm"] is True
    assert "DOUBLE_LAUNCH" in R.ALARM_STATUSES


def test_single_launcher_by_either_route_is_ok_not_double(map_manifest):
    """R15 FIRES-ON-DEFECT-ONLY half: ONE launcher is healthy by either route. The
    transition-tolerant `or` must survive -- a migrated systemd-only daemon and an
    un-migrated tmux-only daemon are both plain OK, never a false DOUBLE_LAUNCH.
    Weaken the branch to `unit_active or tmux_present` and this reds."""
    systemd_only = R.reconcile(unit_states={"en": {"active": True}}, seat_active=False,
                               tmux_running=set(), path=map_manifest)
    assert _status(systemd_only, "en")["status"] == "OK"
    tmux_only = R.reconcile(unit_states={}, seat_active=False,
                            tmux_running={"en"}, path=map_manifest)
    assert _status(tmux_only, "en")["status"] == "OK"


def test_double_launch_never_flags_the_interactive_seat(map_manifest):
    """The seat is decided by _seat_active alone, never by unit+tmux -- the director's console
    must never be alarmed as a duplicate daemon."""
    res = R.reconcile(unit_states={s: {"active": True} for s in ("en", "hl", "dk", "rt")},
                      seat_active=True, tmux_running={"en", "hl", "dk", "rt"}, path=map_manifest)
    assert all(r["session"] != R.SEAT_MATCH for r in res)


def test_live_readers_cannot_exclude_a_migrated_daemon_from_double_detection():
    """FAIL-OPEN GUARD: both live readers must cover EVERY declared daemon. The original code
    scoped the unit read to `launched_by==systemd` and the tmux scan to `launched_by!=systemd`,
    so a half-migrated daemon was invisible to one reader and a migrated daemon invisible to the
    other -- meaning this very fix would fail open the moment the manifest entry was flipped.
    Restore either filter and this reds."""
    import inspect
    unit_src = inspect.getsource(R._live_unit_states)
    assert 'e.get("owner") == "systemd"' in unit_src
    assert "_systemd_owned_sessions(path)" not in unit_src
    tmux_src = inspect.getsource(R._live_tmux_running)
    # Match the FILTER EXPRESSION, not prose -- the comment above it names `launched_by` while
    # explaining why it must not be filtered on.
    assert 'e.get("launched_by", "tmux") != "systemd"' not in tmux_src, \
        "tmux scan must not filter migrated daemons back out"


def test_no_declared_daemon_has_two_launchers_in_the_committed_manifest():
    """R10 CLASS INVARIANT on the committed declaration: a daemon flipped to
    `launched_by: systemd` must NOT also be in start_worker.sh's tmux launch set. This is the
    declaration-level half -- the live half is the DOUBLE_LAUNCH alarm above."""
    startlist = {s for s, _ in R.startlist()}
    migrated = {e["session"] for e in R.load_manifest()
                if e.get("launched_by", "tmux") == "systemd"}
    both = sorted(startlist & migrated)
    assert both == [], f"declared with TWO launchers (systemd unit + tmux): {both}"


def _fake_proc(stdout: str, rc: int = 0):
    class P:
        pass
    p = P()
    p.stdout = stdout
    p.returncode = rc
    return p


def _fake_subprocess(monkeypatch, ps_lines: str, main_pids: dict[str, int], tmux: str = ""):
    """Stand in for the three shell reads _live_tmux_running makes."""
    def run(cmd, *a, **k):
        if cmd[0] == "tmux":
            return _fake_proc(tmux)
        if cmd[0] == "ps":
            return _fake_proc(ps_lines)
        if cmd[0] == "systemctl" and "MainPID" in cmd:
            session = cmd[3].removesuffix(".service")
            return _fake_proc(f"MainPID={main_pids.get(session, 0)}\n")
        return _fake_proc("")
    monkeypatch.setattr(R.subprocess, "run", run)


def test_a_daemons_own_systemd_process_is_not_counted_as_a_second_launcher(map_manifest, monkeypatch):
    """REGRESSION (2026-07-29, caught on the LIVE box, not by the suite): _live_tmux_running used
    `match in ps_out`, a substring scan over ALL of ps. A systemd-launched daemon's OWN command
    line matches its own `match`, so every migrated daemon reported itself as a second launcher
    and DOUBLE_LAUNCH false-positived on all five healthy daemons. A control that fires on
    healthy input is worse than none -- it trains you to ignore it.

    Drop the `pid != own` exclusion and this reds."""
    _fake_subprocess(monkeypatch,
                     ps_lines="1234 /usr/bin/python3 background/en.py\n",
                     main_pids={"en": 1234})
    assert R._live_tmux_running(path=map_manifest) == set()


def test_a_stray_non_systemd_copy_IS_counted_as_a_second_launcher(map_manifest, monkeypatch):
    """The other half: a process running the daemon that systemd did NOT start is exactly the
    duplicate we hunt. Here PID 1234 is the unit's own; 5678 is a stray tmux/hand launch."""
    _fake_subprocess(monkeypatch,
                     ps_lines="1234 /usr/bin/python3 background/en.py\n"
                              "5678 python3 background/en.py\n",
                     main_pids={"en": 1234})
    assert R._live_tmux_running(path=map_manifest) == {"en"}


def test_unmigrated_daemon_with_no_unit_still_detected_by_ps(map_manifest, monkeypatch):
    """MainPID=0 (no unit / inactive) must not swallow a real tmux-launched daemon -- an
    un-migrated daemon has to keep reading as running, or it would alarm MISSING."""
    _fake_subprocess(monkeypatch,
                     ps_lines="4321 python3 background/dk.py\n",
                     main_pids={})
    assert "dk" in R._live_tmux_running(path=map_manifest)


def test_a_process_merely_mentioning_the_daemon_is_not_a_second_launcher(map_manifest, monkeypatch):
    """REGRESSION (2026-07-29, caught LIVE minutes after the control shipped): the stray scan
    used `match in args`, a substring test, so ANY command line containing the daemon's name
    counted as a second launcher -- `grep en.py`, an editor, a deploy script, or the very
    diagnostic shell command used to investigate the duplicate. DOUBLE_LAUNCH fired on a
    healthy single-launcher daemon. A control that cries wolf on healthy input gets ignored.

    Replace `_runs_daemon(...)` with `e["match"] in args` and this reds."""
    _fake_subprocess(monkeypatch,
                     ps_lines="1234 /usr/bin/python3 background/en.py\n"
                              "9001 grep --color=auto en.py\n"
                              "9002 /bin/bash -c ps -eo args | grep en.py\n"
                              "9003 /usr/bin/python3 -m pytest tests/background/test_en.py\n"
                              "9004 vim background/en.py\n",
                     main_pids={"en": 1234})
    assert R._live_tmux_running(path=map_manifest) == set()


def test_runs_daemon_distinguishes_running_from_mentioning():
    """The predicate itself, both directions."""
    assert R._runs_daemon("/usr/bin/python3 background/en.py", "en.py") is True
    assert R._runs_daemon("python3 background/en.py", "en.py") is True
    assert R._runs_daemon("grep en.py", "en.py") is False
    assert R._runs_daemon("/bin/bash -c ps | grep en.py", "en.py") is False
    assert R._runs_daemon("python3 -m pytest tests/background/test_en.py", "en.py") is False
    assert R._runs_daemon("vim background/en.py", "en.py") is False
    assert R._runs_daemon("", "en.py") is False
