"""Tests for saas/ledger.py — Phase 7a/7b/8a transaction log."""
import pytest

from saas.ledger import (
    build_ledger,
    derive_cash_position,
    derive_pnl,
    ledger_summary,
    make_acquisition_spend_event,
    make_bad_debt_event,
    make_billing_event,
    make_fixed_cost_event,
    make_capital_charge_event,
    make_non_commodity_cost_event,
    make_payment_received_event,
    make_settlement_event,
    make_vat_remittance_event,
)


def _settlement_record(
    customer_id="C1",
    date="2016-01-01",
    period=1,
    revenue=10.0,
    wholesale=6.0,
    capital=0.5,
    net=3.5,
    consumption=50.0,
    rate=120.0,
    commodity="electricity",
    treasury=1000.0,
):
    return {
        "customer_id": customer_id,
        "settlement_date": date,
        "settlement_period": period,
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "capital_cost_gbp": capital,
        "net_margin_gbp": net,
        "consumption_kwh": consumption,
        "unit_rate_gbp_per_mwh": rate,
        "commodity": commodity,
        "treasury_cash_balance_gbp": treasury,
        "margin_gbp": revenue - wholesale,
    }


def _bill(customer_id="C1", period_start="2016-01-01", period_end="2016-01-31",
          amount=100.0, consumption=1500.0):
    return {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "total_amount_gbp": amount,
        "total_consumption_kwh": consumption,
        "clarity_score": 0.85,
        "bill_shock_pct": None,
    }


def _bill_9a(customer_id="C1", period_start="2016-01-01", period_end="2016-01-31",
             commodity_amount=80.0, non_commodity=11.0, standing=5.0,
             vat=4.8, segment="resi", commodity="electricity"):
    total = commodity_amount + non_commodity + standing + vat
    return {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "commodity_amount_gbp": commodity_amount,
        "non_commodity_amount_gbp": non_commodity,
        "standing_charge_gbp": standing,
        "vat_gbp": vat,
        "total_amount_gbp": total,
        "total_consumption_kwh": 1500.0,
        "clarity_score": 0.85,
        "bill_shock_pct": None,
        "segment": segment,
        "commodity": commodity,
    }


# --- make_settlement_event ---

def test_make_settlement_event_amount_is_negative():
    r = _settlement_record(wholesale=6.0)
    e = make_settlement_event(r)
    assert e["amount_gbp"] == -6.0


def test_make_settlement_event_carries_volume_and_rate():
    r = _settlement_record(consumption=50.0, rate=120.0)
    e = make_settlement_event(r)
    assert e["volume_kwh"] == 50.0
    assert e["unit_rate_gbp_per_mwh"] == 120.0


def test_make_settlement_event_transaction_id_is_deterministic():
    r = _settlement_record()
    id1 = make_settlement_event(r)["transaction_id"]
    id2 = make_settlement_event(r)["transaction_id"]
    assert id1 == id2


def test_make_settlement_event_different_periods_give_different_ids():
    r1 = _settlement_record(period=1)
    r2 = _settlement_record(period=2)
    assert make_settlement_event(r1)["transaction_id"] != make_settlement_event(r2)["transaction_id"]


# --- make_capital_charge_event ---

def test_make_capital_charge_event_amount_is_negative():
    r = _settlement_record(capital=0.5)
    e = make_capital_charge_event(r)
    assert e["amount_gbp"] == -0.5


def test_make_capital_charge_event_id_differs_from_settlement_event():
    r = _settlement_record()
    s_id = make_settlement_event(r)["transaction_id"]
    c_id = make_capital_charge_event(r)["transaction_id"]
    assert s_id != c_id


# --- make_billing_event ---

def test_make_billing_event_amount_is_positive():
    e = make_billing_event("C1", "electricity", "2016-01-01", 100.0, 1500.0)
    assert e["amount_gbp"] == 100.0


