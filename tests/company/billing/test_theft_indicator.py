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


# --- the structural flags (2026-10-17, unbilled_energy_and_revenue_assurance.md §4a) ---

def _period(month, kwh, status="actual", commodity="electricity", **shares):
    return {"customer_id": "C1", "commodity": commodity, "period_start": f"2020-{month:02d}-01",
            "period_end": f"2020-{month:02d}-28", "read_status": status, "registered_kwh": kwh,
            **shares}


def test_an_empty_period_is_judged_only_between_two_actual_reads_and_by_who_was_named():
    """Defect: the flag fires on use, judges a span with no opening read, splits a span at an
    estimate, files a void or a gas meter as a theft lead, or can never fire at all."""
    from company.billing.theft_indicator import empty_period_flags

    named = empty_period_flags([_period(1, 300), _period(2, 0, "estimated"), _period(3, 0)])
    void = empty_period_flags([_period(1, 300), _period(2, 0, void_owner_share=1.0)])
    unnamed = empty_period_flags([_period(1, 300), _period(2, 0, occupier_share=1.0)])
    gas = empty_period_flags([_period(1, 300, commodity="gas"), _period(2, 0, commodity="gas")])
    # The whole partition is reachable before any leg is graded.
    assert ([f["status"] for f in named + void + unnamed + gas]
            == ["investigate", "void", "void", "not_screened"])
    assert named[0]["periods"] == 2 and named[0]["span_start"] == "2020-02-01"
    # A part-void period still has a named occupier on it.
    assert empty_period_flags([_period(1, 300), _period(2, 0, void_owner_share=0.4)])[0]["status"] == "investigate"
    assert empty_period_flags([_period(1, 0), _period(2, 300), _period(3, 5)]) == []
    assert empty_period_flags([_period(1, 300), _period(2, 0, "estimated"), _period(3, 40)]) == []
    assert "Ofgem" not in named[0]["message"] and "SLC 12A" in named[0]["message"]


def test_the_annual_window_refuses_a_short_window_and_holds_no_cut_of_its_own():
    """Defect: a month is read as a year, or the window classifies on a cut nobody sourced."""
    from company.billing.theft_indicator import (
        _ANNUAL_WINDOW_CUT,
        ANNUAL_WINDOW_MIN_DAYS,
        annual_window,
    )

    assert annual_window(100, 1000, ANNUAL_WINDOW_MIN_DAYS - 1, 0.5)["status"] == "not_annual"
    assert annual_window(100, 0, 365, 0.5)["status"] == "no_data"
    assert annual_window(100, 1000, 365, 0.5)["status"] == "investigate"
    assert annual_window(900, 1000, 365, 0.5)["status"] == "ok"
    # Keyed to the property, not today's value: a module cut must be one the page publishes.
    if _ANNUAL_WINDOW_CUT is None:
        assert annual_window(100, 1000, 365)["status"] == "unscreened"
    else:
        from pathlib import Path

        page = Path(__file__).resolve().parents[3] / "docs/market_research/unbilled_energy_and_revenue_assurance.md"
        assert str(_ANNUAL_WINDOW_CUT) in page.read_text().split("### 4a.")[1].split("## 5.")[0]
