"""W1_9 flex coupled-triad harness tests (L1): the belief-vs-truth revenue
gap is computed and non-trivial, plus the R15 MUTATION test proving the gap
control FIRES on its named defect (a divergent revenue forecast) and does NOT
false-fire (a leaking / perfect-foresight belief collapses the gap to ~0).
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from background.flex_dispatch_triad import (
    build_gap_summary,
    build_gap_summary_l2,
    build_gap_summary_l3,
    measure,
    measure_l2,
    measure_l3,
    solicit_registration,
)
from background.gap_metric import prediction_gap
from company.market.flex_participation import form_participation_belief
from sim.flex_dispatch import (
    DeliveryModel,
    UnregisteredDispatch,
    _base_date,
    dispatch_and_settle,
)


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
    from interface.contracts.flex_observable_seam import FlexVenue
    from sim.flex_dispatch import FlexPaymentBasis, VenueSpec

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


# ===========================================================================
# EP6 pass 22 -- THE HARNESS CROSSES ON THE WIRE. These are the proofs that
# the codecs are not a spare path built beside the live one: this is the
# module that scores the belief-vs-truth gap, so the gap is now measured
# against a company that only ever saw encoded, version-checked bytes.
# ===========================================================================


def test_the_L2_statement_REALLY_crosses_the_wire_and_not_beside_it():
    """MUTATION on the LIVE path. A codec nobody calls leaves every codec test
    green -- the only way to see that is to break the codec and require the
    harness to notice. Patch the company's seam read to refuse and `measure_l2`
    must FAIL; unpatched, it must still produce its gap.

    NULL CONTROL is the unpatched twin below the assertion, not a separate
    test: without it the mutation is satisfied by a harness that fails always.
    """
    import background.flex_dispatch_triad as triad
    rec = _synthetic_record()
    sentinel = RuntimeError("the seam refused")

    def _refuse(_messages):
        raise sentinel

    original = triad.observe_settlement_wire
    try:
        triad.observe_settlement_wire = _refuse
        with pytest.raises(RuntimeError) as exc:
            measure_l2(rec, delivery=DeliveryModel(seed=3))
        assert exc.value is sentinel
    finally:
        triad.observe_settlement_wire = original
    assert measure_l2(rec, delivery=DeliveryModel(seed=3))["gap"] is not None


def test_the_L3_feeds_REALLY_cross_the_wire():
    """The same proof for the stacked instruction and settlement feeds. Wiring
    L1/L2 alone would have moved the census reading to `3 of 3` with these two
    still handed over as objects -- the identical defect, one granularity below
    the instrument's, which is the trap this atom has now met twice."""
    import background.flex_dispatch_triad as triad
    rec = _synthetic_record()
    sentinel = RuntimeError("the instruction feed refused")

    def _refuse(_message, **_kw):
        raise sentinel

    original = triad.observe_response_wire
    try:
        triad.observe_response_wire = _refuse
        with pytest.raises(RuntimeError) as exc:
            measure_l3(rec)
        assert exc.value is sentinel
    finally:
        triad.observe_response_wire = original
    assert measure_l3(rec)["gap"] is not None


def test_TRANSPORT_DOES_NOT_MOVE_THE_BELIEF():
    """The atom's actual claim, asserted rather than asserted-about: a mock
    counterparty and a real one are INDISTINGUISHABLE to the company. Two
    companies see the same settlement run -- one handed the lines as objects
    across a call frame, one handed the same run as bytes it decoded itself --
    and their beliefs must be identical to the last float. If encoding moves
    the belief at all, the envelope is transport in name only."""
    from company.market.flex_participation import (
        form_participation_belief_l2,
        observe_settlement_wire,
    )
    from sim.flex_dispatch import (
        emit_settlement_lines,
        emit_settlement_lines_over_wire,
    )
    truth = dispatch_and_settle(_synthetic_record(), delivery=DeliveryModel(seed=7))
    book = solicit_registration(truth, enrolled_mw=truth.enrolled_mw).venue_book
    as_objects = [r.payload.metered_delivery_mwh for r in emit_settlement_lines(truth)]
    as_bytes = [
        line.metered_delivery_mwh
        for line in observe_settlement_wire(
            emit_settlement_lines_over_wire(truth, registrations=book))
    ]
    assert as_bytes == as_objects and len(as_bytes) > 0

    kw = dict(enrolled_mw=1.0, period_hours=1.0)
    object_belief = form_participation_belief_l2(
        truth.outturn_price, observed_delivery_mwh=as_objects, **kw)
    wire_belief = form_participation_belief_l2(
        truth.outturn_price, observed_delivery_mwh=as_bytes, **kw)
    assert wire_belief.learned_delivery_ratio == object_belief.learned_delivery_ratio
    assert np.array_equal(
        wire_belief.expected_utilised_revenue, object_belief.expected_utilised_revenue)


def test_the_wire_carries_the_version_on_EVERY_message_the_harness_crosses():
    """Not a call-signature claim -- the emitted bytes are inspected. Channel
    D's lesson applied to channel C: the field being structurally present on
    the envelope is exactly what made its absence from the wire invisible for
    four days."""
    from interface.contracts.flex_observable_seam import SCHEMA_VERSION
    from sim.flex_dispatch import emit_settlement_lines_over_wire
    truth = dispatch_and_settle(_synthetic_record(), delivery=DeliveryModel(seed=7))
    book = solicit_registration(truth, enrolled_mw=truth.enrolled_mw).venue_book
    messages = emit_settlement_lines_over_wire(truth, registrations=book)
    assert len(messages) > 0
    assert all(m["schema_version"] == SCHEMA_VERSION for m in messages)


