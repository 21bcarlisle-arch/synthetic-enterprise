"""OPS1 sub-step 4 — the BUILD EXIT TEST (SUBSTEP4_SUPERVISOR_HYBRID.md §9).

This is the single named artifact that proves sub-step 4's BUILD is done. It re-asserts the §9
criteria end-to-end as one coherent check (the piece-wise mechanisms are also tested in
test_process_reconciler / test_generate_units / test_schedule_reconciler / test_worker_seat /
test_boot_announce / test_console_sanctity). Passing this does NOT go live — the gated
one-at-a-time migration (worker-seat -> supervisor -> deadmans) is a separate, director-approved
step. Nothing here starts, stops, or enables anything."""
from __future__ import annotations

import re
from pathlib import Path

from background import generate_units as G
from background import process_reconciler as R

_BG = Path(R.__file__).resolve().parent


def _status(results, session):
    return next(r for r in results if r["session"] == session)


# ── §9.1 units generated from the manifest == committed units (anti-drift) ──

def test_committed_units_equal_generated():
    committed = {p.name: p.read_text() for p in (_BG / "systemd").glob("*.service")}
    assert committed == G.regenerate()


# ── §9.2 HELD<->unit mapping mutation-tested: MISSING / HELD_VIOLATED / DARK / retired ──

# The autonomy migration is COMPLETE — the live manifest has no `held` daemon — so the HELD leg of
# the mapping is exercised on a synthetic manifest (the invariant survives the migration).
_HELD_MANIFEST = """version: 2
processes:
  - {session: en, command: python3 background/en.py, match: en.py, owner: systemd, launched_by: systemd, state: enabled}
  - {session: hl, command: python3 background/hl.py, match: hl.py, owner: systemd, launched_by: systemd, state: held, reason: r, flip: f}
"""


def test_held_unit_mapping_full_matrix(tmp_path):
    # enabled/dark/retired legs on the LIVE manifest (those states still exist there)
    down = R.reconcile(unit_states={}, seat_active=False)
    assert _status(down, "sim-runner")["status"] == "MISSING"       # enabled, down -> fault
    assert _status(down, "executor-daemon")["status"] == "DARK"     # dark, down -> ok
    assert _status(down, "autonomous-runner")["status"] == "OK"     # retired, down -> ok
    # HELD leg on a synthetic manifest (no live daemon is held post-migration)
    hm = tmp_path / "held.yaml"
    hm.write_text(_HELD_MANIFEST)
    hdown = R.reconcile(unit_states={}, seat_active=False, path=hm)
    assert _status(hdown, "hl")["status"] == "HELD" and _status(hdown, "hl")["alarm"] is False
    hup = R.reconcile(unit_states={"hl": {"active": True}}, seat_active=False, path=hm)
    assert _status(hup, "hl")["status"] == "HELD_VIOLATED" and _status(hup, "hl")["alarm"] is True


# ── §9.3 G-L3: a failed / crash-looping unit ALARMS (the 32,707 case, now caught) ──

def test_g_l3_unit_failed_and_crashlooping_alarm():
    failed = R.reconcile(unit_states={"sim-runner": {"active": False, "substate": "failed"}},
                         seat_active=False)
    assert _status(failed, "sim-runner")["status"] == "UNIT_FAILED"
    looping = R.reconcile(
        unit_states={"ntfy-responder": {"active": False, "substate": "auto-restart"}},
        seat_active=False)
    assert _status(looping, "ntfy-responder")["status"] == "UNIT_CRASHLOOPING"
    assert all(s in R.ALARM_STATUSES for s in ("UNIT_FAILED", "UNIT_CRASHLOOPING"))


# ── §9.4 reaper gone: no process-kill path anywhere; exit-143 impossible by construction ──

def test_reaper_absent_no_kill_path_in_background():
    kill_call = re.compile(r"os\.kill\s*\(|signal\.SIGTERM|signal\.SIGKILL")
    import glob
    for path in glob.glob(str(_BG / "*.py")):
        src = Path(path).read_text()
        assert "def reap_orphan" not in src, path
        assert kill_call.search(src) is None, f"{path}: a process-kill call reappeared"


def test_exit_143_invariant_still_holds_against_console_sanctity():
    """The exit-143 CLASS invariant survives the reaper's deletion (SUBSTEP4 §6): a sanctified
    console is spared and the marker is tmux-independent. Consumer gone, contract kept."""
    from background import console_sanctity as cs
    import os
    assert cs.sanctify(os.getpid()) is True
    assert cs.is_sanctified(os.getpid()) is True   # reads /proc + registry only, no tmux
    cs.unsanctify(os.getpid())
    assert cs.is_sanctified(os.getpid()) is False


# ── the current safe posture: held layer HELD, executor DARK, seat HELD ──

def test_declared_posture_autonomy_layer_fully_migrated():
    """The autonomy layer is now FULLY migrated (all three gates taken, one at a time): worker-seat
    + supervisor + deadmans all enabled + launched_by systemd (they left start_worker's tmux set);
    the seat live; executor DARK (director-gated separately); autonomous-runner retired. The
    manifest declares the live truth — never a held-but-running lie — and no autonomy daemon is
    held any more."""
    m = {e["session"]: e for e in R.load_manifest()}
    for migrated in ("worker-seat-manager", "supervisor", "deadmans-switch"):
        assert m[migrated]["state"] == "enabled", migrated
        assert m[migrated]["launched_by"] == "systemd", migrated   # left the tmux launch set
    assert m["claude"]["state"] == "enabled"                       # the seat is live
    assert m["executor-daemon"]["state"] == "dark"
    assert m["autonomous-runner"]["state"] == "retired"
    assert not any(e["state"] == "held" for e in m.values())       # no daemon left held


# ── the build never starts anything: install is install+enable only, migration starts ──

def test_install_schedule_never_starts_a_service_daemon():
    """install_schedule.sh installs + enables (boot-start) only — it must NOT `systemctl start` any
    .service DAEMON (bringing a daemon live is the gated one-at-a-time migration). The ONE allowed
    start is ARMING a .timer (scheduling, not launching a daemon), and it must be guarded to
    `*.timer)` so it can never start a .service."""
    text = (_BG / "install_schedule.sh").read_text()
    for m in re.finditer(r"systemctl\s+--user\s+start\b[^\n]*", text):
        line = m.group(0)
        # every start must be arming "$name" inside the *.timer) case (never a literal .service)
        assert '"$name"' in line, f"unexpected start target: {line!r}"
        assert ".service" not in line, f"a .service is being started: {line!r}"
    # and the only start present is the timer-guarded one
    assert "*.timer) systemctl --user start" in text
