"""Tests for Phase NZ: Ofgem FRA Regulatory Capital Ratio."""
import pytest
from saas.reporting.fra_capital_ratio import (
    FRACapitalRatio,
    build_fra_ratio_series,
    weakest_year,
    strongest_year,
    _rag,
    _FRA_GREEN_THRESHOLD,
    _FRA_AMBER_THRESHOLD,
    _FRA_RED_THRESHOLD,
)


def _make_ma(years_data):
    """Build management_accounts dict from list of (year, equity, revenue) tuples."""
    ma = {}
    for yr, equity, revenue in years_data:
        ma[str(yr)] = {
            "balance_sheet": {"total_equity_gbp": float(equity)},
            "income_statement": {"revenue_gbp": float(revenue)},
        }
    return ma


class TestRAGThresholds:
    def test_green_above_threshold(self):
        assert _rag(_FRA_GREEN_THRESHOLD + 1) == "GREEN"

    def test_green_at_threshold(self):
        assert _rag(_FRA_GREEN_THRESHOLD) == "GREEN"

    def test_amber_between_thresholds(self):
        mid = (_FRA_GREEN_THRESHOLD + _FRA_AMBER_THRESHOLD) / 2
        assert _rag(mid) == "AMBER"

    def test_red_below_amber(self):
        assert _rag(_FRA_AMBER_THRESHOLD - 0.1) == "RED"

    def test_red_at_minimum(self):
        assert _rag(1.0) == "RED"

    def test_red_below_minimum(self):
        assert _rag(0.5) == "RED"


class TestBuildFRARatioSeries:
    def test_empty_input_returns_empty(self):
        assert build_fra_ratio_series({}) == []

    def test_none_input_returns_empty(self):
        assert build_fra_ratio_series(None) == []

    def test_returns_one_record_per_year(self):
        ma = _make_ma([(2022, 5_000_000, 4_000_000), (2023, 6_000_000, 3_500_000)])
        result = build_fra_ratio_series(ma)
        assert len(result) == 2

    def test_sorted_by_year(self):
        ma = _make_ma([(2023, 6_000_000, 3_500_000), (2022, 5_000_000, 4_000_000)])
        result = build_fra_ratio_series(ma)
        assert result[0].year == 2022
        assert result[1].year == 2023

    def test_fra_ratio_formula(self):
        equity = 5_930_262.0
        revenue = 4_245_566.0
        ma = _make_ma([(2022, equity, revenue)])
        result = build_fra_ratio_series(ma)
        expected = equity / (revenue / 12)
        assert abs(result[0].fra_ratio - expected) < 0.1

    def test_monthly_revenue_is_annual_divided_by_12(self):
        ma = _make_ma([(2022, 5_000_000, 4_200_000)])
        result = build_fra_ratio_series(ma)
        assert abs(result[0].monthly_revenue_gbp - 350_000) < 0.01

    def test_compliant_when_ratio_above_1(self):
        ma = _make_ma([(2022, 5_000_000, 4_000_000)])
        result = build_fra_ratio_series(ma)
        assert result[0].is_compliant

    def test_non_compliant_when_ratio_below_1(self):
        ma = _make_ma([(2022, 100_000, 4_000_000)])
        result = build_fra_ratio_series(ma)
        assert not result[0].is_compliant

    def test_skip_year_with_zero_revenue(self):
        ma = _make_ma([(2022, 5_000_000, 0), (2023, 6_000_000, 3_500_000)])
        result = build_fra_ratio_series(ma)
        assert len(result) == 1
        assert result[0].year == 2023

    def test_rag_on_high_ratio_is_green(self):
        ma = _make_ma([(2022, 50_000_000, 4_000_000)])
        result = build_fra_ratio_series(ma)
        assert result[0].rag == "GREEN"

    def test_rag_on_low_ratio_is_red(self):
        ma = _make_ma([(2022, 200_000, 4_000_000)])
        result = build_fra_ratio_series(ma)
        assert result[0].rag == "RED"

    def test_record_is_frozen(self):
        ma = _make_ma([(2022, 5_000_000, 4_000_000)])
        r = build_fra_ratio_series(ma)[0]
        with pytest.raises(Exception):
            r.equity_gbp = 9_000_000


class TestWeakestStrongest:
    def test_weakest_returns_min_ratio(self):
        ma = _make_ma([(2020, 4_000_000, 1_800_000), (2022, 5_000_000, 4_200_000)])
        series = build_fra_ratio_series(ma)
        w = weakest_year(series)
        assert w.year == 2022

    def test_strongest_returns_max_ratio(self):
        ma = _make_ma([(2020, 4_000_000, 1_800_000), (2022, 5_000_000, 4_200_000)])
        series = build_fra_ratio_series(ma)
        s = strongest_year(series)
        assert s.year == 2020

    def test_weakest_empty_returns_none(self):
        assert weakest_year([]) is None

    def test_strongest_empty_returns_none(self):
        assert strongest_year([]) is None

    def test_crisis_2022_is_weakest(self):
        ma = _make_ma([
            (2020, 4_263_302, 1_857_096),
            (2021, 4_977_645, 2_421_344),
            (2022, 5_930_262, 4_245_566),
            (2023, 6_817_903, 3_495_762),
        ])
        series = build_fra_ratio_series(ma)
        w = weakest_year(series)
        assert w.year == 2022

    def test_ratio_label_format(self):
        ma = _make_ma([(2022, 5_000_000, 4_000_000)])
        r = build_fra_ratio_series(ma)[0]
        assert r.ratio_label.endswith("x")
