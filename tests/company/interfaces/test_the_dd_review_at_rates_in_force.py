"""Controls on the second DD review rule: last year's consumption at the rates in force.

`simulation.dd_balance_book.reviewed_standing` sizes a review either from last year's spend or
from last year's billed kWh and days priced at the rates on the new year's first bill
(`company.interfaces.dd_review_outcome.reviewed_monthly_amount_at_rates`). The property: the
rules agree when prices are flat and part when they move. A rule that ignored the rate would
pass the first leg, and the second leg is there to catch it.
"""
from __future__ import annotations

from datetime import date

import pytest

from company.interfaces.dd_review_outcome import reviewed_monthly_amount_at_rates
from simulation.arrears_engine import payment_method
from simulation.dd_balance_book import REVIEW_RULES, build_dd_balance_book, reviewed_standing

VAT = 1.05
KWH = 300.0


def _bill(cid: str, y: int, m: int, unit: float, sc: float) -> dict:
    start = date(y, m, 1)
    end = date(y + (m == 12), m % 12 + 1, 1)
    days = (end - start).days
    end = date.fromordinal(end.toordinal() - 1)
    return {"customer_id": cid, "segment": "resi", "commodity": "electricity",
            "period_start": start.isoformat(), "period_end": end.isoformat(),
            "days_in_period": days, "total_consumption_kwh": KWH,
            "average_unit_rate_gbp_per_mwh": unit, "standing_charge_gbp_per_day": sc,
            "total_amount_gbp": (KWH / 1000.0 * unit + days * sc) * VAT}


def _two_years(cid: str, second_unit: float) -> list[dict]:
    return ([_bill(cid, 2017, m, 120.0, 0.20) for m in range(1, 13)]
            + [_bill(cid, 2018, m, second_unit, 0.20) for m in range(1, 13)])


def _a_direct_debit_id() -> str:
    for i in range(1, 500):
        if payment_method("resi", 40.0, f"C{i}", "electricity") == "direct_debit":
            return f"C{i}"
    raise AssertionError("no direct-debit id in C1..C499")


def test_the_two_rules_agree_when_prices_are_flat():
    """DEFECT: the new rule re-prices something other than the year (wrong days, VAT dropped,
    kWh double-counted), so it moves the debit even when nothing about the price moved."""
    bills = _two_years("C1", 120.0)
    spend = reviewed_standing("last_year_spend", bills[:12], bills[12])
    priced = reviewed_standing("consumption_at_rates_in_force", bills[:12], bills[12])
    assert priced == spend


def test_the_two_rules_part_when_the_price_rises_at_the_review():
    """DEFECT: the rule reads the rate off the completed year (its last bill) and not the year
    being set, or ignores the rate. The new year's price is 10% up from its first bill, so the
    rule must set more than last year's spend, by the price rise on the kWh."""
    bills = _two_years("C1", 132.0)
    spend = reviewed_standing("last_year_spend", bills[:12], bills[12])
    priced = reviewed_standing("consumption_at_rates_in_force", bills[:12], bills[12])
    expected = reviewed_monthly_amount_at_rates(
        annual_kwh=12 * KWH, days=365, unit_rate_per_mwh_ex_vat=132.0,
        standing_charge_per_day_ex_vat=0.20)
    assert priced == expected
    # 3,600 kWh x £12/MWh x 1.05 = £45.36 a year, about £3.78 a month.
    assert priced - spend >= 3


def test_every_branch_of_the_rule_is_reachable():
    """DEFECT: the fallback swallows the rule (every review reads as last year's spend), and the
    flat-price leg still passes. One control over the partition: priced, fallback, refused."""
    bills = _two_years("C1", 132.0)
    stripped = dict(bills[12])
    del stripped["average_unit_rate_gbp_per_mwh"]
    spend = reviewed_standing("last_year_spend", bills[:12], bills[12])
    priced = reviewed_standing("consumption_at_rates_in_force", bills[:12], bills[12])
    fallback = reviewed_standing("consumption_at_rates_in_force", bills[:12], stripped)
    assert priced != spend and fallback == spend
    with pytest.raises(ValueError, match="unknown DD review rule"):
        reviewed_standing("seek_balance", bills[:12], bills[12])
    assert set(REVIEW_RULES) == {
        "last_year_spend", "consumption_at_rates_in_force", "own_forecast_plus_balance"}


def test_the_book_carries_the_rule_it_is_given():
    """DEFECT: `review_rule` is accepted and never reaches the chain, so the book is the spend
    book whichever rule is named. Flat: identical trajectories. Rising: a different balance."""
    cid = _a_direct_debit_id()
    flat, rising = _two_years(cid, 120.0), _two_years(cid, 132.0)

    def final(bills, rule):
        book = build_dd_balance_book(bills, {cid: 40.0}, review_rule=rule)
        return [p.balance_gbp for p in book.trajectories[cid]]

    assert final(flat, "last_year_spend") == final(flat, "consumption_at_rates_in_force")
    assert final(rising, "consumption_at_rates_in_force")[-1] > final(rising, "last_year_spend")[-1]


def test_the_legs_tool_follows_the_rule_and_only_rounding_and_lag_move():
    """DEFECT: `tools/dd_book_legs` grades the new rule against the old book, or books the
    re-pricing into a leg the rule does not touch. `decompose` refuses legs that miss the book's
    own balance, so admitting the account is the sum check."""
    from tools.dd_book_legs import decompose

    cid = _a_direct_debit_id()
    bills = _two_years(cid, 132.0)
    old = decompose(bills, {cid: 40.0}, "2018-06", "last_year_spend")["groups"]["all"]
    new = decompose(bills, {cid: 40.0}, "2018-06", "consumption_at_rates_in_force")["groups"]["all"]
    assert old["n_accounts"] == new["n_accounts"] == 1
    for leg in ("opening_sizing", "seasonal_phase", "estimate_vs_actual"):
        assert new[leg] == old[leg]
    assert new["review_lag"] > old["review_lag"]
    assert new["balance_gbp"] - old["balance_gbp"] == pytest.approx(
        new["review_lag"] - old["review_lag"] + new["rounding"] - old["rounding"], abs=0.02)


def test_the_third_rule_books_a_balance_recovery_leg_and_sums_to_the_books_own_balance():
    """DEFECT: the balance addition lands in `rounding` instead of its own leg (the contamination
    `priced_annual`/`reviewed_standing` would otherwise share), or the book `build_dd_balance_book`
    builds disagrees with what `account_legs` prices, which `decompose`'s own sum check catches."""
    from tools.dd_book_legs import decompose

    cid = _a_direct_debit_id()
    bills = _two_years(cid, 132.0)
    rates = decompose(bills, {cid: 40.0}, "2018-06", "consumption_at_rates_in_force")["groups"]["all"]
    forecast = decompose(bills, {cid: 40.0}, "2018-06", "own_forecast_plus_balance")["groups"]["all"]
    # Flat-opening DD below the first year's real spend puts the account in debit by the second
    # window, so the balance leg this rule reads is non-zero -- the branch is actually taken.
    assert forecast["balance_recovery"] != 0.0
    for leg in ("opening_sizing", "seasonal_phase", "estimate_vs_actual", "review_lag"):
        assert forecast[leg] == rates[leg]
    assert forecast["balance_gbp"] == pytest.approx(
        sum(forecast[leg] for leg in (
            "opening_sizing", "review_lag", "rounding", "seasonal_phase",
            "estimate_vs_actual", "balance_recovery")), abs=0.02)
