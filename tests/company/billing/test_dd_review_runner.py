"""DD4a closed-loop + fail-closed tests for the live annual-DD-review organ.

The pure review() thresholds are already covered by test_dd_review.py; these
tests exercise the DRIVER (run_annual_reviews): anniversary timing, the
year-on-year re-estimation chain, determinism/idempotency (C-S2), the
large_increase shock flag (fail-closed, R15-style), and wall-cleanliness
(reads only company-observable bill fields)."""
from __future__ import annotations

from company.billing.dd_review import DDAction
from company.billing.dd_review_runner import (
    LARGE_INCREASE_THRESHOLD_PCT,
    run_annual_reviews,
)


def _bills(cid: str, monthly_amounts: list[float], start=(2020, 1)):
    """One bill per month from ``start``, ``monthly_amounts`` in order."""
    out = []
    y, m = start
    for amt in monthly_amounts:
        out.append(
            {
                "customer_id": cid,
                "period_end": f"{y:04d}-{m:02d}-28",
                "total_amount_gbp": amt,
            }
        )
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


# ---- anniversary timing --------------------------------------------------

def test_no_review_before_twelve_months():
    # Only 6 months of data -> no completed year -> no review event.
    result = run_annual_reviews(_bills("C1", [50.0] * 6))
    assert result.events == []
    assert result.summary()["total_reviews"] == 0


def test_first_review_fires_after_a_full_year():
    # 13 bills: window 0 (months 0..11) is complete once month 12 exists.
    result = run_annual_reviews(_bills("C1", [100.0] * 13))
    assert len(result.events) == 1
    assert result.events[0].window_index == 0


# ---- action classification over a real year ------------------------------

def test_underestimated_dd_yields_large_increase():
    # First (Jan) bill £40 -> standing DD £40 -> implied annual £480.
    # Actual year of spend is much higher -> big INCREASE, material shock.
    amounts = [40.0] + [120.0] * 11 + [999.0]  # 13th bill just completes the year
    result = run_annual_reviews(_bills("C1", amounts))
    ev = result.events[0]
    assert ev.action == DDAction.INCREASE.value
    assert ev.variance_pct > LARGE_INCREASE_THRESHOLD_PCT
    assert ev.large_increase is True
    assert result.summary()["large_increase_count"] == 1


def test_stable_customer_maintains_and_is_not_a_shock():
    result = run_annual_reviews(_bills("C1", [100.0] * 13))
    ev = result.events[0]
    assert ev.action == DDAction.MAINTAIN.value
    assert ev.large_increase is False


def test_overpaying_customer_decreases():
    # First bill £150 -> implied annual £1800; actual year ~£1200 -> DECREASE.
    amounts = [150.0] + [100.0] * 11 + [100.0]
    result = run_annual_reviews(_bills("C1", amounts))
    ev = result.events[0]
    assert ev.action == DDAction.DECREASE.value
    assert ev.large_increase is False


# ---- fail-closed / R15: the shock flag must not fail open ----------------

def test_moderate_increase_is_not_flagged_large():
    # Between +5% (INCREASE fires) and +15% (LARGE cut): must be INCREASE but
    # NOT large_increase. Proves the flag is a real >threshold test, not
    # always-true (fail-open) nor coupled to action alone.
    # Standing DD £100 -> implied £1200. Target actual ~ +10% = £1320.
    amounts = [100.0] * 11 + [1320.0 - 100.0 * 11] + [100.0]
    result = run_annual_reviews(_bills("C1", amounts))
    ev = result.events[0]
    assert ev.action == DDAction.INCREASE.value
    assert 5.0 < ev.variance_pct <= LARGE_INCREASE_THRESHOLD_PCT
    assert ev.large_increase is False


def test_large_flag_requires_increase_not_just_magnitude():
    # A large NEGATIVE variance (big DECREASE) must never be a large_increase.
    amounts = [500.0] + [50.0] * 11 + [50.0]
    result = run_annual_reviews(_bills("C1", amounts))
    ev = result.events[0]
    assert ev.action == DDAction.DECREASE.value
    assert abs(ev.variance_pct) > LARGE_INCREASE_THRESHOLD_PCT
    assert ev.large_increase is False


# ---- year-on-year re-estimation chain ------------------------------------

def test_second_year_uses_prior_recommendation_as_standing_dd():
    # 25 bills -> windows 0 and 1 both complete. Year-2 standing DD must equal
    # year-1's recommendation (the review reset the DD).
    result = run_annual_reviews(_bills("C1", [40.0] + [120.0] * 23 + [120.0]))
    assert len(result.events) == 2
    y0, y1 = result.events
    assert y0.window_index == 0 and y1.window_index == 1
    assert y1.current_dd_gbp == y0.recommended_monthly_gbp


# ---- determinism / idempotency (C-S2) ------------------------------------

def test_deterministic_and_idempotent():
    bills = _bills("C1", [40.0] + [120.0] * 12) + _bills("C2", [100.0] * 13, start=(2021, 6))
    a = run_annual_reviews(bills).serialise()
    b = run_annual_reviews(list(reversed(bills))).serialise()  # order-insensitive
    assert a == b


# ---- wall-cleanliness: only company-observable bill fields ---------------

def test_reads_only_observable_bill_fields():
    # A bill dict carrying ONLY the three company-observable keys must work --
    # the organ never reaches for a SIM-internal field.
    minimal = [
        {"customer_id": "C1", "period_end": f"2020-{m:02d}-28", "total_amount_gbp": 100.0}
        for m in range(1, 13)
    ] + [{"customer_id": "C1", "period_end": "2021-01-28", "total_amount_gbp": 100.0}]
    result = run_annual_reviews(minimal)
    assert result.summary()["total_reviews"] == 1


def test_empty_portfolio():
    result = run_annual_reviews([])
    assert result.events == []
    assert result.serialise()["summary"]["total_reviews"] == 0
