"""Tests for sim/forward_curve.py — term-structure forward price model.

Phase 41-prep: model reformed from (SMA + pstdev × risk_factor) to
    forward = spot_ewma × seasonal_shape × (1 + term_premium)
Tests updated to reflect the new formula and its structural properties.
"""
import statistics
from datetime import date, timedelta
from math import sqrt

import pytest

from sim.forward_curve import (
    BASE_TERM_PREMIUM,
    DEFAULT_RISK_FACTOR,
    EWMA_HALF_LIFE_DAYS,
    GAS_BASE_TERM_PREMIUM,
    GAS_MONTH_SEASONAL_MULTIPLIER,
    MONTH_SEASONAL_MULTIPLIER,
    SUMMER_MULTIPLIER,
    WINTER_MULTIPLIER,
    _ewma,
    _seasonal_shape,
    generate_forward_price,
)
from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER


def _records(start_date: str, end_date: str, price_pattern=None):
    """Daily price records (one per day, flat or patterned)."""
    if price_pattern is None:
        price_pattern = [50.0]
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    idx = 0
    while current <= end:
        records.append({
            "settlementDate": current.isoformat(),
            "systemSellPrice": price_pattern[idx % len(price_pattern)],
        })
        current += timedelta(days=1)
        idx += 1
    return records


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

def test_ewma_flat_series_returns_constant():
    """EWMA of a constant series equals the constant."""
    means = [50.0] * 60
    assert _ewma(means, half_life=30) == pytest.approx(50.0)


def test_ewma_recent_value_weighted_higher():
    """EWMA weights recent values more: rising series → result > SMA."""
    means = list(range(1, 61))  # 1, 2, …, 60
    ewma_val = _ewma(means, half_life=30)
    sma_val = statistics.mean(means)
    assert ewma_val > sma_val


def test_seasonal_shape_annual_contract_near_flat():
    """12-month seasonal shape ≈ 1.0 regardless of start month."""
    for start_month in range(1, 13):
        shape = _seasonal_shape(start_month, 12)
        assert abs(shape - 1.0) < 0.01, f"Month {start_month}: seasonal={shape:.4f}"


def test_seasonal_shape_winter_above_summer():
    """3-month winter delivery is more expensive than 3-month summer delivery."""
    winter = _seasonal_shape(1, 3)   # Jan–Mar
    summer = _seasonal_shape(6, 3)   # Jun–Aug
    assert winter > summer


def test_winter_multiplier_above_summer_multiplier():
    """Derived aggregates: winter mean > summer mean."""
    assert WINTER_MULTIPLIER > SUMMER_MULTIPLIER


# ---------------------------------------------------------------------------
# generate_forward_price — structural properties
# ---------------------------------------------------------------------------

def test_forward_price_above_spot_flat_series():
    """Flat spot → forward = spot × seasonal × (1 + term_premium).

    Jan-start, 12-month contract:
      seasonal ≈ 1.002; term_premium = BASE × sqrt(1) × (1.2/1.2) = BASE.
    """
    acquisition_date = "2023-01-15"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    seasonal = _seasonal_shape(1, 12)
    term_prem = BASE_TERM_PREMIUM * sqrt(1.0) * (1.2 / DEFAULT_RISK_FACTOR)
    expected = 50.0 * seasonal * (1.0 + term_prem)

    result = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)

    assert result == pytest.approx(expected)
    assert result > 50.0


def test_risk_factor_increases_forward_price():
    """Higher risk_factor → higher term premium → higher forward price."""
    acquisition_date = "2023-07-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[45.0, 55.0] * 45)

    fwd_low = generate_forward_price(acquisition_date, records, contract_length_months=6, risk_factor=1.0)
    fwd_high = generate_forward_price(acquisition_date, records, contract_length_months=6, risk_factor=2.0)

    assert fwd_high > fwd_low


def test_longer_tenor_higher_forward_price():
    """2-year contract has higher forward price than 6-month (sqrt-tenor premium)."""
    acquisition_date = "2023-04-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[60.0])

    fwd_6m = generate_forward_price(acquisition_date, records, contract_length_months=6)
    fwd_24m = generate_forward_price(acquisition_date, records, contract_length_months=24)

    assert fwd_24m > fwd_6m


