"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/account_ledger.py — the account event store that both the
balance-based (resi/micro-SME) and open-item (SME/I&C) accounting models emit into.
This is the money core's ledger: every bill, payment, adjustment, write-off and
refund lands here, and downstream ageing/dunning/arrears read it.

All inputs are fixed and explicit. No randomness, no wall-clock reads: every date is
a literal, so these tests are stable under replay.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import (
    AccountLedger,
    AllocationInvariantError,
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
    LedgerReconciliationError,
)

TT = dt.datetime(2024, 1, 1, 12, 0, 0)  # fixed transaction_time for every event


def ev(event_id, event_type, amount, valid_time, account_id="A1", **kw):
    """Build a LedgerEvent with fixed transaction_time and ISO date string."""
    return LedgerEvent(
        event_id=event_id,
        account_id=account_id,
        event_type=event_type,
        amount_gbp=amount,
        valid_time=dt.date.fromisoformat(valid_time),
        transaction_time=TT,
        **kw,
    )


# ---------------------------------------------------------------------------
# Sign convention
# ---------------------------------------------------------------------------


def test_signed_amount_sign_by_event_type():
    """POSITIVE increases what the customer owes us; NEGATIVE reduces it."""
    signs = {t: ev("x", t, 10.0, "2024-01-01").signed_amount for t in LedgerEventType}
    assert signs[LedgerEventType.BILL_DEBIT] == 10.0
    assert signs[LedgerEventType.ADJUSTMENT_DEBIT] == 10.0
    assert signs[LedgerEventType.INTEREST_DEBIT] == 10.0
    assert signs[LedgerEventType.PAYMENT_CREDIT] == -10.0
    assert signs[LedgerEventType.ADJUSTMENT_CREDIT] == -10.0
    assert signs[LedgerEventType.WRITE_OFF_CREDIT] == -10.0
    # SURPRISE (sign class): REFUND_DEBIT is a DEBIT (+10), i.e. paying a credit
    # balance back to the customer INCREASES the modelled balance toward zero from
    # below. Consistent with the module's stated convention, but it means a refund
    # and a bill are indistinguishable by sign in the rolling balance.
    assert signs[LedgerEventType.REFUND_DEBIT] == 10.0


def test_affects_pnl_only_write_off_and_interest():
    assert ev("x", LedgerEventType.WRITE_OFF_CREDIT, 5.0, "2024-01-01").affects_pnl is True
    assert ev("x", LedgerEventType.INTEREST_DEBIT, 5.0, "2024-01-01").affects_pnl is True
    assert ev("x", LedgerEventType.BILL_DEBIT, 5.0, "2024-01-01").affects_pnl is False
    assert ev("x", LedgerEventType.PAYMENT_CREDIT, 5.0, "2024-01-01").affects_pnl is False
    assert ev("x", LedgerEventType.REFUND_DEBIT, 5.0, "2024-01-01").affects_pnl is False


# ---------------------------------------------------------------------------
# Event construction guards
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_amount_rejected_at_construction(bad):
    with pytest.raises(ValueError, match="finite"):
        ev("x", LedgerEventType.BILL_DEBIT, bad, "2024-01-01")


def test_negative_amount_rejected_amount_is_a_magnitude():
    with pytest.raises(ValueError, match="magnitude"):
        ev("x", LedgerEventType.BILL_DEBIT, -1.0, "2024-01-01")


def test_zero_amount_is_accepted():
    # Zero passes both guards — a £0.00 bill event is storable.
    assert ev("x", LedgerEventType.BILL_DEBIT, 0.0, "2024-01-01").signed_amount == 0.0


# ---------------------------------------------------------------------------
# post(): idempotency and account routing
# ---------------------------------------------------------------------------


def test_post_is_idempotent_on_event_id():
    led = AccountLedger("A1")
    e = ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10")
    assert led.post(e) is True
    assert led.post(e) is False  # duplicate event_id — no-op
    assert led.balance() == 100.0


