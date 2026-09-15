"""The figure the growth headline sends a reader to BY NAME must have a cell on the page.

THE DEFECT IT SERVES. `3957ba848` replaced the count cull with a chooser, and the headline
`_engine_bound_statement` builds for a chosen book ends:

    "... each settled account carries its own weight in the company's own wins, and
     `settlement_weight` on each row below is what reads across to the supplier."

`7ecefdaf7` then made that true of the FEED: every published row of `site/data/book_growth.json`
carries `settlement_weight`, and on this book each year's weight reconstructs that year's funnel
wins EXACTLY — 24/32/46/70/72/59/20/56/83/38 against settled counts of 9/6/6/12/11/9/5/5/16/4,
which are not proportional to them at all.

**And the table rendered eight columns, none of them that one.** The headline said "on each row
below" and no row below had a cell for it. A reader who did exactly what the page told them to do
found nothing, and the only route to the figure was opening the JSON. A pointer whose referent
renders nowhere is the same defect as a pointer with no referent — which is the defect
`7ecefdaf7` had just fixed at the other end of the same sentence. **Probe BOTH ends of a pointer.**

WHY THE EXISTING CONTROLS COULD NOT SEE IT.
`test_the_chosen_sample_reaches_the_reader_without_a_divide_instruction` asserts
`"settlement_weight" in text` — but `text` there is the HEADLINE, so it is checking that the
sentence names the field, which is precisely the half that was already true.
`tests/tools/test_generate_book_growth_data` checks the field reaches the FEED. Both ends were
controlled and the span between them was not.

THE THREE LEGS, and why none of them can be dropped:

  * **RENDER** — the real door, driven over a feed this file controls, puts each row's
    `settlement_weight` in a cell. Catches the shipped defect: no column at all.
  * **THE RARE BRANCH CAN BE TAKEN** — a year whose weight does NOT reconstruct its funnel wins
    renders MARKED. Without this leg the cell is one that could only ever agree, because on the
    chosen book every year reconstructs to 0.0% and a cell that silently blends a 60% miss into
    the same grey text would pass every other assertion here. This is the leg keyed to the
    PROPERTY — *does this year's weight reconstruct what the company won* — rather than to the
    zeros today's book happens to return.
  * **LIFT** — the PUBLISHED bytes rendered by the PUBLISHED door agree, row for row. A door test
    that builds its own feed controls the render and not the lift: it proves the page would say
    the right thing IF the feed said so, and stays green for as long as the feed does not.

THE LIFT LEG IS KEYED TO AGREEMENT, NOT TO A VALUE. It asserts the rendered cell says what the
feed says — em-dash exactly when the feed says `null`, the number otherwise. Pinning it to
"every published row carries a weight" would go red the day the settlement budget lifts far
enough that no sample exists, on a page that got BETTER; pinning it to 24.0 would go red on any
re-run. Comparing two published things against each other cannot rot into agreeing with whatever
the code does.

R15 — the mutations, each naming the defect it catches:

  * delete the `stands` cell from the row -> RENDER and LIFT red. The shipped defect, reproduced.
  * render `w == null` as `0.0` instead of an em-dash -> the absent leg red. A year that stands
    for nothing and a year we cannot say for are different claims and zero is the flattering one.
  * drop the `wrong` flag (`var wrong = false`) -> the rare-branch leg red, and ONLY that leg.
    This is the mutation that proves the column reports rather than merely displays.
  * round the cell to `toFixed(0)` -> the lift leg red, because the rendered cell stops agreeing
    with the feed it claims to carry.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# REUSED, not rebuilt: the sibling door test already owns the node harness contract -- payload
# shape, the unresolved-feed and scriptError fail-closed checks. A second copy of that would be a
# second thing to fix when `_live_harness.mjs` changes, and the two files render the SAME door.
from test_the_chosen_sample_reaches_the_reader_without_a_divide_instruction import _render
from test_the_published_bytes_reader import published_json

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
FEED_REL = "site/data/book_growth.json"

sys.path.insert(0, str(PROJECT))

#: The header the reader looks for. Matched on the rendered header text, so a column that exists
#: under a different name still has to be found by the same route a reader would use.
_COLUMN = "Stands for"

#: What an absent weight must render as. The character, not the entity, because the assertion is
#: about what a READER sees.
_ABSENT = "—"


def _build(weights, funnel):
    """The REAL producer's feed for a campaign whose per-year weights this test sets.

    `funnel` is per-year, and it is a LIST rather than one number because the flag is a statement
    about the DISTANCE between a year's weight and its own funnel count. The first draft passed a
    single funnel for every year alongside three different weights, so two rows were flagged
    correctly and the test read it as the column carrying the wrong values. Kept as a list so the
    fixture cannot quietly disagree with itself again.

    Imported inside the helper so a collection-time ImportError in the tools package reports as
    this file's failure rather than taking the whole selection down with it.
    """
    import tools.generate_book_growth_data as gb

    funnels = [funnel] * len(weights) if isinstance(funnel, int) else list(funnel)
    assert len(funnels) == len(weights), "the fixture names {} weights and {} funnel counts".format(
        len(weights), len(funnels))
    by_year = []
    for i, (w, fw) in enumerate(zip(weights, funnels)):
        row = {"year": 2016 + i, "quotes_issued": 50, "wins": 2, "funnel_wins": fw,
               "wins_refused_by_settlement_budget": fw - 2, "accounts_after": 20 + i,
               "book_after": 20 + i, "spend_gbp": 100.0, "binding": "growth_rate",
               "homes_in_market": 400, "switching_multiplier": 1.0, "believed_win_rate": 0.2,
               "realised_win_rate_used": None, "planning_on": "belief"}
        # ABSENT means the KEY IS MISSING, which is what a record written before the weights
        # existed really looks like -- not a key present and set to None by this test.
        if w is not None:
            row["settlement_weight"] = w
        by_year.append(row)
    campaign = {
        "by_year": by_year, "notes": [], "quotes": 150, "wins": 2 * len(weights),
        "spend_gbp": 300.0, "customer_years_committed": 1194.9, "customer_year_budget": 1200.0,
        "settlement_sample_rate": 0.2, "settlement_selection": "chosen_weighted",
    }
    return gb.build(campaign)


def _table(feed):
    """The growth table the door actually built, as `(headers, [[cell, ...], ...])`.

    FAIL-CLOSED: a missing element or a table with no header row raises here rather than yielding
    an empty list that an `all(...)` assertion would pass on vacuously.
    """
    el = _render(feed).get("growth")
    assert el is not None, (
        "the door has no `growth` element at all, so the growth curve is nowhere on the page"
    )
    html = el if isinstance(el, str) else (el.get("innerHTML") or el.get("textContent") or "")
    assert html.strip(), "the growth table rendered EMPTY, which no reader can act on"

    # The whole `<th>` content with its markup stripped, rather than the first text run: a header
    # wrapped in a `<span>` for a tooltip is the same header to a reader, and matching only the
    # leading run would report it as an empty column name.
    headers = [re.sub(r"<[^>]+>", "", h).strip()
               for h in re.findall(r"<th[^>]*>(.*?)</th>", html, re.S)]
    assert headers, "the growth table rendered no header row, so no column can be located by name"
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if cells:
            rows.append(cells)
    assert rows, "the growth table rendered a header and NO rows, so nothing reaches the reader"
    return headers, rows


def _column(feed):
    """Every row's raw `Stands for` cell, in year order."""
    headers, rows = _table(feed)
    if _COLUMN not in headers:
        pytest.fail(
            "the growth table has no {!r} column, so the ONLY figure the headline tells a reader "
            "reads across to the supplier -- `settlement_weight` -- is nowhere on the page they "
            "were sent to. The columns are {}".format(_COLUMN, headers)
        )
    i = headers.index(_COLUMN)
    return [r[i] for r in rows]


