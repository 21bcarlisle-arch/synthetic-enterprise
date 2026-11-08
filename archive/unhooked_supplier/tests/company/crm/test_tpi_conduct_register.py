import datetime as dt
import pytest
from company.crm.tpi_conduct_register import (
    TPIConductRegister, TPIMisconductType, TPIComplaintStatus, TPISanction,
)

DATE = dt.date(2022, 6, 1)


def _reg():
    r = TPIConductRegister()
    r.receive_complaint("TPI-001", "ACC-001", DATE, TPIMisconductType.MIS_SELLING)
    return r


def test_complaint_id_prefix():
    reg = _reg()
    assert reg._records[0].complaint_id.startswith("TPIC-")


def test_status_default_received():
    reg = _reg()
    assert reg._records[0].status == TPIComplaintStatus.RECEIVED


def test_investigation_due_10_days():
    reg = _reg()
    r = reg._records[0]
    assert r.investigation_due == DATE + dt.timedelta(days=10)


def test_contract_forgery_is_serious():
    reg = TPIConductRegister()
    reg.receive_complaint("TPI-X", "ACC-X", DATE, TPIMisconductType.CONTRACT_FORGERY)
    assert reg._records[0].is_serious is True


def test_mis_selling_not_serious():
    reg = _reg()
    assert reg._records[0].is_serious is False


def test_start_investigation_changes_status():
    reg = _reg()
    cid = reg._records[0].complaint_id
    updated = reg.start_investigation(cid, DATE + dt.timedelta(days=1))
    assert updated.status == TPIComplaintStatus.UNDER_INVESTIGATION


def test_uphold_sets_upheld_with_sanction():
    reg = _reg()
    cid = reg._records[0].complaint_id
    updated = reg.uphold(cid, DATE + dt.timedelta(days=9),
                         TPISanction.WARNING_ISSUED, customer_remedy_gbp=50.0)
    assert updated.status == TPIComplaintStatus.UPHELD
    assert updated.sanction == TPISanction.WARNING_ISSUED
    assert updated.customer_remedy_gbp == 50.0


def test_not_uphold_sets_not_upheld():
    reg = _reg()
    cid = reg._records[0].complaint_id
    updated = reg.not_uphold(cid, DATE + dt.timedelta(days=9))
    assert updated.status == TPIComplaintStatus.NOT_UPHELD


def test_escalate_sets_reported_to_ofgem():
    reg = _reg()
    cid = reg._records[0].complaint_id
    updated = reg.escalate_to_ofgem(cid)
    assert updated.status == TPIComplaintStatus.ESCALATED_OFGEM
    assert updated.sanction == TPISanction.REPORTED_TO_OFGEM


def test_uphold_rate_none_empty():
    reg = TPIConductRegister()
    assert reg.uphold_rate_pct() is None
