"""The defect: a drawn founder became a GAS account on a home heated by electricity.

`_drawn_founder_pairs` took the account's fuel from the draw record's `commodity` while the
premise -- the house the world built, whose heating system the physics runs -- said
electricity. The campaign path already refused a gas leg without a gas meter; the founder path
did not. At the live seed three storage- or direct-electric homes held ~9.5 MWh gas contracts
their physics never burned, and settlement billed the AQ on the population split.
"""
from __future__ import annotations

import pytest

import simulation.live_population as lp
from simulation.population_draw import iter_acquisition_events

SEED = lp._DEFAULT_BASE_SEED
_GAS_HEATING = {"gas_boiler_combi", "gas_boiler_system", "gas_boiler_regular"}


@pytest.fixture(scope="module")
def founders():
    return lp._drawn_founder_pairs(SEED)


def _gas_on_non_gas_homes(wanted: int, **weights) -> int:
    seen = disagree = 0
    for customer in iter_acquisition_events(
        SEED + lp._FOUNDER_SEED_OFFSET,
        start_year=lp.FOUNDER_ACQUISITION_YEAR,
        end_year=lp.FOUNDER_ACQUISITION_YEAR,
        acquisitions_per_year_lambda=float(wanted) * lp._FOUNDER_DRAW_HEADROOM,
        draw_region=True,
        assign_cohorts=True,
        **weights,
    ):
        premise = getattr(customer, "premise", None)
        if customer.to_customer_dict().get("commodity") == "gas" and premise is not None:
            disagree += premise.commodity != "gas"
        seen += 1
        if seen >= wanted * 2:
            break
    return disagree


def test_the_disagreement_is_closed_at_the_draw_and_a_forced_fuel_still_produces_it(founders):
    """Reachability first, and since 2026-10-17 the case lives in the DRAW, not the founder loop.

    The account now takes its home's fuel (`population_draw.fuel_arrangement`), so the default
    draw cannot put gas on a home with no gas meter. A caller that forces the fuel by explicit
    weights still can, and that is the control showing the zero below is not vacuous.
    """
    wanted = len(founders)
    assert _gas_on_non_gas_homes(wanted, commodity_weights={"gas": 1.0}) > 0
    assert _gas_on_non_gas_homes(wanted) == 0


def test_every_drawn_gas_founder_sits_on_a_gas_heated_home(founders):
    gas = [(r, p) for r, p in founders if r.get("commodity") == "gas"]
    assert gas, "the founder draw produced no gas account at all -- the property below is vacuous"
    wrong = []
    for record, premise in gas:
        if premise is None:
            continue
        heating = getattr(premise.household.heating_system, "value", premise.household.heating_system)
        if premise.commodity != "gas" or heating not in _GAS_HEATING:
            wrong.append((record["customer_id"], premise.commodity, heating))
    assert not wrong, (
        f"gas accounts on homes the world heats with something else: {wrong}. The contract "
        "must follow what is plumbed in; the AQ settles gas the physics never burns")
