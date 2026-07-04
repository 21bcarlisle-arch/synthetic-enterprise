"""Tests for the churn-model evidence retrofit (Phase QJ), the third and
final item in EVIDENCE_IN_BUSINESS_SURFACES.md retrofit queue: the three-
signal churn model (SIM churn probability, Phase QB market-switching
multiplier, company estimate) must be visible on the business surfaces --
a real signal-vs-accuracy panel on the Sim tab, and one real renewal
decision shown on both sides of the epistemic wall on the Supplier tab."""
from tools.generate_dashboard_data import extract_customers
from tools.generate_shadow_html import _churn_model_signal, _renewal_decision_case_study


def test_events_export_carries_market_signal_and_realized_churn():
    data = {
        "customer_events": [
            {"customer_id": "C1", "event_date": "2020-01-01", "event_type": "renewed",
             "commodity": "electricity", "churn_probability": 0.2, "company_churn_estimate": 0.3,
             "retention_offered": False, "market_switching_multiplier": 1.5,
             "realized_churn_probability": 0.1},
        ],
        "retention_log": [],
        "per_customer_lifetime": {},
    }
    out = extract_customers(data)
    ev = out["events"][0]
    assert ev["market_signal"] == 1.5
    assert ev["realized_churn_p"] == 0.1


def test_retention_export_cross_references_sim_side_by_customer_and_date():
    data = {
        "customer_events": [
            {"customer_id": "C5", "event_date": "2021-12-30", "event_type": "renewed",
             "commodity": "electricity", "churn_probability": 0.17, "company_churn_estimate": 0.4921,
             "retention_offered": True, "market_switching_multiplier": 0.7407,
             "realized_churn_probability": 0.09},
        ],
        "retention_log": [
            {"customer_id": "C5", "event_date": "2021-12-30", "company_churn_estimate": 0.4921,
             "discount_pct": 0.03, "retention_cost_gbp": 198.22, "outcome": "retained"},
        ],
        "per_customer_lifetime": {},
    }
    out = extract_customers(data)
    r = out["retention"][0]
    assert r["sim_churn_p"] == 0.17
    assert r["market_signal"] == 0.7407
    assert r["realized_churn_p"] == 0.09


def test_retention_export_leaves_sim_side_none_when_no_matching_event():
    data = {
        "customer_events": [],
        "retention_log": [
            {"customer_id": "C8", "event_date": "2017-04-01", "company_churn_estimate": 0.345,
             "discount_pct": 0.03, "retention_cost_gbp": 46.0, "outcome": "retained"},
        ],
        "per_customer_lifetime": {},
    }
    out = extract_customers(data)
    r = out["retention"][0]
    assert r["sim_churn_p"] is None
    assert r["market_signal"] is None
    assert r["realized_churn_p"] is None


def test_churn_model_signal_averages_market_signal_by_year():
    events = [
        {"date": "2022-01-01", "market_signal": 1.0},
        {"date": "2022-06-01", "market_signal": 3.0},
        {"date": "2023-01-01", "market_signal": 2.0},
    ]
    perf = {
        "recall": 0.0, "precision": 0.0, "f1_score": 0.0, "total_churn_events": 4,
        "per_year": {
            "2022": {"tp": 0, "fp": 1, "fn": 0, "recall": 0.0, "precision": 0.0},
            "2023": {"tp": 0, "fp": 0, "fn": 1, "recall": 0.0, "precision": 0.0},
        },
    }
    html = _churn_model_signal(events, perf)
    assert "<td>2022</td><td>2.00</td><td>0</td><td>1</td><td>0</td>" in html
    assert "<td>2023</td><td>2.00</td><td>0</td><td>0</td><td>1</td>" in html
    assert "F1 0.000" in html


def test_churn_model_signal_missing_data_returns_empty():
    assert _churn_model_signal([], {}) == ""
    assert _churn_model_signal(None, None) == ""


def test_renewal_decision_picks_the_widest_divergence():
    retention = [
        {"customer_id": "C1", "date": "2020-01-01", "company_est": 0.35, "sim_churn_p": 0.30,
         "market_signal": 1.0, "realized_churn_p": 0.2, "discount_pct": 0.03, "cost_gbp": 20.0,
         "outcome": "retained"},
        {"customer_id": "C_IC1", "date": "2018-01-31", "company_est": 0.95, "sim_churn_p": 0.05,
         "market_signal": 1.63, "realized_churn_p": 0.04, "discount_pct": 0.08, "cost_gbp": 24227.89,
         "outcome": "retained"},
        {"customer_id": "C9", "date": "2019-01-01", "company_est": 0.4, "sim_churn_p": None,
         "market_signal": None, "realized_churn_p": None, "discount_pct": 0.03, "cost_gbp": 15.0,
         "outcome": "retained"},
    ]
    html = _renewal_decision_case_study(retention)
    assert "C_IC1 on 2018-01-31" in html
    assert "overestimated the SIM ground truth by 90.0 percentage points" in html


def test_renewal_decision_no_matched_records_returns_empty():
    assert _renewal_decision_case_study([]) == ""
    assert _renewal_decision_case_study([{"customer_id": "C1", "sim_churn_p": None}]) == ""