# ===========================================================================
# EP6 pass 54 -- IS THE LOOP SOLICITED?
#
# Pass 53 gave the flex seam a request leg and 27 controls; the running loop
# still began at a dispatch instruction, so the world settled `FLEX_UNIT_1` --
# a keyword default -- to a company that had never enrolled it, and the gap was
# scored on that statement. `measure_l2` now registers first, through the
# production seam, and reports whether the statement it scored answers a
# registration the company holds.
# ===========================================================================


def test_the_L2_statement_answers_a_registration_the_company_HOLDS():
    m = measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1))
    assert m["settlement_solicited"] is True
    # The reference is the VENUE's -- the company did not mint it.
    assert m["enrolment_reference"].startswith("BALANCING_MECHANISM-REG-")


def test_MUTATION_a_world_settling_a_unit_NOBODY_enrolled_is_now_REFUSED(monkeypatch):
    """FLIPPED AT EP6 PASS 57, and the flip is the point rather than a repair.

    This test used to reproduce the pass-54 state -- the settlement feed names a
    unit nobody registered -- and assert the harness SCORED it unsolicited. That
    was the strongest claim available while the check was an observation. It now
    reds on its own success: the venue consults its own book before anything
    crosses, so the stranger's lines never reach the wire to be scored. Asserting
    the refusal is a strictly stronger claim than asserting the score, so the
    test asserts the refusal -- this project's recorded pattern for a control
    whose subject was fixed, kept rather than deleted because its useful half was
    never "the score is False" but "a unit nobody enrolled must not be settled".
    """
    import background.flex_dispatch_triad as triad

    real = triad.emit_settlement_lines_over_wire

    def settle_a_stranger(truth, *, unit_id="FLEX_UNIT_1", **kw):
        return real(truth, unit_id="A_UNIT_NOBODY_ENROLLED", **kw)

    monkeypatch.setattr(triad, "emit_settlement_lines_over_wire", settle_a_stranger)
    with pytest.raises(UnregisteredDispatch):
        measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1))


def test_the_solicited_OBSERVATION_can_still_be_False__it_is_not_always_green(monkeypatch):
    """The world law above does not make `settlement_solicited` unfalsifiable,
    and a check that could only ever be True would be theatre.

    The law refuses at EMISSION; the observation reads the DECODED lines. So the
    discriminating mutation is downstream of both: a decoder handing back a unit
    the company never registered -- a mis-keyed feed, or the same statement read
    for the wrong party -- is exactly what this observation is for, and it still
    scores False."""
    from dataclasses import replace

    import background.flex_dispatch_triad as triad

    real = triad.observe_settlement_wire

    def decode_as_a_stranger(messages):
        return [replace(line, unit_id="A_UNIT_NOBODY_ENROLLED") for line in real(messages)]

    monkeypatch.setattr(triad, "observe_settlement_wire", decode_as_a_stranger)
    m = measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1))

    assert m["settlement_solicited"] is False


def test_the_request_leg_does_not_touch_the_SCORE():
    """R12/R13. Enrolling is a crossing, not a tuning knob: the L2 gap must be
    the one an independent recomputation from truth and belief gives, so no
    published figure moved when the loop gained its first leg."""
    m = measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1))
    independent = prediction_gap(
        m["truth"].true_utilised_revenue, m["belief"].expected_utilised_revenue)
    assert m["gap"] == independent.gap


def test_the_L2_summary_carries_the_solicited_fact_a_digest_would_quote():
    s = build_gap_summary_l2(measure_l2(_synthetic_record(), delivery=DeliveryModel(seed=1)))
    assert s["settlement_solicited"] is True
    assert s["enrolment_reference"]


def test_the_company_holds_the_SAME_reference_the_world_will_honour():
    """The injection is the substance of the pass-57 change, so it is asserted
    rather than assumed: the book the seam registered into IS the book the
    world's dispatch legs consult, and the reference the company got back off
    the wire is the one that covers the delivered window.

    Until now the venue's book was minted inside the seam and died with it, so
    these were two facts that happened to agree. One book makes them one fact.
    """
    from interface.contracts.flex_observable_seam import FlexVenue

    truth = dispatch_and_settle(_synthetic_record(), delivery=DeliveryModel(seed=1))
    solicited = solicit_registration(truth, enrolled_mw=truth.enrolled_mw)

    called = [
        _base_date(d) for d, on in zip(truth.dates, truth.dispatch_mask) if on
    ]
    assert called
    for start in (min(called), max(called)):
        held = solicited.venue_book.covers(
            solicited.outcome.unit_id,
            FlexVenue.BALANCING_MECHANISM,
            start,
            start + dt.timedelta(hours=truth.period_hours),
        )
        assert held == solicited.outcome.enrolment_reference

    # NULL CONTROL: the same book does NOT cover a unit it never registered, so
    # the assertion above is about this registration and not about `covers`
    # returning something for anything.
    assert solicited.venue_book.covers(
        "A_UNIT_NOBODY_ENROLLED",
        FlexVenue.BALANCING_MECHANISM,
        min(called),
        min(called) + dt.timedelta(hours=truth.period_hours),
    ) is None
