"""Phase CL: Fuel Mix Disclosure Book tests (SLC 21C / REGO)."""
import pytest
from company.regulatory.fuel_mix_disclosure import (
    FuelMixDisclosureBook, FuelMixDisclosure, FuelMixComponent,
    FuelSource
)


def _book() -> FuelMixDisclosureBook:
    b = FuelMixDisclosureBook()
    b.record_disclosure(
        2022, 50_000,
        [(FuelSource.WIND_ONSHORE, 0.30), (FuelSource.GAS_CCGT, 0.60), (FuelSource.NUCLEAR, 0.10)],
        rego_certificates_held=15_000,  # 30% of supply backed by REGOs
    )
    return b


def _green_book() -> FuelMixDisclosureBook:
    b = FuelMixDisclosureBook()
    b.record_disclosure(
        2023, 10_000,
        [(FuelSource.WIND_OFFSHORE, 0.80), (FuelSource.SOLAR, 0.20)],
        rego_certificates_held=10_000,  # 100% REGO matched
    )
    return b


# 1. Renewable fraction calculated correctly
def test_renewable_fraction():
    b = _book()
    d = b.disclosure_for_year(2022)
    assert abs(d.renewable_fraction - 0.30) < 0.001


# 2. Carbon intensity weighted average
def test_carbon_intensity():
    b = _book()
    d = b.disclosure_for_year(2022)
    # 0.30 × 7.0 (wind) + 0.60 × 394.0 (gas) + 0.10 × 12.0 (nuclear) = 2.1 + 236.4 + 1.2 = 239.7
    expected = 0.30 * 7.0 + 0.60 * 394.0 + 0.10 * 12.0
    assert abs(d.carbon_intensity_gco2_per_kwh - expected) < 0.1


# 3. REGO coverage fraction
def test_rego_coverage_fraction():
    b = _book()
    d = b.disclosure_for_year(2022)
    # 15,000 REGOs / 50,000 MWh = 0.30
    assert abs(d.rego_coverage_fraction - 0.30) < 0.001


# 4. Not fully REGO matched at 30%
def test_not_fully_rego_matched():
    b = _book()
    d = b.disclosure_for_year(2022)
    assert not d.is_fully_rego_matched


# 5. Fully REGO matched at 100%
def test_fully_rego_matched():
    b = _green_book()
    d = b.disclosure_for_year(2023)
    assert d.is_fully_rego_matched


# 6. Unmatched volume = total - REGOs
def test_unmatched_volume():
    b = _book()
    d = b.disclosure_for_year(2022)
    assert abs(d.unmatched_volume_mwh - 35_000) < 0.1  # 50k - 15k


# 7. Unmatched volume = 0 when fully matched
def test_unmatched_zero_when_fully_matched():
    b = _green_book()
    d = b.disclosure_for_year(2023)
    assert d.unmatched_volume_mwh == 0.0


# 8. fully_matched_years filters correctly
def test_fully_matched_years():
    b = FuelMixDisclosureBook()
    b.record_disclosure(2021, 10_000, [(FuelSource.GAS_CCGT, 1.0)], 5_000)  # partial
    b.record_disclosure(2022, 10_000, [(FuelSource.WIND_ONSHORE, 1.0)], 10_000)  # full
    assert 2022 in b.fully_matched_years
    assert 2021 not in b.fully_matched_years


# 9. latest_disclosure returns most recent
def test_latest_disclosure():
    b = FuelMixDisclosureBook()
    b.record_disclosure(2020, 1_000, [(FuelSource.GAS_CCGT, 1.0)], 0)
    b.record_disclosure(2022, 2_000, [(FuelSource.WIND_ONSHORE, 1.0)], 2_000)
    assert b.latest_disclosure.disclosure_year == 2022


# 10. carbon_trend returns dict by year
def test_carbon_trend():
    b = FuelMixDisclosureBook()
    b.record_disclosure(2021, 1_000, [(FuelSource.GAS_CCGT, 1.0)], 0)
    b.record_disclosure(2022, 1_000, [(FuelSource.WIND_ONSHORE, 1.0)], 1_000)
    trend = b.carbon_trend()
    assert trend[2022] < trend[2021]   # wind << gas


# 11. wind is renewable, gas is not
def test_is_renewable_flags():
    wind = FuelMixComponent(FuelSource.WIND_ONSHORE, 0.5)
    gas = FuelMixComponent(FuelSource.GAS_CCGT, 0.5)
    assert wind.is_renewable
    assert not gas.is_renewable


# 12. fmd_summary contains key fields
def test_fmd_summary():
    b = _book()
    summary = b.fmd_summary()
    assert "Fuel Mix" in summary
    assert "SLC 21C" in summary
    assert "30.0%" in summary   # REGO coverage or renewable fraction


# --- Phase MB depth tests ---

def test_source_stored():
    c = FuelMixComponent(source=FuelSource.WIND_ONSHORE, fraction=0.5)
    assert c.source == FuelSource.WIND_ONSHORE


def test_fraction_stored():
    c = FuelMixComponent(source=FuelSource.SOLAR, fraction=0.25)
    assert c.fraction == pytest.approx(0.25)


def test_carbon_intensity_wind_onshore():
    c = FuelMixComponent(source=FuelSource.WIND_ONSHORE, fraction=1.0)
    assert c.carbon_intensity_gco2_per_kwh == pytest.approx(7.0)


def test_is_renewable_wind_true():
    c = FuelMixComponent(source=FuelSource.WIND_OFFSHORE, fraction=1.0)
    assert c.is_renewable is True


def test_is_renewable_gas_false():
    c = FuelMixComponent(source=FuelSource.GAS_CCGT, fraction=1.0)
    assert c.is_renewable is False


def test_weighted_carbon_computed():
    c = FuelMixComponent(source=FuelSource.GAS_CCGT, fraction=0.5)
    assert c.weighted_carbon == pytest.approx(0.5 * 394.0)


def test_disclosure_year_stored():
    b = _book()
    d = b.latest_disclosure
    assert d.disclosure_year == 2022


def test_total_supply_mwh_stored():
    b = _book()
    d = b.latest_disclosure
    assert d.total_supply_mwh == pytest.approx(50_000)


def test_rego_certificates_held_stored():
    b = _book()
    d = b.latest_disclosure
    assert d.rego_certificates_held == 15_000


def test_fuel_source_has_11_members():
    assert len(list(FuelSource)) == 11
