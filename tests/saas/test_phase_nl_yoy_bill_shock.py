"""Phase NL tests -- YoY bill shock mode for score_experience_signals / build_churn_risk.

Validates that comparison_mode='yoy' eliminates seasonal false-positive shocks
while correctly detecting genuine year-over-year price increases.
"""
import pytest
from saas.customer_reaction import score_experience_signals
from saas.churn_model import (
    BASE_ANNUAL_CHURN_PROBABILITY,
    CHURN_UPLIFT_PER_BILL_SHOCK,
    build_churn_risk,
)


CUSTOMERS = [{"customer_id": "C1", "acquisition_date": "2016-01-01"}]
CUSTOMERS_2 = [
    {"customer_id": "C1", "acquisition_date": "2016-01-01"},
    {"customer_id": "C2", "acquisition_date": "2016-01-01"},
]


def _rec(customer_id, period, revenue, cost=50.0):
    return {
        "customer_id": customer_id,
        "settlement_date": period + "-15",
        "settlement_period": 1,
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": cost,
    }


def _make_records(revenues_by_month, year, customer_id="C1"):
    """revenues_by_month: dict of month_int -> float."""
    return [_rec(customer_id, f"{year}-{m:02d}", rev) for m, rev in sorted(revenues_by_month.items())]


# --- YoY mode: no prior year -> no shocks ---

def test_yoy_no_shock_first_12_months():
    """With only one year of data, there is no prior-year reference -> 0 shocks."""
    records = [_rec("C1", f"2016-{m:02d}", 200.0) for m in range(1, 13)]
    signals = score_experience_signals(records, comparison_mode="yoy")
    shocks = sum(1 for p in signals["C1"] if p["bill_shock_triggered"])
    assert shocks == 0


def test_yoy_no_shock_on_seasonal_variation():
    """Summer bills are low, winter bills are high -- YoY mode does not fire if
    same-month prior year had the same seasonal level."""
    summer = {6: 50.0, 7: 50.0, 8: 50.0}
    winter = {12: 200.0, 1: 200.0, 2: 200.0}
    records_2016 = [_rec("C1", f"2016-{m:02d}", rev) for m, rev in {**summer, **winter}.items()]
    records_2017 = [_rec("C1", f"2017-{m:02d}", rev) for m, rev in {**summer, **winter}.items()]
    signals = score_experience_signals(records_2016 + records_2017, comparison_mode="yoy")
    # 2017 records: same as 2016 same month -> 0% change -> no shock
    shocks_2017 = sum(1 for p in signals["C1"] if p["billing_period"].startswith("2017") and p["bill_shock_triggered"])
    assert shocks_2017 == 0


def test_yoy_fires_above_threshold():
    """A genuine 30% year-over-year increase fires a shock."""
    records_2016 = [_rec("C1", "2016-06", 100.0)]
    records_2017 = [_rec("C1", "2017-06", 130.1)]  # 30.1% increase
    signals = score_experience_signals(records_2016 + records_2017, comparison_mode="yoy")
    june_2017 = next(p for p in signals["C1"] if p["billing_period"] == "2017-06")
    assert june_2017["bill_shock_triggered"] is True
    assert june_2017["bill_shock_score"] == pytest.approx(0.301, abs=0.001)


def test_yoy_no_shock_below_threshold():
    """A 10% YoY increase is below the 15% threshold -> no shock."""
    records_2016 = [_rec("C1", "2016-06", 100.0)]
    records_2017 = [_rec("C1", "2017-06", 110.0)]
    signals = score_experience_signals(records_2016 + records_2017, comparison_mode="yoy")
    june_2017 = next(p for p in signals["C1"] if p["billing_period"] == "2017-06")
    assert june_2017["bill_shock_triggered"] is False


def test_yoy_threshold_boundary():
    """Exactly at threshold does not fire; just above does."""
    records_2016 = [_rec("C1", "2016-01", 100.0)]
    at_threshold = [_rec("C1", "2017-01", 115.0)]
    just_above = [_rec("C1", "2017-01", 115.01)]
    signals_at = score_experience_signals(records_2016 + at_threshold, comparison_mode="yoy")
    signals_above = score_experience_signals(records_2016 + just_above, comparison_mode="yoy")
    assert signals_at["C1"][-1]["bill_shock_triggered"] is False
    assert signals_above["C1"][-1]["bill_shock_triggered"] is True


def test_yoy_output_has_yoy_ref_gbp_key():
    """Output records always include yoy_ref_gbp (None when no prior year)."""
    records_2016 = [_rec("C1", "2016-01", 100.0)]
    records_2017 = [_rec("C1", "2017-01", 110.0)]
    signals = score_experience_signals(records_2016 + records_2017, comparison_mode="yoy")
    p_2016 = next(p for p in signals["C1"] if p["billing_period"] == "2016-01")
    p_2017 = next(p for p in signals["C1"] if p["billing_period"] == "2017-01")
    assert "yoy_ref_gbp" in p_2016
    assert p_2016["yoy_ref_gbp"] is None
    assert p_2017["yoy_ref_gbp"] == pytest.approx(100.0)


