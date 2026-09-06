"""The seat's focus list was outranked forever by a lane that hands off to itself.

THE DEFECT, measured on the live draw ledger 2026-09-06. `next_item` walks
`seat_continuation.live()` to exhaustion before `direction_mod.unreachable_focus` is consulted at
all. That ordering was argued from FRESHNESS -- a continuation is minutes old and written by a
session holding the whole context, a focus item up to three hours old and re-derived from the tree
-- and the argument is right for a FIRST continuation. It fails for the fifth in one programme:
once the lane writes its own next item every turn, the first loop never runs dry, and the second
loop is unreachable BY CONSTRUCTION rather than by ranking. The ledger's last twelve rows were
twelve continuations in an unbroken chain, and 94 rows recorded that no focus id had ever been
drawn.

WHY THE POISON ROUND IS THE FIRST TEST IN THIS FILE. This project has entered exactly one trap
three times in one afternoon: asserting that the branch which ALREADY fires still fires, over a
mechanism whose other branch is dead, and reading a green suite as proof of a partition. A test
that only checks "a continuation still wins" passes unchanged if `SELF_HANDOFF_CHAIN_LIMIT` is
raised to a million and the focus-wins branch can never be taken. So the control below asserts
over the WHOLE PARTITION in one statement -- both outcomes observed from one mechanism -- and the
poison round proves it can fail.

MUTATIONS (each must fire, and which test catches it):
  (a) `SELF_HANDOFF_CHAIN_LIMIT = 10**9` (the branch made unreachable) -- the partition control
      and `..._FOCUS_WINS_...` go red;
  (b) delete the swap and always order `(_continuation, _focus)` -- same two;
  (c) always order `(_focus, _continuation)` -- `..._A_FIRST_HANDOFF_STILL_WINS` goes red;
  (d) make the second source a suppression rather than a swap (return None instead of falling
      through) -- `..._STILL_GETS_ITS_CONTINUATION_WHEN_FOCUS_IS_EMPTY` goes red;
  (e) drop the `source_written_at > previous last_drawn_at` link test in `_self_issued_chain`
      -- `..._A_HANDOFF_WRITTEN_BEFORE_THE_PREVIOUS_DRAW_IS_NOT_SELF_ISSUED` goes red;
  (f) stamp every draw `source: focus` -- `..._A_DRAW_STAMPS_WHICH_SOURCE_ANSWERED` and the two
      chain tests go red.

AND ONE SURVIVAL, RECORDED BECAUSE IT WAS ESTABLISHED RATHER THAN ASSUMED. `_self_issued_chain`
opened with a second break on `newer["source"] != "continuation"`, and deleting it killed nothing.
It is an EQUIVALENCE, not a missing test: `record_draw` writes `source_written_at` only where it
writes `source: continuation`, so the link test already breaks the run on the same row. The leg
was deleted rather than left standing green.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_continuation as sc

# Relative for the reason `test_delivery_lane` records at length: the direction record has a
# liveness window checked against the real clock, and a frozen instant makes every draw test here
# go red a day after it is written for a reason that has nothing to do with the code.
NOW = datetime.now(timezone.utc)
NOW_EPOCH = NOW.timestamp()

#: How long a chain these tests build. A FIXED number and deliberately not
#: `dl.SELF_HANDOFF_CHAIN_LIMIT`, which is the shape that made the first draft of this file HANG
#: rather than fail under its own first mutation: a chain built to the length of the constant
#: under test builds 10**9 links when the constant is poisoned to 10**9. `_chain` asserts the
#: module's limit is inside this instead, so a limit raised past what this file exercises is a RED
#: TEST saying so, not a branch that quietly stopped being proved.
CHAIN_BUILT = 6


@pytest.fixture()
def lane(tmp_path, monkeypatch):
    """Direction, map, claims store AND continuation store under tmp_path.

    The draw ledger needs no seam of its own: `_ledger_path` derives it from the claims store, so
    isolating the claims path isolates the record of what this lane has drawn. That is the whole
    reason it was built derived rather than as a module constant.
    """
    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)
    monkeypatch.setattr(sc, "STORE", tmp_path / ".seat_continuation.json")

    def write_focus(ids):
        direction_path.write_text(yaml.safe_dump({
            "version": 1,
            "oriented_at": NOW.isoformat(),
            "focus": [{"id": i, "what": f"do {i}", "why": "the seat ranked it"} for i in ids],
            "not_now": [{"what": "something", "why": "it loses to the above"}],
        }), encoding="utf-8")

    write_focus([])
    return {"focus": write_focus, "claims": tmp_path / "claims.json"}


def _chain(lane, links, *, start=0.0):
    """Drive `links + 1` real self-issued hand-offs through `draw`, returning the last instant.

    THE CHAIN IS BUILT BY THE MECHANISM, NOT HAND-WRITTEN INTO THE LEDGER. A ledger fixture would
    let the two halves of this feature agree with each other while neither agreed with what a draw
    actually stamps -- the shape that has published a verdict no run produced. Each iteration is
    the real cycle: a hand-off written AFTER the previous draw (which is what makes its author the
    lane that drew it), then a draw that claims it and records the row.

    IT EMPTIES THE FOCUS LIST FIRST, and finding out why is the clearest evidence the mechanism
    works: with a focus item present, the fourth draw of a six-link build went to FOCUS and reset
    the chain, so the helper could never hand its caller a chain longer than the limit. The
    mechanism interrupting the helper is the feature. Callers write their focus list AFTER this
    returns, so what they measure is the ordering and not the reset.
    """
    lane["focus"]([])
    assert dl.SELF_HANDOFF_CHAIN_LIMIT <= links, (
        f"SELF_HANDOFF_CHAIN_LIMIT is {dl.SELF_HANDOFF_CHAIN_LIMIT} and this file only ever builds "
        f"a {links}-link chain, so the focus-wins branch is no longer reached by anything here. "
        "Raise CHAIN_BUILT with the limit -- do not delete this assertion.")
    at = start
    for i in range(links + 1):
        at = start + (i + 1) * 100.0
        sc.hand_off(f"self-issued-{i}", f"carry on with {i}", "the lane that drew the last one "
                    "wrote this", "the next link exists", now=at)
        dl.draw(now=at + 10.0, path=lane["claims"])
    return at + 10.0


# --------------------------------------------------------------------------- #
# The poison round FIRST: is the focus-wins branch reachable at all?           #
# --------------------------------------------------------------------------- #

def test_BOTH_BRANCHES_of_the_source_order_are_REACHABLE_from_one_mechanism(lane):
    """ONE CONTROL OVER THE WHOLE PARTITION. Everything below this line asserts one branch each,
    and every one of them passes on a mechanism whose other branch is dead -- which is how a guard
    that refuses everything passes every test of its refusals. This asserts the two outcomes
    together, from the same code path, with nothing changed between them but the chain length.
    """
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("first-continuation", "finish this", "the session knew why",
                "the thing is done", now=NOW_EPOCH)

    short_chain = dl.next_item(now=NOW_EPOCH + 1, path=lane["claims"])
    # `next_item` is a pure read, so this one stays unclaimed and would be drawn FIRST by the
    # cycle below (`live()` is oldest-first) -- shifting every draw onto the wrong hand-off and
    # measuring nothing. Retiring it here leaves the chain the cycle actually builds.
    sc.drop("first-continuation")

    end = _chain(lane, CHAIN_BUILT, start=NOW_EPOCH + 10)
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("continuation-still-standing", "and this too", "still self-issued",
                "done", now=end + 1)
    long_chain = dl.next_item(now=end + 2, path=lane["claims"])

    assert short_chain["id"] == "first-continuation", (
        "the continuation source must still win for a first hand-off")
    assert long_chain["id"] == "the-seats-own-ranked-item", (
        "the focus-wins branch is UNREACHABLE: a live continuation was offered after "
        f"{CHAIN_BUILT} self-issued hand-offs, which is the state the live ledger "
        "was in for twelve consecutive draws")


# --------------------------------------------------------------------------- #
# The legs                                                                     #
# --------------------------------------------------------------------------- #

def test_a_FIRST_HANDOFF_STILL_WINS_over_focus(lane):
    """The ordering this bounds is CORRECT where it started, and the bound must not repeal it.
    A session that has just finished a piece knows what comes next better than a three-hour-old
    re-derivation from the tree; that is the whole reason the continuation source exists."""
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("minutes-old-handoff", "finish the thing", "the session knew why",
                "the control reads its live subject", now=NOW_EPOCH)

    assert dl.next_item(now=NOW_EPOCH + 1, path=lane["claims"])["id"] == "minutes-old-handoff"


def test_FOCUS_WINS_after_the_chain_limit_of_self_issued_handoffs(lane):
    """The defect itself. Nothing about the continuation store has changed -- it still holds a
    live, unclaimed, in-window hand-off -- and the seat's list is consulted first anyway."""
    end = _chain(lane, CHAIN_BUILT)
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("one-more-self-issued", "and again", "the lane wrote this too", "done",
                now=end + 1)

    assert sc.live(now=end + 2), "the continuation source must still be non-empty, or this "\
        "test proves the expiry rather than the ordering"
    assert dl.next_item(now=end + 2, path=lane["claims"])["id"] == "the-seats-own-ranked-item"


