"""The historical half-hourly carbon series. Each test names the defect it exists to catch.

The partition test comes first. Gaps and fills are the branches the code rarely takes, so we
first show that all three sources can be produced, and only then what each one does.
"""
from __future__ import annotations

import json

import pytest

from sim import elexon_fuel_outturn as efo
from sim import grid_carbon_history as gch
from sim.grid_carbon_history import (
    FUELMIX_FILL,
    GAP,
    NESO_HISTORIC_MIX,
    assemble,
    fuel_mix_by_period,
    fuelmix_intensity,
    historic_mix_by_period,
    load_neso,
    overlap_pairs,
    overlap_statistics,
    settlement_periods_on,
    settlement_universe,
)

PRE = ("2017-06-01", 20)
POST = ("2019-06-01", 20)


def _mix(**over: float) -> dict[str, float]:
    """A complete post-split mix: every required fuel present, CCGT and nuclear running."""
    fuels = {f: 0.0 for f in gch.REQUIRED_FUELS}
    fuels.update({"CCGT": 10000.0, "NUCLEAR": 6000.0, efo.BIOMASS_FUEL_TYPE: 0.0})
    fuels.update(over)
    return fuels


SPLIT = ("2017-11-01", 41)


def _neso_record(utc_from: str, actual):
    return {"from": utc_from, "to": "", "intensity": {"forecast": 200, "actual": actual}}


def _mix_row(utc_start: str, intensity, *, generation=30000.0, wind=5000.0, hydro=300.0):
    """One `df_fuel_ckan.csv` row, as `csv.DictReader` gives it: every value a string."""
    return {"DATETIME": utc_start, "CARBON_INTENSITY": "" if intensity is None else str(intensity),
            "GENERATION": str(generation), "WIND": str(wind), "HYDRO": str(hydro)}


# ---------------------------------------------------------------- the partition


def test_every_source_in_the_partition_is_reachable_so_a_collapsed_branch_cannot_hide():
    """Defect: a branch that is never taken, e.g. every missing historic-mix value becoming a gap,
    or a fill read as the historic mix."""
    gap_key = ("2019-06-01", 21)
    fill_key = ("2019-06-01", 22)
    universe = [PRE, POST, gap_key, fill_key]
    raw = {PRE: (200.0, None), POST: (150.0, None), gap_key: (None, "fuelhh_absent"),
           fill_key: (170.0, None)}
    series = assemble(universe, raw, {PRE: 210.0, POST: 160.0}, {fill_key})
    assert {r.source for r in series.values()} == {NESO_HISTORIC_MIX, FUELMIX_FILL, GAP}
    assert series[PRE].value == 210.0, "the historic mix is the value before 2018 too"
    assert series[gap_key].value is None and "fuelhh_absent" in series[gap_key].reason
    assert series[gap_key].reason.startswith("historic_mix_no_record")
    assert series[fill_key].reason == "historic_mix_outage_signature"
    assert series[fill_key].value == 170.0, "the fill is unscaled"


def test_the_real_series_reaches_every_source_and_covers_every_settlement_period():
    """Defect: the same collapse, but on the real caches. Skipped where they are absent.

    On the real record the fill is legitimately empty today (every historic-mix hole is also a
    FUELHH hole), so this asserts the two sources the record reaches and that the fill is a subset
    of the partition, never that it is non-empty."""
    try:
        series, meta = gch.load_series()
    except Exception as exc:  # noqa: BLE001 -- any missing cache is a skip, not a pass
        pytest.skip(f"real caches not available here: {exc}")
    sources = {r.source for r in series.values()}
    assert {NESO_HISTORIC_MIX, GAP} <= sources <= set(gch.SOURCES)
    assert set(series) == set(settlement_universe())
    assert meta["data_regime"] == "historical"
    # The 2023-06-07 feed outage (UTC 10:00-11:30): never a zero, never the historic mix's
    # wind-less value. Period 22 is the PARTIAL drop neither signature catches (finding 4).
    for p in (23, 24, 25, 26):
        r = series[("2023-06-07", p)]
        assert r.source in (FUELMIX_FILL, GAP) and r.value != 0.0
    # The API's basis change is visible in the cross-check and absent from the series.
    step = meta["api_step"]
    assert step["before"]["ratio"] > 1.08 > 1.05 > step["after"]["ratio"]


