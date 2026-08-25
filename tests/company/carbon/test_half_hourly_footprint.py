"""R15 contract for the half-hourly household footprint.

THE CLAIM UNDER TEST is narrow on purpose: that this measures EMISSIONS, that a household's
emissions depend on WHEN it drew power, and that everything the instrument cannot see says so
out loud instead of reporting a convenient number.

EVERY AVAILABLE MISTAKE HERE FLATTERS THE COMPANY, which is why the mutations below are all
written in that direction: a missing shape defaulted to average, a profiled account's absent
timing reported as zero, an unavailable feed reporting a household that emitted nothing. Each
one makes the supplier's carbon story better than the evidence supports, and each has a test.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from company.carbon import half_hourly_footprint as hf
from company.regulatory.carbon_emissions import grid_intensity_g_co2e_per_kwh

REPO = Path(__file__).resolve().parents[3]
MODULE = REPO / "company" / "carbon" / "half_hourly_footprint.py"
INTENSITY_FEED = REPO / "docs" / "market_data" / "grid_intensity_feed.json"
CONSUMPTION_FEED = REPO / "docs" / "market_data" / "consumption_feed.json"

DAY = "2025-06-06"
YEAR = 2025


def _reads(kwh_by_period):
    return [{"date": DAY, "period": p, "kwh": k} for p, k in kwh_by_period.items()]


# --------------------------------------------------------------------------- #
# It measures, and the arithmetic is checked from outside                      #
# --------------------------------------------------------------------------- #

def test_a_measured_footprint_is_consumption_times_the_intensity_of_ITS_OWN_half_hour():
    """ANTI-TAUTOLOGY: the expected value is built here from the annual level and the shape,
    not read back out of the module. Deriving it from the module's own helper would pass with
    both sides multiplied by anything at all."""
    shape = {(DAY, 1): 0.5, (DAY, 2): 1.5}
    reads = _reads({1: 10.0, 2: 10.0})
    level = grid_intensity_g_co2e_per_kwh(YEAR)

    fp = hf.measured_footprint("C7", reads, shape)

    assert fp.co2e_kg_timed == pytest.approx((10.0 * level * 0.5 + 10.0 * level * 1.5) / 1000.0)
    assert fp.co2e_kg_flat == pytest.approx(20.0 * level / 1000.0)
    assert fp.half_hours == 2
    assert fp.method == hf.MEASURED


def test_drawing_at_the_CLEAN_half_hours_beats_drawing_at_the_DIRTY_ones():
    """The mission's whole thesis, reduced to two half hours. Same kWh, different times,
    different carbon -- which is a sentence the annual-only method could not express."""
    shape = {(DAY, 1): 0.4, (DAY, 2): 1.6}
    clean = hf.measured_footprint("clean", _reads({1: 20.0, 2: 0.0}), shape)
    dirty = hf.measured_footprint("dirty", _reads({1: 0.0, 2: 20.0}), shape)

    assert clean.co2e_kg_timed < dirty.co2e_kg_timed
    assert clean.co2e_kg_flat == pytest.approx(dirty.co2e_kg_flat), (
        "the flat method cannot tell these two households apart, which is the point"
    )
    assert clean.timing_effect_pct < 0 < dirty.timing_effect_pct


def test_MUTATION_a_household_drawing_ONLY_in_dirty_half_hours_reports_a_POSITIVE_effect():
    """The null on the sign. A timing effect that is negative for everybody is a units bug
    wearing a good-news hat, and it would be quoted before anyone checked."""
    shape = {(DAY, p): (1.8 if p <= 2 else 0.2) for p in range(1, 5)}
    fp = hf.measured_footprint("evening-peaker", _reads({1: 5.0, 2: 5.0}), shape)

    assert fp.timing_effect_pct > 0, (
        f"a household drawing entirely in the year's dirtiest half hours reports "
        f"{fp.timing_effect_pct:+.1f}%"
    )


# --------------------------------------------------------------------------- #
# Absence is not zero                                                          #
# --------------------------------------------------------------------------- #

def test_a_PROFILED_account_RAISES_on_its_timing_effect_rather_than_returning_zero():
    """THE DESIGN ARGUMENT IN THIS MODULE, pinned so it cannot quietly be lost.

    Zero would mean "this household's timing is exactly average" -- a measurement nobody made,
    for 249 of 263 accounts, in a column headed by three accounts where the figure is real. The
    truth is that a traditional meter does not record time. A caller is made to handle the
    absence, which is what forces the page to show it.

    MUTATION (must fire): return 0.0 for a None `co2e_kg_timed`.
    """
    fp = hf.profiled_footprint("C1", annual_kwh=3_100.0, year=YEAR)

    assert fp.method == hf.PROFILED
    assert fp.co2e_kg_timed is None
    assert fp.co2e_kg_flat == pytest.approx(
        3_100.0 * grid_intensity_g_co2e_per_kwh(YEAR) / 1000.0
    )
    with pytest.raises(hf.FootprintUnavailable):
        fp.timing_effect_pct


def test_a_read_whose_half_hour_has_NO_published_shape_is_DROPPED_not_defaulted_to_average():
    """R15 FAIL-OPEN, in the flattering direction again. Substituting 1.0 for a missing shape is
    the flat method smuggled back in one half hour at a time, and it always drags the timed
    figure toward the flat one -- i.e. toward "timing does not matter here"."""
    shape = {(DAY, 1): 0.4}
    fp = hf.measured_footprint("C7", _reads({1: 10.0, 2: 10.0}), shape)

    assert fp.half_hours == 1, "a half hour with no published intensity was given one anyway"
    assert fp.kwh == pytest.approx(10.0), "the dropped read still reached the kWh total"


def test_a_read_set_that_meets_NOTHING_raises_rather_than_reporting_a_clean_household():
    """Zero emissions is a spectacular result and an instrument that did not run must not be
    able to report one."""
    with pytest.raises(hf.FootprintUnavailable):
        hf.measured_footprint("C7", _reads({1: 10.0}), {("1999-01-01", 1): 1.0})


def test_an_UNREADABLE_intensity_feed_raises_rather_than_returning_an_empty_shape(tmp_path):
    """R15 FAIL-SILENT. An empty shape would give every household its flat figure and a timing
    effect of exactly zero -- the instrument's failure rendered as a finding about the world."""
    missing = tmp_path / "not-here.json"
    with pytest.raises(hf.FootprintUnavailable):
        hf.load_shape(missing)

    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"published_at": "x", "records": [], "typical_day": {}}))
    with pytest.raises(hf.FootprintUnavailable):
        hf.load_shape(empty)


