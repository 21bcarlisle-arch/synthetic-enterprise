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
  * `test_sessions_run_when_hes_says_for_as_long_as_efus_says` -- the flat block at fixed hours this
    replaced: sessions whose lengths are not EFUS's quartiles, or whose energy across many days does
    not fall in HES's hours.
  * `test_set_time_homes_repeat_and_the_rest_do_not` -- a habit draw that returns one answer for every
    home, or a set-time home whose session moves, or an irregular home whose session never does.
  * `test_the_meter_carries_it_and_the_boiler_burns_less` -- a term computed but never added to the
    meter, or added to the meter but never to the room's gain, so gas is not displaced.

Sources: docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import random
import statistics

import pytest

import simulation.premise_trace as pt
from simulation.demand_model import heating_degree_days
from simulation.household import HeatingSystem
from tests.simulation.test_premise_trace import make_household


def _day(temp: float, *, weekend: bool = False, away: bool = False, rng=None, habit=None) -> list[float]:
    return pt.supplementary_heating_kwh(
        temp, is_weekend=weekend, is_away=away, rng=rng or random.Random(0), habit=habit
    )


def test_ownership_is_reachable_both_ways_and_only_in_gas_homes():
    gas = make_household()
    owned = [pt.has_supplementary_electric_heating(gas, s) for s in range(4000)]
    assert True in owned and False in owned
    assert sum(owned) / len(owned) == pytest.approx(pt.SUPPLEMENTARY_ELECTRIC_HEATING_SHARE, abs=0.015)
    heat_pump = dataclasses.replace(gas, heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert not any(pt.has_supplementary_electric_heating(heat_pump, s) for s in range(4000))


def test_a_normal_year_carries_hes_s_annual_energy():
    days = [d for d in pt.load_trace_weather("C1") if 2016 <= d.date.year <= 2024]
    rng = random.Random(3)
    total = sum(sum(_day(d.weather.temperature_mean_c, weekend=d.is_weekend, rng=rng)) for d in days)
    years = len({d.date.year for d in days})
    assert total / years == pytest.approx(pt.SUPPLEMENTARY_ELECTRIC_HEATING_KWH_PER_YEAR, rel=1e-6)


def test_the_season_comes_from_the_weather_not_a_calendar():
    def day(temp: float, *, away: bool = False) -> float:
        return sum(_day(temp, away=away))

    assert heating_degree_days(16.0) == 0.0 and day(16.0) == 0.0
    assert day(0.0) > day(8.0) > 0.0
    assert day(0.0, away=True) == 0.0


@pytest.mark.parametrize("weekend", [False, True])
def test_sessions_run_when_hes_says_for_as_long_as_efus_says(weekend):
    rng = random.Random(11)
    hourly = [0.0] * 24
    lengths = []
    for _ in range(6000):
        day = _day(0.0, weekend=weekend, rng=rng)
        lit = [p for p, k in enumerate(day) if k]
        lengths.append(len(lit) * pt.PERIOD_HOURS)
        assert sum(day) == pytest.approx(sum(_day(0.0, weekend=weekend)))  # the energy is the day's, whole
        for p, k in enumerate(day):
            hourly[p // 2] += k
    assert statistics.quantiles(lengths, n=4) == list(pt._EFUS_HEATER_HOURS_QUARTILES[weekend])
    curve = pt._HES_HEATER_HOLIDAY_HOURLY if weekend else pt._HES_HEATER_WORKDAY_HOURLY
    model = [h / sum(hourly) for h in hourly]
    hes = [c / sum(curve) for c in curve]
    # Within 5 points an hour: a session of at least 2.5 h cannot reproduce HES's one-hour features.
    assert max(abs(m - h) for m, h in zip(model, hes)) < 0.05
    # ...and it is HES's day, not the old fixed evening block: the busiest hour is HES's own.
    assert model.index(max(model)) in sorted(range(24), key=lambda h: -hes[h])[:3]


def test_set_time_homes_repeat_and_the_rest_do_not():
    habits = [pt.heater_habit(s) for s in range(4000)]
    assert any(h is None for h in habits) and any(h is not None for h in habits)
    assert sum(h is not None for h in habits) / len(habits) == pytest.approx(pt._SET_TIME_SHARE, abs=0.02)
    habit = next(h for h in habits if h is not None)
    fixed = {tuple(_day(2.0, rng=random.Random(i), habit=habit)) for i in range(20)}
    drawn = {tuple(_day(2.0, rng=random.Random(i))) for i in range(20)}
    assert len(fixed) == 1 and len(drawn) > 10


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
