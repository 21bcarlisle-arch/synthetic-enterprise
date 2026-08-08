"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/arrears_engine.py — ageing, dunning, statutory late-payment
interest (LPCDA 1998) and write-offs. This is what decides when a customer is
chased, how hard, and what interest attaches to their debt.

All dates and rates are literals; every entry point takes `as_of` explicitly, so
there is no wall-clock dependency to work around.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_ledger import AccountLedger, LedgerEvent, LedgerEventType
from company.billing.arrears_engine import (
    AGE_BUCKETS,
    LPCDA_MARGIN,
    AgedItem,
    AgeingPartitionError,
    DunningPathError,
    DunningStep,
    FixedCompensationError,
    StatutoryInterestScopeError,
    WriteOffAuditError,
    WriteOffReason,
    age_balance,
    age_bucket,
    age_open_items,
    ageing_buckets,
    assert_age_buckets_partition,
    assert_ageing_conserves_value,
    assert_dunning_path_valid,
    assert_fixed_compensation_once,
    assert_interest_is_b2b_only,
    assert_write_off_audited,
    build_interest_event,
    build_write_off_event,
    current_dunning_step,
    dunning_path,
    lpcda_fixed_compensation_gbp,
    oldest_unpaid_bill_date,
    statutory_interest_gbp,
)
from company.crm.account_hierarchy import Segment

TT = dt.datetime(2024, 1, 1, 12, 0, 0)


def ev(event_id, event_type, amount, valid_time, account_id="A1", **kw):
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
# age_bucket
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "days,bucket",
    [(-5, "current"), (0, "current"), (29, "current"),
     (30, "30-60"), (59, "30-60"), (60, "60-90"), (89, "60-90"),
     (90, "90+"), (400, "90+")],
)
def test_age_bucket_boundaries_are_inclusive_lower(days, bucket):
    assert age_bucket(days) == bucket


def test_age_bucket_maps_not_yet_due_into_current():
    """Negative days-overdue (a bill not yet due) shares the "current" bucket with
    a bill that is up to 29 days late — the two are indistinguishable downstream."""
    assert age_bucket(-30) == age_bucket(0) == age_bucket(29) == "current"


def test_bucket_partition_control_passes_on_the_real_bucket_function():
    assert_age_buckets_partition()  # does not raise


def test_bucket_partition_control_fires_on_a_bucket_function_with_a_gap():
    with pytest.raises(AgeingPartitionError, match="out-of-set"):
        assert_age_buckets_partition(bucket_fn=lambda d: "nonsense", max_days=5)


def test_bucket_partition_control_fires_on_non_monotonic_severity():
    def regressing(d):
        return "90+" if d < 10 else "current"
    with pytest.raises(AgeingPartitionError, match="regresses severity"):
        assert_age_buckets_partition(bucket_fn=regressing, max_days=20)


# ---------------------------------------------------------------------------
# ageing_buckets
# ---------------------------------------------------------------------------


def _items():
    return [
        AgedItem("INV1", 100.0, dt.date(2024, 1, 1), 5),
        AgedItem("INV2", 200.0, dt.date(2024, 1, 1), 45),
        AgedItem("INV3", 300.0, dt.date(2024, 1, 1), 95),
        AgedItem("INV4", 999.0, dt.date(2024, 1, 1), 95, disputed=True),
    ]


def test_ageing_buckets_excludes_disputed_items():
    b = ageing_buckets(_items())
    assert b["current"] == {"count": 1, "amount_gbp": 100.0}
    assert b["30-60"] == {"count": 1, "amount_gbp": 200.0}
    assert b["60-90"] == {"count": 0, "amount_gbp": 0.0}
    assert b["90+"] == {"count": 1, "amount_gbp": 300.0}  # the £999 disputed is out


def test_ageing_buckets_always_returns_every_bucket_key():
    assert set(ageing_buckets([])) == set(AGE_BUCKETS)


