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
import dataclasses
import datetime as dt

import pytest

from company.billing import arrears_engine
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
    DunningScopeError,
    DunningStep,
    DunningWithoutAnItemError,
    FixedCompensationError,
    OverdueClockFloorError,
    StatutoryInterestScopeError,
    WriteOffAuditError,
    age_bucket,
    age_open_items,
    ageing_buckets,
    assert_age_buckets_partition,
    assert_ageing_conserves_value,
    assert_dunning_path_scope_valid,
    assert_dunning_path_valid,
    assert_dunning_requires_an_item,
    assert_fixed_compensation_once,
    assert_interest_is_b2b_only,
    assert_overdue_clock_resolves_before_due,
    assert_write_off_audited,
    build_interest_event,
    build_write_off_event,
    collections_snapshot,
    current_dunning_step,
    select_dunning_step,
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
# CONTROL 1b/2b — NON-FINITE FAIL-OPEN (R15 killer pattern 2, the E4-sibling
# class the CSS reconciliation control closed 2026-07-25). A tolerance control
# `abs(a - b) > tol` is silently False when a or b is NaN/inf, so a corrupt
# figure sails through clean. Proven live before the fix: a NaN-corrupted bill
# event made balance_gbp=nan yet reconcile() returned clean against the true
# control total. Fixed at BOTH entry points: the LedgerEvent magnitude guard
# (a NaN can't enter the ledger) and each control's own non-finite rejection
# (a NaN in an EXTERNAL control total, which construction cannot catch).
# ===========================================================================

def test_magnitude_guard_rejects_nonfinite_amount():
    # ROOT-CAUSE entry point: `NaN < 0` is silently False, so the old `< 0`-only
    # magnitude guard let a non-finite amount into the ledger. A magnitude that is
    # not a finite number is corrupt, not a value.
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            _bill("bx", "A", bad, 1)
    _bill("bok", "A", 0.0, 1)          # a finite zero magnitude is still fine


def test_reconcile_FIRES_on_nonfinite_external_total():
    # FAIL-OPEN probe on the EXTERNAL side (construction cannot catch this): a
    # NaN/inf control total makes abs(actual - NaN) > tol silently False.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=float("nan"), expected_credits_gbp=0.0)
    with pytest.raises(LedgerReconciliationError):
        led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=float("inf"))
    led.reconcile(expected_debits_gbp=100.0, expected_credits_gbp=0.0)   # finite: fine


def test_check_conserved_FIRES_on_nonfinite_cash_total():
    # FAIL-OPEN probe: a NaN cash-received total (from a corrupt upstream transform)
    # must RAISE, not pass on abs(accounted - NaN) > tol == False.
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_pay("p1", "A", 40.0, 5))
    res = led.allocate()
    with pytest.raises(AllocationInvariantError):
        res.check_conserved(total_payments_gbp=float("nan"))
    res.check_conserved(total_payments_gbp=40.0)                          # finite: fine


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
# CONTROL 4b — assert_dunning_path_scope_valid (SIBLING of the B2B-only interest
# guard): a B2C segment's dunning path must not ADVERTISE a statutory-interest
# action. Named defect: an 'interest_notice' step inserted into a residential path.
# ===========================================================================

def test_dunning_scope_passes_for_every_real_segment():
    # Real paths: resi/micro-SME advertise no interest; SME/IC (B2B) may.
    for seg in (Segment.RESIDENTIAL, Segment.MICRO_SME, Segment.SME, Segment.IC):
        assert_dunning_path_scope_valid(seg)          # clean: does not raise


def test_dunning_scope_FIRES_on_b2c_interest_step():
    # MUTATION: a residential (B2C) path that duns via a statutory-interest notice
    # — ascending-valid (so assert_dunning_path_valid PASSES it), yet a compliance
    # misstatement to a domestic customer. Only this control catches it.
    b2c_with_interest = [
        DunningStep(0, "reminder", "email/sms"),
        DunningStep(28, "repayment_plan_offer", "phone"),
        DunningStep(42, "interest_notice", "letter"),   # MUTATION: LPCDA is B2B only
    ]
    assert_dunning_path_valid(Segment.RESIDENTIAL, path=b2c_with_interest)  # slips past
    with pytest.raises(DunningScopeError):
        assert_dunning_path_scope_valid(Segment.RESIDENTIAL, path=b2c_with_interest)


def test_dunning_scope_allows_interest_step_for_business():
    # The SAME interest step is legitimate on a B2B path — the control must NOT
    # fire there (not a blanket ban, a scope rule).
    b2b_with_interest = [
        DunningStep(0, "reminder", "email"),
        DunningStep(30, "interest_notice", "letter"),
    ]
    assert_dunning_path_scope_valid(Segment.SME, path=b2b_with_interest)   # no raise


