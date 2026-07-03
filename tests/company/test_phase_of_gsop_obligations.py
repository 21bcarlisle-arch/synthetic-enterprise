"""Phase OF tests: GSOP (Guaranteed Standards of Performance) obligations."""
import datetime as dt
import pytest

from company.regulatory.gsop import (
    GSOPBook,
    GSOPType,
    GSOPPayment,
    _GSOP_AMOUNT_GBP,
    _GSOP_PAYMENT_DAYS,
)


# ── GSOP payment mechanics ────────────────────────────────────────────────────

class TestGSOPBook:
    def _book_with_trigger(self, gsop_type=GSOPType.MISSED_APPOINTMENT):
        book = GSOPBook()
        book.record_trigger("C1", gsop_type, dt.date(2022, 6, 1))
        return book

    def test_trigger_creates_payment(self):
        book = self._book_with_trigger()
        assert len(book._payments) == 1

    def test_payment_amount_is_30_gbp(self):
        book = self._book_with_trigger(GSOPType.MISSED_APPOINTMENT)
        assert book._payments[0].amount_gbp == pytest.approx(30.0, rel=1e-6)

    def test_payment_due_date_after_trigger(self):
        book = self._book_with_trigger()
        p = book._payments[0]
        assert p.payment_due_date > p.trigger_date

    def test_final_bill_delay_payment_amount(self):
        book = self._book_with_trigger(GSOPType.FINAL_BILL_DELAY)
        assert book._payments[0].amount_gbp == pytest.approx(30.0, rel=1e-6)

    def test_total_liability_sums_all(self):
        book = GSOPBook()
        for gt in [GSOPType.MISSED_APPOINTMENT, GSOPType.FINAL_BILL_DELAY, GSOPType.ERRONEOUS_TRANSFER]:
            book.record_trigger("C1", gt, dt.date(2022, 6, 1))
        assert book.total_liability_gbp() == pytest.approx(90.0, rel=1e-6)

    def test_year_filter_on_liability(self):
        book = GSOPBook()
        book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, dt.date(2021, 6, 1))
        book.record_trigger("C2", GSOPType.MISSED_APPOINTMENT, dt.date(2022, 6, 1))
        assert book.total_liability_gbp(year=2021) == pytest.approx(30.0, rel=1e-6)
        assert book.total_liability_gbp(year=2022) == pytest.approx(30.0, rel=1e-6)

    def test_annual_report_empty_year(self):
        book = GSOPBook()
        book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, dt.date(2021, 6, 1))
        rep = book.annual_report(2022)
        assert rep["total_triggers"] == 0
        assert rep["total_liability_gbp"] == 0.0

    def test_overdue_detection(self):
        book = GSOPBook()
        book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, dt.date(2022, 1, 1))
        # Payment due within 10 working days; overdue by March
        overdue = book.overdue(dt.date(2022, 3, 1))
        assert len(overdue) == 1

    def test_paid_clears_overdue(self):
        book = GSOPBook()
        p = book.record_trigger("C1", GSOPType.MISSED_APPOINTMENT, dt.date(2022, 1, 1))
        book.pay(p.payment_id, dt.date(2022, 1, 10))
        overdue = book.overdue(dt.date(2022, 3, 1))
        assert len(overdue) == 0


# ── board section ─────────────────────────────────────────────────────────────

class TestGSOPBoardSection:
    def _data_small(self):
        years = {}
        for yr in range(2016, 2026):
            years[str(yr)] = {"active_customer_ids": ["C1", "C2", "C_IC1"]}
        return {"years": years, "customer_events": []}

    def _data_large(self):
        years = {}
        for yr in range(2016, 2026):
            cids = [f"C_{i}" for i in range(200)]
            years[str(yr)] = {"active_customer_ids": cids}
        churned = [{"event_type": "churned", "event_date": f"{yr}-06-15", "customer_id": f"C_0"}
                   for yr in range(2016, 2026)]
        return {"years": years, "customer_events": churned}

    def _section(self, data):
        from saas.reporting.annual_report import _section_gsop_obligations
        return _section_gsop_obligations(data)

    def test_returns_string(self):
        out = self._section(self._data_small())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_years(self):
        out = self._section({})
        assert out == ""

    def test_phase_of_header(self):
        out = self._section(self._data_small())
        assert "Phase OF" in out

    def test_small_portfolio_no_obligations(self):
        out = self._section(self._data_small())
        assert "No GSOP obligations" in out

    def test_large_portfolio_shows_table(self):
        out = self._section(self._data_large())
        assert "Triggers" in out
        for yr in range(2016, 2026):
            assert str(yr) in out
