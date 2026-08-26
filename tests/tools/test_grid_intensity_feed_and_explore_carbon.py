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
# The fail-open signature, and the one place it is closed (2026-08-25)          #
# --------------------------------------------------------------------------- #

def test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape():
    """THE ONE CONTROL THAT MAKES `build_shape`'s OPTIONAL KEYWORDS SAFE.

    `sim.grid_carbon_intensity.build_shape` takes coal capacity and interconnector flow as
    keywords whose defaults reproduce the shape EXACTLY as it was before either was modelled.
    That is fail-open by construction: a caller that forgets them gets a series that lost two
    corrections and says nothing about it, and the feed's own `named_gaps` would go on claiming
    the corrections were there. Nothing in the arithmetic could notice -- both shapes are
    dimensionless, both normalise to 1.0, both look exactly like a carbon shape.

    So the boundary is here, on the path that actually publishes: no mix, no feed.

    MUTATION (must fire): wrap the `fuel_mix()` call in `generate()` in a try/except that falls
    back to `build_shape(demand, renewables)`.
    """
    from sim import elexon_fuel_outturn as fuel

    original = fuel.CACHE_PATH
    try:
        fuel.CACHE_PATH = REPO / "sim" / "cache" / "definitely_not_a_cache_that_exists.json"
        with pytest.raises(fuel.FuelOutturnUnavailable):
            gif.fuel_mix()
    finally:
        fuel.CACHE_PATH = original


