"""R15 contract for the published fuel-mix adapter.

WHAT IS UNDER TEST is not "does it parse JSON". It is the four places where this module could
produce a plausible number that is wrong in a direction that flatters the mission:

  * NETTING A CABLE AGAINST A CABLE. GB exports on one interconnector while importing on
    another all the time. A single netted figure lets a clean export cancel a 474 gCO2/kWh Dutch
    import and quietly launders the half hour.
  * FILLING IN A FACTOR NOBODY PUBLISHED. Two of GB's cables postdate NESO's factor table.
    Giving them a "reasonable" number is the fabricated constant R10 forbids, and giving them
    zero is worse -- it is a claim that Norwegian and Danish imports are carbon-free.
  * READING A HOLE AS A ZERO. An idle cable and an absent reading are the same shape in JSON and
    are not the same fact. `neso_carbon_intensity` already found this the expensive way.
  * HANDING THE RECONSTRUCTION THE ANSWER. Half-hourly coal outturn is in the payload. If it
    ever reaches the shape as a dispatch input, the reconstruction stops being an independent
    route to NESO's number and the coupled-triad gap stops measuring anything.

Every test below states the mutation that must make it fail.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from sim import elexon_fuel_outturn as fuel

REPO = Path(__file__).resolve().parents[2]
KEY = ("2022-01-15", 20)


def row(fuel_type: str, generation, *, date: str = KEY[0], period: int = KEY[1]) -> dict:
    return {
        "dataset": "FUELHH",
        "settlementDate": date,
        "settlementPeriod": period,
        "fuelType": fuel_type,
        "generation": generation,
    }


# --------------------------------------------------------------------------- #
# The sign convention                                                         #
# --------------------------------------------------------------------------- #

def test_an_export_on_one_cable_cannot_cancel_an_import_on_another():
    """The half hour imports 1 GW of Dutch power and exports 1 GW to France.

    Netted, that is zero flow and a half hour that looks entirely domestic. It is not: a
    gigawatt of 474 gCO2/kWh electricity physically entered GB. Netting would delete it, and
    would delete it in the direction that makes the grid look cleaner than it was.

    MUTATION (must fire): sum the raw `generation` values before clamping at zero, instead of
    clamping each cable individually.
    """
    series = fuel.to_settlement_periods([row("INTNED", 1000), row("INTFR", -1000)])
    entry = series[KEY]
    assert entry["covered_import_mw"] == pytest.approx(1000.0)
    assert entry["covered_import_t_per_mwh"] == pytest.approx(0.474)


def test_an_export_only_half_hour_contributes_no_negative_emissions():
    """Exporting is not importing at a negative intensity.

    MUTATION (must fire): drop the `max(0.0, value)` clamp so an export becomes a negative
    import MW, which downstream multiplies into a negative tonnage and CREDITS GB demand.
    """
    series = fuel.to_settlement_periods([row("INTFR", -1500), row("INTNED", -200)])
    assert series[KEY]["covered_import_mw"] == 0.0
    assert series[KEY]["uncovered_import_mw"] == 0.0
    assert series[KEY]["covered_import_t_per_mwh"] == 0.0


# --------------------------------------------------------------------------- #
# The factor NESO never published                                             #
# --------------------------------------------------------------------------- #

def test_a_cable_with_no_published_factor_is_reported_separately_and_never_priced():
    """North Sea Link (Norway) and Viking Link (Denmark) postdate NESO's Table 1.

    They are not given a factor, and specifically not given ZERO -- "Norway is hydro so its
    imports are carbon-free" is the exact shape of the assumption that makes a clean end
    cleaner than reality. Their MW go to `uncovered_import_mw`, which is a number a reader can
    divide by.

    MUTATION (must fire): add "Norway" or "Denmark" to `IMPORT_INTENSITY_G_CO2_PER_KWH` with any
    value at all, including 0.
    """
    assert "Norway" not in fuel.IMPORT_INTENSITY_G_CO2_PER_KWH
    assert "Denmark" not in fuel.IMPORT_INTENSITY_G_CO2_PER_KWH
    series = fuel.to_settlement_periods([row("INTNSL", 1400), row("INTVKL", 800), row("INTFR", 2000)])
    entry = series[KEY]
    assert entry["uncovered_import_mw"] == pytest.approx(2200.0)
    assert entry["covered_import_mw"] == pytest.approx(2000.0)
    # The rate is the rate of the COVERED cables only. Averaging the uncovered MW in at zero is
    # the same fabrication wearing an arithmetic disguise.
    assert entry["covered_import_t_per_mwh"] == pytest.approx(0.053)


def test_every_import_factor_is_one_NESO_publishes():
    """R15 INDEPENDENCE. These are not this project's numbers.

    The reconstruction is graded against the series NESO builds with exactly these factors, so a
    locally-chosen value would put a FACTOR difference into a comparison whose only job is to
    measure a TIMING difference -- and it would be invisible, because both sides would still be
    carbon intensities in the right units.

    MUTATION (must fire): change any value here to a "better" or rounder one.
    """
    published = {"France": 53.0, "Netherlands": 474.0, "Belgium": 179.0, "Ireland": 458.0}
    assert fuel.IMPORT_INTENSITY_G_CO2_PER_KWH == published


def test_every_cable_in_the_dataset_is_mapped_to_a_market():
    """A new interconnector must not be silently absent.

    An unmapped `INT*` fuel type contributes nothing at all -- neither covered nor uncovered --
    so it would not even show up in the coverage figure that exists to bound this. That is the
    fail-silent shape: the gap would stop being measurable at the moment it grew.

    MUTATION (must fire): remove a cable from `INTERCONNECTOR_MARKETS`.
    """
    assert set(fuel.INTERCONNECTOR_MARKETS) == {
        "INTFR", "INTIFA2", "INTELEC", "INTIRL", "INTEW",
        "INTNED", "INTNEM", "INTNSL", "INTVKL",
    }
    unpriced = {
        market for market in fuel.INTERCONNECTOR_MARKETS.values()
        if market not in fuel.IMPORT_INTENSITY_G_CO2_PER_KWH
    }
    assert unpriced == {"Norway", "Denmark"}, (
        "the set of markets with no published factor has changed; if a factor has been ADDED it "
        "must be NESO's own, and if a market has been added it needs one or needs naming here"
    )


def test_the_import_rate_is_weighted_by_the_MW_actually_flowing():
    """2 GW of French at 53 and 1 GW of Dutch at 474 is 193.3, not the 263.5 of a flat mean.

    MUTATION (must fire): average the factors of the importing cables instead of weighting them,
    which over-weights the small clean cables GB runs constantly against the large dirty ones.
    """
    series = fuel.to_settlement_periods([row("INTFR", 2000), row("INTNED", 1000)])
    expected = (2000 * 53.0 + 1000 * 474.0) / 3000 / 1000.0
    assert series[KEY]["covered_import_t_per_mwh"] == pytest.approx(expected)
    assert expected == pytest.approx(0.19333, abs=1e-5)


# --------------------------------------------------------------------------- #
# Holes are not zeros                                                         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bad", [None, "1200", True, float("nan")])
def test_a_reading_that_is_not_a_number_is_skipped_rather_than_defaulted(bad):
    """An idle cable reads 0 and a broken feed reads nothing; they must not become one fact.

    `True` is in the list because `isinstance(True, int)` is True in Python and a bool that
    slipped through would be dispatched as 1 MW.

    MUTATION (must fire): `float(row.get("generation") or 0.0)`.
    """
    rows = [row("INTFR", bad), row("INTNED", 500)]
    if bad != bad:  # NaN reaches the parse as a float and must not poison the rate
        series = fuel.to_settlement_periods(rows)
        assert series[KEY]["covered_import_t_per_mwh"] == series[KEY]["covered_import_t_per_mwh"]
        return
    series = fuel.to_settlement_periods(rows)
    assert series[KEY]["covered_import_mw"] == pytest.approx(500.0)
    assert series[KEY]["covered_import_t_per_mwh"] == pytest.approx(0.474)


def test_a_revised_reading_replaces_the_one_it_revises_rather_than_adding_to_it():
    """FUELHH is republished. Two rows for one cable in one half hour is a revision, not 2 GW.

    MUTATION (must fire): accumulate into the running sum as rows arrive instead of resolving
    last-row-wins per (half hour, fuel) first.
    """
    series = fuel.to_settlement_periods([row("INTFR", 1000), row("INTFR", 1500)])
    assert series[KEY]["covered_import_mw"] == pytest.approx(1500.0)


def test_a_series_with_nothing_usable_raises_rather_than_returning_zeros():
    """Zero imports and zero coal is a VALID-LOOKING answer that silently restores the exact
    behaviour this module exists to remove.

    MUTATION (must fire): return `{}` instead of raising.
    """
    with pytest.raises(fuel.FuelOutturnUnavailable):
        fuel.to_settlement_periods([row("WIND", 9000), row("CCGT", 12000)])


# --------------------------------------------------------------------------- #
# Coal: a capacity measured, and a dispatch NOT handed over                   #
# --------------------------------------------------------------------------- #

def test_coal_capacity_is_the_demonstrated_annual_maximum_and_reaches_zero_on_its_own():
    """The fleet's own closure has to show up in the data, not in a hand-written end date.

    MUTATION (must fire): use the annual MEAN, or carry the previous year forward when a year's
    maximum is zero -- either of which resurrects a fleet that shut.
    """
    rows = [
        row("COAL", 4000, date="2019-02-01", period=1),
        row("COAL", 9000, date="2019-12-01", period=1),
        row("COAL", 0, date="2025-02-01", period=1),
    ]
    capacity = fuel.coal_capacity_by_year(fuel.to_settlement_periods(rows))
    assert capacity[2019] == pytest.approx(9000.0)
    assert capacity[2025] == pytest.approx(0.0)


def test_the_only_half_hourly_view_handed_to_the_reconstruction_carries_no_coal():
    """`imports_by_period` is the boundary. Coal crosses it only as one number per year.

    If half-hourly coal outturn reached the shape, the reconstruction would stop deciding for
    itself whether coal ran -- which is the merit-order question it exists to answer -- and
    would become NESO's own arithmetic with a different cache. The gap would then measure
    nothing, while still producing a number.

    MUTATION (must fire): add coal to the tuple `imports_by_period` returns.
    """
    series = fuel.to_settlement_periods([row("COAL", 3000), row("INTFR", 1000)])
    handed = fuel.imports_by_period(series)
    assert handed[KEY] == pytest.approx((1000.0, 0.053))
    assert len(handed[KEY]) == 2
    assert 3000.0 not in handed[KEY]


def test_the_reconstruction_does_not_import_this_module():
    """The shape must stay a pure function of the arguments it is given.

    A module that can reach in here for the metered mix is one edit from reading half-hourly
    coal and interconnector CARBON directly, and no test of the shape's arithmetic would notice.
    Structural, because the intent version of this rule is a sentence in a docstring.

    MUTATION (must fire): `from sim.elexon_fuel_outturn import ...` in the shape module.
    """
    tree = ast.parse((REPO / "sim" / "grid_carbon_intensity.py").read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not [name for name in imported if "elexon_fuel_outturn" in name]


# --------------------------------------------------------------------------- #
# The thermal floor                                                           #
# --------------------------------------------------------------------------- #

def thermal_rows(readings, *, date: str, start_period: int = 1) -> list[dict]:
    """One (CCGT, OCGT) pair per half hour, from `readings` of (ccgt_mw, ocgt_mw)."""
    out: list[dict] = []
    for offset, (ccgt, ocgt) in enumerate(readings):
        period = start_period + offset
        out.append(row("CCGT", ccgt, date=date, period=period))
        out.append(row("OCGT", ocgt, date=date, period=period))
    return out


def test_the_floor_is_the_demonstrated_annual_MINIMUM_and_not_a_robust_percentile():
    """The number the dispatch consumes must be the smallest reading, not the tidier one.

    A 1st percentile is the statistically robust choice AND the flattering one: it is higher, so
    it dirties the clean end, narrows the modelled swing and improves this model's score against
    the published series it is graded on. Choosing it would be indistinguishable from choosing
    the number that makes the answer look good (R12).

    MUTATION (must fire): return `p1_mw` as `floor_mw`, or use the annual mean.
    """
    readings = [(float(1000 + 100 * i), 0.0) for i in range(100)]  # 1000..10900 MW
    floors = fuel.thermal_floor_by_year(
        fuel.thermal_by_period(thermal_rows(readings, date="2024-03-01"))
    )
    assert floors[2024]["floor_mw"] == pytest.approx(1000.0)
    # The diagnostic is published and is STRICTLY higher, which is the whole reason it is not used.
    assert floors[2024]["p1_mw"] > floors[2024]["floor_mw"]
    assert floors[2024]["half_hours"] == pytest.approx(100.0)


def test_a_half_hour_MISSING_one_thermal_fuel_is_skipped_rather_than_summed_as_zero():
    """A hole in the CCGT feed and a half hour GB ran no gas are the same shape in JSON.

    Summed as zero, the hole becomes a ~0 MW floor for the whole year -- which is precisely the
    zero-thermal fiction this measurement exists to remove, reintroduced by the measurement
    itself (R15 FAIL-OPEN).

    MUTATION (must fire): `sum(latest.get((key, f), 0.0) for f in THERMAL_FUEL_TYPES)`.
    """
    rows = [
        row("CCGT", 9000, date="2024-03-01", period=1),
        row("OCGT", 200, date="2024-03-01", period=1),
        row("OCGT", 150, date="2024-03-01", period=2),   # CCGT absent -- a hole, not a fact
    ]
    series = fuel.thermal_by_period(rows)
    assert ("2024-03-01", 2) not in series
    assert series[("2024-03-01", 1)] == pytest.approx(9200.0)
    assert fuel.thermal_floor_by_year(series)[2024]["floor_mw"] == pytest.approx(9200.0)


def test_a_ZERO_thermal_reading_is_a_dropout_and_never_becomes_the_floor():
    """GB's thermal fleet has never produced zero, so a zero is a feed outage by construction.

    Taken as the floor it would restore the exact behaviour being corrected, and it would do so
    silently -- the same failure `neso_carbon_intensity` hit when NESO published `actual: 0` for
    five half hours and the first run reported the cleanest possible grid as fact.

    MUTATION (must fire): drop the `if value <= 0.0: continue` guard.
    """
    readings = [(0.0, 0.0), (4000.0, 100.0), (6000.0, 0.0)]
    floors = fuel.thermal_floor_by_year(
        fuel.thermal_by_period(thermal_rows(readings, date="2024-03-01"))
    )
    assert floors[2024]["floor_mw"] == pytest.approx(4100.0)
    assert floors[2024]["half_hours"] == pytest.approx(2.0)


def test_a_year_with_no_positive_thermal_reading_RAISES_rather_than_flooring_at_zero():
    """An absent series must not read as a grid that ran no gas.

    MUTATION (must fire): return `{}` or a zero floor instead of raising.
    """
    with pytest.raises(fuel.FuelOutturnUnavailable):
        fuel.thermal_floor_by_year(
            fuel.thermal_by_period(thermal_rows([(0.0, 0.0)], date="2024-03-01"))
        )


def test_the_reconstruction_is_handed_no_half_hourly_gas():
    """The same boundary the coal series is held behind, for the same reason.

    A dispatch model handed the metered gas output of each half hour is not a second route to
    NESO's number -- it is NESO's arithmetic with a different cache, and the coupled-triad gap it
    is graded on would measure nothing while still producing a figure.

    MUTATION (must fire): pass `thermal_by_period(...)` into `build_shape`, or widen
    `thermal_floor_by_year`'s return to carry a per-half-hour series.
    """
    import inspect

    from tools import generate_grid_intensity_feed as feed

    source = inspect.getsource(feed.generate)
    assert "thermal_by_period" not in source, (
        "generate() must hand build_shape the per-YEAR floor only; thermal_by_period is a "
        "measurement input and must not reach the dispatch"
    )
    floors = fuel.thermal_floor_by_year(
        fuel.thermal_by_period(thermal_rows([(4000.0, 100.0)], date="2024-03-01"))
    )
    # One record per YEAR, never per half hour.
    assert set(floors) == {2024}
    assert set(floors[2024]) == {"floor_mw", "p1_mw", "half_hours"}


# --------------------------------------------------------------------------- #
# The gap, quoted in per cent                                                 #
# --------------------------------------------------------------------------- #

def test_import_coverage_is_measured_in_MWh_and_not_in_cables():
    """Two of nine cables unpriced says nothing about how much energy is unpriced.

    MUTATION (must fire): report the fraction of CABLES with a factor instead of the fraction of
    imported MWh, which here would read 7/9 = 78% against the true 33%.
    """
    series = fuel.to_settlement_periods([row("INTFR", 1000), row("INTNSL", 2000)])
    coverage = fuel.import_coverage(series)
    assert coverage["covered_fraction"] == pytest.approx(1000 / 3000)


def test_coverage_over_a_year_with_no_imports_raises_rather_than_reading_as_full_coverage():
    """0/0 must not become 1.0. A year GB imported nothing has never happened, so this is an
    absence, and an absence reported as total coverage is the flattering answer.

    MUTATION (must fire): return `covered / (total or 1.0)`.
    """
    series = fuel.to_settlement_periods([row("COAL", 500)])
    with pytest.raises(fuel.FuelOutturnUnavailable):
        fuel.import_coverage(series)
