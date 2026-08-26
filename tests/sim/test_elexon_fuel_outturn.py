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
# --------------------------------------------------------------------------- #
# The zero-carbon must-run fleet: the one series allowed across half-hourly    #
# --------------------------------------------------------------------------- #

def must_run_rows(readings, *, date: str, start_period: int = 1) -> list[dict]:
    """One (NUCLEAR, NPSHYD) pair per half hour, from `readings` of (nuclear_mw, hydro_mw)."""
    out: list[dict] = []
    for offset, (nuclear, hydro) in enumerate(readings):
        period = start_period + offset
        out.append(row("NUCLEAR", nuclear, date=date, period=period))
        out.append(row("NPSHYD", hydro, date=date, period=period))
    return out


def test_every_fuel_handed_over_half_hourly_has_a_published_factor_of_exactly_zero():
    """Condition 1 of the boundary: no part of the ANSWER may cross at this grain.

    Half-hourly gas and coal are refused because they ARE NESO's arithmetic. A series whose
    published factor is zero transfers no emissions term at all -- every gram in the
    reconstructed number still comes from a merit order this project decides for itself. That is
    the entire justification for the exception, so it is asserted against NESO's own published
    figure rather than against a sentence in a docstring.

    MUTATION (must fire): add "BIOMASS" (120 gCO2/kWh) or "CCGT" (394) to
    `ZERO_CARBON_MUST_RUN_FUEL_TYPES`.
    """
    for fuel_type in fuel.ZERO_CARBON_MUST_RUN_FUEL_TYPES:
        assert fuel_type in fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH, (
            f"{fuel_type} is handed over half-hourly with no published factor to check it against"
        )
        assert fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH[fuel_type] == 0.0, (
            f"{fuel_type} carries carbon on NESO's own table and must not cross half-hourly"
        )


def test_a_zero_published_factor_is_NOT_sufficient_and_pumped_storage_is_why():
    """Condition 2, and this test exists because condition 1 alone is fail-open.

    NESO publishes PUMPED STORAGE at zero gCO2/kWh, exactly like nuclear and hydro. Pumped
    storage is also pure price arbitrage -- it IS the merit order, wearing a zero factor -- so a
    rule of "hand over anything at zero" would hand over the answer while passing the test above.
    What separates them is the sign: a store goes NEGATIVE when it charges, and an availability
    cannot. That is the checkable form of "this is not a dispatch decision".

    MUTATION (must fire): add "PS" to `ZERO_CARBON_MUST_RUN_FUEL_TYPES`.
    """
    assert fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH["PS"] == 0.0, (
        "this test is only meaningful while pumped storage carries a zero factor"
    )
    assert "PS" not in fuel.ZERO_CARBON_MUST_RUN_FUEL_TYPES
    # And the sign rule that justifies the refusal is the one the parse actually applies.
    negative = fuel.zero_carbon_must_run_by_period(
        must_run_rows([(3_000.0, 400.0), (3_000.0, -1_766.0)], date="2024-03-01")
    )
    assert ("2024-03-01", 1) in negative
    assert ("2024-03-01", 2) not in negative


def test_a_half_hour_MISSING_one_must_run_fuel_is_skipped_rather_than_summed_as_zero():
    """A hole in the NUCLEAR feed and a half hour GB ran no reactors are one shape in JSON.

    Summed as zero the hole becomes a half hour whose baseload vanished, which the dispatch
    answers by burning gas for the whole residual -- inventing a dirty half hour out of a gap in
    the feed (R15 FAIL-OPEN). The same call `thermal_by_period` makes.

    MUTATION (must fire): `sum(latest.get((key, f), 0.0) for f in ZERO_CARBON_MUST_RUN_FUEL_TYPES)`.
    """
    rows = [
        row("NUCLEAR", 3_400, date="2024-03-01", period=1),
        row("NPSHYD", 550, date="2024-03-01", period=1),
        row("NPSHYD", 600, date="2024-03-01", period=2),   # NUCLEAR absent -- a hole, not a fact
    ]
    series = fuel.zero_carbon_must_run_by_period(rows)
    assert ("2024-03-01", 2) not in series
    assert series[("2024-03-01", 1)] == pytest.approx(3_950.0)


