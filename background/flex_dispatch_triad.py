"""COUPLED-TRIAD runner for the W1_9 DSR/flexibility markets atom (L1-L3).

The third loop of the flex coupled triad (COUPLED_TRIAD: SIM adds depth ->
COMPANY copes through the wall -> HARNESS measures the belief-vs-truth GAP;
the gap is the score). This is HARNESS code: it sits OUTSIDE the epistemic
wall and is the ONLY layer permitted to hold the SIM ground truth AND the
company belief side by side (design 1.3). It lives in `background/` (like
`weather_price_triad`), NOT under `company/`, so it may import both sides.

  1. SIM adds depth   -- sim.flex_dispatch (W1_9): dispatches enrolled flex on
                         the TRUE (residual-driven) scarcity schedule and
                         settles at the observed outturn price. Residual demand
                         is the hidden truth; only the dispatch instruction +
                         settlement line (observables) cross the seam.
  2. COMPANY copes    -- company.market.flex_participation: predicts dispatch
                         in the top price-percentile periods (a price-derived
                         scarcity PROXY) and forecasts utilisation revenue.
                         It sees ONLY the observed price -- never residual.
  3. HARNESS measures -- prediction_gap(true_revenue, expected_revenue): the
                         company's forecast utilised-revenue vector vs the
                         SIM's true utilised-revenue vector, normalised to the
                         no-skill (blind, climatological-mean) baseline. The
                         GAP is the L1 score.

R15 INDEPENDENCE / NOT A TAUTOLOGY. The truth dispatches on RESIDUAL DEMAND
(convex composed physics); the belief dispatches on PRICE percentile
(observables-only proxy). Different machinery -- residual drives price but is
not identical to it -- so the gap is a real form-inadequacy measurement. A
belief that recovered the true schedule would mean the observables leaked
residual (a wall violation, not a triumph). The mutation test
(`tests/background/test_flex_dispatch_triad.py`) proves the harness FIRES:
a divergent (price-proxy) belief yields gap > 0, while a leaking/perfect-
foresight belief collapses the gap to ~0 -- so the metric is neither hardwired
nonzero (fail-open) nor blind to divergence.

R12/R13. Nothing here is tuned to a target gap. The scarcity percentile is a
BASELINE structural choice (how often the world is tight), not fitted to any
company outcome. `enrolled_mw`/`period_hours` are illustrative and the
normalised gap is invariant to them, so no un-sourced £/MW figure moves the
score. Every real £/kW/yr, availability price and baseline-window figure
remains BENCHMARK REQUIRED (source: NESO/Elexon); the L3 default book
therefore omits the Capacity Market venue entirely unless a sourced price is
passed, and the L3 headline is measured in PHYSICAL MWh, which carries no
price at all.

LEVELS PRESENT HERE (registered, not implied):
  * L1 `measure`      -- one venue, perfect delivery: the price-proxy gap.
  * L2 `measure_l2`   -- stochastic delivery + baseline-methodology exposure.
  * L3 `measure_l3`   -- N concurrent venues on ONE portfolio: the STACKING
                         over-claim a contention-blind party books.
"""
from __future__ import annotations

import datetime as dt
from typing import Dict, Optional, Sequence

import numpy as np

from background.gap_metric import prediction_gap
from company.interfaces.sim_interface import build_sim_interface
from company.market.flex_participation import (
    CompanyVenueOffer,
    form_participation_belief,
    form_participation_belief_l2,
    form_stacked_belief,
    observe_response_wire,
    observe_settlement_wire,
)
from interface.contracts.flex_observable_seam import (
    FlexDirection,
    FlexDispatchInstruction,
    FlexEnrolment,
    FlexEnrolmentOutcome,
    FlexVenue,
)
from sim.flex_dispatch import (
    DEFAULT_AVAILABILITY_CALL_PERCENTILE,
    DEFAULT_ENROLLED_MW,
    DEFAULT_PERIOD_HOURS,
    TRUE_SCARCITY_PERCENTILE,
    DeliveryModel,
    FlexPaymentBasis,
    VenueSpec,
    # `_base_date` is the world's own date parser, imported rather than
    # restated: these are WORLD dates and a second parser in the harness would
    # be a second thing to keep true. Nothing crosses the wall here -- the
    # harness is the one layer allowed both sides.
    _base_date,
    assert_mw_conservation,
    dispatch_and_settle,
    dispatch_and_settle_stacked,
    emit_dispatch_instructions_stacked_over_wire,
    emit_settlement_lines_over_wire,
    emit_settlement_lines_stacked_over_wire,
)

