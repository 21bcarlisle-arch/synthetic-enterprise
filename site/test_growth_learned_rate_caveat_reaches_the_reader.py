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
    `test_a_clean_rate_from_a_SAMPLED_run_is_NOT_marked` red (the null control, and the
    load-bearing one: our engine settling a fifth of the book does not touch the rate the
    company plans on, because the company learns from its FUNNEL).
  * find the rate column by counting cells instead of by its heading ->
    `_rate_cells` raises, which is what it now does rather than silently matching no row (it
    did exactly that on 2026-08-29 when a column was added, and three controls went dark).
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
DD_ARMS = SITE / "data" / "dd_opening_arms.json"

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
        # The door gained a FOURTH feed on 2026-09-03 (the opening direct-debit
        # comparison). Same reason as the line above: the harness rejects a url the
        # caller did not supply, so every feed the door fetches has to be supplied here
        # or this control reds on a page that is fine.
        "../data/dd_opening_arms.json": json.loads(DD_ARMS.read_text(encoding="utf-8")),
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
    """year -> the rendered 'Planned on' cell, from the table the page actually built.

    THE COLUMN IS FOUND BY ITS HEADING, not by counting to seven, and that is the 2026-08-29
    repair. This helper used to accept a row only when it had exactly 7 cells and then read
    index 5. A legitimate column addition -- the `Settled` column, which splits what the market
    gave the company from what this machine could book -- matched no row at all, so every
    `cells[...]` lookup raised `KeyError` and three controls went dark at once. The obvious fix
    is to bump 7 to 8 and 5 to 6, which buys exactly one more column's worth of life.

    A test helper pinned to today's layout is the same defect as a control pinned to today's
    answer: it does not fail when the page is wrong, it fails when the page changes.
    """
    headers = [
        re.sub(r"<[^>]+>", "", h).strip()
        for h in re.findall(r"<th(?:\s[^>]*)?>(.*?)</th>", growth_html, re.S)
    ]
    if "Planned on" not in headers:
        raise AssertionError(
            "the growth table has no 'Planned on' column, so the learned rate a reader is "
            f"supposed to meet is not on the page at all. Headers rendered: {headers}"
        )
    rate_col = headers.index("Planned on")
    cells = {}
    for row in re.findall(r"<tr>(.*?)</tr>", growth_html, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(tds) == len(headers):
            cells[re.sub(r"<[^>]+>", "", tds[0]).strip()] = tds[rate_col]
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

#: Every fixture year quotes this many and its funnel wins this many, so the rate a year SHOULD
#: have planned on is `FUNNEL_WINS / QUOTES` -- the same in every year, which makes a fixture
#: rate either equal to the funnel's history or visibly not.
QUOTES, FUNNEL_WINS = 100, 18


def _fixture_feed(*rates, settled=None) -> dict:
    """A growth feed whose first year plans on belief and whose rest plan on the given rates.

    RE-KEYED 2026-08-29 with the mechanism it drives. The old fixture chose contamination by
    handing years a `binding` of `settlement_engine`; the generator no longer decides that way
    and no shipped campaign produces that binding. What decides it now is whether the rate the
    company DECLARES it planned on equals what its own funnel converted over the earlier years
    -- so a fixture makes a year clean by passing `FUNNEL_WINS / QUOTES` and dirty by passing
    anything else.

    `settled` is what this machine booked, defaulting to the funnel's own count (nothing
    refused). Passing fewer is what a sampled run looks like.
    """
    from tools.generate_book_growth_data import build
    booked = FUNNEL_WINS if settled is None else settled
    return build({
        "by_year": [
            {"year": 2018 + i, "quotes_issued": QUOTES, "wins": booked,
             "funnel_wins": FUNNEL_WINS,
             "wins_refused_by_settlement_budget": FUNNEL_WINS - booked,
             "accounts_after": 50, "book_after": 50,
             "spend_gbp": 100.0, "binding": "growth_rate", "homes_in_market": 400,
             "switching_multiplier": 1.0, "believed_win_rate": 0.2,
             "realised_win_rate_used": rate,
             "planning_on": "belief" if rate is None else "realised"}
            for i, rate in enumerate(rates)
        ],
        "notes": [], "quotes": 100, "wins": 10, "spend_gbp": 1000.0,
        "customer_years_committed": 590.0, "customer_year_budget": 600.0,
        "settlement_sample_rate": booked / FUNNEL_WINS,
    })


def test_a_contaminated_rate_is_MARKED_where_a_reader_meets_it():
    """The defect in its live shape: a company planning on the wins our machine SETTLED rather
    than on the wins its funnel converted. At a sample rate near a fifth those are different
    numbers, and the smaller one is the one that reads as a supplier losing its touch."""
    booked_rate = 4 / QUOTES  # planned on 4 booked wins per 100 quotes, not the 18 it won
    feed = _fixture_feed(None, booked_rate, settled=4)
    cells = _rate_cells(_render(feed)["growth"]["innerHTML"])

    assert MARK in cells["2019"], "a rate our own engine shaped rendered as a plain percentage"
    assert "4.0%" in cells["2019"], "the figure itself must still be shown, not replaced"


def test_a_clean_rate_from_a_SAMPLED_run_is_NOT_marked():
    """THE NULL CONTROL, and it is the load-bearing one. Our engine settling only a fifth of the
    book does NOT contaminate the rate the company planned on -- the company learns from its
    funnel, which the ceiling never touched. Marking these would caveat a commercial number on
    the strength of an unrelated machine limit, and a caveat a reader learns to ignore is worse
    than none."""
    clean = FUNNEL_WINS / QUOTES
    feed = _fixture_feed(None, clean, clean, settled=4)
    cells = _rate_cells(_render(feed)["growth"]["innerHTML"])

    assert MARK not in cells["2018"], "a year that planned on its opening belief was marked"
    assert MARK not in cells["2019"], "a rate equal to the funnel's own history was marked"
    assert MARK not in cells["2020"], (
        "a rate equal to the funnel's own history was marked in a year our engine refused 14 of "
        "the 18 wins -- the sample rate is not the rate the company plans on, and confusing the "
        "two is the defect this fixture exists to keep out"
    )
    assert "18.0%" in cells["2019"], "the figure itself must still be shown"


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
