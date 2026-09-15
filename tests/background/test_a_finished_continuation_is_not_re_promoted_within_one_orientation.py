"""A tick's finish must survive the re-derivation that produced the item, or `--release` buys an hour.

THE DEFECT, measured on this repair's own doorbell (2026-09-06). `delivery_lane --release` retired
the offer by DELETING the continuation entry, and an absent entry is precisely the state
`seat_executor._promote_to_handoff` reads as "not yet handed over". The focus list is a standing
document that does not change because a tick finished something, so the executor re-derived the
same row on its next stand-down and promoted it again:

    09:06:25  seat-focus-is-outranked-by-a-lane-that-hands-off-to-itself promoted
    09:19:28  drawn and claimed by a tick
    09:49:03  9210d8153 lands the repair the item asked for
    ~10:0x    released -- both stores discharged, exactly as designed
    10:06:25  RE-PROMOTED, same prose, `written_at` restamped
    10:19:20  handed to the next tick, still opening "another lane holds
              `background/delivery_lane.py` dirty with 111 uncommitted lines" about a file that
              had been clean and committed for twenty minutes

Two things fail there, not one. The instruction is spent, and the RE-STAMP restarts the six-hour
window -- so the expiry that exists to stop a continuation outliving the tree it reasoned about
cannot fire on a re-promoted item either. Its clock is reset every hour on prose nobody re-reads.

WHAT EACH LEG NAMES AS ITS OWN DEFECT:

* the refusal cannot fire at all -- a guard that refuses nothing passes every negative leg, which
  is why the POISON ROUND is the first test in this file rather than a note at the bottom;
* the refusal fires FOREVER -- a retirement that never spends starves the promotion route the
  director named as the biggest single drag on the project, which is a worse failure than the one
  being fixed and is why the second test is the same partition from the other side;
* a retired entry vanishes from every surface -- this store's own history is that its one success
  was reported for a day as its defining failure, and a filter nobody can see is how that happens;
* an unfinished item stops being offered -- the discharge is wired to a tick SAYING it finished,
  and any version of this that fires on abandonment loses work instead of stopping a re-offer.
"""
from __future__ import annotations

import pytest

from background import delivery_lane, seat_continuation

ORIENTATION = "2026-09-06T08:22:46+00:00"
LATER = "2026-09-06T11:22:46+00:00"

FOCUS_ROW = {
    "id": "the-piece-a-tick-finished",
    "what": "READ THE TREE BEFORE TOUCHING THIS. Another lane holds the file dirty.",
    "why": "the seat's longest-open error",
}


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "continuations.json"
    monkeypatch.setattr(seat_continuation, "STORE", path)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus",
                        lambda *a, **k: [dict(FOCUS_ROW)])
    return path


def _orientation(monkeypatch, stamp):
    monkeypatch.setattr(delivery_lane, "current_orientation", lambda *a, **k: stamp)


def test_POISON_ROUND_the_refusal_can_fire_before_anything_else_is_asserted_about_it(
    store, monkeypatch
):
    """FIRST, because every other leg here is a negative one and a guard that refuses NOTHING
    passes all of them. This asserts the refusing branch is REACHABLE on the real route: promote,
    finish, and the next promotion under the same orientation is refused by name.

    It also asserts the refusal SAYS WHY -- naming the orientation is what lets a reader discover
    that the retirement itself was wrong, which is how one refusal here was corrected within an
    hour of shipping.
    """
    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "done means what the tick decides")
    assert delivery_lane.retire_continuation(FOCUS_ROW["id"]) is True

    with pytest.raises(ValueError) as refusal:
        delivery_lane.hand_off_focus(FOCUS_ROW["id"], "done means what the tick decides")

    assert "RETIRED as finished" in str(refusal.value)
    assert ORIENTATION in str(refusal.value), (
        "a refusal that does not name the orientation it turned on cannot be argued with"
    )


