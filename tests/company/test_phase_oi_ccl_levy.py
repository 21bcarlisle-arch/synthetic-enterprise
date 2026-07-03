"""Tests for Phase OI: Climate Change Levy (CCL) Observatory."""
import pytest
from company.regulatory.ccl_ledger import (
    CCLLedger,
    CCLFuel,
    CCLCharge,
    CCLExemptReason,
    CCLQuarterlyReturn,
    _CCL_ELECTRICITY_P_KWH,
    _CCL_GAS_P_KWH,
)
import datetime as dt


class TestCCLRateHistory:
    def test_2019_electricity_rate_spike(self):
        """2019: electricity CCL +45% per Budget 2018."""
        assert _CCL_ELECTRICITY_P_KWH[2019] == pytest.approx(0.847)
        assert _CCL_ELECTRICITY_P_KWH[2018] == pytest.approx(0.583)

    def test_2019_gas_rate_spike(self):
        """2019: gas CCL +67% per Budget 2018."""
        assert _CCL_GAS_P_KWH[2019] == pytest.approx(0.339)
        assert _CCL_GAS_P_KWH[2018] == pytest.approx(0.203)

    def test_2021_to_2025_electricity_stable(self):
        for yr in [2021, 2022, 2023, 2024, 2025]:
            assert _CCL_ELECTRICITY_P_KWH[yr] == pytest.approx(0.775)

    def test_2021_to_2025_gas_stable(self):
        for yr in [2021, 2022, 2023, 2024, 2025]:
            assert _CCL_GAS_P_KWH[yr] == pytest.approx(0.465)


class TestCCLLedgerRateForYear:
    def test_rate_for_electricity_2019(self):
        ledger = CCLLedger()
        assert ledger.rate_for_year(2019, CCLFuel.ELECTRICITY) == pytest.approx(0.847)

    def test_rate_for_gas_2022(self):
        ledger = CCLLedger()
        assert ledger.rate_for_year(2022, CCLFuel.GAS) == pytest.approx(0.465)

    def test_rate_for_unknown_year_closest(self):
        ledger = CCLLedger()
        rate = ledger.rate_for_year(2030, CCLFuel.ELECTRICITY)
        assert rate == pytest.approx(_CCL_ELECTRICITY_P_KWH[2025])


class TestCCLChargeCalculation:
    def test_business_customer_pays(self):
        ledger = CCLLedger()
        charge = ledger.record_charge(
            "IC-001", 2022, CCLFuel.ELECTRICITY, 100000.0,
            is_business=True
        )
        expected = round(100000.0 * 0.775 / 100, 2)
        assert charge.charge_gbp == pytest.approx(expected)

    def test_residential_exempt(self):
        ledger = CCLLedger()
        charge = ledger.record_charge(
            "R-001", 2022, CCLFuel.ELECTRICITY, 100000.0,
            is_business=False
        )
        assert charge.is_exempt
        assert charge.charge_gbp == pytest.approx(0.0)

    def test_lec_covered_exempt(self):
        ledger = CCLLedger()
        charge = ledger.record_charge(
            "IC-002", 2022, CCLFuel.ELECTRICITY, 100000.0,
            is_business=True, lec_covered=True
        )
        assert charge.is_exempt
        assert charge.charge_gbp == pytest.approx(0.0)

    def test_charge_proportional_to_consumption(self):
        ledger = CCLLedger()
        c1 = ledger.record_charge("IC-003", 2020, CCLFuel.ELECTRICITY, 50000.0, is_business=True)
        c2 = ledger.record_charge("IC-004", 2020, CCLFuel.ELECTRICITY, 100000.0, is_business=True)
        assert c2.charge_gbp == pytest.approx(2 * c1.charge_gbp, rel=1e-4)


class TestCCLQuarterlyReturn:
    def test_total_due(self):
        r = CCLQuarterlyReturn(
            quarter_end=dt.date(2022, 3, 31),
            electricity_kwh=500000.0,
            gas_kwh=100000.0,
            electricity_due_gbp=3875.0,
            gas_due_gbp=465.0,
        )
        assert r.total_due_gbp == pytest.approx(4340.0)

    def test_nil_return_flag(self):
        r = CCLQuarterlyReturn(
            quarter_end=dt.date(2022, 3, 31),
            electricity_kwh=0.0, gas_kwh=0.0,
            electricity_due_gbp=0.0, gas_due_gbp=0.0,
        )
        assert r.is_nil_return


class TestCCLBoardSection:
    def _make_data(self):
        return {
            "ccl_summary": {
                "total_ccl_gbp": 28600.0,
                "per_year": {
                    "2018": {
                        "elec_kwh": 2000000, "gas_kwh": 0,
                        "elec_rate_p_per_kwh": 0.583, "gas_rate_p_per_kwh": 0.203,
                        "ccl_elec_gbp": 11660.0, "ccl_gas_gbp": 0.0, "ccl_total_gbp": 11660.0,
                    },
                    "2019": {
                        "elec_kwh": 2000000, "gas_kwh": 0,
                        "elec_rate_p_per_kwh": 0.847, "gas_rate_p_per_kwh": 0.339,
                        "ccl_elec_gbp": 16940.0, "ccl_gas_gbp": 0.0, "ccl_total_gbp": 16940.0,
                    },
                },
            },
            "management_accounts": {},
        }

    def _render(self):
        from saas.reporting.annual_report import _section_ccl_levy
        return _section_ccl_levy(self._make_data())

    def test_section_renders(self):
        assert "Climate Change Levy" in self._render()

    def test_section_shows_2019_spike_marker(self):
        assert "(*)" in self._render()

    def test_section_shows_pass_through_note(self):
        assert "pass-through" in self._render()

    def test_section_shows_total_row(self):
        assert "Total" in self._render()

    def test_section_empty_without_data(self):
        from saas.reporting.annual_report import _section_ccl_levy
        assert _section_ccl_levy({}) == ""

    def test_section_shows_rate_spike_explanation(self):
        assert "0.583" in self._render() or "0.847" in self._render()
