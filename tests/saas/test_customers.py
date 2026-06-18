"""Tests for saas.customers Phase 8a additions: ACQUIRED_CUSTOMERS and helpers."""

import pytest

from saas.customers import (
    ACQUIRED_CUSTOMERS,
    CUSTOMERS,
    SUCCESSOR_CUSTOMERS,
    _clear_acquired_customers,
    get_customer,
    make_acquired_customer,
)


@pytest.fixture(autouse=True)
def clear_acquired():
    """Ensure ACQUIRED_CUSTOMERS is empty before and after each test."""
    _clear_acquired_customers()
    yield
    _clear_acquired_customers()


def test_acquired_customers_starts_empty():
    assert ACQUIRED_CUSTOMERS == []


def test_get_customer_finds_original_customers():
    assert get_customer("C1") is not None
    assert get_customer("C1")["segment"] == "resi"


def test_get_customer_finds_successor_customers():
    assert get_customer("C2_2") is not None
    assert get_customer("C2_2")["successor_of"] == "C2"


def test_get_customer_returns_none_for_unknown():
    assert get_customer("C99") is None


def test_make_acquired_customer_clones_predecessor_profile():
    predecessor = get_customer("C3")
    new_customer = make_acquired_customer("C3_3", predecessor, "2020-06-30")
    assert new_customer["customer_id"] == "C3_3"
    assert new_customer["successor_of"] == "C3"
    assert new_customer["location"] == predecessor["location"]
    assert new_customer["epc_rating"] == predecessor["epc_rating"]
    assert new_customer["segment"] == predecessor["segment"]
    assert new_customer["commodity"] == "electricity"
    assert new_customer["acquisition_type"] == "fresh_market"
    assert new_customer["acquisition_date"] == "2020-06-30"


def test_make_acquired_customer_sme_copies_profile_class():
    predecessor = get_customer("C5")
    new_customer = make_acquired_customer("C5_3", predecessor, "2021-12-30")
    assert new_customer["profile_class"] == predecessor["profile_class"]


def test_get_customer_finds_dynamically_acquired_customer():
    predecessor = get_customer("C3")
    new_customer = make_acquired_customer("C3_3", predecessor, "2020-06-30")
    ACQUIRED_CUSTOMERS.append(new_customer)
    found = get_customer("C3_3")
    assert found is not None
    assert found["customer_id"] == "C3_3"


def test_clear_acquired_customers_removes_all():
    predecessor = get_customer("C3")
    ACQUIRED_CUSTOMERS.append(make_acquired_customer("C3_3", predecessor, "2020-06-30"))
    assert len(ACQUIRED_CUSTOMERS) == 1
    _clear_acquired_customers()
    assert ACQUIRED_CUSTOMERS == []
