"""Tests for Phase OH: Feed-in Tariff (FiT) Levelisation Levy Observatory."""
import pytest
from company.regulatory.fit_book import (
    FITBook,
    FITInstallation,
    FITPayment,
    FITTechnology,
    _FIT_LEVELISATION_RATE_PER_MWH,
    FIT_SCHEME_END_DATE,
)


class TestFITLevelisationRates:
    def test_2016_rate(self):
        assert _FIT_LEVELISATION_RATE_PER_MWH[2016] == pytest.approx(8.36)

    def test_2019_rate(self):
        assert _FIT_LEVELISATION_RATE_PER_MWH[2019] == pytest.approx(9.45)

    def test_2020_rate_zero(self):
        assert _FIT_LEVELISATION_RATE_PER_MWH[2020] == pytest.approx(0.0)

    def test_scheme_end_date(self):
        assert FIT_SCHEME_END_DATE == "2019-03-31"

    def test_rates_for_all_sim_years(self):
        for yr in [2016, 2017, 2018, 2019, 2020]:
            assert yr in _FIT_LEVELISATION_RATE_PER_MWH


class TestFITLevelisationChargeFormula:
    def test_levy_formula_2016(self):
        # function signature is kWh-based: charge = kWh * rate / 1000 = MWh * rate
        book = FITBook()
        rate = _FIT_LEVELISATION_RATE_PER_MWH[2016]
        mwh = 5000.0
        charge = book.levelisation_charge_gbp(2016, mwh * 1000.0)
        assert charge == pytest.approx(mwh * rate, rel=1e-4)

    def test_zero_levy_2020(self):
        book = FITBook()
        charge = book.levelisation_charge_gbp(2020, 5000.0 * 1000.0)
        assert charge == pytest.approx(0.0)

    def test_proportional_to_mwh(self):
        book = FITBook()
        c1 = book.levelisation_charge_gbp(2018, 3000.0 * 1000.0)
        c2 = book.levelisation_charge_gbp(2018, 6000.0 * 1000.0)
        assert c2 == pytest.approx(2 * c1, rel=1e-4)

    def test_zero_mwh_zero_levy(self):
        book = FITBook()
        assert book.levelisation_charge_gbp(2017, 0.0) == pytest.approx(0.0)


class TestFITPaymentRecord:
    def test_generation_payment(self):
        payment = FITPayment(
            installation_id="FIT-001",
            quarter="2017Q1",
            generation_kwh=1000.0,
            export_kwh=300.0,
            generation_rate_p=4.18,
            export_rate_p=4.85,
        )
        assert payment.generation_payment_gbp == pytest.approx(41.80)

    def test_export_payment(self):
        payment = FITPayment(
            installation_id="FIT-001",
            quarter="2017Q1",
            generation_kwh=1000.0,
            export_kwh=300.0,
            generation_rate_p=4.18,
            export_rate_p=4.85,
        )
        assert payment.export_payment_gbp == pytest.approx(14.55)

    def test_total_payment(self):
        payment = FITPayment(
            installation_id="FIT-001",
            quarter="2017Q1",
            generation_kwh=1000.0,
            export_kwh=300.0,
            generation_rate_p=4.18,
            export_rate_p=4.85,
        )
        assert payment.total_payment_gbp == pytest.approx(56.35)


class TestFITBookOperations:
    def test_total_paid_returns_sum(self):
        book = FITBook()
        p1 = FITPayment("FIT-001", "2017Q1", 1000.0, 300.0, 4.18, 4.85)
        p2 = FITPayment("FIT-001", "2018Q1", 1000.0, 300.0, 3.97, 5.24)
        book.record_payment(p1)
        book.record_payment(p2)
        total = book.total_paid_gbp()
        assert total == pytest.approx(p1.total_payment_gbp + p2.total_payment_gbp)

    def test_total_paid_by_year_filter(self):
        book = FITBook()
        p1 = FITPayment("FIT-001", "2017Q1", 1000.0, 300.0, 4.18, 4.85)
        p2 = FITPayment("FIT-001", "2018Q1", 1000.0, 300.0, 3.97, 5.24)
        book.record_payment(p1)
        book.record_payment(p2)
        assert book.total_paid_gbp(year=2017) == pytest.approx(p1.total_payment_gbp)


class TestFITBoardSection:
    def _make_data(self):
        return {
            "fit_summary": {
                "total_fit_levy_gbp": 42000.0,
                "per_year": {
                    "2016": {"elec_mwh": 5000.0, "levy_rate_gbp_per_mwh": 8.36, "fit_levy_gbp": 41.80},
                    "2017": {"elec_mwh": 5100.0, "levy_rate_gbp_per_mwh": 9.19, "fit_levy_gbp": 46.87},
                    "2020": {"elec_mwh": 5200.0, "levy_rate_gbp_per_mwh": 0.0, "fit_levy_gbp": 0.0},
                },
            },
            "management_accounts": {
                "2016": {"income_statement": {"revenue_gbp": 1200000.0}},
                "2017": {"income_statement": {"revenue_gbp": 1300000.0}},
            },
        }

    def _render(self):
        from saas.reporting.annual_report import _section_fit_levy
        return _section_fit_levy(self._make_data())

    def test_section_renders(self):
        out = self._render()
        assert "Feed-in Tariff" in out

    def test_section_shows_levy_years(self):
        out = self._render()
        assert "2016" in out
        assert "2017" in out

    def test_section_shows_zero_for_closed_years(self):
        out = self._render()
        assert "NIL" in out or "0.00" in out

    def test_section_shows_scheme_end_date(self):
        out = self._render()
        assert "2019-03-31" in out

    def test_section_shows_total_row(self):
        out = self._render()
        assert "Total" in out

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_fit_levy
        assert _section_fit_levy({}) == ""

    def test_section_shows_revenue_pct(self):
        out = self._render()
        assert "%" in out
