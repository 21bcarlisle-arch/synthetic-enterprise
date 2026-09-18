"""A claim may not be released while the writer holding it is still inside its own bound.

THREE CLOCKS THAT HAD NEVER BEEN COMPARED (director, 2026-09-18), and the comparison is the whole
finding. They live in three modules and nothing anywhere read more than one of them:

  * `seat_executor.SESSION_TIMEOUT_SECONDS` -- 90 minutes, enforced by systemd. A bounded turn may
    legitimately run this long, and the writer inside it cannot be told its claim has gone.
  * `seat_work_in_hand.STALE_AFTER_SECONDS` -- the cross-lane path guard's store deadline. It was
    45 minutes, INSIDE the bound above, and `seat_executor` claims its work id in that store at
    turn start with `paths=[]` while `delivery_lane.record_landing` binds paths into the DELIVERY
    store only. So that claim's observable progress is its own `claimed_at` for the whole turn
    however much the turn lands, and it was released at half-time, every time.
  * `delivery_lane.CLAIM_STALE_SECONDS` -- 100 minutes, and correctly outside the bound. It was
    also IGNORED: `overlapping_claims` read both stores and swept both with the 45.

WHAT IT COST, twice measured and both in the 2,700..6,000 band the 45 opened:

  * a writer that started 08:36 had its finished work re-handed to a second writer at 09:47 --
    4,260 seconds, and two writers were given one id;
  * pid 2436269 was alive at 4,182 seconds of its 5,400-second bound with its claim already swept
    and its completed repair published to the next reader as undone.

THE ORDERING IS THE PROPERTY, NOT THE NUMBERS. Every leg here is keyed to the ordering of the three
bounds or to a behaviour that follows from it; none pins a constant to today's value. Change any of
the three and this stays green. Move one ACROSS another and it reds, which is the only event that
can reopen the defect.

IT WAS WRITTEN DOWN AS AN OBSTACLE AND NEVER AS A DEFECT, which is why it stood. `tests/tools/
test_a_promotion_binds_its_landing_to_the_claim.py` builds its fixture claim "TWO MINUTES AND NOT
AN HOUR, because `refuse_if_duplicated` sweeps every store it reads with `seat_work_in_hand`'s own
45-minute deadline rather than the delivery lane's 100" -- an exact description of the bug, in the
repository, working around it.
"""
from __future__ import annotations

import json

import pytest

import background.delivery_lane as dl
import background.seat_work_in_hand as claims_mod
from background.seat_executor import SESSION_TIMEOUT_SECONDS

NOW = 1_700_000_000.0

#: A path no commit touches, so `_last_commit_time_touching` answers 0.0 and `last_progress` is the
#: claim itself. A REAL path would hand the claim the shared tree's own commit clock, and every leg
#: below would then be measuring what the other four lanes committed this morning.
UNTOUCHED = "tools/no_commit_has_ever_touched_this_path_it_exists_to_pin_a_clock.py"


def _at(age_seconds: float) -> dict:
    return {"claimed_at": NOW - age_seconds, "note": "under test", "paths": [UNTOUCHED]}


@pytest.fixture()
def stores(tmp_path, monkeypatch):
    """A delivery store and a seat store, paired with the deadlines the live code pairs them with.

    Monkeypatched over `claim_stores` so BOTH readers -- `rival_claims` here and
    `overlapping_claims` in the other module -- reach these two files and not the live ones.
    """
    delivery = tmp_path / "delivery_claims.json"
    seat = tmp_path / "seat_claims.json"
    for store in (delivery, seat):
        store.write_text("{}")
        dl._ledger_path(store).write_text("{}")
    paired = [(delivery, float(dl.CLAIM_STALE_SECONDS)),
              (seat, float(claims_mod.STALE_AFTER_SECONDS))]
    monkeypatch.setattr(dl, "claim_stores", lambda: paired)
    return paired


@pytest.fixture(autouse=True)
def _no_live_escalations(monkeypatch):
    """A sweep files into `docs/staging/`. A test that sweeps must not write the shared tree."""
    import background.alarm_repetition as alarm

    monkeypatch.setattr(alarm, "escalate", lambda *a, **k: None)


