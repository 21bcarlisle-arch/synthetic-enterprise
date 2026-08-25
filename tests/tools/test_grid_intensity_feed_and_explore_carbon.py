"""R15 contract for the two generators that put a carbon number on the site.

WHAT THESE GUARD is not arithmetic -- `tests/sim/test_grid_carbon_intensity.py` and
`tests/company/carbon/test_half_hourly_footprint.py` own that. What is guarded here is the
PLUMBING, which is where this class of work actually fails in this repository: a generator with
no caller, a feed whose window silently excludes the days anyone has meter reads for, a page
promising a number for a day the data cannot supply, and a coverage sentence typed by hand
beside a generated one.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import generate_explore_carbon as gec
from tools import generate_grid_intensity_feed as gif

REPO = Path(__file__).resolve().parents[2]
PUBLISH_PATH = REPO / "background" / "process_run_complete.py"
FEED = REPO / "docs" / "market_data" / "grid_intensity_feed.json"
CARBON = REPO / "site" / "data" / "explore_carbon.json"


# --------------------------------------------------------------------------- #
# The window -- the defect this pair had on its first run                      #
# --------------------------------------------------------------------------- #

def test_the_feed_carries_the_DAYS_ANYONE_HAS_METER_READS_FOR_not_just_a_trailing_window():
    """THE FAILURE, MEASURED. The first version published a flat fortnight of half hours. The
    Explore page's named days are chosen from a meter's ten-year record -- 2021-02-11,
    2022-12-15, 2025-01-10 -- and every one of them fell outside it, so the page would have
    shown a household's half-hourly consumption beside no carbon at all. Not zero carbon: none,
    silently, with nothing in the tree able to notice.

    A supplier pulls the history it has meter data for; NESO's API serves any half hour back to
    2018. The bound here is a file-size decision and must never become the reason a day the
    company CAN measure goes unmeasured.

    MUTATION (must fire): drop `extra_dates` from the `build()` call in `generate()`.
    """
    shape = {("2019-05-05", p): 1.0 for p in range(1, 49)}
    shape.update({("2025-06-06", p): 1.0 for p in range(1, 49)})
    demand = {k: 30_000.0 for k in shape}

    built = gif.build(shape, demand, window_days=14, extra_dates={"2019-05-05"})
    days = {r["date"] for r in built["records"]}

    assert "2019-05-05" in days, "a day with meter reads was outside the window and was dropped"
    assert "2025-06-06" in days
    assert built["records_cover"]["extra_days_carried_for_meter_reads"] == ["2019-05-05"], (
        "the feed does not say that it reached outside its own window, so a reader cannot tell "
        "the trailing bound from the end of the data"
    )


def test_MUTATION_a_day_NOBODY_has_reads_for_is_NOT_carried():
    """The null. Without it, "carries the days with reads" is also satisfied by carrying every
    day, which is the 1.24 MB file this bound exists to avoid."""
    shape = {("2019-05-05", 1): 1.0, ("2025-06-06", 1): 1.0}
    demand = {k: 30_000.0 for k in shape}

    built = gif.build(shape, demand, window_days=14, extra_dates=set())

    assert {r["date"] for r in built["records"]} == {"2025-06-06"}


def test_dates_with_reads_survives_a_missing_or_broken_artefact(tmp_path):
    """A feed that cannot be built because one optional input is absent is worse than a feed
    with a shorter window. The trailing window must still publish."""
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"accounts": {"C7": {"day": {"date": "2021-02-11"}}}}))
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")

    found = gif.dates_with_reads((good, broken, tmp_path / "absent.json"))

    assert found == {"2021-02-11"}


# --------------------------------------------------------------------------- #
# The feed says what it is                                                     #
# --------------------------------------------------------------------------- #

def test_the_feed_carries_its_basis_its_gaps_and_which_way_they_point():
    """The advisor's scope brief makes this the condition of publishing at all: "a carbon figure
    without its basis is not a measurement, it is a slogan". A consumer that is not told cannot
    say, and the page quotes these fields rather than restating them."""
    shape = {("2025-06-06", p): 1.0 for p in range(1, 49)}
    built = gif.build(shape, {k: 30_000.0 for k in shape})

    assert "dimensionless" in built["basis"]
    assert built["named_gaps"], "the feed publishes no gaps at all"
    assert "UPPER BOUND" in built["error_direction"], (
        "the feed does not say which way its errors point, and both of the big ones flatter us"
    )
    assert "carbon_emissions" in built["how_to_use"], (
        "the feed does not tell a reader whose annual level to multiply it by, which is the one "
        "thing it cannot supply itself"
    )


def test_the_feed_refuses_to_publish_an_empty_shape():
    """R15 fail-silent: a feed of no half hours would give every consumer a flat answer and a
    timing effect of exactly zero -- the instrument's failure rendered as a fact about the grid."""
    with pytest.raises(gif.ShapeUnavailable):
        gif.build({}, {})