def _text(cell):
    """What a reader sees in the cell, with the markup and the HTML entities resolved."""
    bare = re.sub(r"<[^>]+>", "", cell)
    return (bare.replace("&mdash;", _ABSENT).replace("&#9888;", "⚠")
            .replace("&amp;", "&").strip())


# ── THE RENDER LEG ────────────────────────────────────────────────────────────────────────────

def test_every_row_carries_the_weight_the_headline_sends_the_reader_to():
    """THE ASSERTION THAT CARRIES THE FILE. The headline names `settlement_weight` "on each row
    below"; this is the control that there IS a cell on each row below."""
    cells = _column(_build([24.0, 32.0, 46.0], funnel=[24, 32, 46]))

    assert len(cells) == 3, cells
    rendered = [_text(c) for c in cells]
    assert rendered == ["24.0", "32.0", "46.0"], (
        "the column exists but does not carry the feed's own weights, so a reader comparing it "
        "against the Won column is reading something else: {!r}".format(rendered)
    )


def test_a_year_whose_weight_is_absent_renders_ABSENT_and_never_zero():
    """A year that stands for nothing and a year we cannot say for are different claims, and 0.0
    is the flattering one. Records written before the weights existed are the real population
    here, not a hypothetical."""
    rendered = [_text(c) for c in _column(_build([None, None], funnel=[24, 32]))]

    assert rendered == [_ABSENT, _ABSENT], (
        "an absent weight rendered as {!r}. A number there is a claim the record cannot "
        "support".format(rendered)
    )
    for bad in ("0", "0.0", "null", "undefined", "NaN"):
        assert bad not in rendered, (
            "an absent weight rendered as {!r}, which reads as a measured figure".format(bad))


