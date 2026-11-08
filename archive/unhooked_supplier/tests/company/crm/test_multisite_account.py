import datetime as dt
import pytest
from company.crm.multisite_account import (
    SiteCategory, BillingFrequency, SupplyPoint, MultisiteAccount, MultisitePortfolio
)


def _make_account() -> MultisiteAccount:
    p = MultisitePortfolio()
    acc = p.create_account(
        'ACC001', 'MegaCorp Ltd', BillingFrequency.MONTHLY,
        'Sarah Thompson', 500_000.0
    )
    acc.add_site('MPAN001', 'Head Office', 'EC2V 8RF', SiteCategory.HEAD_OFFICE,
                  annual_kwh=500_000.0, max_demand_kva=200.0, connection_voltage_kv=11.0)
    acc.add_site('MPAN002', 'Warehouse A', 'LS1 1BA', SiteCategory.WAREHOUSE,
                  annual_kwh=1_200_000.0, max_demand_kva=500.0, connection_voltage_kv=11.0)
    acc.add_site('MPAN003', 'Retail Unit', 'M1 1AA', SiteCategory.RETAIL_UNIT,
                  annual_kwh=80_000.0, max_demand_kva=30.0, connection_voltage_kv=0.4)
    return acc


def test_site_count():
    acc = _make_account()
    assert acc.site_count == 3


def test_total_annual_mwh():
    acc = _make_account()
    assert acc.total_annual_mwh == pytest.approx(1780.0, rel=0.01)


def test_hv_sites():
    acc = _make_account()
    hv = acc.hv_sites()
    assert len(hv) == 2
    assert all(sp.connection_voltage_kv >= 11.0 for sp in hv)


def test_lv_site_not_hv():
    sp = SupplyPoint('MPAN_LV', 'Retail', 'M1', SiteCategory.RETAIL_UNIT,
                      80_000.0, 30.0, 0.4)
    assert not sp.is_hv


def test_peak_site():
    acc = _make_account()
    peak = acc.peak_site
    assert peak is not None
    assert peak.mpan == 'MPAN002'


def test_remove_site():
    acc = _make_account()
    removed = acc.remove_site('MPAN003')
    assert removed
    assert acc.site_count == 2


def test_sites_by_category():
    acc = _make_account()
    by_cat = acc.sites_by_category()
    assert 'warehouse' in by_cat
    assert 'retail_unit' in by_cat


def test_portfolio_total_mwh():
    p = MultisitePortfolio()
    a1 = p.create_account('A1', 'Corp A', BillingFrequency.CONSOLIDATED, 'John', 1_000_000.0)
    a1.add_site('M1', 'Site 1', 'SW1', SiteCategory.MANUFACTURING, 2_000_000.0, 800.0)
    a2 = p.create_account('A2', 'Corp B', BillingFrequency.MONTHLY, 'Jane', 500_000.0)
    a2.add_site('M2', 'Site 2', 'N1', SiteCategory.HEAD_OFFICE, 500_000.0, 200.0)
    total = p.total_portfolio_mwh()
    assert total == pytest.approx(2500.0, rel=0.01)


def test_account_summary():
    acc = _make_account()
    s = acc.account_summary()
    assert s['site_count'] == 3
    assert s['hv_sites'] == 2
    assert 'categories' in s


def test_peak_site_none_when_no_sites():
    p = MultisitePortfolio()
    acc = p.create_account('EMPTY', 'EmptyCorp', BillingFrequency.MONTHLY, 'AM', 100_000.0)
    assert acc.peak_site is None


def test_remove_site_returns_false_when_not_found():
    acc = _make_account()
    assert not acc.remove_site('NONEXISTENT')


def test_get_account_found():
    p = MultisitePortfolio()
    p.create_account('ACC001', 'Corp A', BillingFrequency.MONTHLY, 'AM', 500_000.0)
    acc = p.get('ACC001')
    assert acc is not None
    assert acc.company_name == 'Corp A'


def test_get_account_not_found():
    p = MultisitePortfolio()
    assert p.get('NONEXISTENT') is None


def test_annual_mwh_property_on_supply_point():
    sp = SupplyPoint('M1', 'Site', 'EC1', SiteCategory.HEAD_OFFICE, 500_000.0, 200.0)
    assert sp.annual_mwh == pytest.approx(500.0)


def test_accounts_by_manager():
    p = MultisitePortfolio()
    p.create_account('A1', 'Corp A', BillingFrequency.MONTHLY, 'Alice', 200_000.0)
    p.create_account('A2', 'Corp B', BillingFrequency.QUARTERLY, 'Bob', 300_000.0)
    p.create_account('A3', 'Corp C', BillingFrequency.MONTHLY, 'Alice', 150_000.0)
    alice_accounts = p.accounts_by_manager('Alice')
    assert len(alice_accounts) == 2
    assert all(a.account_manager == 'Alice' for a in alice_accounts)


def test_largest_accounts_sorted():
    p = MultisitePortfolio()
    a1 = p.create_account('A1', 'Small', BillingFrequency.MONTHLY, 'AM', 100_000.0)
    a1.add_site('M1', 'Site', 'SW1', SiteCategory.HEAD_OFFICE, 500_000.0, 200.0)
    a2 = p.create_account('A2', 'Large', BillingFrequency.MONTHLY, 'AM', 500_000.0)
    a2.add_site('M2', 'Site', 'EC1', SiteCategory.MANUFACTURING, 5_000_000.0, 2000.0)
    largest = p.largest_accounts(n=1)
    assert largest[0].account_id == 'A2'


def test_add_site_stored():
    p = MultisitePortfolio()
    acc = p.create_account('A1', 'TestCorp', BillingFrequency.MONTHLY, 'AM', 100_000.0)
    sp = acc.add_site('M1', 'Office', 'N1', SiteCategory.REMOTE_OFFICE, 100_000.0, 50.0)
    assert sp in acc.supply_points


def test_account_summary_credit_limit():
    acc = _make_account()
    s = acc.account_summary()
    assert s['credit_limit_gbp'] == pytest.approx(500_000.0)


def test_supply_point_at_33kv_is_hv():
    sp = SupplyPoint('HV1', 'Substation', 'SW1', SiteCategory.MANUFACTURING,
                      10_000_000.0, 5000.0, connection_voltage_kv=33.0)
    assert sp.is_hv
