"""Tests for company/finance/double_entry.py — F1 double-entry ledger."""

import pytest
from company.finance.double_entry import (
    ACCOUNTS,
    account_balances,
    balance_sheet,
    build_journal,
    income_statement,
    to_journal_entry,
    trial_balance,
)
from saas import ledger as ledger_module


# ---------------------------------------------------------------------------
# Helpers — minimal synthetic events
# ---------------------------------------------------------------------------

def _billing(cid="C1", amount=120.0, period="2022-01-01"):
    return {
        "transaction_id": f"bill-{cid}-{period}",
        "event_type": "billing_event",
        "timestamp": period,
        "customer_id": cid,
        "amount_gbp": amount,
    }


def _settlement(cid="C1", amount=80.0, date="2022-01-01", period=1):
    return {
        "transaction_id": f"settle-{cid}-{date}-{period}",
        "event_type": "settlement_event",
        "timestamp": date,
        "customer_id": cid,
        "settlement_period": period,
        "amount_gbp": -amount,
    }


def _payment(cid="C1", amount=120.0, date="2022-02-01"):
    return {
        "transaction_id": f"pmt-{cid}-{date}",
        "event_type": "payment_received_event",
        "timestamp": date,
        "customer_id": cid,
        "amount_gbp": amount,
    }


def _vat(cid="C1", amount=20.0, date="2022-01-01"):
    return {
        "transaction_id": f"vat-{cid}-{date}",
        "event_type": "vat_remittance_event",
        "timestamp": date,
        "customer_id": cid,
        "amount_gbp": -amount,
    }


def _non_commodity(cid="C1", amount=10.0, date="2022-01-01"):
    return {
        "transaction_id": f"nc-{cid}-{date}",
        "event_type": "non_commodity_cost_event",
        "timestamp": date,
        "customer_id": cid,
        "amount_gbp": -amount,
    }


def _bad_debt(cid="C1", amount=5.0, date="2022-03-01"):
    return {
        "transaction_id": f"bd-{cid}-{date}",
        "event_type": "bad_debt_event",
        "timestamp": date,
        "customer_id": cid,
        "amount_gbp": -amount,
    }


def _capital(cid="C1", amount=2.0, date="2022-01-01", period=1):
    return {
        "transaction_id": f"cap-{cid}-{date}-{period}",
        "event_type": "capital_charge_event",
        "timestamp": date,
        "customer_id": cid,
        "settlement_period": period,
        "amount_gbp": -amount,
    }


def _fixed(month="2022-01", amount=1000.0):
    return {
        "transaction_id": f"fixed-{month}",
        "event_type": "fixed_cost_event",
        "timestamp": f"{month}-01",
        "month": month,
        "amount_gbp": -amount,
    }


def _acq(acct="C1", amount=50.0, date="2022-01-15", won=True):
    return {
        "transaction_id": f"acq-{acct}-{date}",
        "event_type": "acquisition_spend_event",
        "timestamp": date,
        "billing_account": acct,
        "amount_gbp": -amount,
        "acquisition_won": won,
    }


def _cts(month="2022-01", amount=250.0):
    return {
        "transaction_id": f"cts-{month}",
        "event_type": "cost_to_serve_event",
        "timestamp": f"{month}-01",
        "month": month,
        "amount_gbp": -amount,
    }


# ---------------------------------------------------------------------------
# Chart of accounts
# ---------------------------------------------------------------------------

def test_all_account_codes_have_required_fields():
    for code, info in ACCOUNTS.items():
        assert "name" in info, f"Account {code} missing name"
        assert "type" in info, f"Account {code} missing type"
        assert info["type"] in ("asset", "liability", "equity", "income", "expense")


def test_account_codes_follow_range_convention():
    for code, info in ACCOUNTS.items():
        prefix = int(code[0])
        if info["type"] == "asset":
            assert prefix == 1
        elif info["type"] == "liability":
            assert prefix == 2
        elif info["type"] == "equity":
            assert prefix == 3
        elif info["type"] == "income":
            assert prefix == 4
        elif info["type"] == "expense":
            assert prefix in (5, 6, 7)


# ---------------------------------------------------------------------------
# to_journal_entry
# ---------------------------------------------------------------------------

