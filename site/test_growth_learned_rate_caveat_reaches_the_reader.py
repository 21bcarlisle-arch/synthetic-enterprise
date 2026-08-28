"""The learned-conversion-rate caveat must reach the RENDERED page, not just the feed.

THE DEFECT IT SERVES.
`WORKER_FINDING_THE_COMPANY_NOW_LEARNS_A_WIN_RATE_FROM_YEARS_AN_ENGINEERING_CAP_DECIDED_2026-08-24`
recorded that the company's realised win rate decays 0.169 -> 0.051 across years whose outcome
OUR settlement engine decided, and that `expected_quotes_per_win` inverts that into ever-larger
quote budgets and therefore into published acquisition spend. Its own closing line is the reason
this file exists: *"Any reading of the form 'the company's conversion collapsed after 2020' is an
artefact of this entry, not a result."* Until now that sentence lived in a staging document, and
the decaying series was published on `/capabilities/` with nothing beside it.

The director's instruction, 2026-08-24 console: *"if our own code binds growth rather than the
simulated economics, say so on the site."* `f6c465e44` did that for the CURVE. The learned rate is
the second artefact of the same cap, and it is the one a reader is most likely to misread, because
a falling conversion rate looks exactly like a supplier losing its touch.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. This project's own
`test_published_caveat_reaches_the_reader.py` records the class: for a day the corrected sentence
was in the code and in the working tree and NOT in what a browser put on screen, and nothing was
red, because every assertion took an in-process object as its subject. A feed carrying
`win_rate_statement` proves nothing about whether a reader meets it. So this drives the REAL page
through its own boot path with `site/_live_harness.mjs` -- the same harness `live_pixel_verify`
points at poesys.net -- and asserts on what the page actually rendered.

R15, and the mutations are cheap to state because the page is the subject:
  * delete the `growth-winrate` paragraph or its assignment ->
    `test_the_caveat_reaches_the_rendered_page` red.
  * render the rate without the contamination mark ->
    `test_a_contaminated_rate_is_MARKED_where_a_reader_meets_it` red.
  * mark every rate ->
    `test_a_clean_rate_from_an_engine_bound_year_is_NOT_marked` red (the null control, and the
    load-bearing one: 2020 was engine-bound AND its learned rate came from four commercial years).
  * add a header without its cell, or a cell without its header ->
    `test_the_rendered_table_body_matches_its_own_header` red.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "capabilities" / "index.html"
FEED = SITE / "data" / "book_growth.json"
CAPS = SITE / "data" / "capabilities_door.json"
ARMS = SITE / "data" / "value_arms.json"

#: The page renders this next to a figure our own engine helped produce.
MARK = "&#9888;"


def _render(growth: dict) -> dict:
    """Drive the real door with the given growth feed and return its rendered elements.

    FAIL-CLOSED: an unresolved feed, a script error or a missing element all raise here rather
    than degrading to an empty string a `not in` assertion would happily pass on.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and "
                    "an unavailable check is a FAILED check (R15)")
    payload = {
        "../data/book_growth.json": growth,
        "../data/capabilities_door.json": json.loads(CAPS.read_text(encoding="utf-8")),
        # The door gained a third feed on 2026-08-28 (the flat-rules baseline comparison). The
        # harness REJECTS a url the caller did not supply -- deliberately, so a page driven with
        # a feed missing runs its real error path rather than a vacuous one -- so every feed the
        # door fetches has to be supplied here or this control reds on a page that is fine.
        "../data/value_arms.json": json.loads(ARMS.read_text(encoding="utf-8")),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
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


def _live_feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


def _rate_cells(growth_html: str) -> dict[str, str]:
    """year -> the rendered 'Planned on' cell, from the table the page actually built."""
    cells = {}
    for row in re.findall(r"<tr>(.*?)</tr>", growth_html, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(tds) == 7:
            cells[re.sub(r"<[^>]+>", "", tds[0]).strip()] = tds[5]
    return cells


# ── the sentence ─────────────────────────────────────────────────────────────────────────────

def test_the_caveat_reaches_the_rendered_page():
    feed = _live_feed()
    if not feed.get("available"):
        pytest.fail("the published growth feed is unavailable, so the door renders no curve and "
                    "this control cannot run -- reported as a failure, never skipped")

    rendered = _render(feed)["growth-winrate"]["textContent"]

    assert rendered.strip(), (
        "the door rendered NOTHING where the learned-rate caveat goes. The feed can carry the "
        "sentence and the reader still never meet it -- that is the whole class this file guards"
    )
    assert rendered.strip() == (feed.get("win_rate_statement") or "").strip(), (
        "the page is serving a different sentence from the one the generator authored"
    )


# ── the marks, against the live feed: the RELATIONSHIP, not this run's years ──────────────────

def test_every_contaminated_year_and_only_those_is_marked_in_the_live_table():
    """Data-independent on purpose. Pinning "2021 onward" would go red the day the engine cap
    moves, which is the outcome we are working toward -- so the invariant is the correspondence
    between the feed's own flag and the mark a reader sees."""
    feed = _live_feed()
    if not feed.get("available"):
        pytest.fail("the published growth feed is unavailable; see above")

    cells = _rate_cells(_render(feed)["growth"]["innerHTML"])
    assert cells, "the door rendered no growth rows at all"

    for year in feed["years"]:
        cell = cells.get(str(year["year"]))
        assert cell is not None, "year {} is in the feed and not in the rendered table".format(
            year["year"])
        assert (MARK in cell) is bool(year["learned_win_rate_is_contaminated"]), (
            "year {}: feed says contaminated={}, the rendered cell says otherwise ({!r})".format(
                year["year"], year["learned_win_rate_is_contaminated"], cell)
        )


# ── the discrimination, pinned against a fixture so no run's data can hollow it out ───────────

def _fixture_feed(*specs) -> dict:
    """A growth feed of (binding_is_our_artefact, contaminated, rate) years, generator-shaped."""
    from tools.generate_book_growth_data import build
    return build({
        "by_year": [
            {"year": 2018 + i, "quotes_issued": 100, "wins": 10, "accounts_after": 50,
             "spend_gbp": 100.0, "binding": binding, "homes_in_market": 400,
             "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": rate, "planning_on": "realised"}
            for i, (binding, rate) in enumerate(specs)
        ],
        "notes": [], "quotes": 100, "wins": 10, "spend_gbp": 1000.0,
        "customer_years_committed": 590.0, "customer_year_budget": 600.0,
    })


def test_a_contaminated_rate_is_MARKED_where_a_reader_meets_it():
    feed = _fixture_feed(("settlement_engine", 0.17), ("settlement_engine", 0.12))
    cells = _rate_cells(_render(feed)["growth"]["innerHTML"])

    assert MARK in cells["2019"], "a rate our own engine shaped rendered as a plain percentage"
    assert "12.0%" in cells["2019"], "the figure itself must still be shown, not replaced"


def test_a_clean_rate_from_an_engine_bound_year_is_NOT_marked():
    """THE NULL CONTROL, and it is the real 2020 row. That year WAS bound by our engine and still
    won 22 accounts, so the rate it planned on came from four commercial years. Marking it would
    make the mark meaningless, and a caveat a reader learns to ignore is worse than none."""
    feed = _fixture_feed(("growth_rate", 0.16), ("settlement_engine", 0.169),
                         ("settlement_engine", 0.178))
    cells = _rate_cells(_render(feed)["growth"]["innerHTML"])

    assert MARK not in cells["2018"], "a wholly commercial year was marked"
    assert MARK not in cells["2019"], (
        "the FIRST engine-bound year's own learned rate was marked. It was computed before that "
        "year's losses existed, so there is nothing wrong with it -- this is the discrimination "
        "the whole flag is for"
    )
    assert MARK in cells["2020"], "the year that inherited the contaminated history is unmarked"


# ── the shape of the table my own edit could have broken ──────────────────────────────────────

def test_the_rendered_table_body_matches_its_own_header():
    """A column added to the header and not to the row (or the reverse) skews every cell after it
    silently -- the reader sees a number under the wrong heading, which is worse than a missing
    column because nothing looks broken."""
    html = _render(_live_feed())["growth"]["innerHTML"]
    # `<th(?:\s...)?>` and not `<th[^>]*>`, which also matches `<thead>` and would count one
    # header too many -- a control that fails on a correct table is how a lane learns to skip it.
    headers = re.findall(r"<th(?:\s[^>]*)?>", html)
    assert headers, "the growth table rendered no header"

    bodies = [re.findall(r"<td[^>]*>", row)
              for row in re.findall(r"<tr>(.*?)</tr>", html, re.S)]
    bodies = [b for b in bodies if b]
    assert bodies, "the growth table rendered no data rows"
    for cells in bodies:
        assert len(cells) == len(headers), (
            "a row has {} cells against {} headers".format(len(cells), len(headers)))
