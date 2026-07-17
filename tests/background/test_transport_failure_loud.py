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
def test_deadman_fires_loop_broken_and_is_transition_only(monkeypatch):
    from background import deadmans_switch as D
    calls = []
    monkeypatch.setattr(D, "send_ntfy", lambda msg, *a, **k: calls.append(msg))
    monkeypatch.setattr(
        R, "evaluate_pull_loop",
        lambda: {"status": "LOOP_BROKEN", "alarm": True, "detail": "cannot draw: import failed"},
    )
    D._last_loop_broken_ts = None
    D._check_pull_loop_transport()
    assert len(calls) == 1 and "LOOP BROKEN" in calls[0]     # the alarm fires
    D._check_pull_loop_transport()
    assert len(calls) == 1                                    # ...once — transition-only (R5)


def test_deadman_silent_when_transport_healthy(monkeypatch):
    from background import deadmans_switch as D
    calls = []
    monkeypatch.setattr(D, "send_ntfy", lambda msg, *a, **k: calls.append(msg))
    monkeypatch.setattr(
        R, "evaluate_pull_loop",
        lambda: {"status": "HEALTHY_IDLE", "alarm": False, "detail": "idle"},
    )
    D._last_loop_broken_ts = None
    D._check_pull_loop_transport()
    assert calls == []                                        # healthy idle never pages
