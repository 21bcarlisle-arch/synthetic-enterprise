"""R15 WIRING tests for D5 — the ledger controls are now ACTIVE.

The prior increment built the reconcile / check_conserved / ageing / dunning /
interest / write-off controls and mutation-tested them in isolation. Nothing in
the production path CALLED them on a live ledger, so they were dormant. This suite
proves the WIRING, not the standalone control:

  1. A real ledger operation now INVOKES the control (verify_against_invoicing /
     verify_allocation_conserved / collections_snapshot / build_* factories).
  2. The control FIRES when the invoice/payment control totals genuinely DIVERGE
     from the ledger (a real discrepancy injected via the independent invoice.py
     store), and PASSES on clean input.
  3. FAIL-OPEN probe: missing invoice data must NOT silently pass.
  4. FAIL-SILENT probe: an unavailable control source is a FAILED control.

Independence is the whole point: the control totals come from the SEPARATE
invoice.py SQLite store (issued invoices + cash book), never re-summed from the
ledger's own events.
"""
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
from company.billing import arrears_engine
from company.billing.arrears_engine import (
    DunningPathError,
    StatutoryInterestScopeError,
    WriteOffAuditError,
    WriteOffReason,
    build_interest_event,
    build_write_off_event,
    collections_snapshot,
)
from company.billing.invoice import (
    InvoiceControlSource,
    create_invoice,
    record_payment,
)
from company.crm.account_hierarchy import Segment

TT = dt.datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def db(tmp_path):
    return tmp_path / "wiring_invoices.db"


@pytest.fixture
def src(db):
    return InvoiceControlSource(db_path=db)


def _invoice(db, account_id, amount, period_end="2024-01-31"):
    """Issue an invoice in the INDEPENDENT invoicing register. Gross (VAT-inc)
    total_gbp = amount * 1.05 (5% domestic VAT) — that gross is what the ledger's
    bill-debit must equal."""
    return create_invoice(
        {
            "customer_id": account_id,
            "period_start": "2024-01-01",
            "period_end": period_end,
            "total_amount_gbp": amount,
            "total_consumption_kwh": 1000.0,
        },
        db,
    )


def _bill(eid, acct, amount, day, ref=None):
    return LedgerEvent(eid, acct, LedgerEventType.BILL_DEBIT, amount,
                       dt.date(2024, 1, day), TT, invoice_ref=ref)


def _pay(eid, acct, amount, day, remittance=()):
    return LedgerEvent(eid, acct, LedgerEventType.PAYMENT_CREDIT, amount,
                       dt.date(2024, 1, day), TT, remittance=tuple(remittance))


# ===========================================================================
# WIRING 1 — AccountLedger.verify_against_invoicing runs reconcile() on a LIVE
# ledger against the INDEPENDENT invoicing register + cash book.
# ===========================================================================

def test_verify_against_invoicing_passes_on_a_consistent_ledger(db, src):
    # Invoicing register: £105 gross billed. Cash book: £40 received.
    _invoice(db, "ACC1", 100.0)                 # gross total_gbp == 105.00
    record_payment("ACC1", 40.0, "2024-01-05", db_path=db)
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))     # ledger mirrors the gross bill
    led.post(_pay("p1", "ACC1", 40.0, 5))
    out = led.verify_against_invoicing(src)      # runs on the live ledger
    assert out["balance_gbp"] == 65.0 and out["basis"] == "settled"


def test_verify_against_invoicing_FIRES_when_a_payment_is_dropped(db, src):
    # REAL DISCREPANCY: the cash book independently records £40 received, but that
    # payment event never landed in the ledger (dropped) — the ledger's own
    # payment total (0) diverges from the unchanged external control.
    _invoice(db, "ACC1", 100.0)
    record_payment("ACC1", 40.0, "2024-01-05", db_path=db)
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))      # only the bill landed
    with pytest.raises(LedgerReconciliationError):
        led.verify_against_invoicing(src)


def test_verify_against_invoicing_FIRES_when_a_bill_is_tampered(db, src):
    # REAL DISCREPANCY: the ledger carries £200 of bill debit but the invoicing
    # register only ever issued £105 (a duplicated / inflated bill in the ledger).
    _invoice(db, "ACC1", 100.0)
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 200.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.verify_against_invoicing(src)


