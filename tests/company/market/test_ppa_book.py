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


# --- Phase JQ depth tests ---

def test_effective_price_indexed_returns_market():
    c = PPAContract(
        contract_id='P6', generator_id='G6',
        technology=PPATechnology.ONSHORE_WIND,
        start_date=START, end_date=END,
        capacity_mw=20.0, annual_generation_mwh=50_000.0,
        price_gbp_per_mwh=45.0, pricing_type=PPAPricingType.INDEXED,
    )
    assert c.effective_price(80.0) == 80.0
    assert c.effective_price(30.0) == 30.0


def test_effective_price_floor_uses_floor_when_market_below():
    c = PPAContract(
        contract_id='P7', generator_id='G7',
        technology=PPATechnology.SOLAR,
        start_date=START, end_date=END,
        capacity_mw=10.0, annual_generation_mwh=20_000.0,
        price_gbp_per_mwh=40.0, pricing_type=PPAPricingType.FLOOR,
        floor_price_gbp_per_mwh=40.0,
    )
    assert c.effective_price(20.0) == 40.0


def test_vs_market_positive_when_ppa_above_market():
    c = PPAContract(
        contract_id='P8', generator_id='G8',
        technology=PPATechnology.BIOMASS,
        start_date=START, end_date=END,
        capacity_mw=5.0, annual_generation_mwh=10_000.0,
        price_gbp_per_mwh=100.0,
    )
    vs = c.vs_market_gbp(market_price=60.0)
    assert vs == pytest.approx(10_000.0 * (100.0 - 60.0), rel=1e-6)
    assert vs > 0


def test_book_total_annual_cost_gbp_two_active():
    book = PPABook()
    book.add_contract('A1', 'G1', PPATechnology.SOLAR, START, END, 10.0, 20_000.0, 40.0)
    book.add_contract('A2', 'G2', PPATechnology.ONSHORE_WIND, START, END, 30.0, 80_000.0, 50.0)
    total = book.total_annual_cost_gbp(dt.date(2022, 6, 1))
    assert total == pytest.approx(20_000.0 * 40.0 + 80_000.0 * 50.0, rel=1e-6)


def test_book_empty_active_contracts():
    book = PPABook()
    assert book.active_contracts(dt.date(2022, 1, 1)) == []


def test_floor_price_attribute_stored():
    c = PPAContract(
        contract_id='P9', generator_id='G9',
        technology=PPATechnology.HYDRO,
        start_date=START, end_date=END,
        capacity_mw=8.0, annual_generation_mwh=15_000.0,
        price_gbp_per_mwh=38.0, pricing_type=PPAPricingType.FLOOR,
        floor_price_gbp_per_mwh=35.0,
    )
    assert c.floor_price_gbp_per_mwh == 35.0


def test_capacity_mw_stored():
    c = PPAContract(
        contract_id='P10', generator_id='G10',
        technology=PPATechnology.OFFSHORE_WIND,
        start_date=START, end_date=END,
        capacity_mw=250.0, annual_generation_mwh=750_000.0,
        price_gbp_per_mwh=55.0,
    )
    assert c.capacity_mw == 250.0


def test_book_total_vs_market_two_contracts():
    book = PPABook()
    book.add_contract('B1', 'G1', PPATechnology.SOLAR, START, END, 20.0, 40_000.0, 45.0)
    book.add_contract('B2', 'G2', PPATechnology.ONSHORE_WIND, START, END, 50.0, 100_000.0, 50.0)
    market = 70.0
    total = book.total_vs_market_gbp(dt.date(2022, 6, 1), market)
    expected = 40_000.0 * (45.0 - 70.0) + 100_000.0 * (50.0 - 70.0)
    assert total == pytest.approx(expected, rel=1e-6)


def test_add_contract_returns_ppa_contract():
    book = PPABook()
    result = book.add_contract(
        'C1', 'G1', PPATechnology.SOLAR, START, END, 10.0, 15_000.0, 42.0,
    )
    assert isinstance(result, PPAContract)
    assert result.contract_id == 'C1'


def test_ppa_summary_vs_market_positive_when_ppa_expensive():
    book = PPABook()
    book.add_contract('D1', 'G1', PPATechnology.BIOMASS, START, END, 5.0, 8_000.0, 120.0)
    s = book.ppa_summary(dt.date(2022, 1, 1), market_price=50.0)
    assert s['vs_market_gbp'] > 0
