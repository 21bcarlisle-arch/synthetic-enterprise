import pytest
from company.regulatory.fuel_mix_disclosure import (
    FuelMixDisclosureBook, FuelMixDisclosure, FuelSource, _UK_AVG_MIX
)


def _fmd(year=2022, coal=0.0, gas=0.0, nuclear=0.0, ren=100.0, other=0.0, unspec=0.0,
         rego_mwh=10000.0, total_mwh=10000.0):
    return FuelMixDisclosure(
        disclosure_year=year, coal_pct=coal, gas_pct=gas, nuclear_pct=nuclear,
        renewables_pct=ren, other_pct=other, unspecified_pct=unspec,
        rego_covered_mwh=rego_mwh, total_retail_mwh=total_mwh,
    )


def test_total_pct_sums():
    d = _fmd(coal=5.0, gas=30.0, nuclear=10.0, ren=50.0, other=5.0, unspec=0.0)
    assert abs(d.total_pct - 100.0) < 0.01


def test_rego_coverage_full():
    d = _fmd(rego_mwh=10000.0, total_mwh=10000.0)
    assert abs(d.rego_coverage_pct - 100.0) < 0.01


def test_rego_coverage_partial():
    d = _fmd(rego_mwh=5000.0, total_mwh=10000.0)
    assert abs(d.rego_coverage_pct - 50.0) < 0.01


def test_is_100pct_renewable():
    d = _fmd(ren=100.0)
    assert d.is_100pct_renewable is True


def test_not_100pct_renewable():
    d = _fmd(ren=80.0, gas=20.0)
    assert d.is_100pct_renewable is False


def test_vs_uk_average_keys():
    d = _fmd(year=2022)
    delta = d.vs_uk_average()
    for k in ("coal_delta", "gas_delta", "nuclear_delta", "renewables_delta"):
        assert k in delta


def test_vs_uk_average_values():
    d = _fmd(year=2022, ren=100.0, coal=0.0, gas=0.0, nuclear=0.0)
    delta = d.vs_uk_average()
    uk_ren = _UK_AVG_MIX["2022"]["renewables"] * 100
    assert abs(delta["renewables_delta"] - (100.0 - uk_ren)) < 0.01


def test_file_and_retrieve():
    book = FuelMixDisclosureBook()
    book.file_disclosure(_fmd(year=2022))
    d = book.disclosure_for_year(2022)
    assert d is not None
    assert d.disclosure_year == 2022


def test_disclosure_missing_year():
    book = FuelMixDisclosureBook()
    assert book.disclosure_for_year(2099) is None


def test_renewable_trend_sorted():
    book = FuelMixDisclosureBook()
    book.file_disclosure(_fmd(year=2022, ren=100.0))
    book.file_disclosure(_fmd(year=2020, ren=80.0))
    trend = book.renewable_trend()
    assert trend[0]["year"] == 2020
    assert trend[1]["renewables_pct"] == 100.0


def test_fmd_summary_keys():
    book = FuelMixDisclosureBook()
    book.file_disclosure(_fmd(year=2022))
    s = book.fmd_summary()
    for k in ("years_filed", "latest_year", "latest_renewables_pct",
               "is_100pct_renewable", "rego_coverage_pct"):
        assert k in s


def test_fmd_summary_empty():
    book = FuelMixDisclosureBook()
    s = book.fmd_summary()
    assert s["years_filed"] == 0
