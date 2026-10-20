"""C35 at the renewal roll: the C34 desk carries each leg's renewal terms, so a rise can be priced.

Defects each control names:
- a desk that refuses every rise passes every refusal test, so the partition control asserts a
  priced rise exists before it asserts either refusal;
- a dual household decided on its electricity leg's headroom alone misses the gas leg's room under
  its own default (SEAT_FINDING_THE_DECISION_PROBE_SEES_A_DUAL_HOUSEHOLD_ONLY_THROUGH_ITS_ELECTRICITY_LEG);
- carrying the terms must not move a C34-only arm's rows by a byte;
- the run must hand the terms at both the roll and the riding leg, and must refuse a policy that
  asks for the rise where nothing would price it, rather than ignore it.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

from company.interfaces.renewal_advice import RenewalAdviceDesk, RenewalTerms
from company.policy.decision_policy import CURRENT_POLICY

C34 = dataclasses.replace(CURRENT_POLICY, next_best_action_decides_at_renewal=True)
C35 = dataclasses.replace(C34, next_best_action_shares_by_retention_rise=True)
START = "2019-06-01"
DEFAULT_E, DEFAULT_G = 176.8, 39.4


def _roll(desk, account, margin, offer, default=DEFAULT_E, mwh=3.1, belief=0.3):
    desk.observe_roll(account_id=account, term_start=START, fuel="electricity",
                      monthly_margin_gbp=margin, renewal_churn_belief=belief,
                      renewal=RenewalTerms(offer, default, mwh))


def test_the_rise_can_be_priced_and_can_be_refused_and_each_refusal_says_why():
    desk = RenewalAdviceDesk(C35)
    _roll(desk, "ROOM", -4.0, 150.0)                 # ~6.9 GBP/month under the default
    _roll(desk, "NONE", -4.0, DEFAULT_E)             # priced at the default: no room
    _roll(desk, "PRE", -4.0, 150.0, default=None)    # before 2019: no published default
    rows = desk.decisions()
    risen = [r for r in rows if r["retention_rise_gbp_per_month"] is not None]
    # Reachability first: a desk that refuses every rise would pass both refusal legs alone.
    assert risen and all(r["advised"] and r["account_id"] == "ROOM" for r in risen)
    assert all(0 < r["retention_rise_gbp_per_month"] <= r["headroom_gbp_per_month"] for r in risen)
    why = {r["account_id"]: r["unscored"][0][1] for r in rows if not r["advised"]}
    assert why["NONE"].startswith("retention rise: the rise our side needs")
    assert "above the headroom under the default" in why["NONE"]
    assert why["PRE"].startswith("retention rise: no published default for this fuel")
    assert {r["headroom_gbp_per_month"] for r in rows if r["account_id"] == "PRE"} == {None}


def test_a_dual_households_rise_has_the_room_of_both_legs():
    """Electricity priced at its default has no room alone; the gas leg's room carries the rise."""
    gas_room = (DEFAULT_G - 30.0) * 12.0 / 12.0
    alone = RenewalAdviceDesk(C35)
    _roll(alone, "A", -4.0, DEFAULT_E)
    assert not any(r["advised"] for r in alone.decisions())
    both = RenewalAdviceDesk(C35)
    _roll(both, "A", -4.0, DEFAULT_E)
    assert both.observe_riding_leg(account_id="A", term_start=START, fuel="gas",
                                   monthly_margin_gbp=-4.0,
                                   renewal=RenewalTerms(30.0, DEFAULT_G, 12.0))
    rows = both.decisions()
    assert {r["legs"] for r in rows} == {2}
    assert {r["headroom_gbp_per_month"] for r in rows} == {round(gas_room, 4)}
    assert any(r["advised"] and r["retention_rise_gbp_per_month"] for r in rows)


def test_carrying_the_terms_leaves_a_c34_only_arms_rows_unchanged():
    with_terms, without = RenewalAdviceDesk(C34), RenewalAdviceDesk(C34)
    for desk, terms in ((with_terms, RenewalTerms(150.0, DEFAULT_E, 3.1)), (without, None)):
        desk.observe_roll(account_id="A", term_start=START, fuel="electricity",
                          monthly_margin_gbp=-4.0, renewal_churn_belief=0.3, renewal=terms)
        desk.observe_roll(account_id="B", term_start=START, fuel="electricity",
                          monthly_margin_gbp=60.0, renewal_churn_belief=0.5, renewal=terms)
    rows = with_terms.decisions()
    assert any(r["advised"] for r in rows) and not all(r["advised"] for r in rows)
    assert rows == without.decisions()
    assert not any("retention_rise_gbp_per_month" in r for r in rows)


def _run_source():
    import simulation.run_phase2b as run
    return run, ast.parse(inspect.getsource(run))


def test_the_run_hands_the_desk_renewal_terms_at_the_roll_and_at_the_riding_leg():
    _, tree = _run_source()
    calls = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("observe_roll", "observe_riding_leg")):
            kw = {k.arg: k.value for k in node.keywords}
            assert "renewal" in kw, f"{node.func.attr} at line {node.lineno} carries no terms"
            assert (isinstance(kw["renewal"], ast.Call) and isinstance(kw["renewal"].func, ast.Name)
                    and kw["renewal"].func.id == "_renewal_terms"), node.lineno
            calls[node.func.attr] = calls.get(node.func.attr, 0) + 1
    assert calls == {"observe_roll": 1, "observe_riding_leg": 1}


def test_the_runs_terms_are_the_offer_the_published_default_and_the_companys_volume():
    run, _ = _run_source()
    from company.crm.save_offer import published_default_rate_ex_vat
    t = run._renewal_terms("gas", START, 30.0, 12_000.0)
    assert t == RenewalTerms(30.0, published_default_rate_ex_vat("gas", START), 12.0)
    assert t.published_default_gbp_per_mwh is not None
    assert run._renewal_terms("electricity", "2017-06-01", 150.0, None) == RenewalTerms(150.0, None, None)


def test_a_rise_asked_for_with_no_caller_is_refused_with_its_reason():
    run, _ = _run_source()
    run._refuse_a_rise_with_no_caller(C35)
    run._refuse_a_rise_with_no_caller(CURRENT_POLICY)
    with pytest.raises(ValueError, match="next_best_action_decides_at_renewal"):
        run._refuse_a_rise_with_no_caller(
            dataclasses.replace(CURRENT_POLICY, next_best_action_shares_by_retention_rise=True))


def test_the_rise_is_off_on_every_standing_policy():
    from company.policy import decision_policy as dp
    standing = [v for v in vars(dp).values() if isinstance(v, dp.DecisionPolicy)]
    assert len(standing) >= 3
    assert not any(p.next_best_action_shares_by_retention_rise for p in standing)
