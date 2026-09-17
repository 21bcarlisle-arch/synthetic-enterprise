"""THE READER-SIDE HALF of the Capabilities door: the sentences are not just composed, they are READ.

`site/capabilities/test_capabilities_door.py` beside this file grades the page's structure and the
derivation behind its status pills, and it is the important suite -- a capabilities page is the
easiest page on any site to lie on, and that one is what stops this one outrunning its record. What
it cannot say is whether a person with a browser meets any of it.

`site/test_every_door_element_a_reader_meets.py` says that much for all 22 doors: every element the
door's script asked for EXISTS and is VISIBLE, in one chromium launch. What that sweep deliberately
does NOT do is assert WORDS -- it would pass this door with every figure on it wrong but readable.
And it names its own residual gap: **an element deleted from BOTH the markup and the script is
outside its subject entirely**, because its id list comes from what the script asked for on that
run. A section quietly dropped from this page takes its own coverage with it and nothing goes red.

This file is the join, and it closes that gap for the readings a person would actually quote.

WHY A NAMED SUBSET AND NOT ALL 41 IDS. Naming every element the page renders would re-state the
sweep with a hand-kept list -- and a hand-kept list is exactly how a control comes to grade a
population that has drifted out from under it. The list below is the sections that carry a READING:
the four headlines, the four notes that carry their clock, the three tally strips, and the page's
own statement of its limits. Those are what a reader quotes and what a deletion would cost them.
Everything else on the door is covered, as exists-and-visible, by the sweep.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here pins a figure. "£16,792" and "154-224
customers" are this run's answers and the page is supposed to move when the record moves; a control
pinned to them would go red the day the company got better and stay green the day the page started
lying. So each leg asserts a SHAPE the sentence must have whatever the run says: the comparison
names both of its sides, the money sections name their clock, the tallies carry figures and not
just labels, and no section publishes a load failure the page did not have.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
SITE = _HERE.parent
# The same insertion `site/capabilities/test_capabilities_door.py` and the deployment door's browser
# leg both make, for the same reason: pytest's prepend import mode puts only the TEST FILE'S OWN
# directory on `sys.path`, so a test in `site/capabilities/` cannot import a module in `site/`.
# Relying on a sibling suite having been collected first would make this import order-dependent,
# which is a fail-silent waiting to happen.
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))

from test_the_browser_reading import (  # noqa: E402  (must follow the sys.path insertion above)
    assert_visible_reading,
    browser_available,
    published_site_server,
    read_in_browser,
)

_PAGE = "/capabilities/index.html"

#: The four sentences this door is quoted on. Each one is a headline a reader would repeat, and
#: each is written by a different `fetch().then()` chain, so naming all four is also what proves
#: every chain on the page ran to its end rather than dying part-way in silence.
_HEADLINES = ("stamp", "growth-headline", "arms-headline", "ddopen-headline")

#: The elements the page's OWN `.catch()` branches write into -- `#stamp`, and the three `-note`
#: elements. There is one per chain and the wording is the page's, not this file's: "could not be
#: loaded" / "could not load its data". A reader meeting one of those on a page whose feeds all
#: loaded is reading a failure that did not happen.
_CATCH_TARGETS = ("stamp", "growth-note", "arms-note", "ddopen-note")

#: The three figure strips. Each renders `<div class="fig-v">N</div>` beside a label, so a strip
#: that loses its figures is still a visible element full of words.
_TALLIES = ("uc-tally", "access", "wall")

#: The three money chains, and for each the elements a reader meets its figures through. The CLOCK
#: is asserted over the chain, not over one element, and that is a correction: the first draft of
#: this file asked `#arms-note` for the arms clock and went red on a page that states it perfectly
#: -- the arms clock lives on the two table headers (`settled-realised`, `settled-provisioned`),
#: because this chain publishes on two of them and one note could not carry both. Naming the chain
#: rather than an element is also what keeps the leg true when the section is re-laid-out.
_MONEY_CHAINS = {
    "the growth curve": ("growth-note",),
    "the arm comparison": ("arms-note", "arms-realised", "arms-split"),
    "the opening direct debit": ("ddopen-note",),
}

#: Everything above plus the limits section and the two capability columns, which is what the one
#: browser load asks about.
_SUBJECT = (
    *_HEADLINES, *_CATCH_TARGETS, *_TALLIES,
    *sorted({eid for ids in _MONEY_CHAINS.values() for eid in ids}),
    "gaps", "supplier", "world", "wallnote", "golive", "growth", "use-cases",
)


@pytest.fixture(scope="module")
def reading():
    """One browser launch and one server for the whole module -- a chromium start is ~1.5s and the
    legs below all ask about the same page load, so paying it per-test would buy nothing."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with published_site_server() as base:
        yield read_in_browser(base + _PAGE, *_SUBJECT)


