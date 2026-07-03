"""Tests for Phase NX: I&C Demand Response Enrollment."""
import pytest
from company.market.ic_flexibility_revenue import (
    ICFlexibilityRevenueBook,
    ICFlexibilityRecord,
    _peak_demand_kw,
    _flex_kw,
    _gross_cm_revenue,
    _gross_dfs_revenue,
    _IC_LOAD_FACTOR,
    _IC_DSR_FRACTION,
    _AGGREGATOR_FEE_PCT,
    _IC_MIN_EAC_KWH,
    _DFS_LAUNCH_YEAR,
    _CM_DELIVERY_GBP_PER_KW_YR,
)


class TestPeakDemandEstimate:
    def test_peak_demand_formula(self):
        eac = 4_000_000.0  # 4 GWh
        expected = eac / (8760.0 * _IC_LOAD_FACTOR)
        assert abs(_peak_demand_kw(eac) - expected) < 0.01

    def test_1gwh_customer(self):
        # 1 GWh / (8760 * 0.65) ≈ 175.7 kW
        pk = _peak_demand_kw(1_000_000.0)
        assert 170 < pk < 180

    def test_4gwh_customer(self):
        pk = _peak_demand_kw(4_000_000.0)
        assert 690 < pk < 720


class TestFlexKw:
    def test_flex_kw_is_dsr_fraction(self):
        pk = 700.0
        assert abs(_flex_kw(pk) - pk * _IC_DSR_FRACTION) < 0.01

    def test_flex_kw_rounds(self):
        result = _flex_kw(350.0)
        assert result == round(350.0 * _IC_DSR_FRACTION, 2)


class TestCMRevenue:
    def test_uses_correct_year_price(self):
        price_2021 = _CM_DELIVERY_GBP_PER_KW_YR[2021]  # £8.40
        rev = _gross_cm_revenue(100.0, 2021)
        assert abs(rev - 100.0 * price_2021) < 0.01

    def test_2018_price_is_highest_early_year(self):
        # 2018: £19.40/kW is first full T-4 delivery year
        assert _CM_DELIVERY_GBP_PER_KW_YR[2018] == 19.40

    def test_2021_cheapest_year(self):
        assert _CM_DELIVERY_GBP_PER_KW_YR[2021] == 8.40

    def test_unknown_year_falls_back_to_2025(self):
        rev = _gross_cm_revenue(100.0, 2030)
        assert rev == round(100.0 * _CM_DELIVERY_GBP_PER_KW_YR[2025], 2)


class TestDFSRevenue:
    def test_zero_before_2022(self):
        assert _gross_dfs_revenue(100.0, 2021) == 0.0

    def test_nonzero_from_2022(self):
        assert _gross_dfs_revenue(100.0, 2022) > 0.0

    def test_dfs_revenue_formula(self):
        flex_kw = 70.0
        flex_mw = flex_kw / 1000.0
        # flex_mw * duration_hrs * rate_per_mwh * events = MWh delivered * rate
        expected = flex_mw * 1.0 * 4.5 * 20
        assert abs(_gross_dfs_revenue(flex_kw, 2023) - expected) < 0.01


class TestICFlexibilityRevenueBook:
    def _make_book_with_customers(self, year=2023):
        book = ICFlexibilityRevenueBook()
        ic_customers = [
            ("C_IC1", 1_998_631.0),
            ("C_IC2", 1_003_306.0),
            ("C_IC3", 4_007_250.0),
            ("C_IC4", 2_997_836.0),
        ]
        book.compute_year(year, ic_customers)
        return book

    def test_all_eligible_customers_enroll(self):
        book = self._make_book_with_customers()
        recs = book.records_for_year(2023)
        assert len(recs) == 4

    def test_below_min_eac_excluded(self):
        book = ICFlexibilityRevenueBook()
        book.compute_year(2023, [("SMALL", 50_000.0)])
        assert len(book.records_for_year(2023)) == 0

    def test_net_revenue_positive(self):
        book = self._make_book_with_customers()
        for r in book.records_for_year(2023):
            assert r.net_revenue_gbp > 0

    def test_net_revenue_is_gross_minus_fee(self):
        book = self._make_book_with_customers()
        for r in book.records_for_year(2023):
            gross = r.gross_cm_revenue_gbp + r.gross_dfs_revenue_gbp
            fee = round(gross * _AGGREGATOR_FEE_PCT, 2)
            assert abs(r.net_revenue_gbp - (gross - fee)) < 0.01

    def test_no_dfs_before_2022(self):
        book = ICFlexibilityRevenueBook()
        book.compute_year(2020, [("C_IC3", 4_007_250.0)])
        recs = book.records_for_year(2020)
        assert recs[0].gross_dfs_revenue_gbp == 0.0

    def test_dfs_revenue_nonzero_from_2022(self):
        book = ICFlexibilityRevenueBook()
        book.compute_year(2022, [("C_IC3", 4_007_250.0)])
        recs = book.records_for_year(2022)
        assert recs[0].gross_dfs_revenue_gbp > 0.0

    def test_total_revenue_accumulates_across_years(self):
        book = ICFlexibilityRevenueBook()
        ic = [("C_IC3", 4_007_250.0)]
        book.compute_year(2020, ic)
        book.compute_year(2021, ic)
        book.compute_year(2022, ic)
        total = book.total_revenue_all_years()
        assert total > 0.0
        year_sum = (
            book.total_revenue_for_year(2020)
            + book.total_revenue_for_year(2021)
            + book.total_revenue_for_year(2022)
        )
        assert abs(total - year_sum) < 0.01

    def test_flexibility_summary_structure(self):
        book = self._make_book_with_customers()
        summary = book.flexibility_summary()
        assert "total_ic_flex_revenue_gbp" in summary
        assert "enrolled_customer_years" in summary
        assert 2023 in summary["per_year"]

    def test_summary_per_year_enrolled_count(self):
        book = self._make_book_with_customers()
        summary = book.flexibility_summary()
        assert summary["per_year"][2023]["enrolled_customers"] == 4

    def test_larger_eac_earns_more(self):
        book = ICFlexibilityRevenueBook()
        book.compute_year(2023, [("SMALL", 1_000_000.0), ("LARGE", 4_000_000.0)])
        recs = book.records_for_year(2023)
        by_cid = {r.customer_id: r for r in recs}
        assert by_cid["LARGE"].net_revenue_gbp > by_cid["SMALL"].net_revenue_gbp

    def test_2021_low_cm_price_reduces_revenue(self):
        book_2021 = ICFlexibilityRevenueBook()
        book_2023 = ICFlexibilityRevenueBook()
        ic = [("C_IC3", 4_007_250.0)]
        book_2021.compute_year(2021, ic)
        book_2023.compute_year(2023, ic)
        assert book_2021.total_revenue_for_year(2021) < book_2023.total_revenue_for_year(2023)

    def test_compute_year_returns_revenue_dict(self):
        book = ICFlexibilityRevenueBook()
        result = book.compute_year(2023, [("C_IC1", 2_000_000.0)])
        assert "C_IC1" in result
        assert result["C_IC1"] > 0