WORLD_ATOM_ID = "W1_9_dsr_flex_markets"
#: The unit this loop's portfolio is registered and settled under. ONE literal,
#: read by the enrolment and never by the settlement emitter -- see
#: `solicit_registration` below for why that separation is the whole point.
LOOP_UNIT_ID = "FLEX_UNIT_1"
# The company twin registered for this world atom (the flex-participation
# belief facet). A dedicated C-atom id is a proposed follow-on; the flex
# participation module is the real twin meanwhile.
TWIN_ATOM_ID = "flex_participation_belief"


def solicit_registration(
    truth,
    *,
    enrolled_mw: float,
    unit_id: str = LOOP_UNIT_ID,
    venue: FlexVenue = FlexVenue.BALANCING_MECHANISM,
) -> FlexEnrolmentOutcome:
    """LEG 1 OF THE LIVE LOOP: the company ASKS this venue to register its unit,
    through the production seam, and reads the venue's answer.

    WHY THE LOOP GAINED A FIRST LEG (EP6 pass 54). Every measurement below used
    to begin at a dispatch instruction: the world settled `FLEX_UNIT_1` -- a
    KEYWORD DEFAULT -- over windows nobody had declared, and the company formed
    beliefs about the resulting statement because it had no record against which
    to ask whether it had asked. `tools.wall_channel_census` read exactly that
    as UNSOLICITED INBOUND. Pass 53 gave the seam a request leg and tests; this
    is the running loop using it, which is the difference between a leg that
    exists and a leg that carries traffic.

    THE CLOCK IS THE WORLD'S. The harness holds the world, so it is the harness
    that hands the venue its read time -- one day before the record opens, so
    the availability window is registered BEFORE it is delivered, as a real
    party registers. The company supplies only its own `as_of`; the seam refuses
    outright rather than judging the window on the submitter's clock.

    Returns the venue's `FlexEnrolmentOutcome`. Raises (never returns an empty
    registration) if the venue declines -- a loop that measured a gap against a
    refused registration would be scoring a business that does not exist.
    """
    # SPAN, not first-to-last: a record's dates are not required to be sorted
    # (the triad's own synthetic fixture cycles months), and a window whose end
    # preceded its start is refused WINDOW_NOT_A_WINDOW -- correctly, and for a
    # reason that has nothing to do with what is being measured.
    stamps = [_base_date(d) for d in truth.dates]
    window_start = min(stamps)
    window_end = max(stamps) + dt.timedelta(hours=truth.period_hours)
    venue_clock = window_start - dt.timedelta(days=1)
    seam = build_sim_interface(flex_venue_clock=venue_clock)
    enrolment = FlexEnrolment(
        unit_id=unit_id,
        venue=venue,
        offered_mw=float(enrolled_mw),
        direction=FlexDirection.TURN_DOWN,
        window_start=window_start,
        window_end=window_end,
    )
    return seam.enrol_flex(enrolment, as_of=venue_clock)


