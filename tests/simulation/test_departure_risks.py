"""C2 — a departure carries a cause. Controls for `simulation/departure_risks.py`.

Design `docs/design/C2_DEPARTURE_WITH_A_CAUSE_DESIGN.md`; pre-registration
`docs/staging/WORKER_PREREGISTRATION_WHAT_A_DEPARTURE_WITH_A_CAUSE_MUST_SHOW_2026-08-30.md`.

Every test below names the specific defect it exists to catch, and each was checked by making the
code wrong in exactly that way and watching it red -- a control that cannot fail is not a control
(`docs/design/CONTROLS_THAT_CANNOT_FAIL.md`).
"""
import math

import pytest

from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from simulation.departure_level_anchor import YEAR_LEVEL_ANCHOR
from simulation.departure_risks import (
    CAUSE_BILL_SHOCK,
    CAUSE_DISSATISFACTION,
    CAUSE_PRICE_POSITION,
    CAUSE_SVT_INERTIA,
    ORDERED_CAUSES,
    PRICE_IMPORTANCE,
    SERVICE_IMPORTANCE,
    SVT_INERTIA_ANNUAL_LONG_STAYER,
    SVT_INERTIA_ANNUAL_RECENT,
    SVT_LONG_STAYER_YEARS,
    build_departure_risks,
    cause_shares,
    price_move_symmetry,
    resolve_departure,
    survival,
    svt_inertia_base_multiplier,
    svt_inertia_hazard,
    total_departure_probability,
)
from simulation.market_switching_propensity import (
    churn_position_multiplier,
    market_switching_multiplier,
)

SCALE = 0.05  # a fixed non-zero sensitivity, so these controls do not depend on the P0 fit


def _risks(**over):
    kw = dict(
        bill_shock_base=0.06,
        price_response=1.0,
        dissatisfaction_response=1.0,
        sensitivity_scale=SCALE,
        # C1b (2026-08-30). NON-ZERO by default, because the fourth cause defaults to 0.0 in
        # production -- nothing is on SVT yet -- and a helper that inherited that default would
        # hand every test below a hazard of zero for it. `test_action_propensity_damps_every_
        # risk...` iterates ORDERED_CAUSES and would then assert `0.0 < 0.0` and red, which is
        # how it was found; the quieter failure is the other tests passing VACUOUSLY on the new
        # cause forever. A fixture whose default silences the subject is the shape this file
        # exists to refuse.
        svt_inertia=0.05,
    )
    kw.update(over)
    return build_departure_risks(**kw)


def test_survival_is_the_product_of_survivals_and_never_the_composed_scalar():
    """DEFECT: reverting to `p = p_base · Π m_k`, which destroys the cause before the roll.

    The two forms are numerically different and that difference is the whole change:
    `1 − Π(1−p_k) ≠ p_base · Π m_k`. Pinning the product form here means a quiet return to the
    composed scalar cannot pass.
    """
    r = _risks()
    assert survival(r) == pytest.approx(math.prod(1.0 - h for h in r.values()))
    assert total_departure_probability(r) == pytest.approx(1.0 - survival(r))
    # And it is strictly below the sum of the hazards -- the concavity P1 predicts the tail
    # compression from. A form that returned Σh would pass the identity above only if some
    # hazard were zero.
    assert total_departure_probability(r) < sum(r.values())


def test_every_departure_carries_a_cause_and_every_retention_carries_none():
    """DEFECT: a departure emitted with `cause=None`, i.e. the uncaused departure C2 exists to end.

    Swept across the whole roll range rather than at a lucky point, because a cause-walk that
    falls off its last bucket only misfires in the top sliver of the tail.
    """
    r = _risks(price_response=1.4, dissatisfaction_response=1.3)
    p = total_departure_probability(r)
    assert 0.0 < p < 1.0
    seen = set()
    for i in range(20001):
        roll = i / 20000.0
        departed, cause = resolve_departure(r, roll)
        assert departed == (roll > 1.0 - p)
        if departed:
            assert cause in ORDERED_CAUSES, f"uncaused departure at roll={roll}"
            seen.add(cause)
        else:
            assert cause is None
    assert seen == set(ORDERED_CAUSES), "a risk with a live hazard never named a departure"


def test_the_realised_cause_mix_matches_the_hazard_shares():
    """DEFECT: the cause walk drifting from the shares it claims to sample.

    Uses the SEQUENTIAL decomposition as the wrong answer to guard against: allocating
    `h1, (1-h1)h2, ...` is exact in total and therefore passes every aggregate check, while giving
    earlier risks a systematically larger share. On these hazards it misallocates ~2pp.
    """
    r = _risks(price_response=1.6, dissatisfaction_response=1.3)
    shares = cause_shares(r)
    n = 200000
    counts = {c: 0 for c in ORDERED_CAUSES}
    departures = 0
    for i in range(n):
        departed, cause = resolve_departure(r, i / float(n))
        if departed:
            departures += 1
            counts[cause] += 1
    for cause, share in shares.items():
        assert counts[cause] / departures == pytest.approx(share, abs=1e-3)
    # The sequential decomposition really would differ here, so the assertion above has teeth.
    seq = {}
    remaining = 1.0
    for c in ORDERED_CAUSES:
        seq[c] = remaining * r[c]
        remaining *= (1.0 - r[c])
    total_seq = sum(seq.values())
    assert abs(seq[ORDERED_CAUSES[0]] / total_seq - shares[ORDERED_CAUSES[0]]) > 1e-3


