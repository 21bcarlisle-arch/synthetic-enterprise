"""Controls for `sim/grid_carbon_future.py`: future grid carbon from the analogue year the world replays.

Each test names the defect it exists to catch. The rare branches (a defect half hour, a date inside
the record, a year with no analogue) are shown to be REACHABLE before anything is asserted about
what they return.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date

import numpy as np
import pytest

from sim import grid_carbon_future as g
from sim.grid_carbon_history import settlement_periods_on
from sim.weather_world import WeatherWorld

SEED = "test_world:1"


# ------------------------------------------------------------------------------- fixtures

def _hh(tx_wind=5_000.0, emb_wind=1_500.0, emb_solar=0.0, tx_demand=28_000.0) -> g.HalfHour:
    return g.HalfHour(tx_wind, emb_wind, emb_solar, tx_demand)


def _inputs(days: dict[str, g.HalfHour]) -> dict:
    """Every period of each day carries that day's half hour."""
    return {(d, p): hh for d, hh in days.items() for p in range(1, settlement_periods_on(d) + 1)}


class _Mapped:
    """A run's already-extended world: it carries `analogue_years` and nothing else is read."""

    def __init__(self, years: dict[int, int]):
        self.analogue_years = years


def _flat_capacity(tech: str, year: int) -> float:
    return 1_000.0


def _small_world(first: int = 2016, last: int = 2017) -> WeatherWorld:
    """A REAL WeatherWorld over two complete years; each row is stamped with its own date."""
    daily: dict[str, dict] = {}
    d = date(first, 1, 1)
    while d.year <= last:
        daily[d.isoformat()] = {"temperature_mean_c": float(d.toordinal())}
        d = date.fromordinal(d.toordinal() + 1)
    return WeatherWorld({}, {"r": daily}, {})


def _future(day, period, *, years={2027: 2019}, inputs=None, capacity=_flat_capacity, **kw):
    if inputs is None:
        inputs = _inputs({"2019-06-01": _hh(), "2025-06-01": _hh()})
    return g.future_intensity_at(day, period, SEED, world=_Mapped(years), inputs=inputs, gaps={},
                                 capacity=capacity, **kw)


def _planted_record(signal: bool, seed: int = 4) -> dict:
    """Three years of half hours; with `signal`, intensity is the share_log form plus noise."""
    rng = np.random.default_rng(seed)
    dates = np.array([f"{y}-{m:02d}-{dd:02d}" for y in (2023, 2024, 2025) for m in range(1, 13)
                      for dd in range(1, 29) for _ in range(12)])
    n = len(dates)
    wind, solar = rng.uniform(1, 20, n), rng.uniform(0, 10, n)
    demand = rng.uniform(20, 40, n)
    share = (wind + solar) / demand
    noise = rng.normal(0, 0.1, n)
    log_y = 5.0 - 2.4 * share + 0.02 * demand + noise if signal else 4.9 + noise
    return {"date": dates, "actual": np.exp(log_y), "wind_gw": wind, "solar_gw": solar,
            "demand_gw": demand, "share": share}


# ------------------------------------------------------------------------- the model

def test_the_fitted_model_beats_a_constant_on_a_held_out_year_and_the_comparison_can_fail():
    test = np.array([d.startswith("2025") for d in _planted_record(True)["date"]])
    # The rare branch first: on a record with NO signal the model must not beat the constant. If it
    # did, "beats a constant" would be a property of the grader, not of the record.
    null = _planted_record(False)
    null_model = g.grade(g.fit(null, g.HELD_OUT_TRAIN), null, test)["rmse"]
    null_const = g.grade(g.fit(null, g.HELD_OUT_TRAIN, form="constant"), null, test)["rmse"]
    assert null_model >= 0.98 * null_const, (null_model, null_const)
    planted = _planted_record(True)
    model = g.grade(g.fit(planted, g.HELD_OUT_TRAIN), planted, test)
    const = g.grade(g.fit(planted, g.HELD_OUT_TRAIN, form="constant"), planted, test)
    assert model["rmse"] < 0.6 * const["rmse"], (model, const)
    assert model["correlation"] > 0.8


