"""Phase II: deeper coverage for pnl, credit_facility, retention_risk."""
import datetime as dt
import pytest

# ===== pnl =====
from company.finance.pnl import company_income_statement, reconcile_with_sim


def _events(**kwargs):
    # settlement_event.amount_gbp is negative by convention (cost outflow)
    defaults = {
        "payment_received_event": [{"event_type": "payment_received_event", "amount_gbp": 5000.0}],
        "settlement_event": [{"event_type": "settlement_event", "amount_gbp": -3000.0}],
        "capital_charge_event": [{"event_type": "capital_charge_event", "amount_gbp": -200.0}],
        "bad_debt_event": [],
        "acquisition_spend_event": [],
        "fixed_cost_event": [],
    }
    defaults.update(kwargs)
    events = []
    for v in defaults.values():
        events.extend(v)
    return events


class TestCompanyIncomeStatement:
    def test_cash_basis_when_payment_events_present(self):
        result = company_income_statement(_events())
        assert result["revenue_basis"] == "cash (payment_received_event)"

    def test_accrual_basis_when_no_payment_events(self):
        events = [{"event_type": "billing_event", "amount_gbp": 5000.0},
                  {"event_type": "settlement_event", "amount_gbp": 3000.0}]
        result = company_income_statement(events)
        assert result["revenue_basis"] == "accrual (billing_event)"

    def test_revenue_gbp(self):
        result = company_income_statement(_events())
        assert result["revenue_gbp"] == pytest.approx(5000.0)

    def test_wholesale_cost_gbp(self):
        result = company_income_statement(_events())
        assert result["wholesale_cost_gbp"] == pytest.approx(3000.0)

    def test_gross_margin_gbp(self):
        result = company_income_statement(_events())
        assert result["gross_margin_gbp"] == pytest.approx(2000.0)

    def test_net_margin_includes_cts(self):
        result = company_income_statement(_events(), cost_to_serve_gbp=300.0)
        assert result["net_margin_gbp"] == pytest.approx(2000.0 - 200.0 - 300.0)

    def test_net_margin_pct_present_when_positive_gross(self):
        result = company_income_statement(_events())
        assert "net_margin_pct" in result

    def test_bad_debt_reduces_net_revenue(self):
        events = _events(bad_debt_event=[{"event_type": "bad_debt_event", "amount_gbp": -100.0}])
        result = company_income_statement(events)
        assert result["bad_debt_gbp"] == pytest.approx(100.0)
        assert result["net_revenue_gbp"] == pytest.approx(4900.0)

    def test_reconcile_agrees_within_penny(self):
        result = company_income_statement(_events())
        r = reconcile_with_sim(result, result["net_margin_gbp"])
        assert r["agrees"] is True

    def test_reconcile_notes_gap(self):
        result = company_income_statement(_events())
        r = reconcile_with_sim(result, result["net_margin_gbp"] + 50.0)
        assert r["agrees"] is False
        assert r["gap_gbp"] == pytest.approx(-50.0)


# ===== credit_facility =====
from company.finance.credit_facility import (
    CreditFacilityBook, DrawdownReason
)


def _book():
    b = CreditFacilityBook()
    b.register_facility("F001", "Barclays", 2_000_000.0, 4.5, 0.5,
                         dt.date(2027, 12, 31))
    return b