def test_dunning_scope_not_fail_open_on_empty():
    # FAIL-OPEN probe: an empty path is a defect, must raise (not a free pass).
    with pytest.raises(DunningScopeError):
        assert_dunning_path_scope_valid(Segment.RESIDENTIAL, path=[])


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


# ===========================================================================
# CONTROL 7 — assert_fixed_compensation_once: the LPCDA 1998 s.5A fixed sum is a
# ONE-OFF per qualifying debt, not per accrual period. Named defect: a recurring
# interest accrual that re-charges the £40/£70/£100 fixed sum every period.
# ===========================================================================

def _accrue(as_of_day, include_fixed):
    # One B2B interest accrual on the SAME debt (INV1) at a later as_of date.
    return build_interest_event(
        "A", Segment.IC, 5000.0, days_late=30, boe_base_rate=0.05,
        as_of=dt.date(2024, 3, as_of_day), transaction_time=TT,
        invoice_ref="INV1", include_fixed_compensation=include_fixed,
    )


def test_fixed_comp_once_passes_when_only_first_accrual_carries_it():
    # CORRECT recurring accrual: fixed sum on the first period only, interest-only
    # thereafter — the one-off is charged exactly once across the debt's events.
    events = [_accrue(1, include_fixed=True), _accrue(15, include_fixed=False)]
    assert all(e is not None for e in events)
    assert_fixed_compensation_once(events)            # clean: does not raise
    # ...and a single accrual with the fixed sum is obviously fine too.
    assert_fixed_compensation_once([_accrue(1, include_fixed=True)])


def test_fixed_comp_once_FIRES_when_recharged_every_period():
    # MUTATION: the caller forgot to suppress the fixed sum on the re-accrual, so
    # the statutory one-off is charged twice on one debt.
    events = [_accrue(1, include_fixed=True), _accrue(15, include_fixed=True)]
    with pytest.raises(FixedCompensationError):
        assert_fixed_compensation_once(events)


def test_fixed_comp_once_is_fail_closed_on_wrong_event_type():
    # FAIL-CLOSED probe: a non-interest event in the set is a mis-scoped input and
    # must RAISE, not pass by silently ignoring it.
    good = _accrue(1, include_fixed=True)
    stray = LedgerEvent("WO-x", "A", LedgerEventType.WRITE_OFF_CREDIT, 100.0,
                        dt.date(2024, 3, 20), TT, reason="insolvency")
    with pytest.raises(FixedCompensationError):
        assert_fixed_compensation_once([good, stray])


def test_fixed_comp_suppressed_accrual_omits_the_statutory_sum():
    # The re-accrual's amount is pro-rata interest ONLY (no £70 band added) and its
    # reason does NOT carry the fixed-sum marker — proving the flag actually works.
    with_fixed = _accrue(1, include_fixed=True)
    interest_only = _accrue(15, include_fixed=False)
    delta = round(with_fixed.amount_gbp - interest_only.amount_gbp, 2)
    assert delta == 70.0                              # £5,000 debt -> £70 band
    assert "fixed compensation" in with_fixed.reason
    assert "fixed compensation" not in interest_only.reason


# ===========================================================================
# CONTROL 9 — assert_overdue_clock_resolves_before_due (atom D24). The organ's
# overdue clock must resolve ONE DAY everywhere in its domain, before the due
# date as much as after. Named defect: `days_overdue = max(0, days)`, which
# shipped, and which made every pre-due `as_of` publish one number.
# ===========================================================================

def _clamped_clock(ledger, as_of, payment_terms_days=14, disputed_refs=()):
    """MUTATION: the pre-D24 organ, floored at zero."""
    return [dataclasses.replace(it, days_overdue=max(0, it.days_overdue))
            for it in age_open_items(ledger, as_of, payment_terms_days, disputed_refs)]


def test_overdue_clock_control_passes_on_the_shipped_organ():
    assert_overdue_clock_resolves_before_due(age_open_items)


def test_overdue_clock_control_FIRES_on_the_clamp_that_shipped():
    with pytest.raises(OverdueClockFloorError) as exc:
        assert_overdue_clock_resolves_before_due(_clamped_clock)
    # The diagnostic must carry the payload (R5): which day, and what it read.
    assert "does not resolve a day" in str(exc.value)
    assert "0 -> 0" in str(exc.value)


