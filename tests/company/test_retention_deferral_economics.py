from company.analytics.retention_deferral_economics import (
    compute_realized_deferrals, serial_saver_summary,
)


def _offer(cid, event_date, outcome, assumed=12, cost=10.0, margin=50.0):
    return {
        "customer_id": cid,
        "event_date": event_date,
        "outcome": outcome,
        "assumed_deferral_months": assumed,
        "retention_cost_gbp": cost,
        "expected_term_margin_gbp": margin,
    }


def _churn(cid, event_date):
    return {"customer_id": cid, "event_date": event_date, "event_type": "churn"}


def test_compute_realized_deferrals_underperformed_when_churn_before_assumed_window():
    retention_log = [_offer("C1", "2020-01-01", "retained", assumed=12)]
    company_event_log = [_churn("C1", "2020-04-01")]

    records = compute_realized_deferrals(retention_log, company_event_log)

    assert len(records) == 1
    r = records[0]
    assert r["customer_id"] == "C1"
    assert r["next_event_type"] == "churn"
    assert r["realized_deferral_months"] == 3.0
    assert r["underperformed"] is True


def test_compute_realized_deferrals_next_offer_before_churn():
    retention_log = [
        _offer("C5", "2019-01-01", "retained"),
        _offer("C5", "2020-01-01", "churned_despite_offer"),
    ]
    company_event_log = [_churn("C5", "2020-06-01")]

    records = compute_realized_deferrals(retention_log, company_event_log)

    first = next(r for r in records if r["offer_date"] == "2019-01-01")
    assert first["next_event_type"] == "next_offer"
    assert first["realized_deferral_months"] == 12.0

    second = next(r for r in records if r["offer_date"] == "2020-01-01")
    assert second["next_event_type"] == "churn"


def test_compute_realized_deferrals_no_terminal_event_yet():
    retention_log = [_offer("C9", "2024-01-01", "retained")]
    company_event_log = []

    records = compute_realized_deferrals(retention_log, company_event_log)

    assert records[0]["realized_deferral_months"] is None
    assert records[0]["next_event_type"] is None
    assert records[0]["underperformed"] is False


def test_compute_realized_deferrals_skips_pending_offers():
    retention_log = [_offer("C2", "2021-01-01", "pending")]
    company_event_log = []

    assert compute_realized_deferrals(retention_log, company_event_log) == []


def test_serial_saver_summary_flags_ev_negative_repeat_saver():
    retention_log = [
        _offer("C6", "2018-01-01", "retained", cost=8.0),
        _offer("C6", "2019-01-01", "retained", cost=8.0),
        _offer("C6", "2020-01-01", "churned_despite_offer", cost=8.0),
    ]

    summaries = serial_saver_summary(retention_log)

    assert len(summaries) == 1
    s = summaries[0]
    assert s["customer_id"] == "C6"
    assert s["offer_count"] == 3
    assert s["cumulative_cost_gbp"] == 24.0
    assert s["is_serial_saver"] is True
    assert s["ev_negative"] is True


def test_serial_saver_summary_single_offer_not_flagged():
    retention_log = [_offer("C1", "2018-01-01", "retained")]

    summaries = serial_saver_summary(retention_log)

    assert summaries[0]["is_serial_saver"] is False
    assert summaries[0]["ev_negative"] is False


def test_serial_saver_summary_repeat_but_eventually_retained_not_ev_negative():
    retention_log = [
        _offer("C3", "2018-01-01", "retained"),
        _offer("C3", "2019-01-01", "retained"),
    ]

    summaries = serial_saver_summary(retention_log)

    assert summaries[0]["is_serial_saver"] is True
    assert summaries[0]["ev_negative"] is False