def test_post_dedups_on_event_id_alone_not_on_content():
    """SURPRISE (boundary class): dedup is keyed on event_id ONLY. A second event
    reusing an existing id is DISCARDED even though its amount differs — the first
    write wins silently and the £500 is lost with no error."""
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    assert led.post(ev("b1", LedgerEventType.BILL_DEBIT, 500.0, "2024-01-10")) is False
    assert led.balance() == 100.0  # not 500.0, and not 600.0


def test_post_rejects_event_for_another_account():
    led = AccountLedger("A1")
    with pytest.raises(ValueError, match="not A1"):
        led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", account_id="A2"))


# ---------------------------------------------------------------------------
# balance(): arrival-order independence and as_of
# ---------------------------------------------------------------------------


def _three_events():
    return [
        ev("b1", LedgerEventType.BILL_DEBIT, 120.50, "2024-01-10"),
        ev("p1", LedgerEventType.PAYMENT_CREDIT, 40.25, "2024-02-01"),
        ev("i1", LedgerEventType.INTEREST_DEBIT, 5.00, "2024-02-15"),
    ]


def test_balance_is_independent_of_arrival_order():
    forward, reverse = AccountLedger("A1"), AccountLedger("A1")
    for e in _three_events():
        forward.post(e)
    for e in reversed(_three_events()):
        reverse.post(e)
    assert forward.balance() == reverse.balance() == 85.25  # 120.50 - 40.25 + 5.00


def test_balance_as_of_is_inclusive_of_that_day():
    led = AccountLedger("A1")
    for e in _three_events():
        led.post(e)
    assert led.balance(as_of=dt.date(2024, 1, 9)) == 0.0
    assert led.balance(as_of=dt.date(2024, 1, 10)) == 120.50  # bill day itself counts
    assert led.balance(as_of=dt.date(2024, 2, 1)) == 80.25
    assert led.balance(as_of=dt.date(2024, 2, 15)) == 85.25


def test_is_in_credit_is_strict_less_than_zero():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 50.0, "2024-01-10"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 50.0, "2024-01-20"))
    assert led.balance() == 0.0
    assert led.is_in_credit() is False  # exactly zero is NOT "in credit"


def test_balance_summary_fields():
    led = AccountLedger("A1")
    for e in _three_events():
        led.post(e)
    assert led.balance_summary(as_of=dt.date(2024, 2, 15)) == {
        "account_id": "A1",
        "as_of": "2024-02-15",
        "balance_gbp": 85.25,
        "total_debits_gbp": 125.50,
        "total_credits_gbp": 40.25,
        "in_arrears": True,
        "in_credit": False,
        "arrears_gbp": 85.25,
        "credit_gbp": 0.0,
    }


def test_balance_summary_credit_side():
    led = AccountLedger("A1")
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 75.0, "2024-01-10"))
    s = led.balance_summary()
    assert s["as_of"] is None
    assert s["balance_gbp"] == -75.0
    assert s["in_credit"] is True and s["in_arrears"] is False
    assert s["credit_gbp"] == 75.0 and s["arrears_gbp"] == 0.0


# ---------------------------------------------------------------------------
# reconcile(): the R15 control against external totals
# ---------------------------------------------------------------------------


def test_reconcile_passes_against_matching_control_totals():
    led = AccountLedger("A1")
    for e in _three_events():
        led.post(e)
    assert led.reconcile(expected_debits_gbp=125.50, expected_credits_gbp=40.25) == {
        "account_id": "A1",
        "as_of": None,
        "debits_gbp": 125.50,
        "credits_gbp": 40.25,
        "balance_gbp": 85.25,
        "basis": "settled",
    }


def test_reconcile_raises_when_a_debit_is_missing():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    with pytest.raises(LedgerReconciliationError, match="debit total"):
        led.reconcile(expected_debits_gbp=200.0, expected_credits_gbp=0.0)


