import pytest
from datetime import date

from company.regulatory.gsop_tracker import (
    GSoPBreach,
    GSoPBreachStatus,
    GSoPStandard,
    GSoPTracker,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker():
    return GSoPTracker()


# ---------------------------------------------------------------------------
# 1. GSoPBreach is frozen (cannot assign attributes)
# ---------------------------------------------------------------------------

def test_breach_is_frozen():
    breach = GSoPBreach(
        breach_id="GSOP-0001",
        account_id="ACC-001",
        standard=GSoPStandard.BILLING_DELAY,
        breach_date=date(2023, 1, 10),
        compensation_gbp=30.0,
        status=GSoPBreachStatus.OPEN,
    )
    import dataclasses
    with pytest.raises(dataclasses.FrozenInstanceError):
        breach.notes = "changed"


# ---------------------------------------------------------------------------
# 2. working_days_open counts Mon-Fri only (skip weekends)
# ---------------------------------------------------------------------------

def test_working_days_open_skips_weekends():
    # 2023-03-13 Monday -> 2023-03-20 Monday = 5 Mon-Fri days (Mon Tue Wed Thu Fri)
    breach = GSoPBreach(
        breach_id="GSOP-0001",
        account_id="ACC-001",
        standard=GSoPStandard.BILLING_DELAY,
        breach_date=date(2023, 3, 13),  # Monday
        compensation_gbp=30.0,
        status=GSoPBreachStatus.COMPENSATED,
        resolution_date=date(2023, 3, 20),  # next Monday (7 calendar days, 5 working)
    )
    assert breach.working_days_open == 5


def test_working_days_open_uses_today_when_no_resolution(tracker):
    # A breach recorded today with no resolution_date should have 0 working days open
    breach = tracker.record_breach("ACC-001", GSoPStandard.APPOINTMENT_MISSED, date.today())
    assert breach.working_days_open == 0


# ---------------------------------------------------------------------------
# 3. compensation_gbp is always 30.0
# ---------------------------------------------------------------------------

def test_compensation_is_always_30(tracker):
    for standard in GSoPStandard:
        b = tracker.record_breach("ACC-X", standard, date(2023, 6, 1))
        assert b.compensation_gbp == 30.0


# ---------------------------------------------------------------------------
# 4. record_breach returns OPEN breach with correct fields
# ---------------------------------------------------------------------------

def test_record_breach_correct_fields(tracker):
    b = tracker.record_breach(
        "ACC-42",
        GSoPStandard.FINAL_BILL_DELAY,
        date(2023, 4, 5),
        notes="delay note",
    )
    assert b.account_id == "ACC-42"
    assert b.standard == GSoPStandard.FINAL_BILL_DELAY
    assert b.breach_date == date(2023, 4, 5)
    assert b.notes == "delay note"
    assert b.status == GSoPBreachStatus.OPEN
    assert b.breach_id.startswith("GSOP-")


# ---------------------------------------------------------------------------
# 5. Recorded breach appears in open_breaches()
# ---------------------------------------------------------------------------

def test_recorded_breach_in_open_breaches(tracker):
    b = tracker.record_breach("ACC-1", GSoPStandard.DEBT_QUERY_DELAY, date(2023, 2, 1))
    assert b in tracker.open_breaches()


# ---------------------------------------------------------------------------
# 6. compensate_breach transitions to COMPENSATED with resolution_date
# ---------------------------------------------------------------------------

def test_compensate_breach(tracker):
    b = tracker.record_breach("ACC-2", GSoPStandard.DIRECT_DEBIT_ERROR, date(2023, 3, 1))
    resolved = tracker.compensate_breach(b.breach_id, date(2023, 3, 10))
    assert resolved.status == GSoPBreachStatus.COMPENSATED
    assert resolved.resolution_date == date(2023, 3, 10)
    assert resolved not in tracker.open_breaches()


# ---------------------------------------------------------------------------
# 7. waive_breach transitions to WAIVED
# ---------------------------------------------------------------------------

def test_waive_breach(tracker):
    b = tracker.record_breach("ACC-3", GSoPStandard.METER_READ_DISPUTE, date(2023, 5, 1))
    waived = tracker.waive_breach(b.breach_id)
    assert waived.status == GSoPBreachStatus.WAIVED
    assert waived not in tracker.open_breaches()


# ---------------------------------------------------------------------------
# 8. total_compensation_outstanding_gbp sums only OPEN breaches
# ---------------------------------------------------------------------------

def test_outstanding_sums_only_open(tracker):
    b1 = tracker.record_breach("ACC-1", GSoPStandard.SWITCHING_DELAY, date(2023, 1, 1))
    b2 = tracker.record_breach("ACC-2", GSoPStandard.SWITCHING_DELAY, date(2023, 1, 2))
    tracker.compensate_breach(b2.breach_id, date(2023, 1, 15))
    # Only b1 is OPEN
    assert tracker.total_compensation_outstanding_gbp() == 30.0


# ---------------------------------------------------------------------------
# 9. total_compensation_paid_gbp sums only COMPENSATED breaches
# ---------------------------------------------------------------------------

def test_paid_sums_only_compensated(tracker):
    b1 = tracker.record_breach("ACC-1", GSoPStandard.RECONNECTION_DELAY, date(2023, 1, 1))
    b2 = tracker.record_breach("ACC-2", GSoPStandard.RECONNECTION_DELAY, date(2023, 1, 2))
    tracker.compensate_breach(b1.breach_id, date(2023, 1, 10))
    # b2 is OPEN, b1 is COMPENSATED
    assert tracker.total_compensation_paid_gbp() == 30.0


# ---------------------------------------------------------------------------
# 10. breach_rate_per_100_customers correct
# ---------------------------------------------------------------------------

def test_breach_rate_correct(tracker):
    tracker.record_breach("ACC-1", GSoPStandard.BILLING_DELAY, date(2023, 1, 1))
    tracker.record_breach("ACC-2", GSoPStandard.BILLING_DELAY, date(2023, 1, 2))
    # 2 breaches / 200 customers * 100 = 1.0
    assert tracker.breach_rate_per_100_customers(200) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 11. breach_rate_per_100_customers returns 0.0 when total_customers == 0
# ---------------------------------------------------------------------------

def test_breach_rate_zero_customers(tracker):
    tracker.record_breach("ACC-1", GSoPStandard.BILLING_DELAY, date(2023, 1, 1))
    assert tracker.breach_rate_per_100_customers(0) == 0.0


# ---------------------------------------------------------------------------
# 12. breaches_for_standard filters correctly
# ---------------------------------------------------------------------------

def test_breaches_for_standard_filters(tracker):
    tracker.record_breach("ACC-1", GSoPStandard.BILLING_DELAY, date(2023, 1, 1))
    tracker.record_breach("ACC-2", GSoPStandard.BILLING_DELAY, date(2023, 1, 2))
    tracker.record_breach("ACC-3", GSoPStandard.COMPLAINT_NO_RESPONSE, date(2023, 1, 3))
    billing = tracker.breaches_for_standard(GSoPStandard.BILLING_DELAY)
    complaint = tracker.breaches_for_standard(GSoPStandard.COMPLAINT_NO_RESPONSE)
    assert len(billing) == 2
    assert len(complaint) == 1


# ---------------------------------------------------------------------------
# 13. is_systemic: True when >5 same-standard breaches, False when <=5
# ---------------------------------------------------------------------------

def test_is_systemic_false_when_five_or_fewer(tracker):
    for i in range(5):
        tracker.record_breach(
            "ACC-{}".format(i), GSoPStandard.COMPLAINT_UNRESOLVED, date(2023, 1, i + 1)
        )
    assert tracker.is_systemic(GSoPStandard.COMPLAINT_UNRESOLVED) is False


def test_is_systemic_true_when_more_than_five(tracker):
    for i in range(6):
        tracker.record_breach(
            "ACC-{}".format(i), GSoPStandard.COMPLAINT_UNRESOLVED, date(2023, 1, i + 1)
        )
    assert tracker.is_systemic(GSoPStandard.COMPLAINT_UNRESOLVED) is True


# ---------------------------------------------------------------------------
# 14. gsop_summary has all required keys and correct totals
# ---------------------------------------------------------------------------

def test_gsop_summary_keys_and_totals(tracker):
    b1 = tracker.record_breach("ACC-1", GSoPStandard.BILLING_DELAY, date(2023, 1, 1))
    b2 = tracker.record_breach("ACC-2", GSoPStandard.BILLING_DELAY, date(2023, 1, 2))
    b3 = tracker.record_breach("ACC-3", GSoPStandard.APPOINTMENT_MISSED, date(2023, 1, 3))
    tracker.compensate_breach(b1.breach_id, date(2023, 1, 15))
    tracker.waive_breach(b2.breach_id)

    summary = tracker.gsop_summary()

    required_keys = {
        "total_breaches", "open_count", "compensated_count", "waived_count",
        "outstanding_gbp", "paid_gbp", "systemic_standards", "breach_rate_note",
    }
    assert required_keys.issubset(summary.keys())

    assert summary["total_breaches"] == 3
    assert summary["open_count"] == 1       # b3
    assert summary["compensated_count"] == 1  # b1
    assert summary["waived_count"] == 1     # b2
    assert summary["outstanding_gbp"] == 30.0
    assert summary["paid_gbp"] == 30.0
    assert isinstance(summary["systemic_standards"], list)
