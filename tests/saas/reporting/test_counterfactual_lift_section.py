"""Tests for the Part 4 lift-per-pound-by-intervention-class board section
(docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md), wired into
saas.reporting.annual_report._section_threshold_optimisation.
"""
from saas.reporting.annual_report import _section_threshold_optimisation


def _event(cid, date, roll=0.05, eff_retain=0.05):
    return {
        "customer_id": cid,
        "event_date": date,
        "event_type": "churned",
        "company_churn_estimate": 0.5,
        "churn_probability": 0.9,
        "random_roll": roll,
        "effective_retention_probability": eff_retain,
    }


def _miss(cid, date, no_offer_reason, would_be_discount_pct=None, expected_margin=1000.0):
    m = {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": 0.5,
        "expected_term_margin_gbp": expected_margin,
        "no_offer_reason": no_offer_reason,
    }
    if would_be_discount_pct is not None:
        m["would_be_discount_pct"] = would_be_discount_pct
    return m


def test_section_includes_lift_by_class_table_when_misses_present():
    data = {
        "no_offer_churn_log": [
            _miss("C1", "2020-01-01", "below_threshold"),
            _miss("C2", "2020-01-01", "uneconomical", would_be_discount_pct=0.08),
        ],
        "customer_events": [
            _event("C1", "2020-01-01"),
            _event("C2", "2020-01-01"),
        ],
    }
    out = _section_threshold_optimisation(data)
    assert "Lift-per-pound by intervention class" in out
    assert "Detection gate" in out
    assert "High-risk tier" in out


def test_section_has_no_lift_table_when_no_misses():
    data = {"no_offer_churn_log": [], "customer_events": []}
    out = _section_threshold_optimisation(data)
    assert "Lift-per-pound by intervention class" not in out


def test_section_does_not_crash_on_missing_keys():
    out = _section_threshold_optimisation({})
    assert "Counterfactual Retention" in out
