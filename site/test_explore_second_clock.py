"""Explore's stage 3 must render the day it has always promised, on the page a reader loads.

THE GAP, in the page's own words. Stage 3 is titled *"Two clocks: gas across the years,
electricity across a day"*, and its standfirst says electricity *"answers to the day"*. It then
drew electricity BY YEAR, in the same bar table as gas — so the two clocks were one clock, and
the switch between them, which the director's brief §5.3 calls *"the point"*, was not on screen.

WHY THE SUBJECT IS THE RENDERED DOM. `site/test_published_caveat_reaches_the_reader.py` records
this project's own version of the lesson: for a day a corrected sentence sat in the code and the
tree and not in what a browser put on screen, and nothing was red, because every assertion took
an in-process object as its subject. A feed carrying 48 numbers proves nothing about whether a
reader meets them. So this drives the real page through its own boot path
(`site/_live_harness.mjs`), on the stage under test, and asserts on what it built.

TWO HOUSEHOLDS, DELIBERATELY, because the interesting half is the ABSENCE. A profile-class home
has no day to draw — for the supplier as much as for this page — and stage 3's whole lesson is
that difference. A test that only checked the half-hourly household would pass a page that drew
an invented curve for every meter on the book.

R15 — each proven by reverting, not asserted:
  * drop the `hhDayPanels()` call from `stageUsed` -> `test_the_day_chart_reaches_the_reader`.
  * render a chart for a meter with no record -> `test_a_profile_class_home_gets_an_explanation`.
  * restore the hard-coded "electricity is flatter across the year" note ->
    `test_the_seasonal_note_is_derived_from_this_meter_and_not_asserted`.
  * drop `stageFromHash` -> every test here lands on stage 1 and all of them go red.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "explore" / "index.html"
BOOK = SITE / "data" / "customers.json"
HH_DAYS = SITE / "data" / "explore_hh_days.json"
WEATHER = SITE / "data" / "weather.json"
# The carbon layer stage 3 gained on 2026-08-25 (EP13). Supplied here because the
# harness asserts NO feed goes unresolved -- a door that asks for a file this fixture
# does not hold renders a stated absence, which would silently make every assertion
# below a test of the absence path rather than of the page.
CARBON = SITE / "data" / "explore_carbon.json"

#: The stage under test, as a reader would link to it.
USED = "#used"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _render(first_group: str) -> dict:
    """Drive the real door on stage 3, with `first_group` as the selected household.

    The account selector is not addressable, so the household under test is put first in the
    book the page is handed — the same book, reordered. FAIL-CLOSED: an unresolved feed or a
    script error raises rather than degrading to an empty string a `not in` would pass on.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing — the render check is UNAVAILABLE, and "
                    "an unavailable check is a FAILED check (R15)")
    book = _load(BOOK)
    book["customers"] = sorted(book["customers"],
                               key=lambda c: c.get("customer_group") != first_group)
    assert book["customers"] and book["customers"][0]["customer_group"] == first_group, (
        "the book carries no household called {} — the fixture is stale".format(first_group))

    feeds = {
        "../data/customers.json": book,
        "../data/weather.json": _load(WEATHER),
        "../data/explore_hh_days.json": _load(HH_DAYS),
        "../data/explore_carbon.json": _load(CARBON),
    }
    for customer in book["customers"]:
        for leg in (customer.get("legs") or {}).values():
            path = SITE / "data" / "customers" / "{}.json".format(leg.get("cid"))
            if path.is_file():
                feeds["../data/customers/{}.json".format(leg["cid"])] = _load(path)

    proc = subprocess.run(["node", str(HARNESS), str(DOOR), USED],
                          input=json.dumps(feeds), capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), "the door asked for a feed this test did not supply: {}"\
        .format(meta.get("unresolved"))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return out


def _stage(first_group: str) -> str:
    html = _render(first_group)["stage"]["innerHTML"]
    assert "Used &mdash; how much energy" in html or "Used — how much energy" in html, (
        "the page did not open on stage 3, so nothing below is testing what it claims to. "
        "`#used` is how a reader links to it and how this test reaches it"
    )
    return html


