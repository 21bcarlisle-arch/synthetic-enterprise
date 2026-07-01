import datetime as dt
import pytest
from company.billing.dd_mandate_register import (
    DDMandateRegister, DDMandateStatus,
)

DATE = dt.date(2022, 3, 1)


def _reg():
    r = DDMandateRegister()
    r.setup_mandate("ACC-001", 15, 80.0, DATE)
    return r


def test_mandate_ref_prefix():
    reg = _reg()
    assert reg._records[0].mandate_ref.startswith("DDM-")


def test_status_default_active():
    reg = _reg()
    assert reg._records[0].status == DDMandateStatus.ACTIVE


def test_day_29_raises():
    reg = DDMandateRegister()
    with pytest.raises(ValueError):
        reg.setup_mandate("ACC-X", 29, 100.0, DATE)


def test_zero_amount_raises():
    reg = DDMandateRegister()
    with pytest.raises(ValueError):
        reg.setup_mandate("ACC-X", 15, 0.0, DATE)


def test_suspend_changes_status():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.suspend(ref, DATE)
    assert updated.status == DDMandateStatus.SUSPENDED


def test_reinstate_after_suspend():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    reg.suspend(ref, DATE)
    updated = reg.reinstate(ref, DATE)
    assert updated.status == DDMandateStatus.REINSTATED


def test_cancel_sets_cancelled():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.cancel(ref, DATE)
    assert updated.status == DDMandateStatus.CANCELLED


def test_record_failure_increments_count():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.record_failure(ref, DATE)
    assert updated.failed_count == 1
    assert updated.status == DDMandateStatus.FAILED


def test_two_failures_auto_cancel():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    reg.record_failure(ref, DATE)
    updated = reg.record_failure(ref, DATE)
    assert updated.failed_count == 2
    assert updated.status == DDMandateStatus.CANCELLED


def test_total_monthly_collection_sums_active():
    reg = _reg()
    reg.setup_mandate("ACC-002", 20, 60.0, DATE)
    assert reg.total_monthly_collection_gbp() == 140.0
