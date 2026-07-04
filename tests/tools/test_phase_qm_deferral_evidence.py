"""Tests for the retention-as-deferral evidence retrofit (Phase QM,
docs/staging/QL_WIRE_AND_DEFERRAL.md): retention offers price a deferral
window (H1), not lifetime CLV, and this must surface on all three business
tabs -- Sim (assumed vs realized deferral by year), Customers (one serial
saver's offer-decay-rechurn timeline), Supplier (portfolio serial-saver
EV-negative flags)."""
from tools.generate_shadow_html import (
    _retention_deferral_signal, _pick_serial_saver_cid,
    _retention_deferral_case_study, _serial_saver_portfolio,
)


def _record(cid, offer_date, assumed=12, realized=None, next_event=None, underperformed=False):
    return {
        "customer_id": cid,
        "offer_date": offer_date,
        "assumed_deferral_months": assumed,
        "realized_deferral_months": realized,
        "next_event_type": next_event,
        "underperformed": underperformed,
        "cost_gbp": 5.0,
        "expected_term_margin_gbp": 10.0,
    }


def _saver(cid, offer_count, cumulative_cost=10.0, final_outcome="retained", is_serial=True, ev_negative=False):
    return {
        "customer_id": cid,
        "offer_count": offer_count,
        "cumulative_cost_gbp": cumulative_cost,
        "final_outcome": final_outcome,
        "is_serial_saver": is_serial,
        "ev_negative": ev_negative,
    }


def test_retention_deferral_signal_empty_when_no_records():
    assert _retention_deferral_signal([]) == ""


def test_retention_deferral_signal_shows_year_and_underperform_pct():
    records = [
        _record("C1", "2020-03-01", assumed=12, realized=3.0, next_event="churn", underperformed=True),
        _record("C5", "2020-06-01", assumed=12, realized=15.0, next_event="churn", underperformed=False),
    ]
    html = _retention_deferral_signal(records)
    assert "2020" in html
    assert "H1" in html and "H2" in html


def test_pick_serial_saver_cid_prefers_most_offers():
    savers = [_saver("C1", 2), _saver("C6", 3), _saver("C5", 1, is_serial=False)]
    assert _pick_serial_saver_cid(savers) == "C6"


def test_pick_serial_saver_cid_none_when_no_serial_savers():
    savers = [_saver("C1", 1, is_serial=False)]
    assert _pick_serial_saver_cid(savers) is None


def test_retention_deferral_case_study_empty_when_no_cid():
    assert _retention_deferral_case_study([], [], None) == ""


def test_retention_deferral_case_study_shows_timeline_and_verdict():
    records = [
        _record("C6", "2018-01-01", assumed=12, realized=12.0, next_event="next_offer", underperformed=False),
        _record("C6", "2019-01-01", assumed=12, realized=6.0, next_event="churn", underperformed=True),
    ]
    savers = [_saver("C6", 2, cumulative_cost=16.0, final_outcome="churned_despite_offer", ev_negative=True)]
    html = _retention_deferral_case_study(records, savers, "C6")
    assert "C6" in html
    assert "EV-negative" in html
    assert "2018-01-01" in html and "2019-01-01" in html


def test_serial_saver_portfolio_empty_when_no_repeats():
    assert _serial_saver_portfolio([_saver("C1", 1, is_serial=False)]) == ""


def test_serial_saver_portfolio_lists_ev_negative_customers():
    savers = [
        _saver("C6", 3, cumulative_cost=24.0, final_outcome="churned_despite_offer", ev_negative=True),
        _saver("C9", 2, cumulative_cost=12.0, final_outcome="retained", ev_negative=False),
    ]
    html = _serial_saver_portfolio(savers)
    assert "C6" in html and "C9" in html
    assert "EV-NEGATIVE" in html
