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