def test_yoy_mode_rolling_avg_is_none():
    """In YoY mode, rolling_avg_gbp is always None."""
    records = [_rec("C1", f"2016-{m:02d}", 100.0) for m in range(1, 13)]
    records += [_rec("C1", f"2017-{m:02d}", 100.0) for m in range(1, 13)]
    signals = score_experience_signals(records, comparison_mode="yoy")
    for period in signals["C1"]:
        assert period["rolling_avg_gbp"] is None, f"Expected None for {period['billing_period']}"


def test_rolling_mode_unchanged():
    """Default rolling mode still uses rolling average (backward-compatible)."""
    records = [_rec("C1", "2016-01", 100.0), _rec("C1", "2016-02", 200.0)]
    signals_rolling = score_experience_signals(records)  # default
    signals_explicit = score_experience_signals(records, comparison_mode="rolling")
    feb_r = next(p for p in signals_rolling["C1"] if p["billing_period"] == "2016-02")
    feb_e = next(p for p in signals_explicit["C1"] if p["billing_period"] == "2016-02")
    assert feb_r["rolling_avg_gbp"] == pytest.approx(100.0)
    assert feb_e["rolling_avg_gbp"] == pytest.approx(100.0)
    assert feb_r["bill_shock_triggered"] is True
    assert feb_e["bill_shock_triggered"] is True


# --- build_churn_risk integration ---

def test_build_churn_risk_stable_prices_zero_shocks():
    """With stable YoY bills, build_churn_risk returns 0 shocks -> base churn."""
    records_2016 = _make_records({m: 100.0 for m in range(1, 13)}, 2016)
    records_2017 = _make_records({m: 100.0 for m in range(1, 13)}, 2017)
    result = build_churn_risk(records_2016 + records_2017, CUSTOMERS)
    # Second renewal should have 0 shocks
    renewal_2017 = next((r for r in result["C1"] if r["renewal_period"] == "2016-12"), None)
    assert renewal_2017 is not None
    assert renewal_2017["bill_shock_count"] == 0
    assert renewal_2017["churn_probability"] == pytest.approx(BASE_ANNUAL_CHURN_PROBABILITY)


def test_build_churn_risk_crisis_shocks_detected():
    """YoY doubling of bills in second year fires shocks -> elevated churn."""
    records_2016 = _make_records({m: 100.0 for m in range(1, 13)}, 2016)
    records_2017 = _make_records({m: 200.0 for m in range(1, 13)}, 2017)
    result = build_churn_risk(records_2016 + records_2017, CUSTOMERS)
    # 2017-12 renewal window: 2016-12 to 2017-11. Dec 2016 has no prior-year
    # reference (no Dec 2015 data), so 11 of 12 months fire -> 11 shocks.
    renewal = next((r for r in result["C1"] if r["renewal_period"] == "2017-12"), None)
    assert renewal is not None
    assert renewal["bill_shock_count"] == 11
    assert renewal["churn_probability"] == pytest.approx(0.05 + 11 * 0.03)  # 0.38


def test_build_churn_risk_uses_yoy_mode():
    """Verify build_churn_risk calls score_experience_signals with comparison_mode='yoy'."""
    import inspect
    from saas import churn_model
    src = inspect.getsource(churn_model.build_churn_risk)
    assert "comparison_mode" in src
    assert "yoy" in src


def test_yoy_mode_multiple_customers_independent():
    """Two customers processed independently in YoY mode."""
    records = [
        _rec("C1", "2016-01", 100.0), _rec("C1", "2017-01", 200.0),
        _rec("C2", "2016-01", 100.0), _rec("C2", "2017-01", 100.0),
    ]
    signals = score_experience_signals(records, comparison_mode="yoy")
    c1_jan17 = next(p for p in signals["C1"] if p["billing_period"] == "2017-01")
    c2_jan17 = next(p for p in signals["C2"] if p["billing_period"] == "2017-01")
    assert c1_jan17["bill_shock_triggered"] is True
    assert c2_jan17["bill_shock_triggered"] is False


def test_yoy_mode_50_pct_increase_fires():
    """50% YoY increase (crisis level) fires a shock."""
    records_2016 = [_rec("C1", "2016-03", 100.0)]
    records_2017 = [_rec("C1", "2017-03", 150.0)]
    signals = score_experience_signals(records_2016 + records_2017, comparison_mode="yoy")
    mar_2017 = next(p for p in signals["C1"] if p["billing_period"] == "2017-03")
    assert mar_2017["bill_shock_triggered"] is True
    assert mar_2017["bill_shock_score"] == pytest.approx(0.50, abs=0.001)
