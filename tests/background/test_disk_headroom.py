#!/usr/bin/env python3
"""R15 proof for the disk governor (director ruling, 2026-08-19).

The ruling named three properties and each is tested as a separate mechanism, because the
failure this replaces was not a missing idea — it was an idea nobody ran. `resource_headroom`
was built on 2026-08-10 after 64 oom-kills and had never executed once: no caller, no unit,
no state file. So the tests that matter most here are the two at the bottom, which assert the
WIRING rather than the logic.

The fail-closed direction is deliberate and asymmetric, and both halves are driven:
  * an unreadable filesystem reads as PRESSURE — a governor that cannot see the disk must
    never certify it healthy;
  * the REAPER is the exception and fails toward KEEPING — it deletes only what it can
    positively identify as this project's own scratch, because a reaper that deletes on
    uncertainty is a worse failure than a full disk.
"""
from __future__ import annotations

import time

import pytest

from background import disk_headroom as dh


# ---------------------------------------------------------------------------
# Property 2: alarm BEFORE exhaustion
# ---------------------------------------------------------------------------
def test_the_bands_alarm_before_exhaustion_not_at_it():
    """The floor is two publish cycles of warning, not a round number. If this ever drops to
    a few hundred MB the alarm announces the stop instead of predicting it -- the failure the
    RAM governor's own comment names and this one inherited."""
    assert dh.PRESSURE_FLOOR_MB >= 2048
    assert dh.CRITICAL_FLOOR_MB < dh.PRESSURE_FLOOR_MB < dh.RECOVERED_FLOOR_MB
    assert dh.band(dh.PRESSURE_FLOOR_MB + 1) == dh.HEALTHY
    assert dh.band(dh.PRESSURE_FLOOR_MB) == dh.PRESSURE
    assert dh.band(dh.CRITICAL_FLOOR_MB) == dh.CRITICAL


def test_MUTATION_the_hysteresis_gap_stops_a_flapping_alarm():
    """Between the floors, a filesystem that has been in pressure stays in pressure. Without
    this a disk hovering at the boundary alarms every cycle and gets muted."""
    between = (dh.PRESSURE_FLOOR_MB + dh.RECOVERED_FLOOR_MB) // 2
    assert dh.band(between, previous=dh.PRESSURE) == dh.PRESSURE
    assert dh.band(between, previous=dh.HEALTHY) == dh.HEALTHY
    assert dh.band(dh.RECOVERED_FLOOR_MB + 1, previous=dh.PRESSURE) == dh.HEALTHY


def test_MUTATION_FAIL_CLOSED_an_unreadable_filesystem_is_pressure_never_healthy(monkeypatch):
    def boom(_p):
        raise OSError("no such filesystem")

    monkeypatch.setattr(dh.shutil, "disk_usage", boom)
    reading = dh.observe()
    assert reading["band"] == dh.PRESSURE
    assert reading["free_mb"] == 0


