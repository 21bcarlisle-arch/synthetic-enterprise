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
