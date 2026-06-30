"""Phase IB: coverage expansion for tpi_commission_book, triad_notification_book, licence_application_register."""
import datetime as dt
import pytest

# ===== tpi_commission_book =====
from company.market.tpi_commission_book import (
    TPICommissionBook, TPITier, CommissionType, TPIAgreement, TPIPayment
)

def _book():
    b = TPICommissionBook()
    b.register_tpi("T1","National Broker",TPITier.NATIONAL,CommissionType.UPFRONT,
                   upfront_gbp=500.0,is_disclosed=True,customer_id="C_IC1",contract_start_year=2022)
    b.register_tpi("T2","Regional Broker",TPITier.REGIONAL,CommissionType.TRAIL,
                   trail_gbp_per_mwh=3.0,is_disclosed=False,customer_id="C_IC2",contract_start_year=2022)
    b.record_payment("P1","T1","C_IC1",2022,CommissionType.UPFRONT,500.0)
    b.record_payment("P2","T2","C_IC2",2022,CommissionType.TRAIL,1200.0,annual_kwh=400_000.0)
    b.record_payment("P3","T2","C_IC2",2023,CommissionType.TRAIL,1250.0,annual_kwh=400_000.0)
    return b

class TestTPICommissionBook:
    def test_all_agreements_count(self):
        b = _book()
        assert len(b.all_agreements) == 2

    def test_non_compliant_when_not_disclosed(self):
        b = _book()
        nc = b.non_compliant_agreements
        assert len(nc) == 1
        assert nc[0].tpi_id == "T2"

    def test_disclosed_is_compliant(self):
        b = _book()
        a = b._agreements["T1"]
        assert a.is_compliant

    def test_payments_for_year(self):
        b = _book()
        assert len(b.payments_for_year(2022)) == 2

    def test_payments_for_customer(self):
        b = _book()
        assert len(b.payments_for_customer("C_IC2")) == 2

    def test_total_commission_gbp(self):
        b = _book()
        assert b.total_commission_gbp() == pytest.approx(2950.0)

    def test_total_for_year(self):
        b = _book()
        assert b.total_for_year(2022) == pytest.approx(1700.0)

    def test_rate_gbp_per_mwh(self):
        b = _book()
        p = b.payments_for_customer("C_IC2")[0]
        assert p.rate_gbp_per_mwh == pytest.approx(3.0)

    def test_avg_rate_trail_only(self):
        b = _book()
        avg = b.avg_rate_gbp_per_mwh()
        assert avg == pytest.approx(3.0625)

    def test_tpi_summary_contains_key_fields(self):
        b = _book()
        s = b.tpi_summary()
        assert "TPIs registered" in s and "Non-disclosed" in s


# ===== triad_notification_book =====
from company.market.triad_notification_book import (
    TriadNotificationBook, CustomerTriadProfile, TriadAlert, AlertStatus, TriadSavingsRecord
)

def _triad_book():
    book = TriadNotificationBook()
    profile = CustomerTriadProfile(account_id="IC1",annual_kwh=2_000_000,peak_demand_kw=400.0)
    book.enrol(profile)
    book.issue_alert(TriadAlert("IC1","2022-11-15",35,400.0,AlertStatus.RESPONDED))
    book.issue_alert(TriadAlert("IC1","2022-12-07",36,400.0,AlertStatus.NO_RESPONSE))
    return book

