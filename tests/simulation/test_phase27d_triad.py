"""Phase 27d: Triad risk tracking for I&C electricity customers."""
import pytest
from simulation.triad import (
    _MIN_TRIAD_SEPARATION_DAYS,
    _N_TRIADS,
    _TRIAD_WINDOW_MONTHS,
    _triad_year,
    compute_triad_exposure,
    get_tnuos_tariff,
    identify_triad_candidates,
)


def test_triad_window_is_nov_to_feb():
    assert _TRIAD_WINDOW_MONTHS == {11, 12, 1, 2}


def test_n_triads_is_three():
    assert _N_TRIADS == 3


def test_min_separation_is_ten_days():
    assert _MIN_TRIAD_SEPARATION_DAYS == 10


def test_triad_year_november():
    """November 2021 is in winter 2021-22 → triad_year 2021."""
    assert _triad_year("2021-11-15") == 2021


def test_triad_year_january():
    """January 2022 is in winter 2021-22 → triad_year 2021."""
    assert _triad_year("2022-01-15") == 2021


def test_triad_year_february():
    """February 2022 is in winter 2021-22 → triad_year 2021."""
    assert _triad_year("2022-02-28") == 2021


def test_tnuos_tariff_2021():
    assert get_tnuos_tariff(2021) == pytest.approx(56.41)


def test_tnuos_tariff_clamps_to_max():
    assert get_tnuos_tariff(2030) == get_tnuos_tariff(2024)


def _make_price_records(dates_ssp: list[tuple[str, float]]) -> list[dict]:
    """Build price records at SP=1 for each (date, ssp) pair."""
    return [
        {"settlementDate": d, "settlementPeriod": 1, "systemSellPrice": ssp}
        for d, ssp in dates_ssp
    ]


def test_identify_triad_candidates_selects_3_highest():
    """Three highest SSP periods (≥10 days apart) in Nov-Feb are selected."""
    records = _make_price_records([
        ("2021-11-01", 400.0),
        ("2021-11-15", 600.0),
        ("2021-12-01", 500.0),
        ("2022-01-10", 300.0),
        ("2022-02-01", 200.0),
    ])
    triads = identify_triad_candidates(records, triad_year=2021)
    assert len(triads) == 3
    prices = [t["systemSellPrice"] for t in triads]
    assert 600.0 in prices
    assert 500.0 in prices
    assert 400.0 in prices


def test_identify_triad_candidates_enforces_separation():
    """Two high-SSP periods within 10 days → only the highest selected from that pair."""
    records = _make_price_records([
        ("2021-11-01", 900.0),
        ("2021-11-05", 800.0),  # within 10 days of 11-01 → excluded
        ("2021-12-01", 500.0),
        ("2022-01-15", 400.0),
        ("2022-02-01", 200.0),
    ])
    triads = identify_triad_candidates(records, triad_year=2021)
    assert len(triads) == 3
    prices = {t["systemSellPrice"] for t in triads}
    assert 900.0 in prices
    assert 800.0 not in prices  # excluded by separation rule


def test_identify_triad_candidates_empty_when_no_window_data():
    records = _make_price_records([
        ("2021-06-01", 400.0),
        ("2021-07-15", 600.0),
    ])
    triads = identify_triad_candidates(records, triad_year=2021)
    assert triads == []


def test_compute_triad_exposure_calculates_tnuos():
    """Triad exposure: avg demand × TNUoS tariff."""
    triad_periods = [
        {"settlementDate": "2021-11-15", "settlementPeriod": 1, "systemSellPrice": 600.0},
        {"settlementDate": "2021-12-01", "settlementPeriod": 1, "systemSellPrice": 500.0},
        {"settlementDate": "2022-01-10", "settlementPeriod": 1, "systemSellPrice": 400.0},
    ]
    # Customer consumed 100 kWh at each Triad period → 200 kW demand
    settlement_records = [
        {"customer_id": "C_IC1", "settlement_date": "2021-11-15", "settlement_period": 1, "consumption_kwh": 100.0},
        {"customer_id": "C_IC1", "settlement_date": "2021-12-01", "settlement_period": 1, "consumption_kwh": 100.0},
        {"customer_id": "C_IC1", "settlement_date": "2022-01-10", "settlement_period": 1, "consumption_kwh": 100.0},
    ]
    result = compute_triad_exposure("C_IC1", triad_periods, settlement_records, triad_year=2021)
    assert result["customer_id"] == "C_IC1"
    assert result["avg_triad_kw"] == pytest.approx(200.0)  # 100 kWh × 2 = 200 kW
    # 200 kW × £56.41/kW = £11,282
    assert result["estimated_tnuos_gbp"] == pytest.approx(200.0 * 56.41, rel=1e-4)
    assert len(result["triad_periods"]) == 3
