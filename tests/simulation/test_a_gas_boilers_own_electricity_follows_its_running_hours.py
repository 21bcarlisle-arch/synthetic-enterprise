"""A gas-heated home's meter carries its boiler's own electricity, and that load follows the boiler.

THE DEFECTS EACH TEST NAMES:

  * `test_both_pump_kinds_are_reachable_and_the_band_decides_which` -- a pump-kind assignment that
    returns ONE kind for every boiler passes every test that only asks what the other leg does. The
    whole partition is asserted reachable first.
  * `test_the_meter_carries_the_term_exactly` -- a term computed and exposed but never added to
    `electricity_kwh` (or added twice) is invisible to everything downstream.
  * `test_the_season_comes_from_the_boilers_running_hours_not_a_calendar` -- the term's season must
    be an OUTPUT of the weather. A day with no space heat and no hot water carries standby only; a
    cold day carries more than a warm one.
  * `test_a_home_without_a_gas_boiler_carries_none` -- a heat pump's circulation is already inside
    its own electricity; adding a boiler term to it double-counts.

Sources for every constant: docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

import simulation.premise_trace as pt
from simulation.household import BoilerAge, HeatingSystem
from tests.simulation.test_premise_trace import make_household


@pytest.fixture(scope="module")
def winter_and_summer():
    jan = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 21))
    jul = pt.load_trace_weather("C1", start=dt.date(2022, 7, 1), end=dt.date(2022, 7, 21))
    return jan, jul


def _trace(weather, household=None, seed=42):
    return pt.generate_premise_trace(
        premise_id="P-aux",
        household=household or make_household(),
        weather=weather,
        seed=seed,
        latitude_deg=pt.DEFAULT_LATITUDE_DEG,
    )


def test_both_pump_kinds_are_reachable_and_the_band_decides_which():
    gas = make_household()
    kinds = {
        pt.boiler_pump_kw(dataclasses.replace(gas, boiler_age=age), seed, dt.date(2022, 1, 1))
        for age in (BoilerAge.NEW, BoilerAge.MID, BoilerAge.OLD)
        for seed in range(40)
    }
    assert kinds == {pt.FIXED_SPEED_PUMP_KW, pt.VARIABLE_SPEED_PUMP_KW}
    # An OLD boiler in 2022 was installed by 2010, before the Ecodesign date: always fixed-speed.
    old = dataclasses.replace(gas, boiler_age=BoilerAge.OLD)
    assert {pt.boiler_pump_kw(old, s, dt.date(2022, 1, 1)) for s in range(40)} == {pt.FIXED_SPEED_PUMP_KW}
    # A MID boiler in 2016 was installed 2004-2011: also always fixed-speed.
    mid = dataclasses.replace(gas, boiler_age=BoilerAge.MID)
    assert {pt.boiler_pump_kw(mid, s, dt.date(2016, 1, 1)) for s in range(40)} == {pt.FIXED_SPEED_PUMP_KW}
    with pytest.raises(ValueError, match="no install window"):
        pt.boiler_pump_kw(dataclasses.replace(gas, boiler_age=BoilerAge.NA), 1, dt.date(2022, 1, 1))


def test_the_meter_carries_the_term_exactly(winter_and_summer):
    jan, _ = winter_and_summer
    trace = _trace(jan)
    assert sum(sum(d.boiler_auxiliary_kwh) for d in trace.days) > 0.0
    for day in trace.days:
        for p in range(pt.PERIODS_PER_DAY):
            assert day.electricity_kwh[p] == pytest.approx(
                day.behavioural_electricity_kwh[p] + day.ev_kwh[p] + day.boiler_auxiliary_kwh[p]
                + day.supplementary_heating_kwh[p],
                abs=1e-12,
            )


def test_the_season_comes_from_the_boilers_running_hours_not_a_calendar(winter_and_summer):
    jan, jul = winter_and_summer
    winter = _trace(jan)
    summer = _trace(jul)

    def mean(trace):
        return sum(sum(d.boiler_auxiliary_kwh) for d in trace.days) / len(trace.days)

    assert mean(winter) > 2.0 * mean(summer)

    standby_day = pt.BOILER_STANDBY_KW * 24.0
    idle = pt.boiler_auxiliary_kwh(
        pump_kw=pt.FIXED_SPEED_PUMP_KW,
        rated_output_kw=12.0,
        space_heat_kwh=[0.0] * pt.PERIODS_PER_DAY,
        space_duty_fraction=[0.0] * pt.PERIODS_PER_DAY,
        dhw_heat_kwh=[0.0] * pt.PERIODS_PER_DAY,
    )
    assert sum(idle) == pytest.approx(standby_day)
    # A whole period firing at full output: pump plus full-load fan, no standby.
    firing = pt.boiler_auxiliary_kwh(
        pump_kw=pt.FIXED_SPEED_PUMP_KW,
        rated_output_kw=12.0,
        space_heat_kwh=[6.0],
        space_duty_fraction=[1.0],
        dhw_heat_kwh=[0.0],
    )
    assert firing[0] == pytest.approx(
        (pt.FIXED_SPEED_PUMP_KW + pt.BOILER_ELECTRICAL_FULL_LOAD_KW) * pt.PERIOD_HOURS
    )
    # The same hours at the Ecodesign part-load point draw the part-load fan.
    part = pt.boiler_auxiliary_kwh(
        pump_kw=0.0,
        rated_output_kw=12.0,
        space_heat_kwh=[12.0 * 0.30 * 0.5],
        space_duty_fraction=[1.0],
        dhw_heat_kwh=[0.0],
    )
    assert part[0] == pytest.approx(pt.BOILER_ELECTRICAL_PART_LOAD_KW * pt.PERIOD_HOURS)


def test_a_home_without_a_gas_boiler_carries_none(winter_and_summer):
    jan, _ = winter_and_summer
    heat_pump = make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    heat_pump = dataclasses.replace(heat_pump, boiler_age=BoilerAge.NA)
    trace = _trace(jan[:7], household=heat_pump)
    assert all(v == 0.0 for d in trace.days for v in d.boiler_auxiliary_kwh)
