"""Tests for SEGExportEstimator — Phase R."""
import pytest
from company.regulatory.seg_book import SEGBook
from company.regulatory.seg_export_estimator import (
    SEGExportEstimator,
    AnnualExportEstimate,
    ANNUAL_YIELD_KWH_PER_KWP,
    SELF_CONSUMPTION_STANDARD,
    SELF_CONSUMPTION_WITH_BATTERY,
    SEG_START_YEAR,
)


def _estimator():
    return SEGExportEstimator(SEGBook())


class TestYieldAndFractions:
    def test_annual_yield_scales_with_capacity(self):
        est = _estimator()
        assert est.annual_yield_kwh(3.8) == pytest.approx(3.8 * ANNUAL_YIELD_KWH_PER_KWP)

    def test_zero_capacity_zero_yield(self):
        est = _estimator()
        assert est.annual_yield_kwh(0.0) == pytest.approx(0.0)

    def test_standard_self_consumption(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=False) == pytest.approx(SELF_CONSUMPTION_STANDARD)

    def test_battery_self_consumption_higher(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=True) > est.self_consumption_fraction(has_battery=False)

    def test_battery_self_consumption_value(self):
        est = _estimator()
        assert est.self_consumption_fraction(has_battery=True) == pytest.approx(SELF_CONSUMPTION_WITH_BATTERY)

    def test_export_fraction_complement(self):
        est = _estimator()
        assert est.export_fraction(has_battery=False) == pytest.approx(1.0 - SELF_CONSUMPTION_STANDARD)
        assert est.export_fraction(has_battery=True) == pytest.approx(1.0 - SELF_CONSUMPTION_WITH_BATTERY)


class TestEstimateAnnualExport:
    def test_standard_export(self):
        est = _estimator()
        result = est.estimate_annual_export_kwh(3.8, has_battery=False)
        expected = 3.8 * ANNUAL_YIELD_KWH_PER_KWP * (1.0 - SELF_CONSUMPTION_STANDARD)
        assert result == pytest.approx(expected)

    def test_battery_export_lower(self):
        est = _estimator()
        no_batt = est.estimate_annual_export_kwh(3.8, has_battery=False)
        with_batt = est.estimate_annual_export_kwh(3.8, has_battery=True)
        assert with_batt < no_batt

    def test_zero_capacity_zero_export(self):
        est = _estimator()
        assert est.estimate_annual_export_kwh(0.0) == pytest.approx(0.0)


