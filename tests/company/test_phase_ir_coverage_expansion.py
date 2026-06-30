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


# ===== vulnerability_index =====
from company.crm.vulnerability_index import (
    assess_vulnerability, FuelPovertyIndicator, VulnerabilityBand
)


class TestVulnerabilityIndex:
    def test_home_oxygen_critical(self):
        a = assess_vulnerability("C1", dt.date(2022,1,1),
                                  [FuelPovertyIndicator.HOME_OXYGEN])
        assert a.band == VulnerabilityBand.CRITICAL

    def test_arrears_score_zero_when_no_arrears(self):
        a = assess_vulnerability("C2", dt.date(2022,1,1), [], arrears_gbp=0.0)
        assert a.arrears_score == 0

    def test_arrears_score_5_small(self):
        a = assess_vulnerability("C2", dt.date(2022,1,1), [], arrears_gbp=100.0)
        assert a.arrears_score == 5

    def test_arrears_score_10_medium(self):
        a = assess_vulnerability("C2", dt.date(2022,1,1), [], arrears_gbp=300.0)
        assert a.arrears_score == 10

    def test_arrears_score_20_high(self):
        a = assess_vulnerability("C2", dt.date(2022,1,1), [], arrears_gbp=600.0)
        assert a.arrears_score == 20

    def test_fuel_poverty_score_high(self):
        a = assess_vulnerability("C3", dt.date(2022,1,1), [], fuel_spend_pct=0.12)
        assert a.fuel_poverty_score == 20

    def test_ppm_score(self):
        a = assess_vulnerability("C4", dt.date(2022,1,1), [], has_ppm=True)
        assert a.ppm_score == 10

    def test_is_priority_services_high(self):
        # DISABILITY(25) + CHILD_HOUSEHOLD(10) = 35 → HIGH band
        a = assess_vulnerability("C5", dt.date(2022,1,1),
                                  [FuelPovertyIndicator.DISABILITY,
                                   FuelPovertyIndicator.CHILD_HOUSEHOLD])
        assert a.is_priority_services

    def test_disconnection_protected_critical_only(self):
        a = assess_vulnerability("C6", dt.date(2022,1,1),
                                  [FuelPovertyIndicator.HOME_OXYGEN])  # CRITICAL
        assert a.disconnection_protected

    def test_disconnection_not_protected_medium(self):
        a = assess_vulnerability("C7", dt.date(2022,1,1),
                                  [FuelPovertyIndicator.CHILD_HOUSEHOLD])  # +10 → MEDIUM
        assert not a.disconnection_protected


# ===== contact_log =====
from company.crm.contact_log import (
    ContactLog, ContactChannel, ContactReason
)


def _log():
    l = ContactLog()
    l.record("C1", ContactChannel.PHONE, ContactReason.BILLING_QUERY, dt.date(2022,3,1))
    l.record("C1", ContactChannel.WEBCHAT, ContactReason.COMPLAINT, dt.date(2022,4,1),
              handle_minutes=20.0, escalated=True, resolved=False)
    l.record("C2", ContactChannel.EMAIL, ContactReason.PAYMENT_DIFFICULTY,
              dt.date(2022,5,1))
    return l


class TestContactLog:
    def test_interaction_id_sequential(self):
        l = _log()
        assert l._interactions[0].interaction_id == 1
        assert l._interactions[1].interaction_id == 2

    def test_default_handle_minutes_from_lookup(self):
        l = _log()
        # billing_query default = 8.0
        assert l._interactions[0].handle_minutes == pytest.approx(8.0)

    def test_contacts_for_customer(self):
        l = _log()
        assert len(l.contacts_for_customer("C1")) == 2

    def test_escalated_flag(self):
        l = _log()
        assert l._interactions[1].escalated

    def test_not_resolved_flag(self):
        l = _log()
        assert not l._interactions[1].resolved

    def test_avg_handle_minutes_for_reason(self):
        l = _log()
        # Only one complaint at 20 minutes
        avg = l.avg_handle_minutes_for_reason(ContactReason.COMPLAINT)
        assert avg == pytest.approx(20.0)

    def test_annual_summary_total(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["total"] == 3

    def test_annual_summary_escalated(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["escalated"] == 1

    def test_annual_summary_unresolved(self):
        l = _log()
        s = l.annual_summary(2022)
        assert s["unresolved"] == 1

    def test_annual_summary_by_reason(self):
        l = _log()
        s = l.annual_summary(2022)
        assert "billing_query" in s["by_reason"]