def test_cause_shares_do_not_depend_on_the_declared_order():
    """DEFECT: P2's reason mix becoming a function of the order of a tuple literal.

    The order-free property is what lets `ORDERED_CAUSES` stay presentational. If shares were
    computed sequentially this fails, which is exactly the bias the previous test measures.
    """
    r = _risks(price_response=1.6, dissatisfaction_response=1.3)
    forward = cause_shares(r)
    reversed_risks = {c: r[c] for c in reversed(ORDERED_CAUSES)}
    assert cause_shares(reversed_risks) == pytest.approx(forward)


def test_the_price_hazard_identity_is_exact_for_every_household():
    """P4, first leg. DEFECT: losing `m(d)·m(−d) == 1` on the price hazard.

    Without it there is a differential at which the company gains on BOTH legs -- the goal-seeking
    hole R12 exists to close. It is exact below the curve's saturation point; above it the loss leg
    keeps the informed slope while the win leg saturates, and the product rises AGAINST the
    company, which is the safe side and is asserted as such rather than smoothed away.
    """
    for bill in (600.0, 1200.0, 2500.0):
        for d in (0.01, 0.05, 0.10, 0.15):
            dear = _risks(price_response=churn_position_multiplier(d, annual_bill_gbp=bill))
            cheap = _risks(price_response=churn_position_multiplier(-d, annual_bill_gbp=bill))
            parity = _risks(price_response=churn_position_multiplier(0.0, annual_bill_gbp=bill))
            assert dear[CAUSE_PRICE_POSITION] * cheap[CAUSE_PRICE_POSITION] == pytest.approx(
                parity[CAUSE_PRICE_POSITION] ** 2, rel=1e-9
            ), f"price hazard identity lost at bill={bill}, d={d}"


def test_the_total_level_symmetry_breaks_only_against_the_company():
    """P4, second leg, and the prediction was that a naive rewrite BREAKS the equality. It does.

    DEFECT: a ratio BELOW 1, which would let a supplier price up one year and down the next and
    finish with fewer departures than holding parity -- a licence to make over-pricing cheap again.
    The competing-risks form guarantees the opposite bound, `p(d)·p(−d) ≥ p(0)²`, because
    `m + 1/m ≥ 2`. The equality survives only when price is the sole risk, which is asserted too so
    that the inequality is shown to be a consequence of competing risks and not of an arithmetic
    slip.
    """
    for bill in (600.0, 2500.0):
        for d in (0.02, 0.05, 0.10, 0.20, 0.30):
            ratio = price_move_symmetry(
                _risks(price_response=churn_position_multiplier(d, annual_bill_gbp=bill)),
                _risks(price_response=churn_position_multiplier(0.0, annual_bill_gbp=bill)),
                _risks(price_response=churn_position_multiplier(-d, annual_bill_gbp=bill)),
            )
            assert ratio >= 1.0 - 1e-12, (
                f"symmetry ratio {ratio} < 1 at bill={bill}, d={d}: over-pricing has become cheap"
            )

    # With price the ONLY risk the old exact equality returns, which is what identifies the break
    # above as the price of competing risks rather than a defect in the price curve.
    def price_only(d):
        return build_departure_risks(
            bill_shock_base=0.0, price_response=churn_position_multiplier(d, annual_bill_gbp=1200.0),
            dissatisfaction_response=0.0, sensitivity_scale=SCALE,
        )
    assert price_move_symmetry(price_only(0.10), price_only(0.0), price_only(-0.10)) == pytest.approx(1.0)
    # ...and with other risks present it is strictly greater, so the bound is not vacuous.
    assert price_move_symmetry(
        _risks(price_response=churn_position_multiplier(0.10, annual_bill_gbp=1200.0)),
        _risks(price_response=churn_position_multiplier(0.0, annual_bill_gbp=1200.0)),
        _risks(price_response=churn_position_multiplier(-0.10, annual_bill_gbp=1200.0)),
    ) > 1.0


def test_market_opportunity_does_not_suppress_dissatisfaction():
    """DEFECT, and it is the substantive one C2 exists to fix: 2022's 0.444 damping SERVICE churn.

    Under the composed form a household disgusted with its supplier in 2022 was modelled as 56%
    less likely to leave because fixed deals were expensive. Dissatisfaction is a reason to leave
    whatever the market is doing; market opportunity is a precondition on the reasons that involve
    going somewhere. Mutating `build_departure_risks` to scale the dissatisfaction hazard by
    `market_opportunity` reds this.
    """
    crisis = _risks(market_opportunity=0.444, dissatisfaction_response=1.3)
    normal = _risks(market_opportunity=1.0, dissatisfaction_response=1.3)
    assert crisis[CAUSE_DISSATISFACTION] == normal[CAUSE_DISSATISFACTION]
    # The opportunity-seeking risks DO move with it, or the modulator would be wired to nothing.
    assert crisis[CAUSE_BILL_SHOCK] < normal[CAUSE_BILL_SHOCK]
    assert crisis[CAUSE_PRICE_POSITION] < normal[CAUSE_PRICE_POSITION]
    # And the consequence that makes the fix visible: dissatisfaction's SHARE of departures rises
    # in a crisis year, because the ways of leaving that need somewhere to go have thinned out.
    assert cause_shares(crisis)[CAUSE_DISSATISFACTION] > cause_shares(normal)[CAUSE_DISSATISFACTION]