def test_verify_against_invoicing_is_not_fail_open_on_missing_invoice_data(db, src):
    # FAIL-OPEN probe: the ledger believes £105 was billed and £40 paid, but the
    # invoicing store is EMPTY for this account (missing data). This must NOT pass
    # by treating 'no invoice record' as 'zero owed' silently — it RAISES.
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))
    led.post(_pay("p1", "ACC1", 40.0, 5))
    with pytest.raises(LedgerReconciliationError):
        led.verify_against_invoicing(src)        # invoice DB has nothing for ACC1
    # ...and a genuinely empty ledger vs an empty register is fine.
    AccountLedger("ACC1").verify_against_invoicing(src)


def test_verify_against_invoicing_fail_silent_on_unavailable_source():
    # FAIL-SILENT probe: a source that cannot answer (no accessor) is a FAILED
    # control, not a free pass.
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.verify_against_invoicing(object())    # no issued_debits_gbp accessor


def test_verify_against_invoicing_fail_closed_when_source_returns_none():
    class NoneSource:
        def issued_debits_gbp(self, account_id, as_of=None):
            return None
        def cash_received_gbp(self, account_id, as_of=None):
            return None
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.verify_against_invoicing(NoneSource())


def test_verify_against_invoicing_respects_as_of_bound(db, src):
    # Point-in-time: an invoice issued LATER must not count against an earlier as-of.
    _invoice(db, "ACC1", 100.0, period_end="2024-01-31")   # issue_date 2024-01-31
    _invoice(db, "ACC1", 100.0, period_end="2024-03-31")   # issue_date 2024-03-31
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 31))               # only the Jan bill by 15-Feb
    out = led.verify_against_invoicing(src, as_of=dt.date(2024, 2, 15))
    assert out["balance_gbp"] == 105.0                     # March invoice excluded both sides


def test_verify_against_invoicing_ties_out_only_billed_paid_on_a_mixed_ledger(db, src):
    # A ledger holding interest + write-off journals (separate control accounts) is
    # tied out ONLY on its invoicing-authoritative movements (bills + cash) — the
    # classic AR three-way match. Interest/write-offs are guarded by their own
    # controls, so they don't pollute this reconciliation.
    _invoice(db, "ACC1", 100.0)                            # register: £105 billed
    record_payment("ACC1", 40.0, "2024-01-05", db_path=db)  # cash book: £40
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1))
    led.post(_pay("p1", "ACC1", 40.0, 5))
    led.post(LedgerEvent("i1", "ACC1", LedgerEventType.INTEREST_DEBIT, 10.0,
                         dt.date(2024, 1, 20), TT, reason="LPCDA"))
    led.post(LedgerEvent("wo1", "ACC1", LedgerEventType.WRITE_OFF_CREDIT, 20.0,
                         dt.date(2024, 1, 25), TT, reason="write-off (goodwill)"))
    out = led.verify_against_invoicing(src)
    assert out["scope"] == "invoicing_movements"
    assert out["billed_gbp"] == 105.0 and out["cash_received_gbp"] == 40.0
    # ...and it still FIRES on a dropped payment even amid the other journals.
    led2 = AccountLedger("ACC1")
    led2.post(_bill("b1", "ACC1", 105.0, 1))               # payment dropped
    led2.post(LedgerEvent("i1", "ACC1", LedgerEventType.INTEREST_DEBIT, 10.0,
                          dt.date(2024, 1, 20), TT, reason="LPCDA"))
    with pytest.raises(LedgerReconciliationError):
        led2.verify_against_invoicing(src)


# ===========================================================================
# WIRING 2 — AllocationResult.check_conserved runs on the LIVE allocation with
# the INDEPENDENT cash-book total.
# ===========================================================================

def test_verify_allocation_conserved_passes_on_clean_open_item(db, src):
    _invoice(db, "ACC1", 100.0)                            # INV gross £105
    record_payment("ACC1", 105.0, "2024-01-15", db_path=db)  # cash book: £105
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1, ref="INV1"))
    led.post(_pay("p1", "ACC1", 105.0, 15))
    res = led.verify_allocation_conserved(src)
    assert res.unallocated_credit_gbp == 0.0


def test_verify_allocation_conserved_FIRES_when_cash_book_diverges(db, src):
    # REAL DISCREPANCY: the cash book independently says £120 arrived, but the
    # ledger only carries a £105 payment (a payment mis-posted / dropped) — the
    # allocation cannot conserve the £120 the cash subsystem handed it.
    _invoice(db, "ACC1", 100.0)
    record_payment("ACC1", 120.0, "2024-01-15", db_path=db)
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1, ref="INV1"))
    led.post(_pay("p1", "ACC1", 105.0, 15))                # ledger short by £15
    with pytest.raises(AllocationInvariantError):
        led.verify_allocation_conserved(src)


