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
  (e) drop the authorship test in `_self_issued_chain` (count every continuation row) --
      `..._A_BATCH_WRITTEN_IN_ONE_SITTING_IS_NOT_SELF_ISSUED` goes red;
  (f) stamp every draw `source: focus` -- `..._A_DRAW_STAMPS_WHICH_SOURCE_ANSWERED` and the two
      chain tests go red;
  (g) re-key the link back to `source_written_at > older["last_drawn_at"]` (the 2026-09-07
      defect) -- `..._A_SELF_ISSUED_BACKLOG_DRAWN_OUT_OF_WRITE_ORDER_IS_STILL_A_CHAIN` goes red;
  (h) stop stamping `written_while_holding` in `seat_continuation.hand_off` -- the backlog test
      goes red (everything reads as somebody else's work).

THE 2026-09-07 RE-KEYING, and why the two legs below had to be added. The link was keyed to the
PREVIOUS DRAW, which credits a lane writing exactly one hand-off per turn and breaks on a lane
working through a BACKLOG of its own -- two programmes interleaved, so the row before is not the
parent. Measured on the live ledger: six consecutive self-issued continuation draws, counter = 1,
swap never armed. `_self_issued_chain`'s docstring carries the instants, and the two temporal
repairs that were tried and refuted before authorship was stamped instead.

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
from background import seat_work_in_hand as claims_mod

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
    # AND THE CLAIMS STORE BY MODULE CONSTANT AS WELL AS BY ARGUMENT. `hand_off` stamps authorship
    # from whatever `dl.claims_file()` resolves, which ignores the `path=` these tests pass -- so
    # without this the stamp would read THIS MACHINE'S live delivery-lane claims and the chain
    # would depend on what the real seat happened to be holding.
    monkeypatch.setattr(dl, "CLAIMS_FILE", tmp_path / "claims.json")

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


def test_a_BATCH_WRITTEN_IN_ONE_SITTING_IS_NOT_SELF_ISSUED(lane):
    """WHAT "SELF-ISSUED" MEANS, and the leg that stops this counting the wrong thing. A batch of
    continuations written by ONE interactive session before any of them was drawn is not a lane
    feeding itself -- it is exactly the case the continuation-first order is right for, and
    counting it would starve the source the director asked for.

    THE WRITE INSTANTS ARE DISTINCT AND THE BATCH SITS ON TOP OF REAL HISTORY, and both halves of
    that were bought with a failed mutation. Until 2026-09-07 the writes were all the SAME instant
    -- which no session produces; a session typing four hand-offs writes them seconds apart -- and
    the ledger held nothing but the batch, which the live one never does (94 rows). A purely
    temporal reading passes this test with an empty ledger and counts 9 with history behind it.
    The history is therefore not scene-setting: it is the leg."""
    end = _chain(lane, CHAIN_BUILT)              # real self-issued history, as production has
    assert dl._self_issued_chain(lane["claims"]) >= dl.SELF_HANDOFF_CHAIN_LIMIT, (
        "the history must itself be a chain, or this test cannot show the batch failing to extend "
        "one")

    # Now ONE SESSION writes a batch. It holds no delivery-lane claim -- that is what makes it a
    # session and not a tick, and it is the whole discriminator -- so the run is released first.
    # AND THE HISTORY IS RETIRED FROM THE CONTINUATION STORE, because releasing a claim makes the
    # item offerable again and `live()` is oldest-first: without this the batch is never drawn at
    # all, the ledger's newest rows stay the history's, and the test reads 6 while proving nothing.
    for work_id in claims_mod.held(path=lane["claims"]):
        claims_mod.release(work_id, path=lane["claims"])
        sc.drop(work_id)
    at = end
    for i in range(CHAIN_BUILT + 1):
        sc.hand_off(f"one-session-wrote-all-of-these-{i}", f"piece {i}", "one session, one sitting",
                    "done", now=at + i)
    at += CHAIN_BUILT
    for _ in range(CHAIN_BUILT + 1):
        at += 100.0
        dl.draw(now=at, path=lane["claims"])

    # NON-VACUITY, ASSERTED RATHER THAN ASSUMED: the 0 below must come from the batch being read
    # as somebody else's work, NOT from the batch never reaching the ledger. The first draft of
    # this test read 0 for the second reason and would have passed every mutation.
    ledger = claims_mod._load(dl._ledger_path(lane["claims"]))
    newest = sorted(ledger.items(), key=lambda kv: kv[1]["last_drawn_at"], reverse=True)
    assert newest[0][0].startswith("one-session-wrote-all-of-these-"), (
        f"the batch never reached the head of the ledger -- newest row is {newest[0][0]!r}, so "
        "this test measures an undrawn batch rather than an uncounted one")

    assert dl._self_issued_chain(lane["claims"]) == 0, (
        "a batch written by one session in one sitting is not this lane feeding itself, and "
        "counting it starves the continuation source the director asked for")


def test_a_SELF_ISSUED_BACKLOG_DRAWN_OUT_OF_WRITE_ORDER_IS_STILL_A_CHAIN(lane):
    """THE 2026-09-07 DEFECT, built by the mechanism. The lane runs two programmes interleaved, so
    the hand-off a tick writes is not the next row drawn -- it queues behind one already standing.
    Every continuation here is written by the tick holding a drawn item, which is what self-issued
    means, and NOT ONE of them (after the first pair) was written after the row drawn immediately
    before it. That is the live ledger's shape: six such draws, and the counter said 1.

    The chain must reach the limit, because reaching it is the entire mechanism -- a counter that
    reads under the limit makes every "the swap did not fire" assertion in this file pass for the
    wrong reason."""
    at = NOW_EPOCH
    # Two continuations standing before either is drawn -- an ordinary backlog, not one sitting:
    # each is drawn, and each drawn tick writes the next while the other is still queued.
    sc.hand_off("programme-a-step-1", "carry on with A", "a tick wrote this", "done", now=at)
    sc.hand_off("programme-b-step-1", "carry on with B", "a tick wrote this", "done", now=at + 10)
    drawn = []
    for i in range(CHAIN_BUILT):
        at += 100.0
        drawn.append(dl.draw(now=at, path=lane["claims"]))
        # The tick that just drew writes its own next piece; `live()` is oldest-first, so the row
        # drawn NEXT is the one already queued -- written BEFORE the draw that just happened.
        sc.hand_off(f"written-by-the-tick-that-drew-{i}", f"carry on {i}",
                    "the tick holding the drawn item wrote this", "done", now=at + 10)

    assert all(drawn), "every iteration must actually draw, or this measures an empty ledger"
    chain = dl._self_issued_chain(lane["claims"])
    assert chain >= dl.SELF_HANDOFF_CHAIN_LIMIT, (
        f"a backlog of {CHAIN_BUILT} self-issued hand-offs counted {chain}, under the limit of "
        f"{dl.SELF_HANDOFF_CHAIN_LIMIT}, so the swap never arms -- this is the live ledger's "
        "defect, where six consecutive self-issued draws counted 1")

    # AND THE SWAP ACTUALLY FIRES ON IT. The counter is not the deliverable; the focus list
    # getting a hearing is, and a counter proved in isolation has been wrong here before.
    lane["focus"](["the-seats-own-ranked-item"])
    assert sc.live(now=at + 20), "a continuation must still be live, or this proves the expiry"
    assert dl.next_item(now=at + 20, path=lane["claims"])["id"] == "the-seats-own-ranked-item"


def test_a_DRAW_STAMPS_WHICH_SOURCE_ANSWERED(lane):
    """The chain is measurable only because the draw records its own source. Re-deriving it later
    would read a continuation store that `drop` and the expiry have since emptied, and call every
    past draw a focus draw."""
    lane["focus"](["the-seats-own-ranked-item"])
    sc.hand_off("a-continuation", "do it", "because", "done", now=NOW_EPOCH)
    dl.draw(now=NOW_EPOCH + 1, path=lane["claims"])
    dl.draw(now=NOW_EPOCH + 2, path=lane["claims"])

    ledger = claims_mod._load(dl._ledger_path(lane["claims"]))
    assert ledger["a-continuation"]["source"] == "continuation"
    assert ledger["a-continuation"]["source_written_at"] == NOW_EPOCH
    # AUTHORSHIP IS STAMPED AT THE DRAW TOO, and False here is the correct answer rather than a
    # missing field: this hand-off was written by a session holding no delivery-lane claim.
    assert ledger["a-continuation"]["source_self_issued"] is False
    assert ledger["the-seats-own-ranked-item"]["source"] == "focus"
    assert "source_written_at" not in ledger["the-seats-own-ranked-item"]
    assert "source_self_issued" not in ledger["the-seats-own-ranked-item"]