def test_every_section_a_reader_would_quote_carries_words_they_can_read(reading):
    """THE LEG THE SWEEP CANNOT MAKE, and the reason this file exists at all.

    The sweep derives its ids from what the script asked for on that run, so a section deleted from
    BOTH the markup and the script leaves its subject silently. These ids are NAMED, so a deletion
    reds here. And `visible` is not enough on its own: an empty `<div>` with a border still has a
    box, so it passes the sweep's visibility clause while the reader meets nothing in it.
    """
    empty = []
    for eid in _SUBJECT:
        el = assert_visible_reading(reading, eid)
        if not el["text"].split():
            empty.append(f"#{eid}")
    assert not empty, (
        "{} section(s) of the Capabilities door are on the page and visible, and carry no words a "
        "reader can read: {}".format(len(empty), ", ".join(empty))
    )


def test_no_section_publishes_a_load_failure_the_page_did_not_have(reading):
    """THE QUIETEST BREAKAGE ON THIS DOOR, and the one no vm control could see.

    This page runs four independent `fetch(...).then(...)` chains and each has a `.catch()` that
    writes "could not be loaded ... The figures are absent, not zero" into its own element. That is
    correct behaviour when a feed really is missing. The failure mode is a render THROWING for some
    other reason -- a renamed container, a shape change -- and the `.catch()` then publishing a
    load failure that did not happen, while every figure after the throw goes missing in silence.
    Exactly that happened on the deployment door on 2026-09-17 with every committed control green.

    Fires on the whole class: any exception in any of the four chains, from any cause.
    """
    for eid in _CATCH_TARGETS:
        el = assert_visible_reading(reading, eid)
        text = el["text"].lower()
        assert "could not be loaded" not in text and "could not load its data" not in text, (
            f"#{eid} tells the reader the page's own record could not be loaded. Either that is "
            "true -- in which case this door's feed is broken -- or a render threw and the "
            f".catch() published a failure the page did not have. It reads {el['text'][:200]!r}"
        )


def test_the_page_states_the_clock_and_the_commit_it_was_generated_at(reading):
    """CLAUDE.md: every financial figure carries its clock. `tools/generate_dashboard_data.py`
    holds that on the FEED; this holds that it REACHES THE READER, which is a different claim and
    the one the rule is actually about.

    Keyed to the shape -- a timestamp and a commit -- never to today's values."""
    el = assert_visible_reading(reading, "stamp", must_contain="Generated")
    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", el["text"]), (
        f"the stamp names no generation instant, so nothing on the page carries a clock a reader "
        f"can read: {el['text'][:200]!r}"
    )
    assert re.search(r"commit\s+[0-9a-f]{7,40}", el["text"]), (
        f"the stamp names no commit, so a reader cannot say which tree produced these figures: "
        f"{el['text'][:200]!r}"
    )


