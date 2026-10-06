"""Phase 116: Energy theft indicator tests.

The module's own thresholds are UNSOURCED and None (2026-10-06), so the classification legs pass
cut-offs in. 0.40/0.65 below are TEST FIXTURES that exercise the banding, not sourced values.
"""

import pytest

from company.billing.theft_indicator import (
    _CONCERN_THRESHOLD_LOW,
    _THEFT_THRESHOLD_LOW,
    classify_anomaly,
    screen_portfolio,
)

CUTS = {"investigate_below": 0.40, "watch_below": 0.65}


def test_classify_ok():
    assert classify_anomaly(3000, 3500, **CUTS)["status"] == "ok"


def test_classify_watch():
    assert classify_anomaly(2000, 3500, **CUTS)["status"] == "watch"  # 57%


def test_classify_investigate():
    assert classify_anomaly(1000, 3500, **CUTS)["status"] == "investigate"  # 28%


def test_classify_no_data_when_eac_zero():
    result = classify_anomaly(1000, 0, **CUTS)
    assert result["status"] == "no_data"
    assert result["ratio"] is None


def test_ratio_is_correct():
    assert abs(classify_anomaly(1000, 4000, **CUTS)["ratio"] - 0.25) < 0.01


def test_classify_boundary_exactly_at_investigate_cut_is_watch():
    assert classify_anomaly(1400, 3500, **CUTS)["status"] == "watch"  # 40%


def test_classify_at_watch_cut_is_ok():
    assert classify_anomaly(2275, 3500, **CUTS)["status"] == "ok"  # 65%


def test_inverted_cuts_are_refused():
    with pytest.raises(ValueError, match="must not exceed"):
        classify_anomaly(1000, 3500, investigate_below=0.7, watch_below=0.5)


def test_screen_portfolio_counts():
    customers = [
        {"customer_id": "C1", "eac_kwh": 3500, "annualised_actual_kwh": 1000},  # investigate
        {"customer_id": "C2", "eac_kwh": 3500, "annualised_actual_kwh": 2000},  # watch
        {"customer_id": "C3", "eac_kwh": 3500, "annualised_actual_kwh": 3000},  # ok
    ]
    s = screen_portfolio(customers, **CUTS)
    assert (s["investigate"], s["watch"], s["ok"], s["unscreened"], s["total"]) == (1, 1, 1, 0, 3)


def test_screen_results_sorted_by_ratio():
    customers = [
        {"customer_id": "C1", "eac_kwh": 3500, "annualised_actual_kwh": 3000},
        {"customer_id": "C2", "eac_kwh": 3500, "annualised_actual_kwh": 1000},
    ]
    assert screen_portfolio(customers, **CUTS)["results"][0]["customer_id"] == "C2"


def test_screen_portfolio_empty_returns_zeros():
    result = screen_portfolio([])
    assert result["total"] == 0
    assert result["investigate"] == 0


# --- the defects corrected 2026-10-06 (read_access_and_theft_duties.md §5) ---

def test_the_unsourced_thresholds_are_none_not_an_invented_ratio():
    assert _THEFT_THRESHOLD_LOW is None
    assert _CONCERN_THRESHOLD_LOW is None


def test_without_a_supplied_threshold_a_customer_is_unscreened_not_classified():
    """The partition: with cut-offs every band is reachable; without, none is."""
    customers = [
        {"customer_id": "C1", "eac_kwh": 3500, "annualised_actual_kwh": 1000},
        {"customer_id": "C2", "eac_kwh": 3500, "annualised_actual_kwh": 2000},
        {"customer_id": "C3", "eac_kwh": 3500, "annualised_actual_kwh": 3000},
    ]
    with_cuts = screen_portfolio(customers, **CUTS)
    assert with_cuts["investigate"] and with_cuts["watch"] and with_cuts["ok"]
    without = screen_portfolio(customers)
    assert without["unscreened"] == 3
    assert without["investigate"] == without["watch"] == without["ok"] == 0
    assert without["results"][0]["ratio"] == pytest.approx(0.286, abs=1e-3)


def test_investigate_message_does_not_send_theft_to_ofgem():
    """No source requires reporting theft to Ofgem; the route is SLC 12A and REC Schedule 7."""
    message = classify_anomaly(500, 3500, **CUTS)["message"]
    assert "Ofgem" not in message
    assert "SLC 12A" in message and "TRAS" in message