def test_reconcile_fails_closed_on_empty_ledger_with_nonzero_expectation():
    with pytest.raises(LedgerReconciliationError):
        AccountLedger("A1").reconcile(expected_debits_gbp=100.0, expected_credits_gbp=0.0)


def test_reconcile_rejects_non_finite_control_total():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    with pytest.raises(LedgerReconciliationError, match="non-finite"):
        led.reconcile(expected_debits_gbp=float("nan"), expected_credits_gbp=0.0)


def test_reconcile_tolerance_is_half_a_penny():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    led.reconcile(expected_debits_gbp=100.004, expected_credits_gbp=0.0)  # within tol
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=100.02, expected_credits_gbp=0.0)


# ---------------------------------------------------------------------------
# allocate(): remittance-else-oldest-first open-item allocation
# ---------------------------------------------------------------------------


def _two_invoice_ledger():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", invoice_ref="INV1"))
    led.post(ev("b2", LedgerEventType.BILL_DEBIT, 100.0, "2024-02-10", invoice_ref="INV2"))
    return led


def test_allocate_oldest_first_when_no_remittance():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 150.0, "2024-03-01"))
    r = led.allocate()
    assert r.allocations == [("p1", "INV1", 100.0), ("p1", "INV2", 50.0)]
    assert r.outstanding_by_invoice() == {"INV2": 50.0}
    assert r.unallocated_credit_gbp == 0.0


def test_allocate_remittance_overrides_oldest_first():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-03-01",
               remittance=("INV2",)))
    r = led.allocate()
    assert r.allocations == [("p1", "INV2", 100.0)]
    assert r.outstanding_by_invoice() == {"INV1": 100.0}  # older invoice left open


def test_allocate_overpayment_becomes_unallocated_credit():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 250.0, "2024-03-01"))
    r = led.allocate()
    assert r.unallocated_credit_gbp == 50.0
    assert r.total_outstanding_gbp == 0.0


def test_allocate_skips_disputed_invoices_in_oldest_first():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-03-01"))
    r = led.allocate(disputed_refs=["INV1"])
    # Payment jumps the disputed INV1 and lands on INV2.
    assert r.allocations == [("p1", "INV2", 100.0)]
    assert r.total_outstanding_gbp == 100.0             # INV1 still open
    assert r.total_undisputed_outstanding_gbp == 0.0    # but excluded from dunning


def test_allocate_remittance_may_still_hit_a_disputed_invoice():
    """The customer's own remittance advice overrides the dispute hold-out."""
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 50.0, "2024-03-01",
               remittance=("INV1",)))
    r = led.allocate(disputed_refs=["INV1"])
    assert r.allocations == [("p1", "INV1", 50.0)]
    assert r.outstanding_by_invoice() == {"INV1": 50.0, "INV2": 100.0}
    assert r.outstanding_by_invoice(include_disputed=False) == {"INV2": 100.0}


def test_allocate_is_independent_of_posting_order():
    events = [
        ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", invoice_ref="INV1"),
        ev("b2", LedgerEventType.BILL_DEBIT, 100.0, "2024-02-10", invoice_ref="INV2"),
        ev("p1", LedgerEventType.PAYMENT_CREDIT, 120.0, "2024-03-01"),
    ]
    fwd, rev = AccountLedger("A1"), AccountLedger("A1")
    for e in events:
        fwd.post(e)
    for e in reversed(events):
        rev.post(e)
    assert fwd.allocate().allocations == rev.allocate().allocations


