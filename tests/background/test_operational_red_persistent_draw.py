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
    # head fns pinned so this stays hermetic: the freshness clause below reads the real repo by
    # default, and a test whose subject is the weather is not a control.
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: 1784957831.287541 - 60, head_hash_fn=lambda: "deadbee")
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


# ── THE RECORD IS NOT REQUIRED TO BE CURRENT (2026-08-14) — R15 both ways ──────────────────
#
# The signal is re-read HOURLY, so between a fix landing and the next check the record still says
# RED and this rung keeps handing PRIORITY-ZERO to already-discharged work, above every other lane.
# Observed live: `fb1493702` fixed the 9-hour red at 16:11 against a record written 15:38, and the
# very next draw was the same finished diagnosis.
#
# The clause does NOT suppress the draw. The stated fail-safe direction is toward drawing, and the
# record freezes RED precisely when the deadman dies -- "old record => stay silent" would rebuild
# the overnight fail-silent this rung exists to kill. So every test below asserts the draw STILL
# FIRES; only the instruction at its head changes.

_RED = {"consecutive_red": 13, "consecutive_green": 0, "last_result": "red"}
_RECORD_TS = 1786718334.9731588   # the live 15:38 record this was found on


def _red_with(**kw):
    return {**_RED, **kw}


def test_a_record_written_before_head_leads_with_re_run_first(tmp_path, monkeypatch):
    """THE INSTANCE. HEAD committed 33 min AFTER the record -> the draw fires, and it leads with
    RE-RUN THE SIGNAL FIRST naming the sha, not with a fresh diagnosis."""
    _write_signal(tmp_path, monkeypatch, _red_with(last_run_ts=_RECORD_TS))
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: _RECORD_TS + 33 * 60, head_hash_fn=lambda: "fb1493702")
    assert msg is not None, "the draw must still fire -- staleness never suppresses it"
    assert msg.startswith("RE-RUN THE SIGNAL FIRST")
    assert "fb1493702" in msg
    assert "33 min BEFORE" in msg
    # and the original draw is still carried in full behind it
    assert "PRIORITY ZERO" in msg and "13 consecutive" in msg


def test_a_record_written_after_head_gets_the_base_draw(tmp_path, monkeypatch):
    """MUST NOT FIRE. Nothing has landed since the record was written, so the red is current and a
    re-run would only burn ten minutes -- diagnose."""
    _write_signal(tmp_path, monkeypatch, _red_with(last_run_ts=_RECORD_TS))
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: _RECORD_TS - 1, head_hash_fn=lambda: "fb1493702")
    assert msg is not None
    assert "RE-RUN" not in msg
    assert msg.startswith("OPERATIONAL-LAYER PERSISTENT-RED")


def test_a_record_written_at_the_same_second_as_head_gets_the_base_draw(tmp_path, monkeypatch):
    """The boundary is STRICT: equal stamps are not evidence that anything landed afterwards."""
    _write_signal(tmp_path, monkeypatch, _red_with(last_run_ts=_RECORD_TS))
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: _RECORD_TS, head_hash_fn=lambda: "fb1493702")
    assert msg is not None and "RE-RUN" not in msg


@pytest.mark.parametrize("state", [
    _red_with(),                          # key absent entirely
    _red_with(last_run_ts=None),
    _red_with(last_run_ts="just now"),
])
def test_an_unreadable_record_stamp_never_softens_the_draw(tmp_path, monkeypatch, state):
    """R15 UNAVAILABLE-IS-FAILED. Without a usable stamp the clause cannot know whether a fix
    landed, and the safe unknown is 'diagnose from scratch' -- never 'assume it is fixed'. git is
    not consulted at all on this path."""
    _write_signal(tmp_path, monkeypatch, state)

    def _must_not_be_called():
        raise AssertionError("git consulted despite an unusable record stamp")

    msg = supervisor._operational_red_persistent_draw(head_time_fn=_must_not_be_called)
    assert msg is not None and "RE-RUN" not in msg


def test_git_unavailable_never_softens_the_draw(tmp_path, monkeypatch):
    """R15 FAIL-SILENT. `_head_commit_epoch` returns None on any git error; the clause must then
    print the base draw, not guess that a fix landed."""
    _write_signal(tmp_path, monkeypatch, _red_with(last_run_ts=_RECORD_TS))
    msg = supervisor._operational_red_persistent_draw(head_time_fn=lambda: None)
    assert msg is not None and "RE-RUN" not in msg


def test_the_clause_cannot_resurrect_a_green_or_below_threshold_record(tmp_path, monkeypatch):
    """The clause is a PREFIX on an already-decided draw, never a second way in. A green record and
    a below-threshold red stay silent however stale they are."""
    for state in ({"consecutive_red": 13, "consecutive_green": 1, "last_result": "green",
                   "last_run_ts": _RECORD_TS},
                  {"consecutive_red": 1, "consecutive_green": 0, "last_result": "red",
                   "last_run_ts": _RECORD_TS}):
        _write_signal(tmp_path, monkeypatch, state)
        assert supervisor._operational_red_persistent_draw(
            head_time_fn=lambda: _RECORD_TS + 3600, head_hash_fn=lambda: "fb1493702") is None