@pytest.mark.parametrize("orientation_now,expect_promoted", [
    (ORIENTATION, False),   # the seat has NOT re-derived: the finish still holds
    (LATER, True),          # the seat oriented again and still names it: the retirement is spent
    (None, True),           # the record could not be read: today's behaviour, never a wedge
])
def test_a_retirement_is_spent_by_THE_SEAT_REORIENTING_and_by_nothing_else(
    store, monkeypatch, orientation_now, expect_promoted
):
    """ONE CONTROL OVER THE WHOLE PARTITION, and both answers occur -- a guard that refuses
    everything fails row 2 and row 3, and one that refuses nothing fails row 1.

    Row 2 is the load-bearing one and it is not tidiness: `AUTO_PROMOTION_DONE_MEANS` has told
    every reader since it was written that "done is when the seat's next orientation stops naming
    it". If the seat re-orients and the row is STILL there, the seat is restating the work and the
    machine must be able to hand it over again. A version of this fix keyed to a timer would have
    to guess how long a seat takes to re-orient; this asks the record.

    Row 3 is fail-open ON PURPOSE and the two costs are not symmetric: allowing a promotion on an
    unreadable direction file costs one repeated offer, which is the defect we already have and can
    see; refusing would silently wedge the promotion route shut behind a file nobody is looking at.

    MUTATIONS RUN, with what each actually killed rather than what was predicted of it:
      * compare against `retired_under is not None` alone (drop the `== current_orientation()`)
        -> row 2 and row 3 red, row 1 green: the retirement never spends. PREDICTED TWO, GOT
        THREE -- `..._carries_FRESH_PROSE_...` below also fires, because a retirement that never
        spends means the seat's restated row never reaches the store at all. Kept beside the claim
        rather than revised: the extra kill is the one that shows this is not a tidiness fix;
      * delete the refusal -> row 1 red and the poison round red, rows 2 and 3 GREEN, which is the
        asymmetry that makes this a partition and not three copies of one assertion.
    """
    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "done means what the tick decides")
    delivery_lane.retire_continuation(FOCUS_ROW["id"])

    _orientation(monkeypatch, orientation_now)
    try:
        delivery_lane.hand_off_focus(FOCUS_ROW["id"], "done means what the tick decides")
        promoted = True
    except ValueError:
        promoted = False

    assert promoted is expect_promoted
    # THE PROPERTY ASSERTED AGAINST THE DRAW, not against the store: what the defect cost was a
    # tick, and a tick sees `live()`, not a JSON file.
    offered = [i["id"] for i in seat_continuation.live()]
    assert (FOCUS_ROW["id"] in offered) is expect_promoted, offered


def test_the_re_promotion_a_reorientation_allows_carries_FRESH_PROSE_and_a_fresh_window(
    store, monkeypatch
):
    """The re-stamp is only honest when the seat has restated the row, so this asserts the entry
    that comes back is the row as it reads NOW rather than the retired text with a new clock.

    MUTATION: have `hand_off` keep the retired entry's `what` and this fires. That is the shape the
    defect actually had -- identical prose, restamped -- and it is what made the stale instruction
    unfalsifiable to the tick that received it.
    """
    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "d")
    delivery_lane.retire_continuation(FOCUS_ROW["id"])

    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus",
                        lambda *a, **k: [dict(FOCUS_ROW, what="the tree has moved; do the next bit")])
    _orientation(monkeypatch, LATER)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "d")

    live = seat_continuation.live()
    assert [i["id"] for i in live] == [FOCUS_ROW["id"]]
    assert live[0]["what"] == "the tree has moved; do the next bit"
    assert not live[0].get("retired_at"), (
        "the re-promotion inherited the retirement, so the seat's restatement is not offerable"
    )