def test_adjustment_debit_inflates_the_existing_invoice_rather_than_opening_a_new_item():
    """SURPRISE (boundary class): an ADJUSTMENT_DEBIT carrying an existing
    invoice_ref is FOLDED INTO that invoice (issued 100 + 25 = 125) and keeps the
    ORIGINAL invoice's issue_date. The adjustment therefore ages from the original
    bill date, not its own — a £25 correction raised in February is already 31 days
    overdue the moment it exists."""
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", invoice_ref="INV1"))
    led.post(ev("a1", LedgerEventType.ADJUSTMENT_DEBIT, 25.0, "2024-02-10",
               invoice_ref="INV1", reason="rebill"))
    (item,) = led.allocate().open_items
    assert item.issued_gbp == 125.0
    assert item.issue_date == dt.date(2024, 1, 10)  # NOT 2024-02-10


def test_credit_adjustments_apply_before_payments_regardless_of_date():
    """SURPRISE (boundary class): credit adjustments and write-offs are applied to
    invoices in a pass that runs BEFORE the payment pass, so a write-off dated
    2024-12-01 settles INV1 ahead of a payment dated 2024-03-01. The payment is then
    pushed onto INV2. Replay the same facts in real time order and the £100 payment
    would have cleared INV1 instead — which invoice a customer's cash settles depends
    on a later, unrelated write-off."""
    led = _two_invoice_ledger()
    led.post(ev("w1", LedgerEventType.WRITE_OFF_CREDIT, 100.0, "2024-12-01",
               invoice_ref="INV1", reason="bad debt"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-03-01"))
    r = led.allocate()
    assert r.allocations == [("p1", "INV2", 100.0)]
    assert r.outstanding_by_invoice() == {}


def test_allocate_ignores_refund_debits_so_credit_view_disagrees_with_balance():
    """SURPRISE (unit/sign class, money-relevant): allocate()'s own inline comment
    says "(and refund debits reduce available credit)", but the allocation loop only
    ever inspects PAYMENT_CREDIT. A REFUND_DEBIT is never subtracted from
    unallocated credit, so after refunding £100 of a £150 credit the two views of
    the same account disagree by exactly the refund: balance() says £50 in credit,
    allocate() still says £150 of unallocated credit available."""
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", invoice_ref="INV1"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 250.0, "2024-02-01"))
    led.post(ev("r1", LedgerEventType.REFUND_DEBIT, 100.0, "2024-03-01", reason="refund"))
    r = led.allocate()
    assert led.balance() == -50.0            # truly £50 in credit
    assert r.unallocated_credit_gbp == 150.0  # but the open-item view says £150


def test_allocate_as_of_excludes_later_events():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-03-01"))
    r = led.allocate(as_of=dt.date(2024, 2, 28))
    assert r.allocations == []
    assert r.total_outstanding_gbp == 200.0


# ---------------------------------------------------------------------------
# check_conserved(): the R15 allocation control
# ---------------------------------------------------------------------------


def test_check_conserved_passes_when_cash_ties_out():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 250.0, "2024-03-01"))
    led.allocate().check_conserved(total_payments_gbp=250.0)  # does not raise


def test_check_conserved_raises_when_external_cash_disagrees():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 250.0, "2024-03-01"))
    with pytest.raises(AllocationInvariantError, match="cash not conserved"):
        led.allocate().check_conserved(total_payments_gbp=300.0)


def test_check_conserved_fails_closed_on_no_allocations_with_cash_expected():
    with pytest.raises(AllocationInvariantError):
        AccountLedger("A1").allocate().check_conserved(total_payments_gbp=100.0)


def test_check_conserved_rejects_non_finite_external_total():
    led = _two_invoice_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-03-01"))
    with pytest.raises(AllocationInvariantError, match="non-finite"):
        led.allocate().check_conserved(total_payments_gbp=float("inf"))


# ---------------------------------------------------------------------------
# verify_against_invoicing(): fail-closed wiring
# ---------------------------------------------------------------------------


class _StubSource:
    def __init__(self, debits, credits):
        self._d, self._c = debits, credits

    def issued_debits_gbp(self, account_id, as_of=None):
        return self._d

    def cash_received_gbp(self, account_id, as_of=None):
        return self._c


