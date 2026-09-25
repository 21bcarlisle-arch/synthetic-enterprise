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


def test_the_disagreement_the_guard_refuses_really_occurs_in_the_founder_draw(founders):
    """Reachability first: a guard over a case the draw never produces passes vacuously."""
    wanted = len(founders)
    seen = disagree = 0
    for customer in iter_acquisition_events(
        SEED + lp._FOUNDER_SEED_OFFSET,
        start_year=lp.FOUNDER_ACQUISITION_YEAR,
        end_year=lp.FOUNDER_ACQUISITION_YEAR,
        acquisitions_per_year_lambda=float(wanted) * lp._FOUNDER_DRAW_HEADROOM,
        draw_region=True,
        assign_cohorts=True,
    ):
        premise = getattr(customer, "premise", None)
        if customer.to_customer_dict().get("commodity") == "gas" and premise is not None:
            disagree += premise.commodity != "gas"
        seen += 1
        if seen >= wanted * 2:
            break
    assert disagree > 0, (
        "no founder candidate is drawn as a gas account on a non-gas premise, so the guard in "
        "_drawn_founder_pairs is unreachable and every test below passes for nothing")


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