def measure(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    enrolled_mw: float = DEFAULT_ENROLLED_MW,
    period_hours: float = DEFAULT_PERIOD_HOURS,
) -> Dict[str, object]:
    """Run the coupled loop and compute the L1 revenue gap.

    SIM truth dispatches on residual (hidden); the company forecasts from the
    OBSERVED price only. `out` may be injected (a small synthetic record) for
    a fast, deterministic run; None loads the real W1_6 derived-price record.
    Returns the gap plus enough numbers for a caller/test to quote the real
    values (true vs expected revenue, dispatch-set overlap)."""
    truth = dispatch_and_settle(out, enrolled_mw=enrolled_mw, period_hours=period_hours)

    # -- COMPANY side: only the OBSERVED price crosses. The company never sees
    #    residual; it infers scarcity from price. --
    belief = form_participation_belief(
        truth.outturn_price, enrolled_mw=enrolled_mw, period_hours=period_hours,
    )

    # -- HARNESS: hold truth and belief side by side; gap over the per-period
    #    utilised-revenue vectors. Normalised to the blind (climatological-mean)
    #    no-skill baseline by prediction_gap. --
    gap = prediction_gap(truth.true_utilised_revenue, belief.expected_utilised_revenue)

    overlap = int((truth.dispatch_mask & belief.predicted_dispatch_mask).sum())
    union = int((truth.dispatch_mask | belief.predicted_dispatch_mask).sum())
    jaccard = float(overlap / union) if union else 0.0

    return {
        "gap": gap.gap,
        "raw_gap_gbp": gap.raw_gap,
        "g0_noskill_gbp": gap.g0,
        "true_total_revenue_gbp": truth.total_true_revenue_gbp,
        "expected_total_revenue_gbp": belief.total_expected_revenue_gbp,
        "n_true_dispatch": truth.n_dispatch,
        "n_predicted_dispatch": belief.n_predicted_dispatch,
        "dispatch_set_jaccard": jaccard,
        "n_periods": int(truth.true_utilised_revenue.size),
        "gap_result": gap,
        "truth": truth,
        "belief": belief,
    }