class _MuteSource:
    """A control source that cannot answer at all."""


def test_verify_against_invoicing_pure_bills_and_payments_runs_full_reconcile():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 30.0, "2024-02-01"))
    out = led.verify_against_invoicing(_StubSource(100.0, 30.0))
    assert out["basis"] == "settled" and out["balance_gbp"] == 70.0
    assert "scope" not in out  # full reconcile shape, not the mixed-ledger shape


def test_verify_against_invoicing_mixed_ledger_ties_only_invoicing_movements():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 30.0, "2024-02-01"))
    led.post(ev("i1", LedgerEventType.INTEREST_DEBIT, 9.0, "2024-02-05"))
    out = led.verify_against_invoicing(_StubSource(100.0, 30.0))
    assert out["scope"] == "invoicing_movements"
    assert out["billed_gbp"] == 100.0 and out["cash_received_gbp"] == 30.0
    assert "balance_gbp" not in out  # the balance leg is NOT checked on a mixed ledger


def test_verify_against_invoicing_fails_closed_when_source_cannot_answer():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    with pytest.raises(LedgerReconciliationError, match="FAILED control"):
        led.verify_against_invoicing(_MuteSource())


def test_verify_against_invoicing_fails_closed_when_source_returns_none():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10"))
    with pytest.raises(LedgerReconciliationError, match="fail-closed"):
        led.verify_against_invoicing(_StubSource(None, None))


def test_verify_allocation_conserved_fails_closed_on_mute_source():
    with pytest.raises(AllocationInvariantError, match="FAILED control"):
        AccountLedger("A1").verify_allocation_conserved(_MuteSource())


# ---------------------------------------------------------------------------
# LedgerBook: portfolio roll-up
# ---------------------------------------------------------------------------


def test_ledger_book_routes_events_and_creates_accounts_on_first_sight():
    book = LedgerBook()
    book.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", account_id="A1"))
    book.post(ev("b2", LedgerEventType.BILL_DEBIT, 60.0, "2024-01-10", account_id="A2"))
    book.post(ev("p2", LedgerEventType.PAYMENT_CREDIT, 90.0, "2024-02-01", account_id="A2"))
    assert book.accounts() == ["A1", "A2"]
    assert book.portfolio_balance_gbp() == 70.0  # 100 + (60 - 90)


def test_total_arrears_excludes_credit_balances_so_it_exceeds_portfolio_balance():
    """Arrears floors each account at zero, so a customer in credit does NOT net off
    another's debt: portfolio balance £70 but total arrears £100."""
    book = LedgerBook()
    book.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", account_id="A1"))
    book.post(ev("p2", LedgerEventType.PAYMENT_CREDIT, 30.0, "2024-02-01", account_id="A2"))
    assert book.portfolio_balance_gbp() == 70.0
    assert book.total_arrears_gbp() == 100.0


def test_ledger_book_verify_propagates_first_failing_account():
    book = LedgerBook()
    book.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", account_id="A1"))
    with pytest.raises(LedgerReconciliationError):
        book.verify_against_invoicing(_StubSource(999.0, 0.0))


# ---------------------------------------------------------------------------
# emit_to(): bitemporal seam
# ---------------------------------------------------------------------------


class _RecordingLog:
    def __init__(self):
        self.records = []

    def record(self, **kw):
        self.records.append(kw)


def test_emit_to_writes_one_bitemporal_fact_per_event():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-10", invoice_ref="INV1"))
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 40.0, "2024-02-01"))
    log = _RecordingLog()
    assert led.emit_to(log) == 2
    first = log.records[0]
    assert first["entity_id"] == "account:A1"
    assert first["fact_type"] == "ledger:bill_debit"
    assert first["valid_time"] == dt.date(2024, 1, 10)
    assert first["value"]["signed_amount_gbp"] == 100.0
    assert log.records[1]["value"]["signed_amount_gbp"] == -40.0
