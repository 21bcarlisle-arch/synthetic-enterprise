import pytest
from company.regulatory.price_cap import (
    PriceCapBook, CapComplianceCheck, CapStatus
)


def test_elec_cap_q3_2022():
    assert abs(PriceCapBook.elec_cap_p_kwh("2022-Q3") - 52.0) < 0.01


def test_gas_cap_q3_2022():
    assert abs(PriceCapBook.gas_cap_p_kwh("2022-Q3") - 14.97) < 0.01


def test_typical_annual_bill_2022_q3():
    assert PriceCapBook.typical_annual_bill("2022-Q3") == 3549


def test_cap_data_unknown_quarter():
    assert PriceCapBook.cap_data("2018-Q4") is None


def test_check_below_cap():
    check = CapComplianceCheck(
        quarter="2022-Q3", commodity="electricity",
        supplier_rate_p_kwh=50.0, cap_rate_p_kwh=52.0
    )
    assert check.status == CapStatus.BELOW_CAP
    assert check.is_compliant is True
    assert abs(check.headroom_p_kwh - 2.0) < 0.01


def test_check_exceeds_cap():
    check = CapComplianceCheck(
        quarter="2022-Q3", commodity="electricity",
        supplier_rate_p_kwh=55.0, cap_rate_p_kwh=52.0
    )
    assert check.status == CapStatus.EXCEEDS_CAP
    assert check.is_compliant is False


def test_check_pre_cap():
    check = CapComplianceCheck(
        quarter="2018-Q2", commodity="electricity",
        supplier_rate_p_kwh=15.0, cap_rate_p_kwh=0.0
    )
    assert check.status == CapStatus.PRE_CAP
    assert check.is_compliant is True


def test_breach_quarters():
    book = PriceCapBook()
    book.record_check(CapComplianceCheck(
        quarter="2022-Q3", commodity="electricity",
        supplier_rate_p_kwh=55.0, cap_rate_p_kwh=52.0
    ))
    book.record_check(CapComplianceCheck(
        quarter="2022-Q3", commodity="electricity",
        supplier_rate_p_kwh=50.0, cap_rate_p_kwh=52.0
    ))
    assert len(book.breach_quarters()) == 1


def test_cap_summary_peak_quarter():
    book = PriceCapBook()
    s = book.cap_summary()
    assert s["peak_quarter"] == "2022-Q3"
    assert s["peak_typical_annual_gbp"] == 3549


def test_cap_increases_sharply_2022():
    q1 = PriceCapBook.elec_cap_p_kwh("2021-Q4")
    q3 = PriceCapBook.elec_cap_p_kwh("2022-Q3")
    assert q3 > q1 * 2  # more than doubled
