"""One home draws one life across its two fuels.

`build_household_register` aliases a gas leg to its electricity point's Household; the life-event
stream must follow the same alias. Before this, `HouseholdDemandRegister` drew events per supply-point
id, so PROS-2019-0208g installed a heat pump its electricity never did: its gas fell to the 0.12
residual and no meter carried the heat (docs/staging/SEAT_FINDING_A_HEAT_PUMP_HOMES_GAS_SETTLES_
FLAT_FOREVER_AND_ITS_HEAT_REACHES_NO_METER_2026-11-27.md).

The control is keyed to the property -- every leg sharing a Household shares its events -- over the
real roster, and asserts both branches can be taken: aliased legs exist, and an orphaned leg keeps a
life of its own. Mutation: draw per supply-point id again (the pre-fix loop) and the first test reds
on the 19 heat-pump legs and every other dual-fuel home whose draws diverge.
"""
from __future__ import annotations

from simulation.household import household_of
from simulation.household_demand import HouseholdDemandRegister
from simulation.live_population import live_drawn_households
from simulation.run_phase2b import CUSTOMERS


def test_every_aliased_gas_leg_lives_its_primarys_life():
    reg = HouseholdDemandRegister(CUSTOMERS, drawn_households=live_drawn_households())
    aliased = [
        cid for cid in reg.all_customer_ids()
        if household_of(cid) != cid
        and reg._households[cid] is reg._households.get(household_of(cid))
    ]
    assert len(aliased) > 100, f"only {len(aliased)} aliased gas legs: the roster lost its dual fuel"
    split = [cid for cid in aliased if reg._events[cid] != reg._events[household_of(cid)]]
    assert not split, f"{len(split)} gas legs draw a life apart from their home's, e.g. {split[:5]}"
    # The partition is not vacuous: some aliased home lives at least one event.
    assert any(reg._events[cid] for cid in aliased)


def test_an_orphaned_gas_leg_keeps_its_own_life():
    leg = next(c for c in CUSTOMERS if household_of(c["customer_id"]) != c["customer_id"])
    orphan = dict(leg)  # a gas leg whose electricity point is not in this book
    reg = HouseholdDemandRegister([orphan], drawn_households=live_drawn_households())
    cid = orphan["customer_id"]
    assert cid in reg._events and reg._households[cid] is not None
