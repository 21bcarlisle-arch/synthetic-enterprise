"""FOUR INVOCATIONS WERE SPENT ARRIVING BEFORE THE FILE THEY WERE SENT TO READ COULD EXIST.

THE DEFECT. A Lane 0 item that sends a tick to read a long-running run's artefact carries the
instant that artefact starts existing:

    DO NOT START BEFORE 12:45 on 2026-09-18

**Nothing read it.** It was prose inside a work description, and `next_item` -- the thing that
decides which item a tick is handed -- had never looked at the text at all. The item was drawn at
00:37, at 02:35 and at 03:12 on 2026-09-18, every one of them hours before the artefact existed.
Each of those turns could do nothing except re-measure the ETA and hand the item straight back, and
each of them filed a finding saying so. The third wrote the sentence this suite exists to answer:

    "That guard is prose inside a work description. Nothing reads it, so nothing can honour it. It
    has now failed three times in a row, which is as much evidence as a rule of that shape can
    produce. This is a finding about the draw mechanism, not about any of the three invocations."

WHY IT IS WORSE THAN NO GUARD, which is the part that makes it worth a mechanism rather than a
deletion: a precondition that is stated and unenforced reads, every time it fails, as a seat that
ignored its own instruction. The failure is attributed to judgement when it belongs to wiring.

THE PROPERTY, keyed to the property and not to today's stamp: **an item states an instant before
which it must not be drawn, and the draw honours it -- by SKIPPING that item and continuing to
offer the rest, never by falling silent.**

THE SECOND HALF OF THAT SENTENCE IS THE WHOLE CONTROL. A `next_item` that returns `None` for
everything honours "the embargoed item is not returned" perfectly, and it is a far worse machine
than the one being repaired: it trades one wasted invocation for every invocation in the window.
That is this project's most-repeated control failure -- a guard that refuses everything passing
every test of whether it refuses correctly -- so nothing here asserts a withholding without
asserting, in the same breath and over the same call, that a sibling still gets through and that
the held item is released the moment its instant passes.
"""
from __future__ import annotations

import datetime
import time

import pytest

from background import delivery_lane, seat_continuation


def _stamp(when: float, verb: str = "DRAW") -> str:
    """The embargo as the seat writes it, for an instant chosen by the caller.

    Built from `when` rather than typed as a literal so the suite cannot rot into a test of a date
    in the past -- a stamp hard-coded to 2026-09-18 stops embargoing anything on 2026-09-19 and
    every leg below would go green for the wrong reason.
    """
    return datetime.datetime.fromtimestamp(when).strftime(
        f"DO NOT {verb} BEFORE %H:%M on %Y-%m-%d")


