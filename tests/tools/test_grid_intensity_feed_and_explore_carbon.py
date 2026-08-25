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