def test_verify_allocation_conserved_fail_closed_on_unavailable_cash():
    led = AccountLedger("ACC1")
    led.post(_bill("b1", "ACC1", 105.0, 1, ref="INV1"))
    with pytest.raises(AllocationInvariantError):
        led.verify_allocation_conserved(object())          # no cash_received_gbp


# ===========================================================================
# WIRING 3 — LedgerBook.verify_against_invoicing portfolio checkpoint.
# ===========================================================================

def test_ledger_book_checkpoint_passes_when_all_accounts_reconcile(db, src):
    _invoice(db, "A", 100.0); record_payment("A", 40.0, "2024-01-05", db_path=db)
    _invoice(db, "B", 200.0)
    book = LedgerBook()
    book.post(_bill("ba", "A", 105.0, 1)); book.post(_pay("pa", "A", 40.0, 5))
    book.post(_bill("bb", "B", 210.0, 1))
    results = book.verify_against_invoicing(src)
    assert set(results) == {"A", "B"}


def test_ledger_book_checkpoint_FIRES_on_one_bad_account(db, src):
    # FAIL-CLOSED: a single tampered account fails the whole portfolio checkpoint.
    _invoice(db, "A", 100.0); record_payment("A", 40.0, "2024-01-05", db_path=db)
    _invoice(db, "B", 200.0)
    book = LedgerBook()
    book.post(_bill("ba", "A", 105.0, 1)); book.post(_pay("pa", "A", 40.0, 5))
    book.post(_bill("bb", "B", 999.0, 1))                  # B's ledger disagrees
    with pytest.raises(LedgerReconciliationError):
        book.verify_against_invoicing(src)


# ===========================================================================
# WIRING 4 — the arrears/collections controls now run inside the production
# factories + snapshot (build_interest_event, build_write_off_event,
# collections_snapshot), fail-closed.
# ===========================================================================

def test_build_interest_event_FIRES_on_resi_interest(monkeypatch):
    # REAL DISCREPANCY: a producer bug makes statutory interest positive for a
    # RESIDENTIAL account. The scope control is now wired into the factory and
    # RAISES rather than minting a non-compliant interest event.
    monkeypatch.setattr(arrears_engine, "statutory_interest_gbp",
                        lambda *a, **k: 42.0)
    with pytest.raises(StatutoryInterestScopeError):
        build_interest_event("A", Segment.RESIDENTIAL, 1000.0, 90, 0.05,
                             dt.date(2024, 4, 1), TT)


def test_build_interest_event_clean_b2b_still_produces(db):
    ev = build_interest_event("A", Segment.IC, 10000.0, 365, 0.02,
                              dt.date(2024, 4, 1), TT, invoice_ref="INV1")
    assert ev.event_type == LedgerEventType.INTEREST_DEBIT and ev.signed_amount > 0


def test_build_write_off_event_is_verified_before_return():
    # The factory now runs assert_write_off_audited on what it mints; a real
    # write-off passes and comes back audited.
    ev = build_write_off_event("A", 250.0, WriteOffReason.INSOLVENCY,
                               dt.date(2024, 6, 1), TT, note="liquidation")
    assert ev.event_type == LedgerEventType.WRITE_OFF_CREDIT and ev.affects_pnl


def test_build_write_off_event_is_fail_closed(monkeypatch):
    # The wiring must not swallow the audit control: if the audit fires, the
    # factory propagates it rather than returning an unaudited write-off.
    def boom(event):
        raise WriteOffAuditError("injected audit failure")
    monkeypatch.setattr(arrears_engine, "assert_write_off_audited", boom)
    with pytest.raises(WriteOffAuditError):
        build_write_off_event("A", 250.0, WriteOffReason.GOODWILL,
                              dt.date(2024, 6, 1), TT)


def test_collections_snapshot_runs_controls_and_FIRES_on_bad_dunning_path(monkeypatch):
    # REAL DEFECT: a segment's dunning path is emptied. collections_snapshot now
    # validates the path as part of producing the snapshot, so it RAISES.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    monkeypatch.setitem(arrears_engine._DUNNING_PATHS, Segment.IC, [])
    with pytest.raises(DunningPathError):
        collections_snapshot(led, Segment.IC, True, dt.date(2024, 4, 1),
                             disputed_refs=["INV1"])


def test_collections_snapshot_clean_snapshot_still_works():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_bill("b2", "A", 200.0, 1, ref="INV2"))
    snap = collections_snapshot(led, Segment.IC, True, dt.date(2024, 4, 1),
                                disputed_refs=["INV1"])
    assert snap["undisputed_overdue_gbp"] == 200.0
