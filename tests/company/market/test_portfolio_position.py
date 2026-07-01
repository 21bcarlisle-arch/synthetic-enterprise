import pytest
from company.market.portfolio_position import (
    PositionDirection, CommodityType, EnergyPosition,
    PortfolioEnergyPosition, compute_energy_position
)


def test_compute_fully_hedged():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 10000.0)
    assert pos.hedge_ratio_pct == pytest.approx(100.0)
    assert pos.direction == PositionDirection.FLAT


def test_compute_short_position():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 8000.0)
    assert pos.hedge_ratio_pct == pytest.approx(80.0)
    assert pos.direction == PositionDirection.SHORT


def test_compute_long_position():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 11000.0)
    assert pos.direction == PositionDirection.LONG


def test_flat_within_tolerance():
    pos = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 52000.0)
    assert pos.direction == PositionDirection.FLAT


def test_is_within_policy_for_flat():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 10200.0)
    assert pos.is_within_policy


def test_net_position_short():
    pos = compute_energy_position(CommodityType.GAS, 2023, 100000.0, 80000.0)
    assert pos.net_position_mwh == pytest.approx(-20000.0)


def test_portfolio_fully_hedged():
    elec = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 10000.0)
    gas = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 50000.0)
    portfolio = PortfolioEnergyPosition(year=2023, electricity=elec, gas=gas)
    assert portfolio.is_fully_hedged


def test_portfolio_not_fully_hedged_if_one_short():
    elec = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 7000.0)
    gas = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 50000.0)
    portfolio = PortfolioEnergyPosition(year=2023, electricity=elec, gas=gas)
    assert not portfolio.is_fully_hedged


def test_portfolio_summary_keys():
    elec = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 9500.0)
    gas = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 48000.0)
    portfolio = PortfolioEnergyPosition(year=2023, electricity=elec, gas=gas)
    s = portfolio.summary()
    assert 'electricity_direction' in s
    assert 'gas_net_mwh' in s
    assert 'is_fully_hedged' in s


def test_net_position_long():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 11000.0)
    assert pos.net_position_mwh == pytest.approx(1000.0)


def test_direction_just_over_upper_tolerance():
    pos = compute_energy_position(CommodityType.GAS, 2023, 10000.0, 10501.0)
    assert pos.direction == PositionDirection.LONG


def test_direction_just_under_lower_tolerance():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 9499.0)
    assert pos.direction == PositionDirection.SHORT


def test_flat_exactly_at_lower_boundary():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 9500.0)
    assert pos.direction == PositionDirection.FLAT


def test_flat_exactly_at_upper_boundary():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 10500.0)
    assert pos.direction == PositionDirection.FLAT


def test_is_within_policy_false_for_short():
    pos = compute_energy_position(CommodityType.GAS, 2023, 100000.0, 70000.0)
    assert not pos.is_within_policy


def test_portfolio_summary_year():
    elec = compute_energy_position(CommodityType.ELECTRICITY, 2022, 10000.0, 10000.0)
    gas = compute_energy_position(CommodityType.GAS, 2022, 50000.0, 50000.0)
    portfolio = PortfolioEnergyPosition(year=2022, electricity=elec, gas=gas)
    assert portfolio.summary()['year'] == 2022


def test_compute_zero_forecast_ratio():
    pos = compute_energy_position(CommodityType.ELECTRICITY, 2023, 0.0, 5000.0)
    assert pos.hedge_ratio_pct == pytest.approx(0.0)
    assert pos.direction == PositionDirection.SHORT


def test_portfolio_not_fully_hedged_if_one_long():
    elec = compute_energy_position(CommodityType.ELECTRICITY, 2023, 10000.0, 11500.0)
    gas = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 50000.0)
    portfolio = PortfolioEnergyPosition(year=2023, electricity=elec, gas=gas)
    assert not portfolio.is_fully_hedged


def test_compute_stores_commodity():
    pos = compute_energy_position(CommodityType.GAS, 2023, 50000.0, 50000.0)
    assert pos.commodity == CommodityType.GAS
