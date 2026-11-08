"""Phase IQ: deeper coverage for contact_journey, multisite_account, clv_cohort_book."""
import datetime as dt
import pytest


# ===== clv_cohort_book =====
from company.crm.clv_cohort_book import CLVCohortBook


def _book():
    b = CLVCohortBook()
    b.add("C1", 2020, "price_comparison", "residential", 800.0, 120.0, 5.0)
    b.add("C2", 2020, "price_comparison", "residential", 1200.0, 160.0, 6.0)
    b.add("C3", 2021, "direct_web", "residential", -100.0, -20.0, 2.0)
    b.add("C4", 2021, "direct_web", "sme", 500.0, 80.0, 4.0)
    return b


class TestCLVCohortBook:
    def test_by_acquisition_year_count(self):
        b = _book()
        c = b.by_acquisition_year(2020)
        assert c.customer_count == 2

    def test_avg_clv_gbp(self):
        b = _book()
        c = b.by_acquisition_year(2020)
        assert c.avg_clv_gbp == pytest.approx(1000.0)

    def test_median_clv_gbp_even(self):
        b = _book()
        c = b.by_acquisition_year(2020)
        assert c.median_clv_gbp == pytest.approx(1000.0)

    def test_total_clv_gbp(self):
        b = _book()
        c = b.by_acquisition_year(2020)
        assert c.total_clv_gbp == pytest.approx(2000.0)

    def test_profitable_pct(self):
        b = _book()
        c = b.by_acquisition_year(2021)
        # C3=-100 (not), C4=500 (yes) → 50%
        assert c.profitable_pct == pytest.approx(50.0)

    def test_is_profitable_cohort(self):
        b = _book()
        assert b.by_acquisition_year(2020).is_profitable_cohort

    def test_is_not_profitable_cohort_negative_avg(self):
        b2 = CLVCohortBook()
        b2.add("X1", 2022, "ch", "seg", -500.0, -50.0, 3.0)
        assert not b2.by_acquisition_year(2022).is_profitable_cohort

    def test_by_channel(self):
        b = _book()
        c = b.by_channel("direct_web")
        assert c.customer_count == 2

    def test_best_cohort_by_year(self):
        b = _book()
        best = b.best_cohort_by_year()
        # 2020 avg=1000 > 2021 avg=200
        assert best.key == "2020"

    def test_portfolio_summary_keys(self):
        b = _book()
        s = b.portfolio_summary()
        assert "total_clv_gbp" in s and "profitable_pct" in s
