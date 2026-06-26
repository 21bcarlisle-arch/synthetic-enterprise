import datetime as dt
import pytest
from company.market.network_charge_ledger import (
    NetworkChargeType, NetworkChargeRate, NetworkChargeRecord, NetworkChargeLedger
)


def test_set_and_get_rate():
    ledger = NetworkChargeLedger()
    ledger.set_rate(2022, NetworkChargeType.TNUOS, 'electricity', 15.50,
                    'National Grid TNUoS 2022/23')
    rate = ledger.get_rate(2022, NetworkChargeType.TNUOS, 'electricity')
    assert rate == pytest.approx(15.50)


def test_missing_rate_returns_none():
    ledger = NetworkChargeLedger()
    assert ledger.get_rate(2020, NetworkChargeType.DUOS, 'electricity') is None


def test_post_and_charge_gbp():
    ledger = NetworkChargeLedger()
    rec = ledger.post_charge(
        'C001', 'MPAN001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
        NetworkChargeType.TNUOS, 10.0, 15.50
    )
    assert rec.charge_gbp == pytest.approx(155.0)


def test_total_charges_for_customer():
    ledger = NetworkChargeLedger()
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.TNUOS, 10.0, 15.50)
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.DUOS, 10.0, 8.0)
    total = ledger.total_charges_gbp('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert total == pytest.approx(155.0 + 80.0)


def test_charges_by_type():
    ledger = NetworkChargeLedger()
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                        NetworkChargeType.BSUOS, 5.0, 20.0)
    ledger.post_charge('C002', 'MPAN002', dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                        NetworkChargeType.TNUOS, 8.0, 15.0)
    by_type = ledger.charges_by_type(2022)
    assert by_type['bsuos'] == pytest.approx(100.0)
    assert by_type['tnuos'] == pytest.approx(120.0)


def test_portfolio_total():
    ledger = NetworkChargeLedger()
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.DUOS, 10.0, 8.0)
    ledger.post_charge('C002', 'MPAN002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.METERING, 10.0, 2.0)
    total = ledger.portfolio_total_gbp(2022)
    assert total == pytest.approx(80.0 + 20.0)


def test_different_customer_excluded():
    ledger = NetworkChargeLedger()
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.TNUOS, 10.0, 15.0)
    ledger.post_charge('C002', 'MPAN002', dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        NetworkChargeType.TNUOS, 10.0, 15.0)
    total = ledger.total_charges_gbp('C001', dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert total == pytest.approx(150.0)


def test_annual_summary():
    ledger = NetworkChargeLedger()
    ledger.post_charge('C001', 'MPAN001', dt.date(2022, 6, 1), dt.date(2022, 6, 30),
                        NetworkChargeType.CMSUOS, 20.0, 5.0)
    s = ledger.annual_summary(2022)
    assert s['total_gbp'] == pytest.approx(100.0)
    assert 'cmsuos' in s['by_type']
    assert s['record_count'] == 1
