"""Tests for Phase OG: Renewable Obligation (RO) Cost Observatory."""
import pytest
from company.regulatory.roc_ledger import (
    ROCLedger,
    ROCObligationRecord,
    ROCObligationStatus,
    _ROC_OBLIGATION_LEVEL,
    _ROC_BUY_OUT_PRICE_GBP,
)


class TestROCObligationLevel:
    def test_2016_level(self):
        assert _ROC_OBLIGATION_LEVEL[2016] == pytest.approx(0.317)

    def test_2025_level(self):
        assert _ROC_OBLIGATION_LEVEL[2025] == pytest.approx(0.389)

    def test_level_increases_each_year(self):
        years = sorted(_ROC_OBLIGATION_LEVEL.keys())
        for i in range(len(years) - 1):
            assert _ROC_OBLIGATION_LEVEL[years[i]] < _ROC_OBLIGATION_LEVEL[years[i + 1]]

    def test_buy_out_price_increases(self):
        prices = [_ROC_BUY_OUT_PRICE_GBP[y] for y in sorted(_ROC_BUY_OUT_PRICE_GBP.keys())]
        assert all(prices[i] < prices[i + 1] for i in range(len(prices) - 1))

    def test_2023_buy_out_price(self):
        assert _ROC_BUY_OUT_PRICE_GBP[2023] == pytest.approx(54.35)


class TestROCObligationRecord:
    def test_rocs_required_formula(self):
        rec = ROCObligationRecord(
            obligation_year=2022,
            total_mwh_supplied=10000.0,
            rocs_required=10000.0 * 0.370,
        )
        assert rec.rocs_required == pytest.approx(3700.0)

    def test_shortfall_when_nothing_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2020, total_mwh_supplied=5000.0,
            rocs_required=1790.0, rocs_surrendered=0.0,
        )
        assert rec.rocs_shortfall == pytest.approx(1790.0)

    def test_no_shortfall_when_fully_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2020, total_mwh_supplied=5000.0,
            rocs_required=1790.0, rocs_surrendered=1790.0,
        )
        assert rec.rocs_shortfall == pytest.approx(0.0)
        assert rec.is_fully_compliant

    def test_buy_out_cost_for_shortfall(self):
        price = _ROC_BUY_OUT_PRICE_GBP[2022]
        rec = ROCObligationRecord(
            obligation_year=2022, total_mwh_supplied=5000.0,
            rocs_required=1850.0, rocs_surrendered=0.0,
        )
        assert rec.buy_out_cost_for_shortfall == pytest.approx(1850.0 * price)

    def test_compliance_pct_zero_when_none_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2019, total_mwh_supplied=3000.0,
            rocs_required=1053.0, rocs_surrendered=0.0,
        )
        assert rec.compliance_pct == pytest.approx(0.0)

    def test_compliance_pct_100_when_fully_surrendered(self):
        rec = ROCObligationRecord(
            obligation_year=2019, total_mwh_supplied=3000.0,
            rocs_required=1053.0, rocs_surrendered=1053.0,
        )
        assert rec.compliance_pct == pytest.approx(100.0)


class TestROCLedgerOperations:
    def test_create_obligation_computes_rocs(self):
        ledger = ROCLedger()
        ob = ledger.create_obligation(2020, 10000.0)
        assert ob.rocs_required == pytest.approx(10000.0 * _ROC_OBLIGATION_LEVEL[2020])

    def test_total_buy_out_exposure_two_years(self):
        ledger = ROCLedger()
        ob1 = ledger.create_obligation(2022, 5000.0)
        ob2 = ledger.create_obligation(2023, 5100.0)
        expected = ob1.buy_out_cost_for_shortfall + ob2.buy_out_cost_for_shortfall
        assert ledger.total_buy_out_exposure_gbp() == pytest.approx(expected)

    def test_obligation_for_year_retrieval(self):
        ledger = ROCLedger()
        ledger.create_obligation(2021, 4000.0)
        ob = ledger.obligation_for_year(2021)
        assert ob is not None
        assert ob.total_mwh_supplied == pytest.approx(4000.0)

    def test_obligation_for_missing_year_returns_none(self):
        ledger = ROCLedger()
        assert ledger.obligation_for_year(2030) is None

    def test_surrender_marks_compliant(self):
        ledger = ROCLedger()
        ledger.create_obligation(2019, 3000.0)
        rocs_needed = 3000.0 * _ROC_OBLIGATION_LEVEL[2019]
        updated = ledger.surrender_rocs(2019, rocs_needed)
        assert updated is not None
        assert updated.status == ROCObligationStatus.SURRENDERED
        assert updated.is_fully_compliant

    def test_non_compliant_years_empty_when_open(self):
        ledger = ROCLedger()
        ledger.create_obligation(2018, 2000.0)
        assert ledger.non_compliant_years() == []

    def test_roc_ledger_summary_string(self):
        ledger = ROCLedger()
        ledger.create_obligation(2021, 4000.0)
        summary = ledger.roc_ledger_summary()
        assert "1 obligation years" in summary
        assert "GBP" in summary


class TestROCBoardSection:
    def _make_data(self):
        return {
            "roc_summary": {
                "total_buy_out_cost_gbp": 200000.0,
                "per_year": {
                    "2022": {
                        "elec_mwh": 5000.0,
                        "rocs_required": 1850.0,
                        "obligation_level": 0.370,
                        "buy_out_price_gbp": 52.88,
                        "buy_out_cost_gbp": 97828.0,
                    },
                    "2023": {
                        "elec_mwh": 5100.0,
                        "rocs_required": 1917.6,
                        "obligation_level": 0.376,
                        "buy_out_price_gbp": 54.35,
                        "buy_out_cost_gbp": 104242.0,
                    },
                },
            },
            "management_accounts": {
                "2022": {"income_statement": {"revenue_gbp": 1500000.0}},
                "2023": {"income_statement": {"revenue_gbp": 1600000.0}},
            },
        }

    def _render(self):
        from saas.reporting.annual_report import _section_roc_obligations
        return _section_roc_obligations(self._make_data())

    def test_section_renders(self):
        out = self._render()
        assert "Renewable Obligation" in out

    def test_section_shows_years(self):
        out = self._render()
        assert "2022" in out
        assert "2023" in out

    def test_section_shows_mwh(self):
        out = self._render()
        assert "5,000" in out or "5000" in out

    def test_section_shows_buy_out_cost(self):
        out = self._render()
        assert "97,828" in out or "97828" in out

    def test_section_shows_revenue_pct(self):
        out = self._render()
        assert "%" in out

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_roc_obligations
        assert _section_roc_obligations({}) == ""

    def test_section_shows_total_row(self):
        out = self._render()
        assert "Total" in out