def test_ageing_conservation_control_passes_and_can_fire():
    assert_ageing_conserves_value(_items())  # does not raise

    def lossy(items):
        out = ageing_buckets(items)
        out["90+"]["amount_gbp"] = 0.0  # drop money
        return out

    with pytest.raises(AgeingPartitionError):
        assert_ageing_conserves_value(_items(), aggregator=lossy)


# ---------------------------------------------------------------------------
# oldest_unpaid_bill_date / age_balance — FIFO appropriation
# ---------------------------------------------------------------------------


def _two_bill_ledger():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-01"))
    led.post(ev("b2", LedgerEventType.BILL_DEBIT, 100.0, "2024-03-01"))
    return led


def test_oldest_unpaid_is_none_when_there_are_no_bills():
    assert oldest_unpaid_bill_date(AccountLedger("A1"), dt.date(2024, 6, 1)) is None


def test_oldest_unpaid_advances_once_early_bills_are_covered():
    """FIFO: a £100 payment clears the January bill, so arrears age from March."""
    led = _two_bill_ledger()
    assert oldest_unpaid_bill_date(led, dt.date(2024, 6, 1)) == dt.date(2024, 1, 1)
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 100.0, "2024-04-01"))
    assert oldest_unpaid_bill_date(led, dt.date(2024, 6, 1)) == dt.date(2024, 3, 1)


def test_oldest_unpaid_counts_write_offs_and_credits_as_appropriable_credit():
    """SURPRISE (boundary class): the credit pool sums EVERY non-debit event, so a
    write-off or a goodwill credit adjustment appropriates against the oldest bill
    exactly like cash. Writing off £100 of bad debt therefore makes the remaining
    arrears look YOUNGER (aged from March, not January) and de-escalates dunning."""
    led = _two_bill_ledger()
    led.post(ev("w1", LedgerEventType.WRITE_OFF_CREDIT, 100.0, "2024-04-01",
               reason="bad debt"))
    assert oldest_unpaid_bill_date(led, dt.date(2024, 6, 1)) == dt.date(2024, 3, 1)


def test_oldest_unpaid_returns_none_when_all_bills_are_covered():
    led = _two_bill_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 200.0, "2024-04-01"))
    assert oldest_unpaid_bill_date(led, dt.date(2024, 6, 1)) is None


def test_age_balance_returns_none_when_not_in_arrears():
    led = AccountLedger("A1")
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 50.0, "2024-01-01"))
    assert age_balance(led, dt.date(2024, 6, 1)) is None


def test_age_balance_ages_from_the_oldest_unpaid_bill_plus_payment_terms():
    led = _two_bill_ledger()
    item = age_balance(led, dt.date(2024, 6, 1), payment_terms_days=14)
    assert item.due_date == dt.date(2024, 1, 15)     # 2024-01-01 + 14
    assert item.days_overdue == (dt.date(2024, 6, 1) - dt.date(2024, 1, 15)).days
    assert item.outstanding_gbp == 200.0
    assert item.bucket == "90+"


def test_age_balance_of_a_non_bill_residual_ages_from_as_of_and_reads_current():
    """When every bill is covered and the residual is interest/adjustment, the item
    ages from as_of — so a purely interest-driven arrears never leaves "current"
    and never escalates through dunning."""
    led = _two_bill_ledger()
    led.post(ev("p1", LedgerEventType.PAYMENT_CREDIT, 200.0, "2024-04-01"))
    led.post(ev("i1", LedgerEventType.INTEREST_DEBIT, 25.0, "2024-04-02"))
    item = age_balance(led, dt.date(2024, 6, 1))
    assert item.outstanding_gbp == 25.0
    assert item.days_overdue == 0
    assert item.bucket == "current"


def test_age_open_items_ages_each_invoice_from_its_own_due_date():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-01", invoice_ref="INV1"))
    led.post(ev("b2", LedgerEventType.BILL_DEBIT, 200.0, "2024-05-01", invoice_ref="INV2"))
    items = {i.reference: i for i in age_open_items(led, dt.date(2024, 6, 1))}
    assert items["INV1"].due_date == dt.date(2024, 1, 15)
    assert items["INV1"].bucket == "90+"
    assert items["INV2"].due_date == dt.date(2024, 5, 15)
    assert items["INV2"].bucket == "current"


