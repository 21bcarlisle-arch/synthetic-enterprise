"""R15 proofs for the scheduled-bounded-invocation tick (background/worker_tick.py,
SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md, 2026-07-20).

The three director-required properties, proven by mutation:
  P1 (cheap at rest): a drained-and-gated draw -> NO spawn (no model inference at rest). Mutation:
     make the draw return work -> it WOULD spawn -> proves the gate is the draw, not a constant.
  P2 (wakes on a staged doc): a non-empty draw -> spawn; and the two systemd triggers are
     INDEPENDENT (timer alone wakes; path alone wakes) so losing one is not a silent dead chain.
  (P3 lives in tests/hooks/test_scheduled_mode.py -- it is the Stop hook's job.)

Plus the safety invariants: fail-closed kill switch, dark-until-cutover, no-stacking (live-pid
lock), draw-error is loud-not-spawn.
"""
import importlib
import json
from pathlib import Path

import pytest

import background.worker_tick as wt

REPO = Path(__file__).resolve().parents[2]

# Captured at import, BEFORE the autouse _isolate fixture repoints it at tmp -- so the structural
# ship-path guard can assert the module's REAL default.
_REAL_HEARTBEAT_FILE = wt.HEARTBEAT_FILE


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Redirect every live file the tick writes into tmp so a test never touches real observability
    signals (the .pull_loop_health leak lesson)."""
    monkeypatch.setattr(wt, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(wt, "SCHEDULED_FLAG", tmp_path / ".scheduled_invocations_enabled")
    monkeypatch.setattr(wt, "LOCK_FILE", tmp_path / ".worker_tick.lock")
    monkeypatch.setattr(wt, "LOG_FILE", tmp_path / "worker-tick-log.md")
    monkeypatch.setattr(wt, "HEALTH_FILE", tmp_path / ".worker_tick_health.json")
    monkeypatch.setattr(wt, "HEARTBEAT_FILE", tmp_path / "tick_heartbeat.json")
    return tmp_path


# ---- P1: cheap at rest (the load-bearing property) ---------------------------------------------

def test_p1_drained_draw_does_not_spawn():
    d = wt.decide_tick(enabled=True, scheduled=True, in_flight=False, draw=(None, False))
    assert d.spawn is False and d.outcome == "REST_NO_WORK"


def test_p1_mutation_work_would_spawn():
    """The gate is the DRAW, not a constant: flip the draw to work and it spawns (so P1 is a real
    property of 'no work', not the tick simply never spawning)."""
    d = wt.decide_tick(True, True, False, ("unprocessed staging -- FOO.md", False))
    assert d.spawn is True and d.outcome == "SPAWNED"


def test_p1_run_tick_at_rest_spawns_no_process(_isolate, monkeypatch):
    """End-to-end mutation: enabled + scheduled + a drained draw -> run_tick spawns NOTHING."""
    (_isolate / ".build_executor_enabled").write_text("")
    (_isolate / ".scheduled_invocations_enabled").write_text("")
    monkeypatch.setattr(wt, "_draw", lambda: (None, False))
    calls = []
    monkeypatch.setattr(wt, "spawn_invocation", lambda reason: calls.append(reason))
    d = wt.run_tick()
    assert d.outcome == "REST_NO_WORK"
    assert calls == []  # zero spawns => zero inference at rest
    health = json.loads((_isolate / ".worker_tick_health.json").read_text())
    assert health["outcome"] == "REST_NO_WORK"


# ---- P2: wakes on work / trigger independence ---------------------------------------------------

def test_p2_work_draw_spawns(_isolate, monkeypatch):
    (_isolate / ".build_executor_enabled").write_text("")
    (_isolate / ".scheduled_invocations_enabled").write_text("")
    monkeypatch.setattr(wt, "_draw", lambda: ("unprocessed staging -- BAR.md", False))
    seen = {}

    class _FakeProc:
        pid = 4321
        def wait(self):
            return 0
    monkeypatch.setattr(wt, "spawn_invocation", lambda reason: (seen.setdefault("reason", reason), _FakeProc())[1])
    d = wt.run_tick()
    assert d.spawn is True and d.outcome == "SPAWNED"
    assert "BAR.md" in seen["reason"]
    # lock cleared after the (fake) invocation exits
    assert not (_isolate / ".worker_tick.lock").exists()


def test_p2_timer_and_path_are_independent_triggers():
    """R15: worker-tick.timer and worker-tick.path BOTH fire worker-tick.service, independently.
    Killing either still leaves a working wake (no single point of failure / silent dead chain)."""
    timer = (REPO / "background" / "worker-tick.timer").read_text()
    path = (REPO / "background" / "worker-tick.path").read_text()
    svc = (REPO / "background" / "worker-tick.service").read_text()
    assert "[Timer]" in timer and "OnUnitActiveSec=60s" in timer          # timer wakes every 60s
    assert "[Path]" in path and "PathModified=" in path                    # path wakes on a staged doc
    assert "Unit=worker-tick.service" in path                              # path -> the same service
    assert "Type=oneshot" in svc and "background.worker_tick" in svc       # the service runs the tick


# ---- kill switch, dark-until-cutover, stacking, draw-error -------------------------------------

def test_kill_switch_disabled_no_spawn():
    assert wt.decide_tick(False, True, False, ("x", False)).outcome == "DISABLED"


def test_dark_until_cutover_no_spawn():
    assert wt.decide_tick(True, False, False, ("x", False)).outcome == "NOT_SCHEDULED"


def test_autonomy_enabled_fail_closed(_isolate):
    assert wt.autonomy_enabled() is False                      # missing flag
    (_isolate / ".build_executor_enabled").mkdir()             # a directory, not a file
    assert wt.autonomy_enabled() is False
    import shutil
    shutil.rmtree(_isolate / ".build_executor_enabled")
    (_isolate / ".build_executor_enabled").write_text("")
    assert wt.autonomy_enabled() is True


def test_scheduled_mode_flag(_isolate):
    assert wt.scheduled_mode() is False
    (_isolate / ".scheduled_invocations_enabled").write_text("")
    assert wt.scheduled_mode() is True


def test_no_stacking_live_pid_in_flight(_isolate):
    import os
    (_isolate / ".worker_tick.lock").write_text(json.dumps({"pid": os.getpid(), "ts": 0}))
    assert wt.invocation_in_flight() is True                    # our own pid is alive


def test_stale_lock_dead_pid_reclaimed(_isolate):
    # pid 2^31-ish is (almost certainly) not a live process -> lock is stale -> reclaimable.
    (_isolate / ".worker_tick.lock").write_text(json.dumps({"pid": 2_000_000_111, "ts": 0}))
    assert wt.invocation_in_flight() is False


def test_malformed_lock_not_in_flight(_isolate):
    (_isolate / ".worker_tick.lock").write_text("{not json")
    assert wt.invocation_in_flight() is False


def test_draw_error_is_loud_not_spawn():
    d = wt.decide_tick(True, True, False, RuntimeError("supervisor import blew up"))
    assert d.spawn is False and d.outcome == "DRAW_ERROR"


# ---- RAIL-3 HEARTBEAT: origin-verifiable liveness (DIRECTOR_RULING_HEARTBEAT... 2026-07-24) -------

def test_heartbeat_ships_under_site_data():
    """The load-bearing ABSORPTION property: the heartbeat lands on the auto-published surface
    (site/data/*.json is committed WHOLE by process_run_complete.py), NOT in the .gitignored
    worker-tick-log.md that never reaches origin. If someone moves it off site/data, the
    fetch-from-origin acceptance test silently breaks -- so guard it structurally. Uses the REAL
    module constant, not the tmp-isolated one."""
    real = Path(wt.__file__).resolve().parents[1] / "site" / "data" / "tick_heartbeat.json"
    assert _REAL_HEARTBEAT_FILE == real, _REAL_HEARTBEAT_FILE
    assert _REAL_HEARTBEAT_FILE.parent.name == "data" and _REAL_HEARTBEAT_FILE.parent.parent.name == "site"


def test_heartbeat_written_at_rest_carries_enumeration(_isolate, monkeypatch):
    """A rested tick ships a heartbeat classed 'rested' with the whole-set enumeration attached."""
    (_isolate / ".build_executor_enabled").write_text("")
    (_isolate / ".scheduled_invocations_enabled").write_text("")
    monkeypatch.setattr(wt, "_draw", lambda: (None, False))
    monkeypatch.setattr(wt, "spawn_invocation", lambda reason: None)
    monkeypatch.setattr(wt, "_enumeration_line", lambda: "AUTHORIZED-SET enumeration [build=. site=.] -> REST-LEGITIMATE")
    wt.run_tick()
    hb = json.loads((_isolate / "tick_heartbeat.json").read_text())
    assert hb["verdict"] == "rested" and hb["outcome"] == "REST_NO_WORK"
    assert "AUTHORIZED-SET enumeration" in hb["enumeration"]
    assert hb["line"].startswith("[") and "rested" in hb["line"]
    assert hb["recent"] and hb["recent"][0] == hb["line"]


def test_heartbeat_verdict_tracks_outcome_not_constant(_isolate, monkeypatch):
    """MUTATION: the verdict is DERIVED from the tick outcome, not a constant. A drew tick reads
    'drew'; a rested tick reads 'rested' -- so the heartbeat can distinguish work from rest (a
    constant 'drew' would hide a stall behind a false-live signal)."""
    # drew
    drew = wt.TickDecision(True, "SPAWNED", reason="x", detail="drew-detail")
    wt._write_heartbeat(drew, "enum-A")
    hb = json.loads((_isolate / "tick_heartbeat.json").read_text())
    assert hb["verdict"] == "drew"
    # rested (same file, appends to recent, verdict flips)
    rested = wt.TickDecision(False, "REST_NO_WORK", detail="rested-detail")
    wt._write_heartbeat(rested, "enum-B")
    hb = json.loads((_isolate / "tick_heartbeat.json").read_text())
    assert hb["verdict"] == "rested"
    assert len(hb["recent"]) == 2 and "drew" in hb["recent"][1]  # prior verdict preserved in the window
    # exception classifies distinctly too
    exc = wt.TickDecision(False, "DRAW_ERROR", detail="boom")
    wt._write_heartbeat(exc, "enum-C")
    assert json.loads((_isolate / "tick_heartbeat.json").read_text())["verdict"] == "exception"


def test_heartbeat_recent_window_bounded(_isolate):
    for i in range(wt.HEARTBEAT_RECENT_MAX + 5):
        wt._write_heartbeat(wt.TickDecision(False, "REST_NO_WORK", detail=f"t{i}"), f"enum{i}")
    hb = json.loads((_isolate / "tick_heartbeat.json").read_text())
    assert len(hb["recent"]) == wt.HEARTBEAT_RECENT_MAX     # rolls, never grows unbounded
