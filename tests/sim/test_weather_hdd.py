"""Tests for sim/weather_hdd.py -- HDD model for gas consumption."""

import pytest

from sim.weather_hdd import (
    HDD_BASE_TEMP_C,
    REFERENCE_MONTHLY_HDD,
    _resolve_source_cid,
    get_hdd,
)


def test_hdd_base_temp_is_15p5():
    assert HDD_BASE_TEMP_C == pytest.approx(15.5)


def test_reference_hdd_all_12_months():
    assert set(REFERENCE_MONTHLY_HDD.keys()) == set(range(1, 13))


def test_reference_hdd_january_highest():
    assert REFERENCE_MONTHLY_HDD[1] == max(REFERENCE_MONTHLY_HDD.values())


def test_reference_hdd_july_lowest():
    assert REFERENCE_MONTHLY_HDD[7] == min(REFERENCE_MONTHLY_HDD.values())


def test_resolve_source_cid_gas_customer():
    assert _resolve_source_cid("C1g") == "C1"


def test_resolve_source_cid_non_gas_unchanged():
    assert _resolve_source_cid("C1") == "C1"


def test_resolve_source_cid_longer_gas():
    assert _resolve_source_cid("C_IC3g") == "C_IC3"


def test_get_hdd_unknown_customer_falls_back_to_reference():
    # Unknown customer → no CSV file → uses REFERENCE_MONTHLY_HDD / 30
    hdd = get_hdd("2022-01-15", "UNKNOWN_CUSTOMER_XYZ")
    expected = REFERENCE_MONTHLY_HDD[1] / 30.0
    assert hdd == pytest.approx(expected)


def test_get_hdd_never_negative():
    # Whatever date/customer, HDD must be >= 0
    for month in range(1, 13):
        hdd = get_hdd(f"2022-{month:02d}-15", "UNKNOWN_CUSTOMER_XYZ")
        assert hdd >= 0.0
