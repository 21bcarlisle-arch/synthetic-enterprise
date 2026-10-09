"""AN ID CLAIMED BETWEEN COMPOSE AND SPAWN IS NOT HANDED TO A SECOND WRITER.

Measured 2026-10-01: `seat_executor` picked
`retake-the-renewal-feedback-attribution-without-the-look-ahead` at 19:12 UTC, claimed it at
19:14:49 after building its worktree, and the worker tick dispatched the same id at 19:15:34 and
logged "claim taken" over the executor's row. Two Opus turns on one measurement.

`next_item` walks past ids held in either store, so a held id at dispatch was claimed in the gap
after the compose. Both dispatchers now re-ask `delivery_lane.held_at_dispatch` at the last moment
before their own claim: `worker_tick.run_tick` before `_claim_dispatched`, and
`seat_executor.run_once` after `ensure_worktree` (the minutes-wide gap) and before its claim.

The change was written across all three files on 2026-10-01 and sat unlanded for eight days; when
the reconciler cleared the `delivery_lane` third, both callers raised AttributeError on every turn
for five hours. These controls are what makes the three files one landing.
"""
from __future__ import annotations

import json
import subprocess
import time

import pytest

from background import delivery_lane, seat_executor
from background import seat_work_in_hand as claims_mod
from background import worker_tick as wt

from .test_worker_tick import _FakeProc, _isolate  # noqa: F401 - fixture used by name

ITEM = "retake-the-renewal-feedback-attribution-without-the-look-ahead"
DOORBELL = f"ALSO -- LANE 0 DELIVERY -- ... `python3 -m background.delivery_lane --landed {ITEM}`"


@pytest.fixture
def stores(tmp_path, monkeypatch):
    """Both claim stores off the live records, each on its production deadline."""
    lane = tmp_path / "lane_claims.json"
    hand = tmp_path / "work_in_hand.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", lane)
    monkeypatch.setattr(delivery_lane, "DRAW_LEDGER_FILE", lane.with_suffix(".draws.json"))
    monkeypatch.setattr(claims_mod, "CLAIMS_FILE", hand)
    return lane, hand


def _rival(store, *, now=None):
    claims_mod.claim(ITEM, note="another writer", paths=[], path=store, now=now)


def test_held_at_dispatch_over_its_whole_partition(stores):
    """ONE CONTROL OVER THE PARTITION: a guard answering None for everything passes every
    "does not refuse wrongly" leg, and one answering a holder for everything passes every
    "refuses" leg. Both outcomes must be reached by the same function on the same doorbell.

    MUTATIONS (each must fire): `return None` at the top; drop the `not in stale` filter; read
    only the first store.
    """
    lane, hand = stores
    assert delivery_lane.held_at_dispatch(DOORBELL) is None, "nothing holds it: dispatch"
    assert delivery_lane.held_at_dispatch("unprocessed staging -- FOO.md") is None, (
        "a map doorbell names no Lane 0 id and is never held")

    _rival(hand)  # the executor / interactive seat's store, not this lane's
    held = delivery_lane.held_at_dispatch(DOORBELL)
    assert held == f"{ITEM} in {hand.name}", held

    stale_at = time.time() + claims_mod.STALE_AFTER_SECONDS + 3600
    assert delivery_lane.held_at_dispatch(DOORBELL, now=stale_at) is None, (
        "a swept-in-waiting row must not hold an item forever")


def _arm_tick(monkeypatch):
    monkeypatch.setattr(wt, "autonomy_enabled", lambda: True)
    monkeypatch.setattr(wt, "scheduled_mode", lambda: True)
    monkeypatch.setattr(wt, "_mode_gate", lambda: None)
    monkeypatch.setattr(wt, "_draw", lambda: (DOORBELL, False))
    spawned: list[str] = []
    monkeypatch.setattr(wt, "spawn_invocation",
                        lambda reason: spawned.append(reason) or _FakeProc())
    return spawned


def test_run_tick_spawns_a_free_item_and_not_a_held_one(_isolate, stores, monkeypatch):  # noqa: F811
    """Both branches through the real `run_tick`. The free arm is the control: without it, a tick
    that never spawns a Lane 0 doorbell would pass the held arm.

    MUTATION (must fire): delete the `holder is not None` branch -> the held arm spawns.
    """
    lane, hand = stores
    spawned = _arm_tick(monkeypatch)

    d = wt.run_tick()
    assert d.outcome == "SPAWNED" and spawned == [DOORBELL]
    assert ITEM in json.loads(lane.read_text()), "the free arm claimed at dispatch"

    claims_mod.release(ITEM, path=lane)
    _rival(hand)
    spawned.clear()
    d = wt.run_tick()
    assert spawned == [], "a held item was dispatched to a second writer"
    assert (d.spawn, d.outcome) == (False, "HELD_AT_DISPATCH"), d
    assert ITEM not in json.loads(lane.read_text()), "the tick must not claim over the holder"
    health = json.loads((_isolate / ".worker_tick_health.json").read_text())
    assert health["outcome"] == "HELD_AT_DISPATCH"


@pytest.fixture
def turn(tmp_path, stores, monkeypatch):
    """A `run_once` that reaches its claim without the shared tree or the network, with a hook
    that runs INSIDE `ensure_worktree` -- the gap the re-ask exists for."""
    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)
    monkeypatch.setattr(seat_executor, "_is_handed_off", lambda item, now=None: True)
    monkeypatch.setattr(seat_executor, "_resolve_claude", lambda: "claude")
    monkeypatch.setattr(seat_executor, "guard_live_ledger_write", lambda path, writer="": path)
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item",
                        lambda **k: {"id": ITEM, "what": "w", "why": "y"})
    monkeypatch.setattr(seat_executor, "seat_continuation_drop", lambda wid: True)
    (tmp_path / "wt").mkdir()
    during_build: list = []

    def _build(base):
        for act in during_build:
            act()
        return tmp_path / "wt"

    monkeypatch.setattr(seat_executor, "ensure_worktree", _build)
    sessions: list = []

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="basesha0000\n", stderr="")
        sessions.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(seat_executor.subprocess, "run", fake_run)
    return during_build, sessions


def test_the_executor_stands_down_when_its_item_is_claimed_while_it_builds(turn, stores):
    """Both branches again, through the real `run_once`. The free arm reaches the session; the
    held arm, whose rival claims during `ensure_worktree`, stands down before claiming over it.

    MUTATION (must fire): delete the re-ask -> the held arm runs a session and overwrites the
    rival's row.
    """
    during_build, sessions = turn
    lane, hand = stores

    seat_executor.run_once()
    assert sessions, "the free arm must reach the session"
    for store in (lane, hand):
        if store.exists():
            claims_mod.release(ITEM, path=store)

    sessions.clear()
    rival_at = time.time() - 5
    during_build.append(lambda: _rival(lane, now=rival_at))
    ran, detail = seat_executor.run_once()
    assert (ran, sessions) == (False, []), detail
    assert "claimed by another writer" in detail
    row = json.loads(lane.read_text())[ITEM]
    assert row["note"] == "another writer", "the executor overwrote the holder's row"
