"""A hand-written `premise_spent` explained EVERY later window of the same id, for ever.

THE DEFECT, measured on this lane's live ledger 2026-09-19. `_disposition` opens with two
hand-written dispositions and the docstring above them argues the across-windows fail-open in so
many words -- *"a credited id that is DRAWN AGAIN and lands nothing has both the credit and a
genuine second miss... the instant is therefore compared against THIS draw"*. The instant was
compared for `landed_under`. For `premise_spent`, tested one branch EARLIER, the condition was the
presence of a commit and nothing else. So the fail-open the paragraph names lived in the branch the
paragraph sits under, and the guard read as covering both because it was written between them.

THE INSTANCE THAT SURFACED IT is a delivery-lane id whose premise was stated spent at 04:37:43Z and
which was RE-DRAWN 216 seconds later at 04:41:19Z. The new window inherited the old window's excuse:
whatever that second window did or failed to do, the reader was going to be shown a commit from
before it started. One sentence, written once, would have silenced every future draw of that id.

WHY IT IS THE EXPENSIVE DIRECTION rather than untidy. The two readings want opposite actions, which
is this partition's whole purpose: a real miss says *draw it again, it is workable*; a spent premise
says *there was nothing left to deliver*. A stale credit converts the first into the second silently
and for ever, and the row it happens to is the row a seat has already spent turns on -- an id gets
re-drawn precisely because it keeps not landing.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ROW: **a hand-written disposition explains the window it was
stated in, and never a later one.** No live id, sha or count appears below. The live row that
surfaced it is described in the paragraphs above as history and is not asserted anywhere.

MUTATIONS (each must fire, and which test catches it):
  (a) drop `_stated_at(spent) >= drawn` from the `premise_spent` branch -- the defect itself;
      `..._A_STATED_PREMISE_DOES_NOT_EXPLAIN_THE_NEXT_WINDOW` goes red on its second leg;
  (b) return `PREMISE_SPENT` whenever a commit is present, i.e. make the guard vacuous the other
      way by never crediting -- the SAME test's first leg goes red, because both readings are
      asserted over ONE row and a guard that refuses everything fails the partition;
  (c) flip to `>` or to `<=` -- `..._THE_WINDOW_IS_CLOSED_AT_ITS_OWN_DRAW_INSTANT` goes red, from
      one side or the other, because its two legs straddle the boundary by one second;
  (d) make `_stated_at` return `inf`, or any positive default, for a row that will not say when --
      `..._SILENCE_ABOUT_WHEN_IS_NEVER_A_CREDIT` goes red on both its legs;
  (e) make `_stated_at` RAISE on an unparseable stamp instead of answering 0.0 -- the same test
      goes red on its second leg, since a disposition reader that crashes on a hand-edited row
      takes the whole orientation brief with it;
  (f) restore the guard on `premise_spent` but drop it from `landed_under` --
      `..._BOTH_HAND_WRITTEN_DISPOSITIONS_OBEY_THE_SAME_RULE` goes red. It is asserted as one
      property over both branches precisely because the defect was one branch having it.
"""

import pytest

from background import delivery_lane as dl

NOW = 1789000000.0
#: Two windows on ONE id: the second is drawn an hour after the first, which is the shape the
#: guard exists for. Every instant below is relative to these, never to a live row.
FIRST_DRAW = NOW - 4 * 3600
SECOND_DRAW = FIRST_DRAW + 3600


def _row_stated_in_its_first_window(**stamp):
    """A row whose premise was stated spent DURING its first window, drawn twice.

    The `premise_spent` dict is built the way `note_premise_spent` builds it -- commit, reason AND
    `at` -- because that producer is the only writer of the field and has stamped all three since
    the field existed. A fixture that omitted `at` would be asserting a shape no producer can make,
    which is how this defect stayed invisible: the two partition controls that already cover
    `PREMISE_SPENT` both build the field by hand without an instant.
    """
    spent = {"commit": "0" * 40, "reason": "the work was already on origin/main when this was drawn"}
    spent.update(stamp)
    return {"first_drawn_at": FIRST_DRAW, "last_drawn_at": FIRST_DRAW, "premise_spent": spent}


