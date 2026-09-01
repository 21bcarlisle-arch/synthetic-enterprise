"""LANE 0 CLAIMED SIXTY-EIGHT ITEMS AND DELIVERED NONE, and it logged every claim as a success.

THE DEFECT (measured 2026-08-31, over the whole of `docs/observability/supervisor-log.md`):

    "LANE 0 DELIVERY:"   -- the line the DRAW writes when it takes an item   ->  68 occurrences
    "LANE 0 DELIVERY --" -- the DOORBELL text that reaches a worker          ->   0 occurrences

Sixty-eight claims, zero deliveries, across every ledger in the repository. The lane was built on
2026-08-25 so the delivery seat's own decisions could be drawn as work; it has never handed one
out.

WHY. `supervisor.find_work()` has two callers with different powers, and only one of them can
deliver:

  * `background/supervisor.py` polls it every ~2 minutes as an INDEPENDENT ESCALATION WATCHDOG.
    Its own `grant_turn` docstring says it "performs ZERO pane writes" -- it draws for the alarm
    signal and throws the reason away.
  * `.claude/hooks/pull_next_work.py`, the Stop hook, calls the same draw AT A TURN BOUNDARY and
    is the only thing that feeds work to a session.

`delivery_lane.draw()` claimed on the way past. Two-minute polling against a turn boundary is not
a race, it is a walkover: the watchdog took every item first, discarded the doorbell, and held the
claim for its full 100-minute deadline -- during which `next_item` correctly skipped it as `held`,
so every draw that COULD have delivered saw an empty lane. Then the sweeper released it as an
abandoned claim and the cycle repeated.

WHAT MAKES IT THIS PROJECT'S RECURRING SHAPE rather than an ordinary bug: **it failed quietly and
it failed by SUCCEEDING.** The claim worked. The log line was written. The ledger recorded a draw.
Nothing anywhere was red, and two separate sessions -- including one that had just built a handoff
mechanism ON TOP of this lane and reported it "armed and untested" -- looked straight at the log
line and read it as delivery. The only thing that could have told them apart is the pair of counts
at the top of this file, and nobody had counted.

THE PROPERTY, keyed to the property and not to today's answer: **a caller that cannot deliver must
not claim.** `draw(claim=False)` is the watchdog's read.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane, seat_continuation, supervisor


@pytest.fixture
def lane(tmp_path, monkeypatch):
    """A delivery lane with its own claim store and exactly one live continuation.

    Both stores are redirected: the claim file this lane reads, and the continuation store
    `next_item` consults ahead of the periodic focus list. Nothing here touches the real ones --
    `tests/production_surface_guard.py` would refuse anyway, and refusing is the point.
    """
    claims = tmp_path / "claims.json"
    handoffs = tmp_path / "continuations.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    # `STORE`, and it must be the module attribute rather than a `path=` argument: `next_item`
    # calls `seat_continuation.live(now=now)` with no path, so a fixture that only passed a path
    # to `hand_off` would write to tmp and READ the live store -- a test that passes for the
    # wrong reason and, worse, one that reads real state.
    monkeypatch.setattr(seat_continuation, "STORE", handoffs)
    seat_continuation.hand_off(
        "union-the-departure-routes",
        what="Union both departure routes and declare the denominator.",
        why="A mean over a selected sub-population is not a whole-population rate.",
        done_means="the level prints over both routes with the denominator named.",
    )
    return claims


def _claim_ids(store):
    if not store.exists():
        return set()
    return set(json.loads(store.read_text()).keys())


def test_the_watchdogs_read_returns_the_work_and_claims_nothing(lane):
    """`claim=False` sees exactly what would be handed out, and hands out nothing."""
    doorbell = delivery_lane.draw(path=lane, claim=False)

    assert doorbell, "the watchdog must still SEE the item -- it is the escalation signal"
    assert "union-the-departure-routes" in doorbell
    assert _claim_ids(lane) == set(), (
        "a caller that cannot deliver must leave the lane exactly as it found it"
    )


def test_the_transports_draw_still_claims(lane):
    """The default is unchanged. The fix must not turn the delivery route into a read too --
    two transports drawing the same item is the collision claims exist to prevent."""
    doorbell = delivery_lane.draw(path=lane)

    assert doorbell
    assert _claim_ids(lane) == {"union-the-departure-routes"}


def test_a_hundred_watchdog_polls_leave_the_item_drawable(lane):
    """THE REGRESSION ITSELF, in the shape it actually took.

    The watchdog polls every ~2 minutes; a turn boundary comes when it comes. Before the fix the
    first poll won and the transport found an empty lane for the next hundred minutes. Fifty polls
    stands in for that hour, and the assertion is the one that was false in production: after all
    of them, the thing that CAN deliver still can.
    """
    for _ in range(50):
        assert delivery_lane.draw(path=lane, claim=False), "the lane went empty under polling"

    item = delivery_lane.next_item(path=lane)
    assert item is not None and item["id"] == "union-the-departure-routes"

    delivered = delivery_lane.draw(path=lane)
    assert delivered and "union-the-departure-routes" in delivered
    assert _claim_ids(lane) == {"union-the-departure-routes"}


def test_the_supervisor_lane_draw_is_a_read(monkeypatch):
    """Keyed to the SEAT of the defect, not to the lane's own signature.

    The lane could grow a correct `claim=False` and the supervisor could carry on calling it
    without one -- which is precisely the state this repo was in for six days. So this asserts
    what the supervisor PASSES, by watching the call rather than by reading the source (a source
    check would be satisfied by the word `claim=False` appearing in a comment).
    """
    seen = {}

    def _spy(*args, **kwargs):
        seen.update(kwargs)
        return "LANE 0 DELIVERY -- spy"

    monkeypatch.setattr(delivery_lane, "draw", _spy)
    result = supervisor._delivery_lane_draw()

    assert result == "LANE 0 DELIVERY -- spy"
    assert seen.get("claim") is False, (
        "the supervisor is the escalation watchdog and performs zero pane writes; if it claims, "
        "it takes the item away from the pull-loop hook, which is the only caller that delivers"
    )


def test_a_lane_that_cannot_read_its_store_costs_no_tick(lane, monkeypatch):
    """`draw` documents that a lane which can throw takes every other lane down with it. The new
    parameter must not open a path that raises -- including the early return it added."""
    def _explode(*a, **k):
        raise RuntimeError("store unreadable")

    monkeypatch.setattr(delivery_lane, "next_item", _explode)
    assert delivery_lane.draw(path=lane, claim=False) is None
    assert delivery_lane.draw(path=lane) is None


# ── Publish-gate scope (R10): DAEMON-LIFECYCLE test module. It validates the work-granting
# machinery -- which caller may claim a queue item -- never a published business surface, so it
# must never wedge the live publish. The gate runs `-m 'not operational'`.
pytestmark = pytest.mark.operational