def test_billing_event_dr_receivables_cr_revenue():
    je = to_journal_entry(_billing(amount=120.0))
    assert je["debit_account"] == "1100"
    assert je["credit_account"] == "4001"
    assert je["amount_gbp"] == pytest.approx(120.0)


def test_settlement_event_dr_wholesale_cr_cash():
    je = to_journal_entry(_settlement(amount=80.0))
    assert je["debit_account"] == "5001"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(80.0)


def test_payment_received_dr_cash_cr_receivables():
    je = to_journal_entry(_payment(amount=120.0))
    assert je["debit_account"] == "1001"
    assert je["credit_account"] == "1100"
    assert je["amount_gbp"] == pytest.approx(120.0)


def test_vat_remittance_dr_revenue_cr_cash():
    je = to_journal_entry(_vat(amount=20.0))
    assert je["debit_account"] == "4001"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(20.0)


def test_non_commodity_dr_expense_cr_cash():
    je = to_journal_entry(_non_commodity(amount=10.0))
    assert je["debit_account"] == "5100"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(10.0)


def test_bad_debt_dr_expense_cr_receivables():
    je = to_journal_entry(_bad_debt(amount=5.0))
    assert je["debit_account"] == "6001"
    assert je["credit_account"] == "1100"
    assert je["amount_gbp"] == pytest.approx(5.0)


def test_capital_charge_dr_expense_cr_cash():
    je = to_journal_entry(_capital(amount=2.0))
    assert je["debit_account"] == "5200"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(2.0)


def test_fixed_cost_dr_overheads_cr_cash():
    je = to_journal_entry(_fixed(amount=1000.0))
    assert je["debit_account"] == "6200"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(1000.0)


def test_cost_to_serve_dr_cts_cr_cash():
    """CTS reconciliation fix (NEXT_PHASE.md option B): account 6100 must
    actually receive postings, distinct from 6200 (fixed_cost_event)."""
    je = to_journal_entry(_cts(amount=250.0))
    assert je["debit_account"] == "6100"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(250.0)


def test_acquisition_spend_dr_acq_cr_cash():
    je = to_journal_entry(_acq(amount=50.0))
    assert je["debit_account"] == "6300"
    assert je["credit_account"] == "1001"
    assert je["amount_gbp"] == pytest.approx(50.0)


def test_unknown_event_type_returns_none():
    event = {"transaction_id": "x", "event_type": "future_event_v99", "amount_gbp": 10.0, "timestamp": "2022-01-01"}
    assert to_journal_entry(event) is None


# ---------------------------------------------------------------------------
# build_journal
# ---------------------------------------------------------------------------

def test_opening_treasury_prepended_as_dr_cash_cr_equity():
    journal = build_journal([], opening_treasury=5000.0)
    assert len(journal) == 1
    je = journal[0]
    assert je["debit_account"] == "1001"
    assert je["credit_account"] == "3001"
    assert je["amount_gbp"] == pytest.approx(5000.0)


def test_build_journal_skips_unknown_events():
    events = [
        _billing(amount=100.0),
        {"transaction_id": "x", "event_type": "mystery_event", "amount_gbp": 0.0, "timestamp": "2022-01-01"},
        _settlement(amount=60.0),
    ]
    journal = build_journal(events)
    assert len(journal) == 2


# ---------------------------------------------------------------------------
# Trial balance — sum of all DR = sum of all CR
# ---------------------------------------------------------------------------

def test_trial_balance_balances_for_simple_set():
    events = [_billing(amount=120.0), _settlement(amount=80.0)]
    journal = build_journal(events, opening_treasury=1000.0)
    tb = trial_balance(journal)
    assert tb["balanced"] is True
    assert abs(tb["discrepancy_gbp"]) < 0.01


def test_trial_balance_balances_for_full_lifecycle():
    events = [
        _billing(amount=120.0),
        _vat(amount=20.0),
        _non_commodity(amount=10.0),
        _settlement(amount=70.0),
        _capital(amount=3.0),
        _payment(amount=120.0),
        _bad_debt(amount=5.0),
        _fixed(amount=500.0),
        _acq(amount=25.0),
    ]
    journal = build_journal(events, opening_treasury=2000.0)
    tb = trial_balance(journal)
    assert tb["balanced"] is True


