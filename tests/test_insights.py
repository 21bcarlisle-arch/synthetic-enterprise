"""Tests for tools.generate_insights -- Phase 257."""
import json
import pytest
from pathlib import Path
from tools.generate_insights import (
    generate_insights, save_insights, append_run_history,
    InsightArea, AreaInsight, RunInsights,
)

_MINIMAL = {
    "_ledger_headline": {
        "net_margin_gbp": 1_000_000.0,
        "gross_margin_gbp": 1_200_000.0,
        "revenue_gbp": 5_000_000.0,
    },
    "total_net_gbp": 1_000_000.0,
    "administration_event": None,
    "committee_wake_ups_total": 5,
    "bills_total": 200,
    "avg_clarity_total": 0.85,
    "service_quality_score": 0.91,
    "cost_to_serve_portfolio_gbp": 50_000.0,
    "net_margin_after_cost_to_serve_gbp": 950_000.0,
    "enterprise_value_gbp": 800_000.0,
    "enterprise_value_account_count": 4,
    "retention_log": [
        {"outcome": "retained"},
        {"outcome": "retained"},
        {"outcome": "churned"},
    ],
    "no_offer_churn_log": [{"customer_id": "C1"}],
    "churned_billing_accounts": ["C1", "C2"],
    "per_customer_lifetime": {
        "C_IC1": {"net_margin_gbp": 800_000.0},
        "C1": {"net_margin_gbp": 150_000.0},
        "C2": {"net_margin_gbp": 50_000.0},
    },
    "years": {
        "2021": {
            "net_gbp": 100_000.0,
            "committee_wake_ups": 1,
            "bill_shock_events": [
                {"customer_id": "C1", "period_end": "2021-06-30", "bill_shock_pct": 0.3}
            ],
            "hedge_effectiveness": {
                "actual_net_gbp": 50_000.0,
                "naked_net_gbp": 80_000.0,
                "hedging_value_add_gbp": -30_000.0,
            },
        },
        "2022": {
            "net_gbp": 200_000.0,
            "committee_wake_ups": 4,
            "bill_shock_events": [
                {"customer_id": "C1", "period_end": "2022-10-31", "bill_shock_pct": 1.5},
                {"customer_id": "C2", "period_end": "2022-11-30", "bill_shock_pct": 0.5},
            ],
            "hedge_effectiveness": {
                "actual_net_gbp": 100_000.0,
                "naked_net_gbp": 300_000.0,
                "hedging_value_add_gbp": -200_000.0,
            },
        },
    },
}


def test_generate_insights_returns_run_insights():
    ins = generate_insights(_MINIMAL, "abc1234")
    assert isinstance(ins, RunInsights)
    assert ins.git_hash == "abc1234"
    assert ins.net_margin_gbp == 1_000_000.0


def test_five_areas_covered():
    ins = generate_insights(_MINIMAL)
    areas = {i.area for i in ins.insights}
    assert areas == set(InsightArea)


def test_trading_insight_negative_hedge_value():
    ins = generate_insights(_MINIMAL)
    trading = next(i for i in ins.insights if i.area == InsightArea.TRADING)
    assert "cost" in trading.headline.lower()
    assert trading.key_metrics["hedging_cost_gbp"] < 0


def test_trading_insight_worst_year():
    ins = generate_insights(_MINIMAL)
    trading = next(i for i in ins.insights if i.area == InsightArea.TRADING)
    assert trading.key_metrics["worst_year"] in ("2021", "2022")
    assert trading.key_metrics["worst_year_cost_gbp"] < 0


def test_customers_insight_shock_counts():
    ins = generate_insights(_MINIMAL)
    cust = next(i for i in ins.insights if i.area == InsightArea.CUSTOMERS)
    assert cust.key_metrics["total_bill_shocks"] == 3
    assert cust.key_metrics["crisis_year_shocks"] == 3
    assert cust.key_metrics["extreme_shocks_over_100pct"] == 1


def test_customers_insight_retention():
    ins = generate_insights(_MINIMAL)
    cust = next(i for i in ins.insights if i.area == InsightArea.CUSTOMERS)
    assert cust.key_metrics["retention_offers"] == 3
    assert cust.key_metrics["retained"] == 2
    assert cust.key_metrics["no_offer_churns"] == 1


def test_risk_insight_survived():
    ins = generate_insights(_MINIMAL)
    risk = next(i for i in ins.insights if i.area == InsightArea.RISK)
    assert risk.key_metrics["survived"] is True
    assert risk.key_metrics["committee_interventions_total"] == 5


def test_risk_insight_crisis_interventions():
    ins = generate_insights(_MINIMAL)
    risk = next(i for i in ins.insights if i.area == InsightArea.RISK)
    assert risk.key_metrics["crisis_year_interventions"] == 5


def test_financial_insight_above_benchmark():
    ins = generate_insights(_MINIMAL)
    fin = next(i for i in ins.insights if i.area == InsightArea.FINANCIAL)
    assert fin.key_metrics["net_margin_pct"] == pytest.approx(20.0, abs=0.1)
    assert "above" in fin.headline


