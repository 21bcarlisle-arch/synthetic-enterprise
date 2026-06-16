"""Tests for saas/ledger.py — Phase 7a transaction log."""
import pytest

from saas.ledger import (
    build_ledger,
    derive_cash_position,
    derive_pnl,
    ledger_summary,
    make_billing_event,
    make_capital_charge_event,
    make_settlement_event,
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
