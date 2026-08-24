"""A negative-valued event must be posted the OTHER WAY ROUND, not as its own opposite.

WHAT THIS IS ABOUT. `saas/ledger.py` signs every event the same way — cash out negative,
cash in positive — and `company/finance/double_entry.to_journal_entry` names an account
pair per event TYPE. It used to take `abs(amount_gbp)`, so the pair was the whole story
and the sign was discarded. For every ordinary event that is right. For an event whose
real value is negative it is wrong by twice the value:

  * a half-hour of NEGATIVE wholesale price — the supplier is PAID to take the energy,
    real and increasingly common on the UK system — was posted as a wholesale COST;
  * a credit bill (a real one in the end-2019 run: PROS-2018-0009, 2019-07, -£4.92) was
    posted as REVENUE.

HOW IT SURFACED, and why the fix is what unblocks the daily settlement fold.
`abs(x + y) != abs(x) + abs(y)`, so the published journal depended on how finely the
book was cut. Folding the same end-2019 settlement book to daily rows — which nets a
negative half-hour against the day's positive ones before `abs` can see it — moved
published cash and equity by £14.08 while every signed figure (portfolio gross margin,
net margin, treasury) stayed identical to the penny. That £14.08 was the last
unexplained movement holding `simulation/settlement_daily.py` unwired.

R15 — each assertion below fails on a named mutation, proven by reverting, not asserted:
  * restore `amount = abs(event["amount_gbp"])` and drop the swap ->
    `test_a_wholesale_credit_is_not_posted_as_a_cost` and
    `test_a_credit_note_is_not_posted_as_revenue`.
  * swap on sign alone, ignoring the entry's normal direction (i.e. treat every
    positive amount as money in) -> `test_every_ordinary_event_keeps_the_direction_it
    _always_had`, because a positive-signed cost event does not exist but a
    negative-signed one does for six of the eight types.
  * make the swap unconditional -> the same test.
  * let a zero-amount event swap -> `test_a_zero_amount_event_is_left_alone`.

The NULL CONTROL is `test_the_old_magnitude_only_answer_does_not_come_back`: it states
the pre-fix answer explicitly and asserts it is NOT what the journal now says, so this
file fails loudly if the `abs` is ever restored rather than quietly agreeing with it.
"""
from __future__ import annotations

import pytest

from company.finance.double_entry import (
    ACCOUNTS,
    account_balances,
    build_journal,
    to_journal_entry,
)
from saas.ledger import (
    make_billing_event,
    make_capital_charge_event,
    make_cost_to_serve_event,
    make_fixed_cost_event,
    make_settlement_event,
)


def _settlement(wholesale_cost_gbp: float) -> dict:
    """One settlement event straight from the maker, so the sign convention is the
    real one and not this test's idea of it."""
    return make_settlement_event({
        "customer_id": "C1",
        "settlement_date": "2019-07-14",
        "settlement_period": 25,
        "wholesale_cost_gbp": wholesale_cost_gbp,
        "consumption_kwh": 12.5,
        "unit_rate_gbp_per_mwh": 140.0,
    })


# ── the defect itself ───────────────────────────────────────────────────────────────

def test_a_wholesale_credit_is_not_posted_as_a_cost():
    """A negative-price half-hour pays the supplier. It is a credit to Wholesale Cost
    and cash IN, not a cost of the same size."""
    je = to_journal_entry(_settlement(wholesale_cost_gbp=-80.0))
    assert je["debit_account"] == "1001"   # cash increases
    assert je["credit_account"] == "5001"  # wholesale cost is relieved
    assert je["amount_gbp"] == pytest.approx(80.0)


def test_a_credit_note_is_not_posted_as_revenue():
    """A bill whose total is negative is money owed BACK to the customer."""
    je = to_journal_entry(make_billing_event("C1", "electricity", "2019-07-01", -4.92, 0.0))
    assert je["debit_account"] == "4001"   # revenue reversed
    assert je["credit_account"] == "1100"  # receivable reduced
    assert je["amount_gbp"] == pytest.approx(4.92)


def test_the_old_magnitude_only_answer_does_not_come_back():
    """NULL CONTROL. The pre-2026-08-24 journal answered both of the above with the
    NORMAL pair and the magnitude. Naming that answer here means restoring `abs` reds
    this file instead of quietly satisfying it."""
    credit = to_journal_entry(_settlement(wholesale_cost_gbp=-80.0))
    assert (credit["debit_account"], credit["credit_account"]) != ("5001", "1001")
    note = to_journal_entry(make_billing_event("C1", "electricity", "2019-07-01", -4.92, 0.0))
    assert (note["debit_account"], note["credit_account"]) != ("1100", "4001")


