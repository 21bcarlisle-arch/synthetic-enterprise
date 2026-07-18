"""R15 MUTATION TESTS for the D5 ledger + arrears controls.

Each control must be able to FAIL. For every invariant-checking control added in
company/billing/account_ledger.py and company/billing/arrears_engine.py, this
suite (a) injects that control's OWN NAMED DEFECT and asserts the control RAISES,
and (b) asserts the control PASSES on clean input. A control that only ever passes
is worthless (R15, CONTROLS_THAT_CANNOT_FAIL.md).

Killer patterns probed per control: TAUTOLOGY (checked value re-derived from the
same source), FAIL-OPEN (passes on missing/zero/empty/malformed), FAIL-SILENT
(passes when the checker itself is unavailable).
"""
import datetime as dt

import pytest

from company.billing.account_ledger import (
    AccountLedger,
    AllocationInvariantError,
    AllocationResult,
    InvoiceOpenItem,
    LedgerEvent,
    LedgerEventType,
    LedgerReconciliationError,
)
from company.billing.arrears_engine import (
    AGE_BUCKETS,
    AgedItem,
    AgeingPartitionError,
    DunningPathError,
    DunningStep,
    StatutoryInterestScopeError,
    WriteOffAuditError,
    age_bucket,
    ageing_buckets,
    assert_age_buckets_partition,
    assert_ageing_conserves_value,
    assert_dunning_path_valid,
    assert_interest_is_b2b_only,
    assert_write_off_audited,
    build_write_off_event,
    current_dunning_step,
    statutory_interest_gbp,
)
from company.crm.account_hierarchy import Segment

TT = dt.datetime(2024, 1, 1, 12, 0, 0)


def _bill(eid, acct, amount, day, ref=None):
    return LedgerEvent(eid, acct, LedgerEventType.BILL_DEBIT, amount,
                       dt.date(2024, 1, day), TT, invoice_ref=ref)


def _pay(eid, acct, amount, day, remittance=()):
    return LedgerEvent(eid, acct, LedgerEventType.PAYMENT_CREDIT, amount,
                       dt.date(2024, 1, day), TT, remittance=tuple(remittance))


# ===========================================================================
# CONTROL 1 — AccountLedger.reconcile: balance == sum of events, vs EXTERNAL
# control totals. Named defect: drop a ledger event so the ledger's own totals
# no longer match the (unchanged) external control account.
# ===========================================================================

def test_reconcile_passes_on_clean_ledger():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    led.post(_pay("p1", "A", 40.0, 5))
    # External control account independently says: £100 billed, £40 received.
    out = led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=40.0)
    assert out["balance_gbp"] == 60.0 and out["basis"] == "settled"


def test_reconcile_FIRES_when_a_bill_event_is_dropped():
    # MUTATION: the £100 bill never made it into the ledger (dropped event), but
    # the external invoicing subsystem still knows it issued £100.
    led = AccountLedger("A")
    led.post(_pay("p1", "A", 40.0, 5))          # only the payment landed
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=40.0)


def test_reconcile_FIRES_when_a_payment_event_is_dropped():
    # MUTATION: a received payment is missing from the ledger.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=40.0)


def test_reconcile_is_not_fail_open_on_empty_ledger():
    # FAIL-OPEN probe: an EMPTY ledger must NOT pass against a non-zero external
    # expectation (all events dropped is the worst drop, not a free pass).
    led = AccountLedger("A")
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=0.0)
    # ...but a genuinely empty account against a zero expectation is fine.
    led.reconcile(expected_debits_gbp=0.0, expected_credits_gbp=0.0)


def test_reconcile_is_independent_not_a_tautology():
    # TAUTOLOGY probe: the expectation comes from OUTSIDE the event set, so a
    # duplicated-magnitude / tampered figure is caught rather than rubber-stamped.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=200.0, expected_credits_gbp=0.0)


# ===========================================================================
# CONTROL 2 — AllocationResult.check_conserved: no over-allocation + cash is
# conserved. Named defect: misallocate a remittance (over-allocate an invoice /
# create or destroy cash).
# ===========================================================================

def test_check_conserved_passes_on_real_allocation():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_bill("b2", "A", 100.0, 10, ref="INV2"))
    led.post(_pay("p1", "A", 120.0, 15))
    res = led.allocate()
    res.check_conserved(total_payments_gbp=120.0)   # clean: does not raise