def test_the_fit_recovers_planted_coefficients_and_reads_only_its_window():
    rec = _planted_record(True)
    m = g.fit(rec, ("2023-01-01", "2024-12-31"))
    assert m.coefficients == pytest.approx((5.0, -2.4, 0.02), abs=0.02)
    assert (m.fit_from, m.fit_to) == ("2023-01-01", "2024-12-28")
    shifted = dict(rec, actual=np.where([d.startswith("2025") for d in rec["date"]],
                                        rec["actual"] * 10, rec["actual"]))
    assert g.fit(shifted, ("2023-01-01", "2024-12-31")) == m, "the fit read outside its window"


def test_a_window_shorter_than_ninety_days_is_refused_and_says_why():
    with pytest.raises(g.FutureCarbonUnavailable, match="season, not a regime"):
        g.fit(_planted_record(True), ("2023-01-01", "2023-03-31"))


def test_the_shipped_model_is_positive_without_a_floor_and_falls_with_share():
    shares = np.linspace(0.0, 1.0, 11)
    values = g.predict(shares, np.full(11, 30.0))
    assert np.all(values > 0)
    assert np.all(np.diff(values) < 0), "more wind and solar per unit of demand must read cleaner"


# --------------------------------------------------------------------- the inputs

def test_true_demand_counts_the_generation_embedded_under_the_meter():
    hh = _hh(tx_wind=4_000, emb_wind=1_000, emb_solar=3_000, tx_demand=25_000)
    assert hh.demand_mw == 29_000
    assert hh.wind_mw == 5_000 and hh.solar_mw == 3_000


def test_a_publication_defect_is_found_and_a_normal_half_hour_is_not():
    normal = {"CCGT": 9_000.0, "NUCLEAR": 5_000.0, "WIND": 6_000.0, "INTFR": 1_000.0}
    zero = {f: 0.0 for f in g.DOMESTIC_FUELS} | {"INTFR": -1_000.0}
    partial = {k: v * 0.3 for k, v in normal.items()}
    mix = {("2022-08-02", 1): normal, ("2022-08-02", 2): partial, ("2022-08-02", 3): normal,
           ("2022-08-02", 4): zero, ("2022-08-02", 5): normal}
    defects = g.publication_defects(mix)
    assert set(defects) == {("2022-08-02", 2), ("2022-08-02", 4)}
    assert "zero" in defects[("2022-08-02", 4)] and "partial" in defects[("2022-08-02", 2)]


def test_a_defect_half_hour_in_the_record_returns_none_with_its_reason():
    mix = {("2019-06-01", p): {"CCGT": 9_000.0, "NUCLEAR": 5_000.0, "WIND": 6_000.0}
           for p in range(1, 49)} | {("2025-06-01", p): {"CCGT": 9_000.0, "WIND": 6_000.0}
                                     for p in range(1, 49)}
    mix[("2019-06-01", 20)] = {f: 0.0 for f in g.DOMESTIC_FUELS}
    embedded = {k: {"wind_mw": 1_000.0, "solar_mw": 0.0} for k in mix}
    inputs, gaps = g.build_inputs(mix, embedded)
    value, prov = g.future_intensity_at("2027-06-01", 20, SEED, world=_Mapped({2027: 2019}),
                                        inputs=inputs, gaps=gaps, capacity=_flat_capacity)
    assert value is None and "every domestic fuel at zero" in prov["reason"]
    ok, _ = g.future_intensity_at("2027-06-01", 21, SEED, world=_Mapped({2027: 2019}),
                                  inputs=inputs, gaps=gaps, capacity=_flat_capacity)
    assert ok is not None


# -------------------------------------------------------------------- the futures

