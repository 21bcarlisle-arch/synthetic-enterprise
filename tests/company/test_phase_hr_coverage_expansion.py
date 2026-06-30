"""Phase HR: coverage expansion for annual_obligations, switch_analytics, trade_finance, hedging_schedule."""
import datetime as dt
import pytest

# ===== annual_obligations =====
from company.regulatory.annual_obligations import (
    ObligationStatus, ObligationLineItem, AnnualObligationsReport,
    build_obligations_report
)

def _report(whd_obl=100, whd_del=100, eco4_obl=500, eco4_del=500,
            gsop_breaches=0, gsop_payments=0.0, submitted=True, rego_obl=0, rego_del=0):
    return build_obligations_report(
        year=2023, report_date=dt.date(2023,3,31),
        whd_obligation_customers=whd_obl, whd_delivered_customers=whd_del,
        eco4_obligation_mwh=eco4_obl, eco4_delivered_mwh=eco4_del,
        gsop_breaches=gsop_breaches, gsop_payments_gbp=gsop_payments,
        ofgem_return_submitted=submitted, rego_obligation_mwh=rego_obl, rego_held_mwh=rego_del,
    )

class TestAnnualObligationsExpanded:
    def test_all_met_overall_status(self):
        r = _report()
        assert r.overall_status == ObligationStatus.MET
        assert r.met_count >= 3

    def test_whd_breach_when_under_90pct(self):
        r = _report(whd_obl=100, whd_del=80)
        whd = r.get("WHD")
        assert whd.status == ObligationStatus.BREACHED
        assert whd.penalty_estimate_gbp == pytest.approx(3000.0)

    def test_whd_at_risk_90_to_100(self):
        r = _report(whd_obl=100, whd_del=95)
        whd = r.get("WHD")
        assert whd.status == ObligationStatus.AT_RISK

    def test_eco4_breach_below_85pct(self):
        r = _report(eco4_obl=500, eco4_del=400)
        eco = r.get("ECO4")
        assert eco.status == ObligationStatus.BREACHED
        assert eco.penalty_estimate_gbp == pytest.approx(1000.0)

    def test_gsop_breach_when_breaches_nonzero(self):
        r = _report(gsop_breaches=3, gsop_payments=450.0)
        gsop = r.get("GSOP")
        assert gsop.status == ObligationStatus.BREACHED
        assert gsop.penalty_estimate_gbp == pytest.approx(450.0)

    def test_ofgem_return_at_risk_when_not_submitted(self):
        r = _report(submitted=False)
        ret = r.get("Ofgem_annual_return")
        assert ret.status in (ObligationStatus.AT_RISK, ObligationStatus.BREACHED)

    def test_rego_included_when_obligation(self):
        r = _report(rego_obl=1000, rego_del=1000)
        assert r.get("REGO") is not None
        assert r.get("REGO").status == ObligationStatus.MET

    def test_rego_breach_below_90pct(self):
        r = _report(rego_obl=1000, rego_del=800)
        rego = r.get("REGO")
        assert rego.status == ObligationStatus.BREACHED
        assert rego.penalty_estimate_gbp == pytest.approx(10000.0)

    def test_total_penalty_sum(self):
        r = _report(whd_obl=100, whd_del=80, gsop_breaches=1, gsop_payments=100.0)
        assert r.total_penalty_estimate_gbp >= 3100.0

    def test_summary_keys_and_values(self):
        r = _report()
        s = r.summary()
        assert s["year"] == 2023
        assert "overall_status" in s and "total_penalty_estimate_gbp" in s

    def test_delivery_pct_calculated(self):
        item = ObligationLineItem("WHD", 100, 90, "customers", ObligationStatus.AT_RISK)
        assert item.delivery_pct == pytest.approx(90.0)
        assert item.shortfall == pytest.approx(10.0)


# ===== switch_analytics =====
from company.crm.switch_analytics import (
    SwitchDirection, SwitchStatus, SwitchEvent, SwitchAnalytics
)

