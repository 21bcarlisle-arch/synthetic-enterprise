"""RUNG-1 PUBLISH-GATE WEDGE draw -- R15 both-ways proof (director rulings UNWEDGE_PUBLISH_
PRIORITY_ZERO 2026-07-23 + WEDGE3_AND_RUNG1_MECHANISE 2026-07-24, the SECOND consumed-not-absorbed
on the same rule).

The mechanism: a publish gate that has been failing for >60 min while alerts fire and the tick
idles is PRIORITY-ZERO drawable work -- it blocks ALL publishing, so it outranks every product/
HARDEN lane. `supervisor._publish_gate_wedge_active()` is the detector; it is wired as the TOP rung
of `_self_refill_draw` and mirrored in `_is_drained_and_gated`.

R15 requires a control that can FAIL. These tests prove it BOTH ways:
  * MUST FIRE: this morning's exact state (>=3 failures in-window + alerts firing + no pass at HEAD +
    wedge_since >60 min ago) -> the detector returns a draw, `_self_refill_draw` returns it ABOVE the
    product lanes, and `_is_drained_and_gated` refuses rest.
  * MUST STAY SILENT: a passed gate (last_tested == HEAD), an empty/absent state, a lone flake
    (< threshold), and a wedge younger than 60 min all return None and leave rest/draw untouched.
The window-trim root cause is covered too: `alerted_at`/`failures` alone cap the measurable age below
60 min for a live wedge, so `wedge_since` (persistent, un-trimmed) is what makes ">60 min" provable.
"""
import json
from pathlib import Path

import pytest

from background import supervisor


HOUR = 60 * 60


def _wedged_state(now, *, n=8, wedge_since_age=2 * HOUR, alerted_age=30 * 60, include_wedge_since=True):
    """Construct a realistic wedged .publish_gate_state.json dict.

    Defaults mirror this morning's state: a sustained wedge (8 failures), the failures themselves
    all inside the trimmed 1h window, an alarm that fired ~30 min ago, and a PERSISTENT wedge_since
    ~2h old (the field the writer now stamps). `include_wedge_since=False` reproduces a LEGACY state
    file written before the wedge_since change landed."""
    failures = [
        {"ts": now - (i * 6 * 60), "reason": f"process_run_complete rc=1 on run_complete_{i}.md",
         "rc": 1, "kind": "test_regression", "git_hash": "deadbeef"}
        for i in range(n)
    ]
    state = {"failures": failures, "alerted_at": now - alerted_age}
    if include_wedge_since:
        state["wedge_since"] = now - wedge_since_age
    return state


def _write(tmp_path, monkeypatch, state, *, head="HEADHASH", last_tested="OLDHASH"):
    sp = tmp_path / ".publish_gate_state.json"
    lp = tmp_path / ".last_tested_hash"
    sp.write_text(json.dumps(state))
    lp.write_text(last_tested)
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", lp)
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: head)
    return sp, lp


# ─────────────────────────── MUST FIRE (the wedge is real and old) ──────────────────────────

def test_fires_on_this_mornings_exact_state(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    msg = supervisor._publish_gate_wedge_active(now=now)
    assert msg is not None
    assert "PUBLISH-GATE WEDGE" in msg and "RUNG 1" in msg and "PRIORITY ZERO" in msg
    # carries the diagnostic payload (R5): how long, how many, and the HEAD it never passed
    assert "min" in msg and "8 failures" in msg and "HEADHASH" in msg


def test_self_refill_draw_returns_wedge_above_product_lanes(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    # Even with a live BUILD atom available, the wedge rung MUST win (it is checked first).
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent",
                        lambda *a, **k: [{"id": "SOME_BUILD_ATOM"}])
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    out = supervisor._self_refill_draw()
    assert out is not None and "PUBLISH-GATE WEDGE" in out and "SOME_BUILD_ATOM" not in out


def test_is_drained_and_gated_refuses_rest_while_wedged(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now))
    monkeypatch.setattr(supervisor.time, "time", lambda: now)
    # Every OTHER lane empty -> the ONLY thing keeping the tick awake is the wedge rung.
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_actionable_backlog_item", lambda *a, **k: None)
    assert supervisor._is_drained_and_gated() is False


def test_fires_via_alerted_at_when_wedge_since_absent_but_old(tmp_path, monkeypatch):
    """LEGACY fallback: a state file written before wedge_since existed still fires if alerted_at
    (or the earliest in-window failure) is itself >60 min old -- fail-safe TOWARD drawing."""
    now = 1_800_000_000.0
    state = _wedged_state(now, include_wedge_since=False, alerted_age=95 * 60)
    _write(tmp_path, monkeypatch, state)
    assert supervisor._publish_gate_wedge_active(now=now) is not None


# ─────────────────────────── MUST STAY SILENT (no draw, rest allowed) ───────────────────────

def test_silent_when_gate_passed_at_head(tmp_path, monkeypatch):
    """INDEPENDENCE (R15 anti-tautology): even with failures on file, a pass at HEAD => stale
    failures => no phantom wedge draw."""
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now), head="SAMEHASH", last_tested="SAMEHASH")
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_on_empty_state(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, {"failures": [], "alerted_at": None, "wedge_since": None})
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_on_absent_state_file(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / "nope.json")
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / "nope_hash")
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: "H")
    assert supervisor._publish_gate_wedge_active(now=1_800_000_000.0) is None


def test_silent_on_lone_flake_below_threshold(tmp_path, monkeypatch):
    now = 1_800_000_000.0
    _write(tmp_path, monkeypatch, _wedged_state(now, n=2))  # < PUBLISH_GATE_WEDGE_MIN_FAILURES
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_silent_when_wedge_younger_than_60_min(tmp_path, monkeypatch):
    """A fresh sustained wedge (alarm already fired, but only ~40 min old) must NOT yet draw -- the
    rule is 60 min. This is the boundary the window-trim problem hid; wedge_since makes it precise."""
    now = 1_800_000_000.0
    state = _wedged_state(now, wedge_since_age=40 * 60, alerted_age=20 * 60, include_wedge_since=True)
    # earliest failure also < 60 min (n=8 * 6min = 42min span), so no candidate is >60 min old
    _write(tmp_path, monkeypatch, state)
    assert supervisor._publish_gate_wedge_active(now=now) is None


def test_malformed_state_is_silent_not_raising(tmp_path, monkeypatch):
    sp = tmp_path / ".publish_gate_state.json"
    sp.write_text("{ this is not json")
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / "h")
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: "H")
    # never raises into the draw ladder
    assert supervisor._publish_gate_wedge_active(now=1_800_000_000.0) is None