def test_make_billing_event_transaction_id_is_deterministic():
    e1 = make_billing_event("C1", "electricity", "2016-01-01", 100.0, 1500.0)
    e2 = make_billing_event("C1", "electricity", "2016-01-01", 100.0, 1500.0)
    assert e1["transaction_id"] == e2["transaction_id"]


def test_make_billing_event_different_periods_give_different_ids():
    e1 = make_billing_event("C1", "electricity", "2016-01-01", 100.0, 1500.0)
    e2 = make_billing_event("C1", "electricity", "2016-02-01", 100.0, 1500.0)
    assert e1["transaction_id"] != e2["transaction_id"]


# --- build_ledger ---

def test_build_ledger_produces_events_for_each_record_and_bill():
    records = [_settlement_record(date="2016-01-01", period=1)]
    bills = [_bill(period_start="2016-01-01")]
    events = build_ledger(records, bills)
    types = [e["event_type"] for e in events]
    assert "settlement_event" in types
    assert "capital_charge_event" in types
    assert "billing_event" in types


def test_build_ledger_omits_capital_event_when_zero():
    records = [_settlement_record(capital=0.0)]
    bills = []
    events = build_ledger(records, bills)
    assert not any(e["event_type"] == "capital_charge_event" for e in events)


def test_build_ledger_infers_commodity_from_settlement_records():
    records = [_settlement_record(customer_id="C1g", commodity="gas")]
    bills = [_bill(customer_id="C1g")]
    events = build_ledger(records, bills)
    billing = [e for e in events if e["event_type"] == "billing_event"][0]
    assert billing["commodity"] == "gas"


def test_build_ledger_events_are_sorted_chronologically():
    records = [
        _settlement_record(date="2016-03-01", period=1),
        _settlement_record(date="2016-01-01", period=1),
    ]
    bills = [_bill(period_start="2016-02-01")]
    events = build_ledger(records, bills)
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)


# --- derive_pnl ---

def test_derive_pnl_matches_direct_calculation():
    records = [_settlement_record(revenue=10.0, wholesale=6.0, capital=0.5)]
    bills = [_bill(amount=10.0)]
    events = build_ledger(records, bills)
    pnl = derive_pnl(events)
    assert abs(pnl["revenue_gbp"] - 10.0) < 1e-9
    assert abs(pnl["wholesale_cost_gbp"] - 6.0) < 1e-9
    assert abs(pnl["capital_cost_gbp"] - 0.5) < 1e-9
    assert abs(pnl["gross_margin_gbp"] - 4.0) < 1e-9   # 10 - 6
    assert abs(pnl["net_margin_gbp"] - 3.5) < 1e-9     # 10 - 6 - 0.5


def test_derive_pnl_with_multiple_records_and_bills():
    records = [
        _settlement_record(date="2016-01-01", period=1, revenue=10.0, wholesale=6.0, capital=0.5),
        _settlement_record(date="2016-02-01", period=1, revenue=12.0, wholesale=7.0, capital=0.6),
    ]
    bills = [_bill(period_start="2016-01-01", amount=10.0), _bill(period_start="2016-02-01", amount=12.0)]
    pnl = derive_pnl(build_ledger(records, bills))
    assert abs(pnl["revenue_gbp"] - 22.0) < 1e-9
    assert abs(pnl["wholesale_cost_gbp"] - 13.0) < 1e-9
    assert abs(pnl["capital_cost_gbp"] - 1.1) < 1e-9


# --- derive_cash_position ---

def test_derive_cash_position_adds_net_to_starting():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(amount=10.0)]
    events = build_ledger(records, bills)
    ending = derive_cash_position(1000.0, events)
    # Net effect: +10 (billing) - 6 (wholesale) - 0.5 (capital) = +3.5
    assert abs(ending - 1003.5) < 1e-9


# --- ledger_summary ---

def test_ledger_summary_counts_event_types():
    records = [_settlement_record()]
    bills = [_bill()]
    events = build_ledger(records, bills)
    summary = ledger_summary(events)
    assert summary["by_type"]["settlement_event"] == 1
    assert summary["by_type"]["capital_charge_event"] == 1
    assert summary["by_type"]["billing_event"] == 1
    assert summary["event_count"] == 3