def test_a_chained_lane_STILL_GETS_ITS_CONTINUATION_WHEN_FOCUS_IS_EMPTY(lane):
    """IT IS A SWAP, NEVER A SUPPRESSION. A bound that idled the lane whenever the seat's list
    happened to be empty would trade one silent stall for another -- and a lane that stops
    delivering is the failure this whole module was built around (`draw`'s six-day walkover)."""
    end = _chain(lane, CHAIN_BUILT)
    sc.hand_off("the-only-work-there-is", "carry on", "nothing else is offered", "done",
                now=end + 1)

    assert dl.next_item(now=end + 2, path=lane["claims"])["id"] == "the-only-work-there-is"


def test_a_FOCUS_DRAW_RESETS_THE_CHAIN(lane):
    """The reset is the ledger's newest row, not a counter. Once focus is drawn the leading run of
    continuation rows is broken, so the ordinary continuation-first order returns on the next draw
    -- otherwise the fix would be a one-way door that retires the continuation source for good."""
    end = _chain(lane, CHAIN_BUILT)
    lane["focus"](["the-seats-own-ranked-item"])
    assert dl.draw(now=end + 1, path=lane["claims"]), "the focus item must actually be drawn"
    assert dl._self_issued_chain(lane["claims"]) == 0

    sc.hand_off("after-the-reset", "carry on", "written by whoever drew last", "done",
                now=end + 2)
    assert dl.next_item(now=end + 3, path=lane["claims"])["id"] == "after-the-reset"


