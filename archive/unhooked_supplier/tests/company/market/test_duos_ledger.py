import pytest
from company.market.duos_ledger import (
    DUoSLedger, DUoSCharge, DNOArea, VoltageLevel
)


def _charge(aid="C1", period="2022-09", dno=DNOArea.SOUTHERN, vol=VoltageLevel.LOW,
            kwh=1000.0, rate=2.35, standing=5.0):
    return DUoSCharge(
        account_id=aid, charge_period=period, dno_area=dno, voltage_level=vol,
        consumption_kwh=kwh, unit_rate_p_per_kwh=rate, standing_charge_gbp=standing,
    )


def test_unit_charge_gbp():
    c = _charge(kwh=1000.0, rate=2.35, standing=0.0)
    assert abs(c.unit_charge_gbp - 23.50) < 0.01


def test_total_charge_gbp():
    c = _charge(kwh=1000.0, rate=2.35, standing=5.0)
    assert abs(c.total_charge_gbp - 28.50) < 0.01


def test_is_hv():
    c_hv = _charge(vol=VoltageLevel.HIGH)
    c_lv = _charge(vol=VoltageLevel.LOW)
    assert c_hv.is_hv is True
    assert c_lv.is_hv is False


def test_unit_rate_for_year_lv():
    rate = DUoSLedger.unit_rate_for_year(2022, VoltageLevel.LOW)
    assert abs(rate - 2.35) < 0.01


def test_unit_rate_for_year_hv_discount():
    lv = DUoSLedger.unit_rate_for_year(2022, VoltageLevel.LOW)
    hv = DUoSLedger.unit_rate_for_year(2022, VoltageLevel.HIGH)
    assert hv < lv
    assert abs(hv - lv * 0.6) < 0.01


def test_record_and_filter_by_account():
    ledger = DUoSLedger()
    ledger.record_charge(_charge(aid="C1"))
    ledger.record_charge(_charge(aid="C2"))
    assert len(ledger.charges_for_account("C1")) == 1


def test_total_charged_gbp_all():
    ledger = DUoSLedger()
    ledger.record_charge(_charge(kwh=1000.0, rate=2.0, standing=0.0))
    ledger.record_charge(_charge(kwh=2000.0, rate=2.0, standing=0.0))
    assert abs(ledger.total_charged_gbp() - 60.0) < 0.01


def test_total_charged_gbp_by_year():
    ledger = DUoSLedger()
    ledger.record_charge(_charge(period="2022-01", kwh=1000.0, rate=2.35, standing=0.0))
    ledger.record_charge(_charge(period="2021-12", kwh=1000.0, rate=2.20, standing=0.0))
    y2022 = ledger.total_charged_gbp(2022)
    assert abs(y2022 - 23.50) < 0.01


def test_hv_customer_count():
    ledger = DUoSLedger()
    ledger.record_charge(_charge(aid="IC1", vol=VoltageLevel.HIGH))
    ledger.record_charge(_charge(aid="C1", vol=VoltageLevel.LOW))
    assert ledger.hv_customer_count() == 1


def test_annual_unit_cost():
    ledger = DUoSLedger()
    ledger.record_charge(_charge(period="2022-09", kwh=1000.0, rate=2.35, standing=0.0))
    cost = ledger.annual_unit_cost_p_per_kwh(2022)
    assert abs(cost - 2.35) < 0.01


def test_duos_summary_keys():
    ledger = DUoSLedger()
    ledger.record_charge(_charge())
    s = ledger.duos_summary(2022)
    for k in ("total_charges", "total_charged_gbp", "hv_customers", "annual_unit_cost_p_per_kwh"):
        assert k in s


# --- Phase LL depth tests ---

def test_account_id_stored():
    c = _charge(aid="ACCT_LL")
    assert c.account_id == "ACCT_LL"


def test_charge_period_stored():
    c = _charge(period="2023-06")
    assert c.charge_period == "2023-06"


def test_dno_area_stored():
    c = _charge(dno=DNOArea.LONDON)
    assert c.dno_area == DNOArea.LONDON


def test_voltage_level_stored():
    c = _charge(vol=VoltageLevel.HIGH)
    assert c.voltage_level == VoltageLevel.HIGH


def test_consumption_kwh_stored():
    c = _charge(kwh=5000.0)
    assert c.consumption_kwh == pytest.approx(5000.0)


def test_unit_rate_stored():
    c = _charge(rate=2.48)
    assert c.unit_rate_p_per_kwh == pytest.approx(2.48)


def test_standing_charge_default_zero():
    c = DUoSCharge(
        account_id="C1", charge_period="2022-09", dno_area=DNOArea.SOUTHERN,
        voltage_level=VoltageLevel.LOW, consumption_kwh=1000.0, unit_rate_p_per_kwh=2.35,
    )
    assert c.standing_charge_gbp == pytest.approx(0.0)


def test_rate_2016_exact():
    assert DUoSLedger.unit_rate_for_year(2016) == pytest.approx(1.85)


def test_rate_2025_exact():
    assert DUoSLedger.unit_rate_for_year(2025) == pytest.approx(2.75)


def test_rate_fallback():
    assert DUoSLedger.unit_rate_for_year(2010) == pytest.approx(2.50)
