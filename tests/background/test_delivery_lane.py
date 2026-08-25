"""R15 contract for LANE 0 — the wire that makes the delivery seat's decisions DRAWABLE.

Director, 2026-08-25, lifting his own constraint: *"When I asked for the delivery seat I said it
must decide and write direction rather than code, so it could never be a second writer on the
tree. That was a defence against a problem you have since solved ... The result was that orienting
became autonomous while the actual building stayed gated on my keypress, which is the opposite of
what I wanted."*

THE DEFECT, MEASURED ON THE SEAT'S FIRST RECORD. Four of five focus items were ids the map had
never heard of, and `direction.focus_weights` only multiplies the weight of an atom the draw was
already considering — so those four biased nothing at all, and the two that got built that day
were built by hand in an interactive session. The steering wheel was connected only to roads
already on the map.

AND THE MAP HAD RUN OUT OF ROADS, in the supervisor's own log the same evening: *"all 24 idle
atom(s) are OVER THE PASS CEILING ... every one of them is now a decision (promote to build, or
close)"*. A dial-weighted draw cannot make a decision. That is what a delivery seat is for.

WHAT THESE TESTS GUARD, and none of them is about the happy path:

  1. THE LANE SILENTLY STOPS BITING. The failure mode of every soft steer in this repo
     (`d7d36b46a`: two soft guards composing into a no-op for 1,307 draws).
  2. THE LANE PRE-EMPTS THE OTHERS. THREE_LANES.md exists because a cascade that returned on the
     first non-empty tier left SITE and DISCOVERY permanently idle. A new tier at the top is that
     regression waiting to happen.
  3. TWO TICKS TAKE THE SAME ITEM, or one takes it and dies holding it forever.
  4. IT DOUBLE-COUNTS. An item that IS an atom is already reached by the weight bias; offering it
     here as well would hand out the same work twice by two routes.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_work_in_hand as claims_mod

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
NOW_EPOCH = NOW.timestamp()


def _record(focus, **over) -> dict:
    base = {
        "version": 1,
        "oriented_at": NOW.isoformat(),
        "focus": focus,
        "not_now": [{"what": "something", "why": "it loses to the above"}],
    }
    base.update(over)
    return base


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    """A direction record, a map, and a claims store, all under tmp_path."""
    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    claims_path = tmp_path / "claims.json"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)

    def _write(focus):
        direction_path.write_text(yaml.safe_dump(_record(focus)), encoding="utf-8")

    return {"write": _write, "claims": claims_path, "map": map_path}


def _item(key, what="do the thing", why="because"):
    return {"id": key, "what": what, "why": why}


# --------------------------------------------------------------------------- #
# 1. It bites: a decision the draw could not reach becomes work                #
# --------------------------------------------------------------------------- #

def test_a_focus_item_with_NO_ATOM_becomes_drawable_work(tree):
    """THE WHOLE POINT. Before this, `flat-control-credible-average-player` could be the seat's
    single highest judgement and no draw on the machine could reach it.

    MUTATION (must fire): return None from `next_item` for a non-atom id -- which is exactly what
    the machine did before this landed.
    """
    tree["write"]([_item("harness-lane-prune", "read the 117 H_harness atoms")])

    item = dl.next_item(now=NOW_EPOCH, path=tree["claims"])

    assert item is not None and item["id"] == "harness-lane-prune"
    assert "read the 117" in dl.doorbell(item)


def test_an_item_that_IS_an_atom_is_NOT_offered_here(tree):
    """It is already reached by `direction.focus_weights`, which multiplies its dial weight in the
    ordinary draw. Offering it here as well hands the same work out twice by two routes, and the
    second route has no file_scope, no disjointness check and no anti-livelock backoff.

    MUTATION (must fire): drop the atom-id filter.
    """
    tree["write"]([_item("EP1_real_atom"), _item("not-an-atom")])

    item = dl.next_item(now=NOW_EPOCH, path=tree["claims"])

    assert item["id"] == "not-an-atom"


def test_THE_SEATS_ORDER_IS_THE_DRAW_ORDER(tree):
    """`focus` is ordered and its first entry is what the seat judged mattered most. Sorting or
    re-ranking it here would quietly overrule the judgement this mechanism exists to carry."""
    tree["write"]([_item("zzz-first-by-the-seat"), _item("aaa-second")])

    assert dl.next_item(now=NOW_EPOCH, path=tree["claims"])["id"] == "zzz-first-by-the-seat"


def test_the_doorbell_carries_the_WHY_and_says_what_DONE_means(tree):
    """A focus item has no exit test -- that is what makes it direction rather than an atom. A
    doorbell that handed over the work without saying so would get a tick looking for an exit
    criterion that was never written.

    MUTATION (must fire): ship the `what` alone.
    """
    tree["write"]([_item("x", "calibrate the control", "the baseline is the whole meaning")])

    bell = dl.doorbell(dl.next_item(now=NOW_EPOCH, path=tree["claims"]))

    assert "calibrate the control" in bell
    assert "the baseline is the whole meaning" in bell
    assert "NOT AN ATOM" in bell and "decide what done means" in bell
    assert "LAND it" in bell, "a decision that is not landed has not been carried out"
    assert "re-orients every three hours" in bell


# --------------------------------------------------------------------------- #
# 2. It never pre-empts the lanes that already work                            #
# --------------------------------------------------------------------------- #

def test_LANE_0_is_PREPENDED_to_the_ladder_and_never_returned_instead_of_it(monkeypatch):
    """THREE_LANES.md exists because a cascade that RETURNED on the first non-empty tier left SITE
    and DISCOVERY permanently idle while BUILD had work. A new tier at the top of that ladder is
    that regression wearing a delivery seat's clothes.

    THE FIRST VERSION OF THIS DID EXACTLY THAT, and three R17 tests caught it inside the hour:
    with the map lanes gated, `PROPOSE-HALF` and `FORWARD-DISCOVERY` stopped firing because the
    delivery item returned above them -- and forward-discovery is the always-drawable floor R17
    exists to protect. It took a delivery seat about forty minutes to build the regression its own
    design doc warns about.

    MUTATION (must fire): return the delivery item instead of combining it with the ladder.
    """
    from background import supervisor as sup

    monkeypatch.setattr(sup, "_delivery_lane_draw", lambda: "DELIVERY-ITEM")
    monkeypatch.setattr(sup, "_self_refill_draw_ladder", lambda: "LADDER-ITEM")

    combined = sup._self_refill_draw()

    assert "DELIVERY-ITEM" in combined
    assert "LADDER-ITEM" in combined, (
        "the ladder's own draw was discarded, so every rung below LANE 0 -- open-campaign, "
        "declared-defect, propose-half, forward-discovery, HARDEN -- is starved whenever the "
        "seat has a decision"
    )
    assert combined.index("DELIVERY-ITEM") < combined.index("LADDER-ITEM"), (
        "the seat's judgement is not first, so a worker reads it after a page of lanes"
    )


def test_an_empty_delivery_lane_leaves_the_draw_BYTE_IDENTICAL(monkeypatch):
    """No live direction, every item an atom, or all of them claimed -- the common case for most
    of any day. The draw must be exactly what it was before this existed.

    MUTATION (must fire): return a wrapper string even when the lane is empty.
    """
    from background import supervisor as sup

    monkeypatch.setattr(sup, "_delivery_lane_draw", lambda: None)
    monkeypatch.setattr(sup, "_self_refill_draw_ladder", lambda: "LADDER-ITEM")

    assert sup._self_refill_draw() == "LADDER-ITEM"

    monkeypatch.setattr(sup, "_self_refill_draw_ladder", lambda: None)

    assert sup._self_refill_draw() is None


def test_the_delivery_item_stands_alone_when_the_ladder_is_empty(monkeypatch):
    """The state this lane was built for: the supervisor's own log on 2026-08-25 read *"all 24
    idle atom(s) are OVER THE PASS CEILING ... every one of them is now a decision"*. A decision is
    what the seat produces, so an empty ladder is the lane's ordinary case, not an edge one."""
    from background import supervisor as sup

    monkeypatch.setattr(sup, "_delivery_lane_draw", lambda: "DELIVERY-ITEM")
    monkeypatch.setattr(sup, "_self_refill_draw_ladder", lambda: None)

    assert sup._self_refill_draw() == "DELIVERY-ITEM"


