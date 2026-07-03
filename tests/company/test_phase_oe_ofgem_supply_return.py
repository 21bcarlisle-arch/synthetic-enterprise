"""Phase OE tests: Ofgem Annual Supply Return."""
import datetime as dt
import pytest

from company.regulatory.ofgem_supply_return import (
    OfgemSupplyReturn,
    OfgemReturnBook,
)


# ── OfgemSupplyReturn properties ──────────────────────────────────────────────

class TestOfgemSupplyReturn:
    def _return(self, resi=10, sme=5, ic=3):
        return OfgemSupplyReturn(
            year=2020,
            submitted_date=dt.date(2021, 3, 31),
            total_customers_residential=resi,
            total_customers_sme=sme,
            total_customers_ic=ic,
            elec_supplied_gwh=50.0,
            gas_supplied_gwh=10.0,
            residential_complaints=2,
            average_debt_per_customer_gbp=15.0,
            whd_customers_supported=3,
            gsop_payments_gbp=0.0,
            bad_debt_written_off_gbp=5_000.0,
        )

    def test_total_customers_sum(self):
        ret = self._return(resi=10, sme=5, ic=3)
        assert ret.total_customers == 18

    def test_is_submitted_true_when_date_set(self):
        ret = self._return()
        assert ret.is_submitted

    def test_is_submitted_false_when_no_date(self):
        ret = OfgemSupplyReturn(
            year=2020, submitted_date=None,
            total_customers_residential=10, total_customers_sme=0, total_customers_ic=0,
            elec_supplied_gwh=10.0, gas_supplied_gwh=0.0,
            residential_complaints=0, average_debt_per_customer_gbp=0.0,
            whd_customers_supported=0, gsop_payments_gbp=0.0,
        )
        assert not ret.is_submitted

    def test_complaints_per_100_customers(self):
        ret = self._return(resi=100)
        ret_new = OfgemSupplyReturn(
            year=2020, submitted_date=dt.date(2021, 3, 31),
            total_customers_residential=100, total_customers_sme=0, total_customers_ic=0,
            elec_supplied_gwh=10.0, gas_supplied_gwh=0.0,
            residential_complaints=5, average_debt_per_customer_gbp=10.0,
            whd_customers_supported=0, gsop_payments_gbp=0.0,
        )
        assert ret_new.complaints_per_100_customers == pytest.approx(5.0, rel=1e-3)

    def test_complaints_none_when_no_resi(self):
        ret = OfgemSupplyReturn(
            year=2020, submitted_date=dt.date(2021, 3, 31),
            total_customers_residential=0, total_customers_sme=0, total_customers_ic=5,
            elec_supplied_gwh=100.0, gas_supplied_gwh=0.0,
            residential_complaints=0, average_debt_per_customer_gbp=0.0,
            whd_customers_supported=0, gsop_payments_gbp=0.0,
        )
        assert ret.complaints_per_100_customers is None

    def test_whd_penetration_percent(self):
        ret = OfgemSupplyReturn(
            year=2020, submitted_date=dt.date(2021, 3, 31),
            total_customers_residential=100, total_customers_sme=0, total_customers_ic=0,
            elec_supplied_gwh=10.0, gas_supplied_gwh=0.0,
            residential_complaints=0, average_debt_per_customer_gbp=0.0,
            whd_customers_supported=15, gsop_payments_gbp=0.0,
        )
        assert ret.whd_penetration_pct == pytest.approx(15.0, rel=1e-3)

    def test_summary_has_required_keys(self):
        summary = self._return().summary()
        for key in ("year", "submitted", "total_customers", "elec_supplied_gwh", "complaints_per_100_customers"):
            assert key in summary


# ── OfgemReturnBook ───────────────────────────────────────────────────────────

class TestOfgemReturnBook:
    def _book_with_returns(self, years=None):
        book = OfgemReturnBook()
        for yr in (years or range(2016, 2026)):
            book.file_return(
                year=yr,
                submitted_date=dt.date(yr + 1, 3, 31),
                total_customers_residential=5,
                total_customers_sme=0,
                total_customers_ic=3,
                elec_supplied_gwh=50.0,
                gas_supplied_gwh=5.0,
                residential_complaints=0,
                average_debt_per_customer_gbp=10.0,
                whd_customers_supported=0,
                gsop_payments_gbp=0.0,
            )
        return book

    def test_all_returns_count(self):
        book = self._book_with_returns()
        assert len(book.all_returns()) == 10

    def test_get_return_by_year(self):
        book = self._book_with_returns()
        ret = book.get(2022)
        assert ret is not None
        assert ret.year == 2022

    def test_missing_years_empty_when_all_filed(self):
        book = self._book_with_returns()
        missing = book.missing_years(2016, 2025)
        assert missing == []

    def test_missing_years_detected(self):
        book = self._book_with_returns(years=range(2016, 2022))
        missing = book.missing_years(2016, 2025)
        assert 2022 in missing
        assert 2025 in missing


# ── board section ─────────────────────────────────────────────────────────────

class TestOfgemSupplyReturnBoardSection:
    def _data(self):
        years = {}
        for yr in range(2016, 2026):
            revenue = 600000.0
            years[str(yr)] = {
                "active_customer_ids": ["C1", "C2", "C_IC1", "C_IC2"],
                "revenue_gbp": revenue,
                "gross_gbp": revenue * 0.08,
                "bad_debt_gbp": revenue * 0.015,
                "avg_complaint_probability": 0.005,
                "commodity_split": {"electricity": {"revenue_gbp": revenue * 0.8}},
                "per_customer": {
                    "C1": {"segment": "resi"},
                    "C2": {"segment": "resi"},
                    "C_IC1": {"segment": "I&C"},
                    "C_IC2": {"segment": "I&C"},
                },
            }
        return {"years": years}

    def _section(self, data):
        from saas.reporting.annual_report import _section_ofgem_supply_return
        return _section_ofgem_supply_return(data)

    def test_returns_string(self):
        out = self._section(self._data())
        assert isinstance(out, str) and len(out) > 0

    def test_silent_when_no_years(self):
        out = self._section({})
        assert out == ""

    def test_phase_oe_header(self):
        out = self._section(self._data())
        assert "Phase OE" in out

    def test_all_years_shown(self):
        out = self._section(self._data())
        for yr in range(2016, 2026):
            assert str(yr) in out

    def test_all_returns_filed_message(self):
        out = self._section(self._data())
        assert "filed" in out.lower() or "submitted" in out.lower()