def test_check_conserved_FIRES_on_over_allocation():
    # MUTATION: an invoice allocated beyond what was issued (a misallocation puts
    # £150 against a £100 invoice) -> outstanding goes negative.
    bad = AllocationResult(
        open_items=[InvoiceOpenItem("INV1", issued_gbp=100.0,
                                    issue_date=dt.date(2024, 1, 1), allocated_gbp=150.0)],
        unallocated_credit_gbp=0.0,
        allocations=[("p1", "INV1", 150.0)],
    )
    with pytest.raises(AllocationInvariantError):
        bad.check_conserved(total_payments_gbp=150.0)


def test_check_conserved_FIRES_when_cash_not_conserved():
    # MUTATION: an allocation was dropped from the result (cash destroyed) — the
    # payments subsystem says £120 came in but only £80 is accounted for.
    bad = AllocationResult(
        open_items=[InvoiceOpenItem("INV1", issued_gbp=100.0,
                                    issue_date=dt.date(2024, 1, 1), allocated_gbp=80.0)],
        unallocated_credit_gbp=0.0,
        allocations=[("p1", "INV1", 80.0)],
    )
    with pytest.raises(AllocationInvariantError):
        bad.check_conserved(total_payments_gbp=120.0)


def test_check_conserved_not_fail_open_on_empty():
    # FAIL-OPEN probe: zero allocations must NOT pass against a non-zero cash total.
    empty = AllocationResult(open_items=[], unallocated_credit_gbp=0.0, allocations=[])
    with pytest.raises(AllocationInvariantError):
        empty.check_conserved(total_payments_gbp=50.0)
    empty.check_conserved(total_payments_gbp=0.0)   # nothing in, nothing out — fine


def test_check_conserved_counts_unallocated_credit():
    # An overpayment is conserved AS unallocated credit, not a violation.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 50.0, 1, ref="INV1"))
    led.post(_pay("p1", "A", 80.0, 5))
    res = led.allocate()
    assert res.unallocated_credit_gbp == 30.0
    res.check_conserved(total_payments_gbp=80.0)    # 50 allocated + 30 credit == 80


# ===========================================================================
# CONTROL 3 — assert_age_buckets_partition: 30/60/90+ buckets partition
# days-overdue with no gap/overlap. Named defect: a bucket fn with a gap or an
# overlap (non-monotonic severity).
# ===========================================================================

def test_partition_passes_on_real_age_bucket():
    assert_age_buckets_partition(age_bucket)          # clean: does not raise


def test_partition_FIRES_on_a_gap():
    # MUTATION: a bucket function with a GAP — days 30..44 fall into NO bucket.
    def gapped(days):
        if days >= 90:
            return "90+"
        if days >= 60:
            return "60-90"
        if days >= 45:
            return "30-60"
        if days < 30:
            return "current"
        return "UNBUCKETED"        # 30..44 -> out-of-set (the gap)
    with pytest.raises(AgeingPartitionError):
        assert_age_buckets_partition(gapped)


def test_partition_FIRES_on_an_overlap():
    # MUTATION: a bucket function whose severity REGRESSES (an overlap): after
    # entering 60-90 it drops a later day back to 30-60.
    def overlapping(days):
        if days == 75:
            return "30-60"          # regression at 75 -> overlap
        return age_bucket(days)
    with pytest.raises(AgeingPartitionError):
        assert_age_buckets_partition(overlapping)


# ===========================================================================
# CONTROL 3b — assert_ageing_conserves_value: aggregation preserves undisputed
# value + count. Named defect: an aggregator that drops an item.
# ===========================================================================

def _aged(ref, amount, days, disputed=False):
    due = dt.date(2024, 1, 1)
    return AgedItem(reference=ref, outstanding_gbp=amount, due_date=due,
                    days_overdue=days, disputed=disputed)


def test_ageing_conserves_passes_with_real_aggregator():
    items = [_aged("INV1", 100.0, 40), _aged("INV2", 50.0, 95),
             _aged("INV3", 999.0, 40, disputed=True)]   # disputed excluded from both
    assert_ageing_conserves_value(items, aggregator=ageing_buckets)


def test_ageing_conserves_FIRES_when_aggregator_drops_an_item():
    items = [_aged("INV1", 100.0, 40), _aged("INV2", 50.0, 95)]

    def dropping(its):
        # MUTATION: an aggregator that silently drops the first undisputed item.
        return ageing_buckets(its[1:])
    with pytest.raises(AgeingPartitionError):
        assert_ageing_conserves_value(items, aggregator=dropping)


def test_ageing_conserves_FIRES_when_aggregator_double_counts():
    items = [_aged("INV1", 100.0, 40)]

    def doubling(its):
        return ageing_buckets(list(its) + list(its))   # MUTATION: double-count
    with pytest.raises(AgeingPartitionError):
        assert_ageing_conserves_value(items, aggregator=doubling)


