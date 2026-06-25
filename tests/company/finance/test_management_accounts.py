"""Tests for company/finance/management_accounts.py -- Phase 64 / FI1."""
import pytest
from company.finance.management_accounts import (
    annual_management_pack,
    build_monthly_accounts,
    cross_check,
)
from company.finance.double_entry import build_journal, trial_balance


def _bill(cid, amount, date):
    return {"transaction_id": f"bill-{cid}-{date}", "event_type": "billing_event",
            "timestamp": date, "customer_id": cid, "amount_gbp": amount}


def _settle(cid, amount, date):
    return {"transaction_id": f"settle-{cid}-{date}", "event_type": "settlement_event",
            "timestamp": date, "customer_id": cid, "amount_gbp": -abs(amount)}


def _bad_debt(cid, amount, date):
    return {"transaction_id": f"bd-{cid}-{date}", "event_type": "bad_debt_event",
            "timestamp": date, "customer_id": cid, "amount_gbp": -abs(amount)}


def _all_event_types():
    """One event of every recognised type for trial balance checks."""
    return [
        {"transaction_id": "b1", "event_type": "billing_event", "timestamp": "2022-01-01",
         "customer_id": "C1", "amount_gbp": 120.0},
        {"transaction_id": "v1", "event_type": "vat_remittance_event", "timestamp": "2022-01-01",
         "customer_id": "C1", "amount_gbp": -20.0},
        {"transaction_id": "nc1", "event_type": "non_commodity_cost_event", "timestamp": "2022-01-01",
         "customer_id": "C1", "amount_gbp": -10.0},
        {"transaction_id": "s1", "event_type": "settlement_event", "timestamp": "2022-01-01",
         "customer_id": "C1", "amount_gbp": -60.0},
        {"transaction_id": "cc1", "event_type": "capital_charge_event", "timestamp": "2022-01-01",
         "customer_id": "C1", "amount_gbp": -5.0},
        {"transaction_id": "pmt1", "event_type": "payment_received_event", "timestamp": "2022-02-01",
         "customer_id": "C1", "amount_gbp": 120.0},
        {"transaction_id": "bd1", "event_type": "bad_debt_event", "timestamp": "2022-03-01",
         "customer_id": "C2", "amount_gbp": -15.0},
        {"transaction_id": "acq1", "event_type": "acquisition_spend_event", "timestamp": "2022-01-01",
         "customer_id": "C3", "amount_gbp": -8.0},
        {"transaction_id": "fc1", "event_type": "fixed_cost_event", "timestamp": "2022-01-31",
         "customer_id": "", "month": "2022-01", "amount_gbp": -500.0},
    ]


def test_journal_from_real_events_trial_balance():
    """Trial balance holds for all recognised event types (mathematical property)."""
    events = _all_event_types()
    journal = build_journal(events, opening_treasury=1000.0)
    tb = trial_balance(journal)
    assert tb["balanced"]
    assert abs(tb["discrepancy_gbp"]) < 0.01


def test_income_statement_net_matches_ledger_pnl():
    """cross_check passes when journal net matches ledger net within 5%."""
    events = [
        _bill("C1", 1000.0, "2022-01-15"),
        _settle("C1", 600.0, "2022-01-15"),
    ]
    pack = annual_management_pack(events)
    journal_net = pack["2022"]["income_statement"]["net_margin_gbp"]
    result = cross_check(journal_net, ledger_net=400.0)
    assert result["pass"]
    assert abs(result["abs_diff_gbp"]) < 0.01


def test_balance_sheet_equation_each_year():
    """Assets = Liabilities + Equity holds for the cumulative balance sheet each year."""
    events = [
        _bill("C1", 500.0, "2021-06-01"),
        _settle("C1", 300.0, "2021-06-01"),
        _bill("C1", 600.0, "2022-06-01"),
        _settle("C1", 350.0, "2022-06-01"),
    ]
    pack = annual_management_pack(events, opening_treasury=2000.0)
    for year, data in pack.items():
        bs = data["balance_sheet"]
        assert bs["equation_holds"], f"Balance sheet unbalanced in {year}: {bs}"