class TestSwitchAnalyticsExpanded:
    def _sa(self):
        return SwitchAnalytics(our_supplier_id="US01")

    def _gain(self, sa, year=2022):
        return sa.record("M1","C1",SwitchDirection.GAIN,"OLD","US01",dt.date(year,3,1))

    def _loss(self, sa, year=2022):
        return sa.record("M2","C2",SwitchDirection.LOSS,"US01","NEW",dt.date(year,4,1))

    def test_event_id_format(self):
        sa = self._sa()
        ev = self._gain(sa)
        assert ev.event_id.startswith("SW-")

    def test_gains_in_year(self):
        sa = self._sa()
        self._gain(sa, 2022)
        self._gain(sa, 2021)
        assert len(sa.gains_in_year(2022)) == 1

    def test_losses_in_year(self):
        sa = self._sa()
        self._loss(sa, 2022)
        assert len(sa.losses_in_year(2022)) == 1

    def test_net_customer_change(self):
        sa = self._sa()
        self._gain(sa)
        self._gain(sa)
        self._loss(sa)
        assert sa.net_customer_change(2022) == 1

    def test_complete_updates_status(self):
        sa = self._sa()
        ev = self._gain(sa)
        done = sa.complete(ev.event_id, dt.date(2022,3,6))
        assert done.status == SwitchStatus.COMPLETED
        assert done.days_to_complete == 5

    def test_mark_erroneous(self):
        sa = self._sa()
        ev = self._gain(sa)
        et = sa.mark_erroneous(ev.event_id)
        assert et.erroneous_transfer
        assert len(sa.erroneous_transfers_in_year(2022)) == 1

    def test_object_switch(self):
        sa = self._sa()
        ev = self._gain(sa)
        objected = sa.object(ev.event_id)
        assert objected.status == SwitchStatus.OBJECTED

    def test_avg_days_to_complete_none_no_completions(self):
        sa = self._sa()
        self._gain(sa)
        assert sa.avg_days_to_complete(2022) is None

    def test_avg_days_to_complete_calculated(self):
        sa = self._sa()
        e1 = self._gain(sa)
        e2 = self._gain(sa)
        sa.complete(e1.event_id, dt.date(2022,3,8))
        sa.complete(e2.event_id, dt.date(2022,3,11))
        avg = sa.avg_days_to_complete(2022)
        assert avg == pytest.approx(8.5, abs=0.1)

    def test_annual_summary_keys(self):
        sa = self._sa()
        self._gain(sa)
        s = sa.annual_summary(2022)
        assert "gains" in s and "losses" in s and "net" in s


# ===== trade_finance =====
from company.finance.trade_finance import (
    InstrumentType, InstrumentStatus, CreditInstrument, TradeFinanceLedger
)

class TestTradeFinanceExpanded:
    def _ledger(self):
        return TradeFinanceLedger()

    def _register(self, ledger, expiry=dt.date(2023,12,31)):
        return ledger.register(
            "INS-001","C1",InstrumentType.LETTER_OF_CREDIT,"BankA",
            50_000.0, dt.date(2022,1,1), expiry
        )

    def test_register_returns_instrument(self):
        l = self._ledger()
        inst = self._register(l)
        assert inst.instrument_id == "INS-001"
        assert inst.status == InstrumentStatus.ACTIVE

    def test_days_to_expiry(self):
        l = self._ledger()
        inst = self._register(l, expiry=dt.date(2023,12,31))
        as_of = dt.date(2023,12,1)
        assert inst.days_to_expiry(as_of) == 30

    def test_refresh_status_expiring_soon(self):
        l = self._ledger()
        inst = self._register(l, expiry=dt.date(2023,12,31))
        inst.refresh_status(dt.date(2023,12,20))
        assert inst.status == InstrumentStatus.EXPIRING_SOON

    def test_refresh_status_expired(self):
        l = self._ledger()
        inst = self._register(l, expiry=dt.date(2022,6,1))
        inst.refresh_status(dt.date(2023,1,1))
        assert inst.status == InstrumentStatus.EXPIRED

    def test_call_instrument(self):
        l = self._ledger()
        self._register(l)
        l.call_instrument("INS-001", dt.date(2022,6,1), 30_000.0)
        inst = l.get("INS-001")
        assert inst.status == InstrumentStatus.CALLED
        assert inst.call_amount_gbp == pytest.approx(30_000.0)

    def test_total_credit_support_active_only(self):
        l = self._ledger()
        self._register(l, expiry=dt.date(2025,1,1))
        l.register("INS-002","C1",InstrumentType.BANK_GUARANTEE,"BankB",
                   20_000.0,dt.date(2022,1,1),dt.date(2023,1,1))
        as_of = dt.date(2022,6,1)
        support = l.total_credit_support_gbp("C1", as_of)
        assert support == pytest.approx(70_000.0)

    def test_expiring_within(self):
        l = self._ledger()
        self._register(l, expiry=dt.date(2022,7,1))
        as_of = dt.date(2022,6,15)
        expiring = l.expiring_within(as_of, 30)
        assert len(expiring) == 1

    def test_instruments_by_type(self):
        l = self._ledger()
        self._register(l)
        bt = l.instruments_by_type(dt.date(2022,6,1))
        assert "letter_of_credit" in bt
        assert bt["letter_of_credit"] == pytest.approx(50_000.0)

    def test_portfolio_summary_keys(self):
        l = self._ledger()
        self._register(l)
        s = l.portfolio_summary(dt.date(2022,6,1))
        assert "total_instruments" in s and "active_count" in s

    def test_get_returns_none_for_unknown(self):
        l = self._ledger()
        assert l.get("MISSING") is None


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