# --- Phase 7b: payment lifecycle events ---

class _FakePaymentBehaviour:
    """Duck-typed stand-in for saas.payment_behaviour."""
    CREDIT_RISK_BY_CUSTOMER = {"C1": "high", "C2": "low"}
    DEFAULT_CREDIT_RISK = "medium"

    @staticmethod
    def bad_debt_provision_gbp(credit_risk: str, revenue_gbp: float) -> float:
        rates = {"low": 0.005, "medium": 0.02, "high": 0.05, "vulnerable": 0.08}
        return revenue_gbp * rates.get(credit_risk, 0.02)

    @staticmethod
    def expected_payment_date(bill_period_end: str, credit_risk: str) -> str:
        from datetime import date, timedelta
        days = {"low": 5, "medium": 14, "high": 30, "vulnerable": 45}
        d = date.fromisoformat(bill_period_end) + timedelta(days=days.get(credit_risk, 14))
        return d.isoformat()


def test_make_payment_received_event_amount():
    bill = _bill(amount=100.0)
    e = make_payment_received_event(bill, 5.0, "2016-02-15")
    assert abs(e["amount_gbp"] - 95.0) < 1e-9
    assert e["event_type"] == "payment_received_event"
    assert e["timestamp"] == "2016-02-15"


def test_make_payment_received_event_zero_provision():
    bill = _bill(amount=100.0)
    e = make_payment_received_event(bill, 0.0, "2016-02-15")
    assert abs(e["amount_gbp"] - 100.0) < 1e-9


def test_make_bad_debt_event_amount_is_negative():
    bill = _bill(period_end="2016-01-31")
    e = make_bad_debt_event(bill, 5.0, "2016-02-15")
    assert abs(e["amount_gbp"] - (-5.0)) < 1e-9
    assert e["event_type"] == "bad_debt_event"


def test_make_bad_debt_event_timestamp_is_30d_after_payment_date():
    bill = _bill(period_end="2016-01-31")
    e = make_bad_debt_event(bill, 5.0, "2016-02-15")
    assert e["timestamp"] == "2016-03-16"  # 2016-02-15 + 30 days


def test_make_payment_received_event_id_is_deterministic():
    bill = _bill()
    e1 = make_payment_received_event(bill, 5.0, "2016-02-15")
    e2 = make_payment_received_event(bill, 5.0, "2016-02-15")
    assert e1["transaction_id"] == e2["transaction_id"]


def test_make_bad_debt_event_id_differs_from_payment_received():
    bill = _bill()
    p = make_payment_received_event(bill, 5.0, "2016-02-15")
    b = make_bad_debt_event(bill, 5.0, "2016-02-15")
    assert p["transaction_id"] != b["transaction_id"]


