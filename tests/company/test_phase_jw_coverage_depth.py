"""Phase JW: Coverage Depth Sprint XLV -- 30 tests."""
import datetime as dt
import pytest
from company.market.hedging_schedule import (
    HedgeTenor, Commodity, ForwardContractDelivery, DeliveryMonthPosition, HedgingSchedule,
)


def test_hs_open_position_negative_when_over_hedged():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 500.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 700.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.open_position_mwh == -200.0


def test_hs_over_hedged_months_returns_multiple():
    s = HedgingSchedule()
    for m in [10, 11]:
        s.set_forecast(dt.date(2022, m, 1), Commodity.GAS, 300.0)
        s.add_contract(dt.date(2022, m, 1), Commodity.GAS, 400.0, 80.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert len(s.over_hedged_months(Commodity.GAS)) == 2


def test_hs_portfolio_hedge_ratio_gas():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 750.0, 80.0, HedgeTenor.QUARTER_AHEAD, dt.date(2022, 7, 1))
    assert s.portfolio_hedge_ratio(Commodity.GAS) == 75.0


def test_hs_schedule_summary_months_count():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    s.set_forecast(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 1200.0)
    assert s.schedule_summary(Commodity.ELECTRICITY)["months"] == 2


def test_hs_hedged_mwh_zero_when_no_contracts():
    s = HedgingSchedule()
    pos = s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 800.0)
    assert pos.hedged_mwh == 0.0


def test_hs_contract_value_rounds_to_2dp():
    c = ForwardContractDelivery("FWD-0001", Commodity.GAS, dt.date(2022, 11, 1), 333.0, 75.5, HedgeTenor.MONTH_AHEAD, dt.date(2022, 10, 1))
    assert abs(c.contract_value_gbp - 333.0 * 75.5) < 0.01


def test_hs_schedule_summary_over_hedged_count_two():
    s = HedgingSchedule()
    for m in [10, 11]:
        s.set_forecast(dt.date(2022, m, 1), Commodity.ELECTRICITY, 400.0)
        s.add_contract(dt.date(2022, m, 1), Commodity.ELECTRICITY, 500.0, 140.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert s.schedule_summary(Commodity.ELECTRICITY)["over_hedged_count"] == 2


def test_hs_avg_price_single_contract():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 500.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 500.0, 90.0, HedgeTenor.YEAR_AHEAD, dt.date(2022, 1, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.GAS)
    assert pos.avg_contracted_price == 90.0


def test_hs_portfolio_ratio_two_gas_months():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 1000.0)
    s.set_forecast(dt.date(2022, 11, 1), Commodity.GAS, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 600.0, 80.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    s.add_contract(dt.date(2022, 11, 1), Commodity.GAS, 400.0, 82.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert s.portfolio_hedge_ratio(Commodity.GAS) == 50.0


def test_hs_schedule_summary_total_hedged_across_months():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    s.set_forecast(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 700.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    s.add_contract(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 800.0, 155.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 10, 1))
    assert s.schedule_summary(Commodity.ELECTRICITY)["total_hedged_mwh"] == 1500.0
