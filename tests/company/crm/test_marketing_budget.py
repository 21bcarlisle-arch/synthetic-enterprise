import pytest
from company.crm.marketing_budget import (
    MarketingCategory, MarketingSpend, AnnualMarketingBudget, MarketingBudgetTracker
)


def test_record_spend_and_cac():
    tracker = MarketingBudgetTracker()
    s = tracker.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2023, 65000.0, 1000)
    assert s.cost_per_customer_gbp == pytest.approx(65.0)


def test_budget_utilisation():
    tracker = MarketingBudgetTracker()
    tracker.set_budget(2023, 200000.0)
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2023, 80000.0, 2000)
    tracker.record_spend(MarketingCategory.TELESALES_COMMISSION, 2023, 50000.0, 500)
    budget = tracker.annual_budget(2023)
    assert budget.budget_utilisation_pct == pytest.approx(65.0)


def test_blended_cac():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2023, 65000.0, 1000)
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2023, 28000.0, 1000)
    budget = tracker.annual_budget(2023)
    assert budget.blended_cac_gbp == pytest.approx(46.5)


def test_total_customers_acquired():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2023, 65000.0, 1000)
    tracker.record_spend(MarketingCategory.REFERRAL_REWARD, 2023, 20000.0, 1000)
    budget = tracker.annual_budget(2023)
    assert budget.total_customers_acquired == 2000


def test_annual_budget_summary_keys():
    tracker = MarketingBudgetTracker()
    tracker.set_budget(2022, 300000.0)
    tracker.record_spend(MarketingCategory.BRAND_ADVERTISING, 2022, 150000.0, 0)
    tracker.record_spend(MarketingCategory.RETENTION_OUTBOUND, 2022, 30000.0, 2500)
    budget = tracker.annual_budget(2022)
    s = budget.summary()
    assert 'blended_cac_gbp' in s
    assert 'by_category' in s
    assert 'budget_utilisation_pct' in s


def test_zero_customers_acquired_cac():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.BRAND_ADVERTISING, 2022, 100000.0, 0)
    budget = tracker.annual_budget(2022)
    assert budget.blended_cac_gbp == 0.0


def test_total_spend_all_years():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2021, 50000.0, 1000)
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2022, 80000.0, 1500)
    assert tracker.total_spend_all_years() == pytest.approx(130000.0)


def test_cac_by_category():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2023, 65000.0, 1000)
    tracker.record_spend(MarketingCategory.REFERRAL_REWARD, 2023, 20000.0, 1000)
    cac = tracker.cac_by_category(2023)
    assert cac['price_comparison_commission'] == pytest.approx(65.0)
    assert cac['referral_reward'] == pytest.approx(20.0)
