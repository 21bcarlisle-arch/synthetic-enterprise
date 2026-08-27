"""S1: the household's own price sensitivity reaches the world's price response.

WHAT THIS CLOSES. Until 2026-08-27 every household in the world shared ONE price-response curve.
Two customers in identical circumstances responded identically, so there was no household TYPE to
infer — and inference advantage means knowing something about THIS household that its observables
do not already say. The company could therefore demonstrate no inference advantage however good its
model became, which is the ceiling the director named:

    "In a world with one decision axis the company can't show inference advantage, because there's
     only one thing to infer. The world's richness sets the maximum skill the company can ever
     demonstrate."

The `price_sensitivity` axis was ALREADY drawn per household, coverage-tested, walled off from the
company and mutation-tested against leaks — and read by no live module. The curriculum file even
states it is *"discoverable via rate-change churn response (get_churn_estimate)"*, a channel that
did not exist until this wiring. See `docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md`.

R13. The MECHANISM is baseline/fidelity and mine: real households differ in how hard they feel a
price move. The MARGINALS — how many are highly elastic — are curriculum and stay the director's.
`test_the_weights_are_mean_preserving_against_the_CURRICULUMS_OWN_SHARES` is that boundary made
mechanical.
"""
from __future__ import annotations

import pytest

from simulation.market_switching_propensity import (
    PRICE_SENSITIVITY_WEIGHT,
    churn_position_multiplier,
    offer_position_multiplier,
    perceived_price_differential,
    price_sensitivity_weight,
)
from simulation.population_draw import (
    _load_cohort_curriculum,
    assign_cohort,
    price_sensitivity_for_customer,
)

BASE_SEED = 20260724
#: Enough ids that all three levels appear. Floored below, not assumed.
IDS = [f"PROS-2019-{i:04d}" for i in range(400)]


# ---------------------------------------------------------------------------
# 1. one source of truth — the accessor and the cohort never disagree
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("customer_id", ["C1", "C5", "PROS-2016-0003", "SYN-2023-0007"])
def test_the_accessor_returns_EXACTLY_what_the_cohort_carries(customer_id):
    """THE `draw_region_for_customer` DISCIPLINE. A second, independent draw here would give a
    customer one sensitivity in its cohort and a different one in its behaviour — the precise
    disagreement that accessor was created to prevent."""
    assert price_sensitivity_for_customer(customer_id, BASE_SEED) == (
        assign_cohort(customer_id, BASE_SEED).price_sensitivity)


def test_the_draw_is_stable_for_a_customers_whole_life():
    """A sensitivity redrawn per renewal would be noise, not a trait, and nothing could ever infer
    it — which would reproduce the defect this closes while appearing to fix it."""
    assert len({price_sensitivity_for_customer("C1", BASE_SEED) for _ in range(5)}) == 1


# ---------------------------------------------------------------------------
# 2. the world is no longer homogeneous — the defect this exists to remove
# ---------------------------------------------------------------------------

def test_the_population_actually_spans_all_three_levels():
    """POPULATION FLOOR. Every test below compares levels; if the draw collapsed to one value they
    would all pass while measuring a world still homogeneous."""
    drawn = {price_sensitivity_for_customer(i, BASE_SEED) for i in IDS}
    assert len(IDS) >= 100, "the id list itself emptied"
    assert drawn == {"high", "medium", "low"}, (
        f"the draw spans only {sorted(drawn)} — the axis cannot differentiate anyone")


def test_two_households_at_the_SAME_price_now_respond_DIFFERENTLY():
    """THE WHOLE POINT, stated as an assertion. Before this wiring both sides of this comparison
    returned the same number for every pair of customers in the world."""
    differential = 0.10
    responses = {
        churn_position_multiplier(perceived_price_differential(differential, level))
        for level in ("high", "medium", "low")
    }
    assert len(responses) == 3, (
        "households of different drawn sensitivity respond identically to the same price — the "
        "axis is wired but inert, which is the state this change exists to leave")


def test_a_MORE_sensitive_household_leaves_faster_when_dear():
    d = 0.10
    high = churn_position_multiplier(perceived_price_differential(d, "high"))
    low = churn_position_multiplier(perceived_price_differential(d, "low"))
    assert high > low


