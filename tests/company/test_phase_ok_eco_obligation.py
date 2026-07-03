"""Tests for Phase OK: Energy Company Obligation (ECO) Observatory."""
import pytest
from company.regulatory.eco_obligation import (
    ECOObligationBook,
    ECODelivery,
    ECOPhase,
    MeasureCategory,
    _ECO_OBLIGATION_COST_PER_MWH,
    _ECO_PHASE_YEARS,
)


class TestECOPhaseYears:
    def test_eco2_years(self):
        start, end = _ECO_PHASE_YEARS["ECO2"]
        assert start == 2015 and end == 2018

    def test_eco3_years(self):
        start, end = _ECO_PHASE_YEARS["ECO3"]
        assert start == 2018 and end == 2022

    def test_eco4_years(self):
        start, end = _ECO_PHASE_YEARS["ECO4"]
        assert start == 2022 and end == 2026

    def test_rates_increase_across_phases(self):
        r2 = _ECO_OBLIGATION_COST_PER_MWH["ECO2"]
        r3 = _ECO_OBLIGATION_COST_PER_MWH["ECO3"]
        r4 = _ECO_OBLIGATION_COST_PER_MWH["ECO4"]
        assert r2 < r3 < r4

    def test_eco4_rate(self):
        assert _ECO_OBLIGATION_COST_PER_MWH["ECO4"] == pytest.approx(6.80)


class TestECODelivery:
    def test_cost_per_tonne_co2(self):
        d = ECODelivery(
            delivery_id="D001",
            phase=ECOPhase.ECO4,
            delivery_year=2023,
            customer_id="C1",
            category=MeasureCategory.INSULATION,
            co2_saved_tonnes=5.0,
            cost_gbp=250.0,
            is_fuel_poor=True,
        )
        assert d.cost_per_tonne_co2 == pytest.approx(50.0)

    def test_zero_co2_does_not_crash(self):
        d = ECODelivery(
            delivery_id="D002",
            phase=ECOPhase.ECO3,
            delivery_year=2020,
            customer_id="C2",
            category=MeasureCategory.HEATING,
            co2_saved_tonnes=0.0,
            cost_gbp=100.0,
            is_fuel_poor=False,
        )
        assert d.cost_per_tonne_co2 == pytest.approx(0.0)


class TestECOObligationBook:
    def test_estimated_annual_obligation_eco4(self):
        book = ECOObligationBook(annual_electricity_supplied_mwh=5000.0)
        charge = book.estimated_annual_obligation_gbp(ECOPhase.ECO4)
        assert charge == pytest.approx(5000.0 * 6.80)

    def test_estimated_annual_obligation_eco3(self):
        book = ECOObligationBook(annual_electricity_supplied_mwh=10000.0)
        assert book.estimated_annual_obligation_gbp(ECOPhase.ECO3) == pytest.approx(10000.0 * 4.50)

    def test_total_cost_sums_deliveries(self):
        book = ECOObligationBook()
        book.record_delivery(ECODelivery("D1", ECOPhase.ECO4, 2023, "C1", MeasureCategory.INSULATION, 3.0, 200.0, True))
        book.record_delivery(ECODelivery("D2", ECOPhase.ECO4, 2023, "C2", MeasureCategory.HEATING, 2.0, 150.0, False))
        assert book.total_cost_gbp() == pytest.approx(350.0)

    def test_fuel_poor_pct(self):
        book = ECOObligationBook()
        book.record_delivery(ECODelivery("D1", ECOPhase.ECO4, 2023, "C1", MeasureCategory.INSULATION, 3.0, 200.0, True))
        book.record_delivery(ECODelivery("D2", ECOPhase.ECO4, 2023, "C2", MeasureCategory.HEATING, 2.0, 150.0, False))
        assert book.fuel_poor_delivery_pct() == pytest.approx(50.0)

    def test_deliveries_for_phase_filtered(self):
        book = ECOObligationBook()
        book.record_delivery(ECODelivery("D1", ECOPhase.ECO3, 2021, "C1", MeasureCategory.INSULATION, 3.0, 100.0, False))
        book.record_delivery(ECODelivery("D2", ECOPhase.ECO4, 2023, "C2", MeasureCategory.HEATING, 2.0, 150.0, True))
        assert len(book.deliveries_for_phase(ECOPhase.ECO3)) == 1
        assert len(book.deliveries_for_phase(ECOPhase.ECO4)) == 1

    def test_eco_summary_dict_keys(self):
        book = ECOObligationBook(annual_electricity_supplied_mwh=5000.0)
        summary = book.eco_summary()
        assert "total_deliveries" in summary
        assert "eco4_estimated_annual_gbp" in summary


class TestECOBoardSection:
    def _make_data(self):
        return {
            "years": {
                "2020": {"active_customer_ids": ["C1", "C2", "C_IC1", "C_IC2"]},
                "2023": {"active_customer_ids": ["C1", "C_IC1", "C_IC2", "C_IC3"]},
            },
            "management_accounts": {
                "2020": {"income_statement": {"revenue_gbp": 1200000.0}},
                "2023": {"income_statement": {"revenue_gbp": 1800000.0}},
            },
        }

    def _render(self):
        from saas.reporting.annual_report import _section_eco_obligation
        return _section_eco_obligation(self._make_data())

    def test_section_renders(self):
        assert "Energy Company Obligation" in self._render()

    def test_section_shows_eco_phases(self):
        out = self._render()
        assert "ECO3" in out and "ECO4" in out

    def test_section_shows_exempt(self):
        assert "exempt" in self._render().lower()

    def test_section_shows_counterfactual(self):
        assert "Counterfactual" in self._render()

    def test_section_shows_nil_actual_liability(self):
        assert "NIL" in self._render()

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_eco_obligation
        assert _section_eco_obligation({}) == ""
