"""Phase OA tests: I&C Broker/TPI Commission Model."""
import datetime as dt
import pytest

from company.crm.tpi_book import (
    TPIBook,
    TPITier,
    TPICommissionBasis,
    TPIDeal,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_book(rate=1.5) -> TPIBook:
    book = TPIBook()
    book.register(
        tpi_id="TPI-001",
        name="Standard Energy Broker",
        tier=TPITier.PREFERRED,
        commission_basis=TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION,
        commission_rate=rate,
        registered_date=dt.date(2016, 1, 1),
    )
    return book


def _record_deal(book, cid, mwh, rev, year):
    return book.record_deal(
        tpi_id="TPI-001",
        customer_id=cid,
        annual_consumption_mwh=mwh,
        annual_revenue_gbp=rev,
        deal_date=dt.date(year, 1, 1),
    )


# ── commission formula ────────────────────────────────────────────────────────

class TestTPICommissionFormula:
    def test_rate_1_5_gbp_per_mwh_4000_mwh(self):
        book = _make_book(rate=1.5)
        deal = _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)
        assert deal.commission_gbp == pytest.approx(6000.0, rel=1e-6)

    def test_rate_1_5_on_small_customer(self):
        book = _make_book(rate=1.5)
        deal = _record_deal(book, "C_IC2", 500.0, 75_000.0, 2019)
        assert deal.commission_gbp == pytest.approx(750.0, rel=1e-6)

    def test_commission_proportional_to_consumption(self):
        book = _make_book(rate=1.5)
        d1 = _record_deal(book, "C_IC1", 1000.0, 100_000.0, 2018)
        d2 = _record_deal(book, "C_IC2", 2000.0, 200_000.0, 2018)
        assert d2.commission_gbp == pytest.approx(2 * d1.commission_gbp, rel=1e-6)

    def test_zero_consumption_gives_zero_commission(self):
        deal = TPIDeal(
            deal_id="DEAL-0001",
            tpi_id="TPI-001",
            customer_id="C_IC1",
            annual_consumption_mwh=0.0,
            annual_revenue_gbp=0.0,
            deal_date=dt.date(2020, 1, 1),
            commission_basis=TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION,
            commission_rate=1.5,
        )
        assert deal.commission_gbp == 0.0


# ── annual summary ────────────────────────────────────────────────────────────

class TestTPIAnnualSummary:
    def test_deal_count_correct(self):
        book = _make_book()
        _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)
        _record_deal(book, "C_IC2", 8000.0, 1_200_000.0, 2020)
        summary = book.annual_summary(2020)
        assert summary["deal_count"] == 2

    def test_commission_sums_across_customers(self):
        book = _make_book(rate=1.5)
        _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)
        _record_deal(book, "C_IC2", 8000.0, 1_200_000.0, 2020)
        summary = book.annual_summary(2020)
        assert summary["total_commission_gbp"] == pytest.approx(4000*1.5 + 8000*1.5, rel=1e-6)

    def test_no_deals_gives_zero_commission(self):
        book = _make_book()
        summary = book.annual_summary(2025)
        assert summary["total_commission_gbp"] == 0.0
        assert summary["deal_count"] == 0

    def test_deals_not_in_year_excluded(self):
        book = _make_book()
        _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)
        summary = book.annual_summary(2021)
        assert summary["deal_count"] == 0

    def test_total_commission_accumulates_across_years(self):
        book = _make_book(rate=1.5)
        for yr in range(2016, 2026):
            _record_deal(book, "C_IC1", 4000.0, 600_000.0, yr)
        expected = 10 * 4000.0 * 1.5
        assert book.total_commission_gbp() == pytest.approx(expected, rel=1e-6)


# ── tpi book state ────────────────────────────────────────────────────────────

class TestTPIBookState:
    def test_registered_tpi_is_active(self):
        book = _make_book()
        assert len(book.active_tpis()) == 1

    def test_suspended_tpi_not_active(self):
        book = _make_book()
        book.suspend("TPI-001")
        assert len(book.active_tpis()) == 0

    def test_suspended_tpi_cannot_record_deal(self):
        book = _make_book()
        book.suspend("TPI-001")
        with pytest.raises(ValueError, match="suspended"):
            _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)

    def test_multiple_deals_tracked(self):
        book = _make_book()
        for yr in range(2016, 2021):
            _record_deal(book, "C_IC1", 4000.0, 600_000.0, yr)
        assert len(book._deals) == 5

    def test_deals_for_tpi_filtered(self):
        book = _make_book()
        book.register(
            tpi_id="TPI-002",
            name="Second Broker",
            tier=TPITier.STANDARD,
            commission_basis=TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION,
            commission_rate=2.0,
            registered_date=dt.date(2016, 1, 1),
        )
        _record_deal(book, "C_IC1", 4000.0, 600_000.0, 2020)
        book.record_deal(
            tpi_id="TPI-002",
            customer_id="C_IC2",
            annual_consumption_mwh=8000.0,
            annual_revenue_gbp=1_200_000.0,
            deal_date=dt.date(2020, 1, 1),
        )
        assert len(book.deals_for_tpi("TPI-001")) == 1
        assert len(book.deals_for_tpi("TPI-002")) == 1


# ── board section ─────────────────────────────────────────────────────────────

class TestTPIBoardSection:
    def _data(self, total_deals=10, total_comm=60_000.0, rate=1.5):
        per_year = {}
        for yr in range(2016, 2026):
            per_year[str(yr)] = {
                "year": yr,
                "deal_count": 1,
                "total_commission_gbp": total_comm / 10,
                "total_annual_revenue_gbp": 600_000.0,
                "tpi_count": 1,
            }
        return {
            "tpi_summary": {
                "total_commission_gbp": total_comm,
                "commission_rate_gbp_per_mwh": rate,
                "per_year": per_year,
                "active_tpi_count": 1,
                "total_deals": total_deals,
            }
        }

    def _section(self, data):
        from saas.reporting.annual_report import _section_tpi_commission
        return _section_tpi_commission(data)

    def test_returns_string_when_data_present(self):
        out = self._section(self._data())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_tpi_summary(self):
        out = self._section({})
        assert out == ""

    def test_silent_when_zero_deals(self):
        out = self._section({"tpi_summary": {"total_deals": 0, "per_year": {}}})
        assert out == ""

    def test_total_commission_shown(self):
        out = self._section(self._data(total_comm=60_000.0))
        assert "60,000" in out

    def test_rate_shown(self):
        out = self._section(self._data(rate=1.5))
        assert "1.5" in out

    def test_all_years_in_table(self):
        out = self._section(self._data())
        for yr in range(2016, 2026):
            assert str(yr) in out

    def test_phase_header_present(self):
        out = self._section(self._data())
        assert "Phase OA" in out
