"""Phase AH tests: Portfolio Intelligence Pack section in annual report."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from saas.reporting.annual_report import _section_portfolio_intelligence_pack


def _make_data(
    retention_log=None,
    no_offer_churn_log=None,
    company_event_log=None,
    flexibility_revenue_summary=None,
):
    return {
        "retention_log": retention_log or [],
        "no_offer_churn_log": no_offer_churn_log or [],
        "company_event_log": company_event_log or [],
        "flexibility_revenue_summary": flexibility_revenue_summary or {},
    }


def _churn_ev(cid, date):
    return {"event_type": "churn", "customer_id": cid, "event_date": date, "reason": "non-renewal"}


def _acq_ev(cid, date):
    return {"event_type": "acquisition", "customer_id": cid, "event_date": date}


def _ret_offer(cid, date, outcome, discount=0.05, cost=100.0, margin=500.0):
    return {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": 0.4,
        "discount_pct": discount,
        "retention_cost_gbp": cost,
        "expected_term_margin_gbp": margin,
        "acq_cost_saved_gbp": 150.0,
        "outcome": outcome,
    }


def _no_offer(cid, date, reason=None, margin=300.0):
    return {
        "customer_id": cid,
        "event_date": date,
        "company_churn_estimate": 0.2,
        "expected_term_margin_gbp": margin,
        "no_offer_reason": reason,
    }


# 1. Silent when no retention log and no churn events
def test_returns_empty_when_no_data():
    result = _section_portfolio_intelligence_pack(_make_data())
    assert result == ""


# 2. Returns content when there are churn events (even without retention log)
def test_returns_content_with_only_churn_events():
    data = _make_data(company_event_log=[_churn_ev("C1", "2021-04-01")])
    result = _section_portfolio_intelligence_pack(data)
    assert "Portfolio Intelligence Pack" in result


# 3. Retention coverage rate: offers / (offers + no-offer churns)
def test_retention_coverage_rate():
    data = _make_data(
        retention_log=[_ret_offer("C1", "2021-04-01", "retained")],
        no_offer_churn_log=[_no_offer("C2", "2021-04-01")],
        company_event_log=[_churn_ev("C2", "2021-04-01")],
    )
    result = _section_portfolio_intelligence_pack(data)
    # 1 offer / (1 offer + 1 no-offer) = 50%
    assert "50%" in result


# 4. Offer acceptance rate computed correctly
def test_offer_acceptance_rate():
    data = _make_data(
        retention_log=[
            _ret_offer("C1", "2021-04-01", "retained"),
            _ret_offer("C2", "2021-04-01", "retained"),
            _ret_offer("C3", "2021-04-01", "churned_despite_offer"),
        ],
        company_event_log=[_churn_ev("C3", "2021-04-01")],
    )
    result = _section_portfolio_intelligence_pack(data)
    # 2/3 = 67% acceptance
    assert "67%" in result


# 5. No-offer churns counted with blind miss vs deliberate split
def test_no_offer_churn_breakdown():
    data = _make_data(
        no_offer_churn_log=[
            _no_offer("C1", "2021-04-01", reason=None),        # blind miss
            _no_offer("C2", "2021-04-01", reason="uneconomical"),  # deliberate
        ],
        company_event_log=[
            _churn_ev("C1", "2021-04-01"),
            _churn_ev("C2", "2021-04-01"),
        ],
    )
    result = _section_portfolio_intelligence_pack(data)
    assert "1 blind miss" in result
    assert "1 deliberate pass" in result


# 6. Flexibility enrollment growth rate non-zero when multi-year data
def test_flexibility_enrollment_cagr():
    flex = {
        "total_flexibility_revenue_gbp": 2000.0,
        "total_cm_revenue_gbp": 1500.0,
        "total_dfs_revenue_gbp": 500.0,
        "enrolled_customer_years": 4,
        "peak_year_revenue_gbp": 1000.0,
        "years_with_revenue": [2016, 2018],
        "per_year": {
            2016: {"total_gbp": 500.0, "cm_gbp": 500.0, "dfs_gbp": 0.0, "enrolled_customers": 1},
            2018: {"total_gbp": 1500.0, "cm_gbp": 1000.0, "dfs_gbp": 500.0, "enrolled_customers": 3},
        },
    }
    data = _make_data(
        company_event_log=[_churn_ev("C1", "2018-04-01")],
        flexibility_revenue_summary=flex,
    )
    result = _section_portfolio_intelligence_pack(data)
    assert "CAGR" in result
    assert "Flexibility Revenue Intelligence" in result


# 7. Revenue per enrolled customer computed from per_year data
def test_revenue_per_enrolled_customer():
    flex = {
        "total_flexibility_revenue_gbp": 3000.0,
        "total_cm_revenue_gbp": 3000.0,
        "total_dfs_revenue_gbp": 0.0,
        "enrolled_customer_years": 3,
        "peak_year_revenue_gbp": 1000.0,
        "years_with_revenue": [2016, 2017, 2018],
        "per_year": {
            2016: {"total_gbp": 1000.0, "cm_gbp": 1000.0, "dfs_gbp": 0.0, "enrolled_customers": 1},
            2017: {"total_gbp": 1000.0, "cm_gbp": 1000.0, "dfs_gbp": 0.0, "enrolled_customers": 1},
            2018: {"total_gbp": 1000.0, "cm_gbp": 1000.0, "dfs_gbp": 0.0, "enrolled_customers": 1},
        },
    }
    data = _make_data(
        company_event_log=[_churn_ev("C1", "2018-04-01")],
        flexibility_revenue_summary=flex,
    )
    result = _section_portfolio_intelligence_pack(data)
    # £3000 / 3 enrolled years = £1,000.00 per enrolled customer-year
    assert "£1,000.00" in result


# 8. Board recommendations section is always present when data exists
def test_board_recommendations_present():
    data = _make_data(company_event_log=[_churn_ev("C1", "2022-04-01")])
    result = _section_portfolio_intelligence_pack(data)
    assert "Board Recommendations" in result


# 9. Churn pattern analysis includes peak year
def test_churn_peak_year_identified():
    data = _make_data(
        company_event_log=[
            _churn_ev("C1", "2022-04-01"),
            _churn_ev("C2", "2022-10-01"),
            _churn_ev("C3", "2021-04-01"),
        ],
    )
    result = _section_portfolio_intelligence_pack(data)
    assert "2022" in result
    assert "**Peak churn year:** 2022 (2 events)" in result


# 10. Net book movement computed correctly
def test_net_book_movement():
    data = _make_data(
        company_event_log=[
            _acq_ev("C1", "2016-01-01"),
            _acq_ev("C2", "2017-01-01"),
            _acq_ev("C3", "2018-01-01"),
            _churn_ev("C4", "2022-04-01"),
        ],
    )
    result = _section_portfolio_intelligence_pack(data)
    # 3 acquisitions - 1 churn = +2
    assert "+2" in result
    assert "growing" in result


# 11. Crisis-year churn triggers board recommendation
def test_crisis_churn_recommendation():
    data = _make_data(
        company_event_log=[
            _churn_ev("C1", "2021-06-01"),
            _churn_ev("C2", "2022-06-01"),
        ],
    )
    result = _section_portfolio_intelligence_pack(data)
    assert "Crisis-year churn" in result
    assert "2021" in result or "2022" in result


# 12. Avoidable margin loss computed for blind-miss no-offer churns
def test_avoidable_margin_loss():
    data = _make_data(
        no_offer_churn_log=[
            _no_offer("C1", "2022-04-01", reason=None, margin=800.0),
            _no_offer("C2", "2022-04-01", reason=None, margin=600.0),
            _no_offer("C3", "2022-04-01", reason="uneconomical", margin=200.0),
        ],
        company_event_log=[
            _churn_ev("C1", "2022-04-01"),
            _churn_ev("C2", "2022-04-01"),
            _churn_ev("C3", "2022-04-01"),
        ],
    )
    result = _section_portfolio_intelligence_pack(data)
    # Blind miss margin = 800 + 600 = 1400
    assert "£1,400.00" in result
