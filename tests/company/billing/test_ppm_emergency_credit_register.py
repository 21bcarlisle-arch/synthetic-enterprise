"""Tests for company/billing/ppm_emergency_credit_register.py (Sprint CXLIX)."""
import datetime as dt
import pytest

from company.billing.ppm_emergency_credit_register import (
    PPMEmergencyCreditRegister,
    EmergencyCreditType,
    EmergencyCreditStatus,
)

TODAY = dt.date(2022, 6, 15)


def _reg():
    return PPMEmergencyCreditRegister()


def test_record_id_starts_with_ppme():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY)
    assert r.record_id.startswith("PPME-")


def test_account_id_stored():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY)
    assert r.account_id == "C1"


def test_default_amount_is_five():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY)
    assert r.amount_gbp == 5.0


def test_credit_type_stored():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY, credit_type=EmergencyCreditType.FRIENDLY, amount_gbp=10.0)
    assert r.credit_type == EmergencyCreditType.FRIENDLY


def test_outstanding_equals_amount_when_unrepaid():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY, amount_gbp=5.0)
    assert r.outstanding_gbp == 5.0


def test_is_active_true_for_new_credit():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY)
    assert r.is_active is True


def test_welfare_check_due_after_28_days():
    reg = _reg()
    reg.issue_credit("C1", TODAY)
    due = reg.welfare_check_due(TODAY + dt.timedelta(days=28))
    assert len(due) == 1


def test_mark_written_off_changes_status():
    reg = _reg()
    r = reg.issue_credit("C1", TODAY)
    w = reg.mark_written_off(r.record_id)
    assert w.status == EmergencyCreditStatus.WRITTEN_OFF


def test_total_outstanding_sums_active():
    reg = _reg()
    reg.issue_credit("C1", TODAY, amount_gbp=5.0)
    reg.issue_credit("C2", TODAY, amount_gbp=10.0)
    assert reg.total_outstanding_gbp() == 15.0


def test_negative_amount_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.issue_credit("C1", TODAY, amount_gbp=-1.0)
