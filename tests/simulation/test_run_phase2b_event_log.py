"""Integration tests for run_phase2b company_event_log - Phase 12a.

Uses a truncated window (2017-12-31) so tests run in reasonable time.
Calls main() once via a session fixture to avoid 5 separate sim runs.
"""

import pytest

from company.interfaces.sim_interface import StubSimInterface
from simulation.run_phase2b import main as run_phase2b


@pytest.fixture(scope="module")
def sim_result_2017():
    stub = StubSimInterface()
    result = run_phase2b(report_end="2017-12-31", sim_interface=stub)
    return result, stub


def test_company_event_log_key_present(sim_result_2017):
    result, _ = sim_result_2017
    assert "company_event_log" in result
    assert isinstance(result["company_event_log"], list)


def test_company_event_log_entries_have_required_fields(sim_result_2017):
    result, _ = sim_result_2017
    for entry in result["company_event_log"]:
        assert "event_type" in entry
        assert "customer_id" in entry
        assert "event_date" in entry
        assert entry["event_type"] in ("churn", "acquisition")


def test_sim_interface_churn_notifications_match_churned_accounts(sim_result_2017):
    result, stub = sim_result_2017
    churned = result.get("churned_billing_accounts", [])
    if churned:
        assert len(stub.churn_notifications) > 0
        notified_ids = {n["account_id"] for n in stub.churn_notifications}
        for cba in churned:
            assert cba in notified_ids


def test_stub_churn_notifications_have_extended_fields(sim_result_2017):
    _, stub = sim_result_2017
    for notif in stub.churn_notifications:
        assert "reason" in notif
        assert "sim_churn_probability" in notif
        assert "company_churn_estimate" in notif


def test_sim_interface_none_still_works():
    """run_phase2b works fine when sim_interface is None (default)."""
    result = run_phase2b(report_end="2017-12-31", sim_interface=None)
    assert "company_event_log" in result


def test_retention_log_key_present(sim_result_2017):
    result, _ = sim_result_2017
    assert "retention_log" in result
    assert isinstance(result["retention_log"], list)


def test_retention_cost_events_key_present(sim_result_2017):
    result, _ = sim_result_2017
    assert "retention_cost_events" in result
    assert isinstance(result["retention_cost_events"], list)


def test_retention_log_entries_have_required_fields(sim_result_2017):
    result, _ = sim_result_2017
    for entry in result["retention_log"]:
        assert "customer_id" in entry
        assert "event_date" in entry
        assert "company_churn_estimate" in entry
        assert "discount_pct" in entry
        assert "outcome" in entry
        assert entry["outcome"] in ("retained", "churned_despite_offer")


def test_retention_cost_events_are_negative_amounts(sim_result_2017):
    result, _ = sim_result_2017
    for ev in result["retention_cost_events"]:
        assert ev["amount_gbp"] < 0


def test_retention_log_entries_above_threshold(sim_result_2017):
    from simulation.run_phase2b import RETENTION_THRESHOLD
    result, _ = sim_result_2017
    for entry in result["retention_log"]:
        assert entry["company_churn_estimate"] > RETENTION_THRESHOLD


def test_stub_retention_notifications_count_matches_log(sim_result_2017):
    result, stub = sim_result_2017
    assert len(stub.retention_notifications) == len(result["retention_log"])


def test_retention_log_entries_have_expected_margin(sim_result_2017):
    result, _ = sim_result_2017
    for entry in result["retention_log"]:
        assert "expected_term_margin_gbp" in entry
        assert isinstance(entry["expected_term_margin_gbp"], float)


def test_no_offer_churn_log_key_present(sim_result_2017):
    result, _ = sim_result_2017
    assert "no_offer_churn_log" in result
    assert isinstance(result["no_offer_churn_log"], list)


def test_no_offer_churn_log_entries_have_required_fields(sim_result_2017):
    result, _ = sim_result_2017
    for entry in result["no_offer_churn_log"]:
        assert "customer_id" in entry
        assert "event_date" in entry
        assert "expected_term_margin_gbp" in entry


def test_no_offer_churn_log_customers_are_churned(sim_result_2017):
    result, _ = sim_result_2017
    churned = set(result.get("churned_billing_accounts", []))
    for entry in result["no_offer_churn_log"]:
        cid = entry["customer_id"]
        assert cid in churned, cid + " in no_offer_churn_log but not in churned_billing_accounts"
