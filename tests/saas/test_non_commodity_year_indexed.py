"""Phase 78 tests: year-indexed non-commodity billing rates."""
import pytest
from saas.non_commodity import (
    non_commodity_rate,
    _NON_COMMODITY_ELEC_RESI_BY_YEAR,
    _NON_COMMODITY_GAS_RESI_BY_YEAR,
    _SME_ELEC_MULTIPLIER,
    _SME_GAS_MULTIPLIER,
)
from saas.bill_generator import generate_bill


# ---------------------------------------------------------------------------
# non_commodity_rate: electricity
# ---------------------------------------------------------------------------

def test_elec_resi_2016_rate():
    assert non_commodity_rate("electricity", "resi", year=2016) == 52.0


def test_elec_resi_2022_crisis_rate():
    # Crisis year: network charges spiked to 73 £/MWh vs 55 flat baseline
    assert non_commodity_rate("electricity", "resi", year=2022) == 73.0


def test_elec_resi_2023_peak_rate():
    assert non_commodity_rate("electricity", "resi", year=2023) == 80.0


def test_elec_resi_2024_rate():
    assert non_commodity_rate("electricity", "resi", year=2024) == 74.0


def test_elec_sme_2022_rate_applies_multiplier():
    expected = 73.0 * _SME_ELEC_MULTIPLIER
    assert non_commodity_rate("electricity", "SME", year=2022) == pytest.approx(expected)


def test_elec_no_year_returns_flat_baseline():
    # Backward compat: year=None → flat 2019 constants
    assert non_commodity_rate("electricity", "resi") == 55.0
    assert non_commodity_rate("electricity", "SME") == 42.0


def test_elec_2019_year_matches_flat_resi_baseline():
    # 2019 is in the indexed table and equals the flat baseline
    assert non_commodity_rate("electricity", "resi", year=2019) == 55.0


# ---------------------------------------------------------------------------
# non_commodity_rate: gas
# ---------------------------------------------------------------------------

def test_gas_resi_2022_crisis_rate():
    assert non_commodity_rate("gas", "resi", year=2022) == 15.0


def test_gas_sme_2022_rate_applies_multiplier():
    expected = 15.0 * _SME_GAS_MULTIPLIER
    assert non_commodity_rate("gas", "SME", year=2022) == pytest.approx(expected)


def test_gas_no_year_returns_flat_baseline():
    assert non_commodity_rate("gas", "resi") == 10.0
    assert non_commodity_rate("gas", "SME") == 8.0


def test_gas_resi_2016_rate():
    assert non_commodity_rate("gas", "resi", year=2016) == 9.0


# ---------------------------------------------------------------------------
# bill_generator: year extracted from dates
# ---------------------------------------------------------------------------

def _make_records(date_prefix: str, count: int = 30, kwh: float = 10.0) -> list[dict]:
    """Make minimal settlement records for one calendar month."""
    return [
        {
            "settlement_date": f"{date_prefix}-{i+1:02d}",
            "consumption_kwh": kwh,
            "revenue_gbp": kwh * 0.2,  # 20p/kWh flat
        }
        for i in range(count)
    ]


def test_bill_2022_has_higher_non_commodity_than_2019():
    records_2022 = _make_records("2022-06", count=30, kwh=10.0)
    records_2019 = _make_records("2019-06", count=30, kwh=10.0)

    bill_2022 = generate_bill("C1", records_2022, "fixed_1yr", segment="resi", commodity="electricity")
    bill_2019 = generate_bill("C1", records_2019, "fixed_1yr", segment="resi", commodity="electricity")

    # 2022 rate=73, 2019 rate=55: non-commodity must be higher in 2022
    assert bill_2022["non_commodity_amount_gbp"] > bill_2019["non_commodity_amount_gbp"]


def test_bill_2022_non_commodity_correct_value():
    # 30 days × 10 kWh = 300 kWh = 0.3 MWh; 73 £/MWh → £21.90
    records = _make_records("2022-06", count=30, kwh=10.0)
    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")
    assert bill["non_commodity_amount_gbp"] == pytest.approx(0.3 * 73.0)


def test_bill_2016_non_commodity_correct_value():
    # 0.3 MWh × 52 £/MWh = £15.60
    records = _make_records("2016-06", count=30, kwh=10.0)
    bill = generate_bill("C1", records, "fixed_1yr", segment="resi", commodity="electricity")
    assert bill["non_commodity_amount_gbp"] == pytest.approx(0.3 * 52.0)
