import pytest
from datetime import date
from company.billing.economy7 import (
    TariffRegister, E7MeterRead, E7Bill, e7_unit_rate_ppm, generate_e7_bill,
)


def test_day_rate_2022_crisis():
    rate = e7_unit_rate_ppm(2022, TariffRegister.DAY)
    assert rate == pytest.approx(34.0)


def test_night_rate_2022_crisis():
    rate = e7_unit_rate_ppm(2022, TariffRegister.NIGHT)
    assert rate == pytest.approx(19.0)


def test_night_rate_significantly_below_day():
    for year in [2016, 2019, 2022, 2024]:
        day = e7_unit_rate_ppm(year, TariffRegister.DAY)
        night = e7_unit_rate_ppm(year, TariffRegister.NIGHT)
        assert night < day, f"Night {night} >= Day {day} in {year}"


def test_meter_read_total_kwh():
    r = E7MeterRead("C001", date(2022, 1, 31), day_kwh=300.0, night_kwh=150.0)
    assert r.total_kwh == pytest.approx(450.0)


def test_meter_read_night_pct():
    r = E7MeterRead("C001", date(2022, 1, 31), day_kwh=300.0, night_kwh=100.0)
    assert r.night_pct == pytest.approx(25.0)


def test_meter_read_night_pct_zero_if_no_consumption():
    r = E7MeterRead("C001", date(2022, 1, 31), day_kwh=0.0, night_kwh=0.0)
    assert r.night_pct == pytest.approx(0.0)


def test_e7_bill_charges_2022():
    bill = generate_e7_bill("C001", date(2022, 1, 1), date(2022, 1, 31),
                            day_kwh=300.0, night_kwh=150.0)
    assert bill.day_rate_ppm == pytest.approx(34.0)
    assert bill.night_rate_ppm == pytest.approx(19.0)
    expected_day = 300.0 * 34.0 / 10000
    expected_night = 150.0 * 19.0 / 10000
    assert bill.day_charge_gbp == pytest.approx(expected_day, abs=0.01)
    assert bill.night_charge_gbp == pytest.approx(expected_night, abs=0.01)


def test_e7_bill_total_is_sum_of_components():
    bill = generate_e7_bill("C001", date(2022, 1, 1), date(2022, 1, 31),
                            day_kwh=300.0, night_kwh=150.0)
    assert bill.total_gbp == pytest.approx(bill.day_charge_gbp + bill.night_charge_gbp, abs=0.01)


def test_e7_bill_blended_rate_between_day_and_night():
    bill = generate_e7_bill("C001", date(2022, 1, 1), date(2022, 1, 31),
                            day_kwh=300.0, night_kwh=150.0)
    assert bill.night_rate_ppm < bill.blended_rate_ppm < bill.day_rate_ppm


def test_e7_bill_2022_more_expensive_than_2016():
    bill_2016 = generate_e7_bill("C001", date(2016, 1, 1), date(2016, 1, 31), 300.0, 150.0)
    bill_2022 = generate_e7_bill("C001", date(2022, 1, 1), date(2022, 1, 31), 300.0, 150.0)
    assert bill_2022.total_gbp > bill_2016.total_gbp


def test_e7_bill_frozen():
    bill = generate_e7_bill("C001", date(2022, 1, 1), date(2022, 1, 31), 300.0, 150.0)
    with pytest.raises(Exception):
        bill.day_kwh = 999.0
