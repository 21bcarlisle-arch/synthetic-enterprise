"""W1_9 flex coupled-triad harness tests (L1): the belief-vs-truth revenue
gap is computed and non-trivial, plus the R15 MUTATION test proving the gap
control FIRES on its named defect (a divergent revenue forecast) and does NOT
false-fire (a leaking / perfect-foresight belief collapses the gap to ~0).
"""
from __future__ import annotations

import numpy as np
import pytest

from background.flex_dispatch_triad import (
    measure, build_gap_summary, measure_l2, build_gap_summary_l2,
    measure_l3, build_gap_summary_l3,
)
from background.gap_metric import prediction_gap
from sim.flex_dispatch import dispatch_and_settle, DeliveryModel
from company.market.flex_participation import form_participation_belief


def _synthetic_record(n=400, seed=1):
    """Residual and price CORRELATED but not identical (a gas-like term moves
    price, not residual) -- so the true (residual) and belief (price) dispatch
    sets genuinely differ: the honest L1 gap."""
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    gas_noise = rng.normal(0, 20, n)
    price = 40 + 0.004 * (residual - 30000) + gas_noise
    dates = np.array([f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(n)])
    return {"dates": dates, "residual_mw": residual, "derived_price": price}


def test_gap_is_computed_and_nontrivial():
    m = measure(_synthetic_record())
    assert m["n_periods"] == 400
    assert m["true_total_revenue_gbp"] > 0.0
    assert m["expected_total_revenue_gbp"] > 0.0
    # the belief and truth dispatch sets are NOT identical (real divergence)
    assert 0.0 < m["dispatch_set_jaccard"] < 1.0
    # the gap FIRES: strictly positive (the company misforecasts revenue)
    assert m["gap"] is not None and m["gap"] > 0.0


def test_build_gap_summary_shape():
    s = build_gap_summary(measure(_synthetic_record()))
    assert s["world_atom"] == "W1_9_dsr_flex_markets"
    assert s["level"] == "L1"
    assert s["gap"] > 0.0


def test_r15_mutation_control_fires_on_divergence_and_not_on_leak():
    """R15: the gap control must be able to FAIL on its named defect and must
    NOT false-fire.

    Named defect: the company's revenue forecast DIVERGES from the SIM truth.
      * REAL belief (price proxy, independent of residual)  -> gap > 0  (FIRES)
      * LEAKING belief (== the true residual-driven revenue) -> gap ~ 0  (a
        perfect-foresight belief; reaching gap 0 would mean observables leaked
        residual -- a wall violation, not a triumph). This proves the metric
        is not hardwired nonzero (fail-open): it CAN reach 0 when belief==truth.
    """
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec)

    # REAL, wall-respecting belief -> control FIRES.
    belief = form_participation_belief(truth.outturn_price, enrolled_mw=truth.enrolled_mw,
                                       period_hours=truth.period_hours)
    real_gap = prediction_gap(truth.true_utilised_revenue, belief.expected_utilised_revenue)
    assert real_gap.gap > 0.0, "control failed to fire on a genuinely divergent forecast"

    # MUTANT: a leaking / perfect-foresight belief that copies the true revenue
    # (the defect the wall exists to prevent) -> gap collapses to ~0.
    leaking_gap = prediction_gap(truth.true_utilised_revenue, truth.true_utilised_revenue)
    assert leaking_gap.gap == pytest.approx(0.0, abs=1e-9)

    # The two must be DISTINGUISHABLE by the metric -- a control that returned
    # the same value for a leak and a real belief would be theatre.
    assert real_gap.gap > leaking_gap.gap + 0.05


# --- L2: delivery-learning gain + baseline-methodology exposure -------------

def test_l2_delivery_learning_narrows_the_gap():
    """R15 (not fail-open): with STOCHASTIC delivery the L2 company de-rates
    using its own settlement observables and its gap is SMALLER than the L1
    perfect-delivery belief (learning genuinely helps) -- and with PERFECT
    delivery there is nothing to learn, so the gain is ~0 (the metric does not
    manufacture a gain out of nothing)."""
    rec = _synthetic_record()
    stochastic = measure_l2(rec, delivery=DeliveryModel(mean_ratio=0.7, dispersion=0.05, seed=4))
    assert stochastic["delivery_learning_gain"] > 0.0
    assert stochastic["learned_delivery_ratio"] < 1.0
    assert 0.0 < stochastic["true_mean_delivery_ratio"] < 1.0
    # perfect delivery: nothing to learn, learned ratio ~1, no spurious gain
    perfect = measure_l2(rec, delivery=None)
    assert perfect["learned_delivery_ratio"] == pytest.approx(1.0)
    assert perfect["delivery_learning_gain"] == pytest.approx(0.0, abs=1e-9)


def test_l2_baseline_exposure_fires_only_on_bias():
    """R15: the baseline-methodology exposure is 0 iff the company's baseline is
    UNBIASED and grows with |bias| -- it fires on its own named defect and does
    not false-fire when the methodology is honest."""
    rec = _synthetic_record()
    unbiased = measure_l2(rec, delivery=DeliveryModel(seed=7), baseline_bias=0.0)
    assert unbiased["baseline_error_frac"] == pytest.approx(0.0)
    assert unbiased["payment_at_risk_gbp"] == pytest.approx(0.0)

    biased = measure_l2(rec, delivery=DeliveryModel(seed=7), baseline_bias=0.2)
    assert biased["baseline_error_frac"] == pytest.approx(0.2)
    assert biased["payment_at_risk_gbp"] > 0.0


