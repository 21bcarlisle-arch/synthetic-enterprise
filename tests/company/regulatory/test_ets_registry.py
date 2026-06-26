import datetime as dt
import pytest
from company.regulatory.ets_registry import (
    AllowanceSource, AllowancePurchase, ComplianceObligation,
    ETSRegistry, get_ukets_price
)


def test_ukets_price_2022():
    assert get_ukets_price(2022) == pytest.approx(72.0)


def test_ukets_price_2021():
    assert get_ukets_price(2021) == pytest.approx(50.0)


def test_purchase_cost():
    p = AllowancePurchase('P001', 2022, dt.date(2022, 3, 1),
                           1000.0, 72.0, AllowanceSource.AUCTION)
    assert p.total_cost_gbp == pytest.approx(72_000.0)


def test_gross_obligation():
    ob = ComplianceObligation(2022, 10_000.0, 0.45, 0.0)
    assert ob.gross_obligation_tonnes == pytest.approx(4500.0)


def test_net_obligation_with_free_allocation():
    ob = ComplianceObligation(2022, 10_000.0, 0.45, 600.0)
    assert ob.net_obligation_tonnes == pytest.approx(3900.0)


def test_net_obligation_never_negative():
    ob = ComplianceObligation(2022, 1000.0, 0.06, 10_000.0)
    assert ob.net_obligation_tonnes == 0.0


def test_registry_holdings():
    reg = ETSRegistry()
    reg.purchase('P001', 2022, dt.date(2022, 1, 15), 5000.0, 70.0, AllowanceSource.AUCTION)
    reg.surrender(2022, 2000.0)
    assert reg.holding_tonnes(2022) == pytest.approx(3000.0)


def test_compliance_position_surplus():
    reg = ETSRegistry()
    reg.purchase('P002', 2022, dt.date(2022, 2, 1), 5000.0, 72.0, AllowanceSource.AUCTION)
    reg.record_obligation(2022, 10_000.0, 0.40, 0.0)
    pos = reg.compliance_position(2022)
    assert pos is not None
    assert pos['is_compliant']
    assert pos['surplus_deficit_tonnes'] == pytest.approx(5000.0 - 4000.0)


def test_compliance_position_deficit():
    reg = ETSRegistry()
    reg.purchase('P003', 2022, dt.date(2022, 1, 1), 1000.0, 72.0, AllowanceSource.SECONDARY_MARKET)
    reg.record_obligation(2022, 10_000.0, 0.45, 0.0)
    pos = reg.compliance_position(2022)
    assert not pos['is_compliant']