# ── THE RARE BRANCH CAN BE TAKEN ──────────────────────────────────────────────────────────────

def test_a_year_the_sample_FAILS_to_reconstruct_is_marked_and_one_it_reconstructs_is_not():
    """THE LEG THAT PROVES THE CELL REPORTS RATHER THAN DISPLAYS.

    Both branches are asserted in ONE test, over one partition, because a control that only ever
    saw the agreeing case would pass just as happily against a cell that can never disagree —
    which is exactly what the chosen book's ten identical zeros would have given it.

    This is also not a hypothetical branch. Under the count cull the weight is `settled / rate`,
    which cannot reproduce a year the sampling thinned, and that is the mechanism this page runs
    whenever the chooser refuses.
    """
    # 24 against a funnel of 24 reconstructs; 9 against 24 is 62.5% out, which is roughly what a
    # uniform cull returns for a year it under-sampled.
    cells = _column(_build([24.0, 9.0], funnel=[24, 24]))
    good, bad = _text(cells[0]), _text(cells[1])

    assert "⚠" in bad, (
        "a year whose settled accounts stand for 9.0 of the 24 wins the company made — a 62% "
        "miss — rendered unmarked as {!r}, so a sample that does not reconstruct the year looks "
        "exactly like one that does".format(bad)
    )
    assert "⚠" not in good, (
        "a year the sample reconstructs EXACTLY rendered marked as {!r}. A cell that flags "
        "everything reports nothing".format(good)
    )
    # And the mark has to be a mark, not the whole cell replaced by a warning: the number is what
    # the reader compares against the Won column.
    assert "9.0" in bad, bad


# ── THE LIFT LEG ──────────────────────────────────────────────────────────────────────────────

def test_the_PUBLISHED_door_renders_the_PUBLISHED_feeds_own_weights():
    """The published bytes, through the published door, row for row.

    KEYED TO AGREEMENT, NOT TO A VALUE. Whatever `book_growth.json` says each year stands for,
    that is what the page must show — em-dash exactly where the feed says nothing. Asserting the
    weights are present, or that they equal 24.0, would both go red on a page that got better.
    """
    feed = published_json(FEED_REL)
    if not feed.get("available"):
        pytest.skip("no campaign record is published, so there is no growth table to render")

    cells = _column(feed)
    years = feed["years"]
    assert len(cells) == len(years), (
        "the door rendered {} rows for a feed carrying {} years, so the column cannot be read "
        "against the feed at all".format(len(cells), len(years))
    )

    disagreed = []
    for year, cell in zip(years, cells):
        shown = _text(cell)
        weight = year.get("settlement_weight")
        expected = _ABSENT if weight is None else "{:.1f}".format(weight)
        if not shown.startswith(expected):
            disagreed.append((year.get("year"), weight, shown))
    assert not disagreed, (
        "the published page shows a different figure from the published feed it claims to carry, "
        "on (year, feed, page): {}".format(disagreed)
    )