def test_a_retention_offer_cannot_retain_a_service_driven_churner():
    """P6. DEFECT: a discount scaling the whole departure probability, as `retention_modifier` did.

    A price cut is a price cut. Nothing about it addresses dissatisfaction, and the actionable
    consequence -- that the answer to a service-driven churner is a service intervention -- exists
    only if the offer is wired to the price risk alone.
    """
    offered = _risks(retention_offer_retained_fraction=0.5, dissatisfaction_response=1.3)
    not_offered = _risks(retention_offer_retained_fraction=1.0, dissatisfaction_response=1.3)
    assert offered[CAUSE_PRICE_POSITION] == pytest.approx(0.5 * not_offered[CAUSE_PRICE_POSITION])
    assert offered[CAUSE_DISSATISFACTION] == not_offered[CAUSE_DISSATISFACTION]
    assert offered[CAUSE_BILL_SHOCK] == not_offered[CAUSE_BILL_SHOCK]
    # So a household whose risk is overwhelmingly service-driven is barely helped by a discount.
    service_led = dict(bill_shock_base=0.001, dissatisfaction_response=1.3, price_response=1.0)
    with_offer = total_departure_probability(
        _risks(retention_offer_retained_fraction=0.0, **service_led))
    without = total_departure_probability(_risks(**service_led))
    assert with_offer / without > 0.5, (
        "a total-probability discount still retains service churners -- P6 is not wired"
    )


def test_action_propensity_damps_every_risk_because_it_is_not_a_reason_anyone_left():
    """DEFECT: modelling income stress or tenure as a RISK.

    `stress_switching_multiplier` runs 1.10 / 0.85 / 0.65 and tenure 1.00 / 0.80 / 0.75, so both
    can make a household leave LESS. A competing-risks model has no negative hazards, and "I was
    too financially stressed to switch" is not a reason anyone left -- it is the same shape as
    "there was nowhere to go". This pins them as one modulator over ALL risks; wiring either as a
    risk, or scoping the modulator to a subset, reds it.
    """
    damped = _risks(action_propensity=0.65 * 0.75, dissatisfaction_response=1.3)
    neutral = _risks(action_propensity=1.0, dissatisfaction_response=1.3)
    for cause in ORDERED_CAUSES:
        assert damped[cause] < neutral[cause], f"{cause} not damped by action propensity"
    # Damping everything leaves the MIX ~untouched, which is what makes it a modulator rather than
    # a cause -- but NOT exactly, and the residual is recorded here rather than asserted away.
    # A uniform multiplier on PROBABILITIES is not a uniform multiplier on hazard RATES, because
    # `λ = -log(1-h)` is convex: damping by 0.49 moves the largest hazard's share by 0.26pp. It is
    # second-order (λ ≈ h for small h) and it is the price of keeping the world's existing
    # multipliers, which are calibrated in probability space and which P0 needs unchanged. The
    # bound is asserted so the drift cannot grow unnoticed into something P2 would read as a
    # finding about the world.
    drift = max(
        abs(cause_shares(damped)[c] - cause_shares(neutral)[c]) for c in ORDERED_CAUSES
    )
    assert drift < 0.005, f"modulator moved the reason mix by {drift:.4f} -- more than second order"
    # And the assertion has teeth: a propensity wrongly scoped to a SUBSET of the risks moves the
    # mix by an order of magnitude more, which is the defect this bound is here to catch.
    mis_scoped = build_departure_risks(
        bill_shock_base=0.06 * 0.65 * 0.75, price_response=1.0,
        dissatisfaction_response=1.3, sensitivity_scale=SCALE,
        # C1b: the mis-scoping under test damps the SHOCK term only, so the SVT hazard is passed
        # UNDAMPED here on purpose -- that is what "scoped to a subset" means for four causes.
        # It must still be non-zero: `cause_shares` omits a zero hazard entirely, and the drift
        # comparison below iterates ORDERED_CAUSES, so a zero would KeyError rather than measure.
        svt_inertia=0.05,
    )
    subset_drift = max(
        abs(cause_shares(mis_scoped)[c] - cause_shares(neutral)[c]) for c in ORDERED_CAUSES
    )
    assert subset_drift > 10 * drift