# ---------------------------------------------------------------------------
# income_statement — must agree with saas.ledger.derive_pnl()
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Corporation Tax (2026-07-10, E1_ledger_double_entry -- docs/design/
# E1_CORPORATION_TAX_FINDING.md) -- strictly additive: year=None (the default,
# and every pre-existing call site) must leave net_margin_gbp and every other
# field byte-for-byte unchanged, with the three new fields all None.
# ---------------------------------------------------------------------------

from company.finance.double_entry import uk_corporation_tax_gbp


def test_income_statement_without_year_leaves_new_fields_none():
    events = [_billing(amount=120.0), _vat(amount=20.0)]
    journal = build_journal(events)
    stmt = income_statement(journal)
    assert stmt["profit_before_tax_gbp"] is None
    assert stmt["corporation_tax_gbp"] is None
    assert stmt["profit_for_year_gbp"] is None


def test_income_statement_without_year_net_margin_unchanged():
    """The pre-existing field's value must be identical whether or not `year`
    is passed -- this is an additive change, not a redefinition."""
    events = [
        _billing(amount=120.0), _vat(amount=20.0), _non_commodity(amount=10.0),
        _settlement(amount=70.0), _capital(amount=3.0),
    ]
    journal = build_journal(events)
    without_year = income_statement(journal)
    with_year = income_statement(journal, year=2024)
    assert without_year["net_margin_gbp"] == with_year["net_margin_gbp"]
    assert without_year["gross_margin_gbp"] == with_year["gross_margin_gbp"]


def test_income_statement_with_year_computes_tax_triplet():
    events = [
        _billing(amount=1_000_000.0), _vat(amount=100_000.0),
        _non_commodity(amount=50_000.0), _settlement(amount=400_000.0),
    ]
    journal = build_journal(events)
    stmt = income_statement(journal, year=2024)
    assert stmt["profit_before_tax_gbp"] == pytest.approx(stmt["net_margin_gbp"])
    assert stmt["corporation_tax_gbp"] > 0
    assert stmt["profit_for_year_gbp"] == pytest.approx(
        stmt["profit_before_tax_gbp"] - stmt["corporation_tax_gbp"]
    )


def test_uk_corporation_tax_zero_for_a_loss():
    assert uk_corporation_tax_gbp(-10_000.0, 2024) == 0.0
    assert uk_corporation_tax_gbp(0.0, 2024) == 0.0


def test_uk_corporation_tax_flat_19pct_before_2023():
    assert uk_corporation_tax_gbp(1_000_000.0, 2016) == pytest.approx(190_000.0)
    assert uk_corporation_tax_gbp(1_000_000.0, 2022) == pytest.approx(190_000.0)


def test_uk_corporation_tax_small_profits_rate_2023_onward():
    assert uk_corporation_tax_gbp(50_000.0, 2023) == pytest.approx(9_500.0)  # 19%
    assert uk_corporation_tax_gbp(30_000.0, 2024) == pytest.approx(5_700.0)  # 19%


def test_uk_corporation_tax_main_rate_at_and_above_threshold():
    assert uk_corporation_tax_gbp(250_000.0, 2023) == pytest.approx(62_500.0)  # 25%
    assert uk_corporation_tax_gbp(1_000_000.0, 2024) == pytest.approx(250_000.0)  # 25%


def test_uk_corporation_tax_marginal_relief_is_continuous_at_both_thresholds():
    """The marginal-relief formula must produce EXACTLY 19% at GBP 50k and
    EXACTLY 25% at GBP 250k -- no discontinuity at either boundary."""
    tax_at_50k = uk_corporation_tax_gbp(50_000.0, 2024)
    tax_at_250k = uk_corporation_tax_gbp(250_000.0, 2024)
    assert tax_at_50k / 50_000.0 == pytest.approx(0.19)
    assert tax_at_250k / 250_000.0 == pytest.approx(0.25)


def test_uk_corporation_tax_marginal_relief_midpoint():
    # Real HMRC-published example: GBP 150,000 profit (2023 rates) -> effective
    # rate roughly 22% (marginal relief blends between 19% and 25%).
    tax = uk_corporation_tax_gbp(150_000.0, 2023)
    effective_rate = tax / 150_000.0
    assert 0.19 < effective_rate < 0.25
    assert tax == pytest.approx(150_000.0 * 0.25 - (250_000.0 - 150_000.0) * 3 / 200)


def test_annual_management_pack_income_statement_carries_tax_triplet():
    """End-to-end: annual_management_pack() (the real call site) must thread
    the year through and produce the tax triplet, without altering
    net_margin_gbp."""
    from company.finance.management_accounts import annual_management_pack
    events = [
        _billing(amount=1_000_000.0, period="2024-01-01"),
        _vat(amount=100_000.0, date="2024-01-01"),
        _settlement(amount=300_000.0, date="2024-01-01"),
    ]
    pack = annual_management_pack(events, opening_treasury=0.0)
    stmt = pack["2024"]["income_statement"]
    assert stmt["corporation_tax_gbp"] is not None
    assert stmt["profit_for_year_gbp"] == pytest.approx(
        stmt["net_margin_gbp"] - stmt["corporation_tax_gbp"]
    )


def test_income_statement_revenue_net_of_vat():
    events = [_billing(amount=120.0), _vat(amount=20.0)]
    journal = build_journal(events)
    stmt = income_statement(journal)
    # Revenue account = billing (120 CR) - vat (20 DR) = 100
    assert stmt["revenue_gbp"] == pytest.approx(100.0)


def test_income_statement_gross_margin():
    events = [
        _billing(amount=120.0),
        _vat(amount=20.0),
        _non_commodity(amount=10.0),
        _settlement(amount=70.0),
    ]
    journal = build_journal(events)
    stmt = income_statement(journal)
    # Revenue = 120 - 20 = 100; COGS = 70 (wholesale) + 10 (nc) = 80; Gross = 20
    assert stmt["gross_margin_gbp"] == pytest.approx(20.0)


def test_income_statement_matches_saas_derive_pnl():
    events = [
        _billing(amount=120.0),
        _vat(amount=20.0),
        _non_commodity(amount=10.0),
        _settlement(amount=70.0),
        _capital(amount=3.0),
        _payment(amount=115.0),
        _bad_debt(amount=5.0),
    ]
    journal = build_journal(events)
    stmt = income_statement(journal)
    old_pnl = ledger_module.derive_pnl(events)

    assert stmt["revenue_gbp"] == pytest.approx(old_pnl["revenue_gbp"])
    assert stmt["wholesale_cost_gbp"] == pytest.approx(old_pnl["wholesale_cost_gbp"])
    assert stmt["gross_margin_gbp"] == pytest.approx(old_pnl["gross_margin_gbp"])
    assert stmt["capital_cost_gbp"] == pytest.approx(old_pnl["capital_cost_gbp"])


# ---------------------------------------------------------------------------
# balance_sheet — Assets = Liabilities + Equity
# ---------------------------------------------------------------------------

def test_balance_sheet_equation_holds_simple():
    events = [_billing(amount=120.0), _settlement(amount=80.0)]
    journal = build_journal(events, opening_treasury=1000.0)
    bs = balance_sheet(journal)
    assert bs["equation_holds"] is True


def test_balance_sheet_equation_holds_full_lifecycle():
    events = [
        _billing(amount=120.0),
        _vat(amount=20.0),
        _non_commodity(amount=10.0),
        _settlement(amount=70.0),
        _capital(amount=3.0),
        _payment(amount=120.0),
        _fixed(amount=500.0),
        _acq(amount=25.0),
    ]
    journal = build_journal(events, opening_treasury=2000.0)
    bs = balance_sheet(journal)
    assert bs["equation_holds"] is True


def test_balance_sheet_cash_reflects_net_flows():
    # Opening 1000, settlement pays 80 out, payment receives 120 in → Cash = 1040
    events = [_billing(amount=120.0), _settlement(amount=80.0), _payment(amount=120.0)]
    journal = build_journal(events, opening_treasury=1000.0)
    bs = balance_sheet(journal)
    assert bs["cash_gbp"] == pytest.approx(1000.0 - 80.0 + 120.0)


def test_balance_sheet_receivables_clear_on_payment():
    events = [_billing(amount=100.0), _payment(amount=100.0)]
    journal = build_journal(events)
    bs = balance_sheet(journal)
    assert bs["trade_receivables_gbp"] == pytest.approx(0.0)


def test_balance_sheet_receivables_reduced_by_bad_debt():
    events = [_billing(amount=100.0), _bad_debt(amount=5.0)]
    journal = build_journal(events)
    bs = balance_sheet(journal)
    assert bs["trade_receivables_gbp"] == pytest.approx(95.0)
