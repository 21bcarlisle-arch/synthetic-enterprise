"""Phase IE: deeper coverage for solr_intake, risk_appetite, renewals_book."""
import datetime as dt
import pytest

# ===== solr_intake =====
from company.crm.solr_intake import (
    SoLRBook, SoLRBatch, SoLRIntakeStatus
)

def _solr():
    book = SoLRBook("OurCo")
    book.register_batch("B001","Bulb Energy",dt.date(2021,11,24),customer_count=150)
    book.add_customer("SC1","B001","M001","resi")
    book.add_customer("SC2","B001","M002","resi")
    book.add_customer("SC3","B001","M003","resi")
    book.mark_contacted("SC1",dt.date(2021,11,25))
    book.mark_onboarded("SC1",dt.date(2021,12,1))
    book.mark_switched_away("SC2",dt.date(2021,12,10))
    return book

class TestSoLRBookExpanded:
    def test_batch_registered(self):
        book = _solr()
        b = book._batches["B001"]
        assert b.failed_supplier == "Bulb Energy"
        assert b.customer_count == 150

    def test_batch_not_priced_above_cap_default(self):
        book = _solr()
        b = book._batches["B001"]
        assert not b.is_priced_above_cap

    def test_batch_priced_above_cap(self):
        book = SoLRBook("OurCo")
        b = book.register_batch("B002","Orbit",dt.date(2021,12,1),50,deemed_tariff_rate_pct_above_cap=5.0)
        assert b.is_priced_above_cap

    def test_add_customer_notified_initial(self):
        book = _solr()
        cust = [c for c in book._customers if c.customer_id == "SC3"][0]
        assert cust.status == SoLRIntakeStatus.NOTIFIED

    def test_mark_contacted(self):
        book = _solr()
        cust = [c for c in book._customers if c.customer_id == "SC1"][0]
        assert cust.status == SoLRIntakeStatus.ONBOARDED  # was contacted then onboarded

    def test_is_retained_when_onboarded(self):
        book = _solr()
        cust = [c for c in book._customers if c.customer_id == "SC1"][0]
        assert cust.is_retained

    def test_retention_rate_one_of_three(self):
        book = _solr()
        assert book.retention_rate("B001") == pytest.approx(100/3, rel=0.01)

    def test_contact_rate_two_of_three_contacted(self):
        book = _solr()
        # SC1 = ONBOARDED, SC2 = SWITCHED_AWAY, SC3 = NOTIFIED (not yet contacted)
        assert book.contact_rate("B001") == pytest.approx(200/3, rel=0.01)

    def test_customers_in_batch(self):
        book = _solr()
        assert len(book.customers_in_batch("B001")) == 3

    def test_batch_summary_keys(self):
        book = _solr()
        s = book.batch_summary("B001")
        assert "retention_rate_pct" in s and "failed_supplier" in s


# ===== risk_appetite =====
from company.risk.risk_appetite import (
    RiskAppetiteFramework, RiskCategory, RiskRAG, RiskLimit
)

def _raf():
    raf = RiskAppetiteFramework(dt.date(2022,1,1))
    raf.add_limit("L1",RiskCategory.MARKET,"VaR limit",5_000_000.0,"GBP",warning_threshold_pct=80.0)
    raf.add_limit("L2",RiskCategory.CREDIT,"Counterparty exposure",2_000_000.0,"GBP",warning_threshold_pct=75.0)
    raf.record_measurement("L1",3_000_000.0,dt.date(2022,3,1))   # within
    raf.record_measurement("L1",4_200_000.0,dt.date(2022,4,1))   # approaching
    raf.record_measurement("L2",2_500_000.0,dt.date(2022,3,1))   # breach
    return raf

