"""Tests for Phase V: ToU Migration Impact Scenario."""
import pytest
from company.pricing.tou_migration_scenario import MigrationScenario, ToUMigrationScenarioBook
from company.pricing.ev_cross_subsidy import CrossSubsidyRegister
from company.pricing.tou_tariff_assessor import WholesaleBandRates

FLAT = 28.5
NORMAL = WholesaleBandRates.normal()
CRISIS = WholesaleBandRates.crisis()


def _ev_records(consumptions, rate=FLAT, wholesale=None):
    if wholesale is None:
        wholesale = NORMAL
    r = CrossSubsidyRegister()
    for i, kwh in enumerate(consumptions):
        r.record(f"EV{i}", 2023, kwh, 1, rate, wholesale)
    return r._records


def test_zero_migration_no_margin_change():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 0.0)
    assert s.migrated_count == 0
    assert s.retained_count == 2
    assert s.margin_delta_gbp == 0.0


def test_full_migration_all_customers_on_tou():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 100.0)
    assert s.migrated_count == 2
    assert s.retained_count == 0
    assert s.margin_delta_gbp < 0


def test_partial_migration_50pct():
    records = _ev_records([3000.0, 3000.0])
    book = ToUMigrationScenarioBook()
    s50 = book.run_scenario(records, 50.0)
    assert s50.migrated_count == 1
    assert s50.retained_count == 1


def test_ev_migration_negative_for_supplier():
    records = _ev_records([3000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 100.0)
    assert s.margin_delta_gbp < 0
    assert s.is_margin_positive is False


def test_higher_consumption_bigger_margin_delta():
    low_records = _ev_records([1000.0])
    high_records = _ev_records([8000.0])
    book = ToUMigrationScenarioBook()
    s_low = book.run_scenario(low_records, 100.0)
    s_high = book.run_scenario(high_records, 100.0)
    assert abs(s_high.margin_delta_gbp) > abs(s_low.margin_delta_gbp)


def test_customers_save_on_migration():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 100.0)
    assert s.total_customer_saving_gbp > 0
    assert s.avg_customer_saving_gbp > 0


def test_migrated_plus_retained_equals_total():
    records = _ev_records([3000.0, 4000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 67.0)
    assert s.migrated_count + s.retained_count == s.total_ev_accounts


def test_frozen_scenario_immutable():
    records = _ev_records([3000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 50.0)
    with pytest.raises(Exception):
        s.margin_delta_gbp = 0.0


def test_invalid_migration_rate_raises():
    records = _ev_records([3000.0])
    book = ToUMigrationScenarioBook()
    with pytest.raises(ValueError):
        book.run_scenario(records, 101.0)
    with pytest.raises(ValueError):
        book.run_scenario(records, -1.0)


def test_compare_rates_returns_sorted():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    scenarios = book.compare_rates(records, [50.0, 0.0, 100.0])
    rates = [s.migration_rate_pct for s in scenarios]
    assert rates == sorted(rates)


def test_portfolio_summary_keys():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    book.run_scenario(records, 0.0)
    book.run_scenario(records, 50.0)
    book.run_scenario(records, 100.0)
    s = book.portfolio_summary()
    assert s["scenarios_run"] == 3
    assert "best_supplier_rate_pct" in s
    assert "best_supplier_margin_gbp" in s


def test_best_scenario_for_ev_portfolio_is_zero_migration():
    records = _ev_records([3000.0, 5000.0])
    book = ToUMigrationScenarioBook()
    book.compare_rates(records, [0.0, 25.0, 50.0, 75.0, 100.0])
    best = book.best_supplier_scenario()
    assert best.migration_rate_pct == 0.0


def test_empty_portfolio_scenario():
    book = ToUMigrationScenarioBook()
    s = book.run_scenario([], 50.0)
    assert s.total_ev_accounts == 0
    assert s.migrated_count == 0
    assert s.margin_delta_gbp == 0.0


def test_crisis_year_migration_more_negative():
    normal_records = _ev_records([3000.0], FLAT, NORMAL)
    crisis_flat = 80.0
    crisis_records = _ev_records([3000.0], crisis_flat, CRISIS)
    book = ToUMigrationScenarioBook()
    s_normal = book.run_scenario(normal_records, 100.0)
    s_crisis = book.run_scenario(crisis_records, 100.0)
    assert abs(s_crisis.margin_delta_gbp) > abs(s_normal.margin_delta_gbp)


def test_revenue_delta_negative_for_ev_on_tou():
    records = _ev_records([3000.0])
    book = ToUMigrationScenarioBook()
    s = book.run_scenario(records, 100.0)
    assert s.revenue_delta_gbp < 0


def test_scenarios_run_tracks_history():
    records = _ev_records([3000.0])
    book = ToUMigrationScenarioBook()
    book.run_scenario(records, 0.0)
    book.run_scenario(records, 100.0)
    assert len(book.scenarios_run()) == 2