def test_monthly_accounts_12_months():
    """build_monthly_accounts returns entries for every month that has events."""
    months = [f"2023-{m:02d}-15" for m in range(1, 13)]
    events = [_bill("C1", 100.0, d) for d in months]
    result = build_monthly_accounts(events)
    assert "2023" in result
    assert len(result["2023"]) == 12
    for m in [f"{m:02d}" for m in range(1, 13)]:
        assert m in result["2023"]


def test_revenue_equals_billing_account_4001():
    """Billing events go to 4001 (revenue) credit; income_statement revenue matches."""
    events = [
        _bill("C1", 300.0, "2022-01-01"),
        _bill("C2", 200.0, "2022-02-01"),
    ]
    pack = annual_management_pack(events)
    revenue = pack["2022"]["income_statement"]["revenue_gbp"]
    assert abs(revenue - 500.0) < 0.01


def test_wholesale_cost_in_cogs_5001():
    """Settlement events go to 5001 (wholesale cost); income_statement wholesale matches."""
    events = [
        _bill("C1", 1000.0, "2022-06-01"),
        _settle("C1", 750.0, "2022-06-01"),
    ]
    pack = annual_management_pack(events)
    wholesale = pack["2022"]["income_statement"]["wholesale_cost_gbp"]
    assert abs(wholesale - 750.0) < 0.01


def test_bad_debt_to_6001():
    """bad_debt_event goes to 6001 (bad debt expense); appears in opex."""
    events = [
        _bill("C1", 500.0, "2022-01-01"),
        _bad_debt("C1", 50.0, "2022-03-01"),
    ]
    pack = annual_management_pack(events)
    bad_debt = pack["2022"]["income_statement"]["bad_debt_gbp"]
    assert abs(bad_debt - 50.0) < 0.01


def test_opening_treasury_in_equity_3001():
    """Opening treasury posted as DR 1001 / CR 3001 equity entry."""
    events = [_bill("C1", 100.0, "2022-01-01")]
    pack = annual_management_pack(events, opening_treasury=5000.0)
    bs = pack["2022"]["balance_sheet"]
    assert abs(bs["opening_capital_gbp"] - 5000.0) < 0.01


def test_management_accounts_section_in_report():
    """_section_management_accounts renders a section heading."""
    from saas.reporting.annual_report import _section_management_accounts
    events = [_bill("C1", 1000.0, "2022-01-01"), _settle("C1", 600.0, "2022-01-01")]
    pack = annual_management_pack(events)
    section = _section_management_accounts({"management_accounts": pack, "total_net_gbp": 400.0})
    assert "## Management Accounts" in section
    assert "2022" in section


def test_cross_check_passes_on_consistent_data():
    """cross_check returns pass=True when values agree within tolerance."""
    result = cross_check(journal_net=1000.0, ledger_net=1020.0)
    assert result["pass"]
    assert result["variance_pct"] < 5.0


def test_cross_check_fails_when_outside_tolerance():
    """cross_check returns pass=False when variance exceeds tolerance."""
    result = cross_check(journal_net=800.0, ledger_net=1000.0)
    assert not result["pass"]
    assert result["variance_pct"] > 5.0


def test_retained_earnings_cumulative():
    """3900 balance should be zero (no explicit retained earnings postings);
    cumulative P&L is in current_period_profit on the balance sheet."""
    events = [
        _bill("C1", 400.0, "2020-01-01"),
        _settle("C1", 200.0, "2020-01-01"),
        _bill("C1", 500.0, "2021-01-01"),
        _settle("C1", 300.0, "2021-01-01"),
    ]
    pack = annual_management_pack(events)
    bs_2021 = pack["2021"]["balance_sheet"]
    # cumulative net = (400-200) + (500-300) = 400
    assert abs(bs_2021["current_period_profit_gbp"] - 400.0) < 0.01
    assert bs_2021["equation_holds"]


def test_management_accounts_handles_empty_events():
    """Empty events list returns empty dicts without error."""
    assert build_monthly_accounts([]) == {}
    assert annual_management_pack([]) == {}
    assert annual_management_pack([], opening_treasury=1000.0) == {}