def test_cold_spell_lookback_temps_increase_forward_price():
    """Cold-spell weather premium multiplies the base forward price."""
    acquisition_date = "2023-01-15"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    no_weather = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)
    with_weather = generate_forward_price(
        acquisition_date, records, contract_length_months=12, risk_factor=1.2,
        lookback_daily_mean_temps_c=[0.0] * 90,
    )

    assert with_weather == pytest.approx(no_weather * COLD_SPELL_PRICE_MULTIPLIER)


def test_mild_lookback_temps_do_not_change_forward_price():
    """Mild temperatures (above threshold) apply no weather adjustment."""
    acquisition_date = "2023-01-15"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    no_weather = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)
    with_weather = generate_forward_price(
        acquisition_date, records, contract_length_months=12, risk_factor=1.2,
        lookback_daily_mean_temps_c=[10.0] * 90,
    )

    assert with_weather == pytest.approx(no_weather)


def test_intraday_spread_does_not_affect_forward_price():
    """Records with identical daily means but different intraday spread give same result.

    The model aggregates to daily means before computing EWMA — intraday
    spread (e.g., £20 overnight / £80 peak) is not forward price uncertainty.
    """
    acquisition_date = "2023-07-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    flat_records = _records(start_lb, end_lb, price_pattern=[50.0])

    intraday_records = []
    current = date.fromisoformat(start_lb)
    end = date.fromisoformat(end_lb)
    while current <= end:
        for price in (20.0, 80.0):
            intraday_records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)

    flat_price = generate_forward_price(acquisition_date, flat_records, contract_length_months=6, risk_factor=1.2)
    intraday_price = generate_forward_price(acquisition_date, intraday_records, contract_length_months=6, risk_factor=1.2)

    assert intraday_price == pytest.approx(flat_price)


def test_forward_curve_is_pit_safe():
    """Records after acquisition_date do not affect the forward price."""
    acquisition_date = "2023-04-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    pre_records = _records(start_lb, end_lb, price_pattern=[45.0])
    post_records = _records(
        acquisition_date,
        (date.fromisoformat(acquisition_date) + timedelta(days=180)).isoformat(),
        price_pattern=[200.0],
    )

    fwd_with_future = generate_forward_price(
        acquisition_date, pre_records + post_records, contract_length_months=6, risk_factor=1.5
    )
    fwd_without_future = generate_forward_price(
        acquisition_date, pre_records, contract_length_months=6, risk_factor=1.5
    )

    assert fwd_with_future == pytest.approx(fwd_without_future)


def test_rising_spot_increases_forward_estimate():
    """EWMA is higher for a rising spot series than a flat one with the same mean."""
    acquisition_date = "2023-10-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    flat_records = _records(start_lb, end_lb, price_pattern=[60.0])
    # Rising: first 45 days at £40, last 45 days at £80 (same arithmetic mean = £60)
    rising_records = _records(start_lb, end_lb, price_pattern=[40.0] * 45 + [80.0] * 45)

    fwd_flat = generate_forward_price(acquisition_date, flat_records)
    fwd_rising = generate_forward_price(acquisition_date, rising_records)

    assert fwd_rising > fwd_flat


def test_no_records_raises_value_error():
    """ValueError when no records exist within the lookback window."""
    with pytest.raises(ValueError, match="No price records found"):
        generate_forward_price("2023-01-01", [], lookback_days=90)


def test_month_seasonal_multiplier_all_12_months_defined():
    """All 12 calendar months have a seasonal multiplier defined."""
    assert set(MONTH_SEASONAL_MULTIPLIER.keys()) == set(range(1, 13))


# ---------------------------------------------------------------------------
# Phase 42: gas-specific seasonal calibration
# ---------------------------------------------------------------------------

def test_gas_month_seasonal_multiplier_all_12_months_defined():
    """All 12 calendar months have a gas seasonal multiplier defined."""
    assert set(GAS_MONTH_SEASONAL_MULTIPLIER.keys()) == set(range(1, 13))


