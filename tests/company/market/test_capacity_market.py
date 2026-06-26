import datetime as dt
import pytest
from company.market.capacity_market import (
    CMUnitType, AuctionType, CMUnit, CMObligation,
    CapacityMarketBook, get_cm_price
)


def test_cm_price_2022():
    assert get_cm_price(2022) == pytest.approx(75.00)


def test_cm_price_2016():
    assert get_cm_price(2016) == pytest.approx(18.00)


def test_annual_revenue():
    unit = CMUnit('BATT-001', CMUnitType.BATTERY, 10_000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    assert o.annual_revenue_gbp == pytest.approx(10_000.0 * 75.0)


def test_penalty_reduces_net():
    unit = CMUnit('BATT-001', CMUnitType.BATTERY, 10_000.0, dt.date(2022, 1, 1))
    o = CMObligation(unit, 2022, AuctionType.T4, 75.0)
    o.apply_penalty(50_000.0)
    assert o.net_revenue_gbp == pytest.approx(10_000.0 * 75.0 - 50_000.0)


def test_book_register_and_obligation():
    book = CapacityMarketBook()
    unit = book.register_unit('DR-001', CMUnitType.DEMAND_RESPONSE, 5000.0, dt.date(2022, 1, 1))
    ob = book.add_obligation(unit, 2022, AuctionType.T4)
    assert ob.clearing_price_gbp_per_kw == pytest.approx(75.0)


def test_total_revenue():
    book = CapacityMarketBook()
    unit = book.register_unit('CCGT-001', CMUnitType.CCGT, 100_000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    assert book.total_revenue_gbp(2022) == pytest.approx(100_000.0 * 75.0)


def test_crisis_price_higher():
    assert get_cm_price(2022) > get_cm_price(2016)


def test_total_derated_kw():
    book = CapacityMarketBook()
    u1 = book.register_unit('U1', CMUnitType.BATTERY, 3000.0, dt.date(2022, 1, 1))
    u2 = book.register_unit('U2', CMUnitType.DEMAND_RESPONSE, 2000.0, dt.date(2022, 1, 1))
    book.add_obligation(u1, 2022, AuctionType.T4)
    book.add_obligation(u2, 2022, AuctionType.T1)
    assert book.total_derated_kw(2022) == pytest.approx(5000.0)


def test_cm_summary():
    book = CapacityMarketBook()
    unit = book.register_unit('U1', CMUnitType.OCGT, 50_000.0, dt.date(2022, 1, 1))
    book.add_obligation(unit, 2022, AuctionType.T4)
    s = book.cm_summary(2022)
    assert s['obligations'] == 1
    assert s['total_derated_kw'] == pytest.approx(50_000.0)
