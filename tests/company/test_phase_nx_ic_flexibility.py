"""Tests for Phase NX: I&C Demand Response Enrollment.

THIS FILE WAS RED AT HEAD when the de-rating pass picked it up, and had been since the pass that
gave the CM price one home: that pass deleted `_CM_DELIVERY_GBP_PER_KW_YR` and left four tests
importing it, so the whole module failed at COLLECTION. A collection error is the worst shape of
red here, because it takes the other seventeen tests in the file down with it silently -- the
module's entire book-level coverage was dark and the count of passing tests barely moved.
"""
import pytest

from company.market import capacity_market_published_record as rec
from company.market import dfs_published_record as dfs
from company.market.ic_flexibility_revenue import (
    _AGGREGATOR_FEE_PCT,
    _CM_AUCTION_FOR_IC,
    _DFS_LAUNCH_YEAR,
    _IC_DSR_FRACTION,
    _IC_LOAD_FACTOR,
    _IC_MIN_EAC_KWH,
    ICFlexibilityRecord,
    ICFlexibilityRevenueBook,
    _cm_derating_factor,
    _flex_kw,
    _gross_cm_revenue,
    _gross_dfs_revenue,
    _peak_demand_kw,
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
    """The CM leg reads the published record and DE-RATES. It used to do neither.

    Every test here used to assert against `_CM_DELIVERY_GBP_PER_KW_YR`, the module's own copy of
    the clearing price -- so they graded the table against itself and would have passed at any
    values whatever. The subject is now the commons, which the module does not own.
    """

    def test_uses_the_published_price_for_the_year_asked_about(self):
        rev = _gross_cm_revenue(100.0, 2021)
        published = rec.clearing_price_gbp_per_kw_year(2021, _CM_AUCTION_FOR_IC)
        assert published == pytest.approx(8.40)
        # ...de-rated, so NOT 100 x 8.40. The old test asserted exactly that product.
        assert rev == pytest.approx(round(100.0 * 8.40 * 0.8634, 2))
        assert rev < 100.0 * published

    def test_the_cm_leg_is_de_rated_for_every_established_year(self):
        """THE DEFECT THIS PASS FIXED, over the whole partition rather than one year.

        MUTATION: multiply by `flex_kw` and the raw price in `_gross_cm_revenue` and every
        established year fires. The leg was overstated by 1/f - 1 -- 12% to 28% across the record,
        NOT by 100%, which is what "overstated by the whole de-rating factor" sounds like.
        """
        checked = 0
        for year in range(2016, 2026):
            rev = _gross_cm_revenue(100.0, year)
            price = rec.clearing_price_gbp_per_kw_year(year, _CM_AUCTION_FOR_IC)
            if rev is None or price is None:
                continue
            checked += 1
            factor = _cm_derating_factor(year)
            assert 0.0 < factor < 1.0
            assert rev == pytest.approx(round(100.0 * price * factor, 2))
            assert rev < round(100.0 * price, 2), f"{year} is not de-rated"
        assert checked >= 7, f"only {checked} established years -- the assertion is near-vacuous"

    def test_2021_is_the_cheapest_t4_in_the_record(self):
        """Keyed to the ordering, not to 8.40: the claim is 'cheapest', so test cheapest.

        AND THE COMPARISON SET IS T-4s ONLY, which is the whole subtlety. DY 2022/23's `t4` field
        holds GBP6.44, lower than 2021's GBP8.40 -- but that is a T-3, the replacement for a
        suspended T-4, so including it answers "cheapest bulk auction" and not "cheapest T-4".
        This test failed on exactly that when first written, which is the same field-versus-label
        confusion that makes the de-rating pairing hazardous one function away.
        """
        prices = {
            y: p for y in range(2016, 2026)
            if rec.auction_actually_held(y, _CM_AUCTION_FOR_IC) == "T-4"
            and (p := rec.clearing_price_gbp_per_kw_year(y, _CM_AUCTION_FOR_IC)) is not None
        }
        assert min(prices, key=prices.get) == 2021
        assert 2022 not in prices, "the suspended year's T-3 must not be graded as a T-4"

    def test_an_unestablished_year_refuses_and_does_not_borrow_a_neighbour(self):
        """The INVERSE of the test this replaced, which asserted the defect as the contract.

        `test_unknown_year_falls_back_to_2025` pinned `.get(year, TABLE[2025])` -- a lookup whose
        miss silently returned another year's price, and whose fallback year was itself an
        unestablished figure. It was deleted as a defect and the test that demanded it outlived
        it. A miss must REFUSE.
        """
        assert _gross_cm_revenue(100.0, 2030) is None
        assert _gross_cm_revenue(100.0, 2016) is None   # no T-4 delivered into 2016/17
        assert _gross_cm_revenue(100.0, 2017) is None


class TestDFSRevenue:
    def test_zero_before_2022(self):
        assert _gross_dfs_revenue(100.0, 2021) == 0.0

    def test_nonzero_from_2022(self):
        assert _gross_dfs_revenue(100.0, 2022) > 0.0

    def test_dfs_revenue_formula(self):
        """The formula, against the published winter rather than against two inlined numbers.

        This test used to assert `flex_mw x 1.0 x 4.5 x 20` for winter 2023/24 -- a GBP4.50/MWh
        rate and 20 events, neither of which the published record carries for that winter. It was
        wrong on BOTH counts and could not report it, because the module's collection error had
        kept the whole file dark since the CM-price pass. 2023/24 is the winter the DFS record
        explicitly does not establish, so the leg refuses there.
        """
        flex_kw = 70.0
        flex_mw = flex_kw / 1000.0
        row = dfs.winter(2022)
        expected = (flex_mw * 1.0 * dfs.realised_rate_gbp_per_mwh(2022)
                    * dfs.events(2022) * row.delivery_fraction_of_committed)
        assert _gross_dfs_revenue(flex_kw, 2022) == pytest.approx(round(expected, 2))

    def test_an_unestablished_winter_refuses_rather_than_paying_zero(self):
        """2023/24 ran and we cannot say what it paid. That is not the same as paying nothing.

        MUTATION: return 0.0 instead of None for an unestablished winter, and this fires. The two
        readings lead to opposite repairs -- one is a research gap, the other a product finding.
        """
        assert _gross_dfs_revenue(70.0, 2023) is None
        assert _gross_dfs_revenue(70.0, 2021) == 0.0   # pre-launch: genuinely paid nothing


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
