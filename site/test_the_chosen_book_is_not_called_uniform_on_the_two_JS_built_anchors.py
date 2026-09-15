"""The two anchors the door builds ITSELF must read the selection, not assume the old one.

THE DEFECT IT SERVES, and why a second file rather than a leg on the first. `480f2cf75` landed a
door over the chosen sample and it is a good one, but it has exactly one subject:
`#growth-headline`, the sentence `tools/generate_book_growth_data.py` builds SERVER SIDE. Two more
published sentences describe the same mechanism and both are built by the door's OWN JavaScript:

  * `#arms-sample`  -- `site/capabilities/index.html`, the `settlement_selection` branch.
  * `#growth-note`  -- `site/capabilities/index.html`, the `var chosen = ...` branch.

`3957ba848` re-worded both, correctly. Nothing was keyed to either of them, and on 2026-09-11 that
was measured rather than argued: neutering BOTH chosen branches so the render falls through to the
cull prose left **145 tests green**, including every leg of
`test_the_baseline_comparison_reaches_the_reader.py` and every leg of the landed headline door,
while the real published feed says `chosen_weighted` and the page told the reader:

    "The 164 settled accounts above are a uniform 18.3% sample of the 500 accounts the company
     won ... divide it by 0.183 to read the supplier instead."

That is the same arithmetic-a-reader-can-carry-out the headline door exists to prevent, on the same
page, one section below it, and nothing could see it.

WHY EVERY EXISTING CONTROL WAS BLIND, and it is not that they were careless.
`test_the_baseline_comparison_reaches_the_reader.py` DOES drive `#arms-sample` through the real
harness against the published growth feed, so since `480f2cf75` it genuinely EXECUTES the chosen
branch. But executing a branch is not dooring it: every assertion it makes is satisfied by the cull
branch too --

    "sample" in rendered            -> "a uniform 18.3% sample"  AND  "a CHOSEN 18.3% sample"
    "{:.1f}%".format(rate * 100)    -> both
    the win count                   -> both
    "{:.3f}".format(rate)           -> "divide it by 0.183"  AND  "dividing by 0.183 would be wrong"

The last row is the sharp one. That control requires the divisor to be PRESENT, and both branches
print it -- one as an instruction to use, one as an instruction to refuse. It cannot discriminate
them, and its own remedy prose ("*without giving them the divisor that turns it back into the
supplier*") is FALSE of a chosen book, where no such divisor exists. The arithmetic stayed right
while the sentence explaining it went wrong. `#growth-note` is the plainer case: nothing named the
selection at all.

THE LEG THAT CARRIES THIS FILE IS `test_MUTATION_*_renders_DIFFERENT_prose_for_the_two_selections`,
and it is deliberately not keyed to any wording. Deleting a chosen branch makes the two renders
IDENTICAL, because the fall-through is the cull. So "these two must differ" is red on exactly the
defect, survives any re-wording of either branch, and cannot rot into agreeing with the code -- it
compares the page against itself under two feeds it is handed.

KEYED TO THE SELECTION, NEVER TO TODAY'S 18.3%. The day the budget lifts far enough to settle every
win the rate goes to 1.0, no sample exists and a third branch renders. Nothing here asserts a
percentage, a count, or that the published feed says `chosen_weighted`; the lift leg asks only that
what the page CLAIMS and what the feed DECLARES describe the same mechanism.

R15 -- the mutations, each naming the defect it catches:

  * `if (false && g && g.settlement_selection === "chosen_weighted")` -> the `#arms-sample` differ
    leg, uniformity leg and instruction leg all red. This is the shipped-defect shape, reproduced.
  * `var chosen = false;` -> the `#growth-note` differ and uniformity legs red. Same shape, the
    other anchor.
  * invert either branch (take the chosen prose on `uniform_count`) -> the CULL legs red. They are
    there so the chosen legs cannot pass vacuously on a page that has lost the cull branch instead:
    a page that says "CHOSEN" unconditionally is as wrong as one that says "uniform"
    unconditionally, and only asserting BOTH ends catches it.
  * publish a feed whose selection disagrees with the rendered claim -> the lift leg red.
"""
from __future__ import annotations

import re

import pytest

# THE PLUMBING IS THE LANDED DOOR'S, IMPORTED RATHER THAN REBUILT. `_render` there already drives
# the real `_live_harness.mjs` over the real published door and returns the WHOLE element map, so
# both anchors below are reachable through it unchanged; `_build` is the real producer's output for
# a campaign we control. Two renderers for one page is how this file and that one would start
# disagreeing about what the door does while both looked right.
from test_the_chosen_sample_reaches_the_reader_without_a_divide_instruction import (
    FEED_REL,
    _build,
    _render,
)
from test_the_published_bytes_reader import published_json

#: The anchors this file exists for: the two the door builds ITSELF. `#growth-headline` is the
#: landed door's subject and is deliberately not re-asserted here.
ANCHORS = ("arms-sample", "growth-note")

#: The claim that is FALSE of a chosen book -- the reassuring half of the cull sentence, and the
#: half that survives a mechanism change unnoticed.
_UNIFORMITY = "uniform"

