"""PB8, the household's own payment-method acts -- the world side (2026-10-12, the world lane).

What each control names as its own defect:

  * `test_the_shipped_world_draws_nothing` -- the acts switched on by default.
  * `test_every_cancellation_branch_is_reachable_and_money_scales_it` -- the partition first
    (cancels, does not), then: a stretched household cancels more; a household not paying by DD,
    or already off it, never does.
  * `test_a_cancellation_returns_its_month_and_moves_every_later_bill_to_pay_on_receipt` -- the
    record is drawn and reaches no collection, or reaches the wrong month.
  * `test_the_shock_summary_does_not_count_an_own_reasons_cancellation` -- one act counted twice.
  * `test_a_prepayment_offer_is_answered_only_when_switched_on_and_both_ways` -- an answer invented
    while off, or one that only goes one way.
  * `test_a_debt_on_a_prepayment_meter_is_recovered_at_the_published_weekly_rate` -- the rate lost.
"""
from __future__ import annotations

import simulation.payment_method_dynamics as pmd
from simulation.dd_shock_response import DDShockResponseBook, bill_effect
from simulation.payment_method_dynamics import (
    CAUSE_OWN_REASONS,
    MethodStrengths,
    answer_prepayment_offer,
    debt_recovery_on_prepayment,
    monthly_hazard,
    own_reasons_cancellation,
    summarise,
)

HIGH = MethodStrengths.at("high")


def _cancel(h, stress, dd=True, already=False, strengths=HIGH):
    return own_reasons_cancellation(household=h, month="2020-04", stress=stress,
                                    pays_by_direct_debit=dd, already_cancelled=already,
                                    strengths=strengths)


def test_the_shipped_world_draws_nothing():
    assert pmd.STRENGTHS.off and MethodStrengths.at("default").off
    assert not any(_cancel(f"H{i}", "high", strengths=pmd.STRENGTHS) for i in range(500))
    assert answer_prepayment_offer("A", "2020-04-01", pmd.STRENGTHS) is None


def test_every_cancellation_branch_is_reachable_and_money_scales_it():
    rows = {s: [_cancel(f"H{i}", s) for i in range(20000)] for s in ("low", "high")}
    assert any(rows["high"]) and not all(rows["high"])
    low, high = (sum(r is not None for r in rows[s]) / 20000 for s in ("low", "high"))
    assert 0 < low < high, (low, high)
    assert abs(high - monthly_hazard(HIGH.own_cancel_share * 0.35 / 0.03)) < 0.01, high
    assert abs((1 - monthly_hazard(0.2)) ** 12 - 0.8) < 1e-9
    assert not any(_cancel(f"H{i}", "high", dd=False) for i in range(500))
    assert not any(_cancel(f"H{i}", "high", already=True) for i in range(500))
    one = next(r for r in rows["high"] if r)
    assert one["cause"] == CAUSE_OWN_REASONS and one["failure_multiplier"] == 1.0


def test_a_cancellation_returns_its_month_and_moves_every_later_bill_to_pay_on_receipt():
    row = next(r for i in range(20000) if (r := _cancel(f"H{i}", "high")))
    assert bill_effect([row], "2020-03").cancel_return is False
    assert bill_effect([row], "2020-04").cancel_return is True
    assert bill_effect([row], "2021-01").cancelled is True


def test_the_shock_summary_does_not_count_an_own_reasons_cancellation():
    book = DDShockResponseBook()
    for i in range(20000):
        r = _cancel(f"H{i}", "high")
        if r:
            book.record(r)
    assert book.summary()["mandates_cancelled"] == 0
    assert summarise(book, HIGH)["own_reasons_cancellations"] == len(book._by_household) > 0


def test_a_prepayment_offer_is_answered_only_when_switched_on_and_both_ways():
    answers = {answer_prepayment_offer(f"A{i}", "2020-04-01", HIGH) for i in range(300)}
    assert answers == {True, False}


def test_a_debt_on_a_prepayment_meter_is_recovered_at_the_published_weekly_rate():
    assert debt_recovery_on_prepayment(601.0) == {"weekly_gbp": 6.01, "weeks_to_clear": 100}
    assert debt_recovery_on_prepayment(440.0, "gas")["weeks_to_clear"] == 100
    assert debt_recovery_on_prepayment(601.01)["weeks_to_clear"] == 101
