"""Every renewal decision that weighs a margin reads the term's contribution, through one function.

The defect: the retention guard and the missed-retention log valued a retained term at
`(unit rate - company forward) x EAC`, the spread over wholesale, which still carries the policy,
network and capital costs the rate passes through. C34 carried the same quantity until a57ea3da0.
One quantity in four places is the VAT shape, so the control is over the run's source: no site may
compute the spread, and the two retention sites call `term_contribution_per_year`
(`next_best_action_and_cross_sell.md` §6.1, amended 2026-10-20).
"""
from __future__ import annotations

import ast
import inspect

import pytest

from company.analytics.counterfactual_retention import compute_counterfactual_retention
from company.interfaces.growth_desk import (
    replacement_cost_avoided_gbp,
    retention_cut_share_at_risk_tiers,
    retention_value_protected,
)
from company.interfaces.renewal_advice import (
    term_contribution_per_month,
    term_contribution_per_year,
)
from company.pricing.renewal_desk import TARGET_MARGIN_GBP_PER_MWH, pre_margin_unit_rate
from simulation.policy_costs import (
    get_electricity_network_cost_per_mwh,
    get_electricity_policy_cost_per_mwh,
)


def _real_term(start="2019-06-01", forward=50.0):
    return dict(term_start=start, company_forward_per_mwh=forward,
                locked_policy_cost_per_mwh=get_electricity_policy_cost_per_mwh(start),
                locked_network_cost_per_mwh=get_electricity_network_cost_per_mwh(start),
                fuel="electricity")


def _run_tree():
    from simulation import run_phase2b

    return ast.parse(inspect.getsource(run_phase2b))


def _calls_contribution(node) -> bool:
    return isinstance(node, ast.Call) and getattr(node.func, "id", None) == "term_contribution_per_year"


def test_the_guard_and_the_missed_log_value_a_term_by_its_contribution():
    tree = _run_tree()
    guard = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
             and any(getattr(t, "id", None) == "expected_margin" for t in n.targets)]
    logged = [v for n in ast.walk(tree) if isinstance(n, ast.Dict)
              for k, v in zip(n.keys, n.values)
              if isinstance(k, ast.Constant) and k.value == "expected_term_margin_gbp"]
    # Reachability first: both sites exist, so an empty census cannot pass.
    assert len(guard) == 1 and len(logged) == 2
    assert _calls_contribution(guard[0])
    # The offered row logs the guard's own value; the missed row computes it the same way.
    assert all(_calls_contribution(v) or getattr(v, "id", None) == "expected_margin" for v in logged)
    assert sum(_calls_contribution(v) for v in logged) == 1


def test_no_decision_in_the_run_computes_the_spread_over_the_companys_forward():
    spreads = [n for n in ast.walk(_run_tree()) if isinstance(n, ast.BinOp)
               and isinstance(n.op, ast.Sub) and getattr(n.right, "id", None) == "company_fwd"]
    assert spreads == []


def test_c34s_monthly_value_is_the_guards_yearly_value_over_twelve():
    term = dict(_real_term(), unit_rate_gbp_per_mwh=180.0, company_eac_kwh=3100)
    assert term_contribution_per_month(**term) * 12.0 == pytest.approx(
        term_contribution_per_year(**term))
    assert term_contribution_per_year(**dict(term, locked_policy_cost_per_mwh=None)) is None


def _guard_offers(rate: float, *, kwh: float = 3100.0, tier: float = 0.03,
                  default_belief_rate: float | None = None) -> bool:
    term = _real_term()
    floor = pre_margin_unit_rate(term["company_forward_per_mwh"], term["term_start"],
                                 term["locked_policy_cost_per_mwh"],
                                 term["locked_network_cost_per_mwh"])
    cut = retention_cut_share_at_risk_tiers(rate, tier, cost_floor=floor)
    assert cut is not None
    cost = rate * cut * kwh / 1000.0
    value = retention_value_protected(
        term_contribution_per_year(unit_rate_gbp_per_mwh=rate, company_eac_kwh=kwh, **term),
        replacement_cost_avoided_gbp(segment="resi", counted_in_guard=True), None,
        default_belief_rate=default_belief_rate, billed=rate * kwh / 1000.0)
    return value > cost


def test_the_guard_still_offers_where_the_strike_sits_well_above_cost_and_refuses_an_unmoved_debtor():
    term = _real_term()
    floor = pre_margin_unit_rate(term["company_forward_per_mwh"], term["term_start"],
                                 term["locked_policy_cost_per_mwh"],
                                 term["locked_network_cost_per_mwh"])
    # The offering branch first: a strike an upstream writer raised GBP 30/MWh over cost buys a 3% cut.
    assert _guard_offers(floor + 30.0)
    # An unmoved strike now contributes about -GBP 4 a year once the standing charge's opex is
    # credited (§6.1, 2026-10-20), and the replacement spend avoided carries it over a cut that only
    # sells down to the floor; so the same strike is offered at the resi base rate and refused once
    # the 2022 bad-debt belief is netted. On the spread over wholesale it read GBP 230 a year and
    # was offered at both.
    unmoved = floor + TARGET_MARGIN_GBP_PER_MWH + 1.0
    assert _guard_offers(unmoved, default_belief_rate=0.02)
    assert not _guard_offers(unmoved, default_belief_rate=0.08)


def test_a_missed_retention_with_no_contribution_is_counted_unpriced_not_summed_as_zero():
    misses = [
        {"customer_id": "A", "event_date": "2019-06-01", "company_churn_estimate": 0.2,
         "expected_term_margin_gbp": None, "expected_term_revenue_gbp": 600.0,
         "no_offer_reason": "below_threshold", "would_be_discount_pct": None},
        {"customer_id": "B", "event_date": "2019-06-01", "company_churn_estimate": 0.2,
         "expected_term_margin_gbp": -30.0, "expected_term_revenue_gbp": 600.0,
         "no_offer_reason": "below_threshold", "would_be_discount_pct": None},
        # Unpriced whether or not the offer would have kept it: a lost one is not a zero either.
        {"customer_id": "C", "event_date": "2019-06-01", "company_churn_estimate": 0.2,
         "expected_term_margin_gbp": None, "expected_term_revenue_gbp": 600.0,
         "no_offer_reason": "below_threshold", "would_be_discount_pct": None},
    ]
    events = [{"customer_id": c, "event_date": "2019-06-01", "churn_probability": 0.5,
               "random_roll": 0.0 if c != "C" else 0.999} for c in "ABC"]
    report = compute_counterfactual_retention(misses, events)
    assert [m.counterfactual_retained for m in report.misses] == [True, True, False]
    assert report.misses_that_could_not_be_priced == 2
    assert report.total_value_at_stake_gbp == pytest.approx(-30.0)
