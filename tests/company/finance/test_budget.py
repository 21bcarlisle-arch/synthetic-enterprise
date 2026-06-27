import pytest
from company.finance.budget import (
    get_annual_budget,
    traffic_light,
    variance_report,
    monthly_variance,
)


class TestGetAnnualBudget:
    def test_known_year_returns_dict(self):
        b = get_annual_budget(2022)
        assert isinstance(b, dict)
        assert "revenue" in b and "net" in b

    def test_returns_copy(self):
        b1 = get_annual_budget(2022)
        b2 = get_annual_budget(2022)
        b1["revenue"] = 999
        assert b2["revenue"] != 999

    def test_unknown_year_returns_empty(self):
        assert get_annual_budget(1999) == {}

    def test_all_expected_keys(self):
        b = get_annual_budget(2020)
        for k in ("revenue", "cogs", "gross", "opex", "net"):
            assert k in b


class TestTrafficLight:
    def test_small_variance_green(self):
        assert traffic_light(3.0) == "GREEN"
        assert traffic_light(-3.0) == "GREEN"

    def test_medium_variance_amber(self):
        assert traffic_light(10.0) == "AMBER"
        assert traffic_light(-10.0) == "AMBER"

    def test_large_variance_red(self):
        assert traffic_light(20.0) == "RED"
        assert traffic_light(-20.0) == "RED"

    def test_boundary_green_amber(self):
        # 5% is amber boundary
        assert traffic_light(5.0) == "AMBER"
        assert traffic_light(4.9) == "GREEN"


class TestVarianceReport:
    def _accounts(self, year, revenue=500000.0, gross=100000.0, net=80000.0):
        return {
            str(year): {
                "income_statement": {
                    "revenue_gbp": revenue,
                    "gross_margin_gbp": gross,
                    "net_margin_gbp": net,
                }
            }
        }

    def test_returns_empty_for_unknown_year(self):
        result = variance_report({}, 1999)
        assert result == {}

    def test_returns_empty_when_accounts_missing(self):
        result = variance_report({}, 2022)
        assert result == {}

    def test_variance_keys_present(self):
        accounts = self._accounts(2022, revenue=607000.0)
        result = variance_report(accounts, 2022)
        for section in ("revenue", "gross", "net"):
            assert section in result
            assert "variance_pct" in result[section]
            assert "variance_gbp" in result[section]

    def test_positive_variance_when_actual_above_budget(self):
        b = get_annual_budget(2022)
        accounts = self._accounts(2022, revenue=b["revenue"] * 1.10)
        result = variance_report(accounts, 2022)
        assert result["revenue"]["variance_pct"] > 0

    def test_custom_budget_override(self):
        accounts = self._accounts(2022, revenue=200.0)
        custom = {"revenue": 100.0, "gross": 50.0, "net": 40.0}
        result = variance_report(accounts, 2022, budget=custom)
        assert result["revenue"]["budget"] == pytest.approx(100.0)


class TestMonthlyVariance:
    def _monthly(self, year):
        return {
            str(year): {
                "01": {"revenue_gbp": 50000.0, "gross_margin_gbp": 10000.0, "net_margin_gbp": 8000.0},
                "06": {"revenue_gbp": 40000.0, "gross_margin_gbp": 8000.0, "net_margin_gbp": 6000.0},
            }
        }

    def test_returns_empty_for_unknown_year(self):
        assert monthly_variance({}, 1999) == {}

    def test_month_keys_present(self):
        result = monthly_variance(self._monthly(2022), 2022)
        assert "01" in result and "06" in result

    def test_budget_evenly_split(self):
        annual = get_annual_budget(2022)
        result = monthly_variance(self._monthly(2022), 2022)
        # Each month's budget should be 1/12 of annual
        assert result["01"]["revenue"]["budget"] == pytest.approx(annual["revenue"] / 12.0, rel=0.01)