def test_age_open_items_marks_disputed_but_still_returns_them():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-01-01", invoice_ref="INV1"))
    (item,) = age_open_items(led, dt.date(2024, 6, 1), disputed_refs=["INV1"])
    assert item.disputed is True
    assert ageing_buckets([item])["90+"]["count"] == 0  # excluded at aggregation


def test_days_overdue_is_floored_at_zero_for_a_not_yet_due_invoice():
    led = AccountLedger("A1")
    led.post(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-06-01", invoice_ref="INV1"))
    (item,) = age_open_items(led, dt.date(2024, 6, 5))
    assert item.due_date == dt.date(2024, 6, 15)
    assert item.days_overdue == 0  # max(0, -10) — the -10 is discarded


# ---------------------------------------------------------------------------
# Dunning
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("segment", list(Segment))
def test_every_segment_has_a_valid_ascending_dunning_path(segment):
    path = dunning_path(segment)
    assert path and [s.trigger_days_overdue for s in path] == sorted(
        s.trigger_days_overdue for s in path
    )
    assert_dunning_path_valid(segment)  # does not raise


def test_dunning_path_returns_a_copy_so_callers_cannot_mutate_the_table():
    path = dunning_path(Segment.RESIDENTIAL)
    path.clear()
    assert dunning_path(Segment.RESIDENTIAL)  # original table intact


@pytest.mark.parametrize("segment", list(Segment))
def test_no_dunning_before_day_zero(segment):
    assert current_dunning_step(segment, -1) is None


@pytest.mark.parametrize(
    "segment,days,action",
    [
        (Segment.RESIDENTIAL, 0, "reminder"),
        (Segment.RESIDENTIAL, 28, "repayment_plan_offer"),
        (Segment.RESIDENTIAL, 89, "final_notice"),
        (Segment.RESIDENTIAL, 90, "prepayment_or_debt_agency"),
        (Segment.IC, 7, "interest_notice"),
        (Segment.IC, 35, "commercial_recovery"),
        (Segment.SME, 30, "interest_notice"),
    ],
)
def test_current_dunning_step_selects_the_furthest_reached_trigger(segment, days, action):
    assert current_dunning_step(segment, days).action == action


def test_dunning_selection_is_order_independent_by_taking_the_max_trigger():
    """Hardened against a mis-ordered path: selection takes the largest reached
    trigger rather than breaking on the first unreached one."""
    assert current_dunning_step(Segment.RESIDENTIAL, 1000).action == "prepayment_or_debt_agency"


def test_dunning_path_validity_control_fires_on_a_non_ascending_path():
    bad = [DunningStep(30, "a", "x"), DunningStep(10, "b", "y")]
    with pytest.raises(DunningPathError):
        assert_dunning_path_valid(Segment.RESIDENTIAL, path=bad)


def test_dunning_path_validity_control_fires_on_an_empty_path():
    with pytest.raises(DunningPathError):
        assert_dunning_path_valid(Segment.RESIDENTIAL, path=[])


def test_micro_sme_gets_consumer_shaped_dunning_but_counts_as_business_for_interest():
    """SURPRISE (boundary class): MICRO_SME carries the SLC-27-shaped protective
    dunning path (a repayment-plan offer before enforcement), yet `is_business` is
    True so LPCDA statutory interest DOES attach to it. The two protections are
    decided by different switches on the same segment."""
    assert any(s.action == "repayment_plan_offer" for s in dunning_path(Segment.MICRO_SME))
    assert Segment.MICRO_SME.is_business is True
    assert statutory_interest_gbp(Segment.MICRO_SME, 1000.0, 90, 0.05) > 0


# ---------------------------------------------------------------------------
# Statutory interest (LPCDA 1998)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "debt,fixed",
    [(0.0, 40.0), (999.99, 40.0), (1000.0, 70.0), (9999.99, 70.0),
     (10000.0, 100.0), (50000.0, 100.0)],
)
def test_fixed_compensation_bands(debt, fixed):
    assert lpcda_fixed_compensation_gbp(debt) == fixed