def test_a_HANDOFF_WRITTEN_BEFORE_THE_PREVIOUS_DRAW_IS_NOT_SELF_ISSUED(lane):
    """WHAT "SELF-ISSUED" MEANS, and the leg that stops this counting the wrong thing. A batch of
    continuations written by ONE interactive session before any of them was drawn is not a lane
    feeding itself -- it is exactly the case the continuation-first order is right for, and
    counting it would starve the source the director asked for."""
    for i in range(CHAIN_BUILT + 1):
        sc.hand_off(f"one-session-wrote-all-of-these-{i}", f"piece {i}", "one session, one sitting",
                    "done", now=NOW_EPOCH)
    at = NOW_EPOCH
    for _ in range(CHAIN_BUILT + 1):
        at += 100.0
        dl.draw(now=at, path=lane["claims"])

    assert dl._self_issued_chain(lane["claims"]) == 0


def test_a_DRAW_STAMPS_WHICH_SOURCE_ANSWERED(lane):
    """The chain is measurable only because the draw records its own source. Re-deriving it later
    would read a continuation store that `drop` and the expiry have since emptied, and call every
    past draw a focus draw."""
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("a-continuation", "do it", "because", "done", now=NOW_EPOCH)
    dl.draw(now=NOW_EPOCH + 1, path=lane["claims"])
    dl.draw(now=NOW_EPOCH + 2, path=lane["claims"])

    from background import seat_work_in_hand as claims_mod
    ledger = claims_mod._load(dl._ledger_path(lane["claims"]))
    assert ledger["a-continuation"]["source"] == "continuation"
    assert ledger["a-continuation"]["source_written_at"] == NOW_EPOCH
    assert ledger["the-seats-own-ranked-item"]["source"] == "focus"
    assert "source_written_at" not in ledger["the-seats-own-ranked-item"]
