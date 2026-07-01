"""Tests for FI2: Budget vs Actual (Phase 65)."""

import pytest
from company.finance.budget import (
    _BUDGET_BY_YEAR,
    get_annual_budget,
    monthly_variance,
    traffic_light,
    variance_report,
)


# --- budget constants ---

def test_budget_constants_present_2016_2025():
    for year in range(2016, 2026):
        b = get_annual_budget(year)
        assert b, f"No budget entry for {year}"
        assert all(k in b for k in ("revenue", "cogs", "gross", "opex", "net")), year


def test_budget_tolerates_missing_year():
    b = get_annual_budget(2099)
    assert b == {}


# --- traffic_light ---

def test_traffic_light_green_under_5pct():
    assert traffic_light(0.0) == "GREEN"
    assert traffic_light(4.9) == "GREEN"
    assert traffic_light(-4.9) == "GREEN"


def test_traffic_light_amber_5_to_15pct():
    assert traffic_light(5.0) == "AMBER"
    assert traffic_light(14.9) == "AMBER"
    assert traffic_light(-10.0) == "AMBER"


def test_traffic_light_red_over_15pct():
    assert traffic_light(15.0) == "RED"
    assert traffic_light(100.0) == "RED"
    assert traffic_light(-50.0) == "RED"


# --- variance_report ---

def _make_annual_pack(**overrides):
    defaults = {
        "revenue_gbp": 100_000.0,
        "gross_margin_gbp": 15_000.0,
        "net_margin_gbp": 5_000.0,
    }
    defaults.update(overrides)
    return {"2020": {"income_statement": defaults, "balance_sheet": {}}}


def test_variance_report_structure():
    budget = {"revenue": 100_000.0, "cogs": 85_000.0, "gross": 15_000.0,
              "opex": 10_000.0, "net": 5_000.0}
    pack = _make_annual_pack()
    result = variance_report(pack, "2020", budget=budget)
    assert set(result.keys()) == {"revenue", "gross", "net"}
    for key in ("revenue", "gross", "net"):
        assert all(k in result[key] for k in ("budget", "actual", "variance_gbp", "variance_pct"))


def test_variance_zero_when_actual_equals_budget():
    budget = {"revenue": 100_000.0, "cogs": 85_000.0, "gross": 15_000.0,
              "opex": 10_000.0, "net": 5_000.0}
    pack = _make_annual_pack(revenue_gbp=100_000.0, gross_margin_gbp=15_000.0,
                              net_margin_gbp=5_000.0)
    result = variance_report(pack, "2020", budget=budget)
    assert result["net"]["variance_pct"] == 0.0
    assert result["revenue"]["variance_pct"] == 0.0


def test_variance_positive_when_actual_beats_budget():
    budget = {"revenue": 100_000.0, "cogs": 85_000.0, "gross": 15_000.0,
              "opex": 10_000.0, "net": 5_000.0}
    pack = _make_annual_pack(net_margin_gbp=6_000.0)
    result = variance_report(pack, "2020", budget=budget)
    assert result["net"]["variance_gbp"] > 0
    assert result["net"]["variance_pct"] == 20.0


def test_variance_negative_when_actual_misses():
    budget = {"revenue": 100_000.0, "cogs": 85_000.0, "gross": 15_000.0,
              "opex": 10_000.0, "net": 5_000.0}
    pack = _make_annual_pack(net_margin_gbp=4_000.0)
    result = variance_report(pack, "2020", budget=budget)
    assert result["net"]["variance_gbp"] < 0
    assert result["net"]["variance_pct"] == -20.0


def test_variance_report_missing_year_returns_empty():
    pack = _make_annual_pack()
    result = variance_report(pack, "2099")
    assert result == {}


def test_2022_crisis_year_shows_red_net():
    import json
    from pathlib import Path
    p = Path("docs/reports/run_output_latest.json")
    if not p.exists():
        pytest.skip("run_output_latest.json not present")
    with open(p) as f:
        data = json.load(f)
    pack = data.get("management_accounts")
    if not pack:
        pytest.skip("No management_accounts in run_output_latest.json")
    result = variance_report(pack, "2022")
    if not result:
        pytest.skip("No 2022 data in management accounts")
    rag = traffic_light(result["net"]["variance_pct"])
    assert rag in ("AMBER", "RED"), f"Expected anomalous 2022 net variance (got {rag}): crisis year should not be GREEN"


def test_monthly_variance_returns_12_months():
    monthly_pack = {
        "2020": {
            str(m).zfill(2): {"revenue_gbp": 10_000.0,
                               "gross_margin_gbp": 1_500.0,
                               "net_margin_gbp": 500.0}
            for m in range(1, 13)
        }
    }
    result = monthly_variance(monthly_pack, "2020")
    assert len(result) == 12
    assert "01" in result and "12" in result
    for m in result.values():
        assert set(m.keys()) == {"revenue", "gross", "net"}


# --- Phase LV depth tests ---

def test_budget_has_revenue_key_2022():
    b = get_annual_budget(2022)
    assert 'revenue' in b


def test_budget_has_net_key_2022():
    b = get_annual_budget(2022)
    assert 'net' in b


def test_budget_has_gross_key_2022():
    b = get_annual_budget(2022)
    assert 'gross' in b


def test_budget_has_opex_key_2022():
    b = get_annual_budget(2022)
    assert 'opex' in b


def test_budget_has_cogs_key_2022():
    b = get_annual_budget(2022)
    assert 'cogs' in b


def test_budget_revenue_positive_2022():
    b = get_annual_budget(2022)
    assert b['revenue'] > 0


def test_traffic_light_amber_boundaries():
    assert traffic_light(5.0) == 'AMBER'
    assert traffic_light(14.9) == 'AMBER'


def test_traffic_light_red_at_15pct():
    assert traffic_light(15.0) == 'RED'


def test_budget_integer_year_works():
    b = get_annual_budget(2022)
    assert b is not None
    assert b != {}


def test_budget_2016_through_2025_all_five_keys():
    for yr in range(2016, 2026):
        b = get_annual_budget(yr)
        assert len(b) == 5, f'Missing keys for {yr}'
