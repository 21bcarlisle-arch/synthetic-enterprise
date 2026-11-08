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
