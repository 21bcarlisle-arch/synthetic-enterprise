"""Tests for BSC credit cover working capital model (Phase 53)."""

import pytest
from saas.capital.bsc_credit import (
    CREDIT_BUFFER_MULTIPLIER,
    CREDIT_WINDOW_DAYS,
    compute_bsc_credit_by_year,
    compute_bsc_credit_requirement,
    compute_daily_wholesale_exposure,
)


def _rec(date: str, cost: float, commodity: str = "electricity") -> dict:
    return {"settlement_date": date, "wholesale_cost_gbp": cost, "commodity": commodity}


class TestComputeDailyWholesaleExposure:
    def test_aggregates_same_date(self):
        records = [_rec("2022-01-15", 100.0), _rec("2022-01-15", 50.0)]
        result = compute_daily_wholesale_exposure(records)
        assert result["2022-01-15"] == pytest.approx(150.0)

    def test_separates_different_dates(self):
        records = [_rec("2022-01-15", 100.0), _rec("2022-01-16", 200.0)]
        result = compute_daily_wholesale_exposure(records)
        assert len(result) == 2
        assert result["2022-01-16"] == pytest.approx(200.0)

    def test_excludes_gas_records(self):
        records = [_rec("2022-01-15", 100.0, "electricity"), _rec("2022-01-15", 999.0, "gas")]
        result = compute_daily_wholesale_exposure(records)
        assert result["2022-01-15"] == pytest.approx(100.0)

    def test_empty_records_returns_empty(self):
        assert compute_daily_wholesale_exposure([]) == {}

    def test_date_key_uses_iso_prefix(self):
        records = [_rec("2022-01-15T16:00:00", 50.0)]
        result = compute_daily_wholesale_exposure(records)
        assert "2022-01-15" in result


class TestComputeBscCreditRequirement:
    def test_returns_peak_times_buffer(self):
        daily = {"2022-01-01": 1000.0, "2022-01-02": 500.0, "2022-01-03": 800.0}
        result = compute_bsc_credit_requirement(daily)
        assert result == pytest.approx(1000.0 * CREDIT_BUFFER_MULTIPLIER)

    def test_empty_exposure_returns_zero(self):
        assert compute_bsc_credit_requirement({}) == 0.0

    def test_custom_buffer(self):
        daily = {"2022-01-01": 1000.0}
        result = compute_bsc_credit_requirement(daily, buffer=1.5)
        assert result == pytest.approx(1500.0)

    def test_single_day(self):
        daily = {"2022-01-01": 250.0}
        result = compute_bsc_credit_requirement(daily)
        assert result == pytest.approx(250.0 * 1.2)


class TestComputeBscCreditByYear:
    def test_groups_by_year(self):
        records = [
            _rec("2020-06-15", 500.0),
            _rec("2021-01-01", 1000.0),
            _rec("2021-06-01", 800.0),
        ]
        result = compute_bsc_credit_by_year(records)
        assert "2020" in result
        assert "2021" in result

    def test_crisis_year_has_higher_peak(self):
        records = [
            _rec("2016-01-01", 100.0),
            _rec("2022-01-01", 2000.0),
        ]
        result = compute_bsc_credit_by_year(records)
        assert result["2022"]["peak_daily_wholesale_gbp"] > result["2016"]["peak_daily_wholesale_gbp"]

    def test_credit_cover_is_peak_times_buffer(self):
        records = [_rec("2021-01-01", 600.0), _rec("2021-01-02", 400.0)]
        result = compute_bsc_credit_by_year(records)
        assert result["2021"]["credit_cover_required_gbp"] == pytest.approx(600.0 * CREDIT_BUFFER_MULTIPLIER)

    def test_gas_records_excluded_from_bsc(self):
        records = [_rec("2022-01-01", 100.0, "electricity"), _rec("2022-01-01", 9999.0, "gas")]
        result = compute_bsc_credit_by_year(records)
        assert result["2022"]["peak_daily_wholesale_gbp"] == pytest.approx(100.0)

    def test_empty_returns_empty(self):
        assert compute_bsc_credit_by_year([]) == {}
