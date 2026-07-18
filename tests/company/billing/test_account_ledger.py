"""Tests for the one-ledger-two-models engine + payment allocation (M2 / D5).

Covers happy path AND legitimate edge cases: a valid credit balance, an
out-of-order payment, idempotent double-post, deterministic replay (C-S1/C-S2).
"""
import datetime as dt

import pytest

from company.billing.account_ledger import (
    AccountLedger,
    AllocationResult,
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
)
from company.interfaces.bitemporal_event_log import BitemporalEventLog

TT = dt.datetime(2024, 1, 1, 12, 0, 0)


def _bill(eid, acct, amount, day, ref=None):
    return LedgerEvent(eid, acct, LedgerEventType.BILL_DEBIT, amount,
                       dt.date(2024, 1, day), TT, invoice_ref=ref)


def _pay(eid, acct, amount, day, remittance=()):
    return LedgerEvent(eid, acct, LedgerEventType.PAYMENT_CREDIT, amount,
                       dt.date(2024, 1, day), TT, remittance=tuple(remittance))


# --- sign convention / basics ---

def test_bill_debit_is_positive_signed():
    assert _bill("b1", "A", 100.0, 1).signed_amount == 100.0

def test_payment_credit_is_negative_signed():
    assert _pay("p1", "A", 40.0, 5).signed_amount == -40.0

def test_negative_magnitude_rejected():
    with pytest.raises(ValueError):
        LedgerEvent("x", "A", LedgerEventType.BILL_DEBIT, -1.0, dt.date(2024, 1, 1), TT)


# --- balance-based model ---

def test_rolling_balance_partial_payment_reduces():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    led.post(_pay("p1", "A", 40.0, 5))
    assert led.balance() == 60.0            # partial payment reduces balance, no matching
    assert led.balance_summary()["in_arrears"]

def test_credit_balance_is_legitimate_not_error():
    # EDGE CASE: customer overpays / flat DD ahead of seasonal usage -> in credit.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 50.0, 1))
    led.post(_pay("p1", "A", 80.0, 5))
    assert led.balance() == -30.0
    assert led.is_in_credit()
    s = led.balance_summary()
    assert s["in_credit"] and s["credit_gbp"] == 30.0 and s["arrears_gbp"] == 0.0

def test_balance_as_of_excludes_future_events():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    led.post(_pay("p1", "A", 100.0, 20))
    assert led.balance(as_of=dt.date(2024, 1, 10)) == 100.0   # payment not yet valid
    assert led.balance(as_of=dt.date(2024, 1, 25)) == 0.0

def test_out_of_order_arrival_same_balance():
    # EDGE CASE: events arrive late / out of order (C-S1) -> balance unchanged.
    a = AccountLedger("A")
    a.post(_bill("b1", "A", 100.0, 1)); a.post(_pay("p1", "A", 30.0, 5))
    b = AccountLedger("A")
    b.post(_pay("p1", "A", 30.0, 5)); b.post(_bill("b1", "A", 100.0, 1))  # reversed order
    assert a.balance() == b.balance() == 70.0


# --- idempotency / replay (C-S2) ---

def test_double_post_is_noop():
    led = AccountLedger("A")
    assert led.post(_bill("b1", "A", 100.0, 1)) is True
    assert led.post(_bill("b1", "A", 100.0, 1)) is False   # duplicate event_id ignored
    assert led.balance() == 100.0

def test_deterministic_replay_reproduces_state():
    events = [_bill("b1", "A", 100.0, 1), _pay("p1", "A", 40.0, 5),
              _bill("b2", "A", 60.0, 10), _pay("p2", "A", 20.0, 15)]
    a = AccountLedger("A")
    for e in events:
        a.post(e)
    b = AccountLedger("A")
    for e in reversed(events):        # replay in a different order
        b.post(e)
        b.post(e)                     # and twice — still idempotent
    assert a.balance() == b.balance()
    assert [e.event_id for e in a.events()] == [e.event_id for e in b.events()]

def test_post_wrong_account_rejected():
    led = AccountLedger("A")
    with pytest.raises(ValueError):
        led.post(_bill("b1", "B", 10.0, 1))


# --- open-item allocation ---

def test_oldest_first_allocation():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_bill("b2", "A", 100.0, 10, ref="INV2"))
    led.post(_pay("p1", "A", 120.0, 15))   # no remittance -> oldest first
    res = led.allocate()
    out = res.outstanding_by_invoice()
    assert out.get("INV1", 0.0) == 0.0     # fully cleared
    assert out["INV2"] == 80.0             # remainder on newer invoice
    assert res.unallocated_credit_gbp == 0.0

def test_remittance_directed_allocation_overrides_oldest():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_bill("b2", "A", 100.0, 10, ref="INV2"))
    led.post(_pay("p1", "A", 100.0, 15, remittance=["INV2"]))  # pay the NEWER one
    out = led.allocate().outstanding_by_invoice()
    assert out["INV1"] == 100.0            # untouched
    assert out.get("INV2", 0.0) == 0.0     # remittance-cleared

def test_disputed_invoice_excluded_from_oldest_first():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))   # disputed
    led.post(_bill("b2", "A", 100.0, 10, ref="INV2"))
    led.post(_pay("p1", "A", 60.0, 15))    # oldest-first would hit INV1, but it's disputed
    res = led.allocate(disputed_refs=["INV1"])
    out = res.outstanding_by_invoice()
    assert out["INV1"] == 100.0            # disputed, skipped by oldest-first
    assert out["INV2"] == 40.0             # payment landed on INV2 instead
    assert res.total_undisputed_outstanding_gbp == 40.0

def test_overpayment_becomes_unallocated_credit():
    # EDGE CASE: pays more than all open invoices -> credit, not an error.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 50.0, 1, ref="INV1"))
    led.post(_pay("p1", "A", 80.0, 5))
    res = led.allocate()
    assert res.outstanding_by_invoice().get("INV1", 0.0) == 0.0
    assert res.unallocated_credit_gbp == 30.0

def test_allocation_order_independent():
    # posting order must not change allocation outcome (C-S2)
    def build(order):
        led = AccountLedger("A")
        for e in order:
            led.post(e)
        return led.allocate().outstanding_by_invoice()
    evs = [_bill("b1", "A", 100.0, 1, ref="INV1"),
           _bill("b2", "A", 100.0, 10, ref="INV2"),
           _pay("p1", "A", 120.0, 15)]
    assert build(evs) == build(list(reversed(evs)))


# --- bitemporal emission (model-agnostic downstream) ---

def test_emit_to_bitemporal_log():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_pay("p1", "A", 40.0, 5))
    log = BitemporalEventLog()
    n = led.emit_to(log)
    assert n == 2
    rec = log.as_known_at(dt.datetime(2024, 6, 1), "account:A", "ledger:bill_debit")
    assert rec is not None and rec.value["amount_gbp"] == 100.0


# --- portfolio book ---

def test_ledger_book_routes_and_aggregates():
    book = LedgerBook()
    book.post(_bill("b1", "A", 100.0, 1))
    book.post(_bill("b2", "B", 50.0, 1))
    book.post(_pay("p1", "A", 30.0, 5))
    assert book.accounts() == ["A", "B"]
    assert book.portfolio_balance_gbp() == 120.0   # (100-30) + 50
    assert book.total_arrears_gbp() == 120.0
