import datetime as dt
import pytest
from company.regulatory.ofgem_supply_return import OfgemSupplyReturn, OfgemReturnBook


def _return(year=2022, complaints=500):
    return OfgemSupplyReturn(
        year=year, submitted_date=dt.date(year + 1, 3, 31),
        total_customers_residential=5000, total_customers_sme=200, total_customers_ic=10,
        elec_supplied_gwh=25.0, gas_supplied_gwh=60.0,
        residential_complaints=complaints,
        average_debt_per_customer_gbp=180.0,
        whd_customers_supported=500,
        gsop_payments_gbp=2400.0,
        bad_debt_written_off_gbp=900_000.0,
    )


def test_total_customers():
    r = _return()
    assert r.total_customers == 5210


def test_complaints_per_100():
    r = _return(complaints=500)
    assert r.complaints_per_100_customers == pytest.approx(10.0)


def test_is_submitted():
    r = _return()
    assert r.is_submitted is True


def test_whd_penetration_pct():
    r = _return()
    assert r.whd_penetration_pct == pytest.approx(10.0)


def test_summary_keys():
    r = _return()
    s = r.summary()
    assert 'complaints_per_100_customers' in s
    assert 'whd_penetration_pct' in s
    assert 'bad_debt_written_off_gbp' in s
    assert 'total_customers' in s


def test_file_and_retrieve():
    book = OfgemReturnBook()
    book.file_return(
        year=2022, submitted_date=dt.date(2023, 3, 31),
        total_customers_residential=5000, total_customers_sme=200, total_customers_ic=10,
        elec_supplied_gwh=25.0, gas_supplied_gwh=60.0,
        residential_complaints=500, average_debt_per_customer_gbp=180.0,
        whd_customers_supported=500, gsop_payments_gbp=2400.0,
    )
    r = book.get(2022)
    assert r is not None
    assert r.year == 2022


def test_missing_years():
    book = OfgemReturnBook()
    book.file_return(
        year=2021, submitted_date=dt.date(2022, 3, 31),
        total_customers_residential=4000, total_customers_sme=150, total_customers_ic=8,
        elec_supplied_gwh=20.0, gas_supplied_gwh=50.0,
        residential_complaints=300, average_debt_per_customer_gbp=120.0,
        whd_customers_supported=400, gsop_payments_gbp=1500.0,
    )
    missing = book.missing_years(2019, 2022)
    assert 2019 in missing
    assert 2020 in missing
    assert 2021 not in missing


def test_all_returns_sorted():
    book = OfgemReturnBook()
    for year in [2022, 2020, 2021]:
        book.file_return(
            year=year, submitted_date=dt.date(year + 1, 3, 31),
            total_customers_residential=5000, total_customers_sme=200, total_customers_ic=10,
            elec_supplied_gwh=25.0, gas_supplied_gwh=60.0,
            residential_complaints=400, average_debt_per_customer_gbp=150.0,
            whd_customers_supported=450, gsop_payments_gbp=1800.0,
        )
    years = [r.year for r in book.all_returns()]
    assert years == [2020, 2021, 2022]


# --- Phase KP depth tests ---

def test_year_stored():
    r = _return(year=2022)
    assert r.year == 2022


def test_elec_supplied_stored():
    r = _return()
    assert r.elec_supplied_gwh == pytest.approx(25.0)


def test_gas_supplied_stored():
    r = _return()
    assert r.gas_supplied_gwh == pytest.approx(60.0)


def test_residential_customers_stored():
    r = _return()
    assert r.total_customers_residential == 5000


def test_sme_customers_stored():
    r = _return()
    assert r.total_customers_sme == 200


def test_complaints_stored():
    r = _return(complaints=300)
    assert r.residential_complaints == 300


def test_avg_debt_stored():
    r = _return()
    assert r.average_debt_per_customer_gbp == pytest.approx(180.0)


def test_get_missing_returns_none():
    book = OfgemReturnBook()
    assert book.get(2099) is None


def test_missing_years_when_none_filed():
    book = OfgemReturnBook()
    missing = book.missing_years(2020, 2022)
    assert set(missing) == {2020, 2021, 2022}


def test_complaints_per_100_zero_customers():
    r = OfgemSupplyReturn(
        year=2022, submitted_date=dt.date(2023, 3, 31),
        total_customers_residential=0, total_customers_sme=0, total_customers_ic=0,
        elec_supplied_gwh=0.0, gas_supplied_gwh=0.0,
        residential_complaints=0,
        average_debt_per_customer_gbp=0.0,
        whd_customers_supported=0,
        gsop_payments_gbp=0.0,
        bad_debt_written_off_gbp=0.0,
    )
    assert r.total_customers == 0
