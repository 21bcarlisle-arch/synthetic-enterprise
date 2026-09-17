"""THE READER-SIDE HALF of the Explore door: the household journey is not just composed, it is READ.

This door is the one place on the site where the epistemic wall is shown to a visitor rather than
asserted to a reviewer: each stage puts what the SUPPLIER BELIEVED beside what the WORLD KNEW, and
says how many of the stage's panels the customer could see. It is driven entirely by
`_bill_render_harness.mjs` and its own inline script, and until this file the only evidence anyone
could read it was that node's `vm` reported a string.

WHAT THE CLASS SWEEP ALREADY COVERS, so this file does not repeat it.
`site/test_every_door_element_a_reader_meets.py` asserts every element this door's script asked for
EXISTS and is VISIBLE in a browser, over the published bytes. It asserts no WORDS -- it would pass
this door with every figure on it wrong but readable -- and it names its own residual gap: an
element deleted from BOTH the markup and the script is outside its subject, because its id list
comes from what the script asked for on the run.

WHY THAT GAP IS WIDER ON THIS DOOR THAN ON ANY OTHER, and the reason this file was written second
after Capabilities. Four of the elements below carry a PLACEHOLDER in the markup -- `#wall-truth`
and `#wall-belief` are literally `—`, `#bookcount` is the word `This` -- so a render that never
runs leaves a visible element containing readable characters. Every exists-and-visible clause in
the sweep passes; so does "carries words". The reader meets an em-dash where the world's ground
truth should be, and nothing anywhere goes red. Only a leg that names the section and says what
kind of sentence belongs in it can see that, which is what this file is.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. No figure is pinned. The household on stage 1 today
consumed 213.8 kWh and the book is 154 households; both are supposed to move. What is asserted is
the shape each reading must have whatever the record says -- the wall has two sides and both are
filled, the stage names its clock, the spine offers every stage the page's own script defines, the
panel counter counts something, and the population headline counts the list it heads.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
SITE = _HERE.parent
# pytest's prepend import mode puts only the TEST FILE'S OWN directory on `sys.path`, so a test in
# `site/explore/` cannot import a module in `site/`. Relying on a sibling suite having been
# collected first would make this import order-dependent, which is a fail-silent waiting to happen.
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))

from test_the_browser_reading import (  # noqa: E402  (must follow the sys.path insertion above)
    assert_visible_reading,
    browser_available,
    published_site,
    read_in_browser,
)

_PAGE = "/explore/index.html"

#: The two sides of the epistemic wall, as a reader meets them. Both carry `—` in the markup, so
#: "the element exists and has characters in it" is satisfied by a door that rendered nothing.
_WALL = ("wall-truth", "wall-belief")

#: Everything the one browser load asks about.
_SUBJECT = (*_WALL, "who", "bookcount", "spine", "stage", "eyes-note", "eyes-all", "eyes-cust", "cust")

#: What the markup leaves in an element the script has not filled yet. Asserted against, by name,
#: because it is the exact string that makes this door's un-rendered state look rendered.
_PLACEHOLDERS = {"—", "-", "–", "This", "…", "..."}


@pytest.fixture(scope="module")
def reading():
    """One browser launch, one server, and the PUBLISHED SOURCE of the door beside the reading.

    The source is yielded because one leg below joins the two halves of a single subject: how many
    stages the page's own script DEFINES against how many the reader is offered. `published_site`
    exists in the form it does for exactly this -- a leg that read the script from the working tree
    and the page from the published extract would be describing a door that exists nowhere.
    """
    why = browser_available()
    if why:
        pytest.skip(why)
    with published_site() as (base, docroot):
        source = (docroot / "explore" / "index.html").read_text(encoding="utf-8")
        yield read_in_browser(base + _PAGE, *_SUBJECT), source


def test_every_section_a_reader_would_quote_carries_words_they_can_read(reading):
    """THE NAMED-SECTION LEG the class sweep cannot make: its id list comes from what the script
    asked for on the run, so a section deleted from BOTH the markup and the script leaves its
    subject in silence. These are named, so a deletion reds here."""
    payload, _source = reading
    empty = []
    for eid in _SUBJECT:
        el = assert_visible_reading(payload, eid)
        if not el["text"].split():
            empty.append(f"#{eid}")
    assert not empty, (
        "{} section(s) of the Explore door are on the page and visible, and carry no words a "
        "reader can read: {}".format(len(empty), ", ".join(empty))
    )


def test_both_sides_of_the_wall_are_filled_and_not_left_at_their_placeholder(reading):
    """THE LEG THIS DOOR EXISTS FOR, and the one the placeholders defeat everywhere else.

    `#wall-truth` and `#wall-belief` ship as `—` in the markup. A render that never runs therefore
    leaves two visible elements carrying a readable character each: the class sweep's exists clause
    passes, its visible clause passes, and a words-are-present clause passes too. The reader meets
    an em-dash where the world's ground truth should be.

    Both sides matter and in both directions. A stage showing only what the world knew publishes
    ground truth as if the supplier held it -- the epistemic wall, on the one page built to show it.
    A stage showing only the belief drops the comparison that makes the belief worth reading.
    """
    payload, _source = reading
    for eid in _WALL:
        el = assert_visible_reading(payload, eid)
        text = el["text"].strip()
        assert text not in _PLACEHOLDERS, (
            f"#{eid} is still showing its markup placeholder {text!r}, so this stage never "
            "rendered that side of the wall and the reader meets a dash where a sentence belongs"
        )
        assert len(text.split()) >= 4, (
            f"#{eid} reads {text!r}, which is not a statement of what was known or believed"
        )
    truth = payload["elements"]["wall-truth"]["text"]
    belief = payload["elements"]["wall-belief"]["text"]
    assert truth.strip() != belief.strip(), (
        "both sides of the wall carry the SAME sentence, so the page is showing the supplier's "
        f"belief and the world's truth as one reading: {truth[:160]!r}"
    )


def test_the_stage_asks_its_question_and_names_the_clock_it_answers_on(reading):
    """Every stage of this journey is a question with a clock -- "why does this tariff cost what it
    costs?" answered at a single moment before any energy flows. The clock is what stops a reader
    reconciling a forecast against a settled figure, and CLAUDE.md makes carrying it a rule.

    Neither the question nor the clock's VALUE is pinned; that both are stated is."""
    payload, _source = reading
    el = assert_visible_reading(payload, "stage")
    text = el["text"]
    assert "Clock:" in text, (
        f"the stage a reader is looking at does not say which clock its figures are on: {text[:250]!r}"
    )
    assert "?" in text.split("Clock:")[0], (
        "the stage heading asks the reader no question, which is the whole form of this journey: "
        f"{text[:250]!r}"
    )