@pytest.mark.parametrize("orientation_now,expect_offered", [
    (ORIENTATION, False),   # finished under the orientation still in force
    (LATER, True),          # the seat oriented again and STILL names it: offer it
])
def test_the_FOCUS_route_honours_the_finish_too_or_the_id_comes_back_by_the_other_door(
    store, monkeypatch, tmp_path, orientation_now, expect_offered
):
    """THE HALF THAT WAS MISSED FIRST TIME, and it was missed for a minute rather than a month
    because the fix was checked against `next_item` on the live tree instead of against the store.

    `_focus` reads `DIRECTION.yaml` directly, and a focus row does not disappear because a tick
    finished it. So draining the continuation store changed which SOURCE answered and not what the
    next tick was handed: the identical id, the identical prose, from the other door.

    Row 2 is what keeps this from being a way to lose work: a seat that re-orients and still names
    the row is restating it, and the retirement must spend.

    MUTATION: drop the `finished` set from `_retired_ids` and row 1 fires.
    """
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "d")
    delivery_lane.retire_continuation(FOCUS_ROW["id"])

    _orientation(monkeypatch, orientation_now)
    offered = delivery_lane.next_item(path=claims)

    assert (offered is not None and offered["id"] == FOCUS_ROW["id"]) is expect_offered, offered


def test_a_retired_entry_is_still_READABLE_because_a_silent_filter_is_how_this_store_lies(
    store, monkeypatch
):
    """It is in neither `live()` nor `expired()`. If it printed nowhere, a finish would be
    indistinguishable from a store that had lost a write -- and `expired()` would report the
    project's only working handoff as "written and never taken; that is the drag", which is
    literally what this module did for a day.

    MUTATION: make `retire` call `drop` and this fires on the `retired()` assertion -- and so do
    the partition's row 1 and the executor leg, because deleting the entry restores the whole
    defect rather than only its reporting. Make `expired()` stop filtering and it fires on the
    drag assertion alone.
    """
    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "d")
    delivery_lane.retire_continuation(FOCUS_ROW["id"])

    reported = seat_continuation.retired()
    assert [i["id"] for i in reported] == [FOCUS_ROW["id"]]
    assert reported[0]["retired_at_orientation"] == ORIENTATION
    assert seat_continuation.retirement_orientation(FOCUS_ROW["id"]) == ORIENTATION
    # Six hours on, the entry is stale by the clock -- and it must NOT be reported as the drag.
    stale = float(reported[0]["written_at"]) + seat_continuation.STALE_AFTER_SECONDS + 1
    assert [i["id"] for i in seat_continuation.expired(now=stale)] == [], (
        "a finished continuation is being reported as work nobody took"
    )