def _a_half_hourly_group() -> str:
    accounts = _load(HH_DAYS).get("accounts") or {}
    if not accounts:
        pytest.fail("no household on this book has a half-hourly record, so the day panel "
                    "cannot be verified — reported as a failure, never skipped")
    return sorted(accounts)[0]


def _a_profile_class_group() -> str:
    without = _load(HH_DAYS).get("accounts_without_half_hourly") or []
    if not without:
        pytest.fail("every household is half-hourly, so the absence branch cannot be verified")
    return without[0]["customer_group"]


# ── the day itself ───────────────────────────────────────────────────────────────────────────

def test_the_day_chart_reaches_the_reader():
    html = _stage(_a_half_hourly_group())
    panel = html.split('<div id="hhday">')[-1]

    bars = re.findall(r'<span class="(?:peak)?"\s+style="height:', panel)
    assert len(bars) >= 48, (
        "stage 3 rendered fewer than one day of settlement periods ({}). Its own title has "
        "promised 'electricity across a day' since it was written".format(len(bars))
    )
    assert 'class="peak"' in panel, "no half hour is marked as the day's peak"


def test_the_day_is_DATED_on_the_face_of_the_panel():
    """One real day, and a reader must be able to go and check it. A panel with no date could
    be an average, and an average is a number this page authored."""
    group = _a_half_hourly_group()
    day = (_load(HH_DAYS)["accounts"][group])["hardest_day"]
    panel = _stage(group).split('<div id="hhday">')[-1]

    year = str(day["date"])[:4]
    assert year in panel, "the panel does not name the year of the day it is drawing"
    assert day["peak_clock"] in panel, "the peak half hour is not named in the clock time"


def test_the_agreement_with_the_companys_own_feed_is_a_MEASUREMENT_on_the_page():
    """The panel claims that for an HH meter the supplier's picture and the world's are the same
    artefact. That is the strongest wall statement on the page and it must carry the number it
    rests on, or it is an assertion in a place that does not make them."""
    group = _a_half_hourly_group()
    corroboration = _load(HH_DAYS)["accounts"][group]["corroboration"]
    panel = _stage(group).split('<div id="hhday">')[-1]

    if corroboration.get("available"):
        assert "periods" in panel and "disagreement" in panel, (
            "the agreement is stated without the comparison behind it"
        )
    else:
        assert "asserted here rather than measured" in panel, (
            "an UNMEASURED agreement is being presented as a measured one — the fail-open this "
            "whole panel would otherwise be"
        )


# ── the absence, which is the lesson ─────────────────────────────────────────────────────────

def test_a_profile_class_home_gets_an_explanation_and_never_an_invented_curve():
    panel = _stage(_a_profile_class_group()).split('<div id="hhday">')[-1]

    assert not re.findall(r'<span class="(?:peak)?"\s+style="height:', panel), (
        "a day curve was drawn for a meter that reports a handful of times a year. Nobody has "
        "that data — not this page and not the supplier — so any curve here is invented"
    )
    assert "inferred from a national" in panel, (
        "the absence is unexplained, so it reads as a broken chart rather than as the thing "
        "stage 3 exists to show"
    )


# ── the sentence the new chart would otherwise contradict ────────────────────────────────────

def test_the_seasonal_note_is_derived_from_this_meter_and_not_asserted():
    """This said "electricity is flatter across the year — lighting, appliances and hot water do
    not track the weather", which is true of a gas-heated home and plainly false of the
    electrically-heated ones on this book. A sentence contradicted by the chart under it is
    worse than no sentence."""
    html = _stage(_a_half_hourly_group())

    assert "do not track the weather" not in html, (
        "the hard-coded flatness claim is back, on a page that now prints the winter day "
        "beside the summer one"
    )
    assert re.search(r"Winter months run <b>?[\d.]+&times;|Winter months run [\d.]+×|"
                     r"Winter months run <b>[\d.]+×", html) or "Winter months run" in html, (
        "the electricity panel no longer says how this meter actually moves with the seasons"
    )