def test_the_page_does_not_tell_the_reader_a_record_failed_to_load_when_none_did(reading):
    """This door has three `.catch()` branches that write into `#stage` -- the customer book, the
    household's own records, and the carbon feed. Each is correct when the feed really is missing.
    The failure mode is a render THROWING for another reason and the `.catch()` then publishing a
    load failure that did not happen, which is what happened on the deployment door on 2026-09-17
    with every committed control green. Fires on the class, not on one cause."""
    payload, _source = reading
    el = assert_visible_reading(payload, "stage")
    assert "could not be loaded" not in el["text"].lower(), (
        "the page tells the reader its own records could not be loaded. Either that is true -- in "
        "which case this door's feed is broken -- or a render threw and the .catch() published a "
        f"failure the page did not have. #stage reads {el['text'][:250]!r}"
    )


def test_the_reader_is_offered_every_stage_the_page_defines(reading):
    """THE JOIN, and nothing in it is hand-kept. The spine is built in a loop over the door's own
    `RENDER` array, so the number of stages a reader is offered is derivable from the published
    script rather than written down here -- a stage added to the journey is covered the same day,
    and a stage renamed takes its own coverage with it.

    The defect this catches is a spine that renders SHORT: the door still works, the reader simply
    never learns that stages 4, 5 and 6 exist. Every element on the page exists and is visible, so
    the class sweep is green, and each of the stages that DID render reads perfectly."""
    payload, source = reading
    match = re.search(r"var\s+RENDER\s*=\s*\[([^\]]*)\]", source)
    assert match, (
        "the published copy of this door defines no RENDER array, so this leg has no independent "
        "count to hold the spine against -- the page's shape has changed and this control with it"
    )
    defined = [s.strip() for s in match.group(1).split(",") if s.strip()]
    assert len(defined) >= 2, (
        f"the door defines {len(defined)} stage renderer(s); a journey with one stage is not one"
    )
    el = assert_visible_reading(payload, "spine")
    offered = len(re.findall(r"Stage\s+\d+", el["text"]))
    assert offered == len(defined), (
        "the page's script defines {} stage(s) and the spine offers the reader {}. The stages a "
        "reader never learns exist render perfectly when nobody asks for them: the spine reads "
        "{!r}".format(len(defined), offered, el["text"][:200])
    )


