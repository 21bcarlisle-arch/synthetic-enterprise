"""C34 at the renewal roll: the on branch decides, per household, on the company's own belief.

Defects each control names:
- a desk whose floor refuses EVERYTHING passes every refusal test, so the partition control asserts
  an advised row exists before it asserts any refusal;
- a riding leg that never joins its roll leaves per household deciding on electricity alone, the
  instrument defect 608c0d0fa fixed in the probe;
- a standing policy that turns the caller on changes every published run;
- a margin read as the rate less the wholesale forward still carries network, policy and capital,
  which put 11% of the r4 rows over the floor (§6.1, amended 2026-10-20);
- a leg whose term records no locked costs must be counted, not priced on a guess, and a desk
  that skipped EVERY leg would pass that leg alone.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

from company.crm.renewal_advice_desk import (
    STATED_ADVICE_EFFECTS,
    monthly_hazard,
    standing_charge_opex_per_year,
    term_contribution_per_year,
)
from company.interfaces.renewal_advice import RenewalAdviceDesk, term_contribution_per_month
from company.policy import decision_policy as dp
from company.policy.decision_policy import CURRENT_POLICY
from company.pricing.renewal_desk import TARGET_MARGIN_GBP_PER_MWH, pre_margin_unit_rate
from saas.cost_to_serve import FIXED_OVERHEAD_GBP_PER_YEAR
from simulation.policy_costs import (
    get_electricity_network_cost_per_mwh,
    get_electricity_policy_cost_per_mwh,
)

START = "2019-01-01"


def _desk(policy=CURRENT_POLICY, book=((5, 0.1), (15, 0.1), (60, 0.3), (100, 0.5))):
    desk = RenewalAdviceDesk(policy)
    for i, (margin, belief) in enumerate(book):
        desk.observe_roll(account_id=f"A{i}", term_start=START, fuel="electricity",
                          monthly_margin_gbp=margin, renewal_churn_belief=belief)
    return desk


def test_the_on_branch_can_advise_and_can_refuse_and_every_row_says_why():
    rows = _desk().decisions()
    assert len(rows) == 4 * len(STATED_ADVICE_EFFECTS)
    advised = [r for r in rows if r["advised"]]
    refused = [r for r in rows if not r["advised"]]
    # Reachability first: a desk that refuses everything would pass the refusal leg alone.
    assert advised and refused
    assert all(r["reason"] for r in rows)
    assert all(r["value_change_gbp"] >= 0.0 for r in advised)
    assert {r["reason"] for r in refused} == {
        "no scored action leaves both the customer and us no worse off"}
    # A small-margin household is refused under every stated effect: the floor on our side binds.
    assert not any(r["advised"] for r in rows if r["account_id"] in ("A0", "A1"))


def test_a_riding_leg_joins_its_households_roll_and_lifts_our_side():
    desk = _desk(book=((15, 0.3),))
    assert desk.observe_riding_leg(account_id="A0", term_start=START, fuel="gas",
                                   monthly_margin_gbp=40.0)
    rows = desk.decisions()
    assert {r["legs"] for r in rows} == {2} and rows[0]["fuels"] == ["electricity", "gas"]
    assert rows[0]["monthly_margin_gbp"] == 55.0
    assert any(r["advised"] for r in rows)
    alone = _desk(book=((15, 0.3),)).decisions()
    assert not any(r["advised"] for r in alone)


def test_a_declined_fix_spliced_on_the_same_start_is_not_a_second_leg_or_a_second_notice():
    """The engine withdraws a declined fix and splices default-tariff segments on its start; the
    short-window run joined such a gas leg twice (legs 3) before this was refused."""
    desk = _desk(book=((15, 0.3),))
    assert desk.observe_riding_leg(account_id="A0", term_start=START, fuel="gas",
                                   monthly_margin_gbp=40.0)
    desk.observe_roll(account_id="A0", term_start=START, fuel="electricity",
                      monthly_margin_gbp=1.0, renewal_churn_belief=0.9)
    assert not desk.observe_riding_leg(account_id="A0", term_start=START, fuel="gas",
                                       monthly_margin_gbp=3.0)
    [row, *_] = desk.decisions()
    assert row["fuels"] == ["electricity", "gas"] and row["monthly_margin_gbp"] == 55.0
    assert row["monthly_hazard"] == round(monthly_hazard(0.3), 6)


def test_per_household_off_decides_each_leg_alone():
    policy = dataclasses.replace(CURRENT_POLICY, next_best_action_decides_per_household=False)
    desk = _desk(policy, book=((15, 0.3),))
    desk.observe_riding_leg(account_id="A0", term_start=START, fuel="gas", monthly_margin_gbp=40.0)
    rows = desk.decisions()
    assert sorted({(tuple(r["fuels"]), r["legs"]) for r in rows}) == [
        (("electricity",), 1), (("gas",), 1)]


def test_a_leg_with_no_roll_held_for_it_is_not_decided():
    desk = _desk(book=())
    assert not desk.observe_riding_leg(account_id="Z", term_start=START, fuel="gas",
                                       monthly_margin_gbp=40.0)
    assert desk.decisions() == []


@pytest.mark.parametrize("p", [0.0, 0.05, 0.3, 0.9])
def test_the_hazard_is_the_companys_renewal_belief_spread_over_its_twelve_month_term(p):
    assert (1.0 - monthly_hazard(p)) ** 12 == pytest.approx(1.0 - p)


@pytest.mark.parametrize("name", [n for n in dir(dp) if n.isupper() and n.endswith("POLICY")
                                  and isinstance(getattr(dp, n), dp.DecisionPolicy)])
def test_no_standing_policy_turns_the_caller_on(name):
    assert getattr(dp, name).next_best_action_decides_at_renewal is False


def _real_term(start="2019-06-01", forward=50.0):
    return dict(term_start=start, company_forward_per_mwh=forward,
                locked_policy_cost_per_mwh=get_electricity_policy_cost_per_mwh(start),
                locked_network_cost_per_mwh=get_electricity_network_cost_per_mwh(start),
                fuel="electricity")


def test_the_contribution_is_the_rate_over_the_terms_own_cost_plus_the_standing_charge_opex_less_cost_to_serve():
    term = _real_term()
    rate = pre_margin_unit_rate(term["company_forward_per_mwh"], term["term_start"],
                                term["locked_policy_cost_per_mwh"],
                                term["locked_network_cost_per_mwh"]) + TARGET_MARGIN_GBP_PER_MWH
    got = term_contribution_per_month(unit_rate_gbp_per_mwh=rate, company_eac_kwh=3100, **term)
    # Ofgem's nil-consumption electricity opex for April-September 2019 (v1.31, direct debit).
    assert got == pytest.approx(
        (TARGET_MARGIN_GBP_PER_MWH * 3.1 + 41.57 - FIXED_OVERHEAD_GBP_PER_YEAR["resi"]) / 12.0)
    # The old reading, the spread over the forward, is GBP 15+ a month on the same leg.
    assert (rate - term["company_forward_per_mwh"]) * 3.1 / 12.0 - got > 15.0


def test_a_leg_with_no_locked_costs_is_counted_and_a_priced_leg_still_decides():
    no_cost = dict(_real_term(), locked_network_cost_per_mwh=None)
    assert term_contribution_per_month(
        unit_rate_gbp_per_mwh=200.0, company_eac_kwh=3100, **no_cost) is None
    desk = _desk(book=((60, 0.3),))
    desk.observe_roll(account_id="B", term_start=START, fuel="electricity",
                      monthly_margin_gbp=None, renewal_churn_belief=0.3)
    assert not desk.observe_riding_leg(account_id="A0", term_start=START, fuel="gas",
                                       monthly_margin_gbp=None)
    rows = desk.decisions()
    # Reachability first: the priced household is still decided.
    assert {r["account_id"] for r in rows} == {"A0"} and {r["legs"] for r in rows} == {1}
    assert desk.legs_without_contribution == {"roll": 1, "riding": 1}


def test_every_margin_the_run_hands_c34_is_the_terms_contribution():
    from simulation import run_phase2b

    tree = ast.parse(inspect.getsource(run_phase2b))
    handed = [kw.value for node in ast.walk(tree) if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)
              and node.func.attr in ("observe_roll", "observe_riding_leg")
              for kw in node.keywords if kw.arg == "monthly_margin_gbp"]
    assert len(handed) == 2
    assert all(isinstance(v, ast.Call) and getattr(v.func, "id", None)
               == "term_contribution_per_month" for v in handed)


def test_the_standing_charge_opex_credited_is_the_legs_own_fuel_at_the_cap_period_in_force_on_its_start():
    # Ofgem cap level model v1.31, direct-debit nil column: OC to June 2025, CO from July 2025.
    assert standing_charge_opex_per_year("electricity", "2019-06-01") == 41.57
    assert standing_charge_opex_per_year("gas", "2019-06-01") == 68.06
    assert standing_charge_opex_per_year("electricity", "2025-06-30") == 52.43
    assert standing_charge_opex_per_year("electricity", "2025-08-01") == 45.77
    term = dict(_real_term(), unit_rate_gbp_per_mwh=150.0, company_eac_kwh=3100)
    resi = term_contribution_per_year(**term)
    # A gas leg on the same rate and costs is credited the gas allowance, not the electricity one.
    assert term_contribution_per_year(**dict(term, fuel="gas")) - resi == pytest.approx(68.06 - 41.57)
    # The domestic cap does not cover SME: no credit, so it differs from resi by the overheads only.
    sme = term_contribution_per_year(**dict(term, segment="SME"))
    assert resi - sme == pytest.approx(41.57 + FIXED_OVERHEAD_GBP_PER_YEAR["SME"]
                                       - FIXED_OVERHEAD_GBP_PER_YEAR["resi"])
