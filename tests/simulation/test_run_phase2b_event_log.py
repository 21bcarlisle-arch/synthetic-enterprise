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
