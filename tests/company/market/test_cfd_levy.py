import datetime as dt
import pytest
from company.market.cfd_levy import (
    LevyDirection, CfDLevyCharge, CfDLevyBook, get_levy_rate, _quarter
)


def test_quarter_mapping():
    assert _quarter(1) == 1
    assert _quarter(3) == 1
    assert _quarter(4) == 2
    assert _quarter(7) == 3
    assert _quarter(10) == 4
    assert _quarter(12) == 4


def test_get_levy_rate_positive_normal_year():
    rate = get_levy_rate(2019, 2)
    assert rate == pytest.approx(4.6)
    assert rate > 0


def test_get_levy_rate_negative_crisis_peak():
    # Q4 2022: generators paying back -> suppliers receive credit
    rate = get_levy_rate(2022, 4)
    assert rate == pytest.approx(-12.3)
    assert rate < 0


def test_get_levy_rate_fallback_unknown_year():
    rate = get_levy_rate(2030, 1)
    assert rate == pytest.approx(3.0)


def test_charge_direction_positive():
    charge = CfDLevyCharge(
        account_id="ACC-001", charge_date=dt.date(2019, 6, 1),
        year=2019, quarter=2, consumption_mwh=100.0, rate_gbp_per_mwh=4.6,
    )
    assert charge.direction == LevyDirection.POSITIVE
    assert not charge.is_credit
    assert charge.levy_gbp == pytest.approx(460.0)


def test_charge_direction_negative_credit():
    charge = CfDLevyCharge(
        account_id="ACC-001", charge_date=dt.date(2022, 10, 1),
        year=2022, quarter=4, consumption_mwh=500.0, rate_gbp_per_mwh=-12.3,
    )
    assert charge.direction == LevyDirection.NEGATIVE
    assert charge.is_credit
    assert charge.levy_gbp == pytest.approx(-6150.0)


def test_book_record_charge_derives_rate():
    book = CfDLevyBook()
    charge = book.record_charge("ACC-001", dt.date(2019, 5, 15), 100.0)
    assert charge.year == 2019
    assert charge.quarter == 2
    assert charge.rate_gbp_per_mwh == pytest.approx(4.6)
    assert charge.levy_gbp == pytest.approx(460.0)


def test_book_annual_levy_gbp():
    book = CfDLevyBook()
    book.record_charge("ACC-001", dt.date(2020, 1, 15), 200.0)   # Q1 2020: 5.2
    book.record_charge("ACC-001", dt.date(2020, 7, 15), 200.0)   # Q3 2020: 4.9
    annual = book.annual_levy_gbp(2020)
    expected = 200.0 * 5.2 + 200.0 * 4.9
    assert annual == pytest.approx(expected, rel=1e-6)


def test_book_quarterly_levy_gbp():
    book = CfDLevyBook()
    book.record_charge("ACC-001", dt.date(2022, 11, 1), 300.0)  # Q4 2022: -12.3
    book.record_charge("ACC-002", dt.date(2022, 11, 15), 200.0)
    q4_total = book.quarterly_levy_gbp(2022, 4)
    assert q4_total == pytest.approx((300.0 + 200.0) * (-12.3), rel=1e-6)
    assert q4_total < 0


def test_book_total_credit_quarters():
    book = CfDLevyBook()
    # 2022 Q2, Q3, Q4 are negative; 2023 Q1 is negative
    book.record_charge("ACC-001", dt.date(2022, 4, 1), 100.0)   # Q2 2022: -1.8
    book.record_charge("ACC-001", dt.date(2022, 7, 1), 100.0)   # Q3 2022: -8.5
    book.record_charge("ACC-001", dt.date(2022, 10, 1), 100.0)  # Q4 2022: -12.3
    book.record_charge("ACC-001", dt.date(2023, 1, 1), 100.0)   # Q1 2023: -6.2
    book.record_charge("ACC-001", dt.date(2023, 4, 1), 100.0)   # Q2 2023: +1.4
    assert book.total_credit_quarters() == 4


def test_book_levy_summary_2022_net_credit():
    book = CfDLevyBook()
    # 2022: Q1 pos (0.5), Q2/Q3/Q4 negative -> net credit
    for month, mwh in [(1, 400.0), (4, 400.0), (7, 400.0), (10, 400.0)]:
        book.record_charge("ACC-001", dt.date(2022, month, 1), mwh)
    summary = book.levy_summary(2022)
    assert summary["year"] == 2022
    assert summary["is_net_credit"] is True
    assert summary["credit_quarters"] == 3  # Q2, Q3, Q4
    assert summary["accounts_charged"] == 1
    assert summary["total_mwh"] == pytest.approx(1600.0)


def test_book_charges_for_account_filter():
    book = CfDLevyBook()
    book.record_charge("ACC-001", dt.date(2020, 3, 1), 100.0)
    book.record_charge("ACC-002", dt.date(2020, 3, 1), 200.0)
    book.record_charge("ACC-001", dt.date(2020, 6, 1), 150.0)
    acc1_charges = book.charges_for_account("ACC-001")
    assert len(acc1_charges) == 2
    assert all(c.account_id == "ACC-001" for c in acc1_charges)