def test_residential_never_accrues_statutory_interest():
    assert statutory_interest_gbp(Segment.RESIDENTIAL, 5000.0, 365, 0.05) == 0.0


def test_statutory_interest_is_simple_pro_rata_plus_the_fixed_sum():
    principal, days, base = 1000.0, 90, 0.05
    expected = principal * (base + LPCDA_MARGIN) * (days / 365.0)
    assert statutory_interest_gbp(Segment.SME, principal, days, base,
                                  include_fixed_compensation=False) == round(expected, 2)
    assert statutory_interest_gbp(Segment.SME, principal, days, base) == round(
        expected + 70.0, 2
    )


def test_interest_uses_a_fixed_365_day_year_ignoring_leap_years():
    """A full leap year (366 days late) accrues 366/365 of a year's interest."""
    a = statutory_interest_gbp(Segment.SME, 1000.0, 365, 0.05, include_fixed_compensation=False)
    b = statutory_interest_gbp(Segment.SME, 1000.0, 366, 0.05, include_fixed_compensation=False)
    assert b > a


@pytest.mark.parametrize("days,principal", [(0, 1000.0), (-5, 1000.0), (90, 0.0), (90, -1.0)])
def test_no_interest_for_non_positive_days_or_principal(days, principal):
    assert statutory_interest_gbp(Segment.SME, principal, days, 0.05) == 0.0


def test_one_day_late_is_dominated_by_the_fixed_statutory_sum():
    """£40.04 on a £100 debt one day late: the s.5A sum is 1000x the interest. This
    is what the statute says, recorded here so a later 'tidy-up' cannot quietly
    drop the fixed sum."""
    assert statutory_interest_gbp(Segment.SME, 100.0, 1, 0.05) == 40.04


def test_a_base_rate_below_minus_eight_percent_yields_negative_interest():
    """SURPRISE (sign class): there is no floor at zero on the rate leg. A BoE base
    rate below -8% makes `annual_rate` negative and the function returns a NEGATIVE
    charge — i.e. statutory late payment would CREDIT the late payer. No UK base
    rate has ever been negative, so this is unreachable from real data today, but
    the guard is absent rather than present-and-satisfied."""
    assert statutory_interest_gbp(Segment.SME, 1000.0, 365, -0.10,
                                  include_fixed_compensation=False) == -20.0
    # With the fixed sum the total swings positive again, masking the negative leg.
    assert statutory_interest_gbp(Segment.SME, 1000.0, 365, -0.10) == 50.0


def test_interest_scope_control_fires_on_b2c_interest():
    assert_interest_is_b2b_only(Segment.SME, 100.0)          # fine
    assert_interest_is_b2b_only(Segment.RESIDENTIAL, 0.0)    # zero is fine
    with pytest.raises(StatutoryInterestScopeError):
        assert_interest_is_b2b_only(Segment.RESIDENTIAL, 0.01)


def test_build_interest_event_returns_none_for_residential():
    assert build_interest_event("A1", Segment.RESIDENTIAL, 1000.0, 90, 0.05,
                                dt.date(2024, 6, 1), TT) is None


def test_build_interest_event_produces_a_pnl_visible_interest_debit():
    e = build_interest_event("A1", Segment.SME, 1000.0, 90, 0.05,
                             dt.date(2024, 6, 1), TT, invoice_ref="INV1")
    assert e.event_type == LedgerEventType.INTEREST_DEBIT
    assert e.affects_pnl is True
    assert e.amount_gbp == 102.05
    assert e.signed_amount == 102.05  # a debit: increases what the customer owes
    assert "s.5A fixed compensation" in e.reason


