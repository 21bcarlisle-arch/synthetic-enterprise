from company.analytics.decision_event_ledger import (
    build_customer_ledger, build_portfolio_event_stream,
)


def _journey(cid, dt, state, resentment=10.0, burned=False):
    return dict(customer_id=cid, date=dt, state=state, resentment_score=resentment, is_burned=burned)

def _retention(cid, dt, company_est=0.5, discount_pct=0.05, cost_gbp=20.0,
                expected_term_margin_gbp=100.0, outcome="retained", realized_churn_p=0.1):
    return dict(
        customer_id=cid, date=dt, company_est=company_est, discount_pct=discount_pct,
        cost_gbp=cost_gbp, expected_term_margin_gbp=expected_term_margin_gbp,
        outcome=outcome, realized_churn_p=realized_churn_p,
    )

def _event(cid, dt, etype="renewed", company_est=0.2, realized_churn_p=0.1):
    return dict(customer_id=cid, date=dt, type=etype, company_est=company_est, realized_churn_p=realized_churn_p)

def _ledger_customer(cases):
    return dict(arrears_history=cases)

def _case(case_id, amount, stages):
    return dict(case_id=case_id, arrears_gbp=amount, stages=stages)

def _stage(stage, dt, note=""):
    return dict(stage=stage, date=dt, note=note)


def test_build_customer_ledger_merges_and_sorts_chronologically():
    journey = [_journey("C1", "2021-05-01", "irritated", resentment=12.0)]
    retention = [_retention("C1", "2021-06-01")]
    events = [_event("C1", "2021-06-01", "renewed")]
    ledger_cust = _ledger_customer([_case("X", 50.0, [_stage("DD_FAILED", "2021-04-01", "dd returned")])])

    result = build_customer_ledger("C1", events, retention, journey, ledger_cust)

    dates = [r["date"] for r in result]
    assert dates == sorted(dates)
    assert dates == ["2021-04-01", "2021-05-01", "2021-06-01", "2021-06-01"]
    types = [r["event_type"] for r in result]
    assert "arrears_dd_failed" in types
    assert "journey_state" in types
    assert "retention_decision" in types
    assert "outcome_renewed" in types


def test_build_customer_ledger_only_includes_matching_customer():
    events = [_event("C1", "2021-01-01"), _event("C2", "2021-02-01")]
    result = build_customer_ledger("C1", events, [], [], None)
    assert len(result) == 1
    assert result[0]["customer_id"] == "C1"


def test_build_customer_ledger_empty_when_no_data():
    assert build_customer_ledger("C1", [], [], [], None) == []


def test_retention_decision_event_carries_ev_and_belief_vs_truth():
    retention = [_retention("C1", "2021-06-01", company_est=0.95, cost_gbp=100.0,
                             expected_term_margin_gbp=1000.0, realized_churn_p=0.04)]
    result = build_customer_ledger("C1", [], retention, [], None)
    assert len(result) == 1
    r = result[0]
    assert r["company_belief"] == 0.95
    assert r["sim_truth"] == 0.04
    assert r["amount_gbp"] == 900.0  # EV = expected_margin - cost
    assert "95%" in r["description"]


def test_arrears_events_expand_every_stage():
    ledger_cust = _ledger_customer([_case("X", 100.0, [
        _stage("DD_FAILED", "2021-01-01"), _stage("FIRST_NOTICE", "2021-01-08"),
        _stage("RESOLVED", "2021-01-20"),
    ])])
    result = build_customer_ledger("C1", [], [], [], ledger_cust)
    assert len(result) == 3
    assert [r["event_type"] for r in result] == [
        "arrears_dd_failed", "arrears_first_notice", "arrears_resolved",
    ]


def test_build_portfolio_event_stream_sorted_most_recent_first():
    retention = [_retention("C1", "2020-01-01"), _retention("C2", "2022-01-01")]
    result = build_portfolio_event_stream([], retention, [], None)
    dates = [r["date"] for r in result]
    assert dates == sorted(dates, reverse=True)
    assert len(result) == 2


def test_build_portfolio_event_stream_arrears_one_entry_per_case_not_per_stage():
    billing_ledger = dict(customers=dict(C1=_ledger_customer([_case("X", 50.0, [
        _stage("DD_FAILED", "2021-01-01"), _stage("FIRST_NOTICE", "2021-01-08"),
        _stage("RESOLVED", "2021-01-20"),
    ])])))
    result = build_portfolio_event_stream([], [], [], billing_ledger)
    assert len(result) == 1
    assert result[0]["event_type"] == "arrears_opened"
    assert result[0]["outcome"] == "RESOLVED"  # final stage


def test_build_portfolio_event_stream_respects_limit():
    retention = [_retention("C{}".format(i), "202{}-01-01".format(i % 6)) for i in range(10)]
    result = build_portfolio_event_stream([], retention, [], None, limit=3)
    assert len(result) == 3


def test_build_portfolio_event_stream_empty_when_no_data():
    assert build_portfolio_event_stream([], [], [], None) == []
