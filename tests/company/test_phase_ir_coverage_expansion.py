"""Phase IR: deeper coverage for tpi_book, vulnerability_index, contact_log."""
import datetime as dt
import pytest

# ===== tpi_book =====
from company.crm.tpi_book import (
    TPIBook, TPITier, TPICommissionBasis
)


def _book():
    b = TPIBook()
    b.register("TPI1", "Energy Brokers Ltd", TPITier.PREFERRED,
                TPICommissionBasis.PCT_OF_ANNUAL_REVENUE, 1.5, dt.date(2021,1,1))
    b.register("TPI2", "SmallBroker", TPITier.STANDARD,
                TPICommissionBasis.FIXED_PER_CUSTOMER, 80.0, dt.date(2022,3,1))
    return b


class TestTPIBook:
    def test_deal_id_format(self):
        b = _book()
        d = b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))
        assert d.deal_id == "DEAL-0001"

    def test_commission_pct_revenue(self):
        b = _book()
        d = b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))
        # 1.5% of 10,000 = 150
        assert d.commission_gbp == pytest.approx(150.0)

    def test_commission_fixed_per_customer(self):
        b = _book()
        d = b.record_deal("TPI2", "C2", 20.0, 5_000.0, dt.date(2022,7,1))
        assert d.commission_gbp == pytest.approx(80.0)

    def test_deals_for_tpi(self):
        b = _book()
        b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))
        b.record_deal("TPI1", "C3", 30.0, 8_000.0, dt.date(2022,8,1))
        assert len(b.deals_for_tpi("TPI1")) == 2

    def test_total_commission_all(self):
        b = _book()
        b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))  # 150
        b.record_deal("TPI2", "C2", 20.0, 5_000.0, dt.date(2022,7,1))   # 80
        assert b.total_commission_gbp() == pytest.approx(230.0)

    def test_suspend_changes_tier(self):
        b = _book()
        suspended = b.suspend("TPI2")
        assert suspended.tier == TPITier.SUSPENDED

    def test_active_tpis_excludes_suspended(self):
        b = _book()
        b.suspend("TPI2")
        active = b.active_tpis()
        assert all(t.tier != TPITier.SUSPENDED for t in active)

    def test_record_deal_raises_for_suspended(self):
        b = _book()
        b.suspend("TPI2")
        with pytest.raises(ValueError):
            b.record_deal("TPI2", "C2", 20.0, 5_000.0, dt.date(2022,7,1))

    def test_annual_summary_keys(self):
        b = _book()
        b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))
        s = b.annual_summary(2022)
        assert "deal_count" in s and "total_commission_gbp" in s

    def test_total_commission_by_tpi(self):
        b = _book()
        b.record_deal("TPI1", "C1", 50.0, 10_000.0, dt.date(2022,6,1))
        b.record_deal("TPI1", "C3", 30.0, 8_000.0, dt.date(2022,8,1))
        total = b.total_commission_gbp("TPI1")
        # 150 + 120 = 270
        assert total == pytest.approx(270.0)