def test_the_ladder_itself_is_UNTOUCHED_by_this_change():
    """The ladder keeps its own name, its own body and its own byte-preserved single-BUILD-atom
    message. The wrapper is the only thing that knows about delivery, so a reader auditing the
    ladder reads what was there before.

    MUTATION (must fire): reach back into the ladder and special-case delivery inside it, which is
    how the first version starved the rungs below.
    """
    from pathlib import Path

    source = Path(dl.PROJECT_DIR / "background" / "supervisor.py").read_text(encoding="utf-8")
    ladder = source[source.index("def _self_refill_draw_ladder"):
                    source.index("def _priority_zero_active() -> bool:")]

    assert "delivery" not in ladder.lower(), (
        "the ladder knows about the delivery lane; the whole point of the wrapper is that it "
        "does not"
    )
    assert 'return f"self-refill from maturity map (dial-weighted): ' in ladder, (
        "the byte-preserved single-BUILD-atom message is gone from the ladder"
    )


def test_a_lane_that_cannot_import_or_read_returns_NOTHING_rather_than_raising(monkeypatch):
    """This sits inside `_self_refill_draw`. A lane that can throw takes every other lane with it,
    and an empty feasible set is a defect in the dials (Rule 0) -- a crashing lane is the worst
    possible way to produce one.

    MUTATION (must fire): let the exception out of `draw`.
    """
    def _boom(*a, **k):
        raise RuntimeError("no")

    monkeypatch.setattr(dl, "next_item", _boom)

    assert dl.draw() is None


