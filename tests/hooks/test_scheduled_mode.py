"""R15 proofs for SCHEDULED-INVOCATION MODE in the Stop hook + reconciler
(.claude/hooks/pull_next_work.py, background/process_reconciler.py;
SCHEDULED_BOUNDED_INVOCATIONS_DESIGN.md, 2026-07-20).

P3 (never blocks director input): once the cutover flag exists, decide() allow-stops EVERY session
-- the worker invocation AND the console -- with NO draw, NO block+continue, NO rest-heartbeat. That
is what removes the resident chain that could occupy the session and block input; there is nothing
in-hook that sleeps or holds. Proven by: (a) both payloads -> None; (b) MUTATION -- make find_work
raise, and decide() still allow-stops (proving the draw/heartbeat path is not reached in scheduled
mode); (c) the fallback (flag absent) is unchanged (find_work IS reached).

Plus: the reconciler treats the scheduled-mode health record as a freshness-EXEMPT healthy rest, so
a frozen record at rest never false-pages LOOP_STALE.
"""
import importlib.util
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pull_next_work.py"
WORKER_ID = "22080be5-e19e-4099-a007-d71c3a6e7845"
CONSOLE_ID = "004ea979-3496-42f2-8a23-c406b531ea9d"


def _load(tmp_path, monkeypatch, *, scheduled, draw_result, enabled=True):
    spec = importlib.util.spec_from_file_location("pnw_sched", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(mod, "SCHEDULED_FLAG", tmp_path / ".scheduled_invocations_enabled")
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "pull-loop-log.md")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / ".pull_loop_state.json")
    monkeypatch.setattr(mod, "HEALTH_FILE", tmp_path / ".pull_loop_health.json")
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", WORKER_ID)
    if enabled:
        (tmp_path / ".build_executor_enabled").write_text("")
    if scheduled:
        (tmp_path / ".scheduled_invocations_enabled").write_text("")
    import sys, types
    fake = types.ModuleType("background.supervisor")
    if isinstance(draw_result, Exception):
        def _raise(resumed_from_pause=False):
            raise draw_result
        fake.find_work = _raise
    else:
        fake.find_work = lambda resumed_from_pause=False: draw_result
    fake._real_staged_instructions = lambda: []
    fake._sync_origin_staging = lambda: None
    monkeypatch.setitem(sys.modules, "background.supervisor", fake)
    return mod


def _wp(session_id=WORKER_ID):
    return {"stop_hook_active": False, "session_id": session_id}


def test_p3_scheduled_mode_worker_allows_stop(tmp_path, monkeypatch):
    mod = _load(tmp_path, monkeypatch, scheduled=True, draw_result=("A6 has work", False))
    monkeypatch.setenv("SE_SBI_WORKER", "1")
    assert mod.decide(_wp()) is None                       # worker invocation exits cleanly


def test_p3_scheduled_mode_console_allows_stop(tmp_path, monkeypatch):
    mod = _load(tmp_path, monkeypatch, scheduled=True, draw_result=("A6 has work", False))
    monkeypatch.delenv("SE_SBI_WORKER", raising=False)
    assert mod.decide(_wp(CONSOLE_ID)) is None             # console never pulled, never held


def test_p3_scheduled_mode_does_not_reach_draw(tmp_path, monkeypatch):
    """MUTATION: find_work RAISES. In scheduled mode decide() must still allow-stop -- proving the
    draw/heartbeat path is never reached (no in-hook work, nothing that could block input)."""
    mod = _load(tmp_path, monkeypatch, scheduled=True, draw_result=RuntimeError("must not be called"))
    monkeypatch.setenv("SE_SBI_WORKER", "1")
    assert mod.decide(_wp()) is None                       # did NOT propagate the error => draw not reached


def test_p3_scheduled_mode_writes_exempt_health(tmp_path, monkeypatch):
    import json
    mod = _load(tmp_path, monkeypatch, scheduled=True, draw_result=(None, False))
    mod.decide(_wp())
    health = json.loads((tmp_path / ".pull_loop_health.json").read_text())
    assert health["outcome"] == "ALLOW_STOP_SCHEDULED"


def test_fallback_preserved_flag_absent_reaches_draw(tmp_path, monkeypatch):
    """With the flag ABSENT the persistent-seat path is unchanged: the worker draw IS reached
    (a real drawn turn blocks+continues), so the migration cannot silently disable the fallback."""
    mod = _load(tmp_path, monkeypatch, scheduled=False, draw_result=("A6 has work", False))
    out = mod.decide(_wp())
    assert out is not None and out["decision"] == "block" and "A6 has work" in out["reason"]


# ---- reconciler: the scheduled health record must be a freshness-EXEMPT healthy rest -----------

def test_reconciler_scheduled_outcome_never_alarms_even_when_stale():
    from background.process_reconciler import pull_loop_status
    # A record frozen 3 hours ago while ENABLED -- for any normal healthy outcome this is LOOP_STALE
    # (alarm). ALLOW_STOP_SCHEDULED must be exempt (no session fires the hook at rest, by design).
    st = pull_loop_status({"outcome": "ALLOW_STOP_SCHEDULED", "ts": 0.0}, enable_on=True,
                          now=3 * 3600.0, stale_after=3600.0)
    assert st["alarm"] is False and st["status"] == "HEALTHY_IDLE"


def test_reconciler_normal_healthy_outcome_still_alarms_when_stale():
    """Guard the mutation both ways: a NORMAL healthy outcome frozen that long DOES alarm, so the
    exemption above is specific to scheduled mode, not a blanket freshness disable."""
    from background.process_reconciler import pull_loop_status
    st = pull_loop_status({"outcome": "DREW", "ts": 0.0}, enable_on=True,
                          now=3 * 3600.0, stale_after=3600.0)
    assert st["alarm"] is True and st["status"] == "LOOP_STALE"