def _hold(store, work_id, *, age_seconds):
    rows = json.loads(store.read_text())
    rows[work_id] = _at(age_seconds)
    store.write_text(json.dumps(rows))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE ORDERING ITSELF
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_NO_CLAIM_STORE_IS_SWEPT_INSIDE_A_BOUNDED_TURN():
    """The defect in one line: a deadline shorter than the writer's own lifetime.

    A sweep that fires at 45 minutes against a 90-minute turn is not measuring a stall. By
    construction the claim it releases is held by a process that is still running, still writing,
    and has no way to hear about it -- and the release hands the same id to a second writer.

    MUTATION: put `STALE_AFTER_SECONDS` back to `45 * 60` and this fires. So does lowering
    `CLAIM_STALE_SECONDS` under the bound, or raising `SESSION_TIMEOUT_SECONDS` over either
    deadline -- which is the direction nobody would think to check, because the number that moved
    would be in a third module.
    """
    assert SESSION_TIMEOUT_SECONDS <= claims_mod.STALE_AFTER_SECONDS, (
        "the cross-lane path guard releases claims a live bounded turn is still holding"
    )
    assert SESSION_TIMEOUT_SECONDS <= dl.CLAIM_STALE_SECONDS, (
        "the delivery lane releases claims a live bounded turn is still holding"
    )


def test_THE_DELIVERY_LANES_DEADLINE_IS_THE_LONGER_OF_THE_TWO():
    """The stores are ordered as well as floored, and the order is the lane's stated design: the
    delivery lane's work is the multi-hour class and the cross-lane guard's is one turn's.

    STRICT, so the two can still DISCRIMINATE. Equal deadlines would make every per-store leg below
    vacuously true while reading as green -- the band those legs measure in would be empty.

    MUTATION: make them equal, or swap them, and this fires.
    """
    assert claims_mod.STALE_AFTER_SECONDS < dl.CLAIM_STALE_SECONDS


def test_ALL_THREE_STATES_OF_A_CLAIMS_LIFE_ARE_REACHABLE(stores):
    """ONE control over the WHOLE partition, because a guard that refuses everything passes every
    per-branch leg. Three ages, three different verdicts, in one assertion:

      * inside the bound        -- neither store stale;
      * between the deadlines   -- the seat store stale, the delivery store not;
      * past both               -- both stale.

    The middle state is the band the two measurements landed in, and it only EXISTS because the
    deadlines differ. If a future change collapses it, this reds here rather than silently turning
    the per-store legs below into assertions about nothing.
    """
    delivery, seat = stores[0][0], stores[1][0]
    inside = SESSION_TIMEOUT_SECONDS - 1
    between = (claims_mod.STALE_AFTER_SECONDS + dl.CLAIM_STALE_SECONDS) / 2
    past = dl.CLAIM_STALE_SECONDS + 1

    def stale_at(store, deadline, age):
        _hold(store, "w", age_seconds=age)
        return bool(claims_mod.stale_claims(path=store, now=NOW, stale_after=deadline))

    verdicts = {
        (label, store_label): stale_at(store, deadline, age)
        for label, age in (("inside", inside), ("between", between), ("past", past))
        for store_label, (store, deadline) in (("delivery", (delivery, dl.CLAIM_STALE_SECONDS)),
                                               ("seat", (seat, claims_mod.STALE_AFTER_SECONDS)))
    }

    assert verdicts == {
        ("inside", "delivery"): False, ("inside", "seat"): False,
        ("between", "delivery"): False, ("between", "seat"): True,
        ("past", "delivery"): True, ("past", "seat"): True,
    }, verdicts


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE SWEEP THAT APPLIED THE WRONG STORE'S CLOCK
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_THE_DUPLICATION_CHECK_SWEEPS_EACH_STORE_ON_ITS_OWN_DEADLINE(stores):
    """`overlapping_claims` is the only thing that sweeps on the hot path, and it swept both
    stores with this module's own number. So the delivery lane's 100 minutes was decorative: its
    claims were released at 45 by the duplication check before its own sweep could ever see them.

    The claim here is aged into the band between the two deadlines. It must SURVIVE -- and it must
    still be reported as holding the path, because surviving invisibly would be the same defect
    with the evidence removed.

    MUTATION: drop the `stale_after=deadline` argument from the sweep inside `overlapping_claims`
    and this fires.
    """
    delivery = stores[0][0]
    age = (claims_mod.STALE_AFTER_SECONDS + dl.CLAIM_STALE_SECONDS) / 2
    _hold(delivery, "a-delivery-item-mid-turn", age_seconds=age)

    clash = claims_mod.overlapping_claims([UNTOUCHED], now=NOW)

    assert clash == {"a-delivery-item-mid-turn": [UNTOUCHED]}, (
        "a delivery claim inside its own deadline was swept by the duplication check"
    )
    assert "a-delivery-item-mid-turn" in json.loads(delivery.read_text()), (
        "the claim was removed from the store, not merely under-reported"
    )


