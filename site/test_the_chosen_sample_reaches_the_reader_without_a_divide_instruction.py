"""A reader of the growth curve must never be handed one number to undo a CHOSEN sample with.

THE DEFECT IT SERVES. `3957ba848` replaced the settlement count cull with a chooser: the settled
book is picked for difference over the demand axes and every account carries its own weight, which
on this book span 0.057 to 14.774 — a 259.7x spread. Three published sentences described the old
mechanism. Two of them are built by the door's own JavaScript and that commit re-worded both. The
third is `engine_bound_statement`, built SERVER SIDE in `tools/generate_book_growth_data.py` and
rendered by `site/capabilities/index.html` as the page HEADLINE, above the two that were fixed. It
was keyed to nothing, and over a chosen book it published:

    "... a uniform 18.3% sample ... Every year is represented in proportion to what it won ...
     Divide a booked count by 0.183 to read the supplier rather than the sample."

THE DIVIDE INSTRUCTION IS THE ONE THAT DOES DAMAGE, and it is why this file is about that clause
rather than about the word "uniform". "uniform" is a claim a reader can doubt. `Divide a booked
count by 0.183` is an ARITHMETIC A READER CAN CARRY OUT: it returns a wrong number, in silence,
with nothing on the page to contradict it. Under per-account weights no single number undoes the
sample at all — `settlement_weight` on each row is what reads across to the supplier.

WHY IT SURVIVED EVERY EXISTING CONTROL. **Both selections give a sample rate below one.** Every
assertion in `tests/tools/test_generate_book_growth_data.py` was keyed to the RATE, and the rate
cannot discriminate the two mechanisms. The controls were correct and blind by construction.

THE TWO SUBJECTS, AND WHY BOTH. A door test that builds its own feed controls the RENDER and not
the LIFT: it proves the page would say the right thing IF the feed said so, and stays green for as
long as the feed does not. `3957ba848` landed in exactly that state and said so — the page branch
was inert because `book_growth.json` carried no `settlement_selection`. So:

  * `test_the_rendered_headline_never_tells_a_reader_to_divide_a_CHOSEN_sample` drives the REAL
    door through `site/_live_harness.mjs` over the REAL producer's output. The render leg.
  * `test_the_PUBLISHED_feeds_headline_agrees_with_the_selection_it_declares` reads the published
    bytes. The lift leg.

THE LIFT LEG IS KEYED TO AGREEMENT, NOT TO TODAY'S ANSWER, and that is deliberate. Asserting the
published feed says `chosen_weighted` would pin this control to the mechanism that happens to be
running: the day the budget lifts far enough to settle every win, the rate goes to 1.0, no sample
exists, and a control pinned to `chosen_weighted` would go red on a page that got BETTER. What must
hold whatever runs is that the feed's headline and the feed's own declared selection describe the
SAME mechanism. That can fail, it fails on the exact defect above, and it cannot rot into agreeing
with whatever the code does — because it compares two published fields against each other.

R15 — the mutations, each naming the defect it catches:

  * make `_engine_bound_statement` ignore `selection` (`if False:`) -> both legs red. This is the
    shipped defect, reproduced: one sentence for both mechanisms.
  * default `selection` to `"chosen_weighted"` when the record does not carry it -> the
    fail-closed leg red. Every campaign record older than 2026-09-11 genuinely WAS a uniform cull.
  * drop the `settlement_selection` key from the feed -> the lift leg red, because a headline
    claiming a mechanism the feed does not declare is the state that cannot be checked at all.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_the_published_bytes_reader import (
    published_file,
    published_json,
)

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
HARNESS = SITE / "_live_harness.mjs"

DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
ARMS_REL = "site/data/value_arms.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"

sys.path.insert(0, str(PROJECT))

#: The instruction this file exists to keep off a chosen book's page. Matched case-insensitively
#: on the VERB alone: the damage is the arithmetic and not the capital letter, and a re-worded
#: "you can divide by" would be the same defect in different clothes.
_UNDO_INSTRUCTION = "divide"


def _build(selection: str | None, sample_rate: float | None = 0.2) -> dict:
    """The REAL producer's output for a campaign we control.

    Imported inside the helper so a collection-time ImportError in the tools package reports as
    this file's failure rather than taking the whole selection down with it.
    """
    import tools.generate_book_growth_data as gb

    campaign = {
        "by_year": [
            {"year": 2016 + i, "quotes_issued": 50, "wins": 2, "funnel_wins": 10,
             "wins_refused_by_settlement_budget": 8, "accounts_after": 20 + i,
             "book_after": 20 + i, "spend_gbp": 100.0, "binding": "growth_rate",
             "homes_in_market": 400, "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": None, "planning_on": "belief"}
            for i in range(3)
        ],
        "notes": [], "quotes": 150, "wins": 6, "spend_gbp": 300.0,
        "customer_years_committed": 1195.4, "customer_year_budget": 1200.0,
    }
    if sample_rate is not None:
        campaign["settlement_sample_rate"] = sample_rate
    if selection is not None:
        campaign["settlement_selection"] = selection
    return gb.build(campaign)


def _render(growth: dict) -> dict:
    """Drive the real door with the given growth feed and return its rendered elements.

    FAIL-CLOSED: an unresolved feed, a script error or a missing element all raise here rather
    than degrading to an empty string that a `not in` assertion would happily pass on. An
    unavailable check is a FAILED check.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and "
                    "an unavailable check is a FAILED check (R15)")
    payload = {
        "../data/book_growth.json": growth,
        "../data/capabilities_door.json": published_json(CAPS_REL),
        "../data/value_arms.json": published_json(ARMS_REL),
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(published_file(DOOR_REL))],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is "
        "not what a browser would".format(meta.get("unresolved"))
    )
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return out


