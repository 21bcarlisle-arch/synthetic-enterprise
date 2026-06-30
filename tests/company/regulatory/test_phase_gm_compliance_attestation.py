import datetime as dt
import pytest
from company.regulatory.annual_compliance_attestation_register import (
    AttestationStatus, AttestationOutcome, SLCAttestationRecord,
    AnnualComplianceAttestationRegister, _QUERY_RESPONSE_WD,
)

P_START = dt.date(2024, 1, 1)
P_END = dt.date(2024, 12, 31)
YEAR = 2024
SLC = "SLC22"
AS_OF = dt.date(2025, 3, 31)


def make_record(outcome=AttestationOutcome.COMPLIANT, status=AttestationStatus.DRAFT):
    return SLCAttestationRecord(
        record_id="ATTEST-00001", slc_reference=SLC,
        assessment_year=YEAR, period_start=P_START, period_end=P_END,
        outcome=outcome, status=status)


class TestSLCAttestationRecord:
    def test_is_submitted_submitted(self):
        assert make_record(status=AttestationStatus.SUBMITTED).is_submitted
    def test_is_submitted_acknowledged(self):
        assert make_record(status=AttestationStatus.ACKNOWLEDGED).is_submitted
    def test_is_not_submitted_draft(self):
        assert not make_record().is_submitted
    def test_is_breach_minor(self):
        assert make_record(AttestationOutcome.MINOR_BREACH).is_breach
    def test_is_breach_material(self):
        assert make_record(AttestationOutcome.MATERIAL_BREACH).is_breach
    def test_is_not_breach_compliant(self):
        assert not make_record(AttestationOutcome.COMPLIANT).is_breach
    def test_is_not_breach_with_mitigations(self):
        assert not make_record(AttestationOutcome.COMPLIANT_WITH_MITIGATIONS).is_breach
    def test_is_material_breach(self):
        assert make_record(AttestationOutcome.MATERIAL_BREACH).is_material_breach
    def test_is_not_material_breach_minor(self):
        assert not make_record(AttestationOutcome.MINOR_BREACH).is_material_breach
    def test_is_queried(self):
        assert make_record(status=AttestationStatus.QUERIED).is_queried
    def test_attestation_summary(self):
        s = make_record().attestation_summary()
        assert "ATTEST-00001" in s and SLC in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.outcome = AttestationOutcome.MATERIAL_BREACH


class TestAnnualComplianceAttestationRegister:
    def setup_method(self):
        self.reg = AnnualComplianceAttestationRegister()

    def test_create_attestation_stored(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        assert r.status == AttestationStatus.DRAFT

    def test_auto_id_increments(self):
        r1 = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        r2 = self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        assert r1.record_id != r2.record_id

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            self.reg.create_attestation(SLC, YEAR, P_END, P_START, AttestationOutcome.COMPLIANT)

    def test_submit(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        sub = self.reg.submit(r.record_id, dt.date(2025, 3, 20), ofgem_ref="OFG-12345")
        assert sub.is_submitted and sub.ofgem_ref == "OFG-12345"

    def test_mark_acknowledged(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.submit(r.record_id, dt.date(2025, 3, 20))
        ack = self.reg.mark_acknowledged(r.record_id)
        assert ack.status == AttestationStatus.ACKNOWLEDGED

    def test_mark_queried(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.submit(r.record_id, dt.date(2025, 3, 20))
        query_date = dt.date(2025, 4, 1)
        q = self.reg.mark_queried(r.record_id, query_date)
        assert q.is_queried and q.query_date == query_date
        assert q.query_response_due is not None

    def test_query_response_due_is_20wd_out(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.submit(r.record_id, dt.date(2025, 3, 20))
        query_date = dt.date(2025, 4, 1)  # Tuesday
        q = self.reg.mark_queried(r.record_id, query_date)
        days = (q.query_response_due - query_date).days
        assert days >= _QUERY_RESPONSE_WD

    def test_supersede(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        sup = self.reg.supersede(r.record_id)
        assert sup.status == AttestationStatus.SUPERSEDED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.mark_acknowledged("ATTEST-99999")

    def test_for_year(self):
        self.reg.create_attestation(SLC, 2024, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.create_attestation(SLC, 2023, dt.date(2023,1,1), dt.date(2023,12,31), AttestationOutcome.COMPLIANT)
        assert len(self.reg.for_year(2024)) == 1

    def test_for_slc(self):
        self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        assert len(self.reg.for_slc(SLC)) == 1

    def test_outstanding_queries(self):
        r = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.submit(r.record_id, dt.date(2025, 3, 20))
        self.reg.mark_queried(r.record_id, dt.date(2025, 4, 1))
        assert len(self.reg.outstanding_queries()) == 1

    def test_material_breaches(self):
        self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.MATERIAL_BREACH)
        self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.MINOR_BREACH)
        assert len(self.reg.material_breaches()) == 1

    def test_breaches_includes_minor_and_material(self):
        self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.MATERIAL_BREACH)
        self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.MINOR_BREACH)
        assert len(self.reg.breaches()) == 2

    def test_unsubmitted(self):
        r1 = self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        r2 = self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.submit(r1.record_id, dt.date(2025, 3, 20))
        assert len(self.reg.unsubmitted()) == 1

    def test_compliance_rate_pct(self):
        self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        self.reg.create_attestation("SLC27", YEAR, P_START, P_END, AttestationOutcome.MINOR_BREACH)
        rate = self.reg.compliance_rate_pct(YEAR)
        assert rate == 50.0

    def test_compliance_rate_none_when_empty(self):
        assert self.reg.compliance_rate_pct(YEAR) is None

    def test_attestation_summary(self):
        self.reg.create_attestation(SLC, YEAR, P_START, P_END, AttestationOutcome.COMPLIANT)
        s = self.reg.attestation_summary(YEAR)
        assert "1 attestations" in s

    def test_empty_summary(self):
        s = self.reg.attestation_summary(YEAR)
        assert "0 attestations" in s
