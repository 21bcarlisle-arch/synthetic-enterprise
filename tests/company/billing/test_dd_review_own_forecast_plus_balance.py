"""Controls on the third DD review rule: the company's own twelve-month forecast, priced at the
known rate while the current term runs and the company's forward estimate beyond it, plus the
balance the account carries into the review -- the director's ruling of 2026-10-11 (console,
04:20Z), closing the practitioner question `docs/market_research/
what_a_supplier_holds_to_size_a_direct_debit.md` §4.7 raised.

Properties: the new rule collapses to `consumption_at_rates_in_force` when the account carries no
balance and no term boundary falls inside the forecast year (the only shape reachable through
`simulation.dd_balance_book.build_dd_balance_book` today -- it has no term data to pass). The
known/forward rate split is real and reachable, proven here by calling `reviewed_standing`
directly with the kwargs the SIM-side caller does not yet supply (filed as owed in the knowledge
page, not shipped as a branch nothing can take).
"""
from __future__ import annotations

from datetime import date

import pytest

from company.billing.dd_review import (
    REVIEW_RULES,
    priced_annual_inc_vat_at_rates,
    priced_annual_inc_vat_blended,
    reviewed_standing,
    simple_balance_after_window,
)

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


def test_the_rule_is_registered():
    assert "own_forecast_plus_balance" in REVIEW_RULES


def test_with_no_balance_and_no_term_it_equals_rates_in_force_when_flat():
    bills = _two_years("C1", 120.0)
    priced = reviewed_standing("consumption_at_rates_in_force", bills[:12], bills[12])
    forecast = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    assert forecast == priced


def test_with_no_balance_and_no_term_it_equals_rates_in_force_when_rising():
    """DEFECT: the new rule drifts from rule 2's own price leg even with nothing new supplied --
    it must degrade to EXACTLY the same figure, not a similar one."""
    bills = _two_years("C1", 132.0)
    priced = reviewed_standing("consumption_at_rates_in_force", bills[:12], bills[12])
    forecast = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    assert forecast == priced


def test_the_balance_is_recovered_over_twelve_months():
    """DEFECT: the balance is dropped, charged in one month instead of twelve, or charged before
    VAT (double-grossing cash that is already on the statement)."""
    bills = _two_years("C1", 120.0)
    without = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    with_debit = reviewed_standing(
        "own_forecast_plus_balance", bills[:12], bills[12], balance_to_clear_gbp=1200.0)
    assert with_debit - without == pytest.approx(100.0, abs=0.6)  # 1200/12, within one rounding step


def test_a_credit_balance_lowers_the_debit_symmetrically():
    """The documented GAP: credit and debit are treated symmetrically. A negative balance (credit
    held) must lower the recommendation by the same arithmetic a debit raises it, not clamp at
    zero or do nothing -- the asymmetric reading is a modelling choice this build did NOT make,
    and this is the control that would catch making it by accident."""
    bills = _two_years("C1", 120.0)
    without = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    with_credit = reviewed_standing(
        "own_forecast_plus_balance", bills[:12], bills[12], balance_to_clear_gbp=-1200.0)
    assert without - with_credit == pytest.approx(100.0, abs=0.6)


def test_the_known_forward_split_is_reachable_and_moves_the_price():
    """CLAUDE.md: a branch that exists to be taken rarely must be shown to be taken before
    anything is asserted about what it does. `build_dd_balance_book` does not yet pass
    `term_end_iso`/`forward_rate_per_mwh_ex_vat` (filed as owed), so this calls the door directly --
    the one place in the tree that can reach it today."""
    bills = _two_years("C1", 120.0)
    whole_year_known = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    # Term ends 6 months into the forecast year; the forward half is priced much higher.
    split = reviewed_standing(
        "own_forecast_plus_balance", bills[:12], bills[12],
        term_end_iso="2018-07-01", forward_rate_per_mwh_ex_vat=240.0)
    assert split != whole_year_known
    assert split > whole_year_known


def test_a_term_end_outside_the_forecast_year_does_not_engage_the_forward_rate():
    """DEFECT: the split engages even when the term outlasts the whole forecast year (known_days
    clipped above total_days), silently blending in a forward rate that was never reached."""
    bills = _two_years("C1", 120.0)
    whole_year_known = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    still_whole_year = reviewed_standing(
        "own_forecast_plus_balance", bills[:12], bills[12],
        term_end_iso="2020-01-01", forward_rate_per_mwh_ex_vat=999.0)
    assert still_whole_year == whole_year_known


def test_every_branch_of_the_rule_is_reachable():
    bills = _two_years("C1", 132.0)
    stripped = dict(bills[12])
    del stripped["average_unit_rate_gbp_per_mwh"]
    spend = reviewed_standing("last_year_spend", bills[:12], bills[12])
    forecast = reviewed_standing("own_forecast_plus_balance", bills[:12], bills[12])
    fallback = reviewed_standing("own_forecast_plus_balance", bills[:12], stripped)
    assert forecast != spend and fallback == spend


def test_priced_annual_inc_vat_blended_collapses_to_at_rates_when_known_days_is_total_days():
    at_rates = priced_annual_inc_vat_at_rates(
        annual_kwh=3600.0, days=365, unit_rate_per_mwh_ex_vat=132.0,
        standing_charge_per_day_ex_vat=0.20)
    blended = priced_annual_inc_vat_blended(
        annual_kwh=3600.0, total_days=365, known_days=365,
        unit_rate_known_per_mwh_ex_vat=132.0, unit_rate_forward_per_mwh_ex_vat=999.0,
        standing_charge_per_day_ex_vat=0.20)
    assert blended == at_rates  # the forward rate is never read when known_days == total_days


def test_simple_balance_after_window_is_additive_bookkeeping():
    """DEFECT: the helper applies VAT, rounds, or reads anything but the bills and the standing
    amount -- it is meant to be plain arithmetic the world already holds."""
    window_bills = [{"total_amount_gbp": 100.0}, {"total_amount_gbp": 150.0}]
    result = simple_balance_after_window(50.0, 20.0, window_bills)
    assert result == pytest.approx(50.0 + 20.0 * 12 - 250.0)