# --------------------------------------------------------------------------- #
# The coverage statement -- derived, never written out beside the number       #
# --------------------------------------------------------------------------- #

def test_the_coverage_statement_is_BUILT_from_the_counts():
    """A hand-written coverage sentence goes stale on the first smart meter fitted. This repo
    has already filed that exact defect against a page that told three households they had no
    smart meter when they did."""
    book = hf.BookFootprint(accounts=(), counts={hf.MEASURED: 3, hf.PROFILED: 249, hf.UNCOVERED: 11})
    said = book.coverage_statement()

    assert "3 of 263" in said
    assert "249" in said and "UNAVAILABLE, not zero" in said
    assert "11 are UNCOVERED" in said and "not counted as zero" in said
    assert book.measured_share == pytest.approx(3 / 263)


def test_a_book_with_NOTHING_measured_says_so_in_its_first_breath():
    """The state this instrument is one meter-rollout decision away from, and the state it would
    be most tempting to describe in the same words as a measured one."""
    book = hf.BookFootprint(accounts=(), counts={hf.MEASURED: 0, hf.PROFILED: 263})

    assert "NOTHING here is measured" in book.coverage_statement()


def test_MUTATION_a_fully_measured_book_does_NOT_carry_the_nothing_measured_warning():
    book = hf.BookFootprint(accounts=(), counts={hf.MEASURED: 263, hf.PROFILED: 0})

    assert "NOTHING here is measured" not in book.coverage_statement()


def test_an_EMPTY_book_has_no_coverage_share_rather_than_a_perfect_one():
    book = hf.BookFootprint(accounts=(), counts={})
    with pytest.raises(hf.FootprintUnavailable):
        book.measured_share


# --------------------------------------------------------------------------- #
# The wall, and the single-owner rule                                          #
# --------------------------------------------------------------------------- #

def test_this_module_does_not_import_the_SIM():
    """The company reads a published FEED, the way a GB supplier reads NESO's. It does not look
    inside the world, and the fact that the shape happens to be produced there is exactly the
    thing it must not be able to depend on."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    offenders = sorted(m for m in imported if m.split(".")[0] in ("sim", "simulation"))
    assert offenders == [], f"the company layer imports {offenders} to compute carbon"


def test_the_annual_LEVEL_comes_from_the_single_owner_and_is_not_restated_here():
    """`tools/grid_intensity_guard.py` fails a second annual grid-intensity series under
    company/ -- written after three of them disagreed by up to 55.6% and nothing in the tree
    could observe that they did. This module would have been the fourth."""
    source = MODULE.read_text(encoding="utf-8")

    assert "from company.regulatory.carbon_emissions import" in source
    assert "grid_intensity_g_co2e_per_kwh" in source


# --------------------------------------------------------------------------- #
# The live feeds                                                               #
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not INTENSITY_FEED.is_file() or not CONSUMPTION_FEED.is_file(),
                    reason="the published feeds are not present in this tree")
def test_the_LIVE_feeds_produce_a_measurement_for_every_account_that_has_reads():
    """R11 to the value that will be rendered: the same numbers a reader sees, computed from the
    files on disk rather than from a fixture."""
    shape, _ = hf.load_shape()
    feed = json.loads(CONSUMPTION_FEED.read_text(encoding="utf-8"))
    by_account: dict[str, list] = {}
    for record in feed.get("records") or []:
        by_account.setdefault(str(record["customer_id"]), []).append(record)

    assert by_account, "the consumption feed carries no half-hourly reads at all"
    for account_id, reads in by_account.items():
        fp = hf.measured_footprint(account_id, reads, shape)
        assert fp.half_hours == len(reads), (
            f"{account_id}: {len(reads) - fp.half_hours} of its reads met no published half hour"
        )
        assert fp.co2e_kg_timed > 0.0
        assert abs(fp.timing_effect_pct) < 50.0, (
            f"{account_id}'s timing effect is {fp.timing_effect_pct:+.1f}%, which is outside "
            "anything the published shape's spread can produce over two days -- check the units"
        )