def measure_l2(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    enrolled_mw: float = DEFAULT_ENROLLED_MW,
    period_hours: float = DEFAULT_PERIOD_HOURS,
    delivery: Optional[DeliveryModel] = None,
    baseline_bias: float = 0.0,
) -> Dict[str, object]:
    """Run the L2 coupled loop and score TWO belief-vs-truth gaps a real flex
    party carries beyond L1:

      1. DELIVERY-LEARNING gap -- the SIM delivers stochastically LESS than
         instructed (rebound / non-response). The L1 company (perfect-delivery
         assumption) over-forecasts; the L2 company DE-RATES using the ratio it
         learned from its OWN settlement observables. `delivery_learning_gain`
         = gap(L1 belief) - gap(L2 belief): positive means the observable-only
         learning genuinely narrowed the gap (and is ~0 with perfect delivery,
         so the metric is not fail-open).
      2. BASELINE-METHODOLOGY exposure -- the company estimates its
         counterfactual baseline with a (possibly biased) method it cannot
         validate against the SIM truth. `baseline_error_frac` and
         `payment_at_risk_gbp` quantify the clawback exposure a biased baseline
         creates -- 0 iff unbiased, so the exposure metric fires on its own
         defect (R15).

    `delivery` None reproduces L1 (perfect delivery); pass a `DeliveryModel`
    for the L2 world. The company's settlement history is the OBSERVABLE metered
    deliveries from this run (a steady-state participant with a statement; a
    point-in-time train/forecast split is an L2 refinement, registered)."""
    truth = dispatch_and_settle(
        out, enrolled_mw=enrolled_mw, period_hours=period_hours, delivery=delivery)

    # -- LEG 1: THE COMPANY ASKS, before anything is settled to it. Registered
    #    a day before the record opens, through the production seam. --
    registration = solicit_registration(truth, enrolled_mw=enrolled_mw)

    # -- OBSERVABLES the company reads off its own statement (metered delivery
    #    per settled event). It never sees the true ratio or true baseline. --
    # The statement crosses as BYTES (EP6): the world encodes, the company
    # decodes through its own codec and version-checks in between. Everything
    # the L2 de-rating is learned from has been refusable at the seam.
    settlement = observe_settlement_wire(
        emit_settlement_lines_over_wire(truth, unit_id=LOOP_UNIT_ID))
    observed_delivery = [line.metered_delivery_mwh for line in settlement]

    # -- IS THIS STATEMENT SOLICITED? Two quantities from two sides: the unit
    #    the WORLD settled to (read off the decoded settlement lines, not off
    #    the argument passed in -- an emitter that ignored `unit_id` would
    #    otherwise still score solicited) against the unit the VENUE said it
    #    registered. Equal means every line answers a registration this company
    #    holds; unequal means the world is paying a unit nobody enrolled, which
    #    is the state this whole loop was in until pass 54. --
    settled_units = {line.unit_id for line in settlement}
    settlement_solicited = bool(settled_units) and settled_units == {registration.unit_id}

    # -- COMPANY L2: learns a de-rating from those observables; estimates its
    #    baseline (possibly biased). Only observed price + own settlement. --
    belief = form_participation_belief_l2(
        truth.outturn_price, enrolled_mw=enrolled_mw, period_hours=period_hours,
        observed_delivery_mwh=observed_delivery, baseline_bias=baseline_bias)
    # L1 baseline company (perfect-delivery assumption) for the learning-gain
    # comparison.
    belief_l1 = form_participation_belief(
        truth.outturn_price, enrolled_mw=enrolled_mw, period_hours=period_hours)

    gap = prediction_gap(truth.true_utilised_revenue, belief.expected_utilised_revenue)
    gap_l1 = prediction_gap(truth.true_utilised_revenue, belief_l1.expected_utilised_revenue)

    # -- HARNESS: baseline-methodology exposure. true baseline per dispatched
    #    event vs the company's estimate; phantom-volume payment a biased
    #    baseline would be paid (and exposed to clawback). --
    true_baseline_per_event = float(enrolled_mw * period_hours)
    est_baseline = belief.estimated_baseline_mwh
    baseline_error_frac = (
        abs(est_baseline - true_baseline_per_event) / true_baseline_per_event
        if true_baseline_per_event else 0.0)
    disp_price = truth.outturn_price[truth.dispatch_mask]
    payment_at_risk_gbp = float(abs(est_baseline - true_baseline_per_event) * disp_price.sum())

    return {
        "gap": gap.gap,
        "gap_l1_belief": gap_l1.gap,
        "delivery_learning_gain": float(gap_l1.gap - gap.gap),
        "learned_delivery_ratio": belief.learned_delivery_ratio,
        "true_mean_delivery_ratio": truth.mean_delivery_ratio,
        "baseline_bias": baseline_bias,
        "baseline_error_frac": baseline_error_frac,
        "payment_at_risk_gbp": payment_at_risk_gbp,
        "enrolment_reference": registration.enrolment_reference,
        "settlement_solicited": settlement_solicited,
        "true_total_revenue_gbp": truth.total_true_revenue_gbp,
        "expected_total_revenue_gbp": belief.total_expected_revenue_gbp,
        "n_true_dispatch": truth.n_dispatch,
        "n_predicted_dispatch": belief.n_predicted_dispatch,
        "n_periods": int(truth.true_utilised_revenue.size),
        "gap_result": gap,
        "truth": truth,
        "belief": belief,
    }


def build_gap_summary(measurement: Dict[str, object]) -> Dict[str, object]:
    """Shape a compact, quotable summary of the L1 flex revenue gap for a
    digest / coupled-pair report. NOTE: this deliberately does NOT write to
    `docs/observability/coupled_gap_ledger.json` -- an un-wired entry on that
    shared surface reds its consumer's tests (a known hazard). Wiring the
    ledger line is a follow-on once the ledger consumer is extended for this
    pair; the gap is computed and asserted by the triad test meanwhile."""
    return {
        "world_atom": WORLD_ATOM_ID,
        "twin_atom": TWIN_ATOM_ID,
        "level": "L1",
        "metric": "prediction (per-period utilised-revenue MAE / no-skill)",
        "gap": measurement["gap"],
        "raw_gap_gbp": measurement["raw_gap_gbp"],
        "g0_noskill_gbp": measurement["g0_noskill_gbp"],
        "true_total_revenue_gbp": measurement["true_total_revenue_gbp"],
        "expected_total_revenue_gbp": measurement["expected_total_revenue_gbp"],
        "dispatch_set_jaccard": measurement["dispatch_set_jaccard"],
        "note": (
            "company forecasts flex utilisation from OBSERVED price (scarcity "
            "proxy); SIM truth dispatches on hidden residual demand -- the gap "
            "is that forecast error. L1: perfect delivery, one venue, "
            "scale-free units; L2+ benchmark-gated."
        ),
    }


