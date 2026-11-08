"""Phase II: deeper coverage for pnl, credit_facility, retention_risk."""
import datetime as dt



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