def test_the_historic_mix_is_keyed_by_utc_start_and_its_outages_are_signatures():
    """Defects: reading `DATETIME` as local time (which would put every BST half hour one period
    late), a null or zero intensity passed through, and the partial outage of finding 4 (wind and
    hydro both exactly zero, so the intensity sees only gas) read as a real dirty half hour."""
    rows = [
        _mix_row("2024-10-27T23:30:00", 120.0),                  # GMT: the day's 50th period
        _mix_row("2023-06-07T09:00:00", 174.0),                  # BST 10:00: period 21
        _mix_row("2023-06-07T09:30:00", 0.0),                    # zero intensity
        _mix_row("2023-06-07T10:00:00", None),                   # null intensity
        _mix_row("2023-06-07T10:30:00", 179.0, wind=0.0, hydro=0.0),   # partial outage
        _mix_row("2023-06-07T11:00:00", 179.0, wind=0.0, hydro=12.0),  # calm, not an outage
        _mix_row("2023-06-07T11:30:00", 13579.0),                # above the ceiling
    ]
    usable, signatures, last = historic_mix_by_period(rows)
    assert usable == {("2024-10-27", 50): 120.0, ("2023-06-07", 21): 174.0,
                      ("2023-06-07", 25): 179.0}
    assert signatures == {("2023-06-07", p) for p in (22, 23, 24, 26)}
    assert last == "2024-10-27T23:30:00"


# ---------------------------------------------------------------- settlement alignment


def test_clock_change_days_have_46_and_50_periods_not_48():
    """Defect: subtracting two same-tz datetimes as wall-clock time, which makes every day 48.
    The first draft had this, and it put periods 47 and 48 onto every spring clock-change day."""
    assert settlement_periods_on("2016-03-27") == 46
    assert settlement_periods_on("2024-10-27") == 50
    assert settlement_periods_on("2024-06-01") == 48
    days = [k for k in settlement_universe("2016-03-27", "2016-03-27")]
    assert [p for _, p in days] == list(range(1, 47))


def test_fuelhh_rows_are_keyed_by_start_time_not_by_the_mislabelled_period_48():
    """Defect: trusting FUELHH's `settlementDate`, which puts D-1's period 48 on day D up to
    2022. Also covers the autumn clock-change day's 50th period."""
    rows = [
        {"settlementDate": "2016-01-07", "settlementPeriod": 48,
         "startTime": "2016-01-06T23:30:00Z", "fuelType": "CCGT", "generation": 8000},
        {"settlementDate": "2016-10-30", "settlementPeriod": 48,
         "startTime": "2016-10-30T23:30:00Z", "fuelType": "CCGT", "generation": 7000},
        {"settlementDate": "2016-03-27", "settlementPeriod": 46,
         "startTime": "2016-03-27T22:30:00Z", "fuelType": "CCGT", "generation": 6000},
    ]
    out = fuel_mix_by_period(rows)
    assert out[("2016-01-06", 48)] == {"CCGT": 8000.0}
    assert ("2016-01-07", 48) not in out
    assert out[("2016-10-30", 50)] == {"CCGT": 7000.0}
    assert out[("2016-03-27", 46)] == {"CCGT": 6000.0}


def test_neso_records_land_on_the_same_key_as_fuelhh_on_a_clock_change_day():
    """Defect: the two sources disagreeing on which half hour is which. That would pair the
    wrong half hours in the overlap and in the fill."""
    published, _ = load_neso([_neso_record("2024-10-27T23:30Z", 120)])
    mix = fuel_mix_by_period([{"startTime": "2024-10-27T23:30:00Z", "fuelType": "CCGT",
                               "generation": 1.0}])
    assert set(published) == set(mix) == {("2024-10-27", 50)}


# ---------------------------------------------------------------- outages


def test_a_neso_zero_or_null_becomes_fuelmix_fill_never_a_zero():
    """Defect: a published zero (2023-06-07) passed through as 0 gCO2/kWh, or dropped silently."""
    records = [_neso_record("2023-06-07T10:00Z", 0), _neso_record("2023-06-07T10:30Z", None),
               _neso_record("2023-06-07T11:00Z", 150)]
    published, signatures = load_neso(records)
    # 10:00Z in June is 11:00 BST, which is period 23.
    zero_key, null_key, ok_key = ("2023-06-07", 23), ("2023-06-07", 24), ("2023-06-07", 25)
    assert published == {ok_key: 150.0}
    assert signatures == {zero_key, null_key}
    # The API is the cross-check now; its parse still refuses the zero and the null.


def test_a_neso_value_above_the_physical_ceiling_is_a_signature_not_published():
    """Defect: a 13,579 g reading (the kind NESO's forecast field carries) read as real."""
    published, signatures = load_neso([_neso_record("2023-06-07T10:00Z", 13579)])
    assert published == {} and signatures == {("2023-06-07", 23)}


def test_an_all_zero_fuelhh_half_hour_is_refused_not_priced_at_zero():
    """Defect: FUELHH's own outage (every fuel 0 MW) priced at 0 g, or at the imports alone."""
    zero = {f: 0.0 for f in gch.REQUIRED_FUELS} | {efo.BIOMASS_FUEL_TYPE: 0.0, "INTNED": 900.0}
    value, why = fuelmix_intensity(zero, POST, 500.0, split=SPLIT)
    assert value is None and why == "fuelhh_outage_signature"
    # The same assembly then refuses to call it a fill.
    series = assemble([POST], {POST: (value, why)}, {}, {POST})
    assert series[POST].source == GAP and series[POST].value is None


