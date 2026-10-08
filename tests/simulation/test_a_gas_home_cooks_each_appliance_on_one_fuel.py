"""A gas home cooked every meal twice: on the electric oven and hob, AND on cooking gas.

The defect this names: `owned_stock` drew no cooking fuel, so every gas-DHW home ran the catalogue's
electric oven and hob and also burned the full cooking gas. Against SERL 2022 that was most of a
0.32 kWh/h evening excess. EFUS 2017 Fig 4.5 + EHS 2017 AT3.5 give the split among gas homes.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter

import pytest

from simulation import fabric_physics as fp
from simulation import premise_trace as pt
from simulation.household import HeatingSystem
from tests.simulation.test_premise_trace import make_household

N = 6000
GAS_COOKED = frozenset({"oven", "hob"})


def _trace(household, cooked_on_gas):
    weather = pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 21))
    return pt.generate_premise_trace(
        premise_id="P-cook", household=household, weather=weather, seed=3,
        latitude_deg=fp.latitude_for_weather_site("C1"), cooked_on_gas=cooked_on_gas,
    )


def _kwh(trace, field):
    return sum(sum(getattr(d, field)) for d in trace.days)


def test_every_combination_is_drawn_at_the_share_the_sources_give():
    """The shares are recomputed here from the published figures, not read back from the module."""
    efus = {frozenset(): 0.37 - 0.140, frozenset({"hob"}): 0.33, GAS_COOKED: 0.20}
    expected = {k: v / sum(efus.values()) for k, v in efus.items()}
    drawn = Counter(pt.gas_cooked(seed) for seed in range(N))
    assert set(drawn) == set(expected)
    for combination, share in expected.items():
        assert drawn[combination] / N == pytest.approx(share, abs=0.02), combination


def test_a_gas_cooked_appliance_leaves_the_electricity_and_an_electric_cook_burns_no_gas():
    household = make_household()
    assert household.is_gas_heated
    electric, gas = _trace(household, frozenset()), _trace(household, GAS_COOKED)
    assert _kwh(electric, "cooking_fuel_kwh") == 0.0
    assert _kwh(gas, "cooking_fuel_kwh") > 0.0
    assert _kwh(gas, "electricity_kwh") < _kwh(electric, "electricity_kwh")


def test_the_population_burns_the_cooking_gas_desnz_gives_a_gas_home():
    """The DESNZ share is a mean over all gas homes, so dividing the gas among the gas cooks keeps it."""
    mean = sum(
        share * pt.gas_cooking_daily_kwh(3, combination)
        for combination, share in pt._GAS_HOME_COOKING_FUEL.items()
    )
    assert mean == pytest.approx(pt.cooking_daily_kwh(3), rel=1e-12)


def test_an_off_gas_home_cooks_electrically_whatever_it_is_handed():
    household = make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    assert not household.is_gas_heated
    handed, drawn = _trace(household, GAS_COOKED), _trace(household, None)
    assert _kwh(handed, "electricity_kwh") == _kwh(drawn, "electricity_kwh")
    assert _kwh(handed, "cooking_fuel_kwh") == 0.0