def test_THE_SEAT_STORE_KEEPS_THE_SHORTER_DEADLINE_IT_DECLARES(stores):
    """The mirror, and the reason the leg above is not just "sweep less". A seat-store claim in the
    same band IS past its own deadline and must still be released -- otherwise the repair would
    have bought the delivery lane its clock by giving every store the longest one, and a dead
    cross-lane writer would hold a path for an extra hour.

    MUTATION: hand every store `CLAIM_STALE_SECONDS`, or floor every deadline at the longest, and
    this fires.
    """
    seat = stores[1][0]
    age = (claims_mod.STALE_AFTER_SECONDS + dl.CLAIM_STALE_SECONDS) / 2
    _hold(seat, "a-cross-lane-claim-that-stopped", age_seconds=age)

    assert claims_mod.overlapping_claims([UNTOUCHED], now=NOW) == {}
    assert json.loads(seat.read_text()) == {}, "the stale claim should have been swept away"


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE HOLDER THE RIVAL CHECK EXCLUDED BY THE ITEM'S OWN ID
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_A_LIVE_HOLDER_OF_THIS_VERY_ID_IN_THE_OTHER_STORE_IS_NAMED(stores):
    """The second half of the direction: `rival_claims` must be able to see the holder it excludes
    by the item's own id.

    `draw()` claims into THIS lane's store and nowhere else, so a row under the same id in the seat
    store was written by somebody else -- an interactive seat, or a live `seat_executor` turn,
    which claims in both. And `next_item` filters `held()` on the delivery store ALONE, so the draw
    itself cannot see that holder either. Excluding by id across every store made the one remaining
    instrument blind in exactly the place the draw already was.

    MUTATION: exclude `mine` in every store rather than only in the one the draw claimed in, and
    this fires.
    """
    seat = stores[1][0]
    mine = "reconcile-the-three-clocks-that-have-never-been-compared"
    _hold(seat, mine, age_seconds=60)

    rivals = dl.rival_claims({"id": mine, "what": "reconcile the clocks"}, now=NOW, stores=stores)

    assert mine in rivals, "a live holder of this exact id was reported as no rival at all"
    assert "ALREADY HELD" in " ".join(rivals[mine])
    assert seat.name in " ".join(rivals[mine]), (
        "the note must say WHICH store holds it -- a claim record carries no holder field, so the "
        "store is the only thing that says which writer put the row there"
    )


def test_THE_DRAWS_OWN_CLAIM_IN_ITS_OWN_STORE_IS_STILL_NOT_A_RIVAL(stores):
    """The pass branch, and without it the leg above is a guard that fires on everything.

    `draw()` claims before it composes the doorbell, so the item's own row is ALWAYS in this lane's
    store by the time this runs. Reporting that would put a rival note on every single draw, which
    is the noise direction and the one that trains a reader to skip the line.

    MUTATION: report a same-id row in any store, including the draw's own, and this fires.
    """
    delivery = stores[0][0]
    mine = "reconcile-the-three-clocks-that-have-never-been-compared"
    _hold(delivery, mine, age_seconds=1)

    assert dl.rival_claims({"id": mine, "what": "reconcile the clocks"},
                           now=NOW, stores=stores) == {}


def test_THE_SAME_ID_HOLDER_SURVIVES_THE_NO_OTHER_CLAIMS_SHORT_CIRCUIT(stores):
    """`rival_claims` returns early when there is nothing else to compare against, because the word
    and path legs both cost a `git ls-files`. The same-id leg needs neither.

    AND THE EARLY RETURN IS ITS ORDINARY CASE, which is what makes this worth a leg of its own: the
    commonest way to be the only live holder of an id is for there to be no other live claims at
    all. A same-id holder reported only when some UNRELATED third claim happened to exist would be
    a branch that looks implemented and is unreachable when it matters.

    MUTATION: return `{}` from the short circuit and this fires while the leg above still passes.
    """
    seat = stores[1][0]
    mine = "reconcile-the-three-clocks-that-have-never-been-compared"
    _hold(seat, mine, age_seconds=60)

    assert json.loads(stores[0][0].read_text()) == {}, "no other claim exists anywhere"
    assert mine in dl.rival_claims({"id": mine}, now=NOW, stores=stores)


def test_A_STALE_HOLDER_OF_THIS_ID_IS_NOT_A_LIVE_RIVAL(stores):
    """Bounded in the other direction. The row has to be LIVE on its own store's deadline; a claim
    whose writer died an hour past its lease is not somebody holding the work, and saying it is
    would put a permanent note on every id the seat store has ever seen.

    MUTATION: drop the `work_id in stale` test and this fires.
    """
    seat = stores[1][0]
    mine = "reconcile-the-three-clocks-that-have-never-been-compared"
    _hold(seat, mine, age_seconds=claims_mod.STALE_AFTER_SECONDS + 1)

    assert dl.rival_claims({"id": mine}, now=NOW, stores=stores) == {}