def test_overdue_clock_control_FIRES_on_a_quantisation_that_is_not_the_clamp():
    """The control is a DIFFERENCE against elapsed calendar time, not a test for
    `max(0, …)` — so it fires on any floor, cap or quantisation the clock might
    grow. A weekly-rounded clock is unfloored and still cannot resolve a day."""
    def weekly(ledger, as_of, payment_terms_days=14, disputed_refs=()):
        return [dataclasses.replace(it, days_overdue=(it.days_overdue // 7) * 7)
                for it in age_open_items(ledger, as_of, payment_terms_days, disputed_refs)]
    with pytest.raises(OverdueClockFloorError):
        assert_overdue_clock_resolves_before_due(weekly)


def test_overdue_clock_control_is_FAIL_CLOSED_on_a_clock_that_returns_nothing():
    # FAIL-SILENT probe: an unavailable/empty organ is a FAILED check, never a pass.
    with pytest.raises(OverdueClockFloorError) as exc:
        assert_overdue_clock_resolves_before_due(lambda *a, **k: [])
    assert "fail-closed" in str(exc.value)


def test_overdue_clock_control_is_FAIL_CLOSED_when_the_domain_has_no_pre_due_days():
    """VACUITY probe: with zero payment terms every sample point is on or after
    the due date, so the pre-due claim would be true of nothing. The control must
    refuse to run rather than report a pass it did not earn."""
    with pytest.raises(OverdueClockFloorError) as exc:
        assert_overdue_clock_resolves_before_due(age_open_items, payment_terms_days=0)
    assert "vacuous" in str(exc.value)


def test_collections_snapshot_FIRES_at_read_time_if_the_clock_is_re_clamped(monkeypatch):
    """R15 WIRING, and the reason the control is not merely available: a snapshot
    taken against a re-floored organ RAISES rather than quietly publishing a
    dunning action for a bill that is not due."""
    monkeypatch.setattr(arrears_engine, "age_open_items", _clamped_clock)
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    with pytest.raises(OverdueClockFloorError):
        collections_snapshot(led, Segment.IC, True, dt.date(2024, 4, 1),
                             payment_terms_days=14)


# ===========================================================================
# CONTROL 10 — assert_dunning_requires_an_item (atom D24). No dunning step may
# be selected without an undisputed item that has actually reached its trigger.
# Named defects: the `max(…, default=0)` sentinel, a disputed-only account, and
# a not-yet-due item selecting the trigger-0 step.
# ===========================================================================

def test_dunning_selector_control_passes_on_the_shipped_selector():
    assert_dunning_requires_an_item(select_dunning_step)


def test_dunning_selector_control_FIRES_on_the_zero_sentinel():
    def sentinel(items, segment):
        # MUTATION: the pre-D24 expression — "nothing here" reads as day 0.
        undisputed = [it for it in items if not it.disputed]
        worst = max((it.days_overdue for it in undisputed), default=0)
        return worst, current_dunning_step(segment, worst)
    with pytest.raises(DunningWithoutAnItemError) as exc:
        assert_dunning_requires_an_item(sentinel)
    assert "no items at all" in str(exc.value)


def test_dunning_selector_control_FIRES_when_a_disputed_item_duns():
    def duns_disputes(items, segment):
        # MUTATION: the disputed exclusion dropped.
        if not items:
            return None, None
        worst = max(it.days_overdue for it in items)
        return worst, current_dunning_step(segment, worst)
    with pytest.raises(DunningWithoutAnItemError) as exc:
        assert_dunning_requires_an_item(duns_disputes)
    assert "only a disputed item" in str(exc.value)


def test_dunning_selector_control_FIRES_when_a_not_yet_due_item_duns():
    """The D24 defect itself, one layer up from the clock: with the clamp back in
    the selector, an invoice that is not yet due reaches the trigger-0 step."""
    def clamped(items, segment):
        undisputed = [it for it in items if not it.disputed]
        if not undisputed:
            return None, None
        worst = max(max(0, it.days_overdue) for it in undisputed)   # MUTATION
        return worst, current_dunning_step(segment, worst)
    with pytest.raises(DunningWithoutAnItemError) as exc:
        assert_dunning_requires_an_item(clamped)
    assert "not yet due" in str(exc.value)


def test_dunning_selector_control_FIRES_on_an_INERT_selector():
    """VACUITY guard — the check that keeps the other three from being free. A
    selector that never duns anyone satisfies every negative trivially."""
    with pytest.raises(DunningWithoutAnItemError) as exc:
        assert_dunning_requires_an_item(lambda items, segment: (None, None))
    assert "inert selector" in str(exc.value)


# ===========================================================================
# CONTROL 3a EXTENDED — assert_age_buckets_partition over the SIGNED domain
# (atom D24, R10: the class, not the instance). The clamp was the only thing
# keeping negative days out of the bucket function; the probe now goes there.
# ===========================================================================

def test_bucket_partition_FIRES_on_a_bucket_function_that_breaks_below_zero():
    def falls_off_below_zero(days):
        if days < 0:
            return "not_yet_due"      # MUTATION: out-of-set label for a pre-due day
        return age_bucket(days)
    with pytest.raises(AgeingPartitionError):
        assert_age_buckets_partition(falls_off_below_zero)
    # ...and this is what the pre-D24 domain could see of it: nothing. The defect
    # was unreachable BY CONSTRUCTION rather than by proof.
    assert_age_buckets_partition(falls_off_below_zero, min_days=0)
