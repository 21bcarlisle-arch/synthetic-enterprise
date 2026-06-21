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


# ── Phase 12d: margin-aware retention guard ───────────────────────────────────

def test_no_offer_churn_log_entries_have_reason(sim_result_2017):
    result, _ = sim_result_2017
    for entry in result["no_offer_churn_log"]:
        assert "no_offer_reason" in entry, f"no_offer_reason missing from {entry}"
        assert entry["no_offer_reason"] in ("below_threshold", "uneconomical")


def test_retention_log_offers_are_economically_rational(sim_result_2017):
    """Every offer in the retention_log must have expected_margin > retention_cost."""
    result, _ = sim_result_2017
    for entry in result["retention_log"]:
        exp_m = entry.get("expected_term_margin_gbp", 0.0)
        cost = entry.get("retention_cost_gbp", 0.0)
        assert exp_m > cost, (
            f"{entry['customer_id']} {entry['event_date']}: "
            f"offer made with margin £{exp_m:.2f} < cost £{cost:.2f}"
        )


def test_uneconomical_no_offer_entries_had_high_churn_estimate(sim_result_2017):
    """Entries blocked as uneconomical must have had churn estimate above the threshold."""
    from simulation.run_phase2b import RETENTION_THRESHOLD
    result, _ = sim_result_2017
    for entry in result["no_offer_churn_log"]:
        if entry.get("no_offer_reason") == "uneconomical":
            est = entry.get("company_churn_estimate")
            assert est is not None and est > RETENTION_THRESHOLD, (
                f"{entry['customer_id']}: reason=uneconomical but estimate={est}"
            )


# ── Phase 14a: tiered retention offer size ────────────────────────────────────

def test_retention_discount_function_tiers():
    """_retention_discount_for_risk returns correct tier for each risk band."""
    from simulation.run_phase2b import _retention_discount_for_risk
    assert _retention_discount_for_risk(0.80) == 0.08   # high risk
    assert _retention_discount_for_risk(0.75) == 0.08   # exactly at high-risk threshold
    assert _retention_discount_for_risk(0.60) == 0.05   # medium risk
    assert _retention_discount_for_risk(0.50) == 0.05   # exactly at medium threshold
    assert _retention_discount_for_risk(0.40) == 0.03   # low-risk-above-threshold
    assert _retention_discount_for_risk(0.30) == 0.03   # exactly at retention threshold
    assert _retention_discount_for_risk(0.20) == 0.00   # below threshold — no offer


def test_retention_tiers_cover_threshold():
    """RETENTION_TIERS lower bound matches RETENTION_THRESHOLD."""
    from simulation.run_phase2b import RETENTION_TIERS, RETENTION_THRESHOLD
    min_tier_threshold = min(t for t, _ in RETENTION_TIERS)
    assert min_tier_threshold == RETENTION_THRESHOLD


def test_retention_log_discount_pct_is_in_valid_tier(sim_result_2017):
    """discount_pct in each retention log entry must correspond to a valid tier value."""
    from simulation.run_phase2b import RETENTION_TIERS
    valid_discounts = {d for _, d in RETENTION_TIERS}
    result, _ = sim_result_2017
    for entry in result["retention_log"]:
        assert entry["discount_pct"] in valid_discounts, (
            f"{entry['customer_id']}: unexpected discount_pct {entry['discount_pct']}"
        )


def test_tiered_discount_high_risk_bigger_than_low_risk():
    """High churn risk gets a larger discount than low-risk-above-threshold."""
    from simulation.run_phase2b import _retention_discount_for_risk
    high_risk = _retention_discount_for_risk(0.80)
    low_risk = _retention_discount_for_risk(0.32)
    assert high_risk > low_risk
