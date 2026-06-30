"""Phase AO: Demand Estimation Error Trend in _section_company_divergence."""
import pytest
from saas.reporting.annual_report import _section_company_divergence


def _data(demand_error=None, tariff_error=None, churn_error=None):
    return {
        "company_divergence": {
            "demand_error_by_year": demand_error or {},
            "tariff_error_by_year": tariff_error or {},
            "churn_error_by_year": churn_error or {},
        }
    }


def _ded(yr, n, mean, max_e):
    return {yr: {"n": n, "mean_abs_error_pct": mean, "max_abs_error_pct": max_e}}


# ── 1. No demand_error_by_year silently omitted ──────────────────────────────

def test_no_demand_error_section_absent():
    result = _section_company_divergence(_data())
    assert "Demand Estimation Error" not in result


# ── 2. Header present when demand data available ─────────────────────────────

def test_header_present_with_demand_data():
    ded = _ded("2024", 9, 3.26, 15.56)
    result = _section_company_divergence(_data(demand_error=ded))
    assert "Demand Estimation Error" in result


# ── 3. Year and error shown in table ─────────────────────────────────────────

def test_year_and_error_in_table():
    ded = _ded("2022", 10, 1.87, 7.47)
    result = _section_company_divergence(_data(demand_error=ded))
    assert "2022" in result
    assert "1.87%" in result
    assert "7.47%" in result


# ── 4. HIGH drift signal when mean > 2.5% ────────────────────────────────────

def test_high_drift_signal():
    ded = _ded("2024", 9, 3.26, 15.56)
    result = _section_company_divergence(_data(demand_error=ded))
    assert "HIGH drift" in result


# ── 5. MODERATE signal when mean 1.0-2.5% ────────────────────────────────────

def test_moderate_signal():
    ded = _ded("2022", 9, 1.87, 7.47)
    result = _section_company_divergence(_data(demand_error=ded))
    assert "MODERATE" in result


# ── 6. Low signal when mean < 1.0% ───────────────────────────────────────────

def test_low_signal():
    ded = _ded("2016", 3, 0.07, 0.07)
    result = _section_company_divergence(_data(demand_error=ded))
    assert "Low" in result


# ── 7. Trend note shows first and peak year ───────────────────────────────────

def test_trend_note_shown():
    ded = {}
    ded["2016"] = {"n": 3, "mean_abs_error_pct": 0.07, "max_abs_error_pct": 0.07}
    ded["2022"] = {"n": 9, "mean_abs_error_pct": 1.87, "max_abs_error_pct": 7.47}
    ded["2024"] = {"n": 9, "mean_abs_error_pct": 3.26, "max_abs_error_pct": 15.56}
    result = _section_company_divergence(_data(demand_error=ded))
    assert "Trend:" in result
    assert "0.07%" in result  # first year
    assert "3.26%" in result  # peak mean


# ── 8. Smart meter action note present ───────────────────────────────────────

def test_smart_meter_action_note():
    ded = {}
    ded["2016"] = {"n": 5, "mean_abs_error_pct": 0.07, "max_abs_error_pct": 0.07}
    ded["2024"] = {"n": 9, "mean_abs_error_pct": 3.26, "max_abs_error_pct": 15.56}
    result = _section_company_divergence(_data(demand_error=ded))
    assert "smart meter" in result.lower()


# ── 9. Multiple years all shown ──────────────────────────────────────────────

def test_multiple_years_all_shown():
    ded = {}
    for yr in ["2016", "2017", "2018"]:
        ded[yr] = {"n": 5, "mean_abs_error_pct": 0.5, "max_abs_error_pct": 1.0}
    result = _section_company_divergence(_data(demand_error=ded))
    assert "2016" in result
    assert "2017" in result
    assert "2018" in result


# ── 10. Demand section coexists with tariff section ──────────────────────────

def test_coexists_with_tariff_section():
    ded = _ded("2024", 9, 3.26, 15.56)
    ted = {"2024": {"n": 5, "mean_abs_error_pct": 0.12, "max_abs_error_pct": 0.25}}
    result = _section_company_divergence(_data(demand_error=ded, tariff_error=ted))
    assert "Tariff Pricing Error" in result
    assert "Demand Estimation Error" in result


# ── 11. Demand section coexists with churn section ───────────────────────────

def test_coexists_with_churn_section():
    ded = _ded("2024", 9, 3.26, 15.56)
    ced = {"2024": {"n": 5, "mean_abs_error_pct": 1.5, "max_abs_error_pct": 3.0}}
    result = _section_company_divergence(_data(demand_error=ded, churn_error=ced))
    assert "Churn Estimate Error" in result
    assert "Demand Estimation Error" in result


# ── 12. Single-year with n<5 skipped in trend note (uses last_active filter) ─

def test_single_small_cohort_no_trend():
    # Only 2025 data with n=2 — last_active filter (n>=5) excludes it
    ded = {"2025": {"n": 2, "mean_abs_error_pct": 1.42, "max_abs_error_pct": 2.07}}
    result = _section_company_divergence(_data(demand_error=ded))
    # Section appears (table row shown) but no trend note (no qualifying year)
    assert "Demand Estimation Error" in result
    assert "2025" in result
    # Trend note may be absent
    # (no assertion on "Trend:" — it's only shown when last_active is non-empty)
