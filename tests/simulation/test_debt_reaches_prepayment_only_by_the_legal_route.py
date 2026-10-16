"""W2_42: a household in debt reaches prepayment only by the legal route (2026-10-16, the world lane).

Knowledge: `docs/market_research/company_debt_management.md`, "The world's side of the route from debt
to prepayment".

What each control names as its own defect:

  * `test_every_outcome_of_the_route_is_reachable` -- a gate that refuses everything passes every
    refusal test, so the partition is asserted first: each refusal reason, and both moves, occur.
  * `test_each_condition_of_the_gate_alone_refuses_the_move` -- a 28.7 condition the world forgot to
    check: from a request that moves, breaking one condition must refuse it with that condition named.
  * `test_the_pause_and_the_pre_2023_gap_refuse_a_request_that_moves_after_the_restart` -- the
    timeline read wrong: a lawful request dated in the pause, or before the rules, moves.
  * `test_a_protected_household_may_still_ask_for_prepayment` -- the do-not-install list applied to
    the household's own choice, which it does not cover.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from simulation.payment_method_dynamics import (
    MethodStrengths,
    PrepaymentForDebtRequest,
    move_to_prepayment_for_debt,
)

HIGH = MethodStrengths.at("high")

LAWFUL = PrepaymentForDebtRequest(
    account_id="A1", fuel="electricity", requested_on="2024-06-01", route="warrant",
    debt_gbp=450.0, months_outstanding=5, engagement_attempts=12, site_welfare_visit=True)

BREAKS = {
    "Debt Trigger not met (SLC 28.7)": [dict(debt_gbp=199.99), dict(months_outstanding=2),
                                         dict(on_payment_plan=True)],
    "fewer than 10 engagement attempts": [dict(engagement_attempts=9)],
    "no Site Welfare Visit": [dict(site_welfare_visit=False)],
}


def _move(request, v1=False, strengths=HIGH):
    return move_to_prepayment_for_debt(request, psr_type_vulnerable=v1, strengths=strengths)


def test_every_outcome_of_the_route_is_reachable():
    outcomes = [_move(replace(LAWFUL, **change)) for changes in BREAKS.values() for change in changes]
    outcomes += [_move(LAWFUL), _move(LAWFUL, v1=True),
                 _move(replace(LAWFUL, requested_on="2023-06-01")),
                 _move(replace(LAWFUL, requested_on="2019-06-01"))]
    consent = replace(LAWFUL, route="consent", explicit_consent_recorded=True)
    outcomes += [_move(replace(consent, account_id=f"C{i}")) for i in range(200)]
    outcomes += [_move(replace(consent, explicit_consent_recorded=False)),
                 _move(consent, strengths=MethodStrengths())]
    reasons = {o.reason for o in outcomes}
    assert {o.moved for o in outcomes} == {True, False}
    assert set(BREAKS) <= reasons
    assert {"the 28.7 gate holds", "household is on the do-not-install list",
            "involuntary moves paused industry-wide",
            "the pre-2023 involuntary gate is not established (GAP)",
            "household agreed", "household declined", "no explicit Consent recorded (SLC 28.22)",
            "the household cannot answer: take-up share is off"} <= reasons


@pytest.mark.parametrize("route", ["warrant", "remote_switch"])
def test_each_condition_of_the_gate_alone_refuses_the_move(route):
    lawful = replace(LAWFUL, route=route)
    assert _move(lawful).moved
    for reason, changes in BREAKS.items():
        for change in changes:
            out = _move(replace(lawful, **change))
            assert (out.moved, out.reason) == (False, reason), change
    assert _move(lawful, v1=True).reason == "household is on the do-not-install list"
    assert _move(replace(lawful, debt_gbp=200.0, months_outstanding=3, engagement_attempts=10)).moved


def test_the_pause_and_the_pre_2023_gap_refuse_a_request_that_moves_after_the_restart():
    assert _move(replace(LAWFUL, requested_on="2024-01-01")).moved
    assert not _move(replace(LAWFUL, requested_on="2023-12-31")).moved
    assert not _move(replace(LAWFUL, requested_on="2023-02-01")).moved
    assert "GAP" in _move(replace(LAWFUL, requested_on="2023-01-31")).reason


def test_a_protected_household_may_still_ask_for_prepayment():
    consent = replace(LAWFUL, route="consent", explicit_consent_recorded=True)
    moved = [_move(replace(consent, account_id=f"C{i}"), v1=True).moved for i in range(200)]
    assert any(moved) and not all(moved)
    with pytest.raises(ValueError):
        _move(replace(LAWFUL, route="bailiff"))