def test_a_ZERO_SUM_half_hour_is_a_dropout_and_never_reaches_the_dispatch():
    """GB has not had its whole nuclear and hydro fleet at zero in this window.

    A total of exactly zero is therefore a feed hole, and taken at face value it is the
    cleanest-possible-grid fiction `neso_carbon_intensity` already paid for once. Individual
    zeros are KEPT: one fleet idle while the other runs is a fact, not a hole.

    MUTATION (must fire): drop the `if total <= 0.0: continue` guard.
    """
    series = fuel.zero_carbon_must_run_by_period(
        must_run_rows([(0.0, 0.0), (3_400.0, 0.0), (0.0, 600.0)], date="2024-03-01")
    )
    assert ("2024-03-01", 1) not in series          # both zero -- a dropout
    assert series[("2024-03-01", 2)] == pytest.approx(3_400.0)   # hydro genuinely idle
    assert series[("2024-03-01", 3)] == pytest.approx(600.0)     # reactors genuinely off


def test_coverage_counts_the_half_hours_that_FELL_BACK_rather_than_reporting_full_coverage():
    """The fallback is invisible in the shape, so only this count can report it.

    A half hour served from the flat 5,600 MW and one served from a measured 5,600 MW produce an
    identical number. Without a coverage figure the correction could quietly stop applying to
    most of the series and nothing downstream would read differently (R15 FAIL-SILENT).

    MUTATION (must fire): return `usable_fraction: 1.0`, or stop counting the refusals.
    """
    rows = must_run_rows(
        [(3_400.0, 550.0), (0.0, 0.0), (3_400.0, -10.0), (3_400.0, 600.0)], date="2024-03-01"
    )
    rows.append(row("NUCLEAR", 3_400, date="2024-03-01", period=9))  # NPSHYD absent
    coverage = fuel.zero_carbon_must_run_coverage(rows)
    assert coverage["half_hours_seen"] == pytest.approx(5.0)
    assert coverage["usable_half_hours"] == pytest.approx(2.0)
    assert coverage["usable_fraction"] == pytest.approx(0.4)
    assert coverage["zero_sum_half_hours"] == pytest.approx(1.0)
    assert coverage["negative_half_hours"] == pytest.approx(1.0)
    assert coverage["missing_fuel_half_hours"] == pytest.approx(1.0)


def test_a_must_run_series_with_nothing_usable_RAISES_rather_than_returning_a_flat_block():
    """An absent series must not read as a grid whose baseload never moved.

    MUTATION (must fire): return `{}` instead of raising.
    """
    with pytest.raises(fuel.FuelOutturnUnavailable):
        fuel.zero_carbon_must_run_by_period(must_run_rows([(0.0, 0.0)], date="2024-03-01"))


# --------------------------------------------------------------------------- #
# The biomass envelope -- the fuel that is REFUSED at half-hourly grain        #
# --------------------------------------------------------------------------- #

def biomass_rows(readings, *, date: str, start_period: int = 1) -> list[dict]:
    """One BIOMASS row per half hour, from `readings` of MW."""
    return [
        row("BIOMASS", mw, date=date, period=start_period + offset)
        for offset, mw in enumerate(readings)
    ]


def test_biomass_FAILS_the_half_hourly_crossing_test_that_nuclear_and_hydro_PASS():
    """The reason this fuel is read at coal's grain and not at the must-run block's.

    This is the test that keeps the two rulings from blurring into "we read published outturn".
    Nuclear and hydro cross half-hourly because NESO prices them at exactly zero, so nothing of
    the ANSWER crosses. Biomass is priced at 120 gCO2/kWh on the same table -- its outturn IS an
    emissions term -- so it is refused at that grain and only its annual envelope crosses.

    READ FROM NESO'S OWN TABLE, not from a constant this project chose (R15 INDEPENDENCE): if
    NESO ever republished biomass at zero, this test would say so rather than defend a ruling
    that had stopped being true.

    MUTATION (must fire): add `BIOMASS` to `ZERO_CARBON_MUST_RUN_FUEL_TYPES`.
    """
    assert fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH["BIOMASS"] > 0.0, (
        "if NESO now prices biomass at zero the crossing rule has to be re-argued, not assumed"
    )
    assert fuel.BIOMASS_FUEL_TYPE not in fuel.ZERO_CARBON_MUST_RUN_FUEL_TYPES
    for crossing in fuel.ZERO_CARBON_MUST_RUN_FUEL_TYPES:
        assert fuel.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH[crossing] == 0.0


