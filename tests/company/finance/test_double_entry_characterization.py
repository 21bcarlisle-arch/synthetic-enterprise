"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/finance/double_entry.py — the double-entry journal the trial
balance, P&L and balance sheet all emerge from, plus the UK corporation tax
calculation. Everything the board sees as a financial statement comes through here.

All inputs are fixed and explicit; no randomness and no wall-clock reads.
"""
from __future__ import annotations

import pytest

from company.finance.double_entry import (
    ACCOUNTS,
    account_balances,
    balance_sheet,
    balance_sheet_with_held_credit,
    build_journal,
    held_credit_journal_entries,
    income_statement,
    to_journal_entry,
    trial_balance,
    uk_corporation_tax_gbp,
)


def event(event_type, amount, tid, ts="2024-01-01", cid="C1", **kw):
    return {
        "event_type": event_type,
        "amount_gbp": amount,
        "transaction_id": tid,
        "timestamp": ts,
        "customer_id": cid,
        **kw,
    }


def je(debit, credit, amount, entry_id="e1"):
    """A raw journal entry, bypassing to_journal_entry."""
    return {
        "entry_id": entry_id,
        "timestamp": "2024-01-01",
        "debit_account": debit,
        "credit_account": credit,
        "amount_gbp": amount,
        "description": "",
        "source_event_type": "manual",
    }


# A fixed five-event trading history reused across the statement tests.
FIVE_EVENTS = [
    event("billing_event", 1000.0, "t1", "2024-01-01"),
    event("payment_received_event", 800.0, "t2", "2024-02-01"),
    event("settlement_event", 400.0, "t3", "2024-02-02", cid="WHOLESALE"),
    event("vat_remittance_event", 50.0, "t4", "2024-03-01", cid="HMRC"),
    event("bad_debt_event", 100.0, "t5", "2024-03-05", cid="C2"),
]


# ---------------------------------------------------------------------------
# to_journal_entry: the event -> DR/CR mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "event_type,debit,credit",
    [
        ("billing_event", "1100", "4001"),
        ("vat_remittance_event", "4001", "1001"),
        ("non_commodity_cost_event", "5100", "1001"),
        ("settlement_event", "5001", "1001"),
        ("capital_charge_event", "5200", "1001"),
        ("payment_received_event", "1001", "1100"),
        ("bad_debt_event", "6001", "1100"),
        ("acquisition_spend_event", "6300", "1001"),
        ("retention_cost_event", "6300", "1001"),
        ("fixed_cost_event", "6200", "1001"),
        ("cost_to_serve_event", "6100", "1001"),
    ],
)
def test_event_type_maps_to_fixed_account_pair(event_type, debit, credit):
    entry = to_journal_entry(event(event_type, 100.0, "t1"))
    assert (entry["debit_account"], entry["credit_account"]) == (debit, credit)
    assert entry["amount_gbp"] == 100.0
    assert entry["source_event_type"] == event_type


def test_vat_remittance_debits_revenue_so_it_reduces_reported_revenue():
    """VAT collected sits inside billing revenue, so remitting it to HMRC is booked
    as a DEBIT to Revenue (4001) rather than to a VAT liability. Net effect:
    reported revenue is net of remitted VAT."""
    journal = build_journal([
        event("billing_event", 1000.0, "t1"),
        event("vat_remittance_event", 50.0, "t2", cid="HMRC"),
    ])
    assert income_statement(journal)["revenue_gbp"] == 950.0


def test_unrecognised_event_type_returns_none_and_is_skipped_silently():
    assert to_journal_entry(event("mystery_event", 10.0, "t1")) is None
    # build_journal drops it with no error and no record that anything was dropped.
    assert build_journal([event("mystery_event", 10.0, "t1")]) == []


def test_negative_amount_is_absolutised_flipping_a_credit_note_into_revenue():
    """SURPRISE (sign class, money-relevant): to_journal_entry takes abs() of the
    amount. A billing_event of -£250 — the natural shape of a credit note or a
    rebill reversal — is booked as a POSITIVE £250 DR Receivables / CR Revenue,
    i.e. it INCREASES revenue and receivables instead of reducing them. The sign
    is discarded silently, so a reversal is indistinguishable from a fresh bill."""
    entry = to_journal_entry(event("billing_event", -250.0, "t1"))
    assert entry["amount_gbp"] == 250.0
    assert (entry["debit_account"], entry["credit_account"]) == ("1100", "4001")


def test_missing_transaction_id_falls_back_to_an_unknown_marker():
    entry = to_journal_entry({"event_type": "billing_event", "amount_gbp": 10.0})
    assert entry["entry_id"] == "unknown:billing_event"
    assert entry["timestamp"] == ""


def test_customer_id_falls_back_to_billing_account_then_empty():
    e = {"event_type": "billing_event", "amount_gbp": 10.0, "billing_account": "BA9"}
    assert "BA9" in to_journal_entry(e)["description"]
    e2 = {"event_type": "billing_event", "amount_gbp": 10.0}
    assert to_journal_entry(e2)["description"] == "Customer billed: "


# ---------------------------------------------------------------------------
# build_journal
# ---------------------------------------------------------------------------


def test_opening_treasury_prepends_a_capital_entry():
    journal = build_journal([event("billing_event", 100.0, "t1")], opening_treasury=5000.0)
    assert journal[0]["entry_id"] == "opening-treasury"
    assert (journal[0]["debit_account"], journal[0]["credit_account"]) == ("1001", "3001")
    assert journal[0]["timestamp"] == "0000-00-00"  # sentinel, not a real date


def test_zero_opening_treasury_prepends_nothing():
    # Guarded by a truthiness test, so 0.0 (and 0) produce no opening entry.
    assert len(build_journal([event("billing_event", 100.0, "t1")], opening_treasury=0.0)) == 1


# ---------------------------------------------------------------------------
# account_balances
# ---------------------------------------------------------------------------


def test_account_balances_nets_by_account_normal_balance_side():
    journal = build_journal(FIVE_EVENTS)
    b = account_balances(journal)
    assert b["4001"]["net"] == 950.0    # income: cr - dr = 1000 - 50
    assert b["1100"]["net"] == 100.0    # asset: dr - cr = 1000 - 800 - 100
    assert b["1001"]["net"] == 350.0    # asset: 800 - 50 - 400
    assert b["6001"]["net"] == 100.0    # expense: dr - cr


def test_account_balances_treats_an_unknown_code_as_credit_normal():
    """An account code absent from ACCOUNTS gets type "" and so falls into the
    else-branch: net = cr - dr, the CREDIT-normal treatment. An unmapped asset
    would therefore net with the wrong sign."""
    b = account_balances([je("9999", "8888", 100.0)])
    assert "9999" not in ACCOUNTS and "8888" not in ACCOUNTS
    assert b["9999"]["net"] == -100.0  # debited 100, reported as -100
    assert b["8888"]["net"] == 100.0


# ---------------------------------------------------------------------------
# trial_balance — WAS an R15 TAUTOLOGY (`balanced` could not be False); FIXED.
# The cases below are now the MUTATION PROOF that the control fires.
# ---------------------------------------------------------------------------


def test_trial_balance_of_a_correct_journal_balances():
    tb = trial_balance(build_journal(FIVE_EVENTS, opening_treasury=5000.0))
    assert tb["balanced"] is True
    assert tb["discrepancy_gbp"] == 0.0
    assert tb["violations"] == []


def test_an_empty_journal_balances_and_is_not_a_violation():
    tb = trial_balance([])
    assert tb["balanced"] is True
    assert tb["violations"] == []


@pytest.mark.parametrize(
    "journal,label,expected_fragment",
    [
        ([je("9999", "NOT_A_CODE", 123.45)], "fabricated account codes", "unknown debit account"),
        ([je("1001", "1001", 50.0)], "same account on both sides", "same account"),
        ([je("1001", "4001", -999.0)], "negative amount", "negative amount_gbp"),
        ([je("1001", "4001", float("nan"))], "non-finite amount", "non-finite amount_gbp"),
        ([{"entry_id": "e", "debit_account": "1001", "amount_gbp": 5.0}],
         "missing credit account", "missing credit_account"),
        ([{"entry_id": "e", "debit_account": "1001", "credit_account": "4001"}],
         "missing amount", "missing amount_gbp"),
    ],
)
def test_trial_balance_fires_on_each_malformed_journal(journal, label, expected_fragment):
    """R15 MUTATION PROOF (was the frozen defect). `balanced` used to be computed
    by summing the same `amount_gbp` into a debit bucket AND a credit bucket for
    every entry, so the two totals were equal by construction whatever the entry
    said, and the flag reported True for every case below — a control that could
    not fail. It now reports each of them as a violation and refuses to balance.

    Each parameter IS the mutation: revert `trial_balance` to comparing the two
    derived totals and every case here goes green again."""
    tb = trial_balance(journal)
    assert tb["balanced"] is False, f"{label}: control did not fire"
    assert any(expected_fragment in v for v in tb["violations"]), tb["violations"]


def test_a_malformed_entry_does_not_take_down_the_whole_balance():
    """One bad row is excluded from the totals and named, rather than raising —
    the whole-run-outage shape this codebase has been bitten by before."""
    tb = trial_balance([je("1001", "4001", 100.0), je("1001", "1001", 50.0)])
    assert tb["balanced"] is False
    assert tb["total_debit_gbp"] == 100.0  # the well-formed entry still totals
    assert len(tb["violations"]) == 1


# ---------------------------------------------------------------------------
# income_statement
# ---------------------------------------------------------------------------


def test_income_statement_from_the_fixed_history():
    assert income_statement(build_journal(FIVE_EVENTS)) == {
        "revenue_gbp": 950.0,
        "wholesale_cost_gbp": 400.0,
        "non_commodity_cost_gbp": 0.0,
        "gross_margin_gbp": 550.0,
        "capital_cost_gbp": 0.0,
        "bad_debt_gbp": 100.0,
        "cost_to_serve_gbp": 0.0,
        "fixed_cost_gbp": 0.0,
        "acquisition_spend_gbp": 0.0,
        "total_opex_gbp": 100.0,
        "net_margin_gbp": 450.0,
        "profit_before_tax_gbp": None,
        "corporation_tax_gbp": None,
        "profit_for_year_gbp": None,
    }


def test_income_statement_tax_triplet_is_none_without_a_year():
    """Deliberate: no year means no guessed tax year, so the three tax fields stay
    None rather than being silently computed."""
    pnl = income_statement(build_journal(FIVE_EVENTS))
    assert pnl["corporation_tax_gbp"] is None
    assert pnl["profit_before_tax_gbp"] is None


def test_income_statement_with_year_adds_tax_without_changing_net_margin():
    pnl = income_statement(build_journal(FIVE_EVENTS), year=2023)
    assert pnl["net_margin_gbp"] == 450.0
    assert pnl["profit_before_tax_gbp"] == 450.0
    assert pnl["corporation_tax_gbp"] == pytest.approx(85.5)  # 450 * 19%
    assert pnl["profit_for_year_gbp"] == pytest.approx(364.5)


# ---------------------------------------------------------------------------
# uk_corporation_tax_gbp
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", [2019, 2020, 2021, 2022])
def test_corporation_tax_flat_19_percent_before_2023(year):
    assert uk_corporation_tax_gbp(1_000_000.0, year) == pytest.approx(190_000.0)


@pytest.mark.parametrize(
    "profit,expected",
    [
        (50_000.0, 9_500.0),        # small profits rate exactly at the limit
        (250_000.0, 62_500.0),      # main rate exactly at the threshold
        (100_000.0, 22_750.0),      # marginal relief band
        (1_000_000.0, 250_000.0),   # well above the threshold
    ],
)
def test_corporation_tax_two_tier_from_2023(profit, expected):
    assert uk_corporation_tax_gbp(profit, 2023) == pytest.approx(expected)


def test_corporation_tax_is_continuous_across_both_boundaries():
    """Marginal relief is constructed to meet 19% at £50k and 25% at £250k."""
    below = uk_corporation_tax_gbp(50_000.0, 2023)
    just_above = uk_corporation_tax_gbp(50_000.01, 2023)
    assert just_above == pytest.approx(below, abs=0.01)
    at_top = uk_corporation_tax_gbp(250_000.0, 2023)
    just_over = uk_corporation_tax_gbp(250_001.0, 2023)
    assert just_over == pytest.approx(at_top + 0.25, abs=0.01)


@pytest.mark.parametrize("profit", [0.0, -1.0, -1_000_000.0])
def test_corporation_tax_is_zero_on_a_loss_no_loss_relief_carried(profit):
    assert uk_corporation_tax_gbp(profit, 2023) == 0.0


# ---------------------------------------------------------------------------
# balance_sheet
# ---------------------------------------------------------------------------


def test_balance_sheet_from_the_fixed_history():
    bs = balance_sheet(build_journal(FIVE_EVENTS, opening_treasury=5000.0))
    assert bs["cash_gbp"] == 5350.0
    assert bs["trade_receivables_gbp"] == 100.0
    assert bs["total_assets_gbp"] == 5450.0
    assert bs["total_liabilities_gbp"] == 0.0
    assert bs["opening_capital_gbp"] == 5000.0
    assert bs["current_period_profit_gbp"] == 450.0
    assert bs["total_equity_gbp"] == 5450.0
    assert bs["equation_holds"] is True


def test_balance_sheet_equity_is_pre_tax_because_no_event_ever_posts_to_7001():
    """SURPRISE (unit class): ACCOUNTS defines 7001 Corporation Tax Expense, but no
    event type in to_journal_entry maps to it and build_journal never emits one, so
    tax is computed in income_statement yet never journalled. The balance sheet's
    equity therefore carries PRE-TAX profit — the modelled company's net assets are
    overstated by the corporation tax it owes."""
    journal = build_journal(FIVE_EVENTS, opening_treasury=5000.0)
    assert all(e["debit_account"] != "7001" for e in journal)
    bs = balance_sheet(journal)
    assert bs["current_period_profit_gbp"] == income_statement(journal)["net_margin_gbp"]
    # ...which is the pre-tax figure, not profit_for_year_gbp.
    assert bs["current_period_profit_gbp"] != income_statement(journal, 2023)["profit_for_year_gbp"]


def test_balance_sheet_equation_breaks_if_a_tax_entry_is_ever_posted():
    """Characterizing the consequence of the gap above: income_statement sums only
    5xxx/6xxx expenses, so a 7001 entry lands in assets/expenses without flowing
    into current_period_profit, and the accounting equation stops holding."""
    journal = build_journal(FIVE_EVENTS, opening_treasury=5000.0) + [je("7001", "1001", 85.5)]
    assert balance_sheet(journal)["equation_holds"] is False


# ---------------------------------------------------------------------------
# DD3 held-credit reclassification
# ---------------------------------------------------------------------------


def test_held_credit_entry_moves_equity_to_liability_leaving_assets_untouched():
    (entry,) = held_credit_journal_entries(300.0)
    assert (entry["debit_account"], entry["credit_account"]) == ("3900", "2200")
    assert entry["amount_gbp"] == 300.0
    assert entry["timestamp"] == "9999-12-31"  # sentinel far-future default


def test_held_credit_zero_books_nothing():
    assert held_credit_journal_entries(0.0) == []


@pytest.mark.parametrize("bad", [-0.01, -500.0])
def test_held_credit_rejects_negative_fail_closed(bad):
    with pytest.raises(ValueError, match="must be >= 0"):
        held_credit_journal_entries(bad)


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_held_credit_rejects_non_finite_fail_closed(bad):
    with pytest.raises(ValueError, match="finite"):
        held_credit_journal_entries(bad)


def test_balance_sheet_with_held_credit_shifts_equity_into_liabilities():
    journal = build_journal(FIVE_EVENTS, opening_treasury=5000.0)
    naive = balance_sheet(journal)
    adj = balance_sheet_with_held_credit(journal, held_credit_gbp=300.0)
    assert adj["total_assets_gbp"] == naive["total_assets_gbp"]  # assets untouched
    assert adj["total_liabilities_gbp"] == 300.0
    assert adj["total_equity_gbp"] == naive["total_equity_gbp"] - 300.0
    assert adj["equation_holds"] is True
    assert adj["naive_total_equity_gbp"] == naive["total_equity_gbp"]
    assert adj["true_total_equity_gbp"] == naive["total_equity_gbp"] - 300.0
    assert adj["cash_rich_but_insolvent"] is False
