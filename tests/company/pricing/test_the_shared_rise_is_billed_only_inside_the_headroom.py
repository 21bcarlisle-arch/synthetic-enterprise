"""C34's price half: writer 7 bills the retention rise on the fix only inside the headroom under the
published default, and the desk prices it at the notice. Inputs are §4's B11-scale cases
(`docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §4e), not
estimates of the world.

Mutations observed on 2026-10-24, each applied in place and reverted:

  * the headroom check removed from `bill_the_shared_rise`        -> 1 red, the over-the-headroom
    test. I predicted the partition too, and it stays green: through the desk, `price_retention_rise`
    already refuses above the headroom, so the writer's check is a second leg of the same guard,
    and only a rise handed in directly reaches it.
  * the unknown-headroom refusal removed (falls through to billing) -> 1 red, the unknown test
  * `rise_at_notice` returns the rise whatever C34 decided           -> 1 red, the floor test
"""
from __future__ import annotations

import dataclasses

import pytest

from company.crm.next_best_action import RenewalTerms
from company.crm.renewal_advice_desk import RenewalAdviceDesk, monthly_hazard
from company.policy.decision_policy import CURRENT_POLICY
from company.pricing.renewal_rate_chain import bill_the_shared_rise

ON = dataclasses.replace(CURRENT_POLICY, name="shared_rise_on",
                         next_best_action_decides_at_renewal=True,
                         next_best_action_shares_by_retention_rise=True,
                         renewal_rate_bills_the_shared_rise=True)
MWH, OFFER = 2.7, 200.0


def terms(headroom):
    return RenewalTerms(OFFER, None if headroom is None else OFFER + headroom * 12.0 / MWH, MWH)


def notice(margin, monthly_hz, headroom, policy=ON):
    """The desk's rise at one notice, and what writer 7 bills for it."""
    desk = RenewalAdviceDesk(policy)
    # The desk turns an annual churn belief into the monthly hazard; invert it so the case is exact.
    belief = 1.0 - (1.0 - monthly_hz) ** 12
    assert monthly_hazard(belief) == pytest.approx(monthly_hz)
    t = terms(headroom)
    desk.observe_roll(account_id="a", term_start="2020-04-01", fuel="electricity",
                      monthly_margin_gbp=margin, renewal_churn_belief=belief, renewal=t)
    rise, why = desk.rise_at_notice(account_id="a", term_start="2020-04-01")
    rate, billed_why = bill_the_shared_rise(
        unit_rate_gbp_per_mwh=OFFER, rise_gbp_per_month=None if rise is None else rise.rise_gbp_per_month,
        annual_mwh=MWH, headroom_gbp_per_month=t.headroom_gbp_per_month())
    return rise, why, rate, billed_why


def test_the_partition_share_branch_can_be_taken_and_no_headroom_refuses():
    """One control over the whole partition: the share branch is reachable at B11-scale inputs, and
    the same case is refused with no headroom, with unknown headroom, and left alone with C34 off."""
    shared = notice(5.0, 0.03, 4.0)
    no_room = notice(5.0, 0.03, 0.0)
    unknown = notice(5.0, 0.03, None)
    c34_off = notice(5.0, 0.03, 4.0, policy=CURRENT_POLICY)
    assert shared[2] > OFFER and shared[3].startswith("shared")
    assert no_room[2] == OFFER and no_room[0] is None
    assert unknown[2] == OFFER and unknown[0] is None
    assert c34_off[2] == OFFER and c34_off[0] is None


def test_the_billed_rise_is_the_rise_over_the_accounts_own_volume_and_sits_under_the_default():
    rise, _, rate, _ = notice(5.0, 0.03, 4.0)
    assert rate == pytest.approx(OFFER + rise.rise_gbp_per_month * 12.0 / MWH)
    assert rate <= terms(4.0).published_default_gbp_per_mwh


def test_a_rise_above_the_headroom_is_refused_and_names_both_numbers():
    rate, why = bill_the_shared_rise(unit_rate_gbp_per_mwh=OFFER, rise_gbp_per_month=2.5,
                                     annual_mwh=MWH, headroom_gbp_per_month=1.35)
    assert rate == OFFER
    assert "2.50" in why and "1.35" in why


def test_unknown_headroom_or_volume_refuses_rather_than_reading_zero():
    for headroom, mwh in ((None, MWH), (4.0, None), (4.0, 0.0)):
        rate, why = bill_the_shared_rise(unit_rate_gbp_per_mwh=OFFER, rise_gbp_per_month=2.0,
                                         annual_mwh=mwh, headroom_gbp_per_month=headroom)
        assert rate == OFFER and "unknown" in why


def test_where_no_rise_brings_our_side_to_zero_the_floor_holds_and_nothing_is_billed():
    # §4e table: margin 30, hazard 3%, effect (2, 0.1pt) -- every pound of rise costs more in staying
    # than it earns, so C34 still refuses, with room to spare under the default.
    rise, why, rate, billed_why = notice(30.0, 0.03, 12.38)
    assert rise is None and rate == OFFER
    assert "retention rise" in why and billed_why.startswith("no action")


def test_the_run_bills_the_rise_before_the_world_is_asked_at_the_roll():
    """The household must answer the raised price: the bill precedes the roll's arguments."""
    import ast
    import inspect

    import simulation.run_phase2b as run
    tree = ast.parse(inspect.getsource(run))
    billed = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Name) and n.func.id == "bill_the_shared_rise"]
    asked = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "_roll_kwargs" for t in n.targets)]
    assert len(billed) == 1 and len(asked) == 1
    assert billed[0] < asked[0]


def test_a_billed_rise_with_nothing_priced_to_bill_is_refused_with_its_reason():
    import simulation.run_phase2b as run
    run._refuse_a_billed_rise_with_no_price(ON)
    run._refuse_a_billed_rise_with_no_price(CURRENT_POLICY)
    with pytest.raises(ValueError, match="next_best_action_shares_by_retention_rise"):
        run._refuse_a_billed_rise_with_no_price(
            dataclasses.replace(CURRENT_POLICY, renewal_rate_bills_the_shared_rise=True))


def test_the_billed_rise_is_off_on_every_standing_policy():
    from company.policy import decision_policy as dp
    standing = [v for v in vars(dp).values() if isinstance(v, dp.DecisionPolicy)]
    assert len(standing) >= 3
    assert not any(p.renewal_rate_bills_the_shared_rise for p in standing)