def test_a_windier_analogue_day_yields_lower_intensity_than_a_calm_one():
    inputs = _inputs({"2019-06-01": _hh(tx_wind=15_000), "2019-06-02": _hh(tx_wind=1_000),
                      "2025-06-01": _hh()})
    windy, _ = _future("2027-06-01", 20, inputs=inputs)
    calm, _ = _future("2027-06-02", 20, inputs=inputs)
    assert windy < calm - 20, (windy, calm)


def test_the_fleet_rescale_moves_the_value_when_capacity_differs():
    def grown(tech, year):
        return 2_000.0 if (tech.startswith("wind") and year == 2027) else 1_000.0

    same, p_same = _future("2027-06-01", 20)
    more, p_more = _future("2027-06-01", 20, capacity=grown)
    assert p_same["wind_factor"] == 1.0 and p_more["wind_factor"] == 2.0
    assert more < same, "a bigger wind fleet must read cleaner on the same weather"


def test_the_real_fleet_rescale_grows_wind_and_solar_toward_the_held_flat_2025_fleet():
    for record_year in range(2016, 2025):
        f = g.fleet_factors(record_year, 2030)
        assert f["wind"] > 1.0 and f["solar"] > 1.0, (record_year, f)
    assert g.fleet_factors(2025, 2030) == {"wind": 1.0, "solar": 1.0}


def test_the_demand_factor_holds_a_record_year_at_the_reference_years_level():
    inputs = _inputs({"2019-06-01": _hh(tx_demand=33_000), "2025-06-01": _hh(tx_demand=29_500)})
    _, prov = _future("2027-06-01", 20, inputs=inputs)
    assert prov["demand_factor"] == pytest.approx(31_000 / 34_500, abs=1e-4)
    assert prov["demand_gw"] == pytest.approx(31.0, abs=1e-3)


def test_the_analogue_mapping_is_the_worlds_own_and_the_result_follows_it(monkeypatch):
    world = _small_world()
    inputs = _inputs({"2016-06-01": _hh(tx_wind=15_000), "2017-06-01": _hh(tx_wind=1_000),
                      "2025-06-01": _hh()})
    own = world.extended_by_analogue_years("2019-12-31", seed=SEED).analogue_years[2019]
    year, how = g.analogue_year(2019, SEED, world)
    assert year == own and "extended_by_analogue_years" in how
    values = {}
    for forced in (2016, 2017):
        g._ANALOGUE_CACHE.clear()
        monkeypatch.setattr(WeatherWorld, "extended_by_analogue_years",
                            lambda self, through, seed, y=forced: _Mapped({2019: y}))
        values[forced], prov = g.future_intensity_at("2019-06-01", 20, SEED, world=world,
                                                     inputs=inputs, gaps={},
                                                     capacity=_flat_capacity)
        assert prov["analogue_year"] == forced and prov["record_date"] == f"{forced}-06-01"
    assert values[2016] < values[2017]
    g._ANALOGUE_CACHE.clear()


def test_a_date_inside_the_record_and_a_year_with_no_analogue_return_none_with_a_reason():
    world = _small_world()
    inside, why = g.analogue_year(2017, SEED, world)
    assert inside is None and "inside the record" in why
    value, prov = _future("2031-06-01", 20, years={2027: 2019})
    assert value is None and "no analogue for 2031" in prov["reason"]