#: A DENIAL of uniformity is not a claim of it, and the chosen branch's whole point is to deny it:
#: "It is deliberately NOT uniform". A bare substring test fires on that, which is a control going
#: red on the most correct sentence on the page. Stripped before the test rather than special-cased
#: inside one leg, so the CULL legs are normalised identically -- a narrowing applied to only the
#: end that was inconvenient is a place for the defect to hide (R15), and this one has to leave the
#: cull's own "are a uniform 18.3% sample" standing or those legs stop proving reachability.
_DENIAL = re.compile(r"\bnot\s+uniform\b", re.IGNORECASE)


def _claims_uniformity(text: str) -> bool:
    """Does this sentence ASSERT the sample is uniform, as opposed to denying that it is?

    The cull asserts it twice ("are a uniform 18.3% sample", "and it is uniform, so the SHAPE").
    The chosen branch denies it once and says nothing else uniform. That asymmetry is the whole
    signal, so the denial is removed and whatever "uniform" is left is an assertion.
    """
    return _UNIFORMITY in _DENIAL.sub("", text).lower()

#: The other false-of-a-chosen-book claim, `#growth-note`'s. That anchor never used the word
#: "uniform" -- it asserts proportionality instead, which is the same claim in different clothes.
_SAME_RATE = "same rate"

#: The INSTRUCTION, as distinct from the refusal. Both branches print the divisor; only the cull
#: tells the reader to apply it. This phrase is the imperative's tail, and the chosen branch's
#: "dividing by 0.200 would be wrong" does not contain it.
_INSTRUCTION = "to read the supplier instead"


def _text(element) -> str:
    """The words a reader actually meets, markup stripped.

    FAIL-CLOSED: a missing element or one that renders empty raises here rather than returning ""
    for a `not in` assertion to pass on happily. An unavailable check is a FAILED check (R15) --
    and on this page an empty `#arms-sample` is itself the defect, because silence beside an
    account count reads as "this book is the supplier".
    """
    assert element is not None, "the door rendered no such element at all"
    raw = element if isinstance(element, str) else (
        element.get("innerHTML") or element.get("textContent") or "")
    text = re.sub(r"<[^>]+>", " ", raw)
    text = text.replace("&mdash;", "--").replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    assert text, "the element rendered EMPTY, which no reader can act on"
    return text


@pytest.fixture(scope="module")
def chosen() -> dict:
    """The page as it renders over a book that was CHOSEN for difference."""
    return _render(_build("chosen_weighted"))


@pytest.fixture(scope="module")
def cull() -> dict:
    """The page as it renders over the count cull that really did run before 2026-09-11."""
    return _render(_build("uniform_count"))


# ── THE LEG THAT CARRIES THE FILE ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("anchor", ANCHORS)
def test_MUTATION_the_anchor_renders_DIFFERENT_prose_for_the_two_selections(anchor, chosen, cull):
    """THE DISCRIMINATING LEG, keyed to the property and to no wording at all.

    Both selections give a sample rate below one, so the rate cannot tell them apart and every
    control keyed to it was blind by construction. What must hold is that the page READS the
    selection: hand it two feeds that differ in nothing but `settlement_selection` and it must say
    two different things. Deleting a chosen branch makes the fall-through render the cull prose,
    the two become identical, and this goes red -- whatever either branch has been re-worded to.
    """
    a, b = _text(chosen.get(anchor)), _text(cull.get(anchor))

    assert a != b, (
        "`#{}` renders the IDENTICAL sentence for a CHOSEN book and a uniform cull, so it is "
        "printing a constant and reads nothing from the selection the feed declares. Whichever "
        "mechanism is running, one of the two readings is wrong. Rendered:\n{}".format(anchor, a)
    )


# ── THE CHOSEN END: what must NOT be said over a book picked for difference ───────────────────

def test_a_chosen_book_is_never_described_as_a_uniform_sample(chosen):
    """Uniformity is a claim about the SELECTION, and it is false of a chosen book.

    The accounts were picked to differ across the demand axes and each carries its own weight --
    on this book those weights span 0.057 to 14.774. "Uniform" tells the reader the shape of the
    figures is commercial when the shape is partly the chooser's.
    """
    text = _text(chosen.get("arms-sample"))

    assert not _claims_uniformity(text), (
        "the page calls a CHOSEN sample uniform, which is the reassuring half of the cull "
        "sentence surviving the mechanism changing under it: {}".format(text))


def test_a_chosen_book_is_never_described_as_sampled_at_the_same_rate(chosen):
    """`#growth-note`'s form of the same false claim -- it never used the word "uniform".

    "Every year is sampled at the same rate, so the shape of the curve is the company's" is
    proportionality by another name, and a chosen sample is deliberately not proportional by
    count. A reader who believes it reads the chooser's shape as the market's.
    """
    text = _text(chosen.get("growth-note"))

    assert _SAME_RATE not in text.lower(), (
        "the growth note tells the reader a CHOSEN sample takes every year at the same rate, so "
        "the bars' shape is attributed to the company when it is partly ours: {}".format(text))


