import datetime as dt
import pytest
from company.market.dcc_meter_registration import (
    DCCMeterRegistrationRegister, DCCRegistrationStatus,
)

INSTALL = dt.date(2022, 5, 1)


def _reg():
    r = DCCMeterRegistrationRegister()
    r.register_installation("MPAN-111", INSTALL, "SERIAL-001")
    return r


def test_record_id_prefix():
    reg = _reg()
    assert reg._records[0].record_id.startswith("DCC-")


def test_status_default_pending():
    reg = _reg()
    assert reg._records[0].status == DCCRegistrationStatus.PENDING


def test_registration_deadline_10wd():
    reg = _reg()
    r = reg._records[0]
    assert (r.registration_deadline - INSTALL).days >= 10


def test_mark_registered_sets_status():
    reg = _reg()
    rid = reg._records[0].record_id
    updated = reg.mark_registered(rid, INSTALL + dt.timedelta(days=7))
    assert updated.status == DCCRegistrationStatus.REGISTERED


def test_mark_failed_sets_failed():
    reg = _reg()
    rid = reg._records[0].record_id
    updated = reg.mark_failed(rid, INSTALL + dt.timedelta(days=12))
    assert updated.status == DCCRegistrationStatus.FAILED


def test_mark_failed_increments_retry():
    reg = _reg()
    rid = reg._records[0].record_id
    updated = reg.mark_failed(rid, INSTALL + dt.timedelta(days=12))
    assert updated.retry_count == 1


def test_is_overdue_after_deadline():
    reg = _reg()
    r = reg._records[0]
    overdue_date = r.registration_deadline + dt.timedelta(days=1)
    assert r.is_overdue_as_of(overdue_date) is True


def test_orphan_candidate_after_90_days():
    reg = _reg()
    r = reg._records[0]
    assert r.is_orphan_candidate_as_of(INSTALL + dt.timedelta(days=91)) is True


def test_not_orphan_candidate_before_90_days():
    reg = _reg()
    r = reg._records[0]
    assert r.is_orphan_candidate_as_of(INSTALL + dt.timedelta(days=89)) is False


def test_registration_rate_none_empty():
    reg = DCCMeterRegistrationRegister()
    assert reg.registration_rate_pct() is None
