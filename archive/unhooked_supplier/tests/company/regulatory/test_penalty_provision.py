"""Tests for Regulatory Penalty Provision Book (Phase EL)."""
import datetime as dt
import pytest
from company.regulatory.penalty_provision import (
    InvestigationStatus, PenaltyBasis, PenaltyProvisionRecord,
    RegulatoryPenaltyProvisionBook, _TYPICAL_PENALTY_BY_BASIS,
    _MATERIAL_PROVISION_THRESHOLD_GBP,
)

DATE = dt.date(2024, 1, 15)


def make_rec(status=InvestigationStatus.OFGEM_ENQUIRY,
             penalty=500_000.0, redress=0.0):
    return PenaltyProvisionRecord(
        case_id="REG-0001",
        basis=PenaltyBasis.SLC_BREACH,
        status=status,
        opened_at=DATE,
        estimated_penalty_gbp=penalty,
        redress_estimate_gbp=redress,
    )


class TestPenaltyProvisionRecord:
    def test_probability_monitoring(self):
        r = make_rec(status=InvestigationStatus.MONITORING)
        assert r.probability_of_penalty == 0.10

    def test_probability_formal(self):
        r = make_rec(status=InvestigationStatus.FORMAL_INVESTIGATION)
        assert r.probability_of_penalty == 0.65

    def test_probability_closed(self):
        r = make_rec(status=InvestigationStatus.CLOSED_NO_ACTION)
        assert r.probability_of_penalty == 0.0

    def test_expected_penalty(self):
        r = make_rec(status=InvestigationStatus.OFGEM_ENQUIRY, penalty=1_000_000.0)
        assert r.expected_penalty_gbp == pytest.approx(300_000.0)

    def test_expected_redress(self):
        r = make_rec(status=InvestigationStatus.OFGEM_ENQUIRY, redress=200_000.0)
        assert r.expected_redress_gbp == pytest.approx(60_000.0)

    def test_total_exposure(self):
        r = make_rec(penalty=1_000_000.0, redress=200_000.0,
                     status=InvestigationStatus.OFGEM_ENQUIRY)
        assert r.total_expected_exposure_gbp == pytest.approx(360_000.0)

    def test_is_active_true(self):
        r = make_rec(status=InvestigationStatus.FORMAL_INVESTIGATION)
        assert r.is_active

    def test_is_active_false_closed(self):
        r = make_rec(status=InvestigationStatus.CLOSED_NO_ACTION)
        assert not r.is_active

    def test_is_material(self):
        r = make_rec(status=InvestigationStatus.FORMAL_INVESTIGATION, penalty=500_000.0)
        expected = 500_000.0 * 0.65
        assert expected >= _MATERIAL_PROVISION_THRESHOLD_GBP
        assert r.is_material

    def test_not_material_tiny_penalty(self):
        r = make_rec(status=InvestigationStatus.MONITORING, penalty=10_000.0)
        assert not r.is_material

    def test_provision_summary(self):
        r = make_rec()
        s = r.provision_summary()
        assert "REG-0001" in s


class TestRegulatoryPenaltyProvisionBook:
    def test_open_case_auto_id(self):
        book = RegulatoryPenaltyProvisionBook()
        c = book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING, DATE)
        assert c.case_id == "REG-0001"

    def test_open_case_uses_typical_penalty(self):
        book = RegulatoryPenaltyProvisionBook()
        c = book.open_case(PenaltyBasis.REMIT_BREACH, InvestigationStatus.MONITORING, DATE)
        assert c.estimated_penalty_gbp == _TYPICAL_PENALTY_BY_BASIS[PenaltyBasis.REMIT_BREACH]

    def test_open_case_custom_penalty(self):
        book = RegulatoryPenaltyProvisionBook()
        c = book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING,
                           DATE, estimated_penalty_gbp=999.0)
        assert c.estimated_penalty_gbp == 999.0

    def test_update_status(self):
        book = RegulatoryPenaltyProvisionBook()
        c = book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING, DATE)
        updated = book.update_status(c.case_id, InvestigationStatus.FORMAL_INVESTIGATION,
                                     dt.date(2024, 2, 1))
        assert updated.status == InvestigationStatus.FORMAL_INVESTIGATION

    def test_update_status_closed_sets_closed_at(self):
        book = RegulatoryPenaltyProvisionBook()
        c = book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING, DATE)
        close_date = dt.date(2024, 3, 1)
        updated = book.update_status(c.case_id, InvestigationStatus.CLOSED_NO_ACTION, close_date)
        assert updated.closed_at == close_date

    def test_active_cases_excludes_closed(self):
        book = RegulatoryPenaltyProvisionBook()
        c1 = book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING, DATE)
        book.open_case(PenaltyBasis.CONSUMER_DUTY, InvestigationStatus.CLOSED_NO_ACTION, DATE)
        assert len(book.active_cases()) == 1

    def test_formal_investigations_filter(self):
        book = RegulatoryPenaltyProvisionBook()
        book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.FORMAL_INVESTIGATION, DATE)
        book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.MONITORING, DATE)
        assert len(book.formal_investigations()) == 1

    def test_total_provision_gbp(self):
        book = RegulatoryPenaltyProvisionBook()
        book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.FORMAL_INVESTIGATION,
                       DATE, estimated_penalty_gbp=1_000_000.0)
        assert book.total_provision_gbp() == pytest.approx(650_000.0)

    def test_total_provision_excludes_closed(self):
        book = RegulatoryPenaltyProvisionBook()
        book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.CLOSED_NO_ACTION, DATE)
        assert book.total_provision_gbp() == 0.0

    def test_penalty_provision_summary(self):
        book = RegulatoryPenaltyProvisionBook()
        book.open_case(PenaltyBasis.SLC_BREACH, InvestigationStatus.FORMAL_INVESTIGATION, DATE)
        s = book.penalty_provision_summary(DATE)
        assert "Regulatory Provisions" in s