# --------------------------------------------------------------------------- #
# The page's own absences                                                      #
# --------------------------------------------------------------------------- #

def test_a_day_the_page_shows_CONSUMPTION_for_but_cannot_cost_is_NAMED_not_dropped():
    """A day rendered with a consumption chart and no carbon figure, and no sentence, leaves the
    reader deciding for himself whether the number is zero. Both of these occurred on the first
    real run: 2016-01-01 predates Elexon's outturn entirely, and 2022-06-24 sits in a gap in the
    wind-and-solar series."""
    hh_days = {"accounts": {"C7": {
        "hardest_day": {"date": "2016-01-01", "periods": [1.0] * 48},
        "summer_day": {"date": "2025-06-06", "periods": [1.0] * 48},
    }}}
    shape = {("2025-06-06", p): 1.0 for p in range(1, 49)}
    feed = {"series_covers": {"from": "2016-03-01", "to": "2025-06-07"}}

    built = gec.build(hh_days, shape, feed, {"accounts": 263, "half_hourly_capable": 14})
    by_date = {a["date"]: a for a in built["accounts"]}

    assert "unavailable" in by_date["2016-01-01"]
    assert "outside the published grid-intensity series" in by_date["2016-01-01"]["unavailable"]
    assert "co2e_kg_timed" in by_date["2025-06-06"]


def test_the_two_KINDS_of_absence_are_told_apart():
    """"No data" covers a day before the series starts and a gap inside it, and a reader must not
    have to guess which. One is a known limit of the source; the other looks like a bug."""
    outside = gec._why_unavailable("2015-01-01", {"series_covers": {"from": "2016-03-01", "to": "2025-06-07"}})
    inside = gec._why_unavailable("2022-06-24", {"series_covers": {"from": "2016-03-01", "to": "2025-06-07"}})

    assert "outside the published" in outside
    assert "inside the published series" in inside
    assert outside != inside


def test_the_coverage_sentence_on_the_page_is_DERIVED_from_the_book(tmp_path):
    """The page's sentence must move when a smart meter is fitted. This repo has already filed
    the page that told three households they had no smart meter when they did."""
    hh_days = {"accounts": {"C7": {"d": {"date": "2025-06-06", "periods": [1.0] * 48}}}}
    shape = {("2025-06-06", p): 1.0 for p in range(1, 49)}

    small = gec.build(hh_days, shape, {}, {"accounts": 10, "half_hourly_capable": 2})
    large = gec.build(hh_days, shape, {}, {"accounts": 263, "half_hourly_capable": 14})

    assert "1 of 10" in small["coverage_statement"]
    assert "1 of 263" in large["coverage_statement"]
    assert small["half_hourly_capable_meters"] == 2 and large["half_hourly_capable_meters"] == 14


def test_the_page_data_says_ABATEMENT_IS_NOT_MEASURED_in_its_own_words():
    """The mission's score is £ per tonne ABATED and this pipeline produces EMISSIONS. If the
    page ever stops carrying that sentence, a reader has every reason to read the kilograms as
    the score -- and the front door's NOT YET MEASURED tag becomes a contradiction rather than
    a caveat."""
    built = gec.build({"accounts": {}}, {}, {}, {"accounts": 0, "half_hourly_capable": 0})

    assert built["abatement"]["measured"] is False
    assert "a world that did not happen" in built["abatement"]["why"]
    assert "NOT YET MEASURED" in built["abatement"]["why"]
    assert any("abatement" in n for n in built["not_included"])


# --------------------------------------------------------------------------- #
# Wiring -- a generator with no caller is a file                               #
# --------------------------------------------------------------------------- #

def test_BOTH_generators_are_wired_into_the_publish_cycle():
    """The `no_caller_and_never_runs` class, and this pair is a textbook candidate for it: the
    page would render, from a file that was correct on the day it was written and frozen ever
    after. `explore_hh_days.json` is wired for exactly this reason and says so."""
    source = PUBLISH_PATH.read_text(encoding="utf-8")

    assert "tools.generate_grid_intensity_feed" in source
    assert "tools.generate_explore_carbon" in source


