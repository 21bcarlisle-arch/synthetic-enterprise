import pytest
"""Tests for company.finance.pnl."""

from company.finance.pnl import company_income_statement, reconcile_with_sim


def _event(event_type, amount):
    return {"event_type": event_type, "amount_gbp": amount}


def test_income_statement_uses_billing_when_no_payments():
    events = [
        _event("billing_event", 100.0),
        _event("settlement_event", -60.0),
        _event("capital_charge_event", -5.0),
    ]
    stmt = company_income_statement(events)
    assert stmt["revenue_basis"] == "accrual (billing_event)"
    assert abs(stmt["revenue_gbp"] - 100.0) < 1e-6
    assert abs(stmt["wholesale_cost_gbp"] - 60.0) < 1e-6
    assert abs(stmt["capital_cost_gbp"] - 5.0) < 1e-6
    assert abs(stmt["gross_margin_gbp"] - 40.0) < 1e-6


def test_income_statement_uses_payment_received_when_present():
    events = [
        _event("billing_event", 100.0),
        _event("payment_received_event", 95.0),
        _event("bad_debt_event", -5.0),
        _event("settlement_event", -60.0),
    ]
    stmt = company_income_statement(events)
    assert stmt["revenue_basis"] == "cash (payment_received_event)"
    assert abs(stmt["revenue_gbp"] - 95.0) < 1e-6
    assert abs(stmt["bad_debt_gbp"] - 5.0) < 1e-6


def test_income_statement_includes_phase8a_costs():
    events = [
        _event("billing_event", 100.0),
        _event("settlement_event", -60.0),
        _event("capital_charge_event", -5.0),
        _event("acquisition_spend_event", -150.0),
        _event("fixed_cost_event", -50.0),
    ]
    stmt = company_income_statement(events)
    assert abs(stmt["acquisition_spend_gbp"] - 150.0) < 1e-6
    assert abs(stmt["fixed_cost_gbp"] - 50.0) < 1e-6
    assert "operating_net_margin_gbp" not in stmt  # that's derive_pnl's field
    # net_margin = gross - capital - cts - acq - fixed = 40 - 5 - 0 - 150 - 50 = -165
    assert abs(stmt["net_margin_gbp"] - (100.0 - 60.0 - 5.0 - 150.0 - 50.0)) < 1e-6


def test_income_statement_with_cost_to_serve():
    events = [
        _event("billing_event", 100.0),
        _event("settlement_event", -60.0),
        _event("capital_charge_event", -5.0),
    ]
    stmt = company_income_statement(events, cost_to_serve_gbp=8.0)
    assert abs(stmt["cost_to_serve_gbp"] - 8.0) < 1e-6
    # net_margin = 40 - 5 - 8 = 27
    assert abs(stmt["net_margin_gbp"] - 27.0) < 1e-6


def test_net_margin_pct_present_when_positive_gross():
    events = [
        _event("billing_event", 100.0),
        _event("settlement_event", -60.0),
    ]
    stmt = company_income_statement(events)
    assert "net_margin_pct" in stmt


def test_reconcile_agrees_when_close():
    stmt = {"net_margin_gbp": 100.00}
    rec = reconcile_with_sim(stmt, 100.005)
    assert rec["agrees"] is True


def test_reconcile_disagrees_when_gap_exceeds_one_penny():
    stmt = {"net_margin_gbp": 100.00}
    rec = reconcile_with_sim(stmt, 100.02)
    assert rec["agrees"] is False
    assert "Gap" in rec["note"]


# --- Phase KD depth tests ---

def test_zero_events_zero_revenue():
    stmt = company_income_statement([])
    assert stmt['revenue_gbp'] == pytest.approx(0.0)
    assert stmt['gross_margin_gbp'] == pytest.approx(0.0)


def test_net_margin_negative_when_costs_exceed_revenue():
    events = [_event('billing_event', 100.0), _event('settlement_event', -200.0)]
    stmt = company_income_statement(events)
    assert stmt['net_margin_gbp'] < 0


def test_reconcile_gap_less_than_0_01_agrees():
    stmt = {'net_margin_gbp': 100.00}
    rec = reconcile_with_sim(stmt, 100.009)
    assert rec['agrees'] is True


def test_reconcile_exactly_0_01_disagrees():
    stmt = {'net_margin_gbp': 100.00}
    rec = reconcile_with_sim(stmt, 100.01)
    assert rec['agrees'] is False


def test_cost_to_serve_included_in_total_operating():
    events = [_event('billing_event', 100.0), _event('settlement_event', -60.0)]
    stmt = company_income_statement(events, cost_to_serve_gbp=15.0)
    assert stmt['total_operating_costs_gbp'] == pytest.approx(15.0)


def test_net_revenue_cash_basis_subtracts_bad_debt():
    events = [
        _event('payment_received_event', 90.0),
        _event('bad_debt_event', -10.0),
        _event('settlement_event', -60.0),
    ]
    stmt = company_income_statement(events)
    assert stmt['net_revenue_gbp'] == pytest.approx(80.0)


def test_net_revenue_accrual_basis_equals_revenue():
    events = [_event('billing_event', 100.0), _event('settlement_event', -60.0)]
    stmt = company_income_statement(events)
    assert stmt['net_revenue_gbp'] == pytest.approx(100.0)


def test_gross_margin_formula():
    events = [_event('billing_event', 100.0), _event('settlement_event', -60.0)]
    stmt = company_income_statement(events)
    assert stmt['gross_margin_gbp'] == pytest.approx(40.0)


def test_acquisition_spend_positive():
    events = [_event('billing_event', 100.0), _event('acquisition_spend_event', -50.0)]
    stmt = company_income_statement(events)
    assert stmt['acquisition_spend_gbp'] == pytest.approx(50.0)


def test_net_margin_pct_absent_when_zero_gross():
    events = [_event('billing_event', 100.0), _event('settlement_event', -100.0)]
    stmt = company_income_statement(events)
    assert 'net_margin_pct' not in stmt
