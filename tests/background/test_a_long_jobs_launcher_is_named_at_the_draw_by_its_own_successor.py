"""A continuation that LAUNCHES a long job must not be re-drawn while the job is still running.

THE DEFECT THIS NAMES, measured on the live store on 2026-09-18. A tick took
`re-run-the-noise-floor-over-the-09-18-book-...` (written 15:53), launched the twelve-seed floor as
a detached systemd job at 16:13, and at 16:41 handed the remainder off as
`publish-the-floor-at-18327d977-...` carrying a correct `DO NOT DRAW BEFORE 2026-09-19 09:30`
stamp. At 16:43 the draw handed out the PREDECESSOR, whose text still says "Re-run the noise floor
over the 09-18 book NOW". Obeying it launches a second copy of a sixteen-hour run over the same
twelve seeds, into the same output filename.

THE EMBARGO WENT ON THE WRONG HALF, and that is the generalisable part. Splitting a long job into
"launch it" and "read it when it lands" puts the author's attention on when the ARTEFACT exists, so
the reader gets the stamp. The launcher is the expensive one and it got nothing. `claim_dispatched`
records two earlier detached multi-hour runners re-drawn inside their own shadow; this is the
third, and the first where the claim machinery worked and the CONTINUATION store leaked instead.

WHAT EACH LEG NAMES AS ITS OWN DEFECT:

* the launcher is drawn with nothing said about its own successor — the note never fires, which is
  the 16:43 draw restated;
* a successor that DID declare the supersession still provokes a note — then the note is noise, the
  reader learns to skip it, and it protects nothing when it matters;
* the note fires on work that merely SHARES A TICK — `written_while_holding` records every claim
  held at write time, so reading it as "is a continuation of" without the rest of the partition
  would flag every unrelated handoff a busy tick ever wrote;
* the note is composed and the doorbell does not CARRY it — the failure this store has already had
  once, where a guard existed as prose nothing read;
* an unreadable store takes the draw down — `delivery_lane.draw` documents that a lane which can
  throw takes every other lane with it.
"""
from __future__ import annotations

import time

import pytest

from background import delivery_lane, seat_continuation


@pytest.fixture
def store(tmp_path):
    return tmp_path / "continuation.json"


LAUNCHER = "re-run-the-floor-so-the-error-bar-stops-refusing"
SUCCESSOR = "publish-the-floor-once-its-run-lands"


#: Entries must land INSIDE `live()`'s window or every leg here measures expiry instead of the
#: thing it names -- the first draft stamped 1970 and three legs went green for the wrong reason.
NOW = time.time()


def _hand(store, work_id, what, *, holding=(), supersedes=(), now=NOW, monkeypatch=None):
    """Write one continuation, with `written_while_holding` as a live tick would stamp it.

    The holding list is injected by replacing `_lane_work_in_hand`, which is the ONLY producer of
    that field, rather than by hand-writing the JSON. A fixture that writes the field directly
    would keep passing if `hand_off` stopped stamping it — and then the note would go silent in
    production while every leg here stayed green.
    """
    monkeypatch.setattr(seat_continuation, "_lane_work_in_hand", lambda: list(holding))
    return seat_continuation.hand_off(
        work_id, what,
        "the page publishes a spread over a book it cannot show the figure came from",
        "the floor is republished over the same book, not the caveat text edited",
        supersedes=supersedes, now=now, path=store,
    )


def _launch_then_hand_off(store, monkeypatch, *, supersedes=()):
    """The live 2026-09-18 sequence: a launcher, then its successor written while holding it."""
    _hand(store, LAUNCHER, "Re-run the noise floor over the 09-18 book NOW",
          now=NOW - 120.0, monkeypatch=monkeypatch)
    _hand(store, SUCCESSOR,
          "DO NOT DRAW BEFORE 2026-09-19 09:30. The 12-seed floor is IN FLIGHT as systemd unit "
          "longjob-floor-next12-at-head-20260918; read the artefact when it lands.",
          holding=[LAUNCHER], supersedes=supersedes, now=NOW - 60.0, monkeypatch=monkeypatch)
    monkeypatch.setattr(seat_continuation, "STORE", store)


