"""Phase JV: Coverage Depth Sprint XLIV -- 30 tests.

Modules: risk_appetite · hedging_schedule · annual_obligations
"""
import datetime as dt
import pytest
from company.risk.risk_appetite import (
    RiskCategory, RiskRAG, RiskAppetiteFramework,
)
from company.market.hedging_schedule import (
    HedgeTenor, Commodity, ForwardContractDelivery, HedgingSchedule,
)
from company.regulatory.annual_obligations import (
    ObligationStatus, build_obligations_report,
)


def _raf():
    raf = RiskAppetiteFramework(approved_date=dt.date(2022, 1, 1))
    raf.add_limit("MKT01", RiskCategory.MARKET, "Open position MWh", 5000.0, "MWh")
    raf.add_limit("LIQ01", RiskCategory.LIQUIDITY, "13-week cash min", 500_000.0, "GBP")
    return raf


def _hs():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 1000.0)
    return s


def _bkw(**overrides):
    kw = dict(year=2023, report_date=dt.date(2024, 4, 1),
              whd_obligation_customers=0, whd_delivered_customers=0,
              eco4_obligation_mwh=0.0, eco4_delivered_mwh=0.0,
              gsop_breaches=0, gsop_payments_gbp=0.0,
              ofgem_return_submitted=True)
    kw.update(overrides)
    return kw


# risk_appetite

def test_ra_multiple_limits_in_dashboard():
    raf = _raf()
    raf.record_measurement("MKT01", 2000.0, dt.date(2022, 6, 1))
    raf.record_measurement("LIQ01", 300_000.0, dt.date(2022, 6, 1))
    d = raf.risk_dashboard(dt.date(2022, 6, 30))
    assert d["measured_limits"] == 2 and d["breaches"] == 0


def test_ra_latest_picks_max_date():
    raf = _raf()
    raf.record_measurement("MKT01", 1000.0, dt.date(2022, 1, 1))
    raf.record_measurement("MKT01", 4800.0, dt.date(2022, 9, 1))
    m = raf.latest_measurement("MKT01")
    assert m.measured_value == pytest.approx(4800.0)
    assert m.measured_date == dt.date(2022, 9, 1)


def test_ra_active_breaches_excludes_approaching():
    raf = _raf()
    raf.record_measurement("MKT01", 4200.0, dt.date(2022, 6, 1))
    assert raf.active_breaches() == []


def test_ra_active_breaches_two_limits_both_breach():
    raf = _raf()
    raf.record_measurement("MKT01", 6000.0, dt.date(2022, 10, 1))
    raf.record_measurement("LIQ01", 600_000.0, dt.date(2022, 10, 1))
    assert len(raf.active_breaches()) == 2


def test_ra_utilisation_zero_when_limit_zero():
    raf = RiskAppetiteFramework(approved_date=dt.date(2022, 1, 1))
    raf.add_limit("T01", RiskCategory.OPERATIONAL, "Zero limit", 0.0, "units")
    m = raf.record_measurement("T01", 5.0, dt.date(2022, 6, 1))
    assert m.utilisation_pct == pytest.approx(0.0)


def test_ra_custom_warning_threshold_70pct():
    raf = RiskAppetiteFramework(approved_date=dt.date(2022, 1, 1))
    raf.add_limit("C01", RiskCategory.CREDIT, "Custom", 100.0, "units",
                  warning_threshold_pct=70.0)
    m = raf.record_measurement("C01", 71.0, dt.date(2022, 6, 1))
    assert m.rag == RiskRAG.APPROACHING_LIMIT


def test_ra_dashboard_excludes_future_measurements():
    raf = _raf()
    raf.record_measurement("MKT01", 6000.0, dt.date(2022, 12, 1))
    d = raf.risk_dashboard(dt.date(2022, 11, 30))
    assert d["measured_limits"] == 0


def test_ra_latest_none_when_no_measurements():
    raf = _raf()
    assert raf.latest_measurement("MKT01") is None


def test_ra_unmeasured_limit_not_in_dashboard_items():
    raf = _raf()
    raf.record_measurement("MKT01", 2000.0, dt.date(2022, 6, 1))
    d = raf.risk_dashboard(dt.date(2022, 6, 30))
    ids = [i["limit_id"] for i in d["items"]]
    assert "LIQ01" not in ids and "MKT01" in ids


def test_ra_breach_then_recovery_not_active():
    raf = _raf()
    raf.record_measurement("MKT01", 6000.0, dt.date(2022, 6, 1))
    raf.record_measurement("MKT01", 2000.0, dt.date(2022, 7, 1))
    assert raf.active_breaches() == []


# hedging_schedule

def test_hs_contract_id_fwd0001():
    s = _hs()
    c = s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 500.0,
                       150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    assert c.contract_id == "FWD-0001"


