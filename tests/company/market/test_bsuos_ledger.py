import pytest
from company.market.bsuos_ledger import BSUoSLedger, BSUoSCharge


def _charge(aid="C1", period="2022-09", mwh=100.0, rate=6.85):
    return BSUoSCharge(account_id=aid, charge_period=period,
                       consumption_mwh=mwh, rate_gbp_per_mwh=rate)


def test_charge_gbp():
    c = _charge(mwh=100.0, rate=6.85)
    assert abs(c.charge_gbp - 685.0) < 0.01


def test_is_crisis_period_2022():
    c = _charge(period="2022-09")
    assert c.is_crisis_period is True


def test_is_crisis_period_2021():
    c = _charge(period="2021-12")
    assert c.is_crisis_period is True


def test_not_crisis_period():
    c = _charge(period="2019-06")
    assert c.is_crisis_period is False


def test_rate_for_year():
    assert abs(BSUoSLedger.rate_for_year(2022) - 6.85) < 0.001
    assert abs(BSUoSLedger.rate_for_year(2016) - 2.10) < 0.001


def test_rate_increases_into_crisis():
    assert BSUoSLedger.rate_for_year(2022) > BSUoSLedger.rate_for_year(2020)


def test_total_charged_by_year():
    ledger = BSUoSLedger()
    ledger.record_charge(_charge(period="2022-01", mwh=100.0, rate=6.85))
    ledger.record_charge(_charge(period="2021-12", mwh=100.0, rate=4.10))
    y2022 = ledger.total_charged_gbp(2022)
    assert abs(y2022 - 685.0) < 0.01


def test_crisis_uplift_multiple():
    ledger = BSUoSLedger()
    mult = ledger.crisis_uplift_multiple()
    assert mult > 3.0  # 2022 was >3x 2016 rate


def test_annual_rate_trend_sorted():
    ledger = BSUoSLedger()
    trend = ledger.annual_rate_trend()
    assert trend[0]["year"] < trend[-1]["year"]
    assert trend[0]["year"] == 2016


def test_bsuos_summary_keys():
    ledger = BSUoSLedger()
    ledger.record_charge(_charge())
    s = ledger.bsuos_summary(2022)
    for k in ("total_charges", "total_charged_gbp", "crisis_uplift_multiple",
               "peak_rate_gbp_per_mwh", "peak_rate_year"):
        assert k in s


def test_peak_rate_year_is_2022():
    ledger = BSUoSLedger()
    s = ledger.bsuos_summary()
    assert s["peak_rate_year"] == 2022
