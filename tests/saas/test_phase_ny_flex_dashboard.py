"""Tests for Phase NY: Flexibility Revenue Site/ Dashboard + Annual Report Extension."""
import pytest


class TestExtractFlexibility:
    """Tests for generate_dashboard_data.extract_flexibility."""

    def _make_run_data(self, resi_total=0, ic_total=0, resi_per_year=None, ic_per_year=None):
        flex_summary = {
            "total_flexibility_revenue_gbp": float(resi_total),
            "total_cm_revenue_gbp": resi_total * 0.9,
            "total_dfs_revenue_gbp": resi_total * 0.1,
            "enrolled_customer_years": 4 if resi_total > 0 else 0,
            "years_with_revenue": [2023] if resi_total > 0 else [],
            "per_year": resi_per_year or (
                {2023: {"cm_gbp": resi_total * 0.9, "dfs_gbp": resi_total * 0.1,
                        "total_gbp": float(resi_total), "enrolled_customers": 2}}
                if resi_total > 0 else {}
            ),
        }
        ic_summary = {
            "total_ic_flex_revenue_gbp": float(ic_total),
            "enrolled_customer_years": 4 if ic_total > 0 else 0,
            "years_with_revenue": [2023] if ic_total > 0 else [],
            "per_year": ic_per_year or (
                {2023: {"total_net_gbp": float(ic_total), "enrolled_customers": 4,
                        "total_flex_kw": 174.0}}
                if ic_total > 0 else {}
            ),
        }
        return {
            "total_flexibility_revenue_gbp": float(resi_total + ic_total),
            "flexibility_revenue_summary": flex_summary,
            "ic_flexibility_summary": ic_summary,
        }

    def test_returns_dict_with_expected_keys(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(ic_total=1000))
        assert "total_gbp" in result
        assert "resi_total_gbp" in result
        assert "ic_total_gbp" in result
        assert "resi_per_year" in result
        assert "ic_per_year" in result

    def test_total_is_sum_of_resi_and_ic(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(resi_total=500, ic_total=1000))
        assert abs(result["total_gbp"] - 1500.0) < 0.01

    def test_empty_resi_with_ic_data(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(ic_total=2000))
        assert result["resi_total_gbp"] == 0.0
        assert result["ic_total_gbp"] == 2000.0

    def test_ic_per_year_structure(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(ic_total=2258))
        assert "2023" in result["ic_per_year"]
        yr = result["ic_per_year"]["2023"]
        assert "net_gbp" in yr
        assert "enrolled_customers" in yr
        assert "total_flex_kw" in yr

    def test_resi_per_year_structure(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(resi_total=100))
        assert "2023" in result["resi_per_year"]
        yr = result["resi_per_year"]["2023"]
        assert "cm_gbp" in yr
        assert "dfs_gbp" in yr
        assert "total_gbp" in yr

    def test_enrolled_customer_years_ic(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility(self._make_run_data(ic_total=1000))
        assert result["ic_enrolled_customer_years"] == 4

    def test_all_zeros_when_no_data(self):
        from tools.generate_dashboard_data import extract_flexibility
        result = extract_flexibility({})
        assert result["total_gbp"] == 0.0
        assert result["ic_total_gbp"] == 0.0
        assert result["resi_per_year"] == {}
        assert result["ic_per_year"] == {}


class TestFlexRevenueBoardSection:
    """Tests for _section_flexibility_revenue in annual_report.py with IC data."""

    def _make_data(self, ic_total=21000, resi_total=0):
        ic_per_year = {yr: {"total_net_gbp": ic_total / 10, "enrolled_customers": 4,
                            "total_flex_kw": 174.0}
                       for yr in range(2016, 2026)}
        return {
            "total_flexibility_revenue_gbp": float(ic_total + resi_total),
            "flexibility_revenue_summary": {
                "total_flexibility_revenue_gbp": float(resi_total),
                "total_cm_revenue_gbp": 0.0,
                "total_dfs_revenue_gbp": 0.0,
                "enrolled_customer_years": 0,
                "years_with_revenue": [],
                "per_year": {},
            },
            "ic_flexibility_summary": {
                "total_ic_flex_revenue_gbp": float(ic_total),
                "enrolled_customer_years": 40,
                "years_with_revenue": list(range(2016, 2026)),
                "per_year": ic_per_year,
            },
        }

    def test_renders_when_ic_data_present(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data())
        assert "## Flexibility Revenue" in result

    def test_silent_when_no_data(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue({})
        assert result == ""

    def test_ic_header_present(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data())
        assert "I&C Demand Response Revenue" in result

    def test_ic_total_shown(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data(ic_total=21381))
        assert "21,381" in result or "21381" in result

    def test_all_years_in_table(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data())
        for yr in range(2016, 2026):
            assert str(yr) in result

    def test_resi_section_absent_when_no_resi_data(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data(resi_total=0))
        assert "Residential DSR Revenue" not in result

    def test_resi_section_present_when_resi_data(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        data = self._make_data(resi_total=500)
        data["flexibility_revenue_summary"]["years_with_revenue"] = [2023]
        data["flexibility_revenue_summary"]["per_year"] = {
            2023: {"cm_gbp": 450, "dfs_gbp": 50, "total_gbp": 500, "enrolled_customers": 1}
        }
        result = _section_flexibility_revenue(data)
        assert "Residential DSR Revenue" in result

    def test_phase_ag_nx_reference_in_header(self):
        from saas.reporting.annual_report import _section_flexibility_revenue
        result = _section_flexibility_revenue(self._make_data())
        assert "Phase AG/NX" in result or "Phase AG" in result
