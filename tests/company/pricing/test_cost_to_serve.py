import pytest
from company.pricing.cost_to_serve import (
    CostToServeCalculator, CostToServeBreakdown, CustomerSegment
)


def _bd(aid="C1", year=2022, seg=CustomerSegment.RESIDENTIAL_CREDIT, mwh=3.5,
        wholesale=15.0, cm=0.5, cfd=0.3, ro=0.8, fit=0.2,
        duos=2.35, tnuos=1.05, bsuos=6.85, bad_debt=5.0, smart=8.0):
    return CostToServeBreakdown(
        account_id=aid, year=year, segment=seg, consumption_mwh=mwh,
        wholesale_cost_p_per_kwh=wholesale,
        cm_p_per_kwh=cm, cfd_p_per_kwh=cfd, ro_p_per_kwh=ro, fit_p_per_kwh=fit,
        duos_p_per_kwh=duos, tnuos_p_per_kwh=tnuos, bsuos_p_per_kwh=bsuos,
        bad_debt_provision_gbp=bad_debt, smart_meter_cost_gbp=smart,
    )


def test_levy_p_per_kwh():
    b = _bd(cm=0.5, cfd=0.3, ro=0.8, fit=0.2, duos=2.35, tnuos=1.05, bsuos=6.85)
    expected = 0.5 + 0.3 + 0.8 + 0.2 + 2.35 + 1.05 + 6.85
    assert abs(b.levy_p_per_kwh - expected) < 0.001


def test_total_commodity_and_levy():
    b = _bd(wholesale=15.0, cm=0.5, cfd=0.0, ro=0.0, fit=0.0,
            duos=0.0, tnuos=0.0, bsuos=0.0)
    assert abs(b.total_commodity_and_levy_p_per_kwh - 15.5) < 0.001


def test_operating_cost_gbp():
    b = _bd(seg=CustomerSegment.RESIDENTIAL_CREDIT, bad_debt=5.0, smart=8.0)
    # support=18 + billing=8 + bad_debt=5 + smart=8
    assert abs(b.operating_cost_gbp - 39.0) < 0.01


def test_operating_cost_p_per_kwh():
    b = _bd(mwh=3.5, seg=CustomerSegment.RESIDENTIAL_CREDIT, bad_debt=0.0, smart=0.0)
    # support=18 + billing=8 = 26 gbp / 3500 kwh * 100 = 0.7429 p/kwh
    expected = 26.0 / 3500.0 * 100
    assert abs(b.operating_cost_p_per_kwh - expected) < 0.01


def test_levy_pct_of_total_positive():
    b = _bd()
    assert b.levy_pct_of_total > 0.0
    assert b.levy_pct_of_total < 100.0


def test_acquisition_cost_residential():
    cost = CostToServeCalculator.acquisition_cost_gbp(CustomerSegment.RESIDENTIAL_CREDIT)
    assert abs(cost - 60.0) < 0.01


def test_acquisition_cost_ic_much_higher():
    res = CostToServeCalculator.acquisition_cost_gbp(CustomerSegment.RESIDENTIAL_CREDIT)
    ic = CostToServeCalculator.acquisition_cost_gbp(CustomerSegment.IC)
    assert ic > res * 10


def test_record_and_filter_by_account():
    calc = CostToServeCalculator()
    calc.record(_bd(aid="C1"))
    calc.record(_bd(aid="C2"))
    assert len(calc.breakdown_for_account("C1")) == 1


def test_mean_total_cost():
    calc = CostToServeCalculator()
    b = _bd(wholesale=15.0, cm=0.0, cfd=0.0, ro=0.0, fit=0.0,
            duos=0.0, tnuos=0.0, bsuos=0.0, bad_debt=0.0, smart=0.0,
            mwh=10.0, seg=CustomerSegment.SME)
    calc.record(b)
    mean = calc.mean_total_cost_p_per_kwh()
    # total = wholesale + support(55) + billing(22) / (10000 kwh) * 100
    ops_p = (55.0 + 22.0) / 10_000.0 * 100
    assert abs(mean - (15.0 + ops_p)) < 0.01


def test_cts_summary_keys():
    calc = CostToServeCalculator()
    calc.record(_bd())
    s = calc.cts_summary(2022)
    for k in ("accounts_analysed", "mean_total_cost_p_per_kwh", "mean_levy_pct"):
        assert k in s
