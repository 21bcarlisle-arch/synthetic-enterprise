from datetime import date, timedelta

import pytest

from sim.forward_curve import SUMMER_MULTIPLIER, WINTER_MULTIPLIER, generate_forward_price
from sim.weather_price_sensitivity import COLD_SPELL_PRICE_MULTIPLIER


def create_records(start_date: str, end_date: str, price_pattern=None):
    if price_pattern is None:
        price_pattern = [50.0] * 90  # Default to a flat price pattern of £50/MWh

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []

    current_date = start
    price_index = 0

    while current_date <= end:
        record = {
            "settlementDate": current_date.isoformat(),
            "systemSellPrice": price_pattern[price_index % len(price_pattern)],
        }
        records.append(record)
        current_date += timedelta(days=1)
        price_index += 1

    return records


def test_forward_price_above_spot_in_winter():
    acquisition_date = "2023-01-15"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    records = create_records(start_lookback_date, end_lookback_date, price_pattern=[50.0] * 90)

    expected_seasonal_multiplier = (WINTER_MULTIPLIER * 6 + SUMMER_MULTIPLIER * 6) / 12
    expected_forward_price = 50.0 * expected_seasonal_multiplier

    forward_price = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)

    assert forward_price == pytest.approx(expected_forward_price)
    assert forward_price > 50.0


def test_risk_factor_increases_forward_price():
    acquisition_date = "2023-07-01"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    records = create_records(start_lookback_date, end_lookback_date, price_pattern=[45.0, 55.0] * 45)

    forward_price_risk_1_0 = generate_forward_price(acquisition_date, records, contract_length_months=6, risk_factor=1.0)
    forward_price_risk_2_0 = generate_forward_price(acquisition_date, records, contract_length_months=6, risk_factor=2.0)

    assert forward_price_risk_2_0 > forward_price_risk_1_0


def test_cold_spell_lookback_temps_increase_forward_price():
    acquisition_date = "2023-01-15"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = create_records(start_lookback_date, end_lookback_date, price_pattern=[50.0] * 90)

    no_weather = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)
    cold_lookback_temps = [0.0] * 90  # average HDD well above the cold-spell threshold
    with_weather = generate_forward_price(
        acquisition_date, records, contract_length_months=12, risk_factor=1.2,
        lookback_daily_mean_temps_c=cold_lookback_temps,
    )

    assert with_weather == pytest.approx(no_weather * COLD_SPELL_PRICE_MULTIPLIER)


def test_mild_lookback_temps_do_not_change_forward_price():
    acquisition_date = "2023-01-15"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()
    records = create_records(start_lookback_date, end_lookback_date, price_pattern=[50.0] * 90)

    no_weather = generate_forward_price(acquisition_date, records, contract_length_months=12, risk_factor=1.2)
    mild_lookback_temps = [10.0] * 90  # average HDD below the cold-spell threshold
    with_weather = generate_forward_price(
        acquisition_date, records, contract_length_months=12, risk_factor=1.2,
        lookback_daily_mean_temps_c=mild_lookback_temps,
    )

    assert with_weather == pytest.approx(no_weather)


def test_volatility_premium_uses_daily_mean_not_intraday_spread():
    """Half-hourly records with a large *intraday* peak/off-peak spread but
    an identical daily mean every day should produce the same forward price
    as flat £50/MWh records -- the volatility premium reflects day-to-day
    price uncertainty, not the normal intraday spread."""
    acquisition_date = "2023-07-01"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    flat_records = create_records(start_lookback_date, end_lookback_date, price_pattern=[50.0])

    # Every day has the same two half-hourly prices (£20 and £80), so the
    # daily mean is £50 every day -- zero day-to-day volatility -- despite a
    # large intraday spread.
    intraday_spread_records = []
    current_date = date.fromisoformat(start_lookback_date)
    end = date.fromisoformat(end_lookback_date)
    while current_date <= end:
        for price in (20.0, 80.0):
            intraday_spread_records.append(
                {"settlementDate": current_date.isoformat(), "systemSellPrice": price}
            )
        current_date += timedelta(days=1)

    flat_price = generate_forward_price(acquisition_date, flat_records, contract_length_months=6, risk_factor=1.2)
    intraday_price = generate_forward_price(
        acquisition_date, intraday_spread_records, contract_length_months=6, risk_factor=1.2
    )

    assert intraday_price == pytest.approx(flat_price)


def test_forward_curve_is_pit_safe():
    acquisition_date = "2023-04-01"
    start_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=90)).isoformat()
    end_lookback_date = (date.fromisoformat(acquisition_date) - timedelta(days=1)).isoformat()

    # Records before acquisition date
    records_before_acq = create_records(start_lookback_date, end_lookback_date, price_pattern=[45.0] * 90)

    # Records on/after acquisition date with much higher prices
    future_start_date = acquisition_date
    future_end_date = (date.fromisoformat(acquisition_date) + timedelta(days=180)).isoformat()
    records_after_acq = create_records(future_start_date, future_end_date, price_pattern=[200.0] * 180)

    # Combine records
    all_records = records_before_acq + records_after_acq

    forward_price_with_future_data = generate_forward_price(acquisition_date, all_records, contract_length_months=6, risk_factor=1.5)
    forward_price_without_future_data = generate_forward_price(acquisition_date, records_before_acq, contract_length_months=6, risk_factor=1.5)

    assert forward_price_with_future_data == pytest.approx(forward_price_without_future_data)