def test_financial_insight_ic_concentration():
    ins = generate_insights(_MINIMAL)
    fin = next(i for i in ins.insights if i.area == InsightArea.FINANCIAL)
    assert fin.key_metrics["ic_net_pct_of_total"] > 79
    assert "WARNING" in fin.narrative


def test_financial_insight_uses_total_revenue_when_management_accounts_present():
    """2026-07-10, MARGIN_REALISM Step 1/E2: the commodity-only revenue
    (_ledger_headline/total_revenue_gbp, ~5M here) understates the real
    total revenue (management_accounts' double-entry revenue, net of VAT,
    ~10M here) -- net_pct must be computed against the LARGER, total
    figure, not the smaller commodity-only one, matching the Financial
    tab's own Step 1 fix."""
    data = dict(_MINIMAL)
    data["management_accounts"] = {
        "2021": {"income_statement": {"revenue_gbp": 6_000_000.0}},
        "2022": {"income_statement": {"revenue_gbp": 4_000_000.0}},
    }
    ins = generate_insights(data)
    fin = next(i for i in ins.insights if i.area == InsightArea.FINANCIAL)
    # net=1,000,000 / total_revenue=10,000,000 = 10% -- NOT 20% (the
    # commodity-only-revenue result the old code would have produced).
    assert fin.key_metrics["net_margin_pct"] == pytest.approx(10.0, abs=0.1)
    assert "total revenue" in fin.headline


def test_operations_insight_bills_and_quality():
    ins = generate_insights(_MINIMAL)
    ops = next(i for i in ins.insights if i.area == InsightArea.OPERATIONS)
    assert ops.key_metrics["bills_total"] == 200
    assert ops.key_metrics["service_quality_score"] == pytest.approx(0.91)


def test_executive_summary_contains_key_facts():
    ins = generate_insights(_MINIMAL)
    assert len(ins.executive_summary) > 50
    assert "survived" in ins.executive_summary.lower()
    assert "above" in ins.executive_summary.lower()


def test_save_and_load_insights(tmp_path):
    ins = generate_insights(_MINIMAL, "testgit")
    out = tmp_path / "insights.json"
    save_insights(ins, out)
    loaded = json.loads(out.read_text())
    assert loaded["git_hash"] == "testgit"
    assert len(loaded["insights"]) == 5
    assert all("area" in i and "headline" in i for i in loaded["insights"])


def test_append_run_history_accumulates(tmp_path):
    hp = tmp_path / "history.json"
    ins1 = generate_insights(_MINIMAL, "a1b2c3d")
    append_run_history(ins1, hp)
    ins2 = generate_insights(_MINIMAL, "b2c3d4e")
    append_run_history(ins2, hp)
    history = json.loads(hp.read_text())
    assert len(history) == 2
    assert history[0]["git_hash"] == "a1b2c3d"
    assert history[1]["git_hash"] == "b2c3d4e"


def test_append_run_history_deduplicates(tmp_path):
    hp = tmp_path / "history.json"
    ins = generate_insights(_MINIMAL, "deadbeef")
    append_run_history(ins, hp)
    append_run_history(ins, hp)
    history = json.loads(hp.read_text())
    assert len(history) == 1


# ── Phase 259: coherence narrative and recommended actions ────────────────────

def test_coherence_narrative_present():
    ins = generate_insights(_MINIMAL, "abc")
    assert isinstance(ins.coherence_narrative, str)
    assert len(ins.coherence_narrative) > 50


def test_recommended_actions_always_three():
    ins = generate_insights(_MINIMAL, "abc")
    assert len(ins.recommended_actions) == 3
    for a in ins.recommended_actions:
        assert isinstance(a, str) and len(a) > 10


def test_coherence_narrative_mentions_survival():
    ins = generate_insights(_MINIMAL, "abc")
    lower = ins.coherence_narrative.lower()
    assert "surviv" in lower or "administ" in lower


def test_ic_concentration_flagged_in_actions():
    data = dict(_MINIMAL)
    data["per_customer_lifetime"] = {
        "C_IC1": {"net_margin_gbp": 900_000},
        "C_other": {"net_margin_gbp": 100_000, "segment": "resi"},
    }
    ins = generate_insights(data, "abc")
    action_text = " ".join(ins.recommended_actions).lower()
    assert "concentration" in action_text or "i&c" in action_text.lower()


def test_save_and_reload_preserves_coherence(tmp_path):
    from tools.generate_insights import save_insights, RunInsights
    ins = generate_insights(_MINIMAL, "abc")
    path = tmp_path / "ri.json"
    save_insights(ins, path)
    import json
    loaded = json.loads(path.read_text())
    assert "coherence_narrative" in loaded
    assert "recommended_actions" in loaded
    assert len(loaded["recommended_actions"]) == 3


def test_coherence_contains_hedge_info():
    ins = generate_insights(_MINIMAL, "abc")
    lower = ins.coherence_narrative.lower()
    assert "hedge" in lower or "naked" in lower
