"""Phase IG: deeper coverage for switch_analytics, trade_finance, hedging_schedule."""
import datetime as dt
import pytest


# ===== hedging_schedule =====
from company.market.hedging_schedule import (
    HedgingSchedule, Commodity, HedgeTenor
)

_JAN = dt.date(2023,1,1)
_FEB = dt.date(2023,2,1)

def _hs():
    hs = HedgingSchedule()
    hs.set_forecast(_JAN,Commodity.ELECTRICITY,1000.0)
    hs.set_forecast(_FEB,Commodity.ELECTRICITY,800.0)
    hs.add_contract(_JAN,Commodity.ELECTRICITY,600.0,85.0,HedgeTenor.MONTH_AHEAD,dt.date(2022,12,1))
    hs.add_contract(_JAN,Commodity.ELECTRICITY,200.0,90.0,HedgeTenor.MONTH_AHEAD,dt.date(2022,12,15))
    hs.add_contract(_FEB,Commodity.ELECTRICITY,900.0,88.0,HedgeTenor.MONTH_AHEAD,dt.date(2022,12,1))
    return hs

class TestHedgingScheduleExpanded:
    def test_hedged_mwh(self):
        hs = _hs()
        pos = hs.get_position(_JAN,Commodity.ELECTRICITY)
        assert pos.hedged_mwh == pytest.approx(800.0)

    def test_open_position_mwh(self):
        hs = _hs()
        pos = hs.get_position(_JAN,Commodity.ELECTRICITY)
        assert pos.open_position_mwh == pytest.approx(200.0)

    def test_hedge_ratio_pct(self):
        hs = _hs()
        pos = hs.get_position(_JAN,Commodity.ELECTRICITY)
        assert pos.hedge_ratio_pct == pytest.approx(80.0)

    def test_not_over_hedged_jan(self):
        hs = _hs()
        pos = hs.get_position(_JAN,Commodity.ELECTRICITY)
        assert not pos.is_over_hedged

    def test_is_over_hedged_feb(self):
        hs = _hs()
        pos = hs.get_position(_FEB,Commodity.ELECTRICITY)
        assert pos.is_over_hedged  # 900 hedged vs 800 forecast

    def test_avg_contracted_price_volume_weighted(self):
        hs = _hs()
        pos = hs.get_position(_JAN,Commodity.ELECTRICITY)
        expected = (600*85 + 200*90) / 800
        assert pos.avg_contracted_price == pytest.approx(expected, rel=0.01)

    def test_add_contract_raises_when_no_forecast(self):
        hs = _hs()
        with pytest.raises(KeyError):
            hs.add_contract(dt.date(2023,3,1),Commodity.ELECTRICITY,100.0,85.0,
                           HedgeTenor.MONTH_AHEAD,dt.date(2022,12,1))

    def test_over_hedged_months(self):
        hs = _hs()
        over = hs.over_hedged_months(Commodity.ELECTRICITY)
        assert _FEB in over and _JAN not in over

    def test_portfolio_hedge_ratio(self):
        hs = _hs()
        ratio = hs.portfolio_hedge_ratio(Commodity.ELECTRICITY)
        # total hedged = 800+900=1700; total forecast = 1000+800=1800
        assert ratio == pytest.approx(1700/1800*100, rel=0.01)

    def test_schedule_summary_keys(self):
        hs = _hs()
        s = hs.schedule_summary(Commodity.ELECTRICITY)
        assert "months" in s and "portfolio_hedge_ratio_pct" in s