def test_clock_change_days_resolve_every_period_by_local_clock_time():
    spring, autumn = date(2027, 3, 28), date(2027, 10, 31)
    plain_spring, plain_autumn = date(2019, 3, 28), date(2019, 10, 31)
    assert (settlement_periods_on(spring.isoformat()), settlement_periods_on(autumn.isoformat())) == (46, 50)
    # Every period of each change day resolves, and none outside it does.
    for fwd, src in ((spring, plain_spring), (autumn, plain_autumn)):
        n = settlement_periods_on(fwd.isoformat())
        assert all(g.record_period(fwd, p, src)[0] for p in range(1, n + 1))
        assert g.record_period(fwd, n + 1, src)[0] is None
    assert g.record_period(spring, 3, plain_spring)[0] == 5          # 02:00 local
    assert g.record_period(spring, 46, plain_spring)[0] == 48        # 23:30 local
    assert g.record_period(autumn, 3, plain_autumn)[0] == 3          # 01:00, first pass
    assert g.record_period(autumn, 5, plain_autumn)[0] == 3          # 01:00, second pass
    assert g.record_period(autumn, 50, plain_autumn)[0] == 48
    # The RECORD day is the change day: a 01:00 the source skipped reads the next period it has.
    p, how = g.record_period(date(2027, 3, 31), 3, date(2024, 3, 31))
    assert p == 3 and "skips 01:00" in how
    # A repeated 01:00 on the record side: the forward day's single pass takes the first.
    assert g.record_period(date(2027, 10, 27), 3, date(2024, 10, 27))[0] == 3
    assert g.record_period(date(2027, 10, 27), 5, date(2024, 10, 27))[0] == 7


def test_the_leap_day_rule_is_the_worlds_own():
    assert g.record_date(date(2028, 2, 29), 2019) == date(2019, 2, 28)
    assert g.record_date(date(2028, 2, 29), 2024) == date(2024, 2, 29)
    assert g.record_date(date(2027, 2, 28), 2024) == date(2024, 2, 28)
    world = _small_world()
    extended = world.extended_by_analogue_years("2028-12-31", seed=SEED)
    record_year = extended.analogue_years[2028]
    stamped = extended.daily["r"]["2028-02-29"]["temperature_mean_c"]
    assert date.fromordinal(int(stamped)) == g.record_date(date(2028, 2, 29), record_year)
    value, prov = _future("2028-02-29", 20, years={2028: 2019},
                          inputs=_inputs({"2019-02-28": _hh(), "2025-06-01": _hh()}))
    assert value is not None and prov["record_date"] == "2019-02-28"


def test_the_fit_window_and_the_analogue_year_are_recorded_in_the_provenance():
    value, prov = _future("2027-06-01", 20)
    assert prov["fit_window"] == (g.FROZEN.fit_from, g.FROZEN.fit_to)
    assert prov["analogue_year"] == 2019 and prov["data_regime"] == "synthetic"
    other = replace(g.FROZEN, fit_from="2023-01-01", fit_to="2024-12-31")
    _, prov2 = _future("2027-06-01", 20, model=other)
    assert prov2["fit_window"] == ("2023-01-01", "2024-12-31")


# ------------------------------------------------------------------- the real record

@pytest.fixture(scope="module")
def real_record():
    try:
        return g.load_record()
    except (g.FutureCarbonUnavailable, FileNotFoundError, OSError) as exc:
        pytest.skip(f"real caches absent on this machine: {exc}")


def test_on_the_real_record_the_model_beats_a_constant_on_held_out_2025(real_record):
    test = g._years(real_record["date"]) == g.HELD_OUT_YEAR
    assert test.sum() > 17_000
    model = g.grade(g.fit(real_record, g.HELD_OUT_TRAIN), real_record, test)
    const = g.grade(g.fit(real_record, g.HELD_OUT_TRAIN, form="constant"), real_record, test)
    assert model["rmse"] < 0.6 * const["rmse"] and model["correlation"] > 0.85, (model, const)
    assert model["days_model_p5_zero"] == 0
    assert abs(model["swing_model"] - model["swing_actual"]) < 0.25 * model["swing_actual"]


def test_the_frozen_model_is_what_the_record_refits_to(real_record):
    assert g.fit(real_record) == g.FROZEN, (
        "the record refits to a different model; rerun `python3 -m sim.grid_carbon_future`, "
        "update FROZEN and the docstring's tables")
