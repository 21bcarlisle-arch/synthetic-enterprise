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