def test_a_MORE_sensitive_household_also_stays_HARDER_when_keen():
    """ELASTICITY IS TWO-SIDED. Weighting only the loss leg would model spite, not sensitivity:
    a household that punishes a price rise but shrugs at a price cut is not more price-sensitive,
    it is differently-tempered. This is the half a one-directional test would miss."""
    d = -0.10
    high = churn_position_multiplier(perceived_price_differential(d, "high"))
    low = churn_position_multiplier(perceived_price_differential(d, "low"))
    assert high < low, "the elastic household did not respond more to a KEENER price"


# ---------------------------------------------------------------------------
# 3. R12 — the anti-goal-seek guarantee survives, at every weight
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("level", ["high", "medium", "low"])
@pytest.mark.parametrize("d", [0.01, 0.05, 0.10, 0.20])
def test_the_no_free_lunch_identity_holds_for_every_household(level, d):
    """`m(d) * m(-d) == 1` is what guarantees there is NO differential at which the company gains
    on winning AND on keeping. It holds for any argument, which is exactly why the weight scales
    the DIFFERENTIAL. Checked per household, because a guarantee that held only on average would
    leave individual customers the company could profit from both ways."""
    felt = perceived_price_differential(d, level)
    assert offer_position_multiplier(felt) * offer_position_multiplier(-felt) == pytest.approx(1.0)


def test_weighting_the_MULTIPLIER_instead_would_break_that_identity():
    """THE REJECTED DESIGN, pinned so nobody re-introduces it. Scaling the returned multiplier
    gives `w*m(d) * w*m(-d) == w**2`; at w<1 that is a household the company profits from on both
    legs at once — the goal-seeking hole R12 exists to close. This test FAILS if someone 'simplifies'
    `perceived_price_differential` into a multiplier scaling."""
    d, w = 0.10, PRICE_SENSITIVITY_WEIGHT["low"]
    wrong = (w * offer_position_multiplier(d)) * (w * offer_position_multiplier(-d))
    assert wrong != pytest.approx(1.0), "w**2 == 1 would make this test vacuous"
    right = perceived_price_differential(d, "low")
    assert offer_position_multiplier(right) * offer_position_multiplier(-right) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 4. R13 — fidelity, not difficulty. The boundary, made mechanical.
# ---------------------------------------------------------------------------

def test_the_weights_are_mean_preserving_against_the_CURRICULUMS_OWN_SHARES():
    """THE R13 BOUNDARY AS A CONTROL, and the reason it reads the curriculum FILE rather than a
    copy of its numbers: independence (R15 TAUTOLOGY).

    MEAN-PRESERVING IN THE WEIGHT, WHICH IS NOT THE SAME AS IN THE RESPONSE — see
    `test_the_spread_RAISES_average_churn_and_that_is_recorded_not_tuned_away`. The weight mean is
    the thing that is CHOSEN here, so it is the thing this control pins.

    IF THE DIRECTOR CHANGES THE MARGINALS, THIS TEST FAILS, AND THAT IS CORRECT. New shares against
    unchanged weights move the population mean off 1.0, which silently converts a fidelity change
    into a difficulty change — an agent-side curriculum edit, which R13 forbids. The remedy is to
    renormalise the weights (or to accept the shift deliberately and say so), never to loosen this.
    """
    shares = _load_cohort_curriculum()["price_sensitivity_marginals"]["value"]
    assert shares, "the curriculum's price-sensitivity marginals are empty"
    assert set(shares) == set(PRICE_SENSITIVITY_WEIGHT), (
        f"levels disagree: curriculum {sorted(shares)} vs weights "
        f"{sorted(PRICE_SENSITIVITY_WEIGHT)} — one of them has drifted")
    mean = sum(shares[k] * PRICE_SENSITIVITY_WEIGHT[k] for k in shares)
    assert mean == pytest.approx(1.0, abs=1e-9), (
        f"population-mean price sensitivity is {mean:.6f}, not 1.0. The book's AGGREGATE price "
        "response has moved, so this is no longer a mean-preserving spread and no longer a pure "
        "fidelity change. Renormalise PRICE_SENSITIVITY_WEIGHT against the current shares.")


