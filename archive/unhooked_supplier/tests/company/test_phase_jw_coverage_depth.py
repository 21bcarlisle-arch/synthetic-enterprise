# Increment 3: the legs of tests/company/test_phase_jw_coverage_depth.py that test archived modules. Its live legs stay there.
"""Phase JW: Coverage Depth Sprint XLV -- 30 tests."""
import datetime as dt
import pytest
from company.crm.switch_analytics import SwitchDirection, SwitchStatus, SwitchAnalytics
from company.market.gas_interruption import (
    InterruptClass, InterruptionReason, InterruptionStatus,
    GasInterruption, InterruptibilityContract, GasInterruptionManager,
)

# switch_analytics

def test_sa_days_to_complete_none_when_incomplete():
    book = SwitchAnalytics("SA")
    ev = book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 3, 1))
    assert ev.days_to_complete is None


def test_sa_is_completed_false_when_initiated():
    book = SwitchAnalytics("SA")
    ev = book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 3, 1))
    assert ev.is_completed is False


def test_sa_avg_days_none_when_no_completed_in_year():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 3, 1))
    assert book.avg_days_to_complete(2022) is None


def test_sa_erroneous_year_filter_excludes_other_year():
    book = SwitchAnalytics("SA")
    ev = book.record("M001", None, SwitchDirection.LOSS, "SA", "SB", dt.date(2022, 5, 1))
    book.mark_erroneous(ev.event_id)
    assert len(book.erroneous_transfers_in_year(2023)) == 0


def test_sa_gains_empty_when_no_gains_that_year():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 1, 1))
    assert book.gains_in_year(2021) == []


def test_sa_losses_empty_when_no_losses():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 1, 1))
    assert book.losses_in_year(2022) == []


def test_sa_net_negative_more_losses_than_gains():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 1, 1))
    book.record("M002", "C002", SwitchDirection.LOSS, "SA", "SB", dt.date(2022, 2, 1))
    book.record("M003", "C003", SwitchDirection.LOSS, "SA", "SC", dt.date(2022, 3, 1))
    assert book.net_customer_change(2022) == -1


def test_sa_annual_summary_net_matches_gains_minus_losses():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 1, 1))
    book.record("M002", "C002", SwitchDirection.GAIN, "SC", "SA", dt.date(2022, 2, 1))
    book.record("M003", "C003", SwitchDirection.LOSS, "SA", "SD", dt.date(2022, 3, 1))
    s = book.annual_summary(2022)
    assert s["net"] == s["gains"] - s["losses"]


def test_sa_annual_summary_empty_year_all_zeros():
    book = SwitchAnalytics("SA")
    book.record("M001", "C001", SwitchDirection.GAIN, "SB", "SA", dt.date(2022, 1, 1))
    s = book.annual_summary(2021)
    assert s["gains"] == 0 and s["losses"] == 0 and s["net"] == 0 and s["erroneous_transfers"] == 0


def test_sa_record_loss_stores_direction():
    book = SwitchAnalytics("SA")
    ev = book.record("M001", "C001", SwitchDirection.LOSS, "SA", "SB", dt.date(2022, 6, 1))
    assert ev.direction == SwitchDirection.LOSS
    assert len(book.losses_in_year(2022)) == 1


def test_gi_emergency_only_discount_15pct():
    c = InterruptibilityContract("C001", "MPRN001", InterruptClass.EMERGENCY_ONLY, 1, 0)
    assert c.discount_pct == 15.0


def test_gi_actual_duration_none_when_not_restored():
    gi = GasInterruption("INT001", "C001", "M001", InterruptionReason.NON_PAYMENT, dt.date(2022, 3, 1), dt.date(2022, 3, 5), dt.date(2022, 3, 10))
    assert gi.actual_duration_days is None


def test_gi_interruptions_for_customer_filter():
    mgr = GasInterruptionManager()
    mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.NON_PAYMENT, dt.date(2022, 1, 1), dt.date(2022, 1, 2), dt.date(2022, 1, 5))
    mgr.issue_interruption("INT002", "C002", "M002", InterruptionReason.NON_PAYMENT, dt.date(2022, 2, 1), dt.date(2022, 2, 2), dt.date(2022, 2, 5))
    result = mgr.interruptions_for_customer("C001", 2022)
    assert len(result) == 1 and result[0].customer_id == "C001"


def test_gi_interruptions_for_customer_year_filter():
    mgr = GasInterruptionManager()
    mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.NON_PAYMENT, dt.date(2022, 5, 1), dt.date(2022, 5, 2), dt.date(2022, 5, 5))
    assert mgr.interruptions_for_customer("C001", 2021) == []


def test_gi_vulnerable_customers_empty_when_none_vulnerable():
    mgr = GasInterruptionManager()
    mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.NETWORK_CONSTRAINT, dt.date(2022, 1, 1), dt.date(2022, 1, 2), dt.date(2022, 1, 4), is_vulnerable=False)
    assert mgr.vulnerable_customers_affected() == []


def test_gi_active_excludes_restored():
    mgr = GasInterruptionManager()
    gi = mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.SUPPLY_EMERGENCY, dt.date(2022, 3, 1), dt.date(2022, 3, 2), dt.date(2022, 3, 7))
    gi.restore(dt.date(2022, 3, 5))
    assert len(mgr.active_interruptions()) == 0


def test_gi_summary_total_count():
    mgr = GasInterruptionManager()
    mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.NON_PAYMENT, dt.date(2022, 4, 1), dt.date(2022, 4, 2), dt.date(2022, 4, 6))
    mgr.issue_interruption("INT002", "C002", "M002", InterruptionReason.HEALTH_SAFETY, dt.date(2022, 4, 3), dt.date(2022, 4, 4), dt.date(2022, 4, 8))
    assert mgr.interruption_summary(2022)["total"] == 2


def test_gi_summary_vulnerable_affected_count():
    mgr = GasInterruptionManager()
    mgr.issue_interruption("INT001", "C001", "M001", InterruptionReason.SUPPLY_EMERGENCY, dt.date(2022, 6, 1), dt.date(2022, 6, 2), dt.date(2022, 6, 5), is_vulnerable=True)
    mgr.issue_interruption("INT002", "C002", "M002", InterruptionReason.SUPPLY_EMERGENCY, dt.date(2022, 6, 3), dt.date(2022, 6, 4), dt.date(2022, 6, 8), is_vulnerable=False)
    assert mgr.interruption_summary(2022)["vulnerable_affected"] == 1


def test_gi_notice_days_seven():
    gi = GasInterruption("INT001", "C001", "M001", InterruptionReason.PLANNED_MAINTENANCE, dt.date(2022, 5, 1), dt.date(2022, 5, 8), dt.date(2022, 5, 15))
    assert gi.notice_days == 7


def test_gi_register_contract_stores_attributes():
    mgr = GasInterruptionManager()
    c = mgr.register_contract("C001", "M001", InterruptClass.INTERRUPTIBLE, 12, 6)
    assert c.max_interruptions_per_year == 12 and c.min_notice_hours == 6