def build_gap_summary_l2(measurement: Dict[str, object]) -> Dict[str, object]:
    """Compact, quotable summary of the L2 flex gaps (delivery-learning +
    baseline-methodology exposure) for a digest / coupled-pair report. Like the
    L1 summary it deliberately does NOT write the shared coupled_gap_ledger
    (an un-wired entry reds its consumer's tests); the gap is asserted by the
    triad test meanwhile."""
    return {
        "world_atom": WORLD_ATOM_ID,
        "twin_atom": TWIN_ATOM_ID,
        "level": "L2",
        "metric": "delivery-learning gain + baseline-methodology exposure",
        "gap": measurement["gap"],
        "gap_l1_belief": measurement["gap_l1_belief"],
        "delivery_learning_gain": measurement["delivery_learning_gain"],
        "learned_delivery_ratio": measurement["learned_delivery_ratio"],
        "true_mean_delivery_ratio": measurement["true_mean_delivery_ratio"],
        "baseline_error_frac": measurement["baseline_error_frac"],
        "payment_at_risk_gbp": measurement["payment_at_risk_gbp"],
        # Not a score and not tuned (R12): a structural fact about whether the
        # statement this gap was computed from answers a registration the
        # company holds. A digest quoting a gap against an UNSOLICITED feed is
        # quoting a business that never asked to exist.
        "enrolment_reference": measurement["enrolment_reference"],
        "settlement_solicited": measurement["settlement_solicited"],
        "note": (
            "L2: the SIM portfolio delivers stochastically LESS than instructed "
            "(rebound/non-response); the company DE-RATES using the ratio learned "
            "from its OWN settlement observables (learning_gain>0 vs the L1 "
            "perfect-delivery belief) and estimates its counterfactual baseline "
            "with a methodology whose error is a clawback exposure it cannot see. "
            "Mean delivery ratio + CM availability venue stay benchmark/level-gated."
        ),
    }


# ===========================================================================
# L3 -- THE STACKING GAP (the third loop for the multi-venue world)
#
# WHY THIS EXISTS. The SIM now runs N concurrent venues against ONE physical
# portfolio, where the same MW cannot be delivered twice. The company, on the
# far side of the wall, cannot see the contention: it sees only its own
# dispatch instructions and settlement lines. A party with no evidence of
# contention books BOTH venues' MW and forecasts revenue it can never
# physically deliver. That OVER-CLAIM is the measurement.
#
# WHY THE GAP IS NOT A TAUTOLOGY (R15 independence). The truth's contention is
# resolved by declared venue PRIORITY against the true portfolio (SIM-internal
# allocation); the company's estimate comes from `learn_contention_rate`, which
# counts how often >= 2 venues appeared in the SAME window on its OWN
# instruction feed. Those are different quantities computed from different
# inputs -- an unobserved contention (a venue that would have called but was
# never instructed because the portfolio was already exhausted) is INVISIBLE to
# the company by construction, so the belief cannot recover the truth exactly.
# If it did, the observables would have leaked the allocation.
#
# THE HEADLINE METRIC IS PHYSICAL MWh, carrying no GBP figure at all, so no
# un-sourced availability price can move the score (the CM clearing price stays
# BENCHMARK REQUIRED). The GBP over-claim is reported alongside, explicitly
# labelled as moving with an un-sourced price.
# ===========================================================================