def test_the_feed_is_generated_BEFORE_the_page_that_reads_it():
    """ORDER IS LOAD-BEARING HERE, which is unusual enough to pin. The feed sizes its record
    window from the dated days `generate_explore_hh_day` publishes, and the carbon page reads
    the feed. Built in the wrong order the feed carries a fortnight, the page finds no half
    hours for the days it is showing, and every panel reads UNAVAILABLE on a tree where
    everything works."""
    source = PUBLISH_PATH.read_text(encoding="utf-8")
    hh_day = source.index("tools.generate_explore_hh_day")
    feed = source.index("tools.generate_grid_intensity_feed")
    carbon = source.index("tools.generate_explore_carbon")

    assert hh_day < feed < carbon, (
        "the publish cycle builds these out of order, so the feed cannot know which days need "
        "covering and the page cannot find the days it shows"
    )


# --------------------------------------------------------------------------- #
# The live artefacts                                                           #
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not (FEED.is_file() and CARBON.is_file()),
                    reason="the generated artefacts are not present in this tree")
def test_EVERY_day_the_LIVE_page_shows_has_either_a_figure_or_a_reason():
    carbon = json.loads(CARBON.read_text(encoding="utf-8"))
    for row in carbon["accounts"]:
        assert ("co2e_kg_timed" in row) != ("unavailable" in row), (
            f"{row['account_id']} on {row.get('date')} has neither a carbon figure nor a stated "
            "reason, or somehow both"
        )


@pytest.mark.skipif(not CARBON.is_file(), reason="the carbon layer has not been generated here")
def test_the_LIVE_page_measures_FEWER_accounts_than_have_a_capable_meter():
    """A published fact worth keeping true by test rather than by memory: 14 accounts have a
    meter that COULD record a half hour and 7 have a published half-hourly day. If these ever
    became equal the page's two numbers would be one number, and the read-frequency gap -- which
    is a consent problem, not a metering one -- would vanish from the site without anyone
    deciding it should."""
    carbon = json.loads(CARBON.read_text(encoding="utf-8"))
    measured = carbon["counts"]["measured"]
    capable = carbon["half_hourly_capable_meters"]

    assert 0 < measured <= capable <= carbon["accounts_on_book"], (
        f"measured={measured}, capable={capable}, book={carbon['accounts_on_book']}"
    )


# --------------------------------------------------------------------------- #
# The measured gap against NESO (2026-08-25) -- and its vacuity guard          #
# --------------------------------------------------------------------------- #

def _shape_for(year: str, values):
    return {(f"{year}-01-{1 + i // 48:02d}", 1 + i % 48): v for i, v in enumerate(values)}


def test_a_year_sharing_ONE_half_hour_does_not_count_toward_the_headline():
    """THE DEFECT, MEASURED ON THE LIVE FEED THE DAY THIS WAS WRITTEN, and it flattered us.

    NESO publishes from 2018-05-11 and this tree's demand outturn barely reaches it, so 2018
    shared exactly ONE half hour with the published series. Its "spread" was that value divided
    by itself -- 1.0, perfect agreement -- and its correlation exactly 0.00. That row entered the
    average and dragged the published overstatement from 3.16x to 2.85x: a 10% improvement in
    this model's apparent fidelity, manufactured from one reading.

    Every vacuous row here points the same way, because a degenerate spread is always exactly
    1.0 and 1.0 is the answer we would like.

    MUTATION (must fire): drop the `counts_toward_headline` filter from the average.
    """
    assert gif.MIN_SHARED_HALF_HOURS > 1, "a single half hour would still count as a year"

    feed = json.loads(FEED.read_text(encoding="utf-8")) if FEED.is_file() else None
    if not feed or not (feed.get("versus_published") or {}).get("available"):
        pytest.skip("the published-series comparison is not available in this tree")
    versus = feed["versus_published"]

    for year, row in versus["by_year"].items():
        if row["half_hours"] < gif.MIN_SHARED_HALF_HOURS:
            assert not row["counts_toward_headline"], (
                f"{year} shares {int(row['half_hours'])} half hour(s) and still counts"
            )
            assert year in versus["excluded_years"], (
                f"{year} was excluded from the headline and NOT reported as excluded -- a "
                "silent exclusion is how a coverage bound becomes invisible"
            )


