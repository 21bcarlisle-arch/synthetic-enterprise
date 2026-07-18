"""Tests for arrears physics: ageing, dunning, LPCDA interest, write-offs (M2/D5)."""
import datetime as dt

import pytest

from company.billing.account_ledger import (
    AccountLedger,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.arrears_engine import (
    LPCDA_MARGIN,
    WriteOffReason,
    age_balance,
    age_bucket,
    age_open_items,
    ageing_buckets,
    build_interest_event,
    build_write_off_event,
    collections_snapshot,
    current_dunning_step,
    dunning_path,
    lpcda_fixed_compensation_gbp,
    statutory_interest_gbp,
)
from company.crm.account_hierarchy import Segment

TT = dt.datetime(2024, 1, 1, 12, 0, 0)


def _bill(eid, acct, amount, day, ref=None):
    return LedgerEvent(eid, acct, LedgerEventType.BILL_DEBIT, amount,
                       dt.date(2024, 1, day), TT, invoice_ref=ref)


# --- ageing buckets ---

@pytest.mark.parametrize("days,bucket", [
    (0, "current"), (29, "current"), (30, "30-60"), (59, "30-60"),
    (60, "60-90"), (89, "60-90"), (90, "90+"), (400, "90+"),
])
def test_age_bucket_boundaries(days, bucket):
    assert age_bucket(days) == bucket

def test_age_open_items_and_buckets():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))   # issued 01-Jan, due 15-Jan
    items = age_open_items(led, as_of=dt.date(2024, 3, 20), payment_terms_days=14)
    assert len(items) == 1
    assert items[0].days_overdue == (dt.date(2024, 3, 20) - dt.date(2024, 1, 15)).days
    assert items[0].bucket == "60-90"
    b = ageing_buckets(items)
    assert b["60-90"]["amount_gbp"] == 100.0

def test_disputed_item_excluded_from_buckets():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))
    led.post(_bill("b2", "A", 200.0, 1, ref="INV2"))
    items = age_open_items(led, as_of=dt.date(2024, 4, 1), disputed_refs=["INV1"])
    b = ageing_buckets(items)
    total = sum(v["amount_gbp"] for v in b.values())
    assert total == 200.0    # disputed INV1 excluded, only INV2 counted

def test_age_balance_fifo_from_oldest_bill():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))    # oldest, due 15-Jan
    led.post(_bill("b2", "A", 50.0, 20))
    item = age_balance(led, as_of=dt.date(2024, 3, 1), payment_terms_days=14)
    assert item.outstanding_gbp == 150.0
    assert item.due_date == dt.date(2024, 1, 15)   # aged from oldest

def test_age_balance_none_when_not_in_arrears():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1))
    led.post(LedgerEvent("p1", "A", LedgerEventType.PAYMENT_CREDIT, 100.0,
                         dt.date(2024, 1, 5), TT))
    assert age_balance(led, as_of=dt.date(2024, 3, 1)) is None


# --- dunning ---

def test_dunning_paths_exist_per_segment():
    for seg in (Segment.RESIDENTIAL, Segment.MICRO_SME, Segment.SME, Segment.IC):
        assert len(dunning_path(seg)) > 0

def test_resi_dunning_offers_repayment_plan_before_enforcement():
    step = current_dunning_step(Segment.RESIDENTIAL, 30)
    assert step.action == "repayment_plan_offer"   # SLC 27 ability-to-pay

def test_ic_dunning_escalates_faster():
    # I&C hits final demand by 21 days; resi is nowhere near enforcement then
    assert current_dunning_step(Segment.IC, 21).action == "final_demand"
    assert current_dunning_step(Segment.RESIDENTIAL, 21).action == "reminder_2"

def test_no_dunning_before_first_trigger():
    assert current_dunning_step(Segment.RESIDENTIAL, -1) is None


# --- LPCDA statutory interest (B2B only) ---

def test_residential_never_accrues_statutory_interest():
    assert statutory_interest_gbp(Segment.RESIDENTIAL, 1000.0, 90, 0.05) == 0.0

def test_b2b_interest_base_plus_8pp():
    # £10,000, 365 days, base 2% -> rate 10% -> £1000 interest + £100 fixed
    amt = statutory_interest_gbp(Segment.SME, 10000.0, 365, 0.02)
    assert amt == pytest.approx(10000 * 0.10 + 100.0, abs=0.01)

def test_lpcda_margin_is_8pp():
    assert LPCDA_MARGIN == 0.08

@pytest.mark.parametrize("debt,fixed", [(500, 40.0), (5000, 70.0), (50000, 100.0)])
def test_fixed_compensation_bands(debt, fixed):
    assert lpcda_fixed_compensation_gbp(debt) == fixed

def test_interest_zero_when_not_late():
    assert statutory_interest_gbp(Segment.IC, 5000.0, 0, 0.05) == 0.0

def test_build_interest_event_none_for_resi():
    assert build_interest_event("A", Segment.RESIDENTIAL, 1000.0, 90, 0.05,
                                dt.date(2024, 4, 1), TT) is None

def test_build_interest_event_b2b_produces_debit():
    ev = build_interest_event("A", Segment.IC, 10000.0, 365, 0.02,
                              dt.date(2024, 4, 1), TT, invoice_ref="INV1")
    assert ev.event_type == LedgerEventType.INTEREST_DEBIT
    assert ev.affects_pnl
    assert ev.signed_amount > 0


# --- write-offs ---

def test_write_off_event_is_credit_and_pnl_visible():
    ev = build_write_off_event("A", 250.0, WriteOffReason.GONE_AWAY,
                               dt.date(2024, 6, 1), TT, note="no forwarding address")
    assert ev.event_type == LedgerEventType.WRITE_OFF_CREDIT
    assert ev.affects_pnl
    assert ev.signed_amount == -250.0        # reduces amount owed
    assert "gone_away" in ev.reason and "no forwarding" in ev.reason

def test_write_off_clears_balance_when_posted():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 250.0, 1))
    led.post(build_write_off_event("A", 250.0, WriteOffReason.INSOLVENCY,
                                   dt.date(2024, 6, 1), TT))
    assert led.balance() == 0.0

def test_write_off_negative_amount_rejected():
    with pytest.raises(ValueError):
        build_write_off_event("A", -10.0, WriteOffReason.GOODWILL, dt.date(2024, 6, 1), TT)


# --- collections snapshot over both models ---

def test_collections_snapshot_open_item_excludes_disputed():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 100.0, 1, ref="INV1"))   # disputed
    led.post(_bill("b2", "A", 200.0, 1, ref="INV2"))
    snap = collections_snapshot(led, Segment.IC, True, dt.date(2024, 4, 1),
                                disputed_refs=["INV1"])
    assert snap["disputed_excluded_count"] == 1
    assert snap["undisputed_overdue_gbp"] == 200.0
    assert snap["interest_bearing"] is True

def test_collections_snapshot_balance_based_resi():
    led = AccountLedger("A")
    led.post(_bill("b1", "A", 120.0, 1))
    snap = collections_snapshot(led, Segment.RESIDENTIAL, False, dt.date(2024, 3, 1))
    assert snap["accounting_model"] == "balance_based"
    assert snap["undisputed_overdue_gbp"] == 120.0
    assert snap["interest_bearing"] is False