@pytest.mark.parametrize("orientation_now,expect_offered", [
    (ORIENTATION, False),   # finished under the orientation still in force
    (LATER, True),          # the seat oriented again and STILL names it: offer it
])
def test_a_focus_row_NEVER_HANDED_OVER_is_discharged_by_release_or_the_draw_never_stops(
    store, monkeypatch, tmp_path, orientation_now, expect_offered
):
    """The same partition as the focus-route test above, for a row the PROMOTER NEVER TOUCHED.

    WHY THE CONTROL ABOVE COULD NOT SEE THIS. Every test in this file opens with
    `hand_off_focus`, so every id under test has a continuation entry for `retire` to mark. That
    is not the live population: `_focus` reads `DIRECTION.yaml` DIRECTLY, so a focus row can be
    drawn without ever passing the promoter, and `retire` -- whose subject is an ENTRY -- returns
    False with nothing to mark. `_retired_ids` names this limit in its own docstring and then
    argues it is not reachable in practice, because "every id that reaches Lane 0 through the
    promoter has an entry". Measured against `direction.unreachable_focus` on 2026-09-15, ALL FOUR
    offerable focus rows had no entry. The stated cover is the empty set.

    WHAT IT COST, and it is why this is a defect and not a tidiness fix.
    `the-blind-envelope-the-reader-gets-is-the-one-the-arms-were-re-run-for` was delivered by
    `5421e028e`, released, redrawn 45 minutes later; that tick re-derived it as already done and
    released again; it was redrawn a THIRD time 25 minutes after that, still carrying the pre-land
    measurement as a present-tense fact. Two invocations to establish that a landed thing landed.

    Row 2 is the leg that stops this becoming a veto over the director's focus list: the tombstone
    is keyed to the orientation, so a seat that re-orients and still names the row gets it back.
    Without it this control would pass with a `--release` that silenced an item forever, which is
    a worse failure than the re-offer it fixes.

    MUTATIONS RUN, with the PREDICTION I wrote first and what actually happened, kept side by side
    because two of the three predictions were wrong and a prediction filed after the answer is not
    a prediction:

      * drop the `retire_focus_row` fallback from `retire_continuation` (restore the defect).
        PREDICTED row 1 red, row 2 green. GOT BOTH ROWS RED, plus the tombstone test -- because
        the `retire_continuation(...) is True` assertion sits BEFORE the orientation switch and so
        belongs to neither row. Right kill, wrong reason: this mutation does not demonstrate the
        partition, and I had claimed it did;
      * have `retire_focus_row` omit `retired_at_orientation`. PREDICTED row 1 green, row 2 red
        ("silenced for good"). GOT THE OPPOSITE -- row 1 RED, row 2 green. An unstamped tombstone
        fails `_retired_ids`' `== current_orientation()` test, so the row is never discharged at
        all rather than discharged forever. The failure direction of a missing stamp is fail-OPEN,
        and I had it backwards;
      * have `retire_focus_row` write `written_at: time.time()` instead of 0.0 -> both rows green.
        PREDICTED and CONFIRMED an equivalence: `retired_at` alone already excludes the tombstone
        from `live()`, so the second leg is BELT-AND-BRACES, not load-bearing. Established rather
        than assumed to be the flattering answer;
      * drop the `== current_orientation()` clause from `_retired_ids` (the retirement never
        spends) -> ROW 2 RED, row 1 green. THIS is the mutation that proves the partition, and it
        is the one I had not thought to run: it is the only one that kills row 2 alone, so without
        it row 2 would be a leg nothing could show to be reachable.
    """
    claims = tmp_path / "claims.json"
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", claims)
    _orientation(monkeypatch, ORIENTATION)

    # NO `hand_off_focus`. This is the whole point: the row reaches the draw straight from
    # `DIRECTION.yaml`, which is how all four live rows reach it.
    assert seat_continuation.live() == [], "the fixture handed something over; the case is void"
    drawn = delivery_lane.next_item(path=claims)
    assert drawn is not None and drawn["id"] == FOCUS_ROW["id"], (
        "POISON ROUND: the row must be offerable BEFORE the discharge, or every leg below passes "
        "on an item nothing was ever going to hand out"
    )

    assert delivery_lane.retire_continuation(FOCUS_ROW["id"]) is True, (
        "a tick that says it finished a focus row got no discharge at all"
    )

    _orientation(monkeypatch, orientation_now)
    offered = delivery_lane.next_item(path=claims)
    assert (offered is not None and offered["id"] == FOCUS_ROW["id"]) is expect_offered, offered


def test_a_focus_row_tombstone_SAYS_WHAT_IT_IS_and_never_reads_as_a_continuation_that_ran(
    store, monkeypatch
):
    """The objection `_retired_ids` raises against this repair is that a discharge must not report
    work it did not do -- "retired the continuation" about an id no continuation ever held. That
    objection is to the NAMING and it is correct, so the record carries `focus_row_tombstone` and
    prose saying it was never handed over.

    It must also never leak back into the offer, which is the defect this exists to end arriving
    through the store built to stop it.

    MUTATION: have `retire_focus_row` omit `retired_at` and this fires on both the `live()` leg and
    the `retired()` leg -- the tombstone becomes an offerable continuation with no `what` a seat
    ever wrote.
    """
    _orientation(monkeypatch, ORIENTATION)
    assert delivery_lane.retire_continuation(FOCUS_ROW["id"]) is True

    reported = seat_continuation.retired()
    assert [i["id"] for i in reported] == [FOCUS_ROW["id"]]
    assert reported[0]["focus_row_tombstone"] is True, (
        "nothing distinguishes this from a continuation that was handed over and run"
    )
    assert reported[0]["retired_at_orientation"] == ORIENTATION
    assert seat_continuation.live() == [], "a tombstone is being offered as work"
    assert seat_continuation.expired() == [], (
        "a tombstone is being reported as the drag -- work the seat wrote and nobody took"
    )
    # RE-RELEASING MUST NOT MINT A SECOND ONE: the first finish is the one whose orientation says
    # when the work was actually done, and a duplicate would let a later release move that stamp.
    assert delivery_lane.retire_continuation(FOCUS_ROW["id"]) is False
    assert len(seat_continuation.retired()) == 1
    # AND THE DISCHARGE MUST SAY WHICH ONE IT DID, or it makes the false claim `_retired_ids`
    # objects to -- "retired the continuation" about an id no continuation ever held.
    assert seat_continuation.retirement_is_focus_row_tombstone(FOCUS_ROW["id"]) is True


