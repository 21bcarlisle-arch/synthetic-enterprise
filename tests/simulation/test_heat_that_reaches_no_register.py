"""W2_20 step 2: the gas supply is drawn first, the heating system given it, and heat no supplier
meters reaches no register.

THE DEFECTS THESE NAME:

  * `test_a_home_with_no_gas_meter_never_draws_a_mains_gas_boiler`: heating drawn independently
    of the supply put 15% of homes on a gas boiler with no gas meter. EHS 2017-18 AT3.5 note 3
    measures that combination as 0. The gas-fired homes with no meter burn LPG.
  * `test_unmetered_heat_reaches_neither_register`: an oil, LPG, solid-fuel or communal home's
    heat billed on electricity at 1:1, which is what the trace did for every system that was not
    a gas boiler.
  * `test_the_gas_account_reads_the_supply_flag`: `DrawnPremise.commodity` read only the burner,
    so a drawn supply of False could still hold a gas account.

The partition is asserted before anything else: every one of the three heat routes (gas register,
electricity register, no register) must be drawn, or the controls below pass on an empty case.

Measured against the pre-registration in
`docs/staging/SEAT_FINDING_W2_20_A_SIXTH_OF_DRAWN_GAS_BOILERS_HAVE_NO_GAS_SUPPLY_2026-10-07.md`.
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pytest

from simulation import premise_population as pp
from simulation import premise_trace as pt
from simulation.household import HeatingSystem

N = 1500
SEED = 42
AS_OF = dt.date(2023, 6, 1)
_GAS = (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)


@pytest.fixture(scope="module")
def stock():
    return [pp.draw_premise_from_joint(f"PSTK-W220-{i:05d}", base_seed=SEED, as_of=AS_OF)
            for i in range(N)]


def _route(household) -> str:
    if household.is_gas_heated:
        return "gas"
    return "none" if household.heat_reaches_no_register else "electricity"


def test_all_three_heat_routes_are_drawn(stock):
    routes = {_route(p.household) for p in stock}
    assert routes == {"gas", "electricity", "none"}, (
        f"the drawn stock reaches only {routes}, so a control over the missing route is vacuous")
    assert any(p.household.has_mains_gas_supply is False for p in stock)


def test_a_home_with_no_gas_meter_never_draws_a_mains_gas_boiler(stock):
    for supply in (True, False):
        weights = pp.heating_weights_given_supply(supply)
        assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert not any(pp.heating_weights_given_supply(False).get(s, 0.0) for s in _GAS)
    wrong = [p.premise_id for p in stock
             if p.household.has_mains_gas_supply is False and p.household.heating_system in _GAS]
    assert not wrong, f"gas boilers with no gas meter: {wrong[:5]} (EHS AT3.5 note 3 measures 0)"


def test_the_gas_account_reads_the_supply_flag(stock):
    gas_home = next(p for p in stock if p.household.heating_system in _GAS)
    assert gas_home.commodity == "gas"
    cut = dataclasses.replace(
        gas_home, household=dataclasses.replace(gas_home.household, has_mains_gas_supply=False))
    assert cut.commodity == "electricity", "a home with no gas supply held a gas account"
    unknown = dataclasses.replace(
        gas_home, household=dataclasses.replace(gas_home.household, has_mains_gas_supply=None))
    assert unknown.commodity == "gas", "a supply of None must fall back to the burner"


@pytest.fixture(scope="module")
def january():
    return pt.load_trace_weather("C1", start=dt.date(2022, 1, 1), end=dt.date(2022, 1, 31))


@pytest.fixture(scope="module")
def traces(stock, january):
    base = next(p.household for p in stock if p.household.heating_system in _GAS)
    out = {}
    for system in (HeatingSystem.NON_MAINS_FUEL_BOILER, HeatingSystem.COMMUNAL_HEAT,
                   HeatingSystem.ELECTRIC_DIRECT):
        household = dataclasses.replace(base, heating_system=system, has_mains_gas_supply=False)
        out[system] = pt.generate_premise_trace(
            premise_id="P-W220", household=household, weather=january, seed=SEED,
            latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    return out


@pytest.mark.parametrize("system", [HeatingSystem.NON_MAINS_FUEL_BOILER, HeatingSystem.COMMUNAL_HEAT])
def test_unmetered_heat_reaches_neither_register(traces, system):
    trace = traces[system]
    assert trace.heating_commodity == "none"
    delivered = sum(sum(d.heat_delivered_kwh) for d in trace.days)
    twin = sum(sum(d.heat_delivered_kwh) for d in traces[HeatingSystem.ELECTRIC_DIRECT].days)
    assert delivered > 0.5 * twin, (
        f"the house got {delivered:.0f} kWh of heat against its electric twin's {twin:.0f}: "
        "keeping heat off the registers must not stop heating the house")
    assert sum(d.gas_total_kwh for d in trace.days) == 0.0
    electric = sum(d.electricity_total_kwh for d in traces[HeatingSystem.ELECTRIC_DIRECT].days)
    unmetered = sum(d.electricity_total_kwh for d in trace.days)
    assert unmetered < 0.5 * electric, (
        f"{system.value} put {unmetered:.0f} kWh on electricity against an electric twin's "
        f"{electric:.0f}: its heat is on the electricity register")