def test_the_headline_says_we_OVERSTATE_and_by_how_much():
    """VACUITY GUARD ON THE WHOLE COMPARISON. A `versus_published` block that came out at exactly
    1.0 would mean either perfect agreement or a broken measurement, and the two are
    indistinguishable from the number alone. This model does overstate -- no coal, no
    interconnector imports -- so a headline at or below 1.0 is the instrument failing, not the
    model being right."""
    feed = json.loads(FEED.read_text(encoding="utf-8")) if FEED.is_file() else None
    if not feed or not (feed.get("versus_published") or {}).get("available"):
        pytest.skip("the published-series comparison is not available in this tree")

    factor = feed["versus_published"]["spread_overstated_by"]
    assert factor > 1.5, (
        f"this shape claims to be within {factor}x of NESO's spread. It dispatches no coal and "
        "no interconnector imports, so that is the comparison breaking rather than the model "
        "being that good"
    )
    assert len(feed["versus_published"]["headline_years"]) >= 3, (
        "the headline rests on fewer than three years of overlap"
    )


def test_an_ABSENT_published_series_is_REPORTED_not_omitted(monkeypatch):
    """R15 FAIL-SILENT, and the most expensive silence available here: a comparison missing from
    the feed reads exactly like a comparison that came out clean. The page's own control refuses
    to render a spread without it, so the absence has to be legible rather than falsy."""
    import sim.neso_carbon_intensity as neso

    def _no_cache():
        raise neso.NesoIntensityUnavailable("no cached series in this tree")

    monkeypatch.setattr(neso, "load_cached", _no_cache)
    shape = _shape_for("2024", [1.0] * 96)
    built = gif.versus_published(shape, {k: 30_000.0 for k in shape})

    assert built["available"] is False
    assert "no cached series" in built["why"], "the absence does not say why"


# --------------------------------------------------------------------------- #
# The gap ONE GRAIN DOWN: this household's belief against the published truth  #
# --------------------------------------------------------------------------- #

def _days(first: int, last: int) -> list[str]:
    return [f"2024-{1 + (d - 1) // 30:02d}-{1 + (d - 1) % 30:02d}" for d in range(first, last + 1)]


def _paired_feed():
    """Two series that OVERLAP WITHOUT COINCIDING, each drifting day by day.

    THE COVERAGE MISMATCH IS THE WHOLE FIXTURE, not scenery. Ours runs days 1-60, the published
    one runs days 11-80, and the level of each drifts across the window. So each series' own
    demand-weighted mean is taken over half hours the other never saw, and their raw values sit
    at different levels for a reason that has nothing to do with the grid. That is exactly the
    live situation -- 2022 shares 14,929 of 17,520 half hours -- and it is what gives the
    re-normalisation divisors something real to do. Two series covering identical half hours
    agree about their means for free, which is why the first version of this fixture could not
    fail and skipped itself instead.

    Our shape swings 4x within the day; the published one swings 1.2x. That is the defect in
    miniature: no coal and no interconnector imports make the model's clean end far too clean.
    """
    import sim.neso_carbon_intensity as neso

    ours_days, pub_days = _days(1, 60), _days(11, 80)
    all_days = sorted(set(ours_days) | set(pub_days))
    keys = [(d, p) for d in all_days for p in range(1, 49)]
    demand = {k: 30_000.0 for k in keys}

    def drift(day: str) -> float:
        return 1.0 + 0.01 * all_days.index(day)

    ours = {(d, p): (0.4 if p <= 24 else 1.6) * drift(d) for d in ours_days for p in range(1, 49)}
    grams = {(d, p): (200.0 if p <= 24 else 240.0) * drift(d)
             for d in pub_days for p in range(1, 49)}

    published = neso.published_shape(grams, demand)
    versus = gif.versus_published(ours, demand, published, "")
    feed = {
        "records": [{"date": d, "period": p, "shape": ours.get((d, p)),
                     "published": published.get((d, p))}
                    for d, p in keys if (d, p) in ours],
        "versus_published": versus,
    }
    return feed, ours, published


