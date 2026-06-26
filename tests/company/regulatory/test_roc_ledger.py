import datetime as dt
import pytest
from company.regulatory.roc_ledger import (
    ROCTechnology, ROCPurchase, ROCompliancePeriod,
    ROCLedger, get_buyout_price, get_ro_level
)


def test_buyout_price_2022():
    assert get_buyout_price(2022) == pytest.approx(54.35)


def test_ro_level_decreasing():
    assert get_ro_level(2016) > get_ro_level(2022) > get_ro_level(2025)


def test_roc_purchase_cost():
    p = ROCPurchase('R001', ROCTechnology.ONSHORE_WIND, 100.0, 45.0, dt.date(2022, 3, 1))
    assert p.total_cost_gbp == pytest.approx(4500.0)


def test_obligation_rocs():
    p = ROCompliancePeriod(2022, supplied_mwh=10000.0)
    expected = 10000.0 * get_ro_level(2022)
    assert p.obligation_rocs == pytest.approx(expected, rel=0.01)


def test_shortfall_when_not_surrendered():
    p = ROCompliancePeriod(2022, supplied_mwh=1000.0)
    assert p.shortfall_rocs > 0


def test_compliant_when_fully_surrendered():
    p = ROCompliancePeriod(2022, supplied_mwh=1000.0)
    p.rocs_surrendered = p.obligation_rocs
    assert p.is_compliant


def test_buyout_cost():
    p = ROCompliancePeriod(2022, supplied_mwh=1000.0)
    expected = p.shortfall_rocs * get_buyout_price(2022)
    assert p.buyout_cost_gbp == pytest.approx(expected, rel=0.01)


def test_ledger_surrender_and_compliance():
    ledger = ROCLedger()
    ledger.open_period(2022, 10000.0)
    ledger.buy_rocs(ROCTechnology.OFFSHORE_WIND, 200.0, 48.0, dt.date(2022, 5, 1))
    ledger.surrender_rocs(2022, 200.0)
    period = ledger.get_period(2022)
    assert period is not None
    assert period.rocs_surrendered == pytest.approx(200.0)


def test_roc_summary():
    ledger = ROCLedger()
    ledger.open_period(2022, 5000.0)
    ledger.buy_rocs(ROCTechnology.SOLAR_PV, 50.0, 44.0, dt.date(2022, 4, 1))
    s = ledger.roc_summary(2022)
    assert s['buyout_price_gbp'] == pytest.approx(54.35)
    assert s['roc_spend_gbp'] == pytest.approx(50.0 * 44.0)