def test_hazards_are_functions_of_state_so_the_reason_mix_is_not_the_input_weights():
    """DESIGN §3, and the single most important control here.

    DEFECT: per-cause hazards that are CONSTANTS. Constant hazards reproduce the published
    importance weights as the output reason mix exactly -- which would satisfy pre-registration P2
    by construction, look like a finding, and measure nothing. That is goal-seeking with an extra
    step.

    The guard is that the mix must MOVE with household state. If someone replaces the response
    curves with constants the second assertion collapses to the first and this reds.
    """
    # At a perfectly neutral household the price:service hazard ratio IS the published ratio --
    # that is the sensitivities doing their job, and it is the tautology to be escaped, not a bug.
    neutral = _risks(price_response=1.0, dissatisfaction_response=1.0, bill_shock_base=0.0)
    s = cause_shares(neutral)
    assert s[CAUSE_PRICE_POSITION] / s[CAUSE_DISSATISFACTION] == pytest.approx(
        PRICE_IMPORTANCE / SERVICE_IMPORTANCE, rel=0.02
    )
    # A real household is not neutral, and its mix must differ. A supplier 20% dearer to a
    # high-bill household that is also content: price dominates far beyond its 0.40 weight.
    dear = _risks(
        price_response=churn_position_multiplier(0.20, annual_bill_gbp=2500.0),
        dissatisfaction_response=0.85, bill_shock_base=0.0,
    )
    d = cause_shares(dear)
    assert d[CAUSE_PRICE_POSITION] / d[CAUSE_DISSATISFACTION] > 3.0 * (
        PRICE_IMPORTANCE / SERVICE_IMPORTANCE
    ), "the reason mix did not move with household state -- hazards have become constants"
    # And the other way: a cheap supplier failing a household on service.
    poor = _risks(
        price_response=churn_position_multiplier(-0.15, annual_bill_gbp=2500.0),
        dissatisfaction_response=1.3, bill_shock_base=0.0,
    )
    p = cause_shares(poor)
    assert p[CAUSE_DISSATISFACTION] > p[CAUSE_PRICE_POSITION], (
        "service never outranks price for any household state -- the mix cannot be a measurement"
    )


def test_a_hazard_at_the_world_ceiling_stays_finite_and_does_not_take_the_whole_mix():
    """DEFECT, FAIL-SILENT: a hazard reaching exactly 1.0 makes `-log(1-h)` infinite, which hands
    that risk 100% of every departure share with no error raised and no NaN to notice.

    The clip is at the world's own churn ceiling, so this is also the check that the ceiling is
    still doing something.
    """
    r = _risks(bill_shock_base=5.0, price_response=1000.0, dissatisfaction_response=1000.0)
    for cause, h in r.items():
        assert 0.0 <= h <= WORLD_MAX_CHURN_PROBABILITY, f"{cause} escaped the ceiling at {h}"
    shares = cause_shares(r)
    assert all(math.isfinite(v) for v in shares.values())
    assert sum(shares.values()) == pytest.approx(1.0)
    assert max(shares.values()) < 1.0


def test_a_household_with_no_hazard_at_all_never_departs_and_is_not_given_a_cause():
    """DEFECT, FAIL-OPEN: fabricating a uniform cause split when there is no hazard to split.

    `cause_shares` returns empty rather than an invented uniform mapping, and `resolve_departure`
    cannot depart. A `1/n` fallback here would put causes into the mix for households that could
    not have left.
    """
    r = _risks(bill_shock_base=0.0, price_response=0.0, dissatisfaction_response=0.0,
               # C1b: and the fourth. "No hazard at all" has to mean all four, or this test
               # measures a household that could still drift off SVT.
               svt_inertia=0.0)
    assert total_departure_probability(r) == 0.0
    assert cause_shares(r) == {}
    for roll in (0.0, 0.5, 0.999999):
        assert resolve_departure(r, roll) == (False, None)


# ── C1b: THE DRIFT OFF A STANDARD VARIABLE TARIFF ───────────────────────────────────────────
# A fourth REASON, not a fourth modulator. Two thirds of a real domestic book sits on SVT and
# leaves it without any renewal to leave AT, so this is the largest single departure route the
# world has been unable to express.

def test_the_annual_anchor_recomposes_from_the_segment_hazard():
    """DEFECT: using the ANNUAL rate as a per-segment rate.

    The anchor is annual; the world's SVT segments are cap periods. Charging each quarter the
    annual figure gives `1-(1-0.20)**4 = 0.5904` a year against 0.20 -- nearly three times the
    published band, and in the one direction no evidence supports. The conversion is
    constant-hazard so that four real cap quarters return the annual number.
    """
    year = [90, 91, 92, 92]
    for annual, years_on in ((SVT_INERTIA_ANNUAL_RECENT, 0.0),
                             (SVT_INERTIA_ANNUAL_LONG_STAYER, SVT_LONG_STAYER_YEARS)):
        survival_ = 1.0
        for days in year:
            survival_ *= 1.0 - svt_inertia_hazard(years_on_svt=years_on, segment_days=days,
            market_switching_multiplier=svt_inertia_base_multiplier())
        assert abs((1.0 - survival_) - annual) < 5e-4, (
            f"four cap quarters recompose to {1 - survival_:.5f}, not the published {annual}")
        # And the naive substitution is the large, obvious error this guards.
        naive = 1.0 - (1.0 - annual) ** 4
        assert naive > 2.5 * annual


def test_a_partial_opening_segment_is_charged_for_its_own_length():
    """DEFECT: a flat per-quarter rate. A household arriving mid-quarter gets a 47-day segment;
    charging it a full quarter's hazard over-bills the one segment every SVT account has."""
    short = svt_inertia_hazard(years_on_svt=0.0, segment_days=47,
            market_switching_multiplier=svt_inertia_base_multiplier())
    full = svt_inertia_hazard(years_on_svt=0.0, segment_days=92,
            market_switching_multiplier=svt_inertia_base_multiplier())
    assert short < full
    assert abs(short / full - 47 / 92) < 0.02, "not proportional to elapsed time at these rates"