def test_the_feed_carries_the_PUBLISHED_value_in_THE_SAME_HALF_HOUR_not_only_a_year_summary():
    """A ratio between two YEARS' spreads cannot be applied to one household's day.

    `spread_overstated_by` says this model overstates the grid's total range by about 3.2x, and
    the page used to ask the reader to discount every household figure by that factor himself.
    How wrong the model is for a HOUSEHOLD depends entirely on when that household drew --
    measured on the live page the disagreement runs from 0.3 to 28 percentage points. The two
    values have to travel in the same record for anyone to do that arithmetic.
    """
    feed, _ours, _pub = _paired_feed()
    assert all("published" in r for r in feed["records"]), (
        "a record without a `published` key cannot be compared at all, and its absence would "
        "be indistinguishable from agreement"
    )
    covered = [r for r in feed["records"] if r["published"] is not None]
    assert covered, "no record carries the published series"


def test_a_half_hour_the_published_series_does_not_cover_is_NULL_and_never_a_substituted_ONE():
    """R15 FAIL-OPEN, and the substitution would flatter us in the usual direction.

    1.0 is the shape's own average, so filling a missing published value with it makes the truth
    side read "exactly average" for that half hour -- which always drags the measured gap TOWARD
    ZERO, i.e. toward "our model is fine". An absence has to stay an absence.
    """
    feed, _ours, _pub = _paired_feed()
    uncovered = [r for r in feed["records"] if r["date"] < "2024-01-11"]
    assert uncovered, "the fixture no longer has an uncovered stretch to check"
    assert all(r["published"] is None for r in uncovered), (
        "a half hour outside the published series was given a value"
    )
    assert not any(r["published"] == 1.0 for r in uncovered), "1.0 was substituted for an absence"


def test_the_household_gap_is_MEASURED_against_the_published_series_and_not_inferred():
    """THE COUPLED-TRIAD RUNG at the grain the mission's number is made of: the company's belief,
    the world's published truth, and the distance between them for ONE metered day."""
    feed, ours, published = _paired_feed()
    reads = [{"date": "2024-01-15", "period": p, "kwh": 1.0} for p in range(1, 25)]

    got = gec.belief_versus_truth(reads, ours, gec.published_shape_from_feed(feed), feed, "2024")
    assert got["available"] is True, got.get("why")

    # THE EXPECTATION IS DERIVED FROM THE FIXTURE'S OWN PARAMETERS, never pasted from what the
    # code returned -- a test whose expected value came out of the subject is the TAUTOLOGY
    # pattern and would survive any arithmetic change made consistently in both places.
    #   drift(day n) = 1 + 0.01*(n-1); the household drew day 15, clean half only.
    #   ours: clean half hour = 0.4*drift(15); re-normalised by the mean of ours over the
    #         SHARED days 11..60, which is 1.0 * mean(drift) = 1.345.
    #   theirs: published_shape already divided grams by their mean over days 11..80
    #         (220 * 1.445); re-normalised again by the published mean over days 11..60.
    drift = lambda n: 1.0 + 0.01 * (n - 1)  # noqa: E731 -- one line, and named right here
    mean_drift = lambda a, b: 1.0 + 0.01 * ((a - 1) + (b - 1)) / 2.0  # noqa: E731
    expect_belief = 100.0 * (0.4 * drift(15) / (1.0 * mean_drift(11, 60)) - 1.0)
    pub_own_mean = 220.0 * mean_drift(11, 80)
    expect_truth = 100.0 * (
        (200.0 * drift(15) / pub_own_mean) / (220.0 * mean_drift(11, 60) / pub_own_mean) - 1.0)

    assert got["belief_pct"] == pytest.approx(expect_belief, abs=0.05), got
    assert got["truth_pct"] == pytest.approx(expect_truth, abs=0.05), got
    # THE HEADLINE THE FIXTURE EXISTS TO SHOW: our shape swings 4x within the day and the
    # published one 1.2x, so the company believes timing did far more for this household than
    # the published grid says it did.
    assert got["belief_pct"] < expect_truth - 40.0, got
    assert got["gap_pp"] == pytest.approx(got["belief_pct"] - got["truth_pct"], abs=0.01)
    assert got["half_hours"] == 24