# ── the fix must not disturb anything that was already right ────────────────────────

def test_every_ordinary_event_keeps_the_direction_it_always_had():
    """The eight event types the journal recognises, each with its ORDINARY sign, must
    post exactly as they did before the sign was consulted."""
    expected = {
        "billing_event": ("1100", "4001"),
        "settlement_event": ("5001", "1001"),
        "capital_charge_event": ("5200", "1001"),
        "payment_received_event": ("1001", "1100"),
        "bad_debt_event": ("6001", "1100"),
        "vat_remittance_event": ("4001", "1001"),
        "non_commodity_cost_event": ("5100", "1001"),
        "fixed_cost_event": ("6200", "1001"),
        "cost_to_serve_event": ("6100", "1001"),
        "acquisition_spend_event": ("6300", "1001"),
    }
    events = [
        make_billing_event("C1", "electricity", "2019-07-01", 120.0, 1000.0),
        _settlement(wholesale_cost_gbp=80.0),
        make_capital_charge_event({
            "customer_id": "C1", "settlement_date": "2019-07-14",
            "settlement_period": 25, "capital_cost_gbp": 2.0,
        }),
        {"event_type": "payment_received_event", "transaction_id": "p",
         "timestamp": "2019-08-01", "customer_id": "C1", "amount_gbp": 115.0},
        {"event_type": "bad_debt_event", "transaction_id": "d",
         "timestamp": "2019-09-01", "customer_id": "C1", "amount_gbp": -5.0},
        {"event_type": "vat_remittance_event", "transaction_id": "v",
         "timestamp": "2019-07-01", "customer_id": "C1", "amount_gbp": -20.0},
        {"event_type": "non_commodity_cost_event", "transaction_id": "n",
         "timestamp": "2019-07-01", "customer_id": "C1", "amount_gbp": -10.0},
        make_fixed_cost_event("2019-07", 500.0),
        make_cost_to_serve_event("2019-07", 30.0),
        {"event_type": "acquisition_spend_event", "transaction_id": "a",
         "timestamp": "2019-07-01", "billing_account": "C1", "amount_gbp": -40.0},
    ]
    for event in events:
        je = to_journal_entry(event)
        pair = (je["debit_account"], je["credit_account"])
        assert pair == expected[event["event_type"]], event["event_type"]
        assert je["amount_gbp"] > 0


def test_a_zero_amount_event_is_left_alone():
    """Zero has no direction; a memo event must not be flipped by the sign test."""
    je = to_journal_entry(_settlement(wholesale_cost_gbp=0.0))
    assert (je["debit_account"], je["credit_account"]) == ("5001", "1001")


def test_every_recognised_pair_debits_or_credits_an_asset():
    """The direction is DERIVED from the debit account's type rather than tabulated
    per event type, which is only sound if every pair touches cash or receivables."""
    for event_type, (debit, credit) in {
        "billing_event": ("1100", "4001"), "settlement_event": ("5001", "1001"),
        "capital_charge_event": ("5200", "1001"), "payment_received_event": ("1001", "1100"),
        "bad_debt_event": ("6001", "1100"), "vat_remittance_event": ("4001", "1001"),
        "non_commodity_cost_event": ("5100", "1001"), "fixed_cost_event": ("6200", "1001"),
        "cost_to_serve_event": ("6100", "1001"), "acquisition_spend_event": ("6300", "1001"),
    }.items():
        types = {ACCOUNTS[debit]["type"], ACCOUNTS[credit]["type"]}
        assert "asset" in types, event_type


# ── and the property that makes the settlement fold landable ────────────────────────

def test_the_journal_no_longer_depends_on_how_finely_the_book_was_cut():
    """THE POINT. Three half-hours, one of them negatively priced, posted individually
    and then posted as the single netted day they add up to: the Wholesale Cost account
    must land on the same figure. Under `abs` the two disagree by twice the credit."""
    halves = [_settlement(20.0), _settlement(-8.0), _settlement(15.0)]
    for i, event in enumerate(halves):
        event["transaction_id"] = f"hh-{i}"
    day = _settlement(20.0 - 8.0 + 15.0)
    day["transaction_id"] = "day"

    per_period = account_balances(build_journal(halves))["5001"]["net"]
    netted = account_balances(build_journal([day]))["5001"]["net"]

    assert per_period == pytest.approx(27.0)
    assert netted == pytest.approx(27.0)
    assert per_period == pytest.approx(netted)
    # NULL CONTROL for this one too: the pre-fix per-period answer was 20 + 8 + 15.
    assert per_period != pytest.approx(43.0)