def test_the_alarm_fires_on_transition_only(monkeypatch, tmp_path):
    """R5. An unchanged status is never re-announced, or the signal becomes noise."""
    monkeypatch.setattr(dh, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": 100, "used_pct": 99.9, "tightest": "/tmp", "paths": {}})
    first = dh.observe()
    assert first["changed"] and first.get("alarm")
    second = dh.observe()
    assert not second["changed"] and "alarm" not in second


# ---------------------------------------------------------------------------
# Property 1: bounded lifetimes
# ---------------------------------------------------------------------------
def test_every_scratch_pattern_names_a_real_creator():
    """The first draft of SCRATCH_PATTERNS was GUESSED and one entry (`head-checkout-*`)
    matched nothing this project has ever made -- a decorative reaper. Every prefix must be
    one the tooling actually produces."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    sources = " ".join(
        (root / f).read_text(encoding="utf-8")
        for f in ("tools/surgical_land.py", "tools/epistemic_wall.py",
                  "background/process_run_complete.py")
    )
    for pattern, _ttl in dh.SCRATCH_PATTERNS:
        stem = pattern.rstrip("*")
        if stem.startswith("pytest-of"):
            continue  # pytest's own, not ours
        assert stem in sources, (
            f"{pattern!r} matches no prefix any module in this repo creates -- a reaper "
            "pattern that matches nothing is decoration"
        )


def test_both_scratch_roots_are_watched_and_reaped():
    """The two biggest producers default to /var/tmp, not /tmp. A governor watching only the
    volume that failed last time is blind to where most scratch lands."""
    watched = {str(p) for p in dh.WATCHED}
    assert "/tmp" in watched and "/var/tmp" in watched
    assert {str(p) for p in dh.REAP_ROOTS} == {"/tmp", "/var/tmp"}


def test_MUTATION_expired_scratch_is_reaped_and_fresh_scratch_is_not(tmp_path):
    old = tmp_path / "wall-head-old"
    new = tmp_path / "wall-head-new"
    for d in (old, new):
        d.mkdir()
        (d / "payload").write_bytes(b"x" * 2048)
    ancient = time.time() - (9 * 3600)
    import os
    os.utime(old, (ancient, ancient))

    victims = {v["path"] for v in dh.reapable(roots=(tmp_path,))}
    assert str(old) in victims
    assert str(new) not in victims

    dh.reap(roots=(tmp_path,))
    assert not old.exists()
    assert new.exists(), "a fresh scratch dir was reaped -- a live gate run would be shot"


def test_MUTATION_an_unrecognised_directory_is_NEVER_reaped(tmp_path):
    """The reaper fails toward KEEPING. Positive identification only: the 80 directories that
    filled the disk had ad-hoc names and a pattern-matching reaper cannot claim them -- which
    is correct, because a reaper that deletes on uncertainty is worse than a full disk."""
    stranger = tmp_path / "someone-elses-important-data"
    stranger.mkdir()
    ancient = time.time() - (99 * 3600)
    import os
    os.utime(stranger, (ancient, ancient))
    assert dh.reapable(roots=(tmp_path,)) == []
    dh.reap(roots=(tmp_path,))
    assert stranger.exists()


def test_a_directory_in_use_is_never_reaped_however_old(tmp_path, monkeypatch):
    victim = tmp_path / "wall-head-busy"
    victim.mkdir()
    ancient = time.time() - (99 * 3600)
    import os
    os.utime(victim, (ancient, ancient))
    monkeypatch.setattr(dh, "in_use_dirs", lambda: {str(victim)})
    assert dh.reapable(roots=(tmp_path,)) == []


# ---------------------------------------------------------------------------
# Property 3: admission
# ---------------------------------------------------------------------------
def test_admission_refuses_below_the_floor(monkeypatch):
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": 300, "used_pct": 99.0, "tightest": "/tmp", "paths": {}})
    monkeypatch.setattr(dh, "reap", lambda *a, **k: {"freed_mb": 0, "removed": []})
    ok, why = dh.admit(need_mb=256)
    assert not ok and "REFUSED" in why


def test_admission_reaps_before_refusing(monkeypatch):
    """The space may already be there. Refusing without trying would stop the machine for
    scratch that expired hours ago."""
    state = {"free": 300}
    monkeypatch.setattr(dh, "sample", lambda *a, **k: {
        "free_mb": state["free"], "used_pct": 50.0, "tightest": "/tmp", "paths": {}})

    def fake_reap(*a, **k):
        state["free"] = 9000
        return {"freed_mb": 8700, "removed": [{"path": "/tmp/wall-head-x"}]}

    monkeypatch.setattr(dh, "reap", fake_reap)
    ok, why = dh.admit(need_mb=256)
    assert ok and "after reaping" in why


# ---------------------------------------------------------------------------
# THE WIRING -- the property whose absence caused both outages
# ---------------------------------------------------------------------------
def test_both_governors_are_called_by_a_running_daemon():
    """THE test. `resource_headroom` was built after 64 oom-kills and never ran: no caller, no
    unit, no state file. A governor nobody calls is not a governor. If this fails, someone has
    unwired the housekeeping and the next exhaustion is only a matter of time."""
    import inspect
    from background import background_worker

    src = inspect.getsource(background_worker.main)
    assert "disk_headroom" in src, "the disk governor is not called by the worker loop"
    assert "resource_headroom" in src, (
        "the MEMORY governor is still unwired -- it has never run once since 2026-08-10"
    )


def test_the_governors_cannot_crash_the_worker():
    """A governor that can take the daemon down is a worse outage than the one it prevents."""
    import inspect
    from background import background_worker

    src = inspect.getsource(background_worker.main)
    head = src.split("process_leftover_run_markers")[0]
    assert "try:" in head and "except Exception" in head, (
        "the headroom calls are not wrapped -- a governor fault would kill the worker"
    )