def test_a_long_stayer_drifts_less_than_a_recent_arrival():
    """The published split (5-10% at 3+ years, 15-20% under 3) is the one piece of genuine
    per-household structure this anchor carries. Collapsing it to one rate loses it."""
    recent = svt_inertia_hazard(years_on_svt=1.0, segment_days=91,
            market_switching_multiplier=svt_inertia_base_multiplier())
    settled = svt_inertia_hazard(years_on_svt=SVT_LONG_STAYER_YEARS, segment_days=91,
            market_switching_multiplier=svt_inertia_base_multiplier())
    assert settled < recent
    assert svt_inertia_hazard(years_on_svt=SVT_LONG_STAYER_YEARS - 0.01, segment_days=91,
            market_switching_multiplier=svt_inertia_base_multiplier()) == recent


def test_an_account_not_on_svt_carries_no_inertia_hazard():
    """FAIL-CLOSED. A fixed-term account has no cap period elapsed under a variable tariff, so it
    signals that with `segment_days <= 0` and must get exactly zero -- never a small default that
    would put an SVT cause on a household that has never been on SVT."""
    for days in (0, -1, -91):
        assert svt_inertia_hazard(years_on_svt=0.0, segment_days=days,
            market_switching_multiplier=svt_inertia_base_multiplier()) == 0.0


def test_the_market_term_reaches_the_hazard_and_is_not_merely_in_the_signature():
    """DEFECT: a parameter accepted and then ignored.

    This is the failure mode the repair was most exposed to, because the refusal that demanded it
    (`tools/fit_year_level_anchor.svt_market_invariance_refusal`) inspects the SIGNATURE. A term
    added to the signature and dropped in the body would lift that refusal, emit the whole-book
    anchor, and leave the route carrying 61% of departures exactly as market-blind as before --
    with the one control that named the defect now reporting green.

    So this drives the two years the record separates most and reads the ANSWER. The published GB
    domestic switching rate is 23.00% in 2020 and 4.30% in 2022, a 5.3x swing; the hazard must
    carry it.
    """
    peak = svt_inertia_hazard(years_on_svt=0.0, segment_days=91,
                              market_switching_multiplier=market_switching_multiplier(2020))
    trough = svt_inertia_hazard(years_on_svt=0.0, segment_days=91,
                                market_switching_multiplier=market_switching_multiplier(2022))
    assert trough < peak, "the market term does not reach the hazard at all"
    assert peak / trough > 4.0, (
        f"2020 drift is only {peak / trough:.2f}x 2022's, against a published switching record "
        f"that moves 5.3x between those years -- the term is reaching the hazard damped or "
        f"partially applied"
    )


def test_the_published_rate_is_unchanged_inside_its_own_inference_window():
    """DEFECT, and it is the one a filed repair got wrong: `rate x multiplier(year)` at 2024-ref.

    `SVT_INERTIA_ANNUAL_RECENT = 0.20` is an ABSOLUTE annual rate and
    `svt_rates_active_passive_2016_2025.md` §4 infers it against a 2019-20 market.
    `market_switching_multiplier` is normalised at 2024. Multiplying the two directly levels a
    2019-20 rate UP into the market it was already measured in, by a constant 1.375776 in every
    year -- the year cancels, so no year-shaped check can see it, and at 2024 the naive form looks
    like it did nothing at all because `multiplier(2024) = 1.0` by definition.

    The re-referencing is what makes the composition a re-levelling rather than a new constant, and
    this is the leg that states it: across the window the constants were inferred in, the world
    still runs the published number.
    """
    year = (90, 91, 92, 92)
    for annual, years_on in ((SVT_INERTIA_ANNUAL_RECENT, 0.0),
                             (SVT_INERTIA_ANNUAL_LONG_STAYER, SVT_LONG_STAYER_YEARS)):
        for y in (2019, 2020):
            survival_ = 1.0
            for days in year:
                survival_ *= 1.0 - svt_inertia_hazard(
                    years_on_svt=years_on, segment_days=days,
                    market_switching_multiplier=market_switching_multiplier(y))
            realised = 1.0 - survival_
            # The window is a two-year MEAN, so neither endpoint sits exactly on the published
            # rate -- 2019 below it and 2020 above, by the record's own spread between them. The
            # naive 2024-referenced form misses by 37.6%, an order of magnitude outside this.
            assert abs(realised - annual) / annual < 0.06, (
                f"a year of SVT drift at {y} recomposes to {100 * realised:.2f}% against the "
                f"published {100 * annual:.0f}% -- the rate has been re-levelled inside the very "
                f"window it was inferred in"
            )
    # And the mean across the window IS the published rate, which is the property `factor()` has
    # by construction and the reason a reader can still check the level.
    mean_factor = sum(market_switching_multiplier(y) for y in (2019, 2020)) / 2.0
    assert abs(mean_factor / svt_inertia_base_multiplier() - 1.0) < 1e-12


