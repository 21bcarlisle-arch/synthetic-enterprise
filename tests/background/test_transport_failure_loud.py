"""OPS1_transport_failure_must_be_loud (§9): a broken pull-loop transport must be LOUD, and
must read DIFFERENTLY from a healthy idle worker.

R15 mutation coverage: the day-long bug was a transport that failed-SILENT (broken ==
indistinguishable from idle). These tests inject a broken draw and assert the alarm FIRES, and
assert that healthy quiescence stays SILENT — a transport-health control that never fires (or
that fires on a healthy idle worker) is the very disease this atom cures.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from background import process_reconciler as R

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pull_next_work.py"


def _load_hook():
    spec = importlib.util.spec_from_file_location("pull_next_work_undertest", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── the pure predicate (mutation-testable core) ───────────────────────────────────────────
def test_draw_error_alarms_LOUD():
    r = R.pull_loop_status({"outcome": "DRAW_ERROR", "detail": "boom"}, enable_on=True)
    assert r["status"] == "LOOP_BROKEN"
    assert r["alarm"] is True                      # THE mutation: a broken draw MUST fire


def test_healthy_idle_is_silent_and_reads_differently_from_broken():
    # Real healthy-idle now = kill switch off (ALLOW_STOP_DISABLED). Under Rule-0 an EMPTY draw is
    # no longer 'healthy idle' -- it is loud (DRAW_EMPTY_UNEXPECTED), see the dedicated test below.
    idle = R.pull_loop_status({"outcome": "ALLOW_STOP_DISABLED"}, enable_on=True)
    broken = R.pull_loop_status({"outcome": "DRAW_ERROR"}, enable_on=True)
    assert idle["alarm"] is False                  # deliberately-paused does NOT alarm
    assert idle["status"] == "HEALTHY_IDLE"
    # the director's exact requirement: the two idle states read differently
    assert idle["status"] != broken["status"]


def test_self_sustain_loud_states_alarm_and_read_distinctly():
    """SELF-SUSTAIN (director P0): a continuous loop that stalls must be LOUD, not silent idle.
    Both new outcomes alarm and read distinctly from a healthy DREW."""
    stuck = R.pull_loop_status({"outcome": "STUCK_NO_PROGRESS", "detail": "30 turns no commit"}, True)
    empty = R.pull_loop_status({"outcome": "DRAW_EMPTY_UNEXPECTED"}, True)
    drew = R.pull_loop_status({"outcome": "DREW"}, True)
    assert stuck["alarm"] is True and stuck["status"] == "LOOP_STUCK"
    assert empty["alarm"] is True and empty["status"] == "LOOP_BROKEN"   # empty=broken under Rule-0
    assert drew["alarm"] is False
    assert stuck["status"] != drew["status"] and empty["status"] != drew["status"]


def test_stale_healthy_record_while_enabled_alarms_LOUD():
    """FRESHNESS fail-silent (2026-07-17 HARDEN): an ENABLED loop whose last fire was healthy (DREW)
    but is now FROZEN (Stop hook stopped firing -- dead/hung worker) must read LOUD, not a healthy
    worker forever. The time-blind classifier missed this exact day-long shape."""
    fresh = R.pull_loop_status({"outcome": "DREW", "ts": 1000}, True, now=1000, stale_after=3600)
    stale = R.pull_loop_status({"outcome": "DREW", "ts": 1000}, True, now=1000 + 4000, stale_after=3600)
    assert fresh["alarm"] is False and fresh["status"] == "HEALTHY_DREW"
    assert stale["alarm"] is True and stale["status"] == "LOOP_STALE"   # frozen-healthy -> LOUD
    assert stale["status"] != fresh["status"]                          # reads distinctly (director req)


def test_stale_record_never_alarms_when_disabled():
    # kill switch off -> deliberately paused; a stale record must stay silent (no spurious page).
    r = R.pull_loop_status({"outcome": "DREW", "ts": 0}, False, now=10 ** 9, stale_after=3600)
    assert r["status"] == "DISABLED" and r["alarm"] is False


def test_freshness_check_skipped_without_a_clock():
    # back-compat + purity: no clock supplied -> time-blind classification unchanged.
    r = R.pull_loop_status({"outcome": "DREW", "ts": 0}, True)   # ancient ts, but now=None
    assert r["status"] == "HEALTHY_DREW" and r["alarm"] is False


def test_stale_record_missing_ts_does_not_false_alarm():
    # a record with no/garbage ts can't be judged stale -> classify by outcome, never a spurious page.
    r = R.pull_loop_status({"outcome": "DREW"}, True, now=10 ** 9, stale_after=3600)
    assert r["status"] == "HEALTHY_DREW" and r["alarm"] is False


def test_evaluate_pull_loop_flags_a_stale_ondisk_record(tmp_path, monkeypatch):
    # the LIVE wrapper wires a real clock: an ancient on-disk record (ts=1) reads LOOP_STALE.
    p = tmp_path / ".pull_loop_health.json"
    p.write_text(json.dumps({"outcome": "DREW", "ts": 1}))
    monkeypatch.setattr(R, "PULL_LOOP_HEALTH_PATH", p)
    monkeypatch.setattr(R, "pull_loop_enabled", lambda *a, **k: True)
    out = R.evaluate_pull_loop()
    assert out["status"] == "LOOP_STALE" and out["alarm"] is True


def test_disabled_never_alarms_even_on_a_stale_error():
    # kill switch off -> autonomy deliberately paused; a stale DRAW_ERROR must not alarm.
    r = R.pull_loop_status({"outcome": "DRAW_ERROR"}, enable_on=False)
    assert r["status"] == "DISABLED" and r["alarm"] is False


def test_drew_and_unknown_are_silent():
    assert R.pull_loop_status({"outcome": "DREW"}, True)["alarm"] is False
    assert R.pull_loop_status(None, True)["status"] == "UNKNOWN"
    assert R.pull_loop_status({}, True)["alarm"] is False


def test_readers_are_fail_safe(tmp_path):
    p = tmp_path / "h.json"
    p.write_text(json.dumps({"outcome": "DREW", "ts": 1}))
    assert R.read_pull_loop_health(p)["outcome"] == "DREW"
    assert R.read_pull_loop_health(tmp_path / "missing.json") is None   # absent -> None, no raise
    assert R.pull_loop_enabled(tmp_path / "nope") is False
    flag = tmp_path / "flag"
    flag.write_text("x")
    assert R.pull_loop_enabled(flag) is True


# ── the hook writes the correct typed outcome on each worker-seat path ─────────────────────
@pytest.fixture
def hook(tmp_path, monkeypatch):
    mod = _load_hook()
    monkeypatch.setattr(mod, "HEALTH_FILE", tmp_path / "health.json")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / "state.json")
    # ISOLATION (2026-07-17): without patching LOG_FILE, decide()'s _log() wrote test-fixture
    # strings ("draw blew up", "do atom X", ...) into the REAL committed docs/observability/
    # pull-loop-log.md on every run -- a test polluting a live observability artefact. Patch it.
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "pull-loop-log.md")
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", "WORKER")
    monkeypatch.setattr(mod, "_autonomous_execution_enabled", lambda: True)
    return mod


def _outcome(mod):
    return json.loads(mod.HEALTH_FILE.read_text())["outcome"]


def test_hook_records_DRAW_ERROR_when_find_work_raises(hook, monkeypatch):
    import background.supervisor as sup

    def boom(*a, **k):
        raise RuntimeError("draw blew up")

    monkeypatch.setattr(sup, "find_work", boom)
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": False})
    assert out is None                              # fail-safe allow-stop preserved
    assert _outcome(hook) == "DRAW_ERROR"           # ...but LOUD, not silent


def test_hook_records_DREW_on_work(hook, monkeypatch):
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: ("do atom X", False))
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": False})
    assert out is not None and out["decision"] == "block"
    assert _outcome(hook) == "DREW"


def test_hook_records_DRAW_EMPTY_UNEXPECTED_when_draw_empty(hook, monkeypatch):
    # Under Rule-0 the queue is never genuinely empty, so an empty draw = a broken draw -> LOUD.
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: ("", True))
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": False})
    assert out is None                               # still fail-safe allow-stop
    assert _outcome(hook) == "DRAW_EMPTY_UNEXPECTED"  # ...but LOUD, not a silent healthy idle
    assert R.pull_loop_status({"outcome": "DRAW_EMPTY_UNEXPECTED"}, True)["alarm"] is True


def test_hook_self_sustains_then_STUCK_alarms_when_no_commits(hook, monkeypatch):
    """SELF-SUSTAIN + loud stall: a continued loop that keeps drawing but never advances the repo
    (no commit) sustains for a while then trips the stuck-cap LOUD -- it does not spin forever, and
    it does not read as a healthy idle worker."""
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: ("draw the same thing", False))
    monkeypatch.setattr(hook, "_repo_progress_token", lambda: "FIXED")   # repo NEVER advances
    monkeypatch.setattr(hook, "MAX_NO_PROGRESS", 3)                      # small cap for the test
    outs = [hook.decide({"session_id": "WORKER", "stop_hook_active": True}) for _ in range(6)]
    assert all(o is not None and o["decision"] == "block" for o in outs[:4])  # sustained (not one-shot)
    assert outs[-1] is None                                              # eventually stops (bounded)
    assert _outcome(hook) == "STUCK_NO_PROGRESS"                         # ...LOUD
    assert R.pull_loop_status({"outcome": "STUCK_NO_PROGRESS"}, True)["alarm"] is True


def test_hook_stuck_cap_resets_on_repo_progress(hook, monkeypatch):
    """A PRODUCTIVE loop never trips the stuck-cap however long it runs: every commit (progress
    token advance) resets no_progress. Proves the cap targets thrashing, not healthy long runs."""
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: ("keep building", False))
    monkeypatch.setattr(hook, "MAX_NO_PROGRESS", 3)
    tokens = iter(["c1", "c1", "c2", "c3", "c4", "c5", "c6", "c7"])  # advances at least every few turns
    monkeypatch.setattr(hook, "_repo_progress_token", lambda: next(tokens))
    outs = [hook.decide({"session_id": "WORKER", "stop_hook_active": True}) for _ in range(8)]
    assert all(o is not None and o["decision"] == "block" for o in outs)  # never trips -- always progressing
    assert _outcome(hook) == "DREW"


def test_hook_records_DISABLED_when_kill_switch_off(hook, monkeypatch):
    monkeypatch.setattr(hook, "_autonomous_execution_enabled", lambda: False)
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": False})
    assert out is None
    assert _outcome(hook) == "ALLOW_STOP_DISABLED"


def test_hook_does_not_write_health_for_a_non_worker_session(hook):
    # the console / any non-worker session must not pollute the worker's transport signal
    out = hook.decide({"session_id": "not-the-worker", "stop_hook_active": False})
    assert out is None
    assert not hook.HEALTH_FILE.exists()


# ── the deadman fires the alarm (the RUNNING home) — transition-only ───────────────────────
def test_deadman_fires_loop_broken_and_is_transition_only(tmp_path, monkeypatch):
    # The deadman now delegates transition-only + re-escalate to notify(); isolate its store and
    # capture the actual send via ntfy_utils.send_ntfy (what notify calls).
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        R, "evaluate_pull_loop",
        lambda: {"status": "LOOP_BROKEN", "alarm": True, "detail": "cannot draw: import failed"},
    )
    D._check_pull_loop_transport()
    assert len(calls) == 1 and "LOOP BROKEN" in calls[0]     # the alarm fires
    D._check_pull_loop_transport()
    assert len(calls) == 1                                    # ...once — transition-only (R5)


def test_deadman_silent_when_transport_healthy(tmp_path, monkeypatch):
    from background import deadmans_switch as D
    import background.notify as N
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    calls = []
    monkeypatch.setattr(N.ntfy_utils, "send_ntfy", lambda msg, **k: calls.append(msg) or "id")
    monkeypatch.setattr(
        R, "evaluate_pull_loop",
        lambda: {"status": "HEALTHY_IDLE", "alarm": False, "detail": "idle"},
    )
    D._check_pull_loop_transport()
    assert calls == []                                        # healthy idle never pages


# ── DRAINED-AND-GATED quiet wait (ADVISOR_STEER 2026-07-18, item 1) ─────────────────────────
# The treadmill noise the mechanism kills: when the map is drained of below-target work and the
# remainder is blocked on a director act, find_work returns (None, map_exhausted=False). The hook
# must ALLOW-STOP quietly (no block+continue treadmill, no token burn), the reconciler must read it
# as a LEGITIMATE resting state (no alarm), and it must read DIFFERENTLY from the loud empty/broken
# case (None/"" , True) so a real broken draw is never masked.
def test_quiet_wait_reads_benign_and_freshness_exempt():
    r = R.pull_loop_status({"outcome": "ALLOW_STOP_QUIET_WAIT"}, enable_on=True)
    assert r["status"] == "HEALTHY_IDLE"
    assert r["alarm"] is False                       # a legitimate rest never pages
    # FRESHNESS-EXEMPT: the loop deliberately stops firing while resting, so a STALE quiet-wait
    # record must NOT flip to LOOP_STALE and page the director overnight (the whole point).
    stale = R.pull_loop_status(
        {"outcome": "ALLOW_STOP_QUIET_WAIT", "ts": 0.0}, enable_on=True,
        now=10 ** 9, stale_after=3600.0,
    )
    assert stale["alarm"] is False and stale["status"] == "HEALTHY_IDLE"


def test_quiet_wait_reads_differently_from_loud_empty_draw():
    quiet = R.pull_loop_status({"outcome": "ALLOW_STOP_QUIET_WAIT"}, True)
    loud = R.pull_loop_status({"outcome": "DRAW_EMPTY_UNEXPECTED"}, True)
    assert quiet["alarm"] is False and loud["alarm"] is True   # rest is silent; a broken draw is LOUD
    assert quiet["status"] != loud["status"]                   # and the two read distinctly


def test_hook_allow_stops_QUIETLY_when_drained_and_gated(hook, monkeypatch):
    # STATE TEST 1 (drained-and-gated -> quiet): find_work returns (None, False). The hook must
    # allow-stop (no block+continue) and record the BENIGN quiet-wait outcome -- NOT the loud
    # DRAW_EMPTY_UNEXPECTED. This is what stops the STUCK/LOOP_BROKEN thrash + token burn.
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: (None, False))
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": True})
    assert out is None                                         # allow-stop, no continuation
    assert _outcome(hook) == "ALLOW_STOP_QUIET_WAIT"           # benign, not loud


def test_hook_R15_quiet_wait_still_loud_on_a_genuinely_broken_draw(hook, monkeypatch):
    # R15 / independence: the quiet path must NOT swallow a real broken/empty draw. Only
    # (None, map_exhausted=False) is quiet; (None, True) stays LOUD. The mutation this catches: a
    # hook that treated ANY empty reason as quiet would silence the day-long fail-silent bug.
    import background.supervisor as sup
    monkeypatch.setattr(sup, "find_work", lambda **k: (None, True))
    out = hook.decide({"session_id": "WORKER", "stop_hook_active": True})
    assert out is None
    assert _outcome(hook) == "DRAW_EMPTY_UNEXPECTED"           # broken draw is NOT silenced


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
