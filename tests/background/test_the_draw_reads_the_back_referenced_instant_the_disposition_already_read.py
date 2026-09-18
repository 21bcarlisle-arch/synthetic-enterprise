"""THE READER EXISTED, WAS TESTED, AND WAS WIRED ONLY TO THE ORGAN THAT EXPLAINS THE LOSS.

THE DEFECT. `delivery_lane._back_referenced_start` resolves the third live spelling of a draw-time
embargo -- an instant named once and then referred back to:

    The run exec'd 20:11:48, 13.0 min per arm-leg, ETA near 03:58; do not draw this before then,
    the file will not exist.

It had exactly ONE caller: `_drawn_before_stated_start`, the after-the-fact disposition that stamps
`premise_not_yet_ripe` on a window that has already closed. The draw's own guard `_embargoed` read
`_EMBARGO`, the dated grammar, and nothing else. So on 2026-09-18 the lane could say precisely why
`read-the-next12-twelve-alone-once-the-0358-run-settles` was hopeless from the moment it was handed
out at 00:07 -- and could not decline to hand it out. A whole 100-minute window, spent.

THE PROPERTY, keyed to the property and not to today's grammar: **an item states an instant before
which it must not be drawn, and the draw honours it in EVERY spelling the disposition can read.**
The sibling suite `test_an_items_own_do_not_draw_before_is_read_by_the_draw` holds the same property
for the dated spelling; this one exists because a guard that honours two of three live phrasings is
the silent off-switch that suite's own docstring warns about, found in the wild.

WHAT MADE THE SPELLING SAFE TO HAND TO THE DRAW, and both halves have a leg below, because the
wiring is one line and neither of these is:

  * THE ANCHOR IS WHEN THE PROSE WAS WRITTEN, NEVER `now`. The resolution rule is "the first
    occurrence of that clock time at or after the anchor". Anchored on `now`, an item stamped 03:58
    is withheld at 03:00 correctly and then at 04:30 re-resolves to 03:58 TOMORROW and is withheld
    again -- at every draw, for ever. That is the permanent silent withholding of work that
    `embargoed_until` calls the worse of the two failures, so it is asserted here and not assumed.

  * AN INSTRUCTION INSIDE QUOTES IS BEING MENTIONED, NOT GIVEN. A quoted DATE is inert by
    construction because it has been and gone; a quoted date-LESS clock re-resolves into the future
    against any anchor it meets. Without `_without_quoted_spans` the very item that asked for this
    wiring -- which quotes the sentence above in order to describe it -- embargoes ITSELF until the
    following morning. The two are the discriminating pair on the live store (2 of 282 entries carry
    the spelling), and the fixtures below are their real text.
"""
from __future__ import annotations

import datetime
import time

import pytest

from background import delivery_lane, seat_continuation

#: The burning instance's own sentence, with the instant left for the caller. The `20:11:48` is kept
#: verbatim: it is a timestamp that offers `20:11` and `11:48` to a clock-time pattern without the
#: colon guards, and in this very sentence the wrong one of those resolves eight hours past the real
#: stamp. A fixture that dropped it would stop proving the antecedent rule it was written for.
_BACKREF = ("The run exec'd 20:11:48, 13.0 min per arm-leg, ETA near {}; "
            "do not draw this before then, the file will not exist.")

#: The item that QUOTES the grammar in order to describe it -- the live text of
#: `the-draw-cannot-read-an-instant-the-disposition-already-can`, which is the claim this repair was
#: done under. It is the second half of the pair and it must stay drawable.
_MENTION = ('`background/delivery_lane._back_referenced_start` resolves '
            '"ETA near {}; do not draw this before then" and has exactly ONE caller, '
            'inside the after-the-fact disposition.')


def _clock(when: float) -> str:
    """`HH:MM` for `when` -- built from the instant, never typed, so no leg can rot into a test of a
    date in the past."""
    return datetime.datetime.fromtimestamp(when).strftime("%H:%M")