@pytest.fixture
def now() -> float:
    """A fixed instant on a whole minute.

    The stamp grammar resolves to minutes, so an instant with seconds on it makes `_stamp(now)`
    round DOWN to an embargo that has already expired -- which would quietly turn the held leg
    below into a test of nothing.
    """
    return float(int(time.time() // 60) * 60)


@pytest.fixture
def lane(tmp_path, monkeypatch, now):
    """Two live continuations: an embargoed one FIRST, a free sibling behind it.

    The order is load-bearing and is the production shape. `live()` returns continuations in the
    order they were written and `next_item` takes the first eligible one, so the embargoed item
    stands at the head of the queue -- exactly where a filter that stops the walk instead of
    skipping past it would shut the lane.

    Both stores are redirected, as `test_a_draw_is_not_a_delivery` explains: `next_item` calls
    `seat_continuation.live(now=now)` with no path, so patching the module attribute is the only
    thing that keeps this off the real store.
    """
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off(
        "read-the-twelve-seed-family",
        what=("Read the next12 family as its own twelve-seed family. "
              + _stamp(now + 3600)
              + ": the artefact does not exist until then."),
        why="The twelve are the independent test of the published negative selection sign.",
        done_means="the twelve's mean, sem and sems-from-zero are published on their own terms.",
        now=now,
    )
    seat_continuation.hand_off(
        "decompose-the-negative-selection-leg",
        what="Decompose the -959.78 from the per-account arm values already in the artefacts.",
        why="A negative with a named mechanism is a thing that can be fixed.",
        done_means="the accounts and the mechanism are named.",
        now=now,
    )
    return tmp_path / "claims.json"


def test_the_embargo_withholds_one_item_and_the_lane_keeps_delivering(lane, now):
    """THE WHOLE PARTITION, IN ONE CONTROL, and it is written as one test on purpose.

    Three assertions that are only meaningful together:

      1. inside the window, the embargoed item is NOT what the tick is handed;
      2. inside the window, the tick is handed the SIBLING -- the lane did not fall silent;
      3. outside the window, the embargoed item is handed over, at the head of the queue where it
         has been all along.

    Split into three tests, (1) passes for a lane that delivers nothing and (3) is the only thing
    that can tell an embargo from a blacklist. Together they cannot all hold unless the filter
    skips, waits, and then releases.
    """
    held = delivery_lane.next_item(now=now, path=lane)

    assert held is not None, (
        "the lane went EMPTY inside an embargo window -- an item that cannot be started for an "
        "hour must not hold every other item shut behind it"
    )
    assert held["id"] == "decompose-the-negative-selection-leg", (
        "the embargoed item was handed out anyway, which is the defect verbatim"
    )

    released = delivery_lane.next_item(now=now + 7200, path=lane)

    assert released is not None and released["id"] == "read-the-twelve-seed-family", (
        "the embargo never expired -- it is a WAIT, not a refusal, and an item whose instant has "
        "passed must come back at the head of the queue where it was written"
    )


def test_the_focus_loop_reads_the_stamp_too(monkeypatch, tmp_path, now):
    """The OTHER source, and it is the one the live failures came through.

    `next_item` walks two stores. Filtering only the continuation loop would honour the stamp on a
    handed-off item and ignore it on the `DIRECTION.yaml` row the seat actually wrote -- and the
    three measured failures were draws against a focus row.
    """
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda _atoms: [
        {"id": "read-the-twelve-seed-family",
         "what": "Read the twelve. " + _stamp(now + 3600), "why": "independent test"},
        {"id": "decompose-the-negative-selection-leg",
         "what": "Decompose the negative leg.", "why": "thesis work"},
    ])

    held = delivery_lane.next_item(now=now, path=tmp_path / "claims.json")
    assert held is not None and held["id"] == "decompose-the-negative-selection-leg"

    released = delivery_lane.next_item(now=now + 7200, path=tmp_path / "claims.json")
    assert released is not None and released["id"] == "read-the-twelve-seed-family"


def test_both_verbs_and_both_orderings_parse(now):
    """The SAME item has been written with both verbs across successive re-drawings.

    `DO NOT START BEFORE 12:45 on 2026-09-18` and `DO NOT DRAW BEFORE 10:45 on 2026-09-18` are the
    same instruction from the same author about the same work. A grammar that honoured one of them
    would be a guard with a silent off-switch -- worse than none, because it would work on some
    turns and not others with nothing to distinguish them.
    """
    when = now + 3600
    expected = float(int(when // 60) * 60)

    for verb in ("DRAW", "START"):
        assert delivery_lane.embargoed_until({"what": _stamp(when, verb)}) == expected, verb

    iso = datetime.datetime.fromtimestamp(when).strftime(
        "DO NOT DRAW BEFORE %Y-%m-%d %H:%M")
    assert delivery_lane.embargoed_until({"what": iso}) == expected, (
        "date-first is the other way a human writes the same sentence"
    )
    assert delivery_lane.embargoed_until(
        {"what": _stamp(when).lower()}) == expected, "case is emphasis, not meaning"


def test_the_latest_of_two_stamps_wins(now):
    """An item carrying two stamps is an author restating a deadline that MOVED.

    The conservative reading of "not before X" and "not before Y" is `max` -- honouring the earlier
    one draws into precisely the window the later one was written to close. This item's own history
    is the instance: its stated floor went 10:45 -> 12:45 as the ETA was re-measured three times.
    """
    early, late = now + 3600, now + 7200

    got = delivery_lane.embargoed_until(
        {"what": _stamp(early), "done_means": _stamp(late, "START")})

    assert got == float(int(late // 60) * 60), (
        "the earlier stamp won, so the draw would fire inside the window the later one closed"
    )


def test_an_item_with_no_stamp_is_drawable_and_a_past_stamp_is_inert(lane, now):
    """THE FAIL-OPEN DIRECTION, asserted rather than assumed.

    Almost every item carries no stamp, and one that carries a stamp about a date already gone
    carries no instruction at all. Both must draw. This is the leg that stops the filter being
    tightened into something that withholds work on prose it merely failed to understand -- the
    asymmetry is that a missed stamp costs ONE invocation and is visible to the tick that reads it,
    while an invented one empties the lane and is visible to nobody.
    """
    assert delivery_lane.embargoed_until({"what": "Read the twelve. No stamp anywhere."}) is None
    assert delivery_lane.embargoed_until({"what": _stamp(now - 86400)}) is not None, (
        "a past stamp still PARSES -- it is the comparison, not the grammar, that makes it inert"
    )
    assert delivery_lane._embargoed({"what": _stamp(now - 86400)}, now) is False
    assert delivery_lane.embargoed_until({"what": "DO NOT DRAW BEFORE tea time"}) is None, (
        "an unparseable stamp must leave the item drawable, never withhold it"
    )


def test_the_reader_answers_about_both_stores_it_filters(lane, now, monkeypatch, capsys):
    """`--embargoed` is the only way a human learns why an item was not offered, and its first
    draft read ONE of the two stores `next_item` filters.

    Caught by running it against the live record instead of against this fixture: on 2026-09-18 the
    only embargoed item in the machine was a continuation, and the focus-only reader printed
    "nothing embargoed" while the stamp sat in the other store, held until 12:45. A reader that
    answers confidently about the half it knows is the same fail-silent shape as the missing guard
    it was built to explain -- so the assertion is that the reader's coverage EQUALS the draw's.
    """
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda _atoms: [])

    delivery_lane.main(["--embargoed"])

    out = capsys.readouterr().out
    assert "read-the-twelve-seed-family" in out, (
        "the reader is blind to a store the draw filters, so an embargo it honours cannot be "
        "explained to the person asking why their item was skipped"
    )
    assert "decompose-the-negative-selection-leg" not in out, (
        "an unembargoed sibling was listed as held -- the reader must name the partition, not the "
        "queue"
    )


def test_the_stamps_date_is_read_and_not_only_its_clock_time(now):
    """A time-only parse is green all day and wrong by exactly one day.

    `DO NOT DRAW BEFORE 12:45` read without its date embargoes until 12:45 TODAY, so an item held
    for tomorrow lunchtime is handed out this afternoon -- the original defect, one size smaller,
    and invisible for the twenty-three hours a day when the two readings agree.
    """
    tomorrow = now + 86400

    got = delivery_lane.embargoed_until({"what": _stamp(tomorrow)})

    assert got == float(int(tomorrow // 60) * 60)
    assert delivery_lane._embargoed({"what": _stamp(tomorrow)}, now) is True, (
        "the date was dropped, so a stamp for tomorrow stopped holding once today's clock passed it"
    )
