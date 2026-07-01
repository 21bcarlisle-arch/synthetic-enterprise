import datetime as dt
import pytest
from company.market.gas_storage import (
    StorageFacility, StorageOperation, StorageTransaction,
    GasStorageBook
)


def test_inject_cost():
    t = StorageTransaction(StorageFacility.STUBLACH, dt.date(2022, 5, 1),
                            StorageOperation.INJECT, 1.0, 100.0)
    assert t.cost_gbp == pytest.approx(1.0 * 3412.14 * 100.0, rel=0.001)


def test_withdraw_cost_negative():
    t = StorageTransaction(StorageFacility.STUBLACH, dt.date(2022, 12, 1),
                            StorageOperation.WITHDRAW, 1.0, 200.0)
    assert t.cost_gbp < 0


def test_winter_operation():
    t = StorageTransaction(StorageFacility.STUBLACH, dt.date(2022, 12, 1),
                            StorageOperation.WITHDRAW, 1.0, 200.0)
    assert t.is_winter_operation


def test_summer_not_winter():
    t = StorageTransaction(StorageFacility.HOLFORD, dt.date(2022, 6, 1),
                            StorageOperation.INJECT, 1.0, 80.0)
    assert not t.is_winter_operation


def test_inject_increases_inventory():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    assert book.inventory_mcm(StorageFacility.STUBLACH) == pytest.approx(50.0)


def test_withdraw_reduces_inventory():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 20.0, 200.0)
    assert book.inventory_mcm(StorageFacility.STUBLACH) == pytest.approx(30.0)


def test_total_injected():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 30.0, 80.0)
    book.inject(StorageFacility.HOLFORD, dt.date(2022, 7, 1), 10.0, 85.0)
    assert book.total_injected_mcm(2022) == pytest.approx(40.0)


def test_spread():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 50.0, 200.0)
    spread = book.spread_gbp_per_therm(StorageFacility.STUBLACH, 2022)
    assert spread == pytest.approx(120.0)


def test_storage_summary():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    s = book.storage_summary(2022)
    assert s['total_injected_mcm'] == pytest.approx(50.0)
    assert s['total_inventory_mcm'] == pytest.approx(50.0)


def test_inventory_all_facilities():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    book.inject(StorageFacility.HOLFORD, dt.date(2022, 6, 1), 10.0, 85.0)
    assert book.inventory_mcm() == pytest.approx(60.0)


def test_withdraw_capped_at_zero():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 20.0, 80.0)
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 30.0, 200.0)
    assert book.inventory_mcm(StorageFacility.STUBLACH) == 0.0


def test_net_storage_cost_inject_only():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 10.0, 100.0)
    # cost = 10 * 3412.14 * 100 = 3,412,140
    assert book.net_storage_cost_gbp(2022) == pytest.approx(10 * 3412.14 * 100, rel=0.001)


def test_net_storage_cost_inject_withdraw_net():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 10.0, 80.0)
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 5.0, 80.0)
    # inject cost positive, withdraw cost negative; same price → net = positive
    net = book.net_storage_cost_gbp(2022)
    assert net == pytest.approx(5 * 3412.14 * 80, rel=0.001)


def test_spread_none_when_no_inject():
    book = GasStorageBook()
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 10.0, 200.0)
    assert book.spread_gbp_per_therm(StorageFacility.STUBLACH, 2022) is None


def test_spread_none_when_no_withdraw():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 10.0, 80.0)
    assert book.spread_gbp_per_therm(StorageFacility.STUBLACH, 2023) is None


def test_storage_summary_net_cost():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 50.0, 80.0)
    book.withdraw(StorageFacility.STUBLACH, dt.date(2022, 12, 1), 30.0, 200.0)
    s = book.storage_summary(2022)
    assert 'net_storage_cost_gbp' in s
    assert s['net_storage_cost_gbp'] < 0


def test_total_injected_year_filter():
    book = GasStorageBook()
    book.inject(StorageFacility.STUBLACH, dt.date(2021, 5, 1), 40.0, 75.0)
    book.inject(StorageFacility.STUBLACH, dt.date(2022, 5, 1), 30.0, 80.0)
    assert book.total_injected_mcm(2022) == pytest.approx(30.0)
    assert book.total_injected_mcm(2021) == pytest.approx(40.0)


def test_october_is_winter_operation():
    t = StorageTransaction(StorageFacility.HOLFORD, dt.date(2022, 10, 1),
                            StorageOperation.INJECT, 5.0, 110.0)
    assert t.is_winter_operation


def test_april_not_winter_operation():
    t = StorageTransaction(StorageFacility.STUBLACH, dt.date(2022, 4, 1),
                            StorageOperation.INJECT, 5.0, 85.0)
    assert not t.is_winter_operation
