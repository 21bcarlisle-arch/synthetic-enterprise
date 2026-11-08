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


# --- Phase KJ depth tests ---

def test_category_stored_in_spend():
    tracker = MarketingBudgetTracker()
    s = tracker.record_spend(MarketingCategory.REFERRAL_REWARD, 2023, 10000.0, 500)
    assert s.category == MarketingCategory.REFERRAL_REWARD


def test_year_stored_in_spend():
    tracker = MarketingBudgetTracker()
    s = tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2022, 50000.0, 1000)
    assert s.year == 2022


def test_amount_gbp_stored():
    tracker = MarketingBudgetTracker()
    s = tracker.record_spend(MarketingCategory.BRAND_ADVERTISING, 2023, 75000.0, 0)
    assert s.amount_gbp == pytest.approx(75000.0)


def test_customers_acquired_stored():
    tracker = MarketingBudgetTracker()
    s = tracker.record_spend(MarketingCategory.TELESALES_COMMISSION, 2023, 30000.0, 300)
    assert s.customers_acquired == 300


def test_two_years_independent():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2021, 50000.0, 1000)
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2022, 80000.0, 1500)
    b2021 = tracker.annual_budget(2021)
    b2022 = tracker.annual_budget(2022)
    assert b2021.total_spent_gbp == pytest.approx(50000.0)
    assert b2022.total_spent_gbp == pytest.approx(80000.0)


def test_single_category_blended_cac_equals_that_cac():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.PRICE_COMPARISON_COMMISSION, 2023, 50000.0, 1000)
    budget = tracker.annual_budget(2023)
    assert budget.blended_cac_gbp == pytest.approx(50.0)


def test_total_customers_zero_brand_only():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.BRAND_ADVERTISING, 2023, 100000.0, 0)
    budget = tracker.annual_budget(2023)
    assert budget.total_customers_acquired == 0


def test_budget_utilisation_none_no_budget_set():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2023, 50000.0, 1000)
    budget = tracker.annual_budget(2023)
    assert budget.budget_utilisation_pct == pytest.approx(0.0)


def test_total_spend_all_years_empty_is_zero():
    tracker = MarketingBudgetTracker()
    assert tracker.total_spend_all_years() == pytest.approx(0.0)


def test_cac_by_category_missing_category_not_present():
    tracker = MarketingBudgetTracker()
    tracker.record_spend(MarketingCategory.DIGITAL_ADVERTISING, 2023, 30000.0, 1000)
    cac = tracker.cac_by_category(2023)
    assert 'price_comparison_commission' not in cac
