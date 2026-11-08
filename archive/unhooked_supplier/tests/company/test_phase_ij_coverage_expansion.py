# Increment 3: the legs of tests/company/test_phase_ij_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase IJ: deeper coverage for campaign_tracker, marketing_budget, acquisition_cohort."""
import datetime as dt
import pytest


# ===== marketing_budget =====
from company.crm.marketing_budget import (
    MarketingBudgetTracker, MarketingCategory, MarketingSpend
)


def _budget():
    b = MarketingBudgetTracker()
    b.set_budget(2022, 500_000.0)
    b.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2022,
                   150_000.0, customers_acquired=300)
    b.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2022,
                   100_000.0, customers_acquired=200)
    b.record_spend(MarketingCategory.TELESALES_COMMISSION, 2023,
                   80_000.0, customers_acquired=100)
    return b


class TestMarketingBudget:
    def test_cost_per_customer(self):
        spend = MarketingSpend(MarketingCategory.DIGITAL_ADVERTISING, 2022, 100_000.0, 200)
        assert spend.cost_per_customer_gbp == pytest.approx(500.0)

    def test_cost_per_customer_zero_when_no_acquisitions(self):
        spend = MarketingSpend(MarketingCategory.BRAND_ADVERTISING, 2022, 50_000.0, 0)
        assert spend.cost_per_customer_gbp == pytest.approx(0.0)

    def test_total_spent_gbp(self):
        b = _budget()
        ab = b.annual_budget(2022)
        assert ab.total_spent_gbp == pytest.approx(250_000.0)

    def test_blended_cac_gbp(self):
        b = _budget()
        ab = b.annual_budget(2022)
        # 250k spend / 500 customers = 500
        assert ab.blended_cac_gbp == pytest.approx(500.0)

    def test_budget_utilisation_pct(self):
        b = _budget()
        ab = b.annual_budget(2022)
        assert ab.budget_utilisation_pct == pytest.approx(50.0)

    def test_total_spend_all_years(self):
        b = _budget()
        assert b.total_spend_all_years() == pytest.approx(330_000.0)

    def test_cac_by_category(self):
        b = _budget()
        cac = b.cac_by_category(2022)
        assert cac["price_comparison_commission"] == pytest.approx(500.0)

    def test_annual_budget_summary_keys(self):
        b = _budget()
        s = b.annual_budget(2022).summary()
        assert "blended_cac_gbp" in s and "by_category" in s

    def test_annual_budget_zero_when_no_budget_set(self):
        b = MarketingBudgetTracker()
        ab = b.annual_budget(2025)
        assert ab.budget_gbp == 0.0

    def test_total_customers_acquired(self):
        b = _budget()
        ab = b.annual_budget(2022)
        assert ab.total_customers_acquired == 500


# ==== archive increment 3b: the legs that stayed live in 3a, archived now (the live file is still at its path) ====

# ARCHIVED LEGS of tests/company/test_phase_ij_coverage_expansion.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/test_phase_ij_coverage_expansion.py.
"""Phase IJ: deeper coverage for campaign_tracker, marketing_budget, acquisition_cohort."""
import datetime as dt
import pytest

# ===== campaign_tracker =====
from company.crm.campaign_tracker import (
    CampaignTracker, CampaignType, ContactOutcome, ContactChannel
)


def _tracker():
    t = CampaignTracker()
    t.create_campaign("C001", CampaignType.RENEWAL_CHASE,
                       dt.date(2022,1,1), 200, ContactChannel.EMAIL)
    t.create_campaign("C002", CampaignType.DEBT_COLLECTION,
                       dt.date(2022,2,1), 50, ContactChannel.PHONE)
    return t


class TestCampaignTracker:
    def test_contact_id_format(self):
        t = _tracker()
        contact = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                                    ContactOutcome.CONVERTED)
        assert contact.contact_id == "CTT-0001"

    def test_is_converted(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.CONVERTED)
        assert c.is_converted

    def test_is_reached_for_callback(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.CALLBACK_ARRANGED)
        assert c.is_reached

    def test_is_not_reached_for_no_answer(self):
        t = _tracker()
        c = t.record_contact("C001", "CU1", dt.date(2022,1,5),
                              ContactOutcome.NO_ANSWER)
        assert not c.is_reached

    def test_conversion_rate(self):
        t = _tracker()
        t.record_contact("C001", "CU1", dt.date(2022,1,5), ContactOutcome.CONVERTED)
        t.record_contact("C001", "CU2", dt.date(2022,1,6), ContactOutcome.REFUSED)
        camp = t.get("C001")
        # 1 converted / 2 reached = 50%
        assert camp.conversion_rate == pytest.approx(50.0)

    def test_contact_rate(self):
        t = _tracker()
        t.record_contact("C001", "CU1", dt.date(2022,1,5), ContactOutcome.CONVERTED)
        t.record_contact("C001", "CU2", dt.date(2022,1,6), ContactOutcome.NO_ANSWER)
        camp = t.get("C001")
        # 1 reached out of 2 total = 50%
        assert camp.contact_rate == pytest.approx(50.0)

    def test_active_campaign_before_close(self):
        t = _tracker()
        active = t.active_campaigns()
        assert len(active) == 2

    def test_close_campaign_removes_from_active(self):
        t = _tracker()
        t.close_campaign("C001", dt.date(2022,3,31))
        active = t.active_campaigns()
        assert len(active) == 1

    def test_campaigns_by_type(self):
        t = _tracker()
        debt = t.campaigns_by_type(CampaignType.DEBT_COLLECTION)
        assert len(debt) == 1

    def test_summary_keys(self):
        t = _tracker()
        s = t.get("C001").summary()
        assert "conversion_rate_pct" in s and "contact_rate_pct" in s and "is_active" in s


# ===== acquisition_cohort =====
from company.crm.acquisition_cohort import (
    AcquisitionCohort, AcquisitionChannel
)


def _cohort():
    c = AcquisitionCohort("COH-2022-01", 2022, 1, AcquisitionChannel.PRICE_COMPARISON)
    c.add_customer("CU1", dt.date(2022,1,15), 150.0, 1200.0)
    c.add_customer("CU2", dt.date(2022,1,20), 200.0, 1800.0)
    c.add_customer("CU3", dt.date(2022,2,1), 120.0, 960.0)
    return c