def test_l2_summary_shape():
    s = build_gap_summary_l2(measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1)))
    assert s["world_atom"] == "W1_9_dsr_flex_markets"
    assert s["level"] == "L2"
    assert s["delivery_learning_gain"] >= 0.0
    assert "payment_at_risk_gbp" in s


# ===========================================================================
# L3 -- THE STACKING GAP (the third loop for the multi-venue world)
# ===========================================================================

def test_l3_contention_blind_company_overclaims_physical_delivery():
    """THE HEADLINE. A party with no evidence of contention books both venues'
    MW against one portfolio and forecasts delivery it cannot physically
    produce. Assert the over-claim is real and material."""
    m = measure_l3(_synthetic_record())
    assert m["overclaim_mwh_frac_blind"] > 0.1, (
        "a contention-blind company must materially over-claim -- if it does "
        "not, the stacking gap is not being measured at all")
    assert m["true_delivered_mwh"] > 0.0


def test_l3_learning_from_own_instruction_feed_narrows_the_overclaim():
    """Observable-only learning must EARN its keep: reading its own instruction
    feed should shrink the over-claim versus the blind party."""
    m = measure_l3(_synthetic_record())
    assert m["contention_learning_gain"] > 0.0
    assert abs(m["overclaim_mwh_frac"]) < abs(m["overclaim_mwh_frac_blind"])


def test_R15_l3_overclaim_is_not_fail_open_on_an_uncontended_book():
    """The metric must fire ONLY on its own named defect. Give the venues a
    portfolio large enough that they never contend: the over-claim must
    collapse to ~0, proving a positive reading means real contention rather
    than an always-on number."""
    from sim.flex_dispatch import FlexPaymentBasis, VenueSpec
    from interface.contracts.flex_observable_seam import FlexVenue

    roomy = [
        VenueSpec(venue=FlexVenue.BALANCING_MECHANISM,
                  basis=FlexPaymentBasis.UTILISATION,
                  offered_mw=20.0, priority=1),
        VenueSpec(venue=FlexVenue.DSO_LOCAL_CONSTRAINT,
                  basis=FlexPaymentBasis.UTILISATION,
                  offered_mw=20.0, priority=2),
    ]
    m = measure_l3(_synthetic_record(), venues=roomy, portfolio_mw=1000.0)
    assert m["true_contention_binding_frac"] == 0.0, "fixture was meant to be uncontended"
    assert abs(m["overclaim_mwh_frac_blind"]) < 1e-9, (
        "over-claim must be 0 with no contention -- a non-zero reading here "
        "would mean the metric is always-on and proves nothing when positive")


def test_R15_l3_harness_independently_confirms_mw_conservation():
    """The harness must not take the SIM's word for the stacking law -- it
    re-asserts conservation itself and reports the worst over-allocation."""
    m = measure_l3(_synthetic_record())
    assert m["worst_over_allocation_mw"] == pytest.approx(0.0, abs=1e-9)


def test_l3_gap_is_never_zero_a_perfect_belief_would_mean_a_leak():
    """Independence: the company reads price + its own feed; the truth
    allocates on hidden priority against the true portfolio. If the belief
    recovered the truth exactly, the observables would have leaked."""
    m = measure_l3(_synthetic_record())
    assert m["gap"] > 0.0, (
        "a zero gap would mean the company recovered SIM-internal allocation "
        "from observables -- a wall violation, not a triumph")


def test_l3_headline_metric_carries_no_price():
    """No un-sourced availability price may move the headline score."""
    base = _synthetic_record()
    a = measure_l3(base, availability_price_gbp_per_mw_hour=10.0)
    b = measure_l3(base, availability_price_gbp_per_mw_hour=25.0)
    assert a["true_delivered_mwh"] == pytest.approx(b["true_delivered_mwh"])
    assert a["overclaim_mwh_frac_blind"] == pytest.approx(b["overclaim_mwh_frac_blind"])
    assert b["true_revenue_gbp"] > a["true_revenue_gbp"]


def test_l3_default_book_omits_the_capacity_market_without_a_sourced_price():
    """R12/R13 honoured in the DEFAULT: with no sourced CM price the book must
    fall back to a second utilisation venue rather than invent a GBP/kW."""
    m = measure_l3(_synthetic_record())
    venue_keys = {str(getattr(v.venue, "value", v.venue)) for v in m["truth"].venues}
    assert "capacity_market" not in venue_keys
    assert m["n_venues"] == 2


def test_l3_summary_shape():
    s = build_gap_summary_l3(measure_l3(_synthetic_record()))
    assert s["world_atom"] == "W1_9_dsr_flex_markets"
    assert s["level"] == "L3"
    for k in ("gap", "overclaim_mwh_frac", "contention_learning_gain",
              "true_contention_binding_frac", "worst_over_allocation_mw"):
        assert k in s
    assert "BENCHMARK REQUIRED" in s["note"]
