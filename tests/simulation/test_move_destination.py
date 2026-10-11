"""Where a household that moves with us goes, and the home it finds there."""
from __future__ import annotations

import dataclasses
import datetime as dt

from simulation.household import Household
from simulation.household_demand import HouseholdDemandRegister
from simulation.move_destination import (
    destination_region,
    draw_destination,
    household_at_destination,
    in_region_share,
    ons_region_of,
    shape_across_a_move,
)

_ORIGIN = {"customer_id": "SYN-2016-002", "segment": "resi",
           "location": {"lat": 52.2379, "lon": -0.9821, "region": "East Midlands"}}


def test_both_region_branches_are_reached_and_the_share_is_the_registers():
    """Defect: a destination that always stays (or always leaves) its region, whatever the toggle.
    Both branches are shown reachable over a population of ids before the share is checked."""
    stays = [destination_region(f"PREM-{i:04d}", "East Midlands", 7)[1] for i in range(2000)]
    assert any(stays) and not all(stays)
    assert abs(sum(stays) / len(stays) - in_region_share()) < 0.04
    assert in_region_share() == 0.519
    moved = [destination_region(f"PREM-{i:04d}", "East Midlands", 7) for i in range(400)]
    assert all(r != "East Midlands" for r, same in moved if not same)


def test_a_roster_city_is_placed_in_its_ons_region():
    """Defect: a roster record's city read as an ONS region, so its destination could never stay."""
    assert ons_region_of({"location": {"region": "Glasgow"}}) == "Scotland"
    assert ons_region_of(_ORIGIN) == "East Midlands"


def test_the_destination_is_a_drawn_dwelling_and_the_household_keeps_its_own_ev():
    """Defect: the new home's demand carried from the old one (the "origin's twin"), or the
    household's own EV and stress left behind at the old address."""
    dest = draw_destination("PREM-abc123", _ORIGIN, dt.date(2020, 5, 1), 7)
    assert dest is not None and dest.premise.premise_id == "PREM-abc123"
    assert draw_destination("PREM-abc123", _ORIGIN, dt.date(2020, 5, 1), 7) == dest
    mover = dataclasses.replace(dest.premise.household, customer_id="SYN-2016-002",
                                has_ev=True, ev_charger_kw=7.0)
    at_new = household_at_destination(mover, dest)
    assert at_new.customer_id == "SYN-2016-002" and at_new.has_ev and at_new.ev_charger_kw == 7.0
    assert at_new.epc_rating == dest.premise.household.epc_rating
    assert at_new.property_type == dest.premise.household.property_type


def test_the_register_serves_the_new_home_from_the_move_date_only():
    """Defect: a relocation that rewrites the household's past, or never takes effect."""
    reg = HouseholdDemandRegister([{"customer_id": "C1", "segment": "resi", "eac_kwh": 3000,
                                    "home_type": "suburban_semi", "epc_rating": "D",
                                    "bedrooms": 3, "commodity": "electricity",
                                    "location": {"lat": 51.5, "lon": -0.1, "region": "London"}}])
    before = reg.household_at_date("C1", "2019-01-01")
    assert isinstance(before, Household)
    new = dataclasses.replace(before, epc_rating="B" if before.epc_rating != "B" else "C")
    reg.relocate("C1", "2020-06-01", new)
    assert reg.household_at_date("C1", "2020-05-31").epc_rating == before.epc_rating
    assert reg.household_at_date("C1", "2020-06-01").epc_rating == new.epc_rating


def test_the_term_across_a_move_settles_each_home_on_its_own_side_of_the_date():
    """Defect: the carried term settled on one home throughout."""
    fn = shape_across_a_move(lambda d: [1.0], lambda d: [2.0], "2020-06-01")
    assert fn("2020-05-31") == [1.0] and fn("2020-06-01") == [2.0]