def test_gas_seasonal_shape_annual_contract_near_flat():
    """Gas 12-month seasonal shape ≈ 1.0 regardless of start month."""
    for start_month in range(1, 13):
        shape = _seasonal_shape(start_month, 12, "gas")
        assert abs(shape - 1.0) < 0.05, f"Month {start_month}: gas seasonal={shape:.4f}"


def test_gas_winter_premium_steeper_than_electricity():
    """Gas Dec delivery carries a larger seasonal premium than electricity Dec.
    Empirical 2016-2024 data: gas Dec=1.294, elec Dec=1.257. Q1 inverted by crisis.
    """
    elec_dec = _seasonal_shape(12, 1)
    gas_dec = _seasonal_shape(12, 1, "gas")
    assert gas_dec > elec_dec, (
        f"Gas Dec premium ({gas_dec:.3f}) should exceed electricity ({elec_dec:.3f})"
    )


def test_gas_summer_discount_steeper_than_electricity():
    """Gas May delivery carries a larger seasonal discount than electricity May.
    Empirical 2016-2024: gas May=0.798, elec May=0.827. Jul-Sep inverted by 2021-22 crisis.
    """
    elec_may = _seasonal_shape(5, 1)
    gas_may = _seasonal_shape(5, 1, "gas")
    assert gas_may < elec_may, (
        f"Gas May discount ({gas_may:.3f}) should be deeper than electricity ({elec_may:.3f})"
    )


def test_gas_forward_price_lower_than_electricity_in_summer():
    """Gas forward in May delivery is lower than electricity (May is gas trough month).
    Empirical 2016-2024: gas May=0.798, elec May=0.827.
    """
    acquisition_date = "2023-05-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    fwd_elec = generate_forward_price(acquisition_date, records, contract_length_months=1)
    fwd_gas = generate_forward_price(acquisition_date, records, contract_length_months=1, fuel="gas")

    assert fwd_gas < fwd_elec, (
        f"Gas May forward ({fwd_gas:.2f}) should be lower than electricity ({fwd_elec:.2f})"
    )


def test_gas_forward_price_higher_than_electricity_in_winter():
    """Gas forward in December delivery is higher than electricity (Dec is gas peak month).
    Empirical 2016-2024: gas Dec=1.294, elec Dec=1.257.
    """
    acquisition_date = "2023-12-01"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    fwd_elec = generate_forward_price(acquisition_date, records, contract_length_months=1)
    fwd_gas = generate_forward_price(acquisition_date, records, contract_length_months=1, fuel="gas")

    assert fwd_gas > fwd_elec, (
        f"Gas Dec forward ({fwd_gas:.2f}) should exceed electricity ({fwd_elec:.2f})"
    )


def test_gas_base_term_premium_lower_than_electricity():
    """Gas base term premium is lower than electricity (more liquid forward market)."""
    assert GAS_BASE_TERM_PREMIUM < BASE_TERM_PREMIUM


def test_weather_premium_not_applied_to_gas():
    """Cold-spell weather premium does not apply to gas (fuel != 'electricity')."""
    acquisition_date = "2023-01-15"
    start_lb = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lb = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = _records(start_lb, end_lb, price_pattern=[50.0])

    gas_no_weather = generate_forward_price(acquisition_date, records, contract_length_months=12, fuel="gas")
    gas_with_temps = generate_forward_price(
        acquisition_date, records, contract_length_months=12, fuel="gas",
        lookback_daily_mean_temps_c=[0.0] * 90,
    )

    assert gas_no_weather == pytest.approx(gas_with_temps), (
        "Weather adjustment must not apply to gas forwards"
    )


def test_calibration_loaded_not_fallback():
    from sim.forward_curve import _ELEC_FALLBACK
    assert MONTH_SEASONAL_MULTIPLIER is not _ELEC_FALLBACK
    assert MONTH_SEASONAL_MULTIPLIER != _ELEC_FALLBACK