def measure_l3(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    venues: Optional[Sequence[VenueSpec]] = None,
    portfolio_mw: float = 100.0,
    period_hours: float = DEFAULT_PERIOD_HOURS,
    delivery: Optional[DeliveryModel] = None,
    availability_price_gbp_per_mw_hour: Optional[float] = None,
) -> Dict[str, object]:
    """Run the L3 coupled loop and score the STACKING over-claim.

    Returns, as the headline, `overclaim_mwh_frac` -- how much more physical
    delivery the company expects than the portfolio can actually produce,
    as a fraction of the true delivered MWh. It is:
      * 0.0 when the venues never contend (an uncontended book cannot be
        over-claimed), so the metric is NOT fail-open -- it fires only on its
        own named defect;
      * > 0 for a contention-blind company in a contended book.

    `contention_learning_gain` = overclaim(blind) - overclaim(learned): the
    value the company gets from reading its OWN instruction feed. Positive
    means observable-only learning genuinely narrowed the over-claim.

    An AVAILABILITY venue requires a sourced price (`VenueSpec` enforces this);
    when none is supplied the run is UTILISATION-ONLY, which is the honest
    default rather than a fabricated GBP/kW figure.
    """
    if venues is None:
        venues = _default_venues(
            portfolio_mw=portfolio_mw,
            availability_price_gbp_per_mw_hour=availability_price_gbp_per_mw_hour,
        )

    truth = dispatch_and_settle_stacked(
        out, venues=venues, portfolio_mw=portfolio_mw,
        period_hours=period_hours, delivery=delivery)
    # The stacking law is enforced on every truth; re-assert here so the
    # HARNESS independently confirms it rather than trusting the SIM's word.
    worst_over_allocation_mw = assert_mw_conservation(truth)

    # -- OBSERVABLES: what actually crossed the wall this run. --
    instructions = [
        observe_response_wire(m, expect=FlexDispatchInstruction)
        for m in emit_dispatch_instructions_stacked_over_wire(truth)
    ]
    settlement = observe_settlement_wire(emit_settlement_lines_stacked_over_wire(truth))

    offers = [
        CompanyVenueOffer(
            venue=str(getattr(v.venue, "value", v.venue)),
            offered_mw=v.offered_mw,
            priority=v.priority,
            is_availability=(v.basis is FlexPaymentBasis.AVAILABILITY),
            availability_price_gbp_per_mw_hour=v.availability_price_gbp_per_mw_hour,
            nondelivery_clawback_multiple=v.nondelivery_clawback_multiple,
        )
        for v in truth.venues
    ]

    common = dict(offers=offers, portfolio_mw=portfolio_mw, period_hours=period_hours)

    # -- COMPANY, two readings of the SAME observables. --
    #    (a) contention-BLIND: the cold-start party that assumes no contention.
    blind = form_stacked_belief(truth.outturn_price, contention_awareness=0.0, **common)
    #    (b) LEARNED: infers a contention rate from its own instruction feed.
    learned = form_stacked_belief(
        truth.outturn_price, observed_instructions=instructions,
        observed_settlement_lines=settlement, **common)

    true_mwh = float(np.sum(truth.total_delivered_mwh))
    blind_mwh = float(np.sum(blind.expected_delivered_mwh))
    learned_mwh = float(np.sum(learned.expected_delivered_mwh))

    def _overclaim(expected: float) -> float:
        if true_mwh <= 0.0:
            return 0.0
        return (expected - true_mwh) / true_mwh

    overclaim_blind = _overclaim(blind_mwh)
    overclaim_learned = _overclaim(learned_mwh)

    # Physical contention actually present in this world -- the harness's own
    # reading of the truth, used to tell "no over-claim because the company is
    # good" from "no over-claim because nothing contended".
    binding_frac = float(np.mean(truth.binding_mask)) if truth.binding_mask.size else 0.0

    gap = prediction_gap(truth.total_delivered_mwh, learned.expected_delivered_mwh)
    gap_blind = prediction_gap(truth.total_delivered_mwh, blind.expected_delivered_mwh)

    return {
        "gap": gap.gap,
        "gap_blind_belief": gap_blind.gap,
        "overclaim_mwh_frac": overclaim_learned,
        "overclaim_mwh_frac_blind": overclaim_blind,
        "contention_learning_gain": float(overclaim_blind - overclaim_learned),
        "true_contention_binding_frac": binding_frac,
        "learned_contention_rate": learned.learned_contention_rate,
        "true_delivered_mwh": true_mwh,
        "expected_delivered_mwh": learned_mwh,
        "expected_delivered_mwh_blind": blind_mwh,
        "worst_over_allocation_mw": worst_over_allocation_mw,
        "true_revenue_gbp": float(np.sum(truth.total_revenue_gbp)),
        "expected_revenue_gbp": float(np.sum(learned.expected_revenue_gbp)),
        "n_venues": len(truth.venues),
        "n_periods": int(truth.total_delivered_mwh.size),
        "gap_result": gap,
        "truth": truth,
        "belief": learned,
        "belief_blind": blind,
    }


