"""OPS1 sub-step 4: the drift control made LIVE — periodic reconcile, transition-only paging.

The load-bearing property is that this is the LIVE consumer the reconcile lacked (its absence let a
live worker-seat declared `held` produce no HELD_VIOLATED, 2026-07-17). R5: it pages only on a drift
TRANSITION, never a heartbeat; a clean run logs and stays silent."""
from __future__ import annotations

import pytest

from background import reconcile_watch as W


def _clean():
    proc = [{"session": "sim-runner", "status": "OK", "alarm": False},
            {"session": "supervisor", "status": "HELD", "alarm": False}]
    sched = [{"kind": "unit", "item": "file-api.service", "status": "OK", "alarm": False}]
    return proc, sched


def _drift():
    proc = [{"session": "supervisor", "status": "HELD_VIOLATED", "alarm": True},
            {"session": "sim-runner", "status": "OK", "alarm": False}]
    sched = [{"kind": "cron", "item": "0 * * * * evil", "status": "UNDECLARED_CRON", "alarm": True}]
    return proc, sched


def test_signature_is_order_independent_and_empty_when_clean():
    proc, sched = _clean()
    assert W.drift_signature(proc, sched) == []
    proc2, sched2 = _drift()
    sig = W.drift_signature(proc2, sched2)
    assert "P:supervisor:HELD_VIOLATED" in sig
    assert "S:0 * * * * evil:UNDECLARED_CRON" in sig


def test_clean_report_says_clean_and_lists_nothing():
    proc, sched = _clean()
    sig, summary = W.build_report(proc, sched)
    assert sig == [] and "clean" in summary


def test_drift_report_lists_each_alarm():
    proc, sched = _drift()
    sig, summary = W.build_report(proc, sched)
    assert "supervisor: HELD_VIOLATED" in summary
    assert "UNDECLARED_CRON" in summary


@pytest.fixture
def _wired(monkeypatch, tmp_path):
    pages = []
    monkeypatch.setattr(W, "STATE_FILE", tmp_path / ".reconcile_watch_state.json")
    monkeypatch.setattr(W, "LOG_FILE", tmp_path / "reconcile-watch-log.md")
    return pages


def test_clean_run_does_not_page(_wired):
    proc, sched = _clean()
    paged = W.run(proc, sched, notify=lambda *a, **k: _wired.append((a, k)))
    assert paged is False and _wired == []


def test_drift_appears_pages_once_then_stays_silent_until_change(_wired):
    proc, sched = _drift()
    notify = lambda *a, **k: _wired.append((a, k))
    assert W.run(proc, sched, notify=notify) is True          # transition clean->drift: page
    assert len(_wired) == 1
    assert W.run(proc, sched, notify=notify) is False         # same drift: no repeat (R5)
    assert len(_wired) == 1


def test_drift_clearing_pages_a_recovery(_wired):
    notify = lambda *a, **k: _wired.append((a, k))
    dp, ds = _drift()
    W.run(dp, ds, notify=notify)                              # drift -> page (rotating_light)
    cp, cs = _clean()
    assert W.run(cp, cs, notify=notify) is True               # cleared -> page (recovery)
    assert _wired[-1][1]["headers"]["X-Tags"] == "white_check_mark"


def test_drift_present_is_typed_high_priority(_wired):
    dp, ds = _drift()
    W.run(dp, ds, notify=lambda *a, **k: _wired.append((a, k)))
    assert _wired[0][1]["headers"]["X-Tags"] == "rotating_light"
    assert _wired[0][1]["headers"]["X-Priority"] == "high"