def test_calibration_elec_dec_empirical():
    assert MONTH_SEASONAL_MULTIPLIER[12] == pytest.approx(1.257, abs=0.01)

def test_calibration_gas_dec_empirical():
    assert GAS_MONTH_SEASONAL_MULTIPLIER[12] == pytest.approx(1.294, abs=0.01)

def test_calibration_gas_may_trough():
    gas_may = GAS_MONTH_SEASONAL_MULTIPLIER[5]
    assert gas_may == pytest.approx(0.798, abs=0.01)
    for m in range(1, 13):
        assert GAS_MONTH_SEASONAL_MULTIPLIER[m] >= gas_may

def test_calibration_elec_annual_mean_near_unity():
    mean_val = statistics.mean(MONTH_SEASONAL_MULTIPLIER.values())
    assert abs(mean_val - 1.0) < 0.02

def test_calibration_gas_annual_mean_near_unity():
    mean_val = statistics.mean(GAS_MONTH_SEASONAL_MULTIPLIER.values())
    assert abs(mean_val - 1.0) < 0.02

def test_calibration_q4_peak_both_fuels():
    for m in (11, 12):
        assert MONTH_SEASONAL_MULTIPLIER[m] > 1.0
        assert GAS_MONTH_SEASONAL_MULTIPLIER[m] > 1.0

def test_calibration_spring_trough_both_fuels():
    for m in (5, 6):
        assert MONTH_SEASONAL_MULTIPLIER[m] < 1.0
        assert GAS_MONTH_SEASONAL_MULTIPLIER[m] < 1.0

def test_calibration_all_multipliers_positive():
    for m, v in MONTH_SEASONAL_MULTIPLIER.items():
        assert v > 0
    for m, v in GAS_MONTH_SEASONAL_MULTIPLIER.items():
        assert v > 0

def test_calibration_dec_is_peak_for_gas():
    assert GAS_MONTH_SEASONAL_MULTIPLIER[12] == max(GAS_MONTH_SEASONAL_MULTIPLIER.values())

def test_calibration_dec_is_peak_for_electricity():
    assert MONTH_SEASONAL_MULTIPLIER[12] == max(MONTH_SEASONAL_MULTIPLIER.values())

def test_calibration_file_valid_structure():
    from sim.forward_curve import _CALIBRATION_PATH
    assert _CALIBRATION_PATH.exists()
    import json
    with open(_CALIBRATION_PATH) as f:
        cal = json.load(f)
    assert 'electricity_n2ex' in cal
    assert 'gas_nbp' in cal
    assert 'multipliers' in cal['electricity_n2ex']
    assert 'multipliers' in cal['gas_nbp']
    assert len(cal['electricity_n2ex']['multipliers']) == 12
    assert len(cal['gas_nbp']['multipliers']) == 12

def test_load_calibration_returns_twelve_month_dicts():
    from sim.forward_curve import _load_calibration
    cal_e, cal_g = _load_calibration()
    assert cal_e is not None
    assert cal_g is not None
    assert len(cal_e) == 12
    assert len(cal_g) == 12

def test_calibration_elec_annual_avgs_cover_2016_to_2024():
    from sim.forward_curve import _CALIBRATION_PATH
    import json
    with open(_CALIBRATION_PATH) as f:
        cal = json.load(f)
    avgs = cal['electricity_n2ex']['annual_averages_gbp_mwh']
    for y in range(2016, 2025):
        assert str(y) in avgs

def test_calibration_crisis_years_reflected_in_gas():
    from sim.forward_curve import _CALIBRATION_PATH
    import json
    with open(_CALIBRATION_PATH) as f:
        cal = json.load(f)
    avgs = cal['gas_nbp']['annual_averages_gbp_mwh']
    assert avgs['2022'] > avgs['2016'] * 5

def test_calibration_elec_2022_exceeds_2019():
    from sim.forward_curve import _CALIBRATION_PATH
    import json
    with open(_CALIBRATION_PATH) as f:
        cal = json.load(f)
    avgs = cal['electricity_n2ex']['annual_averages_gbp_mwh']
    assert avgs['2022'] > avgs['2019'] * 3
