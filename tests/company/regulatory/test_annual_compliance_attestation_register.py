"""Tests for company/regulatory/annual_compliance_attestation_register.py (Sprint CLIII)."""
import datetime as dt
import pytest

from company.regulatory.annual_compliance_attestation_register import (
    AnnualComplianceAttestationRegister,
    AttestationOutcome,
    AttestationStatus,
)

PERIOD_START = dt.date(2023, 4, 1)
PERIOD_END = dt.date(2024, 3, 31)


def _reg():
    return AnnualComplianceAttestationRegister()


def _add(reg, outcome=AttestationOutcome.COMPLIANT):
    return reg.create_attestation("SLC14", 2023, PERIOD_START, PERIOD_END, outcome)


def test_record_id_starts_with_attest():
    reg = _reg()
    r = _add(reg)
    assert r.record_id.startswith("ATTEST-")


def test_slc_reference_stored():
    reg = _reg()
    r = _add(reg)
    assert r.slc_reference == "SLC14"


def test_outcome_stored():
    reg = _reg()
    r = _add(reg, outcome=AttestationOutcome.MINOR_BREACH)
    assert r.outcome == AttestationOutcome.MINOR_BREACH


def test_is_breach_true_for_minor():
    reg = _reg()
    r = _add(reg, outcome=AttestationOutcome.MINOR_BREACH)
    assert r.is_breach is True


def test_is_breach_false_for_compliant():
    reg = _reg()
    r = _add(reg, outcome=AttestationOutcome.COMPLIANT)
    assert r.is_breach is False


def test_is_material_breach_true():
    reg = _reg()
    r = _add(reg, outcome=AttestationOutcome.MATERIAL_BREACH)
    assert r.is_material_breach is True


def test_submit_updates_status():
    reg = _reg()
    r = _add(reg)
    s = reg.submit(r.record_id, PERIOD_END)
    assert s.status == AttestationStatus.SUBMITTED


def test_period_end_before_start_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.create_attestation("SLC14", 2023, PERIOD_END, PERIOD_START, AttestationOutcome.COMPLIANT)


def test_compliance_rate_pct_100_when_all_compliant():
    reg = _reg()
    _add(reg, outcome=AttestationOutcome.COMPLIANT)
    _add(reg, outcome=AttestationOutcome.COMPLIANT)
    assert reg.compliance_rate_pct() == 100.0


def test_for_year_filters():
    reg = _reg()
    reg.create_attestation("SLC14", 2023, PERIOD_START, PERIOD_END, AttestationOutcome.COMPLIANT)
    reg.create_attestation("SLC14", 2022, dt.date(2022, 4, 1), dt.date(2023, 3, 31), AttestationOutcome.COMPLIANT)
    assert len(reg.for_year(2023)) == 1