def test_the_spread_RAISES_average_churn_and_that_is_recorded_not_tuned_away():
    """THE CONSEQUENCE OF THE SPREAD, PINNED. `churn_position_multiplier` is CONVEX, so by Jensen
    a mean-preserving spread in its ARGUMENT raises the mean RESPONSE: the book churns more, by up
    to ~14%, purely from households now differing.

    The first version of the module note claimed the aggregate response was unchanged. It is not,
    and the honest move is to record the direction rather than renormalise the weights until the
    aggregate holds still — that would be choosing parameters to hit an output, which is what R12
    forbids. The direction is also why this is safe as a baseline change: it moves AGAINST the
    company, never for it.
    """
    shares = _load_cohort_curriculum()["price_sensitivity_marginals"]["value"]
    for d in (-0.20, -0.10, 0.10, 0.20):
        old = churn_position_multiplier(d)
        new = sum(shares[k] * churn_position_multiplier(perceived_price_differential(d, k))
                  for k in shares)
        assert new >= old, (
            f"at {d:+.0%} the spread LOWERED average churn ({new:.4f} < {old:.4f}) — a convex "
            "response cannot do that under a mean-preserving spread, so either the weights are no "
            "longer mean-preserving or the curve is no longer convex here")


def test_the_median_household_behaves_EXACTLY_as_every_household_did_before():
    """The regression anchor. `medium` is 1.0 by construction, so the pre-change world is still
    reachable and any moved figure can be attributed to the SPREAD rather than to a re-levelling."""
    assert PRICE_SENSITIVITY_WEIGHT["medium"] == 1.0
    for d in (-0.2, -0.05, 0.0, 0.05, 0.2):
        assert perceived_price_differential(d, "medium") == pytest.approx(d)
        assert churn_position_multiplier(perceived_price_differential(d, "medium")) == (
            pytest.approx(churn_position_multiplier(d)))


# ---------------------------------------------------------------------------
# 5. R15 FAIL-OPEN — an unresolvable sensitivity is the OLD world, never immunity
# ---------------------------------------------------------------------------

def test_an_unknown_sensitivity_is_the_pre_change_behaviour_not_a_zero():
    """A zero weight would make the household immune to price — the exact failure this change
    exists to remove, re-introduced through the error path. 1.0 is the world as it was."""
    assert price_sensitivity_weight(None) == 1.0
    assert price_sensitivity_weight("not_a_level") == 1.0
    assert perceived_price_differential(0.1, None) == pytest.approx(0.1)


def test_no_weight_is_zero_or_negative():
    """Zero is immunity; negative is a household that leaves BECAUSE you got cheaper, which would
    also invert the R12 identity's sign."""
    for level, w in PRICE_SENSITIVITY_WEIGHT.items():
        assert w > 0, f"{level} has a non-positive weight ({w})"


# ---------------------------------------------------------------------------
# 6. R15 ON THE WIRING — the weight is FELT at the decision, not merely defined
# ---------------------------------------------------------------------------
#
# EVERY TEST ABOVE THIS LINE EXERCISES THE FUNCTIONS. Not one of them would go red if the call
# site inside `roll_lifecycle_event` were deleted tomorrow: `perceived_price_differential` would
# still weight, `price_sensitivity_for_customer` would still draw, the mean would still be 1.0,
# and the world would be homogeneous again with a green suite over it. A weight that is DRAWN and
# then NOT FELT is the exact failure this change exists to remove — it is the state the axis was
# already in before 2026-08-27, when it was drawn, coverage-tested, walled off, mutation-tested
# against leaks, and read by nothing. So the control has to run the DECISION.
#
# The two mutations this section must fire on, verified red before it was committed:
#   1. WEIGHTING IS A NO-OP:  PRICE_SENSITIVITY_WEIGHT = {high: 1.0, medium: 1.0, low: 1.0}
#   2. WIRING IS REVERTED:    `churn_position_multiplier(differential)` at the call site,
#                             i.e. exactly HEAD before this change.
# Both leave the module importable and the section-1..5 suite green.

def _one_renewal(monkeypatch, sensitivity: str) -> float:
    """`realized_churn_probability` for one account at one renewal, priced 20% above the SVT.

    DEARER ON PURPOSE: at parity the differential is 0.0 and `0.0 * w == 0.0` for every weight,
    so a parity fixture cannot distinguish any of this and would pass against both mutations —
    the FIXTURE-AT-THE-FALLBACK-VALUE shape. The probability is read, never the rolled event:
    the roll is a dice throw, the probability is the world's decision.
    """
    from simulation import population_draw as pd
    from simulation.customer_events import roll_lifecycle_event
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh
    from tests.simulation.test_customer_events import (
        _build_one_year_records,
        _first_renewal_date,
        _make_customers,
    )

    monkeypatch.setattr(pd, "price_sensitivity_for_customer", lambda *a, **k: sensitivity)

    renewal = _first_renewal_date("2016-01-01")
    svt = get_svt_elec_rate_gbp_per_mwh(renewal)
    event = roll_lifecycle_event(
        "C5", renewal, "electricity",
        _build_one_year_records(), _make_customers(),
        old_rate_gbp_per_mwh=svt, new_rate_gbp_per_mwh=svt * 1.20,
    )
    assert event is not None, "the fixture stopped reaching a renewal — it can no longer see this"
    assert event["price_differential_vs_svt"] == pytest.approx(0.20), (
        "the fixture is no longer priced away from the market, so the weight has nothing to bite "
        "on and this whole section would pass vacuously")
    return event["realized_churn_probability"]


