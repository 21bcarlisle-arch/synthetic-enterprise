"""RUNG-1b PERSISTENT OPERATIONAL-LAYER RED draw -- R15 both-ways proof (director console P0,
2026-07-25).

The mechanism: an operational-layer signal (`pytest -m operational` -- the daemon-lifecycle /
IaC-reconcile / capability suite) that has been RED for MORE than OPERATIONAL_RED_DRAWABLE_THRESHOLD
consecutive hourly checks is PRIORITY-ZERO drawable work, not an alarm to admire. It outranks every
product/HARDEN lane. `supervisor._operational_red_persistent_draw()` is the detector; it is wired as
RUNG 1b of `_self_refill_draw` (just below the publish-gate wedge) and mirrored in
`_is_drained_and_gated`.

The overnight incident this reproduces: the signal was RED for 13 consecutive checks (an orphaned
systemd unit for the retired director-comments daemon failing the anti-drift reconcile, plus a
pixel-verification capability regression) and the ONLY response was an hourly page -- no draw rung
ever surfaced 'go fix the red daemon-lifecycle suite', so the tick rested beside it all night. That
is the consumed-not-absorbed class R17/MAKE_IT_STICK forbids: a rule lives as enforced code or not
at all.

R15 requires a control that can FAIL. These tests prove it BOTH ways:
  * MUST FIRE: the exact overnight state (consecutive_red=13, last_result='red') -> the detector
    returns a draw, `_self_refill_draw` returns it ABOVE the product lanes, and
    `_is_drained_and_gated` refuses rest.
  * MUST STAY SILENT: a GREEN result, a below-threshold red (<=3 consecutive), a stale counter with a
    green last_result, and an absent/malformed state file all return None and leave rest/draw
    untouched.
"""
import json
from pathlib import Path

import pytest

from background import supervisor


def _write_signal(tmp_path, monkeypatch, state):
    sp = tmp_path / ".operational_layer_signal.json"
    if state is not None:
        sp.write_text(state if isinstance(state, str) else json.dumps(state))
    monkeypatch.setattr(supervisor, "OPERATIONAL_LAYER_SIGNAL_FILE", sp)
    return sp


# ─────────────────────────── MUST FIRE (persistent red, past paging) ──────────────────────────

def test_fires_on_the_exact_overnight_state(tmp_path, monkeypatch):
    """consecutive_red=13, last_result='red' -- the literal state recorded overnight
    (docs/observability/.operational_layer_signal.json at 05:44Z 2026-07-25)."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_green": 0, "consecutive_red": 13, "last_result": "red",
                   "last_run_ts": 1784957831.287541})
    msg = supervisor._operational_red_persistent_draw()
    assert msg is not None
    assert "PERSISTENT-RED" in msg
    assert "13 consecutive" in msg
    assert "PRIORITY ZERO" in msg


def test_fires_just_above_threshold(tmp_path, monkeypatch):
    """>3 consecutive is the drawable bar; 4 is the first firing value."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_red": supervisor.OPERATIONAL_RED_DRAWABLE_THRESHOLD + 1,
                   "consecutive_green": 0, "last_result": "red"})
    assert supervisor._operational_red_persistent_draw() is not None


def test_self_refill_returns_it_above_product_lanes(tmp_path, monkeypatch):
    """The rung is wired ABOVE the BUILD/SITE/DISCOVERY lanes: even with a fat map of buildable
    atoms, a persistent operational red is drawn FIRST."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_red": 13, "consecutive_green": 0, "last_result": "red"})
    # Neutralise the higher wedge rung and prove the product lanes would otherwise fire.
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent",
                        lambda *a, **k: [{"id": "SOME_BUILD_ATOM"}])
    monkeypatch.setattr(supervisor, "log", lambda *a, **k: None)
    out = supervisor._self_refill_draw()
    assert out is not None
    assert "PERSISTENT-RED" in out


def test_is_drained_and_gated_refuses_rest_while_persistent_red(tmp_path, monkeypatch):
    """Rest is never legitimate while the operational suite is persistently red."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_red": 13, "consecutive_green": 0, "last_result": "red"})
    monkeypatch.setattr(supervisor, "_publish_gate_wedge_active", lambda *a, **k: None)
    # All the lower lanes empty -> without the rung, this would return True (drained). The rung must
    # flip it to False.
    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_site_lane_draw_concurrent", lambda *a, **k: [])
    monkeypatch.setattr(supervisor, "_idle_discover_frame_draw_concurrent", lambda *a, **k: [])
    assert supervisor._is_drained_and_gated() is False


# ─────────────────────────── MUST STAY SILENT (no phantom draw) ──────────────────────────

def test_silent_on_green(tmp_path, monkeypatch):
    """A GREEN result never draws, even if a stale consecutive_red lingers -- the signal's own
    verdict governs."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_red": 13, "consecutive_green": 1, "last_result": "green"})
    assert supervisor._operational_red_persistent_draw() is None


def test_silent_at_and_below_threshold(tmp_path, monkeypatch):
    """<= OPERATIONAL_RED_DRAWABLE_THRESHOLD consecutive reds is paging territory, not drawable --
    page first, mechanise into a draw only once paging has demonstrably not worked."""
    for n in (1, 2, supervisor.OPERATIONAL_RED_DRAWABLE_THRESHOLD):
        _write_signal(tmp_path, monkeypatch,
                      {"consecutive_red": n, "consecutive_green": 0, "last_result": "red"})
        assert supervisor._operational_red_persistent_draw() is None, f"fired at {n}"


def test_silent_on_absent_file(tmp_path, monkeypatch):
    _write_signal(tmp_path, monkeypatch, None)  # no file written
    assert supervisor._operational_red_persistent_draw() is None


def test_silent_on_malformed_file(tmp_path, monkeypatch):
    _write_signal(tmp_path, monkeypatch, "{not json")
    assert supervisor._operational_red_persistent_draw() is None


def test_silent_on_non_dict_json(tmp_path, monkeypatch):
    _write_signal(tmp_path, monkeypatch, "[1, 2, 3]")
    assert supervisor._operational_red_persistent_draw() is None


def test_silent_on_missing_consecutive_red_key(tmp_path, monkeypatch):
    """last_result red but no counter -> fail-safe None (no crash into the draw ladder)."""
    _write_signal(tmp_path, monkeypatch, {"last_result": "red"})
    assert supervisor._operational_red_persistent_draw() is None


def test_silent_on_non_numeric_counter(tmp_path, monkeypatch):
    _write_signal(tmp_path, monkeypatch, {"last_result": "red", "consecutive_red": "lots"})
    assert supervisor._operational_red_persistent_draw() is None
