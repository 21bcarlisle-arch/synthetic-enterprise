import datetime as dt
import pytest
from company.crm.tpi_book import (
    TPITier, TPICommissionBasis, TPI, TPIDeal, TPIBook
)


def _base_book():
    book = TPIBook()
    book.register(
        'TPI001', 'Beacon Energy Brokers', TPITier.PREFERRED,
        TPICommissionBasis.PCT_OF_ANNUAL_REVENUE, 2.5,
        dt.date(2020, 1, 1)
    )
    return book


def test_register_tpi():
    book = _base_book()
    assert len(book.active_tpis()) == 1
    assert book.active_tpis()[0].name == 'Beacon Energy Brokers'


def test_commission_pct_of_revenue():
    book = _base_book()
    deal = book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 3, 1))
    assert deal.commission_gbp == pytest.approx(1_250.0)


def test_commission_fixed_per_customer():
    book = TPIBook()
    book.register('TPI002', 'QuickSwitch', TPITier.STANDARD,
                  TPICommissionBasis.FIXED_PER_CUSTOMER, 80.0, dt.date(2019, 1, 1))
    deal = book.record_deal('TPI002', 'C002', 50.0, 20_000, dt.date(2021, 6, 1))
    assert deal.commission_gbp == pytest.approx(80.0)


def test_commission_per_mwh():
    book = TPIBook()
    book.register('TPI003', 'EnergyBrokerPlus', TPITier.STANDARD,
                  TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION, 1.50, dt.date(2018, 1, 1))
    deal = book.record_deal('TPI003', 'C003', 200.0, 30_000, dt.date(2021, 9, 1))
    assert deal.commission_gbp == pytest.approx(300.0)


def test_suspend_blocks_deals():
    book = _base_book()
    book.suspend('TPI001')
    with pytest.raises(ValueError, match='suspended'):
        book.record_deal('TPI001', 'C005', 50.0, 20_000, dt.date(2022, 1, 1))


def test_active_tpis_excludes_suspended():
    book = _base_book()
    book.suspend('TPI001')
    assert len(book.active_tpis()) == 0


def test_total_commission_for_tpi():
    book = _base_book()
    book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 3, 1))
    book.record_deal('TPI001', 'C002', 80.0, 40_000, dt.date(2022, 4, 1))
    assert book.total_commission_gbp('TPI001') == pytest.approx(2_250.0)


def test_annual_summary_keys():
    book = _base_book()
    book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 3, 1))
    s = book.annual_summary(2022)
    assert s['deal_count'] == 1
    assert s['total_commission_gbp'] == pytest.approx(1_250.0)
    assert 'total_annual_revenue_gbp' in s
    assert 'tpi_count' in s


def test_deals_for_tpi():
    book = _base_book()
    book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 3, 1))
    book.record_deal('TPI001', 'C002', 80.0, 40_000, dt.date(2022, 4, 1))
    assert len(book.deals_for_tpi('TPI001')) == 2


# --- Phase JY depth tests ---

def test_deal_id_sequential():
    book = _base_book()
    d1 = book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 1, 1))
    d2 = book.record_deal('TPI001', 'C002', 80.0, 40_000, dt.date(2022, 2, 1))
    assert d1.deal_id == 'DEAL-0001'
    assert d2.deal_id == 'DEAL-0002'


def test_total_commission_all_tpis():
    book = TPIBook()
    book.register('T1', 'Alpha', TPITier.STANDARD, TPICommissionBasis.FIXED_PER_CUSTOMER, 50.0, dt.date(2020, 1, 1))
    book.register('T2', 'Beta', TPITier.STANDARD, TPICommissionBasis.FIXED_PER_CUSTOMER, 30.0, dt.date(2020, 1, 1))
    book.record_deal('T1', 'C001', 100.0, 20_000, dt.date(2022, 1, 1))
    book.record_deal('T2', 'C002', 100.0, 20_000, dt.date(2022, 1, 1))
    assert book.total_commission_gbp() == pytest.approx(80.0)


def test_deals_for_tpi_empty():
    book = _base_book()
    assert book.deals_for_tpi('TPI001') == []


def test_annual_summary_empty_year():
    book = _base_book()
    s = book.annual_summary(2099)
    assert s['deal_count'] == 0
    assert s['total_commission_gbp'] == pytest.approx(0.0)


def test_annual_summary_two_deals_same_year():
    book = _base_book()
    book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 3, 1))
    book.record_deal('TPI001', 'C002', 80.0, 40_000, dt.date(2022, 5, 1))
    s = book.annual_summary(2022)
    assert s['deal_count'] == 2


def test_annual_summary_year_filter():
    book = _base_book()
    book.record_deal('TPI001', 'C001', 100.0, 50_000, dt.date(2022, 1, 1))
    book.record_deal('TPI001', 'C002', 80.0, 40_000, dt.date(2023, 1, 1))
    s = book.annual_summary(2022)
    assert s['deal_count'] == 1


def test_tpi_accredited_default_true():
    book = _base_book()
    tpi = book.active_tpis()[0]
    assert tpi.accredited is True


def test_suspend_changes_tier_to_suspended():
    book = _base_book()
    suspended = book.suspend('TPI001')
    assert suspended.tier == TPITier.SUSPENDED


def test_annual_summary_tpi_count_two():
    book = TPIBook()
    book.register('T1', 'Alpha', TPITier.PREFERRED, TPICommissionBasis.FIXED_PER_CUSTOMER, 50.0, dt.date(2020, 1, 1))
    book.register('T2', 'Beta', TPITier.STANDARD, TPICommissionBasis.FIXED_PER_CUSTOMER, 30.0, dt.date(2020, 1, 1))
    book.record_deal('T1', 'C001', 100.0, 20_000, dt.date(2022, 1, 1))
    book.record_deal('T2', 'C002', 100.0, 20_000, dt.date(2022, 6, 1))
    s = book.annual_summary(2022)
    assert s['tpi_count'] == 2


def test_probation_tier_can_record_deal():
    book = TPIBook()
    book.register('TPI_P', 'Watchlist Broker', TPITier.PROBATION,
                  TPICommissionBasis.FIXED_PER_CUSTOMER, 40.0, dt.date(2021, 1, 1))
    deal = book.record_deal('TPI_P', 'C010', 50.0, 15_000, dt.date(2022, 1, 1))
    assert deal.deal_id == 'DEAL-0001'
