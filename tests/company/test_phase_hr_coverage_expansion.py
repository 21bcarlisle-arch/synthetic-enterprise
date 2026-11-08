"""Phase HR: coverage expansion for annual_obligations, switch_analytics, trade_finance, hedging_schedule."""
import datetime as dt
import pytest


# ===== hedging_schedule =====
from company.market.hedging_schedule import (
    HedgeTenor, Commodity, ForwardContractDelivery, DeliveryMonthPosition, HedgingSchedule
)

class TestHedgingScheduleExpanded:
    def _hs(self):
        hs = HedgingSchedule()
        hs.set_forecast(dt.date(2022,6,1), Commodity.ELECTRICITY, 1000.0)
        return hs

    def test_set_forecast_returns_position(self):
        hs = HedgingSchedule()
        pos = hs.set_forecast(dt.date(2022,6,1), Commodity.ELECTRICITY, 500.0)
        assert pos.forecast_mwh == 500.0
        assert pos.hedged_mwh == 0.0

    def test_add_contract_increases_hedged(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 400.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        pos = hs.get_position(dt.date(2022,6,1), Commodity.ELECTRICITY)
        assert pos.hedged_mwh == pytest.approx(400.0)

    def test_open_position(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 600.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        pos = hs.get_position(dt.date(2022,6,1), Commodity.ELECTRICITY)
        assert pos.open_position_mwh == pytest.approx(400.0)

    def test_hedge_ratio_pct(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 700.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        pos = hs.get_position(dt.date(2022,6,1), Commodity.ELECTRICITY)
        assert pos.hedge_ratio_pct == pytest.approx(70.0)

    def test_is_over_hedged(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 1100.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        pos = hs.get_position(dt.date(2022,6,1), Commodity.ELECTRICITY)
        assert pos.is_over_hedged

    def test_avg_contracted_price(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 400.0, 140.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 400.0, 160.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        pos = hs.get_position(dt.date(2022,6,1), Commodity.ELECTRICITY)
        assert pos.avg_contracted_price == pytest.approx(150.0)

    def test_portfolio_hedge_ratio(self):
        hs = HedgingSchedule()
        hs.set_forecast(dt.date(2022,6,1), Commodity.ELECTRICITY, 1000.0)
        hs.set_forecast(dt.date(2022,7,1), Commodity.ELECTRICITY, 1000.0)
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 800.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        hs.add_contract(dt.date(2022,7,1), Commodity.ELECTRICITY, 600.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        assert hs.portfolio_hedge_ratio(Commodity.ELECTRICITY) == pytest.approx(70.0)

    def test_over_hedged_months(self):
        hs = self._hs()
        hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 1200.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))
        assert dt.date(2022,6,1) in hs.over_hedged_months(Commodity.ELECTRICITY)

    def test_get_position_returns_none_for_unknown(self):
        hs = HedgingSchedule()
        assert hs.get_position(dt.date(2022,6,1), Commodity.GAS) is None

    def test_add_contract_no_forecast_raises(self):
        hs = HedgingSchedule()
        with pytest.raises(KeyError):
            hs.add_contract(dt.date(2022,6,1), Commodity.ELECTRICITY, 100.0, 150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022,5,1))

    def test_schedule_summary_keys(self):
        hs = self._hs()
        s = hs.schedule_summary(Commodity.ELECTRICITY)
        assert "total_forecast_mwh" in s and "portfolio_hedge_ratio_pct" in s