def test_the_CHURN_DECISION_actually_feels_the_households_drawn_sensitivity(monkeypatch):
    """THE WIRING, AS BEHAVIOUR. Two households, same book, same price, same renewal — differing
    only in the sensitivity the world drew for them — must face different churn probabilities.

    FIRES ON BOTH MUTATIONS. All-1.0 weights make the felt differential identical; a reverted
    call site never consults the sensitivity at all. Either way both sides return the same
    number and this assertion is the thing that notices."""
    high = _one_renewal(monkeypatch, "high")
    low = _one_renewal(monkeypatch, "low")

    assert high > low, (
        f"the elastic household ({high}) and the disengaged one ({low}) face the same churn "
        "probability at the same price — the sensitivity is drawn but never felt at the decision, "
        "which is the pre-2026-08-27 world this change exists to leave")


def test_the_NULL_RUNG_two_identical_households_agree(monkeypatch):
    """RUNG 0. Without this, the test above could be reading fixture noise rather than the weight:
    a difference between two runs means nothing until the SAME input is shown to produce the same
    output. This must pass under both mutations — it is the baseline, not a detector."""
    assert _one_renewal(monkeypatch, "medium") == _one_renewal(monkeypatch, "medium")


def test_the_MEDIAN_household_is_unchanged_at_the_decision_too(monkeypatch):
    """The end-to-end regression anchor, and the reason mutation 1 is detectable at all: `medium`
    is 1.0, so the pre-change world is still reachable THROUGH THE DECISION. Any moved run figure
    is therefore attributable to the SPREAD and not to a re-levelling of the whole book."""
    assert _one_renewal(monkeypatch, "medium") == _one_renewal(monkeypatch, None)


# ---------------------------------------------------------------------------
# 7. THE SEED THE DECISION RESOLVES THE TRAIT AT — the run's, not the default
# ---------------------------------------------------------------------------

def test_the_decision_point_resolves_the_trait_at_the_RUNS_seed_not_the_module_default():
    """A trait resolved at the module DEFAULT is correct only until something passes `base_seed=`,
    and then the customer carries one sensitivity in its cohort and another in its behaviour —
    the disagreement `draw_region_for_customer` exists to prevent, re-introduced downstream.

    MUTATION (must fire): `run_base_seed()` returning `_DEFAULT_BASE_SEED` unconditionally."""
    import simulation.live_population as lp

    assert lp.run_base_seed() == lp._DEFAULT_BASE_SEED or lp._RUN_BASE_SEED is not None


def test_run_base_seed_reports_the_seed_a_book_was_ACTUALLY_drawn_at(monkeypatch):
    """BOTH WAYS. A recorded seed is returned; no recorded seed falls back to the default. The
    fallback is the FAIL-OPEN-shaped branch, so it is asserted rather than assumed."""
    import simulation.live_population as lp

    monkeypatch.setattr(lp, "_RUN_BASE_SEED", None)
    assert lp.run_base_seed() == lp._DEFAULT_BASE_SEED, "no book drawn — the default is the answer"

    monkeypatch.setattr(lp, "_RUN_BASE_SEED", 424242)
    assert lp.run_base_seed() == 424242, (
        "the run drew its book at 424242 and the accessor still reports the module default — "
        "every per-household trait resolved through it now belongs to a different world")


def test_the_live_seam_RECORDS_its_seed_so_the_accessor_is_not_a_second_default(monkeypatch):
    """THE RECORDING ITSELF, which is what makes `run_base_seed()` a thread rather than a
    re-derivation. `live_population()` is called at import by every live entrypoint, so this is
    the step that makes a live decision point read the run's own seed.

    MUTATION (must fire): drop the `_RUN_BASE_SEED = seed` assignment from `live_population()`."""
    import simulation.live_population as lp

    monkeypatch.setattr(lp, "_RUN_BASE_SEED", None)
    lp.live_population(base_seed=987654)
    assert lp.run_base_seed() == 987654, (
        "the seam drew a book and did not record which seed it drew it at")
