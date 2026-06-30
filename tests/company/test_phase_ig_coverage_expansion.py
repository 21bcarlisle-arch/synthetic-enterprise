"""Phase IG: deeper coverage for switch_analytics, trade_finance, hedging_schedule."""
import datetime as dt
import pytest

# ===== switch_analytics =====
from company.crm.switch_analytics import (
    SwitchAnalytics, SwitchDirection, SwitchStatus
)

def _sa():
    sa = SwitchAnalytics("OurCo")
    e1 = sa.record("M001","C1",SwitchDirection.GAIN,"Old Supplier","OurCo",dt.date(2022,1,10))
    e2 = sa.record("M002","C2",SwitchDirection.GAIN,"Old Supplier","OurCo",dt.date(2022,2,1))
    e3 = sa.record("M003","C3",SwitchDirection.LOSS,"OurCo","Octopus",dt.date(2022,3,1))
    sa.complete(e1.event_id,dt.date(2022,1,20))
    sa.complete(e2.event_id,dt.date(2022,2,8))
    sa.mark_erroneous(e3.event_id)
    return sa

class TestSwitchAnalyticsExpanded:
    def test_event_id_format(self):
        sa = _sa()
        assert sa._events[0].event_id == "SW-00001"

    def test_complete_sets_status(self):
        sa = _sa()
        assert sa._events[0].is_completed

    def test_days_to_complete(self):
        sa = _sa()
        assert sa._events[0].days_to_complete == 10

    def test_erroneous_sets_flag(self):
        sa = _sa()
        assert sa._events[2].erroneous_transfer
        assert sa._events[2].status == SwitchStatus.ERRONEOUS

    def test_gains_in_year(self):
        sa = _sa()
        assert len(sa.gains_in_year(2022)) == 2

    def test_losses_in_year(self):
        sa = _sa()
        assert len(sa.losses_in_year(2022)) == 1

    def test_net_customer_change(self):
        sa = _sa()
        assert sa.net_customer_change(2022) == 1

    def test_erroneous_transfers(self):
        sa = _sa()
        ets = sa.erroneous_transfers_in_year(2022)
        assert len(ets) == 1

    def test_avg_days_to_complete(self):
        sa = _sa()
        # e1 = 10 days, e2 = 7 days
        avg = sa.avg_days_to_complete(2022)
        assert avg == pytest.approx(8.5)

    def test_annual_summary_keys(self):
        sa = _sa()
        s = sa.annual_summary(2022)
        assert "gains" in s and "net" in s and s["gains"] == 2


# ===== trade_finance =====
from company.finance.trade_finance import (
    TradeFinanceLedger, InstrumentType, InstrumentStatus
)

def _tfl():
    ledger = TradeFinanceLedger()
    ledger.register("I001","C1",InstrumentType.LETTER_OF_CREDIT,"HSBC",
                    500_000.0,dt.date(2022,1,1),dt.date(2023,1,1))
    ledger.register("I002","C1",InstrumentType.BANK_GUARANTEE,"Barclays",
                    250_000.0,dt.date(2022,1,1),dt.date(2022,12,15))
    ledger.register("I003","C2",InstrumentType.CASH_DEPOSIT,"N/A",
                    100_000.0,dt.date(2022,1,1),dt.date(2023,6,1))
    return ledger

class TestTradeFinanceLedgerExpanded:
    def test_register_creates_instrument(self):
        ledger = _tfl()
        i = ledger.get("I001")
        assert i is not None and i.face_value_gbp == 500_000.0

    def test_days_to_expiry(self):
        ledger = _tfl()
        i = ledger.get("I001")
        assert i.days_to_expiry(dt.date(2022,12,1)) == 31

    def test_refresh_status_active(self):
        ledger = _tfl()
        i = ledger.get("I001")
        i.refresh_status(dt.date(2022,6,1))
        assert i.status == InstrumentStatus.ACTIVE

    def test_refresh_status_expiring_soon(self):
        ledger = _tfl()
        i = ledger.get("I002")
        i.refresh_status(dt.date(2022,11,20))  # 25 days to 2022-12-15
        assert i.status == InstrumentStatus.EXPIRING_SOON

    def test_refresh_status_expired(self):
        ledger = _tfl()
        i = ledger.get("I002")
        i.refresh_status(dt.date(2023,1,1))
        assert i.status == InstrumentStatus.EXPIRED

    def test_call_instrument(self):
        ledger = _tfl()
        ledger.call_instrument("I001",dt.date(2022,9,1),200_000.0)
        i = ledger.get("I001")
        assert i.status == InstrumentStatus.CALLED
        assert i.call_amount_gbp == 200_000.0

    def test_total_credit_support_excludes_called(self):
        ledger = _tfl()
        ledger.call_instrument("I001",dt.date(2022,9,1),200_000.0)
        total = ledger.total_credit_support_gbp("C1",dt.date(2022,9,15))
        # I001 CALLED, I002 ACTIVE -> only 250k
        assert total == pytest.approx(250_000.0)

    def test_expiring_within_30_days(self):
        ledger = _tfl()
        exp = ledger.expiring_within(dt.date(2022,11,20),30)
        assert any(i.instrument_id == "I002" for i in exp)

    def test_instruments_by_type(self):
        ledger = _tfl()
        by_type = ledger.instruments_by_type(dt.date(2022,6,1))
        assert "letter_of_credit" in by_type and by_type["letter_of_credit"] == 500_000.0

    def test_portfolio_summary_keys(self):
        ledger = _tfl()
        s = ledger.portfolio_summary(dt.date(2022,6,1))
        assert "total_instruments" in s and "total_coverage_gbp" in s


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
