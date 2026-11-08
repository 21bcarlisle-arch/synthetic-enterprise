import datetime as dt
import pytest
from company.billing.revenue_protection_visit_register import (
    RevenueProtectionVisitRegister, Fuel, RPVTrigger, RPVStatus, AccessOutcome,
)

DATE = dt.date(2022, 4, 15)


def _reg():
    r = RevenueProtectionVisitRegister()
    r.schedule_visit("ACC-001", "MPAN-111", Fuel.ELECTRICITY,
                     RPVTrigger.THEFT_RISK_SCORE, DATE)
    return r


def test_visit_id_prefix():
    reg = _reg()
    assert reg._records[0].visit_id.startswith("RPV-")


def test_status_default_scheduled():
    reg = _reg()
    assert reg._records[0].status == RPVStatus.SCHEDULED


def test_tamper_found_sets_visited_tamper():
    reg = _reg()
    vid = reg._records[0].visit_id
    updated = reg.record_outcome(vid, AccessOutcome.TAMPER_FOUND, DATE)
    assert updated.status == RPVStatus.VISITED_TAMPER_FOUND


def test_clear_sets_visited_clear():
    reg = _reg()
    vid = reg._records[0].visit_id
    updated = reg.record_outcome(vid, AccessOutcome.CLEAR, DATE)
    assert updated.status == RPVStatus.VISITED_CLEAR


def test_requires_theft_investigation_for_tamper():
    reg = _reg()
    vid = reg._records[0].visit_id
    updated = reg.record_outcome(vid, AccessOutcome.TAMPER_FOUND, DATE)
    assert updated.requires_theft_investigation is True


def test_no_theft_investigation_for_clear():
    reg = _reg()
    vid = reg._records[0].visit_id
    updated = reg.record_outcome(vid, AccessOutcome.CLEAR, DATE)
    assert updated.requires_theft_investigation is False


def test_cancel_changes_status():
    reg = _reg()
    vid = reg._records[0].visit_id
    updated = reg.cancel(vid)
    assert updated.status == RPVStatus.CANCELLED


def test_is_overdue_past_scheduled_date():
    reg = _reg()
    r = reg._records[0]
    assert r.is_overdue(DATE + dt.timedelta(days=1)) is True


def test_not_overdue_on_scheduled_date():
    reg = _reg()
    r = reg._records[0]
    assert r.is_overdue(DATE) is False


def test_record_outcome_on_non_scheduled_raises():
    reg = _reg()
    vid = reg._records[0].visit_id
    reg.cancel(vid)
    with pytest.raises((ValueError, KeyError)):
        reg.record_outcome(vid, AccessOutcome.CLEAR, DATE)