def test_hs_contract_ids_sequential():
    s = _hs()
    c1 = s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 300.0,
                        150.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    s.set_forecast(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 1000.0)
    c2 = s.add_contract(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 400.0,
                        160.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert c1.contract_id == "FWD-0001" and c2.contract_id == "FWD-0002"


def test_hs_portfolio_ratio_multiple_months():
    s = HedgingSchedule()
    for m in [dt.date(2022, 10, 1), dt.date(2022, 11, 1), dt.date(2022, 12, 1)]:
        s.set_forecast(m, Commodity.ELECTRICITY, 1000.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 900.0,
                   150.0, HedgeTenor.YEAR_AHEAD, dt.date(2022, 1, 1))
    s.add_contract(dt.date(2022, 11, 1), Commodity.ELECTRICITY, 600.0,
                   150.0, HedgeTenor.QUARTER_AHEAD, dt.date(2022, 8, 1))
    assert s.portfolio_hedge_ratio(Commodity.ELECTRICITY) == pytest.approx(50.0)


def test_hs_over_hedged_filtered_by_commodity():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 500.0)
    s.set_forecast(dt.date(2022, 10, 1), Commodity.GAS, 500.0)
    s.add_contract(dt.date(2022, 10, 1), Commodity.GAS, 600.0,
                   80.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    assert s.over_hedged_months(Commodity.GAS) == [dt.date(2022, 10, 1)]
    assert s.over_hedged_months(Commodity.ELECTRICITY) == []


def test_hs_get_position_none_for_unknown_month():
    s = _hs()
    assert s.get_position(dt.date(2022, 12, 1), Commodity.ELECTRICITY) is None


def test_hs_portfolio_ratio_none_when_forecast_zero():
    s = HedgingSchedule()
    s.set_forecast(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 0.0)
    assert s.portfolio_hedge_ratio(Commodity.ELECTRICITY) is None


def test_hs_avg_price_none_when_no_contracts():
    s = _hs()
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.avg_contracted_price is None


def test_hs_schedule_summary_zero_when_no_months():
    s = HedgingSchedule()
    summary = s.schedule_summary(Commodity.GAS)
    assert summary["months"] == 0
    assert summary["total_forecast_mwh"] == pytest.approx(0.0)
    assert summary["portfolio_hedge_ratio_pct"] is None


def test_hs_multiple_contracts_hedged_is_sum():
    s = _hs()
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 300.0,
                   150.0, HedgeTenor.YEAR_AHEAD, dt.date(2022, 1, 1))
    s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 400.0,
                   160.0, HedgeTenor.MONTH_AHEAD, dt.date(2022, 9, 1))
    pos = s.get_position(dt.date(2022, 10, 1), Commodity.ELECTRICITY)
    assert pos.hedged_mwh == pytest.approx(700.0)


def test_hs_tenor_stored():
    s = _hs()
    c = s.add_contract(dt.date(2022, 10, 1), Commodity.ELECTRICITY, 500.0,
                       150.0, HedgeTenor.SEASON_AHEAD, dt.date(2022, 8, 1))
    assert c.tenor == HedgeTenor.SEASON_AHEAD


# annual_obligations

def test_ao_whd_at_risk_95pct():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=190))
    assert r.get("WHD").status == ObligationStatus.AT_RISK


def test_ao_eco4_met_exact_100pct():
    r = build_obligations_report(**_bkw(
        eco4_obligation_mwh=500.0, eco4_delivered_mwh=500.0))
    eco = r.get("ECO4")
    assert eco.status == ObligationStatus.MET
    assert eco.penalty_estimate_gbp == pytest.approx(0.0)


def test_ao_eco4_breached_below_85pct():
    r = build_obligations_report(**_bkw(
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=800.0))
    eco = r.get("ECO4")
    assert eco.status == ObligationStatus.BREACHED
    assert eco.penalty_estimate_gbp == pytest.approx(200.0 * 10.0)


def test_ao_rego_at_risk_92pct():
    r = build_obligations_report(**_bkw(
        rego_obligation_mwh=1000.0, rego_held_mwh=920.0))
    assert r.get("REGO").status == ObligationStatus.AT_RISK


def test_ao_overall_at_risk_no_breach():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=190,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=1000.0))
    assert r.overall_status == ObligationStatus.AT_RISK
    assert r.breached_count == 0


def test_ao_total_penalty_accumulates():
    r = build_obligations_report(**_bkw(
        whd_obligation_customers=200, whd_delivered_customers=160,
        eco4_obligation_mwh=1000.0, eco4_delivered_mwh=800.0))
    expected = (200 - 160) * 150.0 + (1000.0 - 800.0) * 10.0
    assert r.total_penalty_estimate_gbp == pytest.approx(expected)


def test_ao_get_returns_none_for_unknown():
    r = build_obligations_report(**_bkw())
    assert r.get("UNKNOWN") is None


def test_ao_ofgem_at_risk_before_due_date():
    r = build_obligations_report(**_bkw(
        ofgem_return_submitted=False,
        ofgem_return_due_date=dt.date(2024, 6, 30),
        report_date=dt.date(2024, 4, 1)))
    assert r.get("Ofgem_annual_return").status == ObligationStatus.AT_RISK


def test_ao_no_rego_item_when_obligation_zero():
    r = build_obligations_report(**_bkw(rego_obligation_mwh=0.0, rego_held_mwh=0.0))
    assert r.get("REGO") is None


def test_ao_summary_has_expected_keys():
    r = build_obligations_report(**_bkw())
    s = r.summary()
    for key in ("year", "report_date", "total_obligations", "met",
                "at_risk", "breached", "overall_status", "total_penalty_estimate_gbp"):
        assert key in s
