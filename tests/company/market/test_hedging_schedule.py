import datetime as dt
import pytest
from company.market.hedging_schedule import (
    HedgeTenor, Commodity, ForwardContractDelivery, DeliveryMonthPosition, HedgingSchedule
)


def test_set_forecast_and_no_hedge():
    s = HedgingSchedule()
    pos = s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    assert pos.hedge_ratio_pct == pytest.approx(0.0)
    assert pos.open_position_mwh == pytest.approx(1000.0)


def test_add_contract_partial_hedge():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 600.0,
                   150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.hedge_ratio_pct == pytest.approx(60.0)
    assert pos.open_position_mwh == pytest.approx(400.0)


def test_over_hedged_detection():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 500.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 600.0,
                   150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.is_over_hedged
    assert len(s.over_hedged_months(Commodity.ELECTRICITY)) == 1


def test_contract_value():
    c = ForwardContractDelivery(
        'FWD-0001', Commodity.GAS, dt.date(2022, 11, 1),
        200.0, 80.0, HedgeTenor.QUARTER_AHEAD, dt.date(2022, 8, 1)
    )
    assert c.contract_value_gbp == pytest.approx(16_000.0)


def test_avg_contracted_price():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 2000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0,
                   100.0, HedgeTenor.YEAR_AHEAD, dt.date(2022, 1, 1))
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0,
                   200.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.avg_contracted_price == pytest.approx(150.0)


def test_missing_forecast_raises():
    s = HedgingSchedule()
    with pytest.raises(KeyError):
        s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 100.0,
                       80.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))


def test_portfolio_hedge_ratio():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    s.set_forecast(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 800.0,
                   150.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    s.add_contract(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 600.0,
                   150.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert s.portfolio_hedge_ratio(Commodity.ELECTRICITY) == pytest.approx(70.0)


def test_schedule_summary():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 500.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 400.0,
                   75.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    summary = s.schedule_summary(Commodity.GAS)
    assert summary['total_forecast_mwh'] == pytest.approx(500.0)
    assert summary['portfolio_hedge_ratio_pct'] == pytest.approx(80.0)
    assert 'over_hedged_count' in summary