def test_MUTATION_dropping_the_RENORMALISATION_makes_the_two_answers_disagree_about_coverage():
    """The divisors are what makes this a measurement of physics rather than of file coverage.

    Each series arrives normalised over ITS OWN half hours; here the published one is missing
    ten days, so its raw values sit at a different level from ours for a reason that is nothing
    to do with the grid. Computing the truth side without dividing by the published divisor is
    the mutation, and it must move the answer.
    """
    feed, ours, published = _paired_feed()
    reads = [{"date": "2024-01-15", "period": p, "kwh": 1.0} for p in range(1, 25)]
    row = feed["versus_published"]["by_year"]["2024"]
    divisor = row["published_renormalisation_divisor"]
    assert divisor > 0.0, "the feed carries no published re-normalisation divisor"

    honest = gec.belief_versus_truth(
        reads, ours, gec.published_shape_from_feed(feed), feed, "2024")
    mutated = dict(row, published_renormalisation_divisor=1.0)
    hurt = gec.belief_versus_truth(
        reads, ours, gec.published_shape_from_feed(feed),
        {**feed, "versus_published": {"by_year": {"2024": mutated}}}, "2024")

    if divisor == pytest.approx(1.0, abs=1e-9):
        pytest.skip("this fixture's coverage happens to leave the divisor at 1.0")
    assert hurt["truth_pct"] != pytest.approx(honest["truth_pct"], abs=0.01), (
        "dropping the re-normalisation left the answer unchanged, so the divisor is decorative"
    )


def test_a_year_the_HEADLINE_EXCLUDES_gets_NO_household_comparison():
    """The 2018 lesson, one grain down. That year shares exactly ONE half hour with the published
    series in this tree; a divisor computed from one reading is not a year's mean, and a
    household figure resting on it would carry the same manufactured agreement that dragged the
    published overstatement from 3.16x to 2.85x. Refused, with the reason said."""
    feed, ours, published = _paired_feed()
    reads = [{"date": "2024-01-15", "period": p, "kwh": 1.0} for p in range(1, 25)]
    got = gec.belief_versus_truth(
        reads, ours, gec.published_shape_from_feed(feed), feed, "2018")
    assert got["available"] is False
    assert "too few half hours" in got["why"], got


def test_a_day_OUTSIDE_the_published_series_is_an_ABSENCE_and_not_an_agreement():
    """Half the household-days this page shows predate NESO's cached series. Reporting them as a
    gap of zero would say the company's model was vindicated on days nothing checked it."""
    feed, ours, published = _paired_feed()
    reads = [{"date": "2024-01-05", "period": p, "kwh": 1.0} for p in range(1, 25)]
    got = gec.belief_versus_truth(
        reads, ours, gec.published_shape_from_feed(feed), feed, "2024")
    assert got["available"] is False
    assert "not an agreement" in got["why"], got


def test_the_BOOK_LEVEL_gap_says_UNMEASURED_rather_than_nothing_when_no_day_overlaps():
    """R15 FAIL-SILENT on the summary. A section that simply omits the comparison reads as a
    section whose comparison came out clean."""
    summary = gec._household_gap_summary([
        {"account_id": "C1", "belief_vs_truth": {"available": False, "why": "no overlap"}},
    ])
    assert summary["available"] is False
    assert "Unmeasured, not agreed" in summary["why"], summary
    assert summary["panels_on_page"] == 1


def test_the_LIVE_page_data_carries_the_household_gap_for_every_day_it_prices():
    """R11 on the artefact the page fetches: every day that gets a carbon figure gets either a
    measured comparison against the published series or a stated reason it has none."""
    if not CARBON.is_file():
        pytest.skip("the page data has not been generated in this tree")
    data = json.loads(CARBON.read_text(encoding="utf-8"))
    priced = [r for r in (data.get("accounts") or []) if "co2e_kg_timed" in r]
    if not priced:
        pytest.skip("no measured household-day on the live page")

    for row in priced:
        got = row.get("belief_vs_truth")
        assert isinstance(got, dict), f"{row['account_id']} {row['date']} carries no comparison"
        assert got.get("available") is True or got.get("why"), (
            f"{row['account_id']} {row['date']} has an unavailable comparison with no reason"
        )
    assert "versus_published_households" in data, (
        "the page data carries no book-level reading of the gap, so the section would render "
        "nothing where an absence has to be legible"
    )


# --------------------------------------------------------------------------- #
# The Expert Hour findings, 2026-08-25 -- a correction that was not like-for-  #
# like, and a stated reason its own module contradicted                        #
# --------------------------------------------------------------------------- #