def test_a_chosen_book_is_never_handed_an_instruction_to_divide_by_the_rate(chosen):
    """THE DAMAGE, and the reason this file is about the instruction and not only the adjective.

    "Uniform" is a claim a reader can doubt. "Divide it by 0.183 to read the supplier instead" is
    an ARITHMETIC A READER CAN CARRY OUT: under per-account weights it returns a wrong number, in
    silence, with nothing on the page to contradict it. Both branches print the divisor -- the
    chosen one prints it to refuse it -- so this is keyed to the imperative's tail and not to the
    number, which is why `dividing by 0.200 would be wrong` passes it and must.
    """
    text = _text(chosen.get("arms-sample"))

    assert _INSTRUCTION not in text.lower(), (
        "the page hands a reader of a CHOSEN book one number to undo the sample with. No single "
        "number undoes it: `settlement_weight` on each row is what reads across to the supplier. "
        "Rendered: {}".format(text))


# ── THE CULL END: proving the legs above can fail, and are not vacuous ────────────────────────
#
# R15's unreachable-PASS-branch shape, which this project has entered three times in one
# afternoon through three different doors. A page that lost its CULL branch instead -- rendering
# "CHOSEN" unconditionally -- passes every assertion above while being exactly as wrong. These
# assert the other end of the partition, so neither branch can quietly become unreachable.

def test_a_real_uniform_cull_IS_still_called_uniform(cull):
    """Every campaign record written before 2026-09-11 genuinely WAS a count cull, and the page
    must still say so over one. If this ever goes red the chosen legs above have gone vacuous."""
    text = _text(cull.get("arms-sample"))

    assert _claims_uniformity(text), (
        "a genuine uniform cull is no longer described as one, so the chosen-branch assertions "
        "in this file are passing on a page that says CHOSEN whatever it is handed: "
        "{}".format(text))


def test_a_real_uniform_cull_IS_still_told_how_to_read_the_supplier(cull):
    """The instruction is CORRECT over a count cull -- that is the whole asymmetry. A control that
    only ever forbade it would be a control that could not distinguish the two mechanisms either,
    which is the defect this file was written about."""
    text = _text(cull.get("arms-sample"))

    assert _INSTRUCTION in text.lower(), (
        "the cull branch no longer tells a reader how to read the supplier, so the chosen-book "
        "instruction leg can no longer fail and proves nothing: {}".format(text))


def test_a_real_uniform_cull_note_IS_still_keyed_to_the_same_rate(cull):
    """`#growth-note`'s end of the same partition."""
    text = _text(cull.get("growth-note"))

    assert _SAME_RATE in text.lower(), (
        "the growth note's cull branch no longer claims proportionality, so the chosen-book leg "
        "above is vacuous: {}".format(text))


# ── THE LIFT LEG ──────────────────────────────────────────────────────────────────────────────

def test_the_PUBLISHED_pages_two_anchors_agree_with_the_selection_the_feed_DECLARES():
    """A door test that builds its own feed controls the RENDER and not the LIFT.

    Every leg above hands the page a feed. That proves the page would say the right thing IF the
    feed said so, and stays green for exactly as long as the feed does not -- which is the state
    `3957ba848` landed in and said so: `book_growth.json` predated the chooser, carried no
    `settlement_selection`, and the JS took the cull branch on a chosen book with every control
    green. This leg reads the PUBLISHED bytes.

    KEYED TO AGREEMENT, NOT TO TODAY'S MECHANISM. Asserting the feed says `chosen_weighted` would
    pin this to whatever happens to be running, and would red on a page that got BETTER the day
    the budget settles every win. What must hold whatever runs is that the two published anchors
    and the feed's own declared selection describe the SAME mechanism.
    """
    feed = published_json(FEED_REL)
    selection = feed.get("settlement_selection")
    assert selection is not None, (
        "the published growth feed declares no `settlement_selection`, so what the two anchors "
        "claim cannot be checked against anything at all -- which is the unfalsifiable state, not "
        "a passing one")

    rendered = _render(feed)
    sample, note = _text(rendered.get("arms-sample")), _text(rendered.get("growth-note"))

    if selection == "chosen_weighted":
        assert not _claims_uniformity(sample), (
            "the published feed declares a CHOSEN book and the published page calls it a uniform "
            "sample: {}".format(sample))
        assert _INSTRUCTION not in sample.lower(), (
            "the published feed declares a CHOSEN book and the published page still hands the "
            "reader one number to undo it with: {}".format(sample))
        assert _SAME_RATE not in note.lower(), (
            "the published feed declares a CHOSEN book and the published growth note still "
            "claims every year is taken at the same rate: {}".format(note))
    elif selection == "uniform_count":
        assert _claims_uniformity(sample), (
            "the published feed declares a uniform cull and the published page does not say so, "
            "so a reader is not told the shape is commercial when it is: {}".format(sample))
    else:
        pytest.fail(
            "the published feed declares a selection this door has no branch for ({!r}). A third "
            "mechanism needs its own prose and its own leg here -- falling through to either "
            "existing branch would publish a description of a mechanism that did not "
            "run".format(selection))