def test_an_incomplete_mix_is_a_gap_with_its_reason_not_a_price():
    """Defect: a half hour missing CCGT priced as if GB ran no gas."""
    fuels = _mix()
    del fuels["CCGT"]
    value, why = fuelmix_intensity(fuels, POST, 0.0, split=SPLIT)
    assert value is None and "CCGT" in why


# ---------------------------------------------------------------- the arithmetic


def test_the_estimate_is_neso_arithmetic_over_generation_imports_and_embedded():
    """Defect: a denominator that leaves out imports or embedded generation, or a numerator that
    nets an export against an import."""
    fuels = _mix(CCGT=1000.0, NUCLEAR=1000.0, INTNED=500.0, INTFR=-400.0, PS=-300.0)
    value, _ = fuelmix_intensity(fuels, POST, 500.0, split=SPLIT)
    table = efo.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH
    expected = (1000 * table["CCGT"] + 500 * efo.import_factor("Netherlands", "2019")) / 3000.0
    assert value == pytest.approx(expected)


def test_changing_a_neso_factor_changes_the_fill(monkeypatch):
    """Defect: the factors restated or frozen here, so a correction to NESO's table never
    reaches the fill."""
    fuels = _mix()
    before, _ = fuelmix_intensity(fuels, PRE, 0.0, split=SPLIT)
    patched = dict(efo.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH, CCGT=500.0)
    monkeypatch.setattr(efo, "NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH", patched)
    after, _ = fuelmix_intensity(fuels, PRE, 0.0, split=SPLIT)
    assert after == pytest.approx(before * 500.0 / 394.0)


def test_before_the_biomass_split_other_is_priced_as_biomass():
    """Defect: pricing pre-November-2017 OTHER, which is mostly Drax biomass, at OTHER's 300 g."""
    fuels = _mix(CCGT=0.0, NUCLEAR=0.0, OTHER=1000.0)
    del fuels[efo.BIOMASS_FUEL_TYPE]
    table = efo.NESO_PUBLISHED_FACTOR_G_CO2_PER_KWH
    pre, _ = fuelmix_intensity(fuels, PRE, 0.0, split=SPLIT)
    assert pre == pytest.approx(table["BIOMASS"])
    post, _ = fuelmix_intensity(_mix(CCGT=0.0, NUCLEAR=0.0, OTHER=1000.0), POST, 0.0, split=SPLIT)
    assert post == pytest.approx(table["OTHER"])


def test_cables_outside_nesos_mix_carry_no_tonnes_and_leave_the_denominator():
    """Defect: ElecLink or Viking counted, which NESO's own published mix does not do."""
    base, _ = fuelmix_intensity(_mix(), POST, 0.0, split=SPLIT)
    with_viking, _ = fuelmix_intensity(_mix(INTVKL=1400.0), POST, 0.0, split=SPLIT)
    assert with_viking == base


# ---------------------------------------------------------------- the cross-checks


def test_overlap_statistics_are_computed_over_the_overlap_only():
    """Defect: pairs from outside the window (a pre-2018 estimate, or a published value with
    no estimate) entering the correlation, bias or RMSE."""
    estimate = {("2017-01-01", 1): 900.0, ("2019-01-01", 1): 110.0, ("2019-01-01", 2): 210.0,
                ("2020-01-01", 1): 150.0}
    published = {("2017-01-01", 1): 100.0, ("2019-01-01", 1): 100.0, ("2019-01-01", 2): 200.0,
                 ("2020-01-01", 1): 140.0, ("2020-01-01", 2): 999.0}
    stats = overlap_statistics(estimate, published, ("2018-05-11", "2025-12-31"))
    assert set(stats) == {"2019", "2020", "ALL"}
    assert stats["ALL"]["n"] == 3
    assert stats["ALL"]["mean_bias"] == pytest.approx(10.0)
    assert stats["ALL"]["rmse"] == pytest.approx(10.0)
    pairs = overlap_pairs(estimate, published, ("2018-05-11", "2019-12-31"))
    assert set(pairs) == {("2019-01-01", 1), ("2019-01-01", 2)}


def test_a_built_artefact_from_other_inputs_is_not_served(tmp_path, monkeypatch):
    """Defect: a stale artefact served after an input cache changed."""
    path = tmp_path / "built.json"
    monkeypatch.setattr(gch, "_input_fingerprint", lambda: [["a", 1, 1]])
    gch.write_built({PRE: gch.Reading(1.0, FUELMIX_FILL)}, {"x": 1}, path)
    assert gch._read_built(path) is not None
    monkeypatch.setattr(gch, "_input_fingerprint", lambda: [["a", 2, 1]])
    assert gch._read_built(path) is None
    assert json.loads(path.read_text())["series"] == [[PRE[0], PRE[1], 1.0, FUELMIX_FILL, None]]
