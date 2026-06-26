import datetime as dt
import pytest
from company.market.ppa_book import (
    PPATechnology, PPAPricingType, PPAContract, PPABook
)

START = dt.date(2020, 1, 1)
END = dt.date(2024, 12, 31)


def _book_with_wind():
    book = PPABook()
    book.add_contract(
        contract_id='PPA-001', generator_id='GEN-WIND-01',
        technology=PPATechnology.ONSHORE_WIND,
        start_date=START, end_date=END,
        capacity_mw=50.0, annual_mwh=120_000.0,
        price_gbp_per_mwh=45.0,
    )
    return book


def test_ppa_technology_values():
    assert PPATechnology.ONSHORE_WIND == 'onshore_wind'
    assert PPATechnology.OFFSHORE_WIND == 'offshore_wind'
    assert PPATechnology.SOLAR == 'solar'


def test_ppa_pricing_types():
    assert PPAPricingType.FIXED == 'fixed'
    assert PPAPricingType.FLOOR == 'floor'
    assert PPAPricingType.INDEXED == 'indexed'


def test_contract_is_active_during():
    c = PPAContract(
        contract_id='P1', generator_id='G1',
        technology=PPATechnology.SOLAR,
        start_date=START, end_date=END,
        capacity_mw=10.0, annual_generation_mwh=15_000.0,
        price_gbp_per_mwh=40.0,
    )
    assert c.is_active(dt.date(2022, 6, 1))
    assert not c.is_active(dt.date(2019, 12, 31))
    assert not c.is_active(dt.date(2025, 1, 1))


def test_contract_term_years():
    c = PPAContract(
        contract_id='P2', generator_id='G2',
        technology=PPATechnology.OFFSHORE_WIND,
        start_date=dt.date(2020, 1, 1), end_date=dt.date(2024, 12, 31),
        capacity_mw=100.0, annual_generation_mwh=300_000.0,
        price_gbp_per_mwh=55.0,
    )
    assert c.term_years == pytest.approx(5.0, abs=0.1)


def test_contract_annual_cost():
    c = PPAContract(
        contract_id='P3', generator_id='G3',
        technology=PPATechnology.SOLAR,
        start_date=START, end_date=END,
        capacity_mw=20.0, annual_generation_mwh=18_000.0,
        price_gbp_per_mwh=42.0,
    )
    assert c.annual_cost_gbp == pytest.approx(18_000.0 * 42.0, rel=1e-6)


def test_effective_price_fixed_ignores_market():
    c = PPAContract(
        contract_id='P4', generator_id='G4',
        technology=PPATechnology.ONSHORE_WIND,
        start_date=START, end_date=END,
        capacity_mw=30.0, annual_generation_mwh=80_000.0,
        price_gbp_per_mwh=45.0, pricing_type=PPAPricingType.FIXED,
    )
    assert c.effective_price(200.0) == 45.0
    assert c.effective_price(10.0) == 45.0


def test_effective_price_floor_tracks_market_above_floor():
    c = PPAContract(
        contract_id='P5', generator_id='G5',
        technology=PPATechnology.HYDRO,
        start_date=START, end_date=END,
        capacity_mw=15.0, annual_generation_mwh=50_000.0,
        price_gbp_per_mwh=40.0, pricing_type=PPAPricingType.FLOOR,
        floor_price_gbp_per_mwh=40.0,
    )
    assert c.effective_price(60.0) == 60.0
    assert c.effective_price(30.0) == 40.0


def test_book_active_contracts_date_filter():
    book = _book_with_wind()
    assert len(book.active_contracts(dt.date(2022, 1, 1))) == 1
    assert len(book.active_contracts(dt.date(2018, 1, 1))) == 0
    assert len(book.active_contracts(dt.date(2026, 1, 1))) == 0


def test_book_total_contracted_mwh():
    book = _book_with_wind()
    book.add_contract(
        'PPA-002', 'GEN-SOLAR-01', PPATechnology.SOLAR,
        START, END, 25.0, 30_000.0, 38.0,
    )
    total = book.total_contracted_mwh(dt.date(2022, 6, 1))
    assert total == pytest.approx(150_000.0, rel=1e-6)


def test_book_vs_market_positive_when_ppa_cheaper():
    book = PPABook()
    book.add_contract(
        'PPA-003', 'GEN-01', PPATechnology.ONSHORE_WIND,
        START, END, 50.0, 100_000.0, 45.0,
    )
    market_price = 80.0
    vs_market = book.total_vs_market_gbp(dt.date(2022, 1, 1), market_price)
    assert vs_market == pytest.approx(100_000.0 * (45.0 - 80.0), rel=1e-6)
    assert vs_market < 0


def test_book_ppa_summary_keys():
    book = _book_with_wind()
    s = book.ppa_summary(dt.date(2022, 1, 1), market_price=70.0)
    assert s['active_ppas'] == 1
    assert s['total_contracted_mwh'] == pytest.approx(120_000.0)
    assert s['total_annual_cost_gbp'] == pytest.approx(120_000.0 * 45.0, rel=1e-6)
    assert 'vs_market_gbp' in s
    assert 'renewable_share_mwh' in s