def test_the_market_term_is_required_so_a_caller_cannot_quietly_run_market_blind():
    """FAIL-CLOSED, and a default of 1.0 is the specific thing being refused here.

    With a default the signature would advertise a market the hazard could see while every
    existing caller kept running market-blind, and the structural refusal keyed to that signature
    would have lifted on a term reaching nothing. This module already fails closed the same way
    for `_SENSITIVITY_SCALE`.
    """
    import inspect

    param = inspect.signature(svt_inertia_hazard).parameters["market_switching_multiplier"]
    assert param.default is inspect.Parameter.empty, (
        "the market term has acquired a default, so a caller can run the market-blind hazard "
        "while the signature says otherwise"
    )
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    with pytest.raises(TypeError):
        svt_inertia_hazard(years_on_svt=0.0, segment_days=91)


def test_nothing_is_on_svt_yet_so_the_fourth_cause_moves_no_published_figure():
    """THE INTERLOCK, and the reason this can land before the assignment does.

    `build_departure_risks` defaults `svt_inertia` to 0.0, so every renewal in the world today
    gets a hazard of exactly zero for this cause and the composed probability is unchanged to the
    last bit. The mechanism exists; nothing is assigned to it. When C1b's assignment lands, THAT
    is the commit where the churn series moves, and it moves for one reason.

    THE TITLE IS NOW HISTORY AND THE ASSERTIONS ARE NOT, corrected 2026-08-31 rather than
    renamed. C1b's assignment HAS landed: `run_phase2b` rolls an SVT segment decision and passes
    `svt_inertia=` explicitly. So "nothing is on SVT yet" is false about the world. What this
    still checks is true and worth checking -- the DEFAULT is 0.0, so the renewal roll, which
    passes no `svt_inertia`, is unchanged to the last bit by the cause's existence. That is the
    interlock; the name is the state it was written in.
    """
    without = build_departure_risks(
        bill_shock_base=0.06, price_response=1.0, dissatisfaction_response=1.0,
        sensitivity_scale=SCALE)
    assert without["svt_inertia"] == 0.0
    explicit_zero = build_departure_risks(
        bill_shock_base=0.06, price_response=1.0, dissatisfaction_response=1.0,
        sensitivity_scale=SCALE, svt_inertia=0.0)
    assert without == explicit_zero
    assert total_departure_probability(without) == total_departure_probability(explicit_zero)


def test_the_level_anchor_scales_the_response_risks_and_never_the_svt_route():
    """DEFECT, and it was LIVE at HEAD when this was written: `level_anchor * svt_inertia`.

    `svt_inertia` arrives already carrying units -- `svt_inertia_hazard` converts the published
    ANNUAL rate (0.20 recent stayer, 0.10 long stayer) into this segment's length, and
    `test_the_annual_anchor_recomposes_from_the_segment_hazard` above is what pins that. The three
    response risks are the opposite: dimensionless curves, ~1.0 at a neutral household, carrying
    no rate at all, which is the entire reason `simulation/departure_level_anchor.py` had to
    exist. Anchoring the one that already has a level destroys the only level anyone could check.

    HOW IT GOT LIVE, because "unreachable" was true when it was written and stopped being true
    without anything noticing. The finding that named this line
    (`WORKER_FINDING_THE_WORLD_AND_THE_COMPOSED_FORM_DISAGREE_ABOUT_WHETHER_THE_LEVEL_ANCHOR_
    REACHES_THE_SVT_ROUTE_2026-08-31.md`) filed it LATENT on the ground that `svt_inertia`
    defaults to 0.0 and no production caller passed it. It then predicted, in its own words, that
    *"the first commit to wire the SVT roll through `build_departure_risks` would silently triple
    the world's SVT departure rate"*. That commit landed -- `run_phase2b` passes
    `svt_inertia=_svt_hazard` AND `level_anchor=year_level_anchor(...)` in the same call -- and
    nothing went red, because the only thing guarding the composition was a refusal inside
    `tools/fit_year_level_anchor.py` that fires at FIT time, on a capture, after the run. A
    severity keyed to "no caller passes it" expires the moment a caller does, and there was no
    control keyed to the property. This is that control.

    LEG (b) IS NOT DECORATION -- IT IS WHAT STOPS THIS BEING FAIL-OPEN. Leg (a) alone passes on
    code where `level_anchor` reaches NOTHING: delete it from all four lines and the SVT hazard is
    still invariant to it. Asserting the response risks DO move with it is what makes (a) mean
    "exempt" rather than "absent". Both legs come from the same call.

    MUTATION: put `level_anchor *` back on the `CAUSE_SVT_INERTIA` line -> (a) fires with the
    magnitude in the message. Remove it from the three response lines -> (b) fires.
    """
    anchors = sorted(YEAR_LEVEL_ANCHOR.values())
    lo, hi = anchors[0], anchors[-1]
    assert hi > 1.05, (
        f"every committed level anchor is now ~1.0 (max {hi:.4f}), so multiplying the SVT route "
        f"by one would be undetectable and this control has gone VACUOUS. That is a finding about "
        f"the anchor, not a reason to delete this -- an exemption nobody can measure is not an "
        f"exemption. Re-key it to a declared probe value and say so here."
    )

    at_lo = _risks(level_anchor=lo, svt_inertia=0.05)
    at_hi = _risks(level_anchor=hi, svt_inertia=0.05)

    # (a) THE SVT ROUTE IS EXEMPT. Exact equality: this is one term present or absent, not a
    #     tolerance question, and a tolerance here would swallow a small anchor.
    assert at_lo[CAUSE_SVT_INERTIA] == at_hi[CAUSE_SVT_INERTIA], (
        f"the SVT hazard moved from {at_lo[CAUSE_SVT_INERTIA]:.6f} to "
        f"{at_hi[CAUSE_SVT_INERTIA]:.6f} across the committed anchor range {lo:.4f}-{hi:.4f}, so "
        f"the year level anchor is reaching a hazard that already carries a published absolute "
        f"rate. At the top of that range the published 10-20%/yr band arrives at the roll as "
        f"{100 * SVT_INERTIA_ANNUAL_LONG_STAYER * hi:.0f}-{100 * SVT_INERTIA_ANNUAL_RECENT * hi:.0f}%/yr. "
        f"The repair is to drop `level_anchor *` from that line, NEVER to widen the published band "
        f"and never to re-fit the anchor around it."
    )

    # (b) THE RESPONSE RISKS ARE NOT EXEMPT, or (a) is passing on a dead argument.
    for cause in (CAUSE_BILL_SHOCK, CAUSE_PRICE_POSITION, CAUSE_DISSATISFACTION):
        assert at_hi[cause] > at_lo[cause], (
            f"{cause} did not move when the level anchor went {lo:.4f} -> {hi:.4f}. The anchor is "
            f"what gives the dimensionless response curves their units; if it reaches none of "
            f"them then leg (a) above is vacuous and the world has no level at all."
        )

    # (c) AT REAL INPUTS, WHICH IS THE LEG THAT STATES THE SIZE. Four real cap quarters under the
    #     largest committed anchor must still recompose to the published annual rate. This is the
    #     same recomposition `test_the_annual_anchor_recomposes_from_the_segment_hazard` pins at
    #     an anchor of 1.0, run at the anchor the world actually uses -- because that test cannot
    #     see `build_departure_risks` and so could not have caught this.
    for annual, years_on in ((SVT_INERTIA_ANNUAL_RECENT, 0.0),
                             (SVT_INERTIA_ANNUAL_LONG_STAYER, SVT_LONG_STAYER_YEARS)):
        survival_ = 1.0
        for days in (90, 91, 92, 92):
            hazard = svt_inertia_hazard(years_on_svt=years_on, segment_days=days,
            market_switching_multiplier=svt_inertia_base_multiplier())
            survival_ *= 1.0 - _risks(
                level_anchor=hi, svt_inertia=hazard, action_propensity=1.0
            )[CAUSE_SVT_INERTIA]
        assert abs((1.0 - survival_) - annual) < 5e-4, (
            f"composed through `build_departure_risks` at the world's largest committed anchor "
            f"({hi:.4f}), a year of SVT drift recomposes to {100 * (1 - survival_):.1f}% against "
            f"the published {100 * annual:.0f}%. The anchor is being applied to a rate that was "
            f"already published as a rate."
        )