# ---------------------------------------------------------------------------
# The carbon layer (EP13, 2026-08-25) -- the mission's own number, on the same days
# ---------------------------------------------------------------------------
#
# WHY IT IS TESTED HERE rather than in its own file: it renders inside stage 3, from the same
# two dated days, for the same two households. Splitting it off would mean a second copy of the
# fixture above and two places to notice that the day the consumption panel shows is not the day
# the carbon panel costs.
#
# THE ASYMMETRY IS AGAIN THE INTERESTING HALF, exactly as for the day chart: 249 of 263 accounts
# have a traditional meter, and for every one of them the honest answer is that the timing effect
# is UNAVAILABLE. A page that printed 0% there would be claiming a measurement nobody made, in a
# column where three of the entries are real -- which is the more expensive error, because it
# reads as good news.

def test_the_carbon_figure_reaches_the_reader_on_a_measured_household():
    """MUTATION (must fire): drop the `carbonPanels()` call from `stageUsed`."""
    html = _stage("C7")

    assert "kg CO&#8322;e" in html or "kg CO₂e" in html, (
        "stage 3 renders no carbon figure at all for a household whose meter reports every "
        "half hour, which is the only kind that can have one"
    )
    assert "EMISSIONS, NOT ABATEMENT" in html.upper(), (
        "the panel does not say which of the two it is, and a reader has every reason to read "
        "the kilograms as the mission's score"
    )


def test_the_timing_effect_is_stated_AGAINST_the_annual_method_it_replaces():
    """The number that is new information rather than a restatement. Without the flat
    counterpart beside it, "29.0 kg" is a quantity; with it, it is a claim about timing."""
    html = _stage("C7")

    assert "annual-average method" in html, (
        "the panel gives a carbon figure with nothing to compare it against, so the reader "
        "cannot tell whether timing mattered here at all"
    )
    assert re.search(r"\d+% (higher|lower)</b> than the annual-average method", html), (
        "no timing effect is rendered as a percentage against the annual method"
    )


def test_a_PROFILED_household_is_told_the_timing_effect_is_UNAVAILABLE_and_never_zero():
    """THE EXPENSIVE ERROR, and the one this page is built to refuse. C1 has a traditional
    meter. Its emissions are known; when it drew is not recorded and no estimate recovers it.

    MUTATION (must fire): return 0.0 from `Footprint.timing_effect_pct` for a profiled account
    instead of raising, and render it.
    """
    html = _stage("C1")

    assert "unavailable" in html.lower() and "not zero" in html.lower(), (
        "a profiled household is not told that its timing effect is unavailable rather than zero"
    )
    assert not re.search(r"\d+% (higher|lower)</b> than the annual-average method", html), (
        "a household with no half-hourly meter was given a timing effect anyway"
    )


def test_the_page_carries_the_direction_its_errors_point_in():
    """Both of the shape's largest gaps -- no coal, no interconnector imports -- make quiet half
    hours look cleaner than they were, so a timing benefit read off it is an upper bound. That
    flatters the mission's own thesis, which is exactly why it belongs on the page and not in a
    module docstring."""
    html = _stage("C7")

    assert "UPPER BOUND" in html, (
        "the page states a timing benefit without stating that it is an upper bound"
    )


def test_the_coverage_is_DERIVED_and_names_how_few_households_are_measured():
    """A carbon figure without its sample size is a slogan (advisor scope brief, 2026-08-04).
    And the sentence must MOVE when a smart meter is fitted, so it is built from the counts
    rather than written beside them."""
    html = _stage("C1")
    carbon = _load(CARBON)
    measured = carbon["counts"]["measured"]
    total = sum(carbon["counts"].values())

    assert "{} of {} account(s) are MEASURED".format(measured, total) in html, (
        "the page's coverage sentence is not the one derived from the live counts"
    )