def test_an_unreadable_map_does_not_HIDE_the_seats_decisions(tmp_path, monkeypatch):
    """FAIL TOWARD OFFERING THE WORK. An unreadable map yields an empty atom set, so every focus
    item reads as unreachable -- noisy, and the safe direction. The opposite error would silently
    swallow the seat's decisions whenever the map hiccuped, which is the failure being repaired.
    """
    monkeypatch.setattr(dl, "MATURITY_MAP", tmp_path / "gone.yaml")

    assert dl._atom_ids() == set()


# --------------------------------------------------------------------------- #
# 3. Claims: one taker, and a stalled item comes back                          #
# --------------------------------------------------------------------------- #

def test_a_CLAIMED_item_is_not_offered_to_a_second_tick(tree):
    """Two ticks doing the same piece of work is the fork-thrash this project has already paid for
    twice (`SITE_EH1` minted a rival implementation inside one hour).

    MUTATION (must fire): stop consulting the claims store.
    """
    tree["write"]([_item("first"), _item("second")])

    assert dl.draw(now=NOW_EPOCH, path=tree["claims"]) is not None
    nxt = dl.next_item(now=NOW_EPOCH, path=tree["claims"])

    assert nxt["id"] == "second", "the claimed head was offered again"


def test_a_claimed_HEAD_does_not_block_the_TAIL(tree):
    """A single in-flight item must not stall the lane: the seat named five things, not one."""
    tree["write"]([_item("a"), _item("b"), _item("c")])
    for expected in ("a", "b", "c"):
        item = dl.next_item(now=NOW_EPOCH, path=tree["claims"])
        assert item["id"] == expected
        claims_mod.claim(item["id"], path=tree["claims"], now=NOW_EPOCH)

    assert dl.next_item(now=NOW_EPOCH, path=tree["claims"]) is None


def test_a_claim_that_LANDS_NOTHING_goes_back_in_the_pool(tree, monkeypatch):
    """A tick that dies holding an item would strand it forever, and the whole subject here is
    CONTINUITY of work. The deadline is the mechanism `seat_work_in_hand` was built around for the
    interactive seat; this is the same primitive with its own store and its own deadline.

    MUTATION (must fire): drop the sweep from `next_item`.
    """
    tree["write"]([_item("stranded")])
    monkeypatch.setattr(claims_mod, "_last_commit_time_touching", lambda paths: 0.0)
    claims_mod.claim("stranded", path=tree["claims"], now=NOW_EPOCH)

    assert dl.next_item(now=NOW_EPOCH + 60, path=tree["claims"]) is None, "released far too early"

    later = NOW_EPOCH + dl.CLAIM_STALE_SECONDS + 1

    assert dl.next_item(now=later, path=tree["claims"])["id"] == "stranded"


def test_the_delivery_deadline_is_LONGER_than_the_interactive_seats_and_SHORTER_than_a_tick():
    """Longer than 45 minutes because this is the multi-hour class of work by design -- the whole
    point of the lane -- and a 45-minute deadline would thrash a claim rather than catch a stall.
    Shorter than the tick's own 2-hour ceiling so a dead invocation cannot hold an item past its
    own lifetime.
    """
    assert claims_mod.STALE_AFTER_SECONDS < dl.CLAIM_STALE_SECONDS < 2 * 60 * 60


def test_the_shared_claim_primitive_is_UNCHANGED_for_the_interactive_seat(tmp_path, monkeypatch):
    """`stale_after` was added so one implementation can serve two subjects. Its default must
    reproduce the interactive seat's behaviour byte-for-byte, or this change moved a mechanism
    that was working.

    MUTATION (must fire): change the default.
    """
    store = tmp_path / "c.json"
    monkeypatch.setattr(claims_mod, "_last_commit_time_touching", lambda paths: 0.0)
    claims_mod.claim("w", path=store, now=NOW_EPOCH)
    just_under = NOW_EPOCH + claims_mod.STALE_AFTER_SECONDS - 1
    just_over = NOW_EPOCH + claims_mod.STALE_AFTER_SECONDS + 1

    assert claims_mod.stale_claims(path=store, now=just_under) == []
    assert [w for w, _, _ in claims_mod.stale_claims(path=store, now=just_over)] == ["w"]


