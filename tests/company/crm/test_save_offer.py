"""The save desk's rules (director, 2026-10-08). One control per way it can mislead:

  1. a vulnerable household is offered a higher save price than a household in the same position
     that is not vulnerable;
  2. the save varies by something other than the two positions it may vary by;
  3. a save is made with no size named (the size is a GAP and must not be defaulted), or at a zero
     cut that is really never offering.
"""
from __future__ import annotations

import inspect

import pytest

from company.crm import save_offer as so

POSITIONS = [(route, months) for route in (None, "price_comparison", "direct", "home_move")
             for months in (None, 0, 6, 36)]


def test_a_vulnerable_household_is_never_offered_less_than_its_twin():
    """Defect 1. Over every position, rate and share, the vulnerable twin's save price is at or below
    the plain twin's. The comparison must be reachable: both twins are priced, below the renewal."""
    for route, months in POSITIONS:
        for rate in (120.0, 265.4, 298.7):
            for share in (0.01, 0.04, 0.15):
                plain = so.save_offer_rate(rate, share, acquisition_route=route,
                                           months_on_default=months, vulnerable=False)
                vuln = so.save_offer_rate(rate, share, acquisition_route=route,
                                          months_on_default=months, vulnerable=True)
                assert vuln <= plain < rate, (route, months, rate, share)


def test_the_save_varies_only_by_route_and_time_on_default():
    """Defect 2. The function that sizes the cut may read the policy share and the two permitted
    positions, and nothing else -- not the household's vulnerability, payment method or bill."""
    params = list(inspect.signature(so._cut_share_for).parameters)
    assert params == ["cut_share", *so.SAVE_MAY_VARY_BY]


def test_no_size_offers_nothing_and_a_zero_cut_is_refused():
    """Defect 3. None is the standing policy's size and offers nothing; a zero or full cut is
    refused by name; a real share yields a Fixed Retention Tariff below the renewal."""
    notice = {"supply_point_id": "SP1"}
    assert so.save_offer_on_invitation(notice, 200.0, None) is None
    assert so.save_offer_on_invitation(notice, None, 0.04) is None
    for bad in (0.0, 1.0):
        with pytest.raises(ValueError, match="never offering"):
            so.save_offer_on_invitation(notice, 200.0, bad)
    offer = so.save_offer_on_invitation(notice, 200.0, 0.04)
    assert offer.tariff == "fixed_retention_tariff"
    assert offer.save_unit_rate == pytest.approx(192.0)


def test_no_standing_policy_names_a_save_size():
    """The size is a GAP (q4_save_offer_cost_share_of_annual_bill). A standing policy that set one
    would be a picked number reaching the run."""
    from company.policy import decision_policy as dp

    standing = [v for v in vars(dp).values() if isinstance(v, dp.DecisionPolicy)]
    assert standing and all(p.save_offer_cut_share is None for p in standing)