def test_a_tombstone_is_written_ONLY_for_an_id_DIRECTION_YAML_ACTUALLY_NAMES(store, monkeypatch):
    """THE FAIL-OPEN THE FIRST DRAFT OF THIS REPAIR SHIPPED, caught by the commit gate rather than
    by me, and controlled here so it cannot come back.

    That draft fell back to a tombstone for ANY id `retire` did not know. So `--release` on a TYPO
    wrote a tombstone and reported success -- and the exit code that means "the lane cannot see
    your work" would have fired zero, which is the one way to train the next tick to ignore it.
    `test_release_discharges_the_offer_and_the_claim_over_the_whole_partition` row 4 went red and
    was right to: a discharge that fires on everything passes every test of a discharge.

    The offerable focus list is exactly the population that can be RE-DRAWN, and a re-draw is the
    only thing a tombstone saves anything from. An id nobody will offer needs no tombstone.

    MUTATION: drop the `unreachable_focus` membership test from `retire_continuation` and this
    fires -- as does row 4 of the partition test in `test_seat_continuation.py`, which is where the
    defect was actually caught.
    """
    _orientation(monkeypatch, ORIENTATION)
    assert delivery_lane.retire_continuation("an-id-no-direction-file-has-ever-named") is False
    assert seat_continuation.retired() == [], (
        "a release on an id DIRECTION.yaml does not name minted a tombstone, so a typo now "
        "reports success and the refusal that means 'the lane cannot see your work' is spent"
    )
    # The control leg: the SAME call for an id the focus list DOES name still discharges.
    assert delivery_lane.retire_continuation(FOCUS_ROW["id"]) is True


def test_the_EXECUTORS_own_discharge_retires_rather_than_deletes_and_a_second_one_still_counts(
    store, monkeypatch
):
    """THE OTHER MOUTH. `seat_executor.seat_continuation_drop` runs at turn end and deleting there
    would undo the retirement just as `--release` did -- one hole closed and one left open is how
    this class survives a fix.

    The second assertion is the one that stops a true statement being reported as a false one: the
    doorbell tells every tick to run `--release` itself, so by turn end the entry is ALREADY
    retired, and a plain `retire()` returning False would send the caller to its `NO HANDOFF TO
    DROP` line -- whose words are "no continuation record held this id".

    MUTATION: return `bool(seat_continuation.retire(...))` alone and the second assertion fires.
    """
    from background import seat_executor

    _orientation(monkeypatch, ORIENTATION)
    delivery_lane.hand_off_focus(FOCUS_ROW["id"], "d")

    assert seat_executor.seat_continuation_drop(FOCUS_ROW["id"]) is True
    assert [i["id"] for i in seat_continuation.live()] == []
    assert seat_continuation.retirement_orientation(FOCUS_ROW["id"]) == ORIENTATION
    assert seat_executor.seat_continuation_drop(FOCUS_ROW["id"]) is True, (
        "a turn ending after its own --release is reported as having found no record"
    )