class TestTriadNotificationBook:
    def test_enrol_account(self):
        book = _triad_book()
        assert len(book.enrolled_accounts()) == 1

    def test_issue_alert_unknown_account_raises(self):
        book = TriadNotificationBook()
        with pytest.raises(KeyError):
            book.issue_alert(TriadAlert("UNKNOWN","2022-11-15",35,200.0,AlertStatus.ISSUED))

    def test_alerts_for_account(self):
        book = _triad_book()
        assert len(book.alerts_for_account("IC1")) == 2

    def test_demand_reduction_when_responded(self):
        book = _triad_book()
        responded = [a for a in book.alerts_for_account("IC1") if a.status == AlertStatus.RESPONDED]
        assert responded[0].demand_reduction_kw == pytest.approx(400.0 * 0.70, rel=0.01)

    def test_demand_reduction_zero_when_no_response(self):
        book = _triad_book()
        no_resp = [a for a in book.alerts_for_account("IC1") if a.status == AlertStatus.NO_RESPONSE]
        assert no_resp[0].demand_reduction_kw == 0.0

    def test_is_triad_season_november(self):
        assert TriadNotificationBook.is_triad_season(dt.date(2022,11,15))

    def test_is_not_triad_season_summer(self):
        assert not TriadNotificationBook.is_triad_season(dt.date(2022,7,15))

    def test_is_triad_risk_period(self):
        assert TriadNotificationBook.is_triad_risk_period(35)
        assert not TriadNotificationBook.is_triad_risk_period(20)

    def test_savings_record_response_rate(self):
        book = _triad_book()
        s = book.savings_for_account_year("IC1", 2023)  # alerts in Nov/Dec 2022 count for 2023
        assert s.response_rate_pct == pytest.approx(50.0)

    def test_triad_summary_contains_key_fields(self):
        book = _triad_book()
        s = book.triad_notification_summary()
        assert "enrolled" in s and "alerts" in s


# ===== licence_application_register =====
from company.regulatory.licence_application_register import (
    LicenceApplicationRegister, LicenceType, LicenceTier, ApplicationStatus, VariationReason
)

def _lar():
    reg = LicenceApplicationRegister()
    reg.register_licence("L001",LicenceType.ELECTRICITY_DOMESTIC,LicenceTier.TIER_1,dt.date(2018,1,1))
    reg.register_licence("L002",LicenceType.GAS_DOMESTIC,LicenceTier.TIER_1,dt.date(2018,1,1),
                         special_conditions=("SpC1",))
    reg.submit_application("A001",LicenceType.ELECTRICITY_NON_DOMESTIC,dt.date(2022,3,1),
                            VariationReason.NEW_CATEGORY)
    return reg

class TestLicenceApplicationRegister:
    def test_active_licences_count(self):
        reg = _lar()
        assert len(reg.active_licences) == 2

    def test_licence_with_special_conditions(self):
        reg = _lar()
        spsc = reg.licences_with_special_conditions
        assert len(spsc) == 1
        assert spsc[0].licence_id == "L002"

    def test_has_special_conditions_property(self):
        reg = _lar()
        lrec = reg._licences["L002"]
        assert lrec.has_special_conditions

    def test_submit_creates_pending(self):
        reg = _lar()
        assert len(reg.open_applications) == 1
        assert reg.open_applications[0].status == ApplicationStatus.PENDING

    def test_decide_approved(self):
        reg = _lar()
        result = reg.decide("A001",True,dt.date(2022,6,1))
        assert result.is_approved
        assert result.decision_date == dt.date(2022,6,1)

    def test_decide_rejected(self):
        reg = _lar()
        result = reg.decide("A001",False,dt.date(2022,6,1))
        assert result.status == ApplicationStatus.REJECTED
        assert not result.is_open

    def test_approved_moves_to_approved_list(self):
        reg = _lar()
        reg.decide("A001",True,dt.date(2022,6,1))
        assert len(reg.approved_applications) == 1
        assert len(reg.open_applications) == 0

    def test_open_application_is_open(self):
        reg = _lar()
        app = reg.open_applications[0]
        assert app.is_open

    def test_licence_no_special_conditions(self):
        reg = _lar()
        assert not reg._licences["L001"].has_special_conditions

    def test_licence_summary_contains_key_fields(self):
        reg = _lar()
        s = reg.licence_summary()
        assert "Active licences" in s and "Open applications" in s