class TestEstimateAndRecord:
    def test_pre_seg_year_raises(self):
        est = _estimator()
        with pytest.raises(ValueError, match="FIT"):
            est.estimate_and_record("C1", 3.8, year=2019)

    def test_returns_annual_export_estimate(self):
        est = _estimator()
        result = est.estimate_and_record("C1", 3.8, year=2022)
        assert isinstance(result, AnnualExportEstimate)
        assert result.customer_id == "C1"
        assert result.year == 2022

    def test_generation_plus_consumed_plus_exported(self):
        est = _estimator()
        r = est.estimate_and_record("C1", 3.8, year=2022)
        assert r.self_consumed_kwh + r.exported_kwh == pytest.approx(r.generation_kwh, abs=0.01)

    def test_seg_rate_from_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r = est.estimate_and_record("C1", 3.8, year=2022)
        assert r.seg_rate_p_per_kwh == pytest.approx(book.seg_rate_for_year(2022))

    def test_payment_recorded_in_seg_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        est.estimate_and_record("C1", 3.8, year=2022)
        assert book.total_export_kwh(2022) > 0.0

    def test_2022_crisis_rate_inflates_payment(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r2020 = est.estimate_and_record("C1", 3.8, year=2020)
        r2022 = est.estimate_and_record("C1", 3.8, year=2022)
        # 2022 SEG rate (7.5p) > 2020 rate (4.0p) → higher payment for same export
        assert r2022.seg_payment_gbp > r2020.seg_payment_gbp

    def test_battery_customer_exports_less(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r_no_batt = est.estimate_and_record("C1", 3.8, year=2023, has_battery=False)
        r_batt = est.estimate_and_record("C2", 3.8, year=2023, has_battery=True)
        assert r_batt.exported_kwh < r_no_batt.exported_kwh

    def test_seg_start_year_is_valid(self):
        est = _estimator()
        r = est.estimate_and_record("C1", 3.8, year=SEG_START_YEAR)
        assert r.exported_kwh > 0.0


class TestPortfolioSummary:
    def test_empty_portfolio(self):
        est = _estimator()
        s = est.portfolio_summary([])
        assert s["customer_count"] == 0
        assert s["total_export_kwh"] == 0.0

    def test_multiple_customers_aggregated(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C2", 2.5, year=2022)
        s = est.portfolio_summary([r1, r2])
        assert s["customer_count"] == 2
        assert s["total_export_kwh"] == pytest.approx(r1.exported_kwh + r2.exported_kwh)

    def test_seg_cost_matches_book(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C2", 2.5, year=2022)
        s = est.portfolio_summary([r1, r2])
        assert s["total_seg_cost_gbp"] == pytest.approx(book.total_paid_gbp(2022), rel=1e-4)

    def test_unique_customer_count(self):
        book = SEGBook()
        est = SEGExportEstimator(book)
        r1 = est.estimate_and_record("C1", 3.8, year=2022)
        r2 = est.estimate_and_record("C1", 3.8, year=2023)  # same customer, different year
        s = est.portfolio_summary([r1, r2])
        assert s["customer_count"] == 1


# ---------------------------------------------------------------------------
# Geographic yield (W1_25 / W1_27) — added 2026-09-06
# ---------------------------------------------------------------------------


def test_the_NATIONAL_FIGURE_IS_A_DECISION_and_not_something_a_caller_falls_into():
    """THE DEFECT THIS TABLE CLOSES. Until 2026-09-06 one number served every household in the
    book, carrying a 3.4% RMS error in annual generation — the same order as the SEG rate spread it
    was used to value — and nothing anywhere required a caller to notice.

    `yield_kwh_per_kwp` therefore has NO default. Passing `None` is how you choose the national
    figure, and it is a visible act.
    """
    import inspect

    from company.regulatory import seg_export_estimator as seg

    sig = inspect.signature(seg.yield_kwh_per_kwp)
    param = sig.parameters["annual_sunshine_hours"]
    assert param.default is inspect.Parameter.empty, (
        "a default here restores the silent national figure this table exists to replace")
    assert seg.yield_kwh_per_kwp(None) == seg.ANNUAL_YIELD_KWH_PER_KWP


def test_the_BAND_TABLE_AVERAGES_TO_ITS_PUBLISHED_ANCHOR():
    """THE LEVEL, checked as an identity rather than trusted. The bands' SHAPE is derived from
    HadUK sunshine; their LEVEL is the MCS 2025 fleet average. Weight each band by its share of GB
    households and the result must be that anchor — if it is not, the derivation has drifted off
    the only published number in it and every yield below is a private opinion."""
    from company.regulatory import seg_export_estimator as seg

    weighted = sum(y * s for y, s in zip(seg.SOLAR_BAND_YIELD_KWH_PER_KWP,
                                         seg.SOLAR_BAND_HOUSEHOLD_SHARE))

    assert weighted == pytest.approx(seg.ANNUAL_YIELD_KWH_PER_KWP, abs=1.5)
    assert sum(seg.SOLAR_BAND_HOUSEHOLD_SHARE) == pytest.approx(1.0, abs=0.005)
    assert len(seg.SOLAR_BAND_YIELD_KWH_PER_KWP) == len(seg.SOLAR_BAND_CUTS_SUNSHINE_HOURS) + 1
    assert len(seg.SOLAR_BAND_HOUSEHOLD_SHARE) == len(seg.SOLAR_BAND_YIELD_KWH_PER_KWP)


def test_more_sunshine_means_more_yield_and_the_boundaries_are_where_they_say():
    """Monotonicity, and the off-by-one that a banded lookup invites: a value exactly ON a cut must
    fall in the UPPER band, and one just below it in the lower. Getting that backwards moves a
    quarter of the country by 20 kWh/kWp and nothing in the output looks wrong."""
    from company.regulatory import seg_export_estimator as seg

    yields = [seg.yield_kwh_per_kwp(h) for h in (900.0, 1450.0, 1550.0, 1650.0, 1900.0)]
    assert yields == sorted(yields)
    assert len(set(yields)) == 5, "each probe must land in a different band"

    for i, cut in enumerate(seg.SOLAR_BAND_CUTS_SUNSHINE_HOURS):
        assert seg.yield_kwh_per_kwp(cut) == seg.SOLAR_BAND_YIELD_KWH_PER_KWP[i + 1]
        assert seg.yield_kwh_per_kwp(cut - 0.1) == seg.SOLAR_BAND_YIELD_KWH_PER_KWP[i]


def test_the_SPREAD_IS_MATERIAL_or_the_bands_are_not_worth_carrying():
    """A table whose bands differed by a percent would be ceremony. Keyed to the property — the
    spread must be big enough to matter against the SEG rate it multiplies — rather than to today's
    numbers."""
    from company.regulatory import seg_export_estimator as seg

    lo, hi = seg.SOLAR_BAND_YIELD_KWH_PER_KWP[0], seg.SOLAR_BAND_YIELD_KWH_PER_KWP[-1]

    assert hi / lo - 1.0 > 0.08, f"a {hi / lo - 1:.1%} spread does not justify five bands"
    assert lo < seg.ANNUAL_YIELD_KWH_PER_KWP < hi, (
        "the national figure must sit INSIDE the band range; outside it, one of the two is wrong")


def test_a_NON_POSITIVE_SUNSHINE_DURATION_is_refused_rather_than_banded():
    """Zero or negative hours is a broken lookup, not the dullest place in Britain. Banding it
    would return a real-looking yield for a location that does not exist."""
    from company.regulatory import seg_export_estimator as seg

    for bad in (0.0, -1.0):
        with pytest.raises(ValueError, match="positive"):
            seg.yield_kwh_per_kwp(bad)


def test_the_ESTIMATOR_USES_THE_LOCATION_when_one_is_given():
    """REACHABILITY at the seam that matters: the table is worthless if `annual_yield_kwh` ignores
    it. Two identical systems in the dullest and sunniest bands must generate different amounts."""
    est = _estimator()
    dull = est.annual_yield_kwh(4.0, annual_sunshine_hours=1000.0)
    bright = est.annual_yield_kwh(4.0, annual_sunshine_hours=1900.0)
    national = est.annual_yield_kwh(4.0)

    assert bright > national > dull
    assert bright / dull > 1.08