@pytest.fixture
def now() -> float:
    """A fixed instant on a whole minute, for the reason the sibling suite gives: the grammar
    resolves to minutes, so seconds on the anchor round the expected stamp DOWN into the past."""
    return float(int(time.time() // 60) * 60)


@pytest.fixture
def lane(tmp_path, monkeypatch, now):
    """Three live continuations: the back-referenced one FIRST, the one that merely quotes it, and a
    free sibling behind both.

    The order is the production shape and it is load-bearing -- an embargoed item at the HEAD of the
    queue is exactly where a filter that stops the walk rather than skipping past it shuts the lane.
    """
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    seat_continuation.hand_off(
        "read-the-next12-twelve-alone-once-the-0358-run-settles",
        what="Read the next12 family as its own twelve-seed family. " + _BACKREF.format(
            _clock(now + 3600)),
        why="The twelve are the independent test of the published negative selection sign.",
        done_means="the twelve's mean, sem and sems-from-zero are published on their own terms.",
        now=now,
    )
    seat_continuation.hand_off(
        "the-draw-cannot-read-an-instant-the-disposition-already-can",
        what="Give the draw the reading the disposition already has. " + _MENTION.format(
            _clock(now + 3600)),
        why="The cheapest of the three open machine errors and the only one whose repair is a wire.",
        done_means="the draw withholds an item whose prose names a future instant in either "
                   "spelling.",
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


def test_the_draw_withholds_the_back_referenced_item_and_keeps_delivering(lane, now):
    """THE WHOLE PARTITION IN ONE CONTROL, and it is one test on purpose.

    Four assertions that are only meaningful together:

      1. inside the window the back-referenced item is NOT what the tick is handed -- this is the
         leg that reds if only the dated grammar is honoured, because nothing in that item's prose
         is a dated stamp;
      2. the item that merely QUOTES the sentence is not withheld with it;
      3. the lane did not fall silent -- a sibling still comes through;
      4. outside the window the held item is handed over, at the head of the queue where it has
         been all along.

    Split into four tests, (1) passes for a lane that delivers nothing at all, which is this
    project's most-repeated control failure: a guard that refuses everything passes every test of
    whether it refuses correctly. Only (4) can tell an embargo from a blacklist, and only (2) can
    tell a grammar from a substring.
    """
    held = delivery_lane.next_item(now=now, path=lane)

    assert held is not None, (
        "the lane went EMPTY inside an embargo window -- an item that cannot be started for an "
        "hour must not hold every other item shut behind it"
    )
    assert held["id"] != "read-the-next12-twelve-alone-once-the-0358-run-settles", (
        "the item whose prose names a future instant in the back-referenced spelling was handed "
        "out anyway -- the defect verbatim, and what it costs is the whole 100-minute window"
    )
    assert held["id"] == "the-draw-cannot-read-an-instant-the-disposition-already-can", (
        "an item that QUOTES the embargo grammar in order to describe it was withheld by it. The "
        "quoted instant re-resolves into the future against any anchor, so without the use/mention "
        "guard this repair's own claim embargoes itself"
    )

    delivery_lane.claims_mod.claim(held["id"], paths=[], path=lane, now=now)
    still_delivering = delivery_lane.next_item(now=now, path=lane)

    assert (still_delivering is not None
            and still_delivering["id"] == "decompose-the-negative-selection-leg"), (
        "with the quoting item taken, the embargoed row at the head of the queue swallowed the "
        "walk instead of being skipped past -- one wasted invocation traded for every invocation "
        "in the window"
    )

    released = delivery_lane.next_item(now=now + 7200, path=lane)

    assert (released is not None
            and released["id"] == "read-the-next12-twelve-alone-once-the-0358-run-settles"), (
        "the embargo never expired -- it is a WAIT, not a refusal, and an item whose instant has "
        "passed must come back at the head of the queue where it was written"
    )


def test_the_anchor_is_when_the_prose_was_written_and_not_now(lane, now):
    """THE LEG THAT REDS ON THE ANCHOR THE INSTRUCTION ASKED FOR, and it is the reason this is not
    a one-line wire.

    "The first occurrence of that clock time at or after the anchor" is the only reading consistent
    with what an ETA is -- but only while the anchor is a FIXED instant in the past. Anchored on
    `now`, the same prose resolves to a different day every time it is read: the item is correctly
    withheld before its instant and then withheld again at 04:30, and at noon, and tomorrow, for
    ever. Nothing in the leg above can see that; it only asks twice, an hour apart.

    THE WALL CLOCK IS MOVED, NOT JUST THE `now` ARGUMENT, and the first draft of this leg did only
    the second -- so the `now`-anchored version passed it. `_embargoed(item, now + offset)` hands
    its instant to the COMPARISON and never to the resolution, so a resolver reading `time.time()`
    answered identically at all four offsets. The mutation was caught, by a different leg, for a
    different reason; a leg that names the anchor has to be able to red on the anchor. Advancing
    `time.time` past the stamp is the only thing that tells a fixed anchor from a moving one.

    A stamp that is stable is a stamp that expires, and an embargo that cannot expire is the silent
    withholding of work that `embargoed_until` chose its whole fail-open direction to avoid.
    """
    item = next(i for i in seat_continuation.live(now=now)
                if i["id"] == "read-the-next12-twelve-alone-once-the-0358-run-settles")
    expected = float(int((now + 3600) // 60) * 60)

    assert delivery_lane._prose_anchor(item) == now, (
        "the anchor is not the instant the prose was written, so every reading below is a reading "
        "of something else"
    )

    with pytest.MonkeyPatch.context() as later:
        later.setattr(delivery_lane.time, "time", lambda: now + 100_000.0)
        assert delivery_lane.embargoed_until(item) == expected, (
            "the resolved instant moved when the WALL CLOCK did, so it is anchored on `now`. A day "
            "past its stamp this item re-resolves to the same clock time tomorrow, and is withheld "
            "again at that draw, and at every draw after it -- for ever"
        )
        assert delivery_lane._embargoed(item, None) is False, (
            "asked with no instant of its own, well past its stated one, the item still read HELD "
            "-- this is the permanent withholding, seen through the call the draw actually makes"
        )

    for offset in (0.0, 1800.0, 7200.0, 100_000.0):
        assert delivery_lane.embargoed_until(item) == expected, (
            "the resolved instant moved between readings taken {:.0f}s apart, so it is anchored "
            "on the clock and not on the prose -- this item is now unreachable for ever".format(
                offset)
        )
        assert delivery_lane._embargoed(item, now + offset) is (offset < 3600.0), (
            "at {:.0f}s past the anchor the item read {} -- an embargo must hold up to its stated "
            "instant and release at it, exactly once".format(
                offset, "drawable" if offset < 3600 else "HELD")
        )


def test_a_quoted_instruction_is_mentioned_and_a_bare_one_is_given(lane, now):
    """THE DISCRIMINATING PAIR, BOUND TOGETHER, because either leg alone passes for the wrong code.

    Assert only that the quoted one is free and a reader that never resolved the spelling at all
    passes. Assert only that the bare one is held and a reader that ignores quoting passes -- and
    that reader withholds the claim this repair was done under until the following morning.

    Both texts are the live ones (2026-09-18, the only two of 282 continuation entries carrying the
    spelling), and the whole difference between them is a pair of quote marks.
    """
    when = _clock(now + 3600)
    expected = float(int((now + 3600) // 60) * 60)

    given = delivery_lane.embargoed_until({"what": _BACKREF.format(when), "written_at": now})
    mentioned = delivery_lane.embargoed_until({"what": _MENTION.format(when), "written_at": now})

    assert given == expected, (
        "a bare back-referenced instruction resolved to {} -- the antecedent rule is 'the last "
        "instant named before `then`', and the 20:11:48 in the same sentence is a duration a "
        "clock-time pattern without colon guards reads as 20:11 or 11:48".format(given)
    )
    assert mentioned is None, (
        "the instruction was read out of a sentence that was describing it. That is how this "
        "repair's own claim embargoes itself, and a quoted date-less clock has none of the "
        "protection a quoted DATE has: it re-resolves into the future against any anchor"
    )


def test_no_anchor_means_no_back_referenced_embargo(monkeypatch, now):
    """THE FAIL-OPEN DIRECTION, ASSERTED RATHER THAN ASSUMED.

    A date-less clock is unresolvable without a reference instant, and the honest answer when none
    is available is that the item is drawable. The asymmetry is `embargoed_until`'s own: a stamp
    this misses costs ONE invocation and is visible to the tick that reads it, while one it invents
    empties the lane and is visible to nobody.
    """
    monkeypatch.setattr(delivery_lane.direction_mod, "read_direction", lambda *a, **k: None)

    assert delivery_lane.embargoed_until({"what": _BACKREF.format(_clock(now + 3600))}) is None, (
        "an item with no written-at and no live direction record was withheld on a clock time "
        "nothing could date"
    )
    assert delivery_lane._prose_anchor({"id": "x", "written_at": "not a number"}) is None, (
        "a malformed written-at must read as ABSENT, never be coerced into an anchor"
    )


def test_a_focus_row_is_anchored_on_the_orientation_that_wrote_it(monkeypatch, tmp_path, now):
    """THE OTHER STORE, AND THE ONE WITH NO `written_at` OF ITS OWN.

    `next_item` walks two sources. A focus row is re-derived wholesale at each orientation, so the
    direction record's `oriented_at` IS when its prose was written -- and `unreachable_focus`
    already returns nothing once that record goes stale, so an anchor read this way can never be
    older than the row it dates. Filtering only the continuation store would honour the spelling on
    a handed-off item and ignore it on the `DIRECTION.yaml` row the seat wrote by hand, which is
    the half the sibling suite's three measured failures came through.
    """
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    monkeypatch.setattr(
        delivery_lane.direction_mod, "read_direction",
        lambda *a, **k: delivery_lane.direction_mod.Direction(
            oriented_at=datetime.datetime.fromtimestamp(now, datetime.timezone.utc),
            focus=(), not_now=()))
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda _atoms: [
        {"id": "read-the-twelve-seed-family",
         "what": "Read the twelve. " + _BACKREF.format(_clock(now + 3600)), "why": "the test"},
        {"id": "decompose-the-negative-selection-leg",
         "what": "Decompose the negative leg.", "why": "thesis work"},
    ])

    held = delivery_lane.next_item(now=now, path=tmp_path / "claims.json")
    assert held is not None and held["id"] == "decompose-the-negative-selection-leg", (
        "a focus row's back-referenced stamp went unread, so the store the measured failures came "
        "through is the one still unguarded"
    )

    released = delivery_lane.next_item(now=now + 7200, path=tmp_path / "claims.json")
    assert released is not None and released["id"] == "read-the-twelve-seed-family"


def test_the_reader_names_the_instant_a_back_referenced_item_waits_for(lane, now, capsys,
                                                                       monkeypatch):
    """A SKIP NOTHING CAN INTERROGATE IS THE SAME SHAPE AS NO SKIP.

    `next_item` walks past an embargoed row in silence, correctly, so `--embargoed` is the only
    place a seat asking "why was that not offered?" gets an answer. A guard that withholds on a
    spelling the reader cannot print would be worse than the gap it closes: the item would vanish
    from the lane with nothing anywhere able to say what it was waiting for.
    """
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda _atoms: [])

    delivery_lane.main(["--embargoed"])
    printed = capsys.readouterr().out

    assert "read-the-next12-twelve-alone-once-the-0358-run-settles" in printed, (
        "the item the draw is withholding is absent from the only reader that can explain the "
        "withholding"
    )
    assert _clock(now + 3600) in printed, (
        "the reader named the item but not the instant it is waiting for, which tells a seat that "
        "its work has gone missing without telling it when it comes back"
    )
    assert "the-draw-cannot-read-an-instant-the-disposition-already-can" not in printed, (
        "the reader reports an embargo on an item that merely quotes the grammar"
    )