def test_build_ledger_with_payment_behaviour_adds_payment_events():
    records = [_settlement_record(date="2016-01-01", period=1)]
    bills = [_bill(customer_id="C1", period_end="2016-01-31", amount=100.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    types = [e["event_type"] for e in events]
    assert "payment_received_event" in types
    assert "bad_debt_event" in types


def test_build_ledger_no_bad_debt_event_when_zero_provision():
    records = [_settlement_record()]
    # C4 not in CREDIT_RISK_BY_CUSTOMER → falls back to "medium" (2% provision)
    # To get zero provision, use a customer with "low" segment but override amount to 0
    bills = [_bill(customer_id="C2", amount=0.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    assert not any(e["event_type"] == "bad_debt_event" for e in events)


def test_build_ledger_without_payment_behaviour_omits_payment_events():
    records = [_settlement_record()]
    bills = [_bill()]
    events = build_ledger(records, bills)
    assert not any(e["event_type"] == "payment_received_event" for e in events)
    assert not any(e["event_type"] == "bad_debt_event" for e in events)


def test_derive_pnl_with_payment_events_adds_cash_fields():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(customer_id="C1", period_end="2016-01-31", amount=100.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    pnl = derive_pnl(events)
    # C1 is "high" credit risk → 5% provision = £5 bad debt
    assert "cash_collected_gbp" in pnl
    assert "bad_debt_gbp" in pnl
    assert "cash_net_margin_gbp" in pnl
    assert abs(pnl["cash_collected_gbp"] - 95.0) < 1e-9   # 100 - 5
    assert abs(pnl["bad_debt_gbp"] - 5.0) < 1e-9
    # cash_net = 95 - 6 (wholesale) - 0.5 (capital) = 88.5
    assert abs(pnl["cash_net_margin_gbp"] - 88.5) < 1e-9


def test_derive_pnl_cash_net_margin_less_than_net_margin_when_bad_debt():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(customer_id="C1", period_end="2016-01-31", amount=100.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    pnl = derive_pnl(events)
    assert pnl["cash_net_margin_gbp"] < pnl["net_margin_gbp"]


def test_derive_pnl_without_payment_events_has_no_cash_fields():
    records = [_settlement_record()]
    bills = [_bill()]
    pnl = derive_pnl(build_ledger(records, bills))
    assert "cash_net_margin_gbp" not in pnl
    assert "cash_collected_gbp" not in pnl


def test_build_ledger_payment_events_sorted_after_billing_event():
    records = [_settlement_record(date="2016-01-01", period=1)]
    bills = [_bill(customer_id="C1", period_start="2016-01-01", period_end="2016-01-31", amount=100.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    billing_ts = next(e["timestamp"] for e in events if e["event_type"] == "billing_event")
    payment_ts = next(e["timestamp"] for e in events if e["event_type"] == "payment_received_event")
    assert payment_ts > billing_ts


def test_derive_cash_position_includes_payment_events():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    # With payment events: cash flow = -6 (wholesale) - 0.5 (capital) + 100 (billing)
    #   + 95 (payment received) - 5 (bad debt) = 183.5
    bills = [_bill(customer_id="C1", period_end="2016-01-31", amount=100.0)]
    pb = _FakePaymentBehaviour()
    events = build_ledger(records, bills, pb)
    ending = derive_cash_position(1000.0, events)
    assert abs(ending - 1183.5) < 1e-9


# ---- Phase 8a: acquisition_spend_event and fixed_cost_event ----

def test_make_acquisition_spend_event_amount_is_negative():
    event = make_acquisition_spend_event("C3", "2020-06-01", 150.0, False, "resi")
    assert event["amount_gbp"] == -150.0
    assert event["event_type"] == "acquisition_spend_event"
    assert event["acquisition_won"] is False


def test_make_acquisition_spend_event_won_flag():
    won = make_acquisition_spend_event("C3", "2020-06-01", 150.0, True, "resi")
    lost = make_acquisition_spend_event("C3", "2020-07-01", 150.0, False, "resi")
    assert won["acquisition_won"] is True
    assert lost["acquisition_won"] is False


def test_make_fixed_cost_event_amount_is_negative():
    event = make_fixed_cost_event("2020-01", 50.0)
    assert event["amount_gbp"] == -50.0
    assert event["event_type"] == "fixed_cost_event"
    assert event["month"] == "2020-01"


def test_make_fixed_cost_event_timestamp_is_first_of_month():
    event = make_fixed_cost_event("2020-03", 50.0)
    assert event["timestamp"] == "2020-03-01"


def test_build_ledger_with_extra_events_includes_them():
    records = [_settlement_record(date="2020-01-01")]
    bills = [_bill(period_start="2020-01-01", period_end="2020-01-31")]
    acq_event = make_acquisition_spend_event("C3", "2020-06-01", 150.0, False, "resi")
    fixed_event = make_fixed_cost_event("2020-01", 50.0)
    events = build_ledger(records, bills, extra_events=[acq_event, fixed_event])
    types = {e["event_type"] for e in events}
    assert "acquisition_spend_event" in types
    assert "fixed_cost_event" in types


def test_build_ledger_without_extra_events_unchanged():
    records = [_settlement_record()]
    bills = [_bill()]
    events = build_ledger(records, bills)
    types = {e["event_type"] for e in events}
    assert "acquisition_spend_event" not in types
    assert "fixed_cost_event" not in types


def test_derive_pnl_includes_acquisition_spend_when_present():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(amount=100.0)]
    acq_event = make_acquisition_spend_event("C3", "2020-06-01", 150.0, False, "resi")
    events = build_ledger(records, bills, extra_events=[acq_event])
    pnl = derive_pnl(events)
    assert "acquisition_spend_gbp" in pnl
    assert abs(pnl["acquisition_spend_gbp"] - 150.0) < 1e-6
    assert "operating_net_margin_gbp" in pnl


def test_derive_pnl_includes_fixed_cost_when_present():
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(amount=100.0)]
    fixed_event = make_fixed_cost_event("2016-01", 50.0)
    events = build_ledger(records, bills, extra_events=[fixed_event])
    pnl = derive_pnl(events)
    assert "fixed_cost_gbp" in pnl
    assert abs(pnl["fixed_cost_gbp"] - 50.0) < 1e-6
    assert "operating_net_margin_gbp" in pnl


def test_operating_net_margin_is_net_less_acquisition_and_fixed():
    records = [_settlement_record(revenue=100.0, wholesale=60.0, capital=5.0, net=35.0)]
    bills = [_bill(amount=100.0)]
    acq_event = make_acquisition_spend_event("C3", "2020-06-01", 150.0, False, "resi")
    fixed_event = make_fixed_cost_event("2016-01", 50.0)
    events = build_ledger(records, bills, extra_events=[acq_event, fixed_event])
    pnl = derive_pnl(events)
    # net_margin = revenue - wholesale - capital = 100 - 60 - 5 = 35
    # operating_net = 35 - 150 - 50 = -165
    assert abs(pnl["operating_net_margin_gbp"] - (pnl["net_margin_gbp"] - 150.0 - 50.0)) < 1e-6


# ---- Phase 9a: non_commodity_cost_event and vat_remittance_event ----

def test_make_non_commodity_cost_event_amount_is_negative():
    bill = _bill_9a(non_commodity=11.0)
    e = make_non_commodity_cost_event(bill)
    assert e["amount_gbp"] == pytest.approx(-11.0)
    assert e["event_type"] == "non_commodity_cost_event"


def test_make_non_commodity_cost_event_deterministic_id():
    bill = _bill_9a()
    e1 = make_non_commodity_cost_event(bill)
    e2 = make_non_commodity_cost_event(bill)
    assert e1["transaction_id"] == e2["transaction_id"]


def test_make_vat_remittance_event_amount_is_negative():
    bill = _bill_9a(vat=4.8)
    e = make_vat_remittance_event(bill)
    assert e["amount_gbp"] == pytest.approx(-4.8)
    assert e["event_type"] == "vat_remittance_event"


def test_make_vat_remittance_event_deterministic_id():
    bill = _bill_9a()
    e1 = make_vat_remittance_event(bill)
    e2 = make_vat_remittance_event(bill)
    assert e1["transaction_id"] == e2["transaction_id"]


def test_make_non_commodity_and_vat_events_have_different_ids():
    bill = _bill_9a()
    nc = make_non_commodity_cost_event(bill)
    vat = make_vat_remittance_event(bill)
    assert nc["transaction_id"] != vat["transaction_id"]


def test_build_ledger_phase9a_bill_generates_nc_and_vat_events():
    records = [_settlement_record(date="2016-01-01", period=1)]
    bills = [_bill_9a(period_start="2016-01-01")]
    events = build_ledger(records, bills)
    types = {e["event_type"] for e in events}
    assert "non_commodity_cost_event" in types
    assert "vat_remittance_event" in types


def test_build_ledger_pre9a_bill_omits_nc_and_vat_events():
    """Bills without non_commodity_amount_gbp / vat_gbp don't generate Phase 9a events."""
    records = [_settlement_record()]
    bills = [_bill()]  # no Phase 9a fields
    events = build_ledger(records, bills)
    types = {e["event_type"] for e in events}
    assert "non_commodity_cost_event" not in types
    assert "vat_remittance_event" not in types


def test_derive_pnl_phase9a_revenue_excludes_vat():
    """revenue_gbp = total_billed - vat (ex-VAT revenue)."""
    records = [_settlement_record(wholesale=60.0, capital=5.0)]
    # total_amount = 80 + 11 + 5 + 4.8 = 100.8; ex-VAT revenue = 100.8 - 4.8 = 96
    bills = [_bill_9a(commodity_amount=80.0, non_commodity=11.0, standing=5.0, vat=4.8)]
    events = build_ledger(records, bills)
    pnl = derive_pnl(events)
    # revenue = total_billed - vat = 100.8 - 4.8 = 96.0
    assert abs(pnl["revenue_gbp"] - 96.0) < 1e-9
    assert "total_billed_gbp" in pnl
    assert abs(pnl["total_billed_gbp"] - 100.8) < 1e-9
    assert abs(pnl["vat_remittance_gbp"] - 4.8) < 1e-9


def test_derive_pnl_phase9a_gross_margin_excludes_non_commodity():
    """gross_margin = revenue - wholesale - non_commodity (commodity + standing only)."""
    records = [_settlement_record(wholesale=60.0, capital=5.0)]
    bills = [_bill_9a(commodity_amount=80.0, non_commodity=11.0, standing=5.0, vat=4.8)]
    events = build_ledger(records, bills)
    pnl = derive_pnl(events)
    # revenue = 96.0, wholesale = 60, non_commodity = 11
    # gross = 96 - 60 - 11 = 25
    assert abs(pnl["gross_margin_gbp"] - 25.0) < 1e-9
    assert abs(pnl["non_commodity_cost_gbp"] - 11.0) < 1e-9


def test_derive_pnl_phase9a_backward_compatible_with_pre9a_bills():
    """Pre-Phase-9a bills (no non_commodity/vat fields) still produce correct P&L."""
    records = [_settlement_record(wholesale=6.0, capital=0.5)]
    bills = [_bill(amount=10.0)]
    pnl = derive_pnl(build_ledger(records, bills))
    # Behaviour unchanged: revenue=10, gross=4, net=3.5
    assert abs(pnl["revenue_gbp"] - 10.0) < 1e-9
    assert abs(pnl["gross_margin_gbp"] - 4.0) < 1e-9
    assert abs(pnl["net_margin_gbp"] - 3.5) < 1e-9
    assert "total_billed_gbp" not in pnl
    assert "vat_remittance_gbp" not in pnl


def test_make_retention_cost_event_structure():
    from saas.ledger import make_retention_cost_event
    ev = make_retention_cost_event("C1", "2021-06-30", 12.50, 0.45)
    assert ev["event_type"] == "retention_cost_event"
    assert ev["billing_account"] == "C1"
    assert ev["timestamp"] == "2021-06-30"
    assert abs(ev["company_churn_estimate"] - 0.45) < 1e-6
    assert abs(ev["amount_gbp"] - (-12.50)) < 1e-6


def test_make_retention_cost_event_amount_is_negative():
    from saas.ledger import make_retention_cost_event
    ev = make_retention_cost_event("C2", "2022-01-01", 50.0, 0.35)
    assert ev["amount_gbp"] < 0


def test_make_retention_cost_event_transaction_id_deterministic():
    from saas.ledger import make_retention_cost_event
    ev1 = make_retention_cost_event("C3", "2020-06-30", 25.0, 0.4)
    ev2 = make_retention_cost_event("C3", "2020-06-30", 25.0, 0.4)
    assert ev1["transaction_id"] == ev2["transaction_id"]


def test_make_retention_cost_event_different_customers_different_ids():
    from saas.ledger import make_retention_cost_event
    ev1 = make_retention_cost_event("C1", "2021-01-01", 10.0, 0.3)
    ev2 = make_retention_cost_event("C2", "2021-01-01", 10.0, 0.3)
    assert ev1["transaction_id"] != ev2["transaction_id"]