def test_A_STATED_PREMISE_DOES_NOT_EXPLAIN_THE_NEXT_WINDOW():
    """One row, two windows, two different answers -- which no constant reading can produce.

    THE PARTITION IS ASSERTED OVER A SINGLE ROW ON PURPOSE. A guard that credited nothing would
    pass any test that only checked the stale window, and a guard that credited everything would
    pass any test that only checked the fresh one. Both legs sit on the same `premise_spent` dict
    and differ ONLY in which draw instant they are read against, so the reading being tested is
    the window comparison itself and not the presence of the field.
    """
    row = _row_stated_in_its_first_window(at=FIRST_DRAW + 60)

    # Stated inside the window it explains: it explains it.
    own = dl._disposition(dict(row), FIRST_DRAW, focus_id="an-id-drawn-twice")
    # The SAME sentence, against a window that opened after it was written: it explains nothing.
    later = dl._disposition(dict(row), SECOND_DRAW, focus_id="an-id-drawn-twice")

    assert own["disposition"] == dl.PREMISE_SPENT
    assert later["disposition"] != dl.PREMISE_SPENT
    # And the second window falls to the LOUD residual rather than a quieter derived reading:
    # nothing about this row names a commit, a sibling or a start, so no join can answer it.
    assert later["disposition"] == dl.NOT_DONE


def test_THE_WINDOW_IS_CLOSED_AT_ITS_OWN_DRAW_INSTANT():
    """The boundary, straddled by one second, so a `>`/`>=`/`<=` slip cannot pass both legs.

    A disposition stated at the very instant of the draw belongs to that draw: the draw is when the
    window OPENS, and a sentence written then is written about it. One second earlier and it was
    written about whatever came before.
    """
    on_the_instant = _row_stated_in_its_first_window(at=FIRST_DRAW)
    one_second_before = _row_stated_in_its_first_window(at=FIRST_DRAW - 1)

    assert dl._disposition(dict(on_the_instant), FIRST_DRAW,
                           focus_id="x")["disposition"] == dl.PREMISE_SPENT
    assert dl._disposition(dict(one_second_before), FIRST_DRAW,
                           focus_id="x")["disposition"] != dl.PREMISE_SPENT


def test_SILENCE_ABOUT_WHEN_IS_NEVER_A_CREDIT():
    """A row that will not say WHEN it was stated explains no window, and does not crash the reader.

    Both halves matter and they pull in opposite directions. A missing or unreadable `at` must not
    be read as "recent enough" -- that is the fail-open in its purest form, one unparseable field
    excusing an id for ever. It must equally not RAISE: `_disposition` is what the orientation brief
    calls to explain every swept row, so a hand-edited row that crashed it would take the brief's
    whole reading with it, which is a louder failure than the one being prevented.
    """
    never_stamped = _row_stated_in_its_first_window()
    unparseable = _row_stated_in_its_first_window(at="the twenty-third")

    assert dl._disposition(dict(never_stamped), FIRST_DRAW,
                           focus_id="x")["disposition"] != dl.PREMISE_SPENT
    assert dl._disposition(dict(unparseable), FIRST_DRAW,
                           focus_id="x")["disposition"] != dl.PREMISE_SPENT


@pytest.mark.parametrize("disposition", (dl.PREMISE_SPENT, dl.LANDED_ELSEWHERE))
def test_BOTH_HAND_WRITTEN_DISPOSITIONS_OBEY_THE_SAME_RULE(disposition):
    """The rule is about hand-written dispositions as a CLASS, not about one branch of two.

    This is the control the defect was hiding from. `landed_under` carried the window comparison
    and `premise_spent` did not, and nothing anywhere asked whether the two agreed -- so the guard
    on one read, to every later reviewer, as a property of both. Parameterised over the pair so
    that removing it from EITHER branch reds, and so that a third hand-written disposition added
    later has an obvious place to be held to the same rule.
    """
    if disposition == dl.PREMISE_SPENT:
        fresh = _row_stated_in_its_first_window(at=FIRST_DRAW + 60)
        stale = _row_stated_in_its_first_window(at=FIRST_DRAW + 60)
    else:
        # `landed_under` states its instant in `last_landing_at`, which is the same question asked
        # of the field that branch reads: WHEN was this credit earned, and for which window.
        base = {"first_drawn_at": FIRST_DRAW, "last_drawn_at": FIRST_DRAW,
                "landed_under": "some-other-drawn-id", "last_landing_paths": ["tools/x.py"]}
        fresh = {**base, "last_landing_at": FIRST_DRAW + 60}
        stale = {**base, "last_landing_at": FIRST_DRAW + 60}

    assert dl._disposition(dict(fresh), FIRST_DRAW, focus_id="x")["disposition"] == disposition
    assert dl._disposition(dict(stale), SECOND_DRAW, focus_id="x")["disposition"] != disposition
