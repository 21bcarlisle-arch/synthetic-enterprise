"""W1_9 COMPANY-side flex-participation tests. The company copes THROUGH THE
WALL: it forms its belief from OBSERVED price + its OWN settlement history only,
never a SIM internal. Covers the L1 price-proxy belief, the L2 learned delivery
de-rating + baseline estimate, and the epistemic-wall no-sim-import guard.
"""
from __future__ import annotations

import numpy as np
import pytest

from company.market.flex_participation import (
    DEFAULT_PRICE_SCARCITY_PERCENTILE,
    form_participation_belief,
    form_participation_belief_l2,
    learn_delivery_ratio,
    realised_revenue_from_settlement,
)


def _prices(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return 40 + rng.normal(0, 10, n)


def test_l1_belief_predicts_top_price_percentile():
    price = _prices()
    b = form_participation_belief(price, enrolled_mw=1.0, period_hours=1.0)
    # dispatch predicted only in the top-percentile price periods
    thr = np.percentile(price, DEFAULT_PRICE_SCARCITY_PERCENTILE)
    assert np.array_equal(b.predicted_dispatch_mask, price >= thr)
    assert b.total_expected_revenue_gbp > 0.0


def test_l1_empty_price_fails_loud():
    with pytest.raises(ValueError):
        form_participation_belief([], enrolled_mw=1.0, period_hours=1.0)


def test_learn_delivery_ratio_from_own_settlement():
    # instructed 2 MWh/event; observed metered mean 1.4 -> learned ratio 0.7
    ratio = learn_delivery_ratio([1.4, 1.4, 1.4], instructed_mwh=2.0)
    assert ratio == pytest.approx(0.7)
    # cold start (no history) falls back to the L1 perfect-delivery assumption
    assert learn_delivery_ratio(None, instructed_mwh=2.0) == 1.0
    assert learn_delivery_ratio([], instructed_mwh=2.0) == 1.0
    # FAIL-CLOSED on a degenerate enrolment
    with pytest.raises(ValueError):
        learn_delivery_ratio([1.0], instructed_mwh=0.0)


def test_l2_belief_de_rates_expected_revenue_below_l1():
    """The L2 company, having learned its portfolio under-delivers, forecasts
    LESS utilisation revenue than the L1 perfect-delivery belief."""
    price = _prices()
    l1 = form_participation_belief(price, enrolled_mw=2.0, period_hours=1.0)
    # observed history: 70% delivery against the 2 MWh instructed volume
    l2 = form_participation_belief_l2(
        price, enrolled_mw=2.0, period_hours=1.0,
        observed_delivery_mwh=[1.4] * 10)
    assert l2.learned_delivery_ratio == pytest.approx(0.7)
    assert l2.total_expected_revenue_gbp == pytest.approx(0.7 * l1.total_expected_revenue_gbp)
    # same dispatch SET as L1 (only the volume de-rates, not the trigger)
    assert np.array_equal(l1.predicted_dispatch_mask, l2.predicted_dispatch_mask)


def test_l2_baseline_estimate_carries_the_bias():
    price = _prices()
    unbiased = form_participation_belief_l2(price, enrolled_mw=2.0, period_hours=1.0)
    assert unbiased.estimated_baseline_mwh == pytest.approx(2.0)
    biased = form_participation_belief_l2(
        price, enrolled_mw=2.0, period_hours=1.0, baseline_bias=0.15)
    assert biased.estimated_baseline_mwh == pytest.approx(2.0 * 1.15)


def test_realised_revenue_tolerant_of_empty_feed():
    assert realised_revenue_from_settlement(None) == 0.0
    assert realised_revenue_from_settlement([]) == 0.0


def test_no_sim_import():
    """Epistemic wall: the company module must not import any SIM/simulation
    internal (it reads observables only)."""
    import company.market.flex_participation as mod

    src = open(mod.__file__).read()
    assert "import sim" not in src and "from sim" not in src
    assert "import simulation" not in src and "from simulation" not in src