def test_a_year_inside_the_published_record_with_no_fitted_anchor_refuses_instead_of_falling_back():
    """THE DEFECT: the fallback's CONDITION was the fitted table; its JUSTIFICATION is the record.

    `year_level_anchor` read `YEAR_LEVEL_ANCHOR.get(year, YEAR_LEVEL_ANCHOR[REFERENCE])`, so the
    branch fired on absence from the FITTED TABLE. The docstring above it justifies the fallback
    by absence from the RECORD -- a synthetic future, where `market_switching_multiplier` already
    carries the level movement. Two different sets. They coincide exactly today (both 2016-2025),
    which is the only reason this survived: a control keyed to today's answer would read green.

    IT IS NOT HYPOTHETICAL. `9a03f3b44` measured `year_level_anchor(2022)` at 3.053619 in a run
    whose block was missing 2022 -- inside the record -- against 1.524110 committed. 1.98x, silent,
    on the one year the published record is loudest about, and in the direction that ADDS
    departures against a 4.30% record. Nothing observed it: not the run, not the fit, not two
    preregistrations written over the top of it.

    THIS CONTROL IS UNREACHABLE AT HEAD BY CONSTRUCTION and that is the point -- all ten record
    years are fitted, so the world never hits it. An unreachable guard that is never driven is
    this repository's most catalogued shape, so leg (c) DRIVES it by removing a year, and leg (a)
    states the size the old code would have returned instead. Keyed to the property (record
    membership), not to the current ten keys: adding 2026 to the record and not to the fit must
    turn this red, and re-fitting must turn it green.
    """
    from simulation.departure_level_anchor import (
        FIT_COMPARISON_WINDOW,
        NO_LEVEL_CORRECTION,
        anchor_coverage,
        year_level_anchor,
    )
    from simulation.market_switching_propensity import (
        MULTIPLIER_REFERENCE_YEAR,
        _published_departure_rates,
    )
    from simulation.renewal_engagement import CRISIS_PASSIVE_YEARS

    record = _published_departure_rates()

    # (a) THE PREMISE, MEASURED RATHER THAN ASSERTED. The reference year's anchor is not a
    #     conservative stand-in for a record year: it has no direction at all.
    ref = YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR]
    ratios = {y: ref / YEAR_LEVEL_ANCHOR[y] for y in record if y in YEAR_LEVEL_ANCHOR}
    assert min(ratios.values()) < 1.0 < max(ratios.values()), (
        "the reference year's anchor is on one side of every fitted year's, so the old docstring's "
        "'fails toward the record' claim would be defensible and this control is arguing with "
        f"something that is not there. ratios: {ratios}"
    )

    # (b) THE PARTITION, WHICH REPLACED "EVERY RECORD YEAR IS FITTED" ON 2026-09-02. That older
    #     leg was true of the ten-year block and the whole-book re-fit abandons it ON PURPOSE:
    #     seven years are identified and three are not. Keyed to the property -- every record year
    #     is in EXACTLY ONE side, and a year in neither has left the subject silently, which is how
    #     an emptied subject reaches a constant PASS. Nothing here raises on an ordinary run.
    fitted, unfitted = anchor_coverage()
    assert not (set(fitted) & set(unfitted)), (
        f"{sorted(set(fitted) & set(unfitted))} are BOTH fitted and declared-unfitted; the two "
        f"returns are a partition and a year in both makes the coverage unreadable either way"
    )
    for y in sorted(record):
        assert y in fitted or y in unfitted, (
            f"{y} is inside the published record and is in neither the fits nor the declared "
            f"absences -- it left the subject SILENTLY, which is the defect this control is for"
        )
        assert year_level_anchor(y) == (fitted[y] if y in fitted else unfitted[y][0]), (
            f"{y}: the accessor and the coverage report disagree, so a consumer asking which "
            f"years are fits gets an answer about a different table than the one the world runs"
        )
    assert year_level_anchor(max(record) + 5) == ref

    # (c) THE MUTATION, DRIVEN RATHER THAN DESCRIBED. Remove one FITTED record year from the fit
    #     and the accessor must refuse, naming the year and the record. Before this guard it
    #     returned `ref` -- a number, silently, that no caller could tell from a fitted one.
    victim = min(fitted, key=lambda y: YEAR_LEVEL_ANCHOR[y])
    saved = YEAR_LEVEL_ANCHOR.pop(victim)
    try:
        assert ref / saved > 1.5, (
            f"{victim} was chosen as the year the fallback distorts most and it only moves "
            f"{ref / saved:.3f}x -- restate this leg rather than letting it pass on a small move."
        )
        with pytest.raises(ValueError, match=f"{victim}"):
            year_level_anchor(victim)
        with pytest.raises(ValueError, match="INSIDE the published"):
            year_level_anchor(victim)
        # ...and the outside-record path is NOT collateral damage of the guard.
        assert year_level_anchor(max(record) + 5) == ref
    finally:
        YEAR_LEVEL_ANCHOR[victim] = saved

    assert year_level_anchor(victim) == saved, "the fixture leaked; every later test is now suspect"

    # (d) THE CORROBORATION, AND IT IS THE LEG THAT MATTERS. Leg (c) proves an UNDECLARED gap
    #     refuses. But the escape from that refusal is a declared cause, and a producer that can
    #     retire any inconvenient year by NAMING it refused has lifted its own guard -- the
    #     catalogued *refusal names a cause the checker never observed*. So a declaration is only
    #     honoured where something OTHER than `UNFITTED_YEARS` says the year cannot be fitted:
    #     either it is outside the window the fit is scoped to, or it is a crisis-forced-passive
    #     year whose renewal rolls C1b routes to the SVT table. Both corroborators live outside
    #     this module and neither is editable from the block.
    #
    #     MUTATION: declare a fitted, in-window, non-crisis year (2020) unfitted and this fires by
    #     name, even though leg (c) goes quiet because the declaration suppresses the raise. That
    #     is exactly the hole (c) alone leaves. Mutation-proven with `python3 -B`.
    for y, (_value, cause) in sorted(unfitted.items()):
        assert str(y) in cause, (
            f"{y}'s declared cause does not name the year it is about: {cause!r}. A refusal a "
            f"reader cannot attribute to a year is not on the surface in any useful sense."
        )
        assert y not in FIT_COMPARISON_WINDOW or str(y) in CRISIS_PASSIVE_YEARS, (
            f"{y} is declared unfitted, but it is INSIDE the fit's comparison window "
            f"({FIT_COMPARISON_WINDOW.start}-{FIT_COMPARISON_WINDOW.stop - 1}) and is not a "
            f"crisis-forced-passive year, so nothing outside `UNFITTED_YEARS` corroborates the "
            f"claim that it cannot be fitted. Declared cause: {cause!r}. A year the fit CLAIMED "
            f"and could simply not be bothered with is a dropped year wearing a refusal's clothes."
        )

    # ...and the two fallback cases are DIFFERENT values, not one shrug wearing two labels.
    in_window = {y for y in unfitted if y in FIT_COMPARISON_WINDOW}
    if in_window and set(unfitted) - in_window:
        assert {unfitted[y][0] for y in in_window} == {NO_LEVEL_CORRECTION}, (
            "a year the fit claimed and could not identify must apply NO level correction, not a "
            "calibration borrowed from the reference year's population -- leg (a) above is the "
            "measurement that the borrow has no direction"
        )
        assert {unfitted[y][0] for y in set(unfitted) - in_window} == {ref}, (
            "a year outside the fit's window takes the reference year's anchor, on the same "
            "argument that covers a synthetic future"
        )
