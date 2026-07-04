"""Tests for company/crm/market_conditions.py -- Phase QB."""
import pytest

from company.crm.market_conditions import (
    DEFAULT_MULTIPLIER,
    MARKET_SWITCHING_MULTIPLIER_BY_YEAR,
    market_conditions_multiplier,
)


def test_none_year_returns_default():
    assert market_conditions_multiplier(None) == pytest.approx(DEFAULT_MULTIPLIER)


def test_unlisted_year_returns_default():
    assert market_conditions_multiplier(1999) == pytest.approx(DEFAULT_MULTIPLIER)


def test_2024_is_calibration_baseline():
    assert market_conditions_multiplier(2024) == pytest.approx(1.00)


def test_2022_crisis_below_one():
    assert market_conditions_multiplier(2022) < 1.0


def test_2016_peak_competition_above_one():
    assert market_conditions_multiplier(2016) > 1.0


def test_all_listed_years_positive():
    for year, multiplier in MARKET_SWITCHING_MULTIPLIER_BY_YEAR.items():
        assert multiplier > 0.0