def _default_venues(
    *, portfolio_mw: float, availability_price_gbp_per_mw_hour: Optional[float] = None,
) -> Sequence[VenueSpec]:
    """A deliberately CONTENDED default book: two venues each offering 60% of
    the portfolio, so the physical ceiling binds whenever both call. An
    uncontended default would make the headline metric vacuously 0."""
    offered = 0.6 * float(portfolio_mw)
    book = [
        VenueSpec(venue=FlexVenue.BALANCING_MECHANISM,
                  basis=FlexPaymentBasis.UTILISATION,
                  offered_mw=offered, priority=1,
                  call_pct=TRUE_SCARCITY_PERCENTILE),
    ]
    if availability_price_gbp_per_mw_hour is not None:
        book.append(VenueSpec(
            venue=FlexVenue.CAPACITY_MARKET,
            basis=FlexPaymentBasis.AVAILABILITY,
            offered_mw=offered, priority=2,
            call_pct=DEFAULT_AVAILABILITY_CALL_PERCENTILE,
            availability_price_gbp_per_mw_hour=availability_price_gbp_per_mw_hour))
    else:
        # No sourced CM price -> a SECOND utilisation venue (a DSO local
        # constraint product) keeps the contention physics real without
        # inventing a GBP/kW figure.
        book.append(VenueSpec(
            venue=FlexVenue.DSO_LOCAL_CONSTRAINT,
            basis=FlexPaymentBasis.UTILISATION,
            offered_mw=offered, priority=2,
            call_pct=DEFAULT_AVAILABILITY_CALL_PERCENTILE))
    return book


def build_gap_summary_l3(measurement: Dict[str, object]) -> Dict[str, object]:
    """Compact, quotable summary of the L3 stacking gap. Like L1/L2 it does NOT
    write the shared coupled_gap_ledger (an un-wired entry reds its consumer's
    tests); the gap is asserted by the triad test meanwhile."""
    return {
        "world_atom": WORLD_ATOM_ID,
        "twin_atom": TWIN_ATOM_ID,
        "level": "L3",
        "metric": "stacking over-claim (physical delivered MWh, no GBP)",
        "gap": measurement["gap"],
        "gap_blind_belief": measurement["gap_blind_belief"],
        "overclaim_mwh_frac": measurement["overclaim_mwh_frac"],
        "overclaim_mwh_frac_blind": measurement["overclaim_mwh_frac_blind"],
        "contention_learning_gain": measurement["contention_learning_gain"],
        "true_contention_binding_frac": measurement["true_contention_binding_frac"],
        "learned_contention_rate": measurement["learned_contention_rate"],
        "true_delivered_mwh": measurement["true_delivered_mwh"],
        "expected_delivered_mwh": measurement["expected_delivered_mwh"],
        "worst_over_allocation_mw": measurement["worst_over_allocation_mw"],
        "note": (
            "L3: N concurrent venues share ONE physical portfolio and the same MW "
            "cannot be delivered twice. The SIM resolves contention by declared "
            "priority (internal); the company sees only its own instruction and "
            "settlement feeds, so an unobserved contention is invisible to it by "
            "construction. A contention-blind party books both venues' MW and "
            "over-claims delivery it cannot physically produce -- the headline is "
            "that over-claim in PHYSICAL MWh, which carries no price, so no "
            "un-sourced GBP/kW figure can move the score. The CM availability "
            "clearing price remains BENCHMARK REQUIRED (NESO / EMR Delivery Body)."
        ),
    }