class TestCreditFacilityBook:
    def test_drawdown_creates_id(self):
        b = _book()
        dd = b.drawdown("F001", 500_000.0, dt.date(2023, 1, 10), DrawdownReason.WORKING_CAPITAL)
        assert dd.drawdown_id == "DD-0001"

    def test_outstanding_balance_after_drawdown(self):
        b = _book()
        b.drawdown("F001", 500_000.0, dt.date(2023, 1, 10), DrawdownReason.WORKING_CAPITAL)
        assert b.outstanding_balance("F001") == pytest.approx(500_000.0)

    def test_limit_breach_raises(self):
        b = _book()
        with pytest.raises(ValueError):
            b.drawdown("F001", 2_500_000.0, dt.date(2023, 1, 10), DrawdownReason.EMERGENCY)

    def test_repay_clears_outstanding(self):
        b = _book()
        dd = b.drawdown("F001", 300_000.0, dt.date(2023, 1, 10), DrawdownReason.WORKING_CAPITAL)
        b.repay(dd.drawdown_id, dt.date(2023, 3, 1))
        assert b.outstanding_balance("F001") == pytest.approx(0.0)

    def test_interest_accrued_positive(self):
        b = _book()
        b.drawdown("F001", 1_000_000.0, dt.date(2023, 1, 1), DrawdownReason.WHOLESALE_SETTLEMENT)
        accrued = b.total_interest_accrued_gbp(dt.date(2023, 4, 1))
        assert accrued > 0

    def test_utilisation_pct_after_drawdown(self):
        b = _book()
        b.drawdown("F001", 1_000_000.0, dt.date(2023, 1, 1), DrawdownReason.SEASONAL_CASHFLOW)
        assert b.utilisation_pct("F001") == pytest.approx(50.0)

    def test_daily_commitment_fee(self):
        b = _book()
        f = b._facilities["F001"]
        expected = round(2_000_000 * 0.5 / 100 / 365, 2)
        assert f.daily_commitment_fee_gbp == pytest.approx(expected)

    def test_repay_not_outstanding(self):
        b = _book()
        dd = b.drawdown("F001", 200_000.0, dt.date(2023, 1, 1), DrawdownReason.BSC_CREDIT_COVER)
        b.repay(dd.drawdown_id, dt.date(2023, 2, 1))
        assert not dd.is_outstanding

    def test_two_drawdowns_cumulative_balance(self):
        b = _book()
        b.drawdown("F001", 400_000.0, dt.date(2023, 1, 1), DrawdownReason.WORKING_CAPITAL)
        b.drawdown("F001", 300_000.0, dt.date(2023, 2, 1), DrawdownReason.WORKING_CAPITAL)
        assert b.outstanding_balance("F001") == pytest.approx(700_000.0)

    def test_interest_stops_accruing_after_repay(self):
        b = _book()
        dd = b.drawdown("F001", 1_000_000.0, dt.date(2023, 1, 1), DrawdownReason.WORKING_CAPITAL)
        b.repay(dd.drawdown_id, dt.date(2023, 1, 31))
        # Check at the repay date vs. a month later — should be the same
        at_repay = b.total_interest_accrued_gbp(dt.date(2023, 1, 31))
        at_later = b.total_interest_accrued_gbp(dt.date(2023, 3, 31))
        assert at_repay == pytest.approx(at_later)


# ===== retention_risk =====
from company.crm.retention_risk import retention_risk, portfolio_risk_summary


def _cust(customer_id="C1", smart_meter=True):
    return {"customer_id": customer_id, "smart_meter": smart_meter}


def _overdue_invoice(customer_id="C1"):
    return {"customer_id": customer_id, "payment_status": "unpaid",
            "due_date": "2020-01-01"}  # old date = overdue


class TestRetentionRisk:
    def test_no_signals_low_tier(self):
        r = retention_risk(_cust(), [], [])
        assert r["tier"] == "LOW"
        assert r["score"] == 0

    def test_overdue_invoice_adds_score(self):
        r = retention_risk(_cust(), [_overdue_invoice()], [])
        assert r["score"] >= 2
        assert "Overdue invoice" in r["signals"]

    def test_overdue_invoice_medium_tier(self):
        r = retention_risk(_cust(), [_overdue_invoice()], [])
        assert r["tier"] == "MEDIUM"

    def test_recent_complaint_adds_signal(self):
        contacts = [{"customer_id": "C1", "complaint_flag": True,
                     "event_date": dt.date.today().isoformat()}]
        r = retention_risk(_cust(), [], contacts)
        assert "Recent complaint (90 days)" in r["signals"]

    def test_rate_above_market_adds_signal(self):
        r = retention_risk(_cust(), [], [],
                           rate_cmp={"protected": False, "delta_p": 2.0})
        assert "Rate significantly above market" in r["signals"]

    def test_renewal_notice_fixed_adds_signal(self):
        r = retention_risk(_cust(), [], [],
                           renewal_info={"in_notice_window": True, "is_fixed": True})
        assert any("notice window" in s for s in r["signals"])

    def test_score_capped_at_5(self):
        contacts = [{"customer_id": "C1", "complaint_flag": True,
                     "event_date": dt.date.today().isoformat()}]
        r = retention_risk(_cust(), [_overdue_invoice()], contacts,
                           renewal_info={"in_notice_window": True, "is_fixed": False},
                           rate_cmp={"protected": False, "delta_p": 5.0})
        assert r["score"] <= 5

    def test_high_tier_when_score_above_3(self):
        contacts = [{"customer_id": "C1", "complaint_flag": True,
                     "event_date": dt.date.today().isoformat()}]
        r = retention_risk(_cust(), [_overdue_invoice()], contacts,
                           renewal_info={"in_notice_window": True, "is_fixed": False},
                           rate_cmp={"protected": False, "delta_p": 5.0})
        assert r["tier"] == "HIGH"

    def test_portfolio_risk_summary_counts(self):
        custs = [_cust("C1"), _cust("C2")]
        invoices = [_overdue_invoice("C1"), _overdue_invoice("C2")]
        s = portfolio_risk_summary(custs, invoices, [])
        assert s["total"] == 2
        assert s["medium_risk"] + s["high_risk"] >= 2

    def test_portfolio_risk_summary_keys(self):
        s = portfolio_risk_summary([_cust()], [], [])
        assert "high_risk" in s and "low_risk" in s and "customers" in s