# --------------------------------------------------------------------------- #
# 4. Stale direction must not hand out work either                             #
# --------------------------------------------------------------------------- #

def test_EXPIRED_direction_offers_NOTHING(tree):
    """Stale direction stops steering the weights on its own; it must not keep handing out work
    through the other route. Two paths out of one record have to expire together, or the fix for
    one is a hole in the other.

    MUTATION (must fire): drop the liveness check from `unreachable_focus`.
    """
    old = NOW - timedelta(hours=d.FOCUS_MAX_AGE_HOURS + 1)
    tree["write"]([_item("too-old")])
    import pathlib
    path = pathlib.Path(d.DIRECTION_PATH)
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    record["oriented_at"] = old.isoformat()
    path.write_text(yaml.safe_dump(record), encoding="utf-8")

    assert d.unreachable_focus({"EP1_real_atom"}, now=NOW) == []
    assert dl.next_item(now=NOW_EPOCH, path=tree["claims"]) is None


def test_a_MISSING_or_BROKEN_record_offers_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "DIRECTION_PATH", tmp_path / "absent.yaml")

    assert d.unreachable_focus({"a"}) == []

    broken = tmp_path / "broken.yaml"
    broken.write_text("this: [is not: yaml", encoding="utf-8")
    monkeypatch.setattr(d, "DIRECTION_PATH", broken)

    assert d.unreachable_focus({"a"}) == []


def test_the_release_CLI_frees_a_claim(tree, capsys):
    """A tick that finishes early should not sit on a claim until the deadline. It does not HAVE
    to release -- the seat's next orientation drops what is done, which is the real acceptance
    test -- but the tick is told the command, so the command has to work."""
    tree["write"]([_item("finished")])
    dl.draw(now=NOW_EPOCH, path=tree["claims"])

    assert dl.held(tree["claims"]) == {"finished"}

    claims_mod.release("finished", path=tree["claims"])

    assert dl.held(tree["claims"]) == set()


def test_the_lane_is_reachable_from_the_supervisors_own_draw():
    """A mechanism nobody invokes is the fix that isn't. The lane exists to be drawn, and the
    draw is the only caller that matters.

    MUTATION (must fire): define `_delivery_lane_draw` and never call it.
    """
    from pathlib import Path

    source = Path(dl.PROJECT_DIR / "background" / "supervisor.py").read_text(encoding="utf-8")

    assert source.count("_delivery_lane_draw()") >= 2, (
        "the delivery lane is defined but the draw never calls it"
    )


def test_an_EMERGENCY_is_the_whole_message_and_never_carries_a_delivery_item(monkeypatch):
    """RUNGS 1/1b/1d ARE PRIORITY ZERO BY RULING. A wedged publish gate, a dead producer or a
    persistent operational red each stop the project outright. Handing a worker two things to do
    with the urgent one second is exactly the dilution those rungs exist to prevent, and
    `test_producer_starvation_draw.py` asserts the equality that catches it -- it caught this.

    The delivery seat AGREES, which is the reassuring part: its own second focus item on the day
    this landed was `publish-path-lands`. A seat that decides what matters puts the outage first
    too.

    MUTATION (must fire): prepend the delivery item unconditionally.
    """
    from background import supervisor as sup

    monkeypatch.setattr(sup, "_delivery_lane_draw", lambda: "DELIVERY-ITEM")
    monkeypatch.setattr(sup, "_self_refill_draw_ladder", lambda: "PRODUCER STARVATION self-refill")
    monkeypatch.setattr(sup, "_priority_zero_active", lambda: True)

    assert sup._self_refill_draw() == "PRODUCER STARVATION self-refill"


def test_the_emergency_check_FAILS_TOWARD_the_emergency(monkeypatch):
    """The harmful mistake is handing a worker a delivery item alongside a dead pipeline. The
    harmless one is delaying a delivery item by one thirty-minute tick. So any error in the check
    reads as "yes, something is wrong".

    MUTATION (must fire): return False on error.
    """
    from background import supervisor as sup

    def _boom(*a, **k):
        raise RuntimeError("the state file is unreadable")

    monkeypatch.setattr(sup, "_publish_gate_wedge_active", _boom)

    assert sup._priority_zero_active() is True


def test_the_emergency_check_asks_the_RUNGS_OWN_predicates_not_the_message(monkeypatch):
    """A string test would break the first time a rung reworded itself, and would break SILENTLY,
    in the direction of diluting an emergency."""
    import inspect

    from background import supervisor as sup

    source = inspect.getsource(sup._priority_zero_active)

    for predicate in ("_publish_gate_wedge_active", "_producer_starved_active",
                      "_operational_red_persistent_draw"):
        assert predicate in source, f"{predicate} is not consulted, so its rung can be diluted"
    assert "startswith" not in source and "in ladder" not in source
