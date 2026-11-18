"""The wedge refill stays quiet behind a declared wait, and only there (director, 18 Nov: "Yes.").

Defect each test names: the priority-zero refill re-asked a refused book 59 times on 17-18 Nov
while `flag1-stop-at-pair3-watch` waited on its one named file, one commit cycle per re-ask.

The partition is asserted as ONE control (`test_the_whole_partition`): quiet while armed, fires
when the watcher is gone, fires 1 h after the file with no book, fires past 72 h. If any leg is
mutated to always-quiet or always-fire, that test reds. The director's named control -- the refill
can still fire while a watcher is ARMED -- is `test_an_armed_watcher_cannot_hold_it_quiet_forever`.
"""
from __future__ import annotations

import json
import os

import pytest

from background import declared_wait, supervisor

HOUR = 3600
NOW = 1_795_000_000.0
FILE = "awaited_control.json"
UNIT = "flag1-stop-at-pair3-watch.service"


@pytest.fixture(autouse=True)
def _no_live_gate(monkeypatch):
    monkeypatch.setattr(supervisor, "_live_publish_gate_runs", lambda *a, **k: [])


def _setup(tmp_path, monkeypatch, *, episode_age=49 * HOUR, kind="domain_invariant_refused",
           file_age=None, declared=True):
    failures = [{"ts": NOW - i * 600, "reason": "Domain-invariant gate REFUSED", "rc": 82,
                 "kind": kind, "git_hash": "18f201c5bf"} for i in range(4)][::-1]
    state = {"failures": failures, "wedge_since": NOW - episode_age, "episode_failures": 55,
             "episode_clean_publishes": 0, "alerted_at": None}
    sp = tmp_path / ".publish_gate_state.json"
    sp.write_text(json.dumps(state))
    (tmp_path / ".last_tested_hash").write_text("OLDHASH")
    monkeypatch.setattr(supervisor, "PUBLISH_GATE_STATE_FILE", sp)
    monkeypatch.setattr(supervisor, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(supervisor, "_current_head_hash", lambda: "HEADHASH")
    awaited = tmp_path / FILE
    if file_age is not None:
        awaited.write_text("{}")
        os.utime(awaited, (NOW - file_age, NOW - file_age))
    waits = tmp_path / ".declared_waits.json"
    waits.write_text(json.dumps([{"unit": UNIT, "awaits": str(awaited), "why": "pair 3"}]
                                if declared else []))
    return waits


def _draw(tmp_path, monkeypatch, *, armed=True, **kw):
    waits = _setup(tmp_path, monkeypatch, **kw)
    return supervisor._publish_gate_wedge_draw(now=NOW, waits_path=waits,
                                               unit_active=lambda u: armed)


def test_the_whole_partition(tmp_path, monkeypatch):
    plan = {
        "quiet_while_armed": _draw(tmp_path, monkeypatch, armed=True),
        "watcher_gone": _draw(tmp_path, monkeypatch, armed=False),
        "file_then_no_book_1h": _draw(tmp_path, monkeypatch, armed=False, file_age=HOUR + 60),
        "file_inside_the_hour": _draw(tmp_path, monkeypatch, armed=False, file_age=20 * 60),
        "past_72h": _draw(tmp_path, monkeypatch, armed=True, episode_age=72 * HOUR + 60),
        "undeclared": _draw(tmp_path, monkeypatch, armed=True, declared=False),
    }
    assert plan["quiet_while_armed"] is None
    assert plan["file_inside_the_hour"] is None
    assert plan["watcher_gone"] and "is gone" in plan["watcher_gone"]
    assert plan["file_then_no_book_1h"] and "no book followed" in plan["file_then_no_book_1h"]
    assert plan["past_72h"] and "72 h cap" in plan["past_72h"]
    assert plan["undeclared"] and "PRIORITY ZERO" in plan["undeclared"]


def test_an_armed_watcher_cannot_hold_it_quiet_forever(tmp_path, monkeypatch):
    """The director's named control: the refill still fires while a watcher is armed."""
    assert _draw(tmp_path, monkeypatch, armed=True, episode_age=73 * HOUR)
    assert _draw(tmp_path, monkeypatch, armed=True, file_age=2 * HOUR)
    # ...and a wedge of another cause is never quieted by any watcher.
    other = _draw(tmp_path, monkeypatch, armed=True, kind="test_regression")
    assert other and "`test_regression`" in other


def test_a_declaration_refuses_a_dead_watcher_and_a_relative_path(tmp_path):
    p = tmp_path / "w.json"
    with pytest.raises(ValueError, match="not active"):
        declared_wait.declare(UNIT, "/abs/x.json", "why", path=p, unit_active=lambda u: False)
    with pytest.raises(ValueError, match="absolute"):
        declared_wait.declare(UNIT, "x.json", "why", path=p, unit_active=lambda u: True)
    declared_wait.declare(UNIT, "/abs/x.json", "pair 3", path=p, now=NOW, unit_active=lambda u: True)
    assert declared_wait.read_waits(p)[0]["awaits"] == "/abs/x.json"


def test_the_ladder_takes_rung_one_through_the_quiet_check():
    """A ladder that called the bare detector again would re-ask behind every armed wait."""
    import inspect
    src = inspect.getsource(supervisor._self_refill_draw_ladder)
    assert "_publish_gate_wedge_draw()" in src and "_publish_gate_wedge_active()" not in src