def test_the_two_percentile_implementations_cannot_drift_apart():
    """THE COMPARISON IS ONLY LIKE-FOR-LIKE IF BOTH SIDES ROUND THE SAME WAY.

    The page prints a p95/p5 spread computed by `gif._percentile`; the factor that corrects it
    is computed from `neso._percentile`. Two percentile conventions -- nearest-rank one side,
    interpolated the other -- would reintroduce the finding this pair was written to close, at a
    grain too small for anyone to see on the page. So they are held to the same rule here.

    MUTATION (must fire): change either implementation's index rule.
    """
    from sim import neso_carbon_intensity as neso

    # Deliberately awkward lengths: 7 and 13 are where nearest-rank and interpolated part
    # company on the 5th and 95th percentile, which is exactly the pair being compared.
    for n in (7, 13, 20, 48, 17_000):
        values = sorted(float(i) for i in range(1, n + 1))
        for fraction in (0.05, 0.5, 0.95):
            assert gif._percentile(values, fraction) == neso._percentile(values, fraction), (
                f"the two percentile implementations disagree at n={n}, p={fraction}: the "
                "page's spread and its correction factor are no longer the same statistic"
            )


def test_the_feed_publishes_the_correction_ON_THE_STATISTIC_THE_PAGE_PRINTS():
    """THE FINDING: a p95/p5 spread was corrected by a max/min-derived factor.

    The panel prints "the dirtiest 5% of half hours ran 5.1x the cleanest 5%" and then said that
    measured `spread_overstated_by` "wider than" NESO's. That factor is the mean of six max/min
    ratios -- two single half hours out of seventeen thousand on each side, which `year_stats`'
    own docstring refuses to rest a claim on. Both statistics are now published and the page
    must be able to reach the one it quotes.

    MUTATION (must fire): delete `p95_spread_overstated_by` from `versus_published`.
    """
    feed = json.loads(FEED.read_text(encoding="utf-8")) if FEED.is_file() else None
    if not feed or not (feed.get("versus_published") or {}).get("available"):
        pytest.skip("the published-series comparison is not available in this tree")
    versus = feed["versus_published"]

    assert versus.get("p95_spread_overstated_by"), (
        "the feed offers no p95/p5 correction, so any page sentence correcting a p95/p5 spread "
        "is forced back onto the max/min factor -- the defect itself"
    )
    assert versus["p95_spread_overstated_by"] > 1.0, (
        "the p95/p5 correction came out at or below 1.0, which would mean this shape's robust "
        "spread is no wider than NESO's -- with no coal and no imports modelled that is the "
        "instrument failing, not the model being right"
    )
    # THE TWO FACTORS ARE DIFFERENT NUMBERS, which is the whole reason the finding mattered. If
    # they ever coincide this test is no longer evidence of anything and should be re-derived.
    assert versus["p95_spread_overstated_by"] != versus["spread_overstated_by"], (
        "the tail and robust corrections are identical, so this control can no longer tell "
        "whether the page picked the right one"
    )
    for year in versus["headline_years"]:
        row = versus["by_year"][year]
        for key in ("reconstructed_p95_over_p5", "published_p95_over_p5"):
            assert row.get(key), f"{year} carries no {key}, so its factor rests on nothing"


def test_the_stated_ERROR_DIRECTION_does_not_contradict_the_NAMED_GAPS_beside_it():
    """THE FINDING: the sentence that reaches the page said both largest gaps push the same way.

    `NAMED_GAPS` says otherwise in the same module -- coal omission is a DIRTY-end error, and
    omitting interconnector imports makes half hours read DIRTIER, not cleaner. The published
    conclusion (the clean end is optimistic) is true and measured; the reason given for it was
    not, and a reason a reader can check against the list one field away is the kind of wrong
    that costs trust in the number beside it.

    MUTATION (must fire): restore "both make quiet half hours look cleaner".
    """
    text = gif.ERROR_DIRECTION.lower()
    gaps = " ".join(gif.NAMED_GAPS).lower()

    assert "interconnector imports are not modelled, so heavy-import half hours read dirtier" in gaps, (
        "the gap list no longer states the interconnector direction, so this control has lost "
        "the side of the comparison it checks against"
    )
    assert not ("both" in text and "cleaner" in text.split("upper bound")[0]), (
        "the error-direction sentence again claims both gaps push toward cleaner, which the "
        "named gaps in this same module contradict on both limbs"
    )
    assert "upper bound" in text, "the direction a reader must take away is no longer stated"
    assert "measured" in text, (
        "the clean-end claim reads as asserted rather than measured -- the exact sentence that "
        "was found to be a recollection in the grammar of a measurement"
    )
