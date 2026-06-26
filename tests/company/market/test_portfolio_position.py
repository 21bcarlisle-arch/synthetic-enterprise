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
