import datetime as dt
import pytest
from company.billing.gas_safety_incident_register import (
    GasSafetyIncidentRegister, GasSafetyIncidentType, IncidentSeverity, IncidentStatus,
)

DATE = dt.date(2022, 3, 1)


def _reg():
    r = GasSafetyIncidentRegister()
    r.report_incident("ACC-001", "1234567890", GasSafetyIncidentType.GAS_ESCAPE,
                      IncidentSeverity.LOW, DATE)
    return r


def test_incident_id_prefix():
    reg = _reg()
    assert reg._records[0].incident_id.startswith("GSI-")


def test_status_default_reported():
    reg = _reg()
    assert reg._records[0].status == IncidentStatus.REPORTED


def test_gas_escape_low_no_riddor():
    reg = _reg()
    assert reg._records[0].requires_riddor_notification is False


def test_co_confirmed_requires_riddor():
    reg = GasSafetyIncidentRegister()
    reg.report_incident("ACC-002", "9876", GasSafetyIncidentType.CO_CONFIRMED,
                        IncidentSeverity.MEDIUM, DATE)
    assert reg._records[0].requires_riddor_notification is True


def test_riddor_deadline_15_days():
    reg = GasSafetyIncidentRegister()
    reg.report_incident("A", "M", GasSafetyIncidentType.EXPLOSION, IncidentSeverity.HIGH, DATE)
    r = reg._records[0]
    assert r.riddor_deadline == DATE + dt.timedelta(days=15)


def test_injuries_trigger_riddor():
    reg = GasSafetyIncidentRegister()
    reg.report_incident("A", "M", GasSafetyIncidentType.GAS_ESCAPE,
                        IncidentSeverity.LOW, DATE, injuries_count=1)
    assert reg._records[0].requires_riddor_notification is True


def test_negative_injuries_raises():
    reg = GasSafetyIncidentRegister()
    with pytest.raises(ValueError):
        reg.report_incident("A", "M", GasSafetyIncidentType.GAS_ESCAPE,
                            IncidentSeverity.LOW, DATE, injuries_count=-1)


def test_dispatch_engineer_changes_status():
    reg = _reg()
    iid = reg._records[0].incident_id
    updated = reg.dispatch_engineer(iid, DATE)
    assert updated.status == IncidentStatus.ENGINEER_DISPATCHED


def test_make_safe_and_close():
    reg = _reg()
    iid = reg._records[0].incident_id
    reg.dispatch_engineer(iid, DATE)
    reg.mark_made_safe(iid, DATE + dt.timedelta(days=1))
    closed = reg.close_incident(iid, DATE + dt.timedelta(days=2))
    assert closed.status == IncidentStatus.CLOSED


def test_total_injuries_sums():
    reg = GasSafetyIncidentRegister()
    reg.report_incident("A", "M1", GasSafetyIncidentType.GAS_ESCAPE,
                        IncidentSeverity.LOW, DATE, injuries_count=2)
    reg.report_incident("B", "M2", GasSafetyIncidentType.GAS_ESCAPE,
                        IncidentSeverity.LOW, DATE, injuries_count=3)
    assert reg.total_injuries == 5
