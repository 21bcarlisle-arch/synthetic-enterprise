"""Tests for the Decision Event Ledger surfaces (Phase QP,
docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md Part 5) -- unifying the
per-topic case studies (behavioral/renewal/churn-journey/retention-deferral)
into one chronological timeline per customer, plus a portfolio-wide feed.
"""
from tools.generate_shadow_html import (
    _event_type_label, _decision_event_ledger_case_study, _portfolio_event_stream,
)


def test_event_type_label_formats_readably():
    assert _event_type_label("retention_decision") == "RETENTION DECISION"
    assert _event_type_label("arrears_dd_failed") == "ARREARS DD FAILED"


def test_decision_event_ledger_case_study_empty_when_no_data():
    assert _decision_event_ledger_case_study([], [], [], {}, "C1") == ""


def test_decision_event_ledger_case_study_shows_both_sides_of_wall():
    events = []
    retention = [dict(
        customer_id="C1", date="2018-01-31", company_est=0.95, discount_pct=0.08,
        cost_gbp=24227.89, expected_term_margin_gbp=163704.65, outcome="retained",
        realized_churn_p=0.04,
    )]
    journey_log = []
    ledger = dict(customers=dict(C1=dict(arrears_history=[])))
    html = _decision_event_ledger_case_study(events, retention, journey_log, ledger, "C1")
    assert "Decision Event Ledger: C1" in html
    assert "95.0%" in html
    assert "4.0%" in html
    assert "RETENTION DECISION" in html


def test_decision_event_ledger_case_study_journey_state_truth_not_percent_formatted():
    journey_log = [dict(
        customer_id="C1", date="2021-05-01", state="irritated",
        resentment_score=12.5, is_burned=False,
    )]
    html = _decision_event_ledger_case_study([], [], journey_log, {}, "C1")
    assert "JOURNEY STATE" in html
    assert "1250.0%" not in html  # resentment score must not be mis-rendered as a percent


def test_portfolio_event_stream_empty_when_no_data():
    assert _portfolio_event_stream([], [], [], {}) == ""


def test_portfolio_event_stream_renders_filter_buttons_and_rows():
    events = []
    retention = [dict(customer_id="C1", date="2020-01-01", company_est=0.3,
                       discount_pct=0.05, cost_gbp=20.0, expected_term_margin_gbp=100.0,
                       outcome="retained", realized_churn_p=0.1)]
    html = _portfolio_event_stream(events, retention, [], {})
    assert "Portfolio Decision Event Stream" in html
    assert "_filterLedger('all')" in html
    assert "_filterLedger('retention_decision')" in html
    assert 'data-event-type="retention_decision"' in html
    assert "C1" in html