def test_re_accrual_without_the_flag_recharges_the_fixed_sum_and_the_control_fires():
    """The s.5A sum is a one-off per debt; a caller that forgets
    include_fixed_compensation=False on the second accrual re-charges it, and
    assert_fixed_compensation_once catches it from the ledger side."""
    first = build_interest_event("A1", Segment.SME, 1000.0, 30, 0.05,
                                 dt.date(2024, 4, 1), TT, event_id="i1")
    second = build_interest_event("A1", Segment.SME, 1000.0, 60, 0.05,
                                  dt.date(2024, 5, 1), TT, event_id="i2")
    with pytest.raises(FixedCompensationError, match="charged 2 times"):
        assert_fixed_compensation_once([first, second])

    suppressed = build_interest_event("A1", Segment.SME, 1000.0, 60, 0.05,
                                      dt.date(2024, 5, 1), TT, event_id="i3",
                                      include_fixed_compensation=False)
    assert_fixed_compensation_once([first, suppressed])  # does not raise


def test_fixed_compensation_control_fails_closed_on_a_non_interest_event():
    with pytest.raises(FixedCompensationError, match="not an interest accrual"):
        assert_fixed_compensation_once([ev("b1", LedgerEventType.BILL_DEBIT, 10.0, "2024-01-01")])


# ---------------------------------------------------------------------------
# Write-offs
# ---------------------------------------------------------------------------


def test_build_write_off_event_is_dated_reasoned_and_pnl_visible():
    e = build_write_off_event("A1", 250.0, WriteOffReason.INSOLVENCY,
                              dt.date(2024, 6, 1), TT, invoice_ref="INV1", note="liquidated")
    assert e.event_type == LedgerEventType.WRITE_OFF_CREDIT
    assert e.affects_pnl is True
    assert e.signed_amount == -250.0  # a credit: reduces what the customer owes
    assert e.reason == "write-off (insolvency): liquidated"
    assert e.event_id == "WO-A1-INV1-2024-06-01"


def test_write_off_event_id_defaults_to_bal_when_no_invoice_ref():
    e = build_write_off_event("A1", 10.0, WriteOffReason.INSOLVENCY, dt.date(2024, 6, 1), TT)
    assert e.event_id == "WO-A1-BAL-2024-06-01"


@pytest.mark.parametrize("amount", [0.0, -1.0])
def test_write_off_rejects_non_positive_amounts(amount):
    with pytest.raises(ValueError, match="must be positive"):
        build_write_off_event("A1", amount, WriteOffReason.INSOLVENCY,
                              dt.date(2024, 6, 1), TT)


def test_write_off_audit_control_fires_on_a_blank_reason():
    silent = ev("w1", LedgerEventType.WRITE_OFF_CREDIT, 100.0, "2024-06-01", reason="")
    with pytest.raises(WriteOffAuditError, match="no reason"):
        assert_write_off_audited(silent)


def test_write_off_audit_control_fires_on_the_wrong_event_type():
    with pytest.raises(WriteOffAuditError, match="not a write-off"):
        assert_write_off_audited(ev("b1", LedgerEventType.BILL_DEBIT, 100.0, "2024-06-01"))


def test_two_write_offs_on_the_same_account_day_and_invoice_collide_on_event_id():
    """SURPRISE (boundary class, money-relevant): the default event_id is
    account+invoice+date with no sequence, so two partial write-offs booked against
    the same balance on the same day produce the SAME id. AccountLedger.post dedups
    on event_id, so the second is silently discarded and only the first amount is
    ever written off."""
    a = build_write_off_event("A1", 100.0, WriteOffReason.INSOLVENCY, dt.date(2024, 6, 1), TT)
    b = build_write_off_event("A1", 250.0, WriteOffReason.GONE_AWAY, dt.date(2024, 6, 1), TT)
    assert a.event_id == b.event_id
    led = AccountLedger("A1")
    assert led.post(a) is True
    assert led.post(b) is False
    assert led.balance() == -100.0  # not -350.0
