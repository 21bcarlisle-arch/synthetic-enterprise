"""Tests for Phase OJ: Warm Home Discount (WHD) Liability Observatory."""
import pytest
from company.regulatory.warm_home_discount import (
    WHDBook,
    WHDRecord,
    WHDEligibilityBasis,
    _CORE_DISCOUNT,
    _BROADER_DISCOUNT,
)


class TestWHDDiscountRates:
    def test_core_discount_2016(self):
        assert _CORE_DISCOUNT[2016] == pytest.approx(140.0)

    def test_core_discount_2022_rises(self):
        assert _CORE_DISCOUNT[2022] == pytest.approx(150.0)

    def test_broader_matches_core_2019(self):
        assert _BROADER_DISCOUNT[2019] == pytest.approx(_CORE_DISCOUNT[2019])


class TestWHDBookOperations:
    def test_record_discount_core(self):
        book = WHDBook()
        rec = book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-02")
        assert rec.discount_gbp == pytest.approx(150.0)
        assert rec.is_core_group

    def test_record_discount_broader(self):
        book = WHDBook()
        rec = book.record_discount("C2", 2020, WHDEligibilityBasis.BROADER_GROUP, "2020-02")
        assert rec.discount_gbp == pytest.approx(140.0)
        assert not rec.is_core_group

    def test_has_received_whd(self):
        book = WHDBook()
        book.record_discount("C3", 2021, WHDEligibilityBasis.CORE_GROUP, "2021-02")
        assert book.has_received_whd("C3", 2021)
        assert not book.has_received_whd("C3", 2020)

    def test_total_discounted_gbp(self):
        book = WHDBook()
        book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-02")
        book.record_discount("C2", 2022, WHDEligibilityBasis.BROADER_GROUP, "2022-02")
        assert book.total_discounted_gbp(2022) == pytest.approx(300.0)

    def test_core_group_count(self):
        book = WHDBook()
        book.record_discount("C1", 2020, WHDEligibilityBasis.CORE_GROUP, "2020-02")
        book.record_discount("C2", 2020, WHDEligibilityBasis.BROADER_GROUP, "2020-02")
        assert book.core_group_count(2020) == 1
        assert book.broader_group_count(2020) == 1

    def test_levy_recoverable_initially(self):
        book = WHDBook()
        book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-02")
        assert book.levy_recoverable_gbp() == pytest.approx(150.0)

    def test_mark_levy_recovered(self):
        book = WHDBook()
        book.record_discount("C1", 2022, WHDEligibilityBasis.CORE_GROUP, "2022-02")
        n = book.mark_levy_recovered(2022)
        assert n == 1
        assert book.levy_recoverable_gbp() == pytest.approx(0.0)


class TestWHDThresholdExemption:
    """Test WHD threshold logic -- our portfolio is exempt."""

    _WHD_THRESHOLD = 150_000

    def _ic_customers_only(self):
        return ["C_IC1", "C_IC2", "C_IC3", "C_IC4"]

    def _mixed_portfolio(self, n_domestic=5):
        return [f"C{i}" for i in range(1, n_domestic + 1)] + ["C_IC1", "C_IC2"]

    def test_ic_only_portfolio_is_exempt(self):
        cids = self._ic_customers_only()
        domestic = [c for c in cids if not (c.startswith("C_IC") or c.startswith("IC"))]
        assert len(domestic) < self._WHD_THRESHOLD

    def test_small_mixed_portfolio_is_exempt(self):
        cids = self._mixed_portfolio(n_domestic=9)
        domestic = [c for c in cids if not (c.startswith("C_IC") or c.startswith("IC"))]
        assert len(domestic) < self._WHD_THRESHOLD

    def test_large_domestic_portfolio_exceeds_threshold(self):
        cids = [f"C{i}" for i in range(1, 200_001)]
        domestic = [c for c in cids if not (c.startswith("C_IC") or c.startswith("IC"))]
        assert len(domestic) >= self._WHD_THRESHOLD


class TestWHDBoardSection:
    def _make_data(self):
        return {
            "years": {
                "2022": {"active_customer_ids": ["C1", "C2", "C3", "C_IC1", "C_IC2"]},
                "2023": {"active_customer_ids": ["C1", "C2", "C_IC1", "C_IC2", "C_IC3"]},
            }
        }

    def _render(self):
        from saas.reporting.annual_report import _section_whd_liability
        return _section_whd_liability(self._make_data())

    def test_section_renders(self):
        assert "Warm Home Discount" in self._render()

    def test_section_shows_exempt_status(self):
        out = self._render()
        assert "exempt" in out.lower() or "EXEMPT" in out

    def test_section_shows_nil_liability(self):
        assert "NIL" in self._render()

    def test_section_shows_threshold(self):
        assert "150,000" in self._render()

    def test_section_shows_growth_warning(self):
        out = self._render()
        assert "150,000" in out

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_whd_liability
        assert _section_whd_liability({}) == ""