def test_the_envelope_carries_BOTH_ENDS_and_consumes_neither_percentile():
    """`capacity_mw` is the demonstrated maximum and `floor_mw` the demonstrated minimum.

    BOTH ENDS, because an envelope open at the bottom lets the fleet switch off in a quiet half
    hour -- and biomass switching off is exactly the change that makes a quiet half hour read as
    a perfectly clean grid, which is the direction every error in this module has to be checked
    against.

    The percentiles are published BESIDE them and never in place of them (R12: reported, never
    consumed); `mean_mw` is the one a goal-seeking author would reach for.

    MUTATION (must fire): return `p1_mw` as `floor_mw`, or `p99_mw` as `capacity_mw`.
    """
    # Split across four settlement dates because a day holds 48 periods, and the sample has to
    # be long enough that NEAREST-RANK puts both percentiles strictly inside the raw ends --
    # on a hundred readings the 99th percentile IS the maximum and the test could not tell the
    # robust statistic from the flattering one it exists to keep out of the dispatch.
    days = {
        "2024-03-01": [900.0] + [2_500.0] * 47,
        "2024-03-02": [2_500.0] * 48,
        "2024-03-03": [2_500.0] * 48,
        "2024-03-04": [2_500.0] * 47 + [3_180.0],
    }
    rows = [r for date, mws in days.items() for r in biomass_rows(mws, date=date)]
    envelope = fuel.biomass_envelope_by_year(fuel.biomass_by_period(rows))[2024]
    readings = [mw for mws in days.values() for mw in mws]
    assert envelope["floor_mw"] == pytest.approx(900.0)
    assert envelope["capacity_mw"] == pytest.approx(3_180.0)
    assert envelope["half_hours"] == pytest.approx(192.0)
    assert envelope["p1_mw"] > envelope["floor_mw"], (
        "the robust statistic must sit above the raw minimum, which is why it is not consumed"
    )
    assert envelope["p99_mw"] < envelope["capacity_mw"]
    assert envelope["mean_mw"] == pytest.approx(sum(readings) / len(readings))


def test_a_ZERO_biomass_reading_is_dropped_as_ABSENT_rather_than_taken_as_the_floor():
    """The lesson `neso_carbon_intensity` learned when NESO published `actual: 0`.

    A zero from a fleet that has never produced zero is a feed dropout. Taken as the floor it
    would hand the dispatch a fleet allowed to switch off entirely -- the fail-open shape, at
    exactly the fuel where it does the most damage.

    MUTATION (must fire): drop the `if value <= 0.0: continue` guard.
    """
    envelope = fuel.biomass_envelope_by_year(
        fuel.biomass_by_period(
            biomass_rows([0.0, 1_400.0, -5.0, 2_900.0], date="2024-03-01")
        )
    )[2024]
    assert envelope["floor_mw"] == pytest.approx(1_400.0)
    assert envelope["half_hours"] == pytest.approx(2.0)


def test_the_envelope_is_PER_YEAR_and_never_borrowed_across_one():
    """A fleet derates and units close; a year's envelope is a fact about that year.

    MUTATION (must fire): key the envelope on anything but the settlement date's year.
    """
    rows = (
        biomass_rows([1_000.0, 3_000.0], date="2023-06-01")
        + biomass_rows([500.0, 1_200.0], date="2024-06-01")
    )
    envelope = fuel.biomass_envelope_by_year(fuel.biomass_by_period(rows))
    assert envelope[2023]["capacity_mw"] == pytest.approx(3_000.0)
    assert envelope[2024]["capacity_mw"] == pytest.approx(1_200.0)
    assert envelope[2024]["floor_mw"] == pytest.approx(500.0)


def test_LAST_ROW_WINS_for_a_REPUBLISHED_biomass_half_hour():
    """FUELHH is republished with revisions; the later row is the corrected one.

    MUTATION (must fire): keep the first reading, or sum the two.
    """
    rows = [
        row("BIOMASS", 3_000.0, date="2024-03-01", period=7),
        row("BIOMASS", 1_100.0, date="2024-03-01", period=7),
    ]
    series = fuel.biomass_by_period(rows)
    assert series[("2024-03-01", 7)] == pytest.approx(1_100.0)
    assert len(series) == 1


def test_a_biomass_series_with_nothing_usable_RAISES_rather_than_returning_an_envelope():
    """An absent series must not read as a fleet with no envelope, because the caller's
    fallback for "no envelope" is the flat 2,400 MW block this measurement exists to remove.

    MUTATION (must fire): return `{}` instead of raising.
    """
    with pytest.raises(fuel.FuelOutturnUnavailable):
        fuel.biomass_envelope_by_year(
            fuel.biomass_by_period(biomass_rows([0.0, 0.0], date="2024-03-01"))
        )


def test_the_biomass_LOADER_refuses_an_absent_cache_rather_than_reverting_in_silence():
    """The same refusal the other three loaders carry (R15 FAIL-OPEN).

    MUTATION (must fire): return `[]` when the cache is missing.
    """
    missing = Path("sim/cache/does_not_exist_biomass.json")
    original = fuel.BIOMASS_CACHE_PATH
    try:
        fuel.BIOMASS_CACHE_PATH = missing
        with pytest.raises(fuel.FuelOutturnUnavailable):
            fuel.load_cached_biomass()
    finally:
        fuel.BIOMASS_CACHE_PATH = original
