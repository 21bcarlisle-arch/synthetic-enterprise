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
from simulation.departure_risks import (
    CAUSE_BILL_SHOCK,
    CAUSE_DISSATISFACTION,
    CAUSE_PRICE_POSITION,
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
    svt_inertia_hazard,
    total_departure_probability,
)
from simulation.market_switching_propensity import churn_position_multiplier

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
            survival_ *= 1.0 - svt_inertia_hazard(years_on_svt=years_on, segment_days=days)
        assert abs((1.0 - survival_) - annual) < 5e-4, (
            f"four cap quarters recompose to {1 - survival_:.5f}, not the published {annual}")
        # And the naive substitution is the large, obvious error this guards.
        naive = 1.0 - (1.0 - annual) ** 4
        assert naive > 2.5 * annual


def test_a_partial_opening_segment_is_charged_for_its_own_length():
    """DEFECT: a flat per-quarter rate. A household arriving mid-quarter gets a 47-day segment;
    charging it a full quarter's hazard over-bills the one segment every SVT account has."""
    short = svt_inertia_hazard(years_on_svt=0.0, segment_days=47)
    full = svt_inertia_hazard(years_on_svt=0.0, segment_days=92)
    assert short < full
    assert abs(short / full - 47 / 92) < 0.02, "not proportional to elapsed time at these rates"


def test_a_long_stayer_drifts_less_than_a_recent_arrival():
    """The published split (5-10% at 3+ years, 15-20% under 3) is the one piece of genuine
    per-household structure this anchor carries. Collapsing it to one rate loses it."""
    recent = svt_inertia_hazard(years_on_svt=1.0, segment_days=91)
    settled = svt_inertia_hazard(years_on_svt=SVT_LONG_STAYER_YEARS, segment_days=91)
    assert settled < recent
    assert svt_inertia_hazard(years_on_svt=SVT_LONG_STAYER_YEARS - 0.01, segment_days=91) == recent


def test_an_account_not_on_svt_carries_no_inertia_hazard():
    """FAIL-CLOSED. A fixed-term account has no cap period elapsed under a variable tariff, so it
    signals that with `segment_days <= 0` and must get exactly zero -- never a small default that
    would put an SVT cause on a household that has never been on SVT."""
    for days in (0, -1, -91):
        assert svt_inertia_hazard(years_on_svt=0.0, segment_days=days) == 0.0


def test_nothing_is_on_svt_yet_so_the_fourth_cause_moves_no_published_figure():
    """THE INTERLOCK, and the reason this can land before the assignment does.

    `build_departure_risks` defaults `svt_inertia` to 0.0, so every renewal in the world today
    gets a hazard of exactly zero for this cause and the composed probability is unchanged to the
    last bit. The mechanism exists; nothing is assigned to it. When C1b's assignment lands, THAT
    is the commit where the churn series moves, and it moves for one reason.
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


# ── The SVT floor's base year ───────────────────────────────────────────────────────────────────
# `SVT_INERTIA_ANNUAL_*` are ABSOLUTE annual rates inferred against a 2019-20 market;
# `market_switching_multiplier` is a RATIO normalised to 2024. The repair filed at `18a09617d`
# composes them directly, which levels a 2019-20 rate up into the market it was already measured
# in. Finding: docs/staging/WORKER_FINDING_THE_SVT_FLOORS_FILED_REPAIR_APPLIES_A_2024_REFERENCED_RATIO_TO_A_2019_20_RATE_2026-08-31.md

#: The window §4 states its basis over, on the all-customer row the segment rows must average to.
SVT_INERTIA_BASE_YEARS = (2019, 2020)

#: What the comment on the constants tells the next implementer to divide by. Written down HERE so
#: the leg below can catch it rotting; derived from the record, never chosen.
STATED_BASE_MULTIPLIER = 1.3758


def _base_multiplier() -> float:
    """The record's own 2019-20 level over its 2024 level -- derived, not written down."""
    from simulation.market_switching_propensity import (
        MULTIPLIER_REFERENCE_YEAR,
        market_departure_rate,
    )
    base = sum(market_departure_rate(y) for y in SVT_INERTIA_BASE_YEARS) / len(SVT_INERTIA_BASE_YEARS)
    return base / market_departure_rate(MULTIPLIER_REFERENCE_YEAR)


def test_the_svt_floors_base_year_is_not_the_multipliers_reference_year():
    """DEFECT: composing an absolute 2019-20 rate with a ratio normalised to 2024.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. This does not assert the record's current
    values. It asserts the two base years are far enough apart that `floor * multiplier(year)` is
    materially wrong -- which is the condition that makes the warning on the constants worth
    carrying. If the record is ever refined so that 2019-20 and 2024 coincide, this goes RED and
    the correct response is to DELETE the warning, not to widen the bound: the naive form would
    have become right.

    The error is a CONSTANT factor -- the year cancels -- so no year-shaped check can see it, and
    it is exactly zero at 2024 where `multiplier` is 1.00 by definition. That is why it needs its
    own leg rather than falling out of some other test.
    """
    factor = _base_multiplier()
    # 1pp of the reference level is the smallest difference the published bands bear; anything
    # inside that is rounding and the two base years would be interchangeable.
    assert abs(factor - 1.0) > 0.01, (
        f"2019-20 and 2024 now sit within rounding of each other (factor {factor:.4f}). The base-"
        f"year warning on SVT_INERTIA_ANNUAL_* is no longer warranted -- delete it."
    )


def test_the_base_year_factor_on_the_constants_still_matches_the_record():
    """DEFECT: the correction factor in the comment rots when the record is refined.

    The constants carry a written instruction -- divide by 1.3758 -- and a written number in a
    comment is exactly the shape this project has paid for: it stays green while the record moves
    under it. Derived here from `market_departure_rate` so the comment cannot outlive its evidence.
    """
    assert round(_base_multiplier(), 4) == STATED_BASE_MULTIPLIER, (
        f"the record now gives {_base_multiplier():.4f}; the comment on SVT_INERTIA_ANNUAL_* and "
        f"STATED_BASE_MULTIPLIER above both say {STATED_BASE_MULTIPLIER} and must be corrected together."
    )
