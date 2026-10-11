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


# ── the standing price match (2026-10-10) ───────────────────────────────────────────────────────



def test_a_price_match_IS_OFFERED_where_the_market_beats_the_renewal_above_our_cost():
    """Fires on: a rule that never offers -- every refusal below would pass and no household would
    ever be saved in the run, which is the state this capability exists to end."""
    # default 250, gap 8% -> market best 230; floor 200; renewal 245 -> offered at 230.
    assert so.price_match_save_rate(245.0, 250.0, 0.08, 200.0) == 230.0


def test_the_match_is_never_below_our_own_cost_floor():
    """Fires on: a save priced below cost -- a guaranteed loss on every saved term."""
    assert so.price_match_save_rate(245.0, 250.0, 0.20, 215.0) == 215.0


def test_no_offer_where_the_market_had_nothing_cheaper_or_the_match_does_not_beat_the_renewal():
    """Fires on: a 'save' at or above the renewal price, or one invented through 2022 when the
    published gap was negative and no deal undercut the default."""
    assert so.price_match_save_rate(245.0, 250.0, -0.05, 200.0) is None
    assert so.price_match_save_rate(245.0, 250.0, 0.0, 200.0) is None
    assert so.price_match_save_rate(225.0, 250.0, 0.08, 200.0) is None   # 230 does not beat 225
    assert so.price_match_save_rate(245.0, 250.0, 0.08, 250.0) is None   # floor 250 does not beat 245


def test_a_missing_published_or_company_input_offers_nothing_rather_than_guessing():
    """Fires on: a None input read as zero -- a gap of 0 or a floor of 0 would invent a price."""
    for args in ((245.0, None, 0.08, 200.0), (245.0, 250.0, None, 200.0),
                 (245.0, 250.0, 0.08, None), (None, 250.0, 0.08, 200.0)):
        assert so.price_match_save_rate(*args) is None


def test_the_door_sizes_by_price_match_only_when_no_experiment_names_a_cut():
    """Fires on: the standing price match overriding an experiment's named cut, which would
    silently change every graded save arm."""
    notice = {"supply_point_id": "P1"}
    by_cut = so.save_offer_on_invitation(notice, 245.0, 0.04, price_match_rate=230.0)
    assert by_cut.save_unit_rate == 245.0 * 0.96
    by_match = so.save_offer_on_invitation(notice, 245.0, None, price_match_rate=230.0)
    assert by_match.save_unit_rate == 230.0
    assert so.save_offer_on_invitation(notice, 245.0, None, price_match_rate=None) is None


def test_no_save_when_the_market_had_nothing_cheaper_even_with_the_renewal_above_the_cap():
    """Fires on: dropping the no-cheaper-deal guard. A renewal ABOVE the default (2022's fixes)
    with a negative gap would otherwise be 'matched' to a price above the market's own default --
    a fixed save offered when suppliers had withdrawn fixed deals and nothing undercut the cap."""
    assert so.price_match_save_rate(300.0, 250.0, -0.05, 200.0) is None