def test_head_commit_epoch_reads_the_real_repo_and_is_defensive():
    """The default supplier is wired to real git (a clause whose supplier is a stub is theatre) and
    swallows every error to None -- it can never raise into the draw ladder."""
    ts = supervisor._head_commit_epoch()
    assert isinstance(ts, float) and ts > 1_700_000_000, ts

    import subprocess as _sp
    orig = _sp.run
    try:
        _sp.run = lambda *a, **k: (_ for _ in ()).throw(OSError("git is gone"))
        assert supervisor._head_commit_epoch() is None
    finally:
        _sp.run = orig


# ──────────── 'red_blocked': still drawable, but NOT the daemon diagnosis ─────────────────
# 2026-08-20, WORKER_FINDING_A_SALVAGE_PARKED_THE_PRODUCER_HALF_AND_LEFT_THE_CONSUMER_HALF_IN_
# THE_TREE. Two unimportable files under tests/company/ interrupted COLLECTION, so the marker
# expression never selected anything and no operational test ran -- and this rung's message
# sent the drawn worker to regenerate the process-set manifest, 23 pages running. The signal
# now records that case as `red_blocked`. Two things must hold, and they pull opposite ways:
# it must STILL draw (an unmonitored layer is exactly this rung's purpose, and silence would
# reintroduce the overnight fail-silent), and it must NOT repeat the daemon instruction.

_BLOCKED_FILES = ["tests/company/interfaces/test_the_run_holds_no_policy.py",
                  "tests/company/policy/test_policy_field_consumption.py"]


def _blocked_state(**kw):
    state = {"consecutive_green": 0, "consecutive_red": 23, "last_result": "red_blocked",
             "last_run_ts": 1787189988.3, "blocked_by": list(_BLOCKED_FILES)}
    state.update(kw)
    return state


def test_a_blocked_signal_still_draws(tmp_path, monkeypatch):
    """FAIL-SAFE DIRECTION: the layer is unmonitored, so this rung must fire. A guard that
    classified the red and then went quiet would be strictly worse than the defect."""
    _write_signal(tmp_path, monkeypatch, _blocked_state())
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: 1787189988.3 - 60, head_hash_fn=lambda: "deadbee")
    assert msg is not None
    assert "PRIORITY ZERO" in msg
    assert "23 consecutive" in msg


def test_a_blocked_draw_does_not_send_the_worker_to_the_daemons(tmp_path, monkeypatch):
    """THE DEFECT THIS BRANCH EXISTS FOR -- the draw's own words."""
    _write_signal(tmp_path, monkeypatch, _blocked_state())
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: 1787189988.3 - 60, head_hash_fn=lambda: "deadbee")
    assert "BLOCKED" in msg
    assert "NOT a daemon-lifecycle defect" in msg
    assert "process-set manifest" not in msg.split("do NOT")[0]
    # It names the files to repair rather than a subsystem to search.
    for path in _BLOCKED_FILES:
        assert path in msg


def test_a_blocked_draw_with_no_named_files_says_so_rather_than_going_blank(tmp_path, monkeypatch):
    """FAIL-LOUD: an older/partial record carrying no `blocked_by` must not render an empty
    list that reads as 'no files affected'."""
    _write_signal(tmp_path, monkeypatch, _blocked_state(blocked_by=[]))
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: 1787189988.3 - 60, head_hash_fn=lambda: "deadbee")
    assert msg is not None
    assert "names none" in msg and "re-run the signal" in msg


def test_a_genuine_red_still_gets_the_daemon_draw(tmp_path, monkeypatch):
    """THE NULL CONTROL. If the blocked branch swallowed the ordinary red too, this rung would
    stop naming daemon regressions at all -- the mutation in the opposite direction."""
    _write_signal(tmp_path, monkeypatch,
                  {"consecutive_green": 0, "consecutive_red": 13, "last_result": "red",
                   "last_run_ts": 1784957831.287541})
    msg = supervisor._operational_red_persistent_draw(
        head_time_fn=lambda: 1784957831.287541 - 60, head_hash_fn=lambda: "deadbee")
    assert "PERSISTENT-RED" in msg
    assert "daemon-lifecycle" in msg
    assert "BLOCKED self-refill" not in msg


def test_still_silent_on_a_below_threshold_blocked_record(tmp_path, monkeypatch):
    """The classification changes the MESSAGE, never the drawable bar."""
    _write_signal(tmp_path, monkeypatch,
                  _blocked_state(consecutive_red=supervisor.OPERATIONAL_RED_DRAWABLE_THRESHOLD))
    assert supervisor._operational_red_persistent_draw() is None
