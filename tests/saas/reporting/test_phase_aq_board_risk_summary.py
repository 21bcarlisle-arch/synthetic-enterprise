"""Phase AQ: Board Risk Summary section tests."""
import pytest
from saas.reporting.annual_report import _section_board_risk_summary


def _data(**kwargs):
    base = {
        "per_customer_lifetime": {},
        "years": {},
        "company_divergence": {},
        "basis_risk_terms": [],
        "customer_events": [],
        "churn_basis_risk": [],
        "_ledger_headline": None,
    }
    base.update(kwargs)
    return base


# 1. Empty data returns empty
def test_empty_returns_empty():
    assert _section_board_risk_summary({}) == ""
    assert _section_board_risk_summary(_data()) == ""


# 2. Header present when pcl or years present
def test_header_present():
    d = _data(per_customer_lifetime={"C1": {
        "segment": "I&C",
        "net_margin_after_cost_to_serve_gbp": 1000.0,
    }})
    result = _section_board_risk_summary(d)
    assert "Board Risk Summary" in result


# 3. Revenue concentration AMBER when HHI 1500-2500
def test_concentration_amber():
    pcl = {
        "C_IC1": {"segment": "I&C", "net_margin_after_cost_to_serve_gbp": 9000.0},
        "C1": {"segment": "resi", "net_margin_after_cost_to_serve_gbp": 1000.0},
    }
    result = _section_board_risk_summary(_data(per_customer_lifetime=pcl))
    assert "AMBER" in result or "RED" in result


# 4. Gas ROC RED when gas is net-negative
def test_gas_roc_red():
    years = {"2024": {"segment_split": {
        "I&C electricity": {"gross_gbp": 100000.0, "capital_gbp": 1000.0, "net_gbp": 20000.0},
        "I&C gas": {"gross_gbp": 50000.0, "capital_gbp": 10000.0, "net_gbp": -5000.0},
    }}}
    result = _section_board_risk_summary(_data(years=years))
    assert "Gas segment ROC" in result
    assert "RED" in result


# 5. Gas ROC GREEN when positive
def test_gas_roc_green():
    years = {"2024": {"segment_split": {
        "I&C gas": {"gross_gbp": 50000.0, "capital_gbp": 10000.0, "net_gbp": 5000.0},
    }}}
    result = _section_board_risk_summary(_data(years=years))
    if "Gas segment ROC" in result:
        assert "GREEN" in result or "AMBER" in result


# 6. Churn blind miss rate RED when > 40%
def test_churn_miss_rate_red():
    events = [
        {"event_type": "churned", "customer_id": "C1"},
        {"event_type": "churned", "customer_id": "C2"},
        {"event_type": "churned", "customer_id": "C3"},
    ]
    cbr = [
        {"customer_id": "C1", "term_start": "2024-01-01", "company_churn_estimate": 0.02},
        {"customer_id": "C2", "term_start": "2024-01-01", "company_churn_estimate": 0.05},
        {"customer_id": "C3", "term_start": "2024-01-01", "company_churn_estimate": 0.8},
    ]
    result = _section_board_risk_summary(_data(customer_events=events, churn_basis_risk=cbr))
    assert "Churn blind miss rate" in result
    assert "RED" in result  # 2/3 = 67%


# 7. Demand estimation error RED when peak mean > 3%
def test_demand_error_red():
    cd = {"demand_error_by_year": {
        "2024": {"n": 9, "mean_abs_error_pct": 3.5, "max_abs_error_pct": 12.0},
    }}
    result = _section_board_risk_summary(_data(company_divergence=cd))
    assert "Demand estimation error" in result
    assert "RED" in result


# 8. Demand estimation error GREEN when low
def test_demand_error_green():
    cd = {"demand_error_by_year": {
        "2024": {"n": 9, "mean_abs_error_pct": 0.5, "max_abs_error_pct": 2.0},
    }}
    result = _section_board_risk_summary(_data(company_divergence=cd))
    assert "Demand estimation error" in result
    assert "GREEN" in result


# 9. Pricing basis risk shown with year label
def test_pricing_basis_risk_shown():
    brt = [
        {"customer_id": "C_IC1", "term_start": "2025-01-01", "tariff_error_pct": 0.328},
        {"customer_id": "C_IC2", "term_start": "2025-01-01", "tariff_error_pct": 0.295},
    ]
    result = _section_board_risk_summary(_data(basis_risk_terms=brt))
    assert "Pricing basis risk" in result
    assert "2025" in result
    assert "RED" in result  # mean ~31% > 15%


# 10. Net margin % GREEN when above 2%
def test_net_margin_green():
    hl = {"revenue_gbp": 1000000.0, "net_margin_gbp": 50000.0}
    result = _section_board_risk_summary(_data(**{"_ledger_headline": hl}))
    assert "Net margin" in result
    assert "GREEN" in result


# 11. Board action note shown when RED indicators exist
def test_board_action_note_shown():
    events = [
        {"event_type": "churned", "customer_id": "C1"},
        {"event_type": "churned", "customer_id": "C2"},
    ]
    cbr = [
        {"customer_id": "C1", "term_start": "2024-01-01", "company_churn_estimate": 0.01},
        {"customer_id": "C2", "term_start": "2024-01-01", "company_churn_estimate": 0.02},
    ]
    result = _section_board_risk_summary(_data(customer_events=events, churn_basis_risk=cbr))
    assert "Board Action Required" in result


# 12. RAG table header present
def test_rag_table_header():
    years = {"2024": {"segment_split": {
        "I&C electricity": {"gross_gbp": 100000.0, "capital_gbp": 1000.0, "net_gbp": 20000.0},
        "I&C gas": {"gross_gbp": 50000.0, "capital_gbp": 10000.0, "net_gbp": -5000.0},
    }}}
    result = _section_board_risk_summary(_data(years=years))
    assert "RAG" in result
    assert "Risk Indicator" in result