def test_every_money_chain_names_the_clock_its_figures_are_on(reading):
    """The three money chains publish on DIFFERENT clocks -- the growth curve on settled, the
    opening direct-debit work on billed, the arm comparison on two of its own -- and this project's
    recorded way of publishing something misleading is two correct figures from two clocks read as
    one. `tools/generate_dashboard_data.py` holds the basis rule on the FEED; this holds that the
    clock REACHES THE READER, which is a different claim and the one the rule is about.

    A property, not an answer, twice over: the clock's NAME is not pinned, and the ELEMENT carrying
    it is not either -- the chain must state it somewhere a reader meets its figures. The first
    draft asserted per element and reddened on a page that states every clock it has, which is a
    control pinned to a layout rather than to the property (CLAUDE.md)."""
    silent = []
    for chain, ids in _MONEY_CHAINS.items():
        readings = [assert_visible_reading(reading, eid) for eid in ids]
        if not any("clock" in el["text"].lower() for el in readings):
            silent.append(f"{chain} (#{', #'.join(ids)})")
    assert not silent, (
        "{} money chain(s) publish figures without telling the reader which clock they are on, so "
        "they cannot be reconciled against anything else on the page: {}".format(
            len(silent), "; ".join(silent))
    )


def test_each_headline_comparison_names_both_of_the_things_it_compares(reading):
    """CLAUDE.md: before dividing two numbers, say out loud what each one counts -- and before
    publishing a difference, say what it is a difference BETWEEN. A comparison sentence that names
    one side is the shape that lets value TRANSFERRED read as value CREATED.

    Each assertion below is on the vocabulary the comparison cannot be stated without, not on its
    result. `#arms-headline` may say the per-customer engine won or lost; it may not say it without
    naming the flat rule it is measured against.
    """
    arms = assert_visible_reading(reading, "arms-headline")["text"].lower()
    assert "per-customer" in arms and "flat" in arms, (
        "the arms headline states an advantage without naming both arms, so a reader cannot tell "
        f"what it is an advantage OVER: {arms[:250]!r}"
    )
    assert "£" in arms, f"the arms headline states no money amount at all: {arms[:250]!r}"

    growth = assert_visible_reading(reading, "growth-headline")["text"].lower()
    assert "won" in growth and "settle" in growth, (
        "the growth headline does not distinguish the accounts the company WON from the ones our "
        f"settlement engine could SETTLE, which is the only reason that sentence exists: {growth[:250]!r}"
    )

    ddopen = assert_visible_reading(reading, "ddopen-headline")["text"].lower()
    assert "estimate" in ddopen and "bill" in ddopen, (
        "the opening direct-debit headline names no pair of sizing rules, so the figure it moves "
        f"is a difference between nothing and nothing: {ddopen[:250]!r}"
    )


def test_every_tally_strip_carries_figures_and_not_only_labels(reading):
    """The three strips are `figure + label` pairs built from a feed. A strip that loses its
    figures keeps every label, keeps its box, and passes both clauses of the class sweep -- the
    reader meets three headings over nothing. Each label is asserted too, because a strip of bare
    numbers is the mirror failure and just as unreadable."""
    for eid in _TALLIES:
        el = assert_visible_reading(reading, eid)
        text = el["text"]
        assert re.search(r"\d", text), (
            f"#{eid} is a tally strip carrying no figure at all, only labels: {text[:200]!r}"
        )
        assert len([w for w in text.split() if w.isalpha()]) >= 3, (
            f"#{eid} carries figures with nothing saying what they count: {text[:200]!r}"
        )


def test_the_page_states_its_own_limits_at_the_length_that_makes_them_honest(reading):
    """A capabilities page is the easiest page on the site to lie on -- its own door suite says so
    -- and the section that keeps it honest is the one listing what is NOT true of this company.
    That section emptying is a silent upgrade of every claim above it.

    The floor is on SUBSTANCE, not on a count of items: a gap list trimmed to three-word bullets
    would satisfy an item count and tell a reader nothing. It is set well below today's length so
    that editing the gaps is free and deleting them is not."""
    el = assert_visible_reading(reading, "gaps")
    words = len(el["text"].split())
    assert words >= 60, (
        f"the Capabilities door states its own limits in {words} words. Everything above that "
        "section is a claim about what this company can do, and the section that qualifies them "
        f"has been emptied to: {el['text'][:300]!r}"
    )