def test_the_panel_counter_is_counting_panels_that_are_there(reading):
    """`countEyes` counts `#stage .panel[data-side]` in the LIVE DOM and prints the total. So its
    sentence is a reading of whether the stage rendered anything at all -- and "0 panels on this
    stage" is what it prints when `#stage` is present, visible, and empty.

    That state passes the class sweep on both clauses, and passes its door-level "rendered nothing"
    floor too, because the floor asks whether the DOOR wrote into any element and this door wrote
    into nine. Measured 2026-09-17: driving this door under node's `vm` reports exactly that -- `0
    panels on this stage` -- while chromium renders 2. A control that could not tell those apart
    would have been reading the harness, not the page.

    Keyed to the property: at least one panel, not today's two. The count moves with the stage."""
    payload, _source = reading
    el = assert_visible_reading(payload, "eyes-note")
    match = re.search(r"(\d+)\s+panels? on this stage", el["text"])
    assert match, (
        f"the panel counter does not state a count of panels at all: {el['text'][:200]!r}"
    )
    assert int(match.group(1)) > 0, (
        "the page tells the reader there are 0 panels on this stage. #stage exists and is visible, "
        "so every reader-side clause about it passes; there is simply nothing in it"
    )


def test_the_population_headline_counts_the_list_it_heads(reading):
    """CLAUDE.md's most expensive recurring shape, in its smallest form: a count published over a
    population it was not measured over. `#bookcount` says "All N households below" and `#cust` IS
    the list below it -- so the two are one subject and must agree, in the browser, where a reader
    can compare them.

    It also catches the un-rendered state, which is the reason the placeholder is named. `#bookcount`
    ships as the word `This` in the markup: a script that never reached it leaves a visible element
    reading "This is the whole book", a true-sounding sentence with no count in it at all."""
    payload, _source = reading
    el = assert_visible_reading(payload, "bookcount")
    text = el["text"].strip()
    assert text not in _PLACEHOLDERS, (
        f"#bookcount is still showing its markup placeholder {text!r}, so the reader is told the "
        "size of the book by a sentence that never received one"
    )
    match = re.search(r"\b(\d[\d,]*)\b", text)
    assert match, f"the population headline states no count: {text!r}"
    claimed = int(match.group(1).replace(",", ""))

    offered = [line for line in payload["elements"]["cust"]["text"].splitlines() if line.strip()]
    assert claimed == len(offered), (
        "the page heads the list with {} households and offers the reader {} to choose from. One "
        "of the two is counting a different population: the headline reads {!r}".format(
            claimed, len(offered), text)
    )