def test_the_published_import_coverage_is_the_MEASURED_one_and_not_a_sentence():
    """The feed states what share of GB's imported energy it can price. That number has to come
    out of the adapter's own count, because a hand-typed "most imports are covered" is exactly
    the coverage sentence this file's docstring already calls out once.

    MUTATION (must fire): hard-code `covered_fraction` in `build()`.
    """
    shape = {("2025-06-06", p): 1.0 for p in range(1, 49)}
    demand = {k: 30_000.0 for k in shape}

    built = gif.build(shape, demand, import_coverage={"covered_fraction": 0.6612},
                      coal_capacity_by_year={2024: 1873.0, 2025: 110.0})

    assert built["import_coverage"]["covered_fraction"] == pytest.approx(0.6612)
    assert built["import_coverage"]["uncovered_cables"] == ["INTNSL (Norway)", "INTVKL (Denmark)"]
    # The coal fleet closing has to be legible AS a closure, which needs the zero row present.
    assert built["coal_demonstrated_max_mw"]["2025"] == 110


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
    indistinguishable from the number alone.

    THIS CONTROL ASSERTED THAT THE MODEL STAYS BAD, AND THE MODEL STOPPED BEING THAT BAD
    (2026-08-25, the thermal floor). It required `spread_overstated_by > 1.5`, and its stated
    reason was "it dispatches no coal and no interconnector imports" -- a premise that died
    earlier the same day when both were built. The floor then carried max/min from 2.44x to
    1.04x and this went red. That is a control encoding a premise the tree has outgrown, and the
    repair is NOT to lower 1.5 until it passes: a threshold moved to green a red is the
    goal-seeking R12 exists to stop, and it would be indistinguishable from this one whether the
    instrument had broken or not.

    SO THE GUARD NOW CHECKS THE THING IT NAMES. A broken comparison is DEGENERATE, and the test
    above documents exactly what that looks like on this feed: a spread of exactly 1.0 from a
    value divided by itself, with a correlation of exactly 0.00. Those are checkable directly,
    and unlike a fidelity threshold they do not expire when the model improves.

    ONE FIDELITY CLAIM SURVIVES, on the statistic the page actually prints. `p95/p5` is the
    robust spread (max/min rests on two single half hours out of seventeen thousand, which
    `year_stats` refuses to rest a claim on) and it still runs ~1.36x, so we do still overstate.
    A drop below 1.0 there would mean this model UNDERSTATES the range, which has never happened
    and would be worth a human look rather than a silent pass.

    MUTATION (must fire): compare the published series against itself, which is the shape a
    broken comparison takes -- correlation 1.0, zero error, every spread ratio 1.0.
    """
    feed = json.loads(FEED.read_text(encoding="utf-8")) if FEED.is_file() else None
    if not feed or not (feed.get("versus_published") or {}).get("available"):
        pytest.skip("the published-series comparison is not available in this tree")

    versus = feed["versus_published"]
    assert len(versus["headline_years"]) >= 3, (
        "the headline rests on fewer than three years of overlap"
    )

    for year in versus["headline_years"]:
        row = versus["by_year"][str(year)]
        assert 0.0 < abs(row["correlation"]) < 1.0, (
            f"{year} correlates {row['correlation']} with the published series. Exactly 0.0 is "
            "the degenerate single-half-hour row and exactly 1.0 is a series compared against "
            "itself; either is the instrument failing, not the model succeeding"
        )
        assert row["mean_abs_error"] > 0.0, (
            f"{year} differs from the published series by exactly nothing, which is not a "
            "reconstruction agreeing -- it is the same numbers on both sides"
        )
        assert row["reconstructed_p95_over_p5"] != row["published_p95_over_p5"], (
            f"{year}'s reconstructed and published spreads are identical to the digit"
        )

    factor = versus["p95_spread_overstated_by"]
    assert factor > 1.0, (
        f"this shape claims to UNDERSTATE the published spread ({factor}x on p95/p5). That has "
        "never happened and is more likely the comparison breaking than the model being right"
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


def test_the_WITHIN_DAY_FIGURES_QUOTED_in_ERROR_DIRECTION_are_the_MEASURED_ones():
    """A DERIVED-VS-TYPED PAIR, and this file already knows why that class matters.

    THE FINDING (2026-08-25): the page's "1.36x" correction blends two axes that behave
    oppositely. Split day by day, this shape's BETWEEN-day swing matches the published series
    (0.93-1.00x over 2019-2024) and its WITHIN-day swing does not (1.41-1.58x). A household can
    shift the washing from 6pm to 2am and cannot shift it to a windier Tuesday in March, so the
    whole exaggeration sits on the only axis a time-shifting claim acts on -- and the annual
    factor therefore UNDER-corrects the claim it is printed to correct.

    That is worth saying on the page only if the numbers said there stay the measured ones. The
    sentence is prose typed by a human hand; the feed is computed. This control reads the numbers
    back OUT of the sentence and holds them against the feed, so the two cannot drift -- the same
    defect shape as the hardcoded '3.2x' correction deleted from this panel earlier the same day,
    and as the ERROR_DIRECTION reason found to be a recollection the same morning.

    MUTATION (must fire): move any quoted bound, or let the measurement move past one.
    """
    import re

    quoted = re.findall(r"\((\d+\.\d+)-(\d+\.\d+)x, mean (\d+\.\d+)\)", gif.ERROR_DIRECTION)
    assert len(quoted) == 2, (
        "ERROR_DIRECTION no longer quotes exactly two (low-highx, mean m) ranges, so this "
        "control cannot tell which claim it is checking and must be re-derived rather than "
        "left to pass on whatever it finds"
    )
    claims = {
        "between_day_swing_overstated_by": tuple(float(v) for v in quoted[0]),
        "within_day_swing_overstated_by": tuple(float(v) for v in quoted[1]),
    }

    feed = json.loads(FEED.read_text(encoding="utf-8")) if FEED.is_file() else None
    if not feed or not (feed.get("versus_published") or {}).get("available"):
        pytest.skip("the published-series comparison is not available in this tree")
    versus = feed["versus_published"]
    years = versus["headline_years"]
    assert years, "no headline year, so the quoted range rests on nothing"

    for key, (low, high, mean_claimed) in claims.items():
        measured = [versus["by_year"][y][key] for y in years]
        assert all(v is not None for v in measured), (
            f"a headline year carries no {key}: the sentence quotes a range over years the feed "
            "does not measure"
        )
        # THE BOUNDS MUST BE THE MEASURED ONES, NOT MERELY CONTAIN THEM. Written first as
        # `min(measured) >= low and max(measured) <= high`, this control passed every time the
        # quoted range was WIDENED -- so "1.41-1.90x" against a measured 1.41-1.58x, which is
        # simply a false sentence to a reader, was invisible to it. A one-sided containment check
        # on a published range is fail-open by construction: the loosest possible claim always
        # survives it. Both ends are pinned to the rounding the sentence itself prints.
        assert (round(min(measured), 2), round(max(measured), 2)) == pytest.approx((low, high), abs=5e-3), (
            f"{key} measured {min(measured):.3f}-{max(measured):.3f} over {years}, but "
            f"ERROR_DIRECTION tells the reader {low}-{high}"
        )
        got_mean = sum(measured) / len(measured)
        assert got_mean == pytest.approx(mean_claimed, abs=5e-3), (
            f"{key} means {got_mean:.3f} across the headline years; the sentence says "
            f"{mean_claimed}"
        )

    # THE DIRECTION OF THE CLAIM, not only its arithmetic: the sentence's whole point is that one
    # axis is right and the other is not. If they ever converge the sentence is wrong even with
    # every number in range, so the ordering is asserted rather than left to the reader.
    within = [versus["by_year"][y]["within_day_swing_overstated_by"] for y in years]
    between = [versus["by_year"][y]["between_day_swing_overstated_by"] for y in years]
    assert min(within) > max(between), (
        "the within-day and between-day overstatements now overlap, so 'the whole of the "
        "exaggeration sits on the intra-day axis' is no longer what the measurement says"
    )


def test_the_stated_ERROR_DIRECTION_does_not_contradict_the_NAMED_GAPS_beside_it():
    """THE FINDING: the sentence that reaches the page said both largest gaps push the same way.

    `NAMED_GAPS` says otherwise in the same module -- coal omission is a DIRTY-end error, and
    omitting interconnector imports makes half hours read DIRTIER, not cleaner. The published
    conclusion (the clean end is optimistic) is true and measured; the reason given for it was
    not, and a reason a reader can check against the list one field away is the kind of wrong
    that costs trust in the number beside it.

    MUTATION (must fire): restore "both make quiet half hours look cleaner".

    ITS SUBJECT MOVED AND THE CONTROL FOLLOWED IT RATHER THAN BEING DELETED (2026-08-25). The
    gap it used to quote -- "interconnector imports are not modelled" -- stopped being true when
    they were modelled, and this test went red for the right reason: the string it anchored on
    was gone. Deleting it would have removed the only check that the published REASON agrees
    with the published GAPS, at the exact moment the gaps changed, which is when that check is
    worth most. So the anchor is now the RESIDUE -- the two cables NESO publishes no factor for,
    which are still dispatched as GB gas and still read dirtier -- and it is asserted on the
    direction word rather than on a whole sentence, so the next rewording does not fake a pass
    OR a fail.
    """
    text = gif.ERROR_DIRECTION.lower()
    gaps = " ".join(gif.NAMED_GAPS).lower()

    assert "interconnector" in gaps and "reads dirtier" in gaps, (
        "the gap list no longer states the interconnector direction, so this control has lost "
        "the side of the comparison it checks against"
    )
    assert "thermal" in gaps and "demonstrated annual minimum" in gaps, (
        "the gap list no longer names the thermal floor, which is what the range claim now rests "
        "on; without it the error direction rests on nothing"
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
    # THE SUBJECT MOVED A SECOND TIME AND THE CONTROL FOLLOWED IT AGAIN (2026-08-25, the thermal
    # floor). The old gap -- "the thermal stack reaches exactly zero" -- stopped being true when
    # the floor was measured, and with it went the claim that the clean end is UNIFORMLY
    # optimistic: in 2020 and 2021 the model's quietest half hours are now DIRTIER than published.
    # An error-direction sentence that still said "the clean end is optimistic" full stop would be
    # asserting a direction the measurement beside it contradicts in two of six years, which is
    # the exact defect this control was written for, pointed the other way. So the claim the
    # sentence is now allowed to make is about the RANGE, and it must say the clean end is mixed.
    assert "range" in text, (
        "the surviving overstatement is of the RANGE, and the sentence no longer says so"
    )
    assert "dirtier than published" in text, (
        "the error-direction sentence omits that the clean end now overshoots in some years -- "
        "reporting only the flattering half of a measurement that moved in both directions"
    )


# --------------------------------------------------------------------------- #
# The CONSUMPTION side of the multiplication (2026-08-25)                      #
# --------------------------------------------------------------------------- #
# THE FINDING these close: every timing figure on Explore is the grid's shape TIMES the
# household's, the EP13 Expert Hour spent all five MAJOR findings on the first one, and the
# second one is a two-block template. `simulation/demand_model.py::HEATING_PERIOD_WEIGHTS` is
# ONE module-level constant -- uniform over periods 13-20 and 34-44, identical for every
# premise in the country -- so 86-94% of a priced winter day's kWh is placed by a national
# constant, in the two windows the grid is dirtiest in. The world defect is already owned by
# `W1_11_fabric_physics_core`; what is closed HERE is the published ATTRIBUTION, which credited
# a household for a shape it did not choose.
#
# R10: not the instance. The class is "a customer-facing figure attributes to a household
# something a constant decided", and the three controls below make the class red automatically
# -- a new priced panel with no provenance fails, a restored attribution clause fails, and a
# window that stops being derived from the producer fails.

def test_every_PRICED_panel_publishes_WHERE_ITS_SHAPE_CAME_FROM():
    """A panel may not publish a timing effect without the share of it a template placed.

    MUTATION (must fire): drop the `shape_provenance` key from `build()`'s account row.
    """
    data = json.loads(CARBON.read_text())
    priced = [a for a in data["accounts"] if "timing_effect_pct" in a]
    assert priced, "no priced panel in the published file, so this control checked nothing"
    for row in priced:
        sp = row.get("shape_provenance")
        assert sp, f"{row['account_id']} {row['date']} prices a day with no shape provenance"
        assert sp.get("available") is True, (
            f"{row['account_id']} {row['date']} reports its provenance unavailable while still "
            "publishing a timing effect built from those same kWh"
        )
        assert 0.0 <= sp["share_in_modelled_window"] <= 1.0
        assert sp["periods_in_window"] < sp["periods_in_day"], (
            "the modelled window covers the whole day, so the share is 1.0 by construction and "
            "measures nothing -- a tautology, not a control"
        )


def test_the_modelled_window_is_DERIVED_from_the_producer_and_not_restated():
    """The published window must move when the world's constant moves.

    THE FAIL-OPEN THIS REFUSES: hard-coding "06:00-10:00 and 16:30-22:00" into the generator
    would keep printing a measured-sounding sentence for years after `W1_11_fabric_physics_core`
    lands a per-home shape. Independence runs the right way here -- the page's claim is ABOUT
    the constant, so reading the constant is correctness, not tautology.

    MUTATION (must fire): replace `modelled_load_windows()`'s body with a literal list.
    """
    from simulation import demand_model

    original = list(demand_model.HEATING_PERIOD_WEIGHTS)
    assert gec.modelled_load_windows() == [
        p for p, w in enumerate(original, start=1) if w > 0
    ]

    # Move the producer; the generator must follow it, not its own memory of it.
    moved = [1.0 if p in (5, 6) else 0.0 for p in range(1, 49)]
    demand_model.HEATING_PERIOD_WEIGHTS[:] = moved
    try:
        assert gec.modelled_load_windows() == [5, 6], (
            "the generator reported the old window after the world's constant moved, so the "
            "sentence it feeds is a restatement wearing the grammar of a derivation"
        )
    finally:
        demand_model.HEATING_PERIOD_WEIGHTS[:] = original
    assert gec.modelled_load_windows() != [5, 6]


def test_the_page_does_not_credit_the_HOUSEHOLD_for_the_TEMPLATES_shape():
    """The rendered clause, and the null the reader needs to read the number.

    MUTATION (must fire): restore "household drew made its carbon", or delete the null-baseline
    sentence from `shapeProvenance`.
    """
    page = (REPO / "site" / "explore" / "index.html").read_text()

    assert "household drew made its carbon" not in page, (
        "the panel again attributes the timing effect to when the HOUSEHOLD drew, which the "
        "consumption template underneath it cannot support"
    )
    assert "household's profile has it drawing" in page, (
        "the hedged attribution is gone and nothing named replaced it"
    )
    assert "shapeProvenance(row)" in page, (
        "the provenance paragraph is no longer rendered, so the share is published in the data "
        "and invisible on the page -- the failure mode that makes a feed field decorative"
    )
    assert "no concentration at all would put" in page, (
        "the provenance sentence no longer prints its own null baseline, so a reader is asked "
        "to supply the 40%-is-flat comparison himself and cannot"
    )


# --------------------------------------------------------------------------- #
# The biomass envelope: measured, published, and deliberately not dispatched   #
# --------------------------------------------------------------------------- #

def test_the_feed_REFUSES_to_publish_without_the_BIOMASS_envelope_too():
    """The envelope is not dispatched, and it is still REQUIRED, which is the whole of what
    makes the not-dispatched decision honest.

    A diagnostic that may quietly go missing is a named gap whose size stops being published the
    moment it matters -- the basis line would still say biomass is held at 2,400 MW and the rows
    that let a reader check how wrong that is would simply be absent (R15 FAIL-SILENT).

    MUTATION (must fire): make `fuel_mix()` swallow the biomass loader's refusal.
    """
    from sim import elexon_fuel_outturn as fuel

    original = fuel.BIOMASS_CACHE_PATH
    try:
        fuel.BIOMASS_CACHE_PATH = REPO / "sim" / "cache" / "no_such_biomass_cache.json"
        with pytest.raises(fuel.FuelOutturnUnavailable):
            gif.fuel_mix()
    finally:
        fuel.BIOMASS_CACHE_PATH = original


def test_the_UNWIRED_flag_is_a_DECISION_and_not_an_INERT_switch():
    """R11: a flag whose release triggers nothing is a defect.

    `BIOMASS_DISPATCH_WIRED` is False because the correction was MEASURED to make the published
    series worse on four axes of five, not because the dispatch was never finished. This test
    holds both halves of that sentence to account: while the flag is False the published shape
    must be exactly the flat-2,400-MW one, and flipping it must actually move the shape --
    otherwise the flag is decoration and the day someone flips it nothing would happen.

    MUTATION (must fire): pass the envelope to `build_shape` regardless of the flag, or wire the
    flag to a parameter the dispatch ignores.
    """
    from sim.grid_carbon_intensity import build_shape

    assert gif.BIOMASS_DISPATCH_WIRED is False, (
        "if this has been flipped on, the before/after measurement in its own docstring has to "
        "be re-run and re-published first -- it is the evidence the flag stands on"
    )
    demand = {("2024-03-01", p): 20_000.0 for p in range(1, 40)}
    renewables = {key: 5_000.0 + 375.0 * key[1] for key in demand}
    envelope = {2024: {"capacity_mw": 3_328.0, "floor_mw": 73.0, "p1_mw": 550.0,
                       "p99_mw": 3_219.0, "mean_mw": 2_142.0, "half_hours": 17_559.0}}

    unwired = build_shape(demand, renewables, biomass_envelope_by_year=None)
    assert unwired == build_shape(demand, renewables), "the unwired path is not the flat block"
    assert build_shape(demand, renewables, biomass_envelope_by_year=envelope) != unwired, (
        "flipping the flag would change nothing, so it is not a decision -- it is decoration"
    )

    # AND THE FLAG HAS TO GOVERN THE PUBLISHING CALL, which the two assertions above cannot
    # show: they prove the PARAMETER works, and the first draft of this test stopped there --
    # the mutation that hard-codes `biomass_envelope_by_year=None` in `generate()`, severing the
    # flag from the only call site that publishes anything, SURVIVED it. Checked on the parsed
    # call rather than on the source text so a mention in a comment cannot satisfy it.
    import ast
    import inspect

    call = next(
        node
        for node in ast.walk(ast.parse(inspect.getsource(gif.generate)))
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "build_shape"
    )
    keyword = next(k for k in call.keywords if k.arg == "biomass_envelope_by_year")
    assert "BIOMASS_DISPATCH_WIRED" in {
        n.id for n in ast.walk(keyword.value) if isinstance(n, ast.Name)
    }, (
        "`generate()` does not consult the flag, so `BIOMASS_DISPATCH_WIRED` documents a "
        "decision the publishing path does not actually make"
    )


def test_the_published_BASIS_says_biomass_is_still_FLAT_while_the_flag_is_off():
    """R14 applied to a basis: the sentence that travels with the number must describe the
    arithmetic that produced it, not the arithmetic that exists in the tree.

    The one way this correction could do real damage is by being DESCRIBED as applied while the
    published series was still flat -- a reader would take the spread at face value.

    MUTATION (must fire): edit `SHAPE_BASIS` to claim the fleet is dispatched while
    `BIOMASS_DISPATCH_WIRED` is False.
    """
    from sim.grid_carbon_intensity import SHAPE_BASIS

    if not gif.BIOMASS_DISPATCH_WIRED:
        assert "constant 2,400 MW" in SHAPE_BASIS
        assert "NOT dispatched" in SHAPE_BASIS
    else:
        assert "constant 2,400 MW" not in SHAPE_BASIS


def test_the_envelope_REACHES_the_published_feed_with_both_ends_and_the_mean():
    """The measurement has to arrive where a reader is, not only where the tests are.

    MUTATION (must fire): drop `biomass_envelope_by_year` from the `build()` call in
    `generate()`, or publish only one end of the envelope.
    """
    shape = {("2024-03-01", p): 1.0 + 0.01 * p for p in range(1, 20)}
    built = gif.build(
        shape, {k: 30_000.0 for k in shape},
        biomass_envelope_by_year={2024: {"capacity_mw": 3_328.4, "floor_mw": 73.2,
                                         "p1_mw": 550.0, "p99_mw": 3_219.0,
                                         "mean_mw": 2_142.6, "half_hours": 17_559.0}},
    )
    row = built["biomass_envelope_mw"]["2024"]
    assert row["floor_mw"] == 73 and row["capacity_mw"] == 3_328
    assert row["mean_mw"] == 2_143, (
        "the mean is what makes the flat 2,400 MW assumption checkable by a reader"
    )
    assert gif.build(shape, {k: 30_000.0 for k in shape})["biomass_envelope_mw"] is None


# --------------------------------------------------------------------------- #
# The CEILING block: the counterparty's own forecast error, published beside    #
# the model's. Mutation-run 2026-08-26.                                         #
# --------------------------------------------------------------------------- #

def _forecast_days(n_days: int, per_period) -> dict:
    out = {}
    for day in range(n_days):
        date_str = f"2024-{1 + day // 28:02d}-{1 + day % 28:02d}"
        for period in range(1, 49):
            forecast, actual = per_period(day, period)
            out[(date_str, period)] = {"forecast": float(forecast), "actual": float(actual)}
    return out


def test_the_forecast_ceiling_reaches_the_feed_with_its_dial_visible():
    """The block a page may quote, and the sweep that stops the dial being turned quietly.

    `shift_window_half_hours` is a choice about how long a household runs an appliance. Any
    choice inside a headline is somewhere the headline can be improved without the world
    changing, so the sweep across 2-12 half hours is published beside it."""
    parsed = _forecast_days(40, lambda d, p: (100.0 + 60.0 * ((p * 7) % 48) / 48.0,) * 2)
    shape = {k: 1.0 for k in parsed}
    block = gif.published_forecast_skill(shape, parsed)

    assert block["available"] is True
    assert block["by_year"]["2024"]["capture_mean"] == pytest.approx(1.0)
    assert block["shift_window_half_hours"] == 6
    assert set(block["window_sensitivity_capture_mean"]) == {"2", "4", "6", "8", "12"}
    assert "ceiling" in block["what_it_means"].lower()


def test_an_ABSENT_forecast_ceiling_is_REPORTED_not_omitted():
    """R15 FAIL-SILENT, and the failure is worse here than for the comparison beside it: a
    missing ceiling does not read as 'no measurement', it reads as NO CEILING -- i.e. as a
    forecast that could pick the clean half hours perfectly, which is the most flattering
    answer available to a page that sells time-shifting."""
    block = gif.published_forecast_skill({("2024-01-01", 1): 1.0}, None, "cache absent in this tree")
    assert block["available"] is False
    assert "cache absent" in block["why"]

    short = _forecast_days(3, lambda d, p: (100.0 + p,) * 2)
    thin = gif.published_forecast_skill({k: 1.0 for k in short}, short)
    assert thin["available"] is False
    assert "distribution" in thin["why"]


def test_the_ceiling_is_measured_on_the_counterpartys_series_and_not_on_ours():
    """R15 TAUTOLOGY. The block must not move when THIS MODEL's shape changes -- it is a fact
    about NESO's forecasting, and a ceiling derived from the thing it caps is not a ceiling.
    Only the set of YEARS is taken from our shape, which is why the years are asserted too."""
    parsed = _forecast_days(40, lambda d, p: (100.0 + 60.0 * ((p * 3) % 48) / 48.0,
                                              100.0 + 60.0 * ((p * 7) % 48) / 48.0))
    flat = gif.published_forecast_skill({k: 1.0 for k in parsed}, parsed)
    swinging = gif.published_forecast_skill({k: float(k[1]) for k in parsed}, parsed)

    assert flat["by_year"] == swinging["by_year"]
    assert list(flat["by_year"]) == ["2024"]


def test_the_live_feed_carries_the_ceiling_and_it_is_neither_perfect_nor_absent():
    """R11-adjacent: the published artefact, not the function. A capture of 1.0 would mean the
    grading collapsed into hindsight; an absent block would mean the page's timing figures are
    quoted with no ceiling at all."""
    if not FEED.exists():
        pytest.skip("feed not generated in this tree")
    block = json.loads(FEED.read_text())["published_forecast_skill"]
    assert block["available"] is True, block.get("why")
    assert 0.6 < block["capture_mean_across_years"] < 0.98
    assert block["by_year"], "no year reached the feed"
    for year, row in block["by_year"].items():
        assert row["capture_p5"] < row["capture_mean"], f"{year} published a mean, not a spread"


def test_the_CEILING_PERCENTAGES_QUOTED_in_ERROR_DIRECTION_are_the_MEASURED_ones():
    """The defect this whole module has been caught by twice: a number written in the grammar
    of a measurement that no longer matches the measurement beside it.

    ERROR_DIRECTION reaches the customer page verbatim (`site/explore/index.html` renders
    `g.error_direction`). It now quotes two percentages -- the mean day's capture and the worst
    day in twenty -- and both must be the figures `published_forecast_skill` actually computes,
    to the tolerance the words "about" earn and no further.

    MUTATION (run 2026-08-26, fires): change either quoted percentage by five points.
    """
    import re

    if not FEED.exists():
        pytest.skip("feed not generated in this tree")
    block = json.loads(FEED.read_text())["published_forecast_skill"]
    if not block.get("available"):
        pytest.skip("no published forecast series cached in this tree")

    quoted = [
        int(found)
        for pattern in (r"about (\d+)% of that day's achievable",
                        r"about (\d+)% on the worst day in twenty")
        for found in re.findall(pattern, gif.ERROR_DIRECTION)
    ]
    assert len(quoted) == 2, (
        "ERROR_DIRECTION no longer quotes exactly the two capture percentages this control "
        "checks, so it has lost its subject rather than passed"
    )
    mean_pct, worst_pct = quoted
    measured_mean = 100.0 * block["capture_mean_across_years"]
    measured_worst = 100.0 * (
        sum(row["capture_p5"] for row in block["by_year"].values()) / len(block["by_year"])
    )
    assert abs(mean_pct - measured_mean) <= 2.0, (
        f"the page is told {mean_pct}% and the feed measures {measured_mean:.1f}%"
    )
    assert abs(worst_pct - measured_worst) <= 2.0, (
        f"the page is told {worst_pct}% on the worst day in twenty and the feed measures "
        f"{measured_worst:.1f}%"
    )


def test_the_page_is_not_told_the_ceiling_can_be_built_away():
    """The one thing this sentence must never soften into. The forecast gap is not a defect in
    the reconstruction and no amount of modelling recovers it -- a reader who takes it as
    'another thing they will fix' will keep reading the timing figures at face value."""
    text = gif.ERROR_DIRECTION.lower()
    assert "forecast" in text and "ceiling" in text
    assert "cannot be built away" in text
