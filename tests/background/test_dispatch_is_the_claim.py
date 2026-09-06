"""EVERY LANE 0 ITEM EVER DELIVERED ARRIVED UNCLAIMED, AND THE DOORBELL TOLD THE WORKER TO BIND IT.

THE DEFECT, filed 2026-09-05 as a BLOCKING finding and left structurally open, then measured again
on 2026-09-06 when it took the identical shape on a different item.

`draw(claim=False)` was the correct 2026-08-31 fix for the opposite defect: the escalation watchdog
polls `find_work()` every ~2 minutes, could not deliver anything, and claimed 68 items on the way
past -- see `test_a_draw_is_not_a_delivery.py`. But that fix separated the two callers **by INTENT,
not by call**:

    worker_tick._draw() -> supervisor.find_work() -> supervisor._delivery_lane_draw()
                                                  -> delivery_lane.draw(claim=False)

`worker_tick` then DISPATCHES the composed text as a real invocation prompt. So the only production
route that hands a Lane 0 item to anybody reaches it through the read that is forbidden to claim,
and every item it delivers arrives unclaimed. Compose is shared with the watchdog; **dispatch is
not**, and dispatch is where the claim has to attach.

WHAT IT COSTS, and the bookkeeping is the smaller half. The worker runs the `--landed <id>` its own
doorbell handed it and reads `bound NOTHING ... it is NOT CLAIMED` -- which is indistinguishable
from the ordinary post-`--release` reading, so nothing tells it apart. The half that bites is that
**a claim is the only thing that hides an item from the next draw.** An unclaimed item stays
drawable WHILE ITS RUNNER IS STILL RUNNING, and both recorded instances had a deliberately-detached
multi-hour runner in flight: a HadUK-Grid pull (2026-09-05) and a mutation battery (2026-09-06).
Every 30-minute tick in that shadow could re-draw the item and act on "resume it" a second time.

WHY NO CONTROL CAUGHT IT, and it is the familiar shape: **a guard whose subject comes from the
register it guards.** `--landed` can only bind what the claims store holds, so an item that never
entered the store is outside its subject by construction. The control has to be keyed to the
DISPATCH, because that is the only place both halves are visible at once.

THE PROPERTY, keyed to the property and not to today's answer: **an id named in a dispatched
doorbell is claimed at dispatch, and is not drawable again until that claim ends.**
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane, seat_continuation
from background import worker_tick as wt

from .test_worker_tick import _FakeProc, _isolate  # noqa: F401 - fixture used by name

FOCUS_ID = "union-the-departure-routes"


@pytest.fixture
def lane(tmp_path, monkeypatch):
    """A delivery lane with its own claim store and exactly one live continuation.

    Both stores are redirected, and `STORE` must be the module attribute rather than a `path=`
    argument for the reason `test_a_draw_is_not_a_delivery.lane` records: `next_item` calls
    `seat_continuation.live()` with no path, so a fixture passing only `path=` would write to tmp
    and READ the live store.
    """
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    monkeypatch.setattr(delivery_lane, "DRAW_LEDGER_FILE", claims.with_suffix(".draws.json"))
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off(
        FOCUS_ID,
        what="Union both departure routes and declare the denominator.",
        why="A mean over a selected sub-population is not a whole-population rate.",
        done_means="the level prints over both routes with the denominator named.",
    )
    return claims


def _claim_ids(store):
    if not store.exists():
        return set()
    return set(json.loads(store.read_text()).keys())


def test_a_lane_0_doorbell_is_claimed_at_dispatch_and_a_map_doorbell_is_not(lane):
    """ONE CONTROL OVER THE WHOLE PARTITION, and it is written this way on purpose.

    A `claim_dispatched` that claims NOTHING passes every "it did not claim the wrong thing" leg,
    and a `claim_dispatched` that claims EVERY hyphenated word passes every "it claimed the right
    thing" leg. Only both legs together can tell the mechanism from either way of not having one.
    """
    doorbell = delivery_lane.draw(path=lane, claim=False)
    assert doorbell and f"--landed {FOCUS_ID}" in doorbell, (
        "the doorbell must carry the bind instruction -- it is the only place the id survives "
        "into the dispatched text, and this control reads it from there"
    )

    assert delivery_lane.claim_dispatched(doorbell, path=lane) == FOCUS_ID
    assert _claim_ids(lane) == {FOCUS_ID}

    # The other side of the partition: the ordinary maturity-map doorbell names no Lane 0 id.
    assert delivery_lane.claim_dispatched(
        "EP5_settlement_true_ups -- Settlement true-ups on the real industry timetable "
        "(lane=E_finance_treasury, dial=3, level 0->3, loop_stage=idle)",
        path=lane,
    ) is None
    assert _claim_ids(lane) == {FOCUS_ID}, "a doorbell naming no Lane 0 id must claim nothing"


def test_the_dispatched_item_is_not_drawable_again(lane):
    """THE CONSEQUENCE THAT BIT, not the bookkeeping.

    The before-leg is not decoration: it asserts the item CAN be drawn, so a fixture whose
    continuation never loaded cannot pass the after-leg vacuously -- an empty lane offers nothing
    for reasons that have nothing to do with claiming.

    KEYED TO THIS ID, NOT TO AN EMPTY LANE, and the first draft was not: `next_item` also reads the
    periodic `focus:` list in the real `docs/direction/DIRECTION.yaml`, which the fixture does not
    redirect, so "the lane is now empty" is a claim about the director's live file. It failed for
    exactly that reason -- the mechanism had worked and the lane had simply moved on to the next
    real candidate. The property was never that the lane goes quiet; it is that THIS item stops
    being offered.
    """
    assert (delivery_lane.next_item(path=lane) or {}).get("id") == FOCUS_ID, (
        "reachability floor: the item must be drawable BEFORE the dispatch"
    )

    doorbell = delivery_lane.draw(path=lane, claim=False)
    delivery_lane.claim_dispatched(doorbell, path=lane)

    assert (delivery_lane.next_item(path=lane) or {}).get("id") != FOCUS_ID, (
        "an item whose runner is still running must not be handed to a second tick"
    )


def test_the_dispatched_claim_makes_the_doorbells_own_bind_instruction_work(lane):
    """The doorbell's `--landed` is the tell. An instruction that cannot succeed is worse than
    none, because the worker runs it and reads a refusal it has no way to tell from `--release`.

    Asserts the REFUSAL first, at the same id and store, so the pass cannot come from
    `refusal_reason` being unreachable or from the id being wrong in both halves.
    """
    assert "NOT CLAIMED" in delivery_lane.refusal_reason(FOCUS_ID, path=lane)

    doorbell = delivery_lane.draw(path=lane, claim=False)
    delivery_lane.claim_dispatched(doorbell, path=lane)

    assert "NOT CLAIMED" not in delivery_lane.refusal_reason(FOCUS_ID, path=lane), (
        "after dispatch the id is claimed, so the bind can no longer refuse for want of a claim"
    )


def test_a_redispatch_does_not_restart_the_deadline(lane):
    """The sweep is a DEADLINE, not a timer the dispatcher may reset.

    If a re-dispatch re-claimed, an item redrawn every 30 minutes would have its 100-minute
    staleness window pushed out forever and could never be swept -- which is the stall-detector
    failing by succeeding, this project's recurring shape.
    """
    doorbell = delivery_lane.draw(path=lane, claim=False)
    delivery_lane.claim_dispatched(doorbell, path=lane)
    first = json.loads(lane.read_text())[FOCUS_ID]["claimed_at"]

    assert delivery_lane.claim_dispatched(doorbell, path=lane, now=first + 3600) == FOCUS_ID
    assert json.loads(lane.read_text())[FOCUS_ID]["claimed_at"] == first, (
        "a re-dispatch of a live claim must leave its instant alone"
    )


def test_run_tick_takes_the_claim_BEFORE_it_spawns(_isolate, lane, monkeypatch):  # noqa: F811
    """THE WIRING, end-to-end through the real `run_tick`, and the ORDER is the contract.

    Claiming after the spawn would leave the window this repairs open at exactly the width that
    matters: the invocation is the thing that runs `--landed`, so a claim it cannot see when it
    starts is a claim that was not there for the only reader that needed it. The fake spawn reads
    the store at the instant it is called, which is the only way to observe the order rather than
    the end state.
    """
    monkeypatch.setattr(wt, "autonomy_enabled", lambda: True)
    monkeypatch.setattr(wt, "scheduled_mode", lambda: True)
    doorbell = delivery_lane.draw(path=lane, claim=False)
    monkeypatch.setattr(wt, "_draw", lambda: (doorbell, False))

    seen = {}

    def _spawn(reason):
        seen["claims_at_spawn"] = _claim_ids(lane)
        return _FakeProc()

    monkeypatch.setattr(wt, "spawn_invocation", _spawn)

    d = wt.run_tick()

    assert d.outcome == "SPAWNED"
    assert seen["claims_at_spawn"] == {FOCUS_ID}, (
        "the claim must already be in the store when the invocation is launched"
    )


def test_a_lane_that_cannot_import_does_not_take_the_tick_down(_isolate, monkeypatch):  # noqa: F811
    """The asymmetry this sits on: losing a claim costs the bookkeeping this repairs; raising
    costs the tick, and the tick is the thing that does the work.

    MUTATION (must fire): drop the `try/except` in `_claim_dispatched` and this reddens.
    """
    monkeypatch.setattr(wt, "autonomy_enabled", lambda: True)
    monkeypatch.setattr(wt, "scheduled_mode", lambda: True)
    monkeypatch.setattr(wt, "_draw", lambda: ("LANE 0 DELIVERY -- ... --landed some-id", False))
    monkeypatch.setattr(wt, "spawn_invocation", lambda reason: _FakeProc())

    import builtins
    real_import = builtins.__import__

    def _boom(name, *a, **k):
        if name == "background.delivery_lane" or name.endswith("delivery_lane"):
            raise ImportError("simulated")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _boom)

    assert wt.run_tick().outcome == "SPAWNED", "the tick must survive a lane that cannot import"
