"""The retention guard can net the bad debt the company itself expects on the term it protects.

The defect each leg names: the payment score lifts a debtor's churn belief over the offer threshold,
and a guard that values the account as if it pays then sends the discount to the worst payers --
value transferred, not created. The belief is the company's own (`company.pricing.default_belief`),
learned from its book by arrears state; nothing here is a new rate.
"""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
from pathlib import Path

from company.crm.churn_model import ARREARS_STATE_NO_DEBT, ARREARS_STATE_WORSENING
from company.interfaces.growth_desk import retention_value_protected
from company.policy.decision_policy import (
    CURRENT_POLICY,
    NAIVE_POLICY,
    VALUE_ARM_CAPPED_POLICY,
    VALUE_ARM_POLICY,
)
from company.pricing.default_belief import AccountYear, default_belief

REPO = Path(__file__).resolve().parents[2]

#: One renewal, at the run's own guard arithmetic: a 3 MWh home at GBP 200/MWh, GBP 15/MWh over
#: forward, a 3% tier discount and the sourced GBP 55 acquisition cost.
EAC_KWH, UNIT, FWD, DISCOUNT, ACQ = 3000.0, 200.0, 185.0, 0.03, 55.0
MARGIN = (UNIT - FWD) * EAC_KWH / 1000.0
COST = UNIT * DISCOUNT * EAC_KWH / 1000.0
BILLED = UNIT * EAC_KWH / 1000.0


def _book() -> list[AccountYear]:
    """A book that has seen clean payers lose 1% of billing and worsening ones 40%."""
    rows = []
    for i in range(60):
        worsening = i % 2 == 1
        rows.append(AccountYear(
            account_id=f"A{i}", payment_method="direct_debit",
            arrears_state=ARREARS_STATE_WORSENING if worsening else ARREARS_STATE_NO_DEBT,
            year_start=dt.date(2018, 1, 1), resolved_on=dt.date(2020, 1, 1), billed_gbp=600.0,
            closed=False, charge_gbp=240.0 if worsening else 6.0))
    return rows


def _belief(state: str) -> float:
    return default_belief(_book(), decided_on=dt.date(2021, 1, 1), arrears_state=state).rate


def test_the_net_guard_both_keeps_a_payers_offer_and_withdraws_a_debtors():
    """The partition first: a guard that withdrew every offer would pass the debtor leg alone."""
    un_netted = retention_value_protected(MARGIN, ACQ, None)
    payer = retention_value_protected(MARGIN, ACQ, None,
                                      default_belief_rate=_belief(ARREARS_STATE_NO_DEBT),
                                      billed=BILLED)
    debtor = retention_value_protected(MARGIN, ACQ, None,
                                       default_belief_rate=_belief(ARREARS_STATE_WORSENING),
                                       billed=BILLED)
    assert un_netted > COST, "the planted debtor must be offered by the un-netted guard"
    assert payer > COST and debtor <= COST
    assert un_netted > payer > debtor


def test_the_learned_belief_is_what_separates_them_not_a_new_rate():
    assert _belief(ARREARS_STATE_WORSENING) > 10 * _belief(ARREARS_STATE_NO_DEBT)


def test_no_belief_leaves_the_guard_bit_identical():
    for engagement in (None, 0.4):
        assert (retention_value_protected(MARGIN, ACQ, engagement, billed=BILLED)
                == retention_value_protected(MARGIN, ACQ, engagement))
    assert retention_value_protected(MARGIN, ACQ, None) == MARGIN + ACQ


def test_the_charge_is_weighed_by_engagement_with_the_margin_it_reduces():
    rate = _belief(ARREARS_STATE_WORSENING)
    assert retention_value_protected(MARGIN, ACQ, 0.5, default_belief_rate=rate,
                                     billed=BILLED) == (MARGIN - rate * BILLED + ACQ) * 0.5


def test_no_standing_policy_nets_bad_debt_so_no_run_moves_until_an_arm_asks():
    for policy in (CURRENT_POLICY, NAIVE_POLICY, VALUE_ARM_POLICY, VALUE_ARM_CAPPED_POLICY):
        assert policy.retention_nets_bad_debt is False
    assert dataclasses.replace(CURRENT_POLICY, retention_nets_bad_debt=True).retention_nets_bad_debt


def test_the_run_hands_the_guard_the_belief_and_gates_it_on_the_flag():
    """The chain: every control above stays green while no production caller reaches the term."""
    tree = ast.parse((REPO / "simulation" / "run_phase2b.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", None) == "retention_value_protected"]
    assert len(calls) == 1
    kw = {k.arg: k.value for k in calls[0].keywords}
    assert isinstance(kw.get("default_belief_rate"), ast.Name)
    belief = kw["default_belief_rate"].id
    gated = [n for n in ast.walk(tree) if isinstance(n, ast.If)
             and "retention_nets_bad_debt" in ast.unparse(n.test)
             and any(isinstance(t, ast.Name) and t.id == belief
                     for s in n.body for a in ast.walk(s) if isinstance(a, ast.Assign)
                     for t in a.targets)]
    assert gated, f"{belief} must be set only under policy.retention_nets_bad_debt"
