import pytest
from company.regulatory.fuel_mix_disclosure import (
    FuelMixDisclosureBook, FuelMixDisclosure, FuelSource, FuelMixComponent,
)


def _fmd(year=2022, ren_frac=1.0, gas_frac=0.0, nuclear_frac=0.0, coal_frac=0.0,
         rego_held=10000, total_mwh=10000.0):
    parts = []
    if ren_frac > 0:
        parts.append((FuelSource.WIND_ONSHORE, ren_frac))
    if gas_frac > 0:
        parts.append((FuelSource.GAS_CCGT, gas_frac))
    if nuclear_frac > 0:
        parts.append((FuelSource.NUCLEAR, nuclear_frac))
    if coal_frac > 0:
        parts.append((FuelSource.COAL, coal_frac))
    if not parts:
        parts.append((FuelSource.WIND_ONSHORE, 1.0))
    return FuelMixDisclosure(
        disclosure_year=year,
        total_supply_mwh=total_mwh,
        components=tuple(FuelMixComponent(s, f) for s, f in parts),
        rego_certificates_held=rego_held,
    )


def test_renewable_fraction_full():
    d = _fmd(ren_frac=1.0)
    assert abs(d.renewable_fraction - 1.0) < 0.001


def test_renewable_fraction_partial():
    d = _fmd(ren_frac=0.5, gas_frac=0.5)
    assert abs(d.renewable_fraction - 0.5) < 0.001


def test_rego_coverage_full():
    d = _fmd(rego_held=10000, total_mwh=10000.0)
    assert abs(d.rego_coverage_fraction - 1.0) < 0.001


def test_rego_coverage_partial():
    d = _fmd(rego_held=5000, total_mwh=10000.0)
    assert abs(d.rego_coverage_fraction - 0.5) < 0.001


def test_is_fully_rego_matched():
    d = _fmd(rego_held=10000, total_mwh=10000.0)
    assert d.is_fully_rego_matched is True


def test_not_fully_rego_matched():
    d = _fmd(rego_held=5000, total_mwh=10000.0)
    assert d.is_fully_rego_matched is False


def test_unmatched_volume():
    d = _fmd(rego_held=7000, total_mwh=10000.0)
    assert abs(d.unmatched_volume_mwh - 3000.0) < 0.01


def test_carbon_intensity_renewable():
    d = _fmd(ren_frac=1.0)
    assert d.carbon_intensity_gco2_per_kwh < 50


def test_carbon_intensity_gas():
    d = _fmd(ren_frac=0.0, gas_frac=1.0)
    assert d.carbon_intensity_gco2_per_kwh > 300


def test_record_and_retrieve():
    book = FuelMixDisclosureBook()
    book.record_disclosure(2022, 10000.0, [(FuelSource.WIND_ONSHORE, 1.0)], 10000)
    d = book.disclosure_for_year(2022)
    assert d is not None
    assert d.disclosure_year == 2022


def test_disclosure_missing_year():
    book = FuelMixDisclosureBook()
    assert book.disclosure_for_year(2099) is None


def test_fully_matched_years():
    book = FuelMixDisclosureBook()
    book.record_disclosure(2022, 10000.0, [(FuelSource.WIND_ONSHORE, 1.0)], 10000)
    book.record_disclosure(2021, 10000.0, [(FuelSource.WIND_ONSHORE, 1.0)], 5000)
    assert 2022 in book.fully_matched_years
    assert 2021 not in book.fully_matched_years


def test_carbon_trend_sorted():
    book = FuelMixDisclosureBook()
    book.record_disclosure(2022, 10000.0, [(FuelSource.GAS_CCGT, 1.0)], 0)
    book.record_disclosure(2020, 10000.0, [(FuelSource.WIND_ONSHORE, 1.0)], 10000)
    trend = book.carbon_trend()
    assert list(trend.keys()) == [2020, 2022]
    assert trend[2022] > trend[2020]


def test_fmd_summary_non_empty():
    book = FuelMixDisclosureBook()
    book.record_disclosure(2022, 10000.0, [(FuelSource.WIND_ONSHORE, 1.0)], 10000)
    s = book.fmd_summary()
    assert "2022" in s


def test_fmd_summary_empty():
    book = FuelMixDisclosureBook()
    s = book.fmd_summary()
    assert "no disclosures" in s