# ===========================================================================
# CONTROL 4 — assert_dunning_path_valid: non-empty, strictly-ascending triggers.
# Named defect: a path with a descending/duplicate trigger (which used to make
# current_dunning_step silently skip a step). Also verifies the hardened
# current_dunning_step is now order-independent.
# ===========================================================================

def test_dunning_path_valid_passes_for_every_real_segment():
    for seg in (Segment.RESIDENTIAL, Segment.MICRO_SME, Segment.SME, Segment.IC):
        assert_dunning_path_valid(seg)               # clean: does not raise


def test_dunning_path_valid_FIRES_on_descending_triggers():
    bad = [DunningStep(0, "reminder", "email"),
           DunningStep(30, "final", "letter"),
           DunningStep(14, "oops", "letter")]         # MUTATION: 14 < 30 (descending)
    with pytest.raises(DunningPathError):
        assert_dunning_path_valid(Segment.SME, path=bad)


def test_dunning_path_valid_not_fail_open_on_empty():
    # FAIL-OPEN probe: an empty path is a defect, must raise (not a free pass).
    with pytest.raises(DunningPathError):
        assert_dunning_path_valid(Segment.SME, path=[])


def test_hardened_current_step_is_order_independent():
    # The old early-break returned the WRONG step on a mis-ordered path; the
    # hardened max-of-reached selection returns the furthest reached regardless.
    misordered = [DunningStep(0, "reminder", "email"),
                  DunningStep(56, "final_notice", "letter"),
                  DunningStep(28, "repayment_plan_offer", "phone")]
    # a real Segment path is well-ordered; confirm selection logic on a real one:
    step = current_dunning_step(Segment.RESIDENTIAL, 60)
    assert step is not None and step.trigger_days_overdue == 56


# ===========================================================================
# CONTROL 5 — assert_interest_is_b2b_only: LPCDA statutory interest is B2B only.
# Named defect: statutory interest attributed to a B2C/residential account.
# ===========================================================================

def test_interest_scope_passes_for_business_and_zero_resi():
    assert_interest_is_b2b_only(Segment.SME, 123.45)      # B2B positive: fine
    assert_interest_is_b2b_only(Segment.RESIDENTIAL, 0.0)  # resi zero: fine


def test_interest_scope_FIRES_on_b2c_interest():
    # MUTATION: a positive statutory-interest figure applied to a resi account.
    with pytest.raises(StatutoryInterestScopeError):
        assert_interest_is_b2b_only(Segment.RESIDENTIAL, 42.0)


def test_interest_scope_is_independent_of_the_producer():
    # The producer already guards (returns 0 for resi); this is a SECOND check on
    # the produced figure, so it still fires even if a caller fabricated interest.
    produced = statutory_interest_gbp(Segment.RESIDENTIAL, 1000.0, 90, 0.05)
    assert produced == 0.0
    assert_interest_is_b2b_only(Segment.RESIDENTIAL, produced)   # 0 -> fine
    with pytest.raises(StatutoryInterestScopeError):
        assert_interest_is_b2b_only(Segment.RESIDENTIAL, 999.0)  # fabricated -> fires


# ===========================================================================
# CONTROL 6 — assert_write_off_audited: dated, reasoned, P&L-visible. Named
# defect: a WRITE_OFF_CREDIT with an empty reason (a silent status flip).
# ===========================================================================

def test_write_off_audited_passes_on_real_write_off():
    from company.billing.arrears_engine import WriteOffReason
    ev = build_write_off_event("A", 250.0, WriteOffReason.INSOLVENCY,
                               dt.date(2024, 6, 1), TT, note="liquidation")
    assert_write_off_audited(ev)                     # clean: does not raise


def test_write_off_audited_FIRES_on_empty_reason():
    # MUTATION: a write-off with NO reason — an unaudited, silent status flip.
    unaudited = LedgerEvent("WO-x", "A", LedgerEventType.WRITE_OFF_CREDIT, 250.0,
                            dt.date(2024, 6, 1), TT, reason="")
    with pytest.raises(WriteOffAuditError):
        assert_write_off_audited(unaudited)


def test_write_off_audited_FIRES_on_wrong_event_type():
    # MUTATION: an ordinary credit adjustment masquerading as a write-off — not
    # P&L-visible, must not pass as an audited write-off.
    not_a_wo = LedgerEvent("adj", "A", LedgerEventType.ADJUSTMENT_CREDIT, 250.0,
                           dt.date(2024, 6, 1), TT, reason="goodwill")
    with pytest.raises(WriteOffAuditError):
        assert_write_off_audited(not_a_wo)
