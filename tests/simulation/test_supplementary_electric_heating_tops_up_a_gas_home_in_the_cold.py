"""About a tenth of gas-heated homes top up with an electric heater in the cold, and it displaces boiler gas.

THE DEFECTS EACH TEST NAMES:

  * `test_ownership_is_reachable_both_ways_and_only_in_gas_homes` -- an ownership draw that returns one
    answer for every home passes every test that asks only what an owner does. Both outcomes are
    asserted reachable FIRST, and a home with no gas boiler never owns one (its electric heating is its
    main system already).
  * `test_a_normal_year_carries_hes_s_annual_energy` -- the HES anchor not reached: energy not tied to
    1,505 kWh in a normal year of heating degree days.
  * `test_the_season_comes_from_the_weather_not_a_calendar` -- a warm day, or an empty house, carrying
    heater energy; a cold day carrying no more than a mild one.
  * `test_the_meter_carries_it_and_the_boiler_burns_less` -- a term computed but never added to the
    meter, or added to the meter but never to the room's gain, so gas is not displaced.

Sources: docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

import simulation.premise_trace as pt
from simulation.demand_model import heating_degree_days
from simulation.household import HeatingSystem
from tests.simulation.test_premise_trace import make_household


def _profile():
    return pt.behaviour_profile_for("P-heater", make_household(), seed=5)


def test_ownership_is_reachable_both_ways_and_only_in_gas_homes():
    gas = make_household()
    owned = [pt.has_supplementary_electric_heating(gas, s) for s in range(4000)]
    assert True in owned and False in owned
    assert sum(owned) / len(owned) == pytest.approx(pt.SUPPLEMENTARY_ELECTRIC_HEATING_SHARE, abs=0.015)
    heat_pump = dataclasses.replace(gas, heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert not any(pt.has_supplementary_electric_heating(heat_pump, s) for s in range(4000))


def test_a_normal_year_carries_hes_s_annual_energy():
    days = [d for d in pt.load_trace_weather("C1") if 2016 <= d.date.year <= 2024]
    profile = _profile()
    total = sum(
        sum(pt.supplementary_heating_kwh(profile, d.weather.temperature_mean_c, is_weekend=d.is_weekend, is_away=False))
        for d in days
    )
    years = len({d.date.year for d in days})
    assert total / years == pytest.approx(pt.SUPPLEMENTARY_ELECTRIC_HEATING_KWH_PER_YEAR, rel=1e-6)


def test_the_season_comes_from_the_weather_not_a_calendar():
    profile = _profile()

    def day(temp: float, *, away: bool = False) -> float:
        return sum(pt.supplementary_heating_kwh(profile, temp, is_weekend=False, is_away=away))

    assert heating_degree_days(16.0) == 0.0 and day(16.0) == 0.0
    assert day(0.0) > day(8.0) > 0.0
    assert day(0.0, away=True) == 0.0
    # One evening block of EFUS's median hours, ending at the household's own bedtime.
    lit = [p for p, k in enumerate(pt.supplementary_heating_kwh(profile, 0.0, is_weekend=False, is_away=False)) if k]
    assert lit[-1] == profile.sleep_period - 1 and len(lit) == 8


def test_the_meter_carries_it_and_the_boiler_burns_less(monkeypatch):
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 21))

    def trace(owns: bool):
        monkeypatch.setattr(pt, "has_supplementary_electric_heating", lambda household, base_seed: owns)
        return pt.generate_premise_trace(
            premise_id="P-heater", household=make_household(), weather=weather, seed=5,
            latitude_deg=pt.DEFAULT_LATITUDE_DEG,
        )

    with_heater, without = trace(True), trace(False)
    heater = sum(sum(d.supplementary_heating_kwh) for d in with_heater.days)
    assert heater > 0.0 and sum(sum(d.supplementary_heating_kwh) for d in without.days) == 0.0
    for day in with_heater.days:
        for p in range(pt.PERIODS_PER_DAY):
            assert day.electricity_kwh[p] == pytest.approx(
                day.behavioural_electricity_kwh[p] + day.ev_kwh[p] + day.boiler_auxiliary_kwh[p]
                + day.supplementary_heating_kwh[p],
                abs=1e-12,
            )
    gas_saved = sum(sum(d.gas_kwh) for d in without.days) - sum(sum(d.gas_kwh) for d in with_heater.days)
    # The heat displaces boiler heat, so gas falls, and by no more than the heat put in over the
    # boiler's efficiency (the room can also run warmer, so not all of it is displaced).
    assert 0.0 < gas_saved < heater / 0.7
