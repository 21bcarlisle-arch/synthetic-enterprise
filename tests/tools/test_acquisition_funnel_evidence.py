"""Tests for the acquisition-funnel evidence retrofit (PROCESS_NOT_EVENTS.md /
docs/market_research/findings/acquisition_funnel_benchmarks.md): the real
quote-to-onboarding funnel (simulation/acquisition_funnel.py) replacing the
flat coin-flip roll must surface on all three business tabs -- Sim (stage
leakage + win rate over time), Customers (one named won attempt next to its
credit-bureau read, both sides of the epistemic wall), Supplier (portfolio
stage-leakage + real CAC, the new operational monitoring capability)."""
from tools.generate_dashboard_data import extract_customers
from tools.generate_shadow_html import (
    _acquisition_funnel_signal, _pick_acquisition_case_study_cid,
    _acquisition_funnel_case_study, _acquisition_funnel_process,
)


def test_extract_customers_carries_acquisition_funnel_log():
    data = {
        "customer_events": [],
        "retention_log": [],
        "per_customer_lifetime": {},
        "acquisition_funnel_log": [
            {"billing_account": "C1", "segment": "resi", "term_start": "2021-01-01",
             "won": True, "stage_reached": "cooling_off", "total_cost_gbp": 145.0,
             "credit_bureau_score_band": "prime", "credit_bureau_passed": True,
             "credit_bureau_true_creditworthy": True},
        ],
    }
    out = extract_customers(data)
    assert out["acquisition_funnel_log"] == [
        {"billing_account": "C1", "segment": "resi", "term_start": "2021-01-01",
         "won": True, "stage_reached": "cooling_off", "total_cost_gbp": 145.0,
         "credit_bureau_score_band": "prime", "credit_bureau_passed": True,
         "credit_bureau_true_creditworthy": True},
    ]


def test_extract_customers_acquisition_funnel_log_empty_when_absent():
    data = {"customer_events": [], "retention_log": [], "per_customer_lifetime": {}}
    out = extract_customers(data)
    assert out["acquisition_funnel_log"] == []


def test_acquisition_funnel_signal_empty_when_no_log():
    assert _acquisition_funnel_signal([]) == ""


def test_acquisition_funnel_signal_reports_year_and_win_rate():
    funnel_log = [
        {"segment": "resi", "term_start": "2022-01-01", "won": True, "stage_reached": "cooling_off"},
        {"segment": "resi", "term_start": "2022-06-01", "won": False, "stage_reached": "credit_check"},
    ]
    html = _acquisition_funnel_signal(funnel_log)
    assert "2022" in html
    assert "50.0%" in html  # 1 of 2 attempts won
    assert "Lost at Credit Check" in html


def test_pick_acquisition_case_study_cid_prefers_divergence():
    funnel_log = [
        {"billing_account": "C1", "term_start": "2021-01-01", "won": True,
         "credit_bureau_passed": True, "credit_bureau_true_creditworthy": True},
        {"billing_account": "C2", "term_start": "2021-06-01", "won": True,
         "credit_bureau_passed": True, "credit_bureau_true_creditworthy": False},
    ]
    assert _pick_acquisition_case_study_cid(funnel_log) == "C2"


def test_pick_acquisition_case_study_cid_falls_back_to_latest_win():
    funnel_log = [
        {"billing_account": "C1", "term_start": "2021-01-01", "won": True,
         "credit_bureau_passed": True, "credit_bureau_true_creditworthy": True},
        {"billing_account": "C2", "term_start": "2021-06-01", "won": True,
         "credit_bureau_passed": True, "credit_bureau_true_creditworthy": True},
    ]
    assert _pick_acquisition_case_study_cid(funnel_log) == "C2"


def test_pick_acquisition_case_study_cid_none_when_no_wins():
    funnel_log = [{"billing_account": "C1", "term_start": "2021-01-01", "won": False}]
    assert _pick_acquisition_case_study_cid(funnel_log) is None


def test_acquisition_funnel_case_study_shows_both_sides_of_wall():
    funnel_log = [
        {"billing_account": "C1", "term_start": "2021-01-01", "won": True,
         "stage_reached": "cooling_off", "total_cost_gbp": 145.0,
         "credit_bureau_score_band": "sub_prime", "credit_bureau_passed": True,
         "credit_bureau_true_creditworthy": False},
    ]
    html = _acquisition_funnel_case_study(funnel_log, "C1")
    assert "Acquisition Funnel Case Study: C1" in html
    assert "sub_prime" in html
    assert "disagreed with" in html.lower()


def test_acquisition_funnel_case_study_empty_when_no_cid():
    assert _acquisition_funnel_case_study([], None) == ""


def test_acquisition_funnel_process_uses_latest_year():
    funnel_log = [
        {"term_start": "2021-01-01", "won": True, "stage_reached": "cooling_off", "total_cost_gbp": 145.0},
        {"term_start": "2022-01-01", "won": False, "stage_reached": "application", "total_cost_gbp": 0.0},
        {"term_start": "2022-06-01", "won": True, "stage_reached": "cooling_off", "total_cost_gbp": 145.0},
    ]
    html = _acquisition_funnel_process(funnel_log)
    assert "Acquisition Funnel Process (2022)" in html
    assert "APPLICATION" in html
    assert "2021" not in html.split("<h2>")[1].split("</h2>")[0]


def test_acquisition_funnel_process_empty_when_no_log():
    assert _acquisition_funnel_process([]) == ""