def _headline(feed: dict) -> str:
    """What the reader actually meets at the top of the growth curve."""
    el = _render(feed).get("growth-headline")
    assert el is not None, (
        "the door has no `growth-headline` element at all, so what share of its own wins this "
        "machine could settle is nowhere on the page a reader reads"
    )
    text = el if isinstance(el, str) else (el.get("textContent") or el.get("innerHTML") or "")
    assert text.strip(), "the growth headline rendered EMPTY, which no reader can act on"
    return text


# ── THE RENDER LEG ────────────────────────────────────────────────────────────────────────────

def test_the_rendered_headline_never_tells_a_reader_to_divide_a_CHOSEN_sample():
    """THE ASSERTION THAT CARRIES THE FILE. Under a chosen sample no single number undoes the
    selection, so an instruction to divide by one is an arithmetic that returns a wrong answer
    and says nothing about its own wrongness."""
    text = _headline(_build("chosen_weighted"))

    assert _UNDO_INSTRUCTION not in text.lower(), (
        "the page handed a reader one number to undo a CHOSEN sample with, and the per-account "
        "weights it would be undoing span two orders of magnitude: {!r}".format(text)
    )
    assert "uniform" not in text.lower(), text
    # And it must still give the reader a route to the supplier. Deleting the false clauses
    # without replacing them is a different defect: a reader who cannot read across at all.
    assert "settlement_weight" in text, (
        "the headline removed the wrong instruction and put nothing in its place, so a reader "
        "has no way to read the supplier from the sample at all: {!r}".format(text)
    )


def test_the_rendered_headline_STILL_says_divide_when_the_sample_really_was_a_cull():
    """THE OTHER HALF OF THE PARTITION, and without it the control above is satisfied by a page
    that never says `divide` under any mechanism — which would be a real loss. Under the count
    cull `1 / rate` IS the estimator, and telling the reader so is correct."""
    text = _headline(_build("uniform_count"))

    assert _UNDO_INSTRUCTION in text.lower(), (
        "the cull's undo instruction is right THERE and was thrown away with the chooser's: a "
        "uniformly sampled book IS recovered by dividing by the rate: {!r}".format(text)
    )
    assert "uniform" in text.lower(), text


def test_a_record_written_BEFORE_the_chooser_renders_as_the_cull_and_not_as_chosen():
    """FAIL CLOSED on the selection. Every campaign record on this tree older than 2026-09-11
    carries no `settlement_selection`, and those runs really were uniform culls. Defaulting the
    other way would put the chosen prose over a book that was counted off."""
    feed = _build(None)

    assert feed["settlement_selection"] == "uniform_count"
    text = _headline(feed)
    assert "uniform" in text.lower(), text
    assert "CHOSEN" not in text, text


# ── THE LIFT LEG ──────────────────────────────────────────────────────────────────────────────

def test_the_PUBLISHED_feeds_headline_agrees_with_the_selection_it_declares():
    """THE LIFT, and the reason the render leg alone is not enough: `3957ba848` landed a correct
    page branch over a feed that could not trigger it, and every control stayed green.

    KEYED TO AGREEMENT, NOT TO TODAY'S MECHANISM. Whatever selection the published feed declares,
    its published headline must describe THAT mechanism. A feed saying `chosen_weighted` while its
    headline says "uniform" and tells the reader to divide is the defect; a feed that legitimately
    stops sampling altogether (rate 1.0, no sample) is not, and must not red this.
    """
    feed = published_json(FEED_REL)
    statement = feed.get("engine_bound_statement")
    assert isinstance(statement, str) and statement.strip(), (
        "the published growth feed carries no `engine_bound_statement`, so the page's headline "
        "renders empty and what share of its own wins this machine settled reaches nobody"
    )

    rate = feed.get("settlement_sample_rate")
    if not isinstance(rate, (int, float)) or rate >= 1.0:
        # No sample was taken, so there is no selection to agree about and nothing to undo.
        assert _UNDO_INSTRUCTION not in statement.lower(), (
            "the published headline tells a reader to divide by a rate on a run that sampled "
            "NOTHING: {!r}".format(statement)
        )
        return

    selection = feed.get("settlement_selection")
    assert selection is not None, (
        "the published feed declares a sample rate of {} but will not say WHICH sample, so "
        "nothing on this page or off it can check whether its headline is true. Both mechanisms "
        "give a rate below one; the rate cannot tell them apart.".format(rate)
    )

    if selection == "chosen_weighted":
        assert _UNDO_INSTRUCTION not in statement.lower(), (
            "the PUBLISHED feed declares a chosen, per-account-weighted sample and its PUBLISHED "
            "headline still hands the reader one number to undo it with: {!r}".format(statement)
        )
        assert "uniform" not in statement.lower(), statement
        assert "settlement_weight" in statement, statement
    else:
        assert _UNDO_INSTRUCTION in statement.lower(), (
            "the published feed declares selection {!r} — a count cull, which a reader CAN undo "
            "by dividing — and the headline no longer tells them how: {!r}".format(
                selection, statement)
        )