class TestRiskAppetiteExpanded:
    def test_warning_value_calculation(self):
        raf = _raf()
        limit = raf._limits["L1"]
        assert limit.warning_value == pytest.approx(5_000_000 * 0.80)

    def test_utilisation_pct(self):
        raf = _raf()
        m = raf.latest_measurement("L1")
        assert m.utilisation_pct == pytest.approx(84.0)

    def test_rag_within_appetite(self):
        raf = _raf()
        m = raf._measurements[0]  # 3M vs 5M limit -> 60% -> within
        assert m.rag == RiskRAG.WITHIN_APPETITE

    def test_rag_approaching_limit(self):
        raf = _raf()
        m = raf._measurements[1]  # 4.2M vs 5M limit -> 84% -> approaching
        assert m.rag == RiskRAG.APPROACHING_LIMIT

    def test_rag_limit_breach(self):
        raf = _raf()
        m = raf._measurements[2]  # 2.5M vs 2M limit -> breach
        assert m.rag == RiskRAG.LIMIT_BREACH
        assert m.is_breach

    def test_latest_measurement_is_most_recent(self):
        raf = _raf()
        latest = raf.latest_measurement("L1")
        assert latest.measured_value == pytest.approx(4_200_000.0)

    def test_active_breaches(self):
        raf = _raf()
        breaches = raf.active_breaches()
        assert len(breaches) == 1
        assert breaches[0].limit_id == "L2"

    def test_no_active_breaches_when_resolved(self):
        raf = _raf()
        raf.record_measurement("L2",1_000_000.0,dt.date(2022,5,1))
        assert len(raf.active_breaches()) == 0

    def test_risk_dashboard_breach_count(self):
        raf = _raf()
        dash = raf.risk_dashboard(dt.date(2022,4,1))
        assert dash["breaches"] == 1

    def test_risk_dashboard_keys(self):
        raf = _raf()
        dash = raf.risk_dashboard(dt.date(2022,4,1))
        assert "total_limits" in dash and "items" in dash


# ===== renewals_book =====
from company.crm.renewals_book import (
    RenewalsBook, RenewalOutcome, OfferType
)

def _rb():
    book = RenewalsBook()
    book.add("C1","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED,
             OfferType.BETTER_TARIFF,28.0,12,was_outbound_contact=True)
    book.add("C2","resi",dt.date(2022,12,31),RenewalOutcome.SWITCHED_AWAY,
             OfferType.SAME_TARIFF,31.0,12,was_outbound_contact=False)
    book.add("C3","resi",dt.date(2022,12,31),RenewalOutcome.RENEWED,
             OfferType.SAME_TARIFF,30.0,12,was_outbound_contact=False)
    book.add("C4","resi",dt.date(2022,12,31),RenewalOutcome.MOVED_OUT,None,None,None)
    return book

class TestRenewalsBookExpanded:
    def test_accepted_property(self):
        book = _rb()
        r = book._records[0]
        assert r.accepted

    def test_not_accepted_switched_away(self):
        book = _rb()
        r = book._records[1]
        assert not r.accepted

    def test_renewal_rate_excludes_moved_out(self):
        book = _rb()
        rate = book.renewal_rate(2022)
        # C1 renewed, C2 switched, C3 renewed, C4 excluded -> 2/3 = 66.7%
        assert rate == pytest.approx(66.7, rel=0.01)

    def test_lapse_rate_complement(self):
        book = _rb()
        assert book.lapse_rate(2022) == pytest.approx(100 - book.renewal_rate(2022), rel=0.01)

    def test_renewal_rate_none_for_empty_year(self):
        book = _rb()
        assert book.renewal_rate(2020) is None

    def test_outbound_lift_positive(self):
        book = _rb()
        # outbound: C1 = 1/1 = 100%; inbound: C2=0, C3=1, C4=0 -> 1/3 = 33.3%; lift = 66.7%
        lift = book.outbound_lift(2022)
        assert lift == pytest.approx(66.7, rel=0.01)

    def test_by_offer_type_keys(self):
        book = _rb()
        by_ot = book.by_offer_type(2022)
        assert "better_tariff" in by_ot and "same_tariff" in by_ot

    def test_by_offer_type_renewal_rate(self):
        book = _rb()
        by_ot = book.by_offer_type(2022)
        # better_tariff: 1 total, 1 renewed = 100%
        assert by_ot["better_tariff"]["renewal_rate"] == pytest.approx(100.0)

    def test_annual_summary_keys(self):
        book = _rb()
        s = book.annual_summary(2022)
        assert "renewal_rate_pct" in s and "by_offer_type" in s

    def test_segment_filter(self):
        book = _rb()
        # All are resi; filtering by sme gives None
        assert book.renewal_rate(2022,"sme") is None
