"""Integration tests for run_phase2b company_event_log - Phase 12a.

Uses a truncated window (2017-12-31) so tests run in reasonable time.
Calls main() once via a session fixture to avoid 5 separate sim runs.
"""

import pytest

from simulation.run_phase2b import main as run_phase2b


@pytest.fixture(scope="module")
def sim_result_2017():
    # No stub interface: run_phase2b's `sim_interface` parameter was deleted 2026-08-29.
    # It was never passed on any production path, so the four tests that injected a stub
    # were the only thing keeping five `notify_*` call sites alive -- a seam only tests
    # satisfied. This fixture now runs the same shape every published figure runs.
    return run_phase2b(report_end="2017-12-31")


def test_company_event_log_key_present(sim_result_2017):
    result = sim_result_2017
    assert "company_event_log" in result
    assert isinstance(result["company_event_log"], list)


def test_company_event_log_entries_have_required_fields(sim_result_2017):
    result = sim_result_2017
    for entry in result["company_event_log"]:
        assert "event_type" in entry
        assert "customer_id" in entry
        assert "event_date" in entry
        assert entry["event_type"] in ("churn", "acquisition")


def test_every_churned_account_appears_in_the_event_log(sim_result_2017):
    """Set equality BOTH WAYS between the run's two projections of one departure.

    This replaces `test_sim_interface_churn_notifications_match_churned_accounts`,
    which asserted the same property across a seam that no production run plumbed.
    Both sides here share a writer (`run_phase2b` books `churned_billing_accounts` and
    the `"churned"` event eight lines apart), so this is an INTERNAL CONSISTENCY check
    between two SIM projections and is NOT a company-vs-world reconciliation -- the
    annual report published one of those for two months and it could not fail
    (see `tests/saas/reporting/test_crm_section_cannot_mirror_itself.py`).

    Symmetric on purpose: the old one-sided `for cba in churned: assert cba in notified`
    could not see an event log carrying a departure the run never booked.
    """
    result = sim_result_2017
    churned = set(result.get("churned_billing_accounts", []))
    logged = {
        e["customer_id"] for e in result["company_event_log"]
        if e["event_type"] == "churn"
    }
    # Fail-open guard: an empty window would make the equality vacuous.
    assert churned, "truncated window produced no churn -- this test would pass vacuously"
    assert churned == logged, (
        f"only in churned_billing_accounts: {sorted(churned - logged)}; "
        f"only in company_event_log: {sorted(logged - churned)}"
    )


def test_retention_log_key_present(sim_result_2017):
    result = sim_result_2017
    assert "retention_log" in result
    assert isinstance(result["retention_log"], list)


def test_retention_cost_events_key_present(sim_result_2017):
    result = sim_result_2017
    assert "retention_cost_events" in result
    assert isinstance(result["retention_cost_events"], list)


def test_retention_log_entries_have_required_fields(sim_result_2017):
    result = sim_result_2017
    for entry in result["retention_log"]:
        assert "customer_id" in entry
        assert "event_date" in entry
        assert "company_churn_estimate" in entry
        assert "discount_pct" in entry
        assert "outcome" in entry
        assert entry["outcome"] in ("retained", "churned_despite_offer")


def test_retention_cost_events_are_negative_amounts(sim_result_2017):
    result = sim_result_2017
    for ev in result["retention_cost_events"]:
        assert ev["amount_gbp"] < 0


def test_retention_log_entries_above_threshold(sim_result_2017):
    from simulation.run_phase2b import RETENTION_THRESHOLD
    result = sim_result_2017
    for entry in result["retention_log"]:
        assert entry["company_churn_estimate"] > RETENTION_THRESHOLD


def test_retention_log_entries_have_expected_margin(sim_result_2017):
    result = sim_result_2017
    for entry in result["retention_log"]:
        assert "expected_term_margin_gbp" in entry
        assert isinstance(entry["expected_term_margin_gbp"], float)


def test_no_offer_churn_log_key_present(sim_result_2017):
    result = sim_result_2017
    assert "no_offer_churn_log" in result
    assert isinstance(result["no_offer_churn_log"], list)


def test_no_offer_churn_log_entries_have_required_fields(sim_result_2017):
    result = sim_result_2017
    for entry in result["no_offer_churn_log"]:
        assert "customer_id" in entry
        assert "event_date" in entry
        assert "expected_term_margin_gbp" in entry


def test_no_offer_churn_log_customers_are_churned(sim_result_2017):
    result = sim_result_2017
    churned = set(result.get("churned_billing_accounts", []))
    for entry in result["no_offer_churn_log"]:
        cid = entry["customer_id"]
        assert cid in churned, cid + " in no_offer_churn_log but not in churned_billing_accounts"


# ── Phase 12d: margin-aware retention guard ───────────────────────────────────

def test_no_offer_churn_log_entries_have_reason(sim_result_2017):
    result = sim_result_2017
    for entry in result["no_offer_churn_log"]:
        assert "no_offer_reason" in entry, f"no_offer_reason missing from {entry}"
        assert entry["no_offer_reason"] in ("below_threshold", "uneconomical")


def test_retention_log_offers_are_economically_rational(sim_result_2017):
    """Every offer in the retention_log must have expected_margin > retention_cost."""
    result = sim_result_2017
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
    result = sim_result_2017
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
    result = sim_result_2017
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
