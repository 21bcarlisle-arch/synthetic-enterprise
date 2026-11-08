"""Tests for company/market/grid_connection_queue_register.py (Sprint CLII)."""
import datetime as dt
import pytest

from company.market.grid_connection_queue_register import (
    GridConnectionApplicationRecord,
    ConnectionApplicationType,
    ConnectionApplicationStatus,
)

try:
    from company.market.grid_connection_queue_register import GridConnectionQueueRegister
    _HAS_REGISTER = True
except ImportError:
    _HAS_REGISTER = False

DATE = dt.date(2022, 1, 1)


def _record(status=ConnectionApplicationStatus.SUBMITTED):
    return GridConnectionApplicationRecord(
        reference="GCQ-00001",
        account_id="C1",
        site_address="1 Test Lane",
        application_type=ConnectionApplicationType.NEW_CONNECTION,
        requested_capacity_kw=100.0,
        dno_name="LPN",
        submitted_date=DATE,
        status=status,
    )


def test_reference_stored():
    r = _record()
    assert r.reference == "GCQ-00001"


def test_account_id_stored():
    r = _record()
    assert r.account_id == "C1"


def test_application_type_stored():
    r = _record()
    assert r.application_type == ConnectionApplicationType.NEW_CONNECTION


def test_is_active_when_submitted():
    r = _record(ConnectionApplicationStatus.SUBMITTED)
    assert r.is_active is True


def test_is_not_active_when_energised():
    r = _record(ConnectionApplicationStatus.ENERGISED)
    assert r.is_active is False


def test_is_not_active_when_abandoned():
    r = _record(ConnectionApplicationStatus.ABANDONED)
    assert r.is_active is False


def test_capacity_stored():
    r = _record()
    assert r.requested_capacity_kw == 100.0


def test_dno_name_stored():
    r = _record()
    assert r.dno_name == "LPN"


def test_submitted_date_stored():
    r = _record()
    assert r.submitted_date == DATE


def test_offer_date_none_by_default():
    r = _record()
    assert r.offer_date is None
