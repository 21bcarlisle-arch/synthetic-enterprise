"""Tests for the churn-journey evidence retrofit (Phase QL Part 2),
docs/design/PROCESS_MODEL.md: the hidden SIM-side churn journey state
machine (simulation/churn_journey.py) must surface on all three business
tabs -- Sim (signal over time + correlation with realized churn), Customers
(one named customer's trajectory next to the company-observable retention
risk feature vector), Supplier (portfolio funnel, the new operational
monitoring capability)."""
from tools.generate_dashboard_data import extract_customers
from tools.generate_shadow_html import (
    _churn_journey_signal, _pick_journey_case_study_cid,
    _churn_journey_case_study, _churn_journey_portfolio_funnel,
)


def test_extract_customers_carries_journey_log():
    data = {
        "customer_events": [],
        "retention_log": [],
        "per_customer_lifetime": {},
        "churn_journey_log": [
            {"customer_id": "C1", "term_start": "2021-01-01", "journey_state": "irritated",
             "resentment_score": 12.5, "is_burned": False, "perceived_bill_saving_gbp": 3.2},
        ],
    }
    out = extract_customers(data)
    assert out["journey_log"] == [
        {"customer_id": "C1", "date": "2021-01-01", "state": "irritated",
         "resentment_score": 12.5, "is_burned": False, "perceived_bill_saving_gbp": 3.2},
    ]


def test_extract_customers_journey_log_empty_when_absent():
    data = {"customer_events": [], "retention_log": [], "per_customer_lifetime": {}}
    out = extract_customers(data)
    assert out["journey_log"] == []


def test_churn_journey_signal_empty_when_no_log():
    assert _churn_journey_signal([], []) == ""


def test_churn_journey_signal_reports_year_and_churn_rate():
    journey_log = [
        {"customer_id": "C1", "date": "2022-01-01", "state": "comparing", "resentment_score": 40.0, "is_burned": True},
        {"customer_id": "C2", "date": "2022-06-01", "state": "content", "resentment_score": 5.0, "is_burned": False},
    ]
    events = [
        {"date": "2022-01-01", "type": "churned"},
        {"date": "2022-06-01", "type": "renewed"},
    ]
    html = _churn_journey_signal(journey_log, events)
    assert "2022" in html
    assert "50.0%" in html  # 1 of 2 entries beyond CONTENT
    assert "Realized Churn Rate" in html


def test_pick_journey_case_study_cid_most_active_wins():
    journey_log = [
        {"customer_id": "C1", "state": "irritated"},
        {"customer_id": "C1", "state": "comparing"},
        {"customer_id": "C2", "state": "irritated"},
    ]
    assert _pick_journey_case_study_cid(journey_log) == "C1"


def test_pick_journey_case_study_cid_none_when_all_content():
    journey_log = [{"customer_id": "C1", "state": "content"}]
    assert _pick_journey_case_study_cid(journey_log) is None


def test_churn_journey_case_study_shows_both_sides_of_wall():
    journey_log = [
        {"customer_id": "C1", "date": "2021-01-01", "state": "irritated",
         "resentment_score": 15.0, "is_burned": False},
        {"customer_id": "C1", "date": "2022-01-01", "state": "comparing",
         "resentment_score": 55.0, "is_burned": True},
    ]
    ledger = {"customers": {"C1": {"invoices": [
        {"customer_id": "C1", "payment_status": "unpaid", "due_date": "2020-01-01"},
    ]}}}
    html = _churn_journey_case_study(journey_log, ledger, "C1")
    assert "Churn Journey Case Study: C1" in html
    assert "COMPARING" in html
    assert "overdue invoice" in html.lower()


def test_churn_journey_case_study_empty_when_no_cid():
    assert _churn_journey_case_study([], {}, None) == ""


def test_churn_journey_portfolio_funnel_uses_latest_year():
    journey_log = [
        {"customer_id": "C1", "date": "2021-01-01", "state": "content"},
        {"customer_id": "C1", "date": "2022-01-01", "state": "irritated"},
        {"customer_id": "C2", "date": "2022-06-01", "state": "comparing"},
    ]
    html = _churn_journey_portfolio_funnel(journey_log)
    assert "Churn Journey Funnel (2022)" in html
    assert "IRRITATED" in html
    assert "COMPARING" in html
    assert "2021" not in html.split("<h2>")[1].split("</h2>")[0]


def test_churn_journey_portfolio_funnel_empty_when_no_log():
    assert _churn_journey_portfolio_funnel([]) == ""