def test_the_LAUNCHER_is_named_at_the_draw_by_the_successor_its_own_tick_wrote(
    store, monkeypatch
):
    """The 16:43 draw, replayed. MUTATION: drop the `written_while_holding` test from
    `undeclared_successors` and this fires — the launcher is offered with nothing said, and the
    tick that takes it relaunches a running sixteen-hour job."""
    _launch_then_hand_off(store, monkeypatch)

    note = delivery_lane.successor_note({"id": LAUNCHER})

    assert SUCCESSOR in note
    # The successor's own TEXT rides along, because the disposition turns on reading it and a note
    # that only names an id sends the tick to a second lookup it will skip.
    assert "IN FLIGHT" in note
    assert f"--release {LAUNCHER}" in note


def test_a_successor_that_DECLARES_the_supersession_provokes_no_note(store, monkeypatch):
    """A note that fires when the author did the right thing is noise, and a reader who learns to
    skip it is unprotected when it matters. MUTATION: delete the `supersedes` test and this fires.
    """
    _launch_then_hand_off(store, monkeypatch, supersedes=[LAUNCHER])

    assert delivery_lane.successor_note({"id": LAUNCHER}) == ""
    # ...and the launcher is not drawable at all now, which is the repair the note exists to prompt.
    assert LAUNCHER not in {i.get("id") for i in seat_continuation.live()}


def test_BOTH_sides_of_the_partition_are_reachable_on_one_store(store, monkeypatch):
    """One control over the whole partition, because a predicate that answers "no" to EVERYTHING
    passes every silence leg above and would be indistinguishable from the guard working."""
    _launch_then_hand_off(store, monkeypatch)
    fires = seat_continuation.undeclared_successors(LAUNCHER)

    _hand(store, SUCCESSOR,
          "DO NOT DRAW BEFORE 2026-09-19 09:30. The 12-seed floor is IN FLIGHT.",
          holding=[LAUNCHER], supersedes=[LAUNCHER], now=NOW - 30.0, monkeypatch=monkeypatch)
    silent = seat_continuation.undeclared_successors(LAUNCHER)

    assert fires and not silent, (
        f"the predicate must be able to answer BOTH ways on one store; got {fires=} {silent=}"
    )


def test_work_that_merely_SHARED_A_TICK_is_not_named_as_a_successor(store, monkeypatch):
    """`written_while_holding` lists every claim in hand at write time, so a tick working two
    items stamps both onto anything it writes. MUTATION: return every live entry regardless of the
    holding list and this fires — every busy tick's unrelated handoff becomes a false continuation.
    """
    _hand(store, LAUNCHER, "Re-run the noise floor over the 09-18 book NOW",
          now=NOW - 120.0, monkeypatch=monkeypatch)
    _hand(store, "wire-the-cm-levy-to-the-regulation-commons",
          "the sim-side levy reaches no commons artefact",
          holding=["some-other-item-entirely"], now=NOW - 60.0, monkeypatch=monkeypatch)
    monkeypatch.setattr(seat_continuation, "STORE", store)

    assert delivery_lane.successor_note({"id": LAUNCHER}) == ""


def test_the_DOORBELL_CARRIES_the_note_and_not_only_the_composer(store, monkeypatch):
    """The failure this store has already had once: a guard that exists, answers correctly, and
    reaches no reader. MUTATION: drop `successor_note(item)` from `doorbell`'s concatenation and
    every leg above stays green while the tick is told nothing."""
    _launch_then_hand_off(store, monkeypatch)

    text = delivery_lane.doorbell({"id": LAUNCHER, "what": "Re-run the noise floor NOW",
                                   "why": "the caveat fires"})

    assert "CONTINUATION CHECK" in text
    assert SUCCESSOR in text


def test_an_unreadable_store_costs_the_NOTE_and_never_the_DRAW(store, monkeypatch):
    """A lane that can throw takes every other lane down with it. The note's absence is visible to
    the tick that then does the work anyway; a raised exception is visible to nobody."""
    def _boom(*a, **k):
        raise OSError("the store is a directory today")

    monkeypatch.setattr(seat_continuation, "undeclared_successors", _boom)
    assert delivery_lane.successor_note({"id": LAUNCHER}) == ""
    assert "LANE 0 DELIVERY" in delivery_lane.doorbell(
        {"id": LAUNCHER, "what": "w", "why": "y"}
    )
