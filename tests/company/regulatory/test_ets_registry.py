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


# --- Phase KX depth tests ---

def test_purchase_id_stored():
    p = AllowancePurchase("ETS-001", 2022, dt.date(2022, 3, 1), 1000.0, 72.0, AllowanceSource.AUCTION)
    assert p.purchase_id == "ETS-001"


def test_purchase_year_stored():
    p = AllowancePurchase("ETS-001", 2022, dt.date(2022, 3, 1), 1000.0, 72.0, AllowanceSource.AUCTION)
    assert p.year == 2022


def test_tonnes_co2_stored():
    p = AllowancePurchase("ETS-001", 2022, dt.date(2022, 3, 1), 500.0, 72.0, AllowanceSource.AUCTION)
    assert p.tonnes_co2 == pytest.approx(500.0)


def test_source_stored():
    p = AllowancePurchase("ETS-001", 2022, dt.date(2022, 3, 1), 100.0, 72.0, AllowanceSource.SECONDARY_MARKET)
    assert p.source == AllowanceSource.SECONDARY_MARKET


def test_ukets_price_2024():
    assert get_ukets_price(2024) == pytest.approx(45.0)


def test_ukets_price_future_uses_latest():
    price = get_ukets_price(2030)
    assert isinstance(price, float)


def test_surrender_reduces_holdings():
    r = ETSRegistry()
    r.purchase("P1", 2022, dt.date(2022, 1, 1), 500.0, 72.0, AllowanceSource.AUCTION)
    r.surrender(2022, 200.0)
    assert r.holding_tonnes(2022) == pytest.approx(300.0)


def test_holdings_zero_no_purchases():
    r = ETSRegistry()
    assert r.holding_tonnes(2022) == pytest.approx(0.0)


def test_total_spend_zero_no_purchases():
    r = ETSRegistry()
    assert r.total_spend_gbp(2022) == pytest.approx(0.0)


def test_compliance_position_none_no_obligation():
    r = ETSRegistry()
    r.purchase("P1", 2022, dt.date(2022, 1, 1), 500.0, 72.0, AllowanceSource.AUCTION)
    assert r.compliance_position(2022) is None
