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


# --- Phase LK depth tests ---

def test_account_id_stored():
    c = _charge(aid="ACCT_LK")
    assert c.account_id == "ACCT_LK"


def test_charge_period_stored():
    c = _charge(period="2023-04")
    assert c.charge_period == "2023-04"


def test_consumption_mwh_stored():
    c = _charge(mwh=250.0)
    assert c.consumption_mwh == pytest.approx(250.0)


def test_rate_stored():
    c = _charge(rate=4.20)
    assert c.rate_gbp_per_mwh == pytest.approx(4.20)


def test_rate_2016_exact():
    assert BSUoSLedger.rate_for_year(2016) == pytest.approx(2.10)


def test_rate_2025_exact():
    assert BSUoSLedger.rate_for_year(2025) == pytest.approx(3.80)


def test_rate_unknown_fallback():
    assert BSUoSLedger.rate_for_year(2010) == pytest.approx(3.50)


def test_charges_for_account():
    ledger = BSUoSLedger()
    ledger.record_charge(_charge(aid="C1", period="2022-01"))
    ledger.record_charge(_charge(aid="C2", period="2022-02"))
    ledger.record_charge(_charge(aid="C1", period="2022-03"))
    c1 = ledger.charges_for_account("C1")
    assert len(c1) == 2


def test_total_charged_no_filter():
    ledger = BSUoSLedger()
    ledger.record_charge(_charge(mwh=100.0, rate=2.10))
    ledger.record_charge(_charge(mwh=100.0, rate=6.85))
    total = ledger.total_charged_gbp()
    assert total == pytest.approx(895.0)


def test_is_crisis_2020_false():
    c = _charge(period="2020-06")
    assert c.is_crisis_period is False
