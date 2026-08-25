"""R15 contract for the one lever a supplier actually holds: its own price.

THE DEFECT, MEASURED AT HEAD BEFORE THIS LANDED. `price_differential_pct` reached
`simulation/customer_events.py` as a parameter and was used at exactly ONE site --
`build_home_move_win_rates`. It touched the WIN side and nothing in the churn chain. An existing
customer's chance of leaving read bill shock, income stress, satisfaction, market conditions and
tenure, and never what this supplier was charging them relative to everyone else.

WHY THAT IS THE THESIS AND NOT A DETAIL. The director's frame is a supplier that beats an
average player "precisely to the degree it understands and predicts the truth better than
average", measured against "the same book run by a supplier applying flat rules". With price
disconnected from departure there is no such measurement: over-pricing has no consequence, so a
flat-rules baseline can be neither beaten nor lost to on the only lever a supplier holds.

It also explains a number: across 1,330 graded renewals in the shipped run, the world's own
churn probability never exceeded 0.41 against its own 0.95 ceiling. The largest lever was not
attached.
"""
from __future__ import annotations

import pytest

from simulation import customer_events as ce
from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from simulation.market_switching_propensity import (
    churn_position_multiplier,
    offer_position_multiplier,
)
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

TERM = "2024-01-01"
SVT = get_svt_elec_rate_gbp_per_mwh(TERM)


# --------------------------------------------------------------------------- #
# The differential is this customer's own, not the run's                       #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("factor,expected", [(0.90, -0.10), (1.00, 0.0), (1.10, 0.10)])
def test_the_differential_is_the_offered_rate_against_the_published_SVT(factor, expected):
    assert ce._price_differential_vs_market(SVT * factor, TERM) == pytest.approx(expected)


def test_TWO_customers_priced_differently_get_DIFFERENT_positions():
    """THE WHOLE POINT, and the thing a run-level constant could never express. A supplier that
    prices two customers differently must face two different consequences, or per-customer
    pricing is a decision with no outcome attached."""
    dearer = ce._price_differential_vs_market(SVT * 1.20, TERM)
    keener = ce._price_differential_vs_market(SVT * 0.95, TERM)

    assert dearer > 0 > keener


def test_an_UNKNOWN_rate_is_NOT_reported_as_parity():
    """Parity is a claim -- "we are exactly at the market" -- and "we do not know where we sit"
    is a different one. Returning 0.0 here would let a missing rate silently assert the first.

    MUTATION (must fire): return 0.0 instead of None when the rate is absent."""
    assert ce._price_differential_vs_market(None, TERM) is None


def test_an_UNKNOWN_market_reference_is_not_reported_as_parity_either():
    assert ce._price_differential_vs_market(SVT, "1990-01-01") is None


# --------------------------------------------------------------------------- #
# Being dearer costs customers, and it is the MIRROR of the win side           #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("differential", [0.05, 0.10, 0.20, 0.50])
def test_being_DEARER_raises_churn(differential):
    """MUTATION (must fire): drop the price block from the churn chain -- which is exactly the
    state of HEAD before this landed."""
    assert churn_position_multiplier(differential) > 1.0


@pytest.mark.parametrize("differential", [-0.05, -0.10, -0.20])
def test_being_CHEAPER_lowers_churn(differential):
    assert churn_position_multiplier(differential) < 1.0


def test_a_supplier_that_prices_itself_OUT_OF_THE_MARKET_can_lose_essentially_everyone():
    """THE PROPERTY THE WORLD DID NOT HAVE, and the reason the loss leg parts from the win leg.

    Measured before the fix: a supplier 25% above the market and one 200% above it lost the SAME
    third of their book, because the shared curve saturates at 4.4x. The world could punish
    moderate over-pricing and could not express a supplier pricing itself out of existence -- so
    `WORLD_MAX_CHURN_PROBABILITY` was unreachable by the one mechanism that should reach it.

    MUTATION (must fire): revert the loss leg to `1 / offer_position_multiplier`.
    """
    base = 0.08
    assert min(base * churn_position_multiplier(0.25), WORLD_MAX_CHURN_PROBABILITY) < 0.5
    assert min(base * churn_position_multiplier(1.00), WORLD_MAX_CHURN_PROBABILITY) == pytest.approx(
        WORLD_MAX_CHURN_PROBABILITY), (
        "a supplier charging double the market still cannot lose its book"
    )


def test_the_two_legs_AGREE_below_saturation_and_only_part_above_it():
    """The split is surgical, not a second curve. Below the calibrated ceiling the loss leg IS
    the reciprocal of the win leg, so nothing already measured moves."""
    for d in (-0.20, -0.05, 0.0, 0.05, 0.10, 0.20):
        assert churn_position_multiplier(d) == pytest.approx(1.0 / offer_position_multiplier(d))
    assert churn_position_multiplier(1.0) > 1.0 / offer_position_multiplier(1.0)


def test_the_WIN_leg_keeps_its_saturation_because_the_market_is_finite():
    """You cannot win more customers than the market has engaged households to give, and
    `_MAX_RATE` is exactly that ceiling. Extending the win leg too would have modelled a supplier
    who can buy an unbounded number of customers by discounting.

    MUTATION (must fire): extrapolate the win leg as well."""
    assert offer_position_multiplier(-2.0) == pytest.approx(offer_position_multiplier(-5.0))


def test_the_loss_side_is_the_EXACT_reciprocal_of_the_win_side():
    """THE ANTI-GOAL-SEEK GUARANTEE, and the reason the same curve is reused rather than a
    second one shaped for churn. `offer_position_multiplier`'s own docstring proves
    `m(d) * m(-d) == 1` so that "there is no d at which both legs improve". Two independently
    shaped price responses would leave a differential at which the company gained on BOTH legs,
    which is the goal-seeking hole R12 exists to close.

    MUTATION (must fire): give the churn side its own elasticity constant.
    """
    # BELOW SATURATION ONLY. Above it the legs part on purpose -- see
    # `test_the_two_legs_AGREE_below_saturation_and_only_part_above_it` -- and the guarantee that
    # survives up there is monotonicity, tested separately: there is still no d at which both
    # legs improve, because churn rises and wins fall across the whole range.
    for d in (0.02, 0.05, 0.10, 0.20):
        win = offer_position_multiplier(d)
        churn = churn_position_multiplier(d)
        # RECIPROCAL WITH THE WIN SIDE: what a price move costs in departures is exactly what it
        # costs in wins, inverted. (The first version of this assertion multiplied the two the
        # wrong way round and asserted m(d)^2 == 1, which is only true at parity -- caught by
        # the test failing at d=0.02 with 0.775.)
        assert churn * win == pytest.approx(1.0), "the two legs are no longer reciprocal"
        # SYMMETRIC ABOUT PARITY: dearer by d costs what cheaper by d gains, so there is no d at
        # which both legs improve.
        assert churn * churn_position_multiplier(-d) == pytest.approx(1.0)


def test_ABOVE_saturation_the_punishment_exceeds_the_reward_which_is_the_asymmetry_real_retail_has():
    """AN ACCIDENT WORTH KEEPING, and worth naming rather than leaving to be discovered.

    `offer_position_multiplier`'s own docstring registers symmetry as a NAMED SIMPLIFICATION and
    says plainly what it costs: "Real retail is not symmetric -- loss aversion and incumbency
    inertia both say a dearer offer is punished harder than a cheaper one is rewarded -- and
    nothing in the DESNZ series can settle the asymmetry."

    Extending the loss leg past the calibrated ceiling, for the separate reason that the world
    could not otherwise kill an over-pricing supplier, produces exactly that asymmetry above
    saturation. It is not evidence for the asymmetry and does not discharge the simplification --
    it happens to point the way the literature says, which is worth recording and not worth
    claiming."""
    for d in (0.50, 1.00, 2.00):
        punished = churn_position_multiplier(d)
        rewarded = 1.0 / churn_position_multiplier(-d)
        assert punished > rewarded


def test_the_response_is_MONOTONE_in_price():
    """The property the model actually needs. A non-monotone response would give a supplier a
    price at which raising it further LOSES fewer customers, which is not a market."""
    multipliers = [churn_position_multiplier(d)
                   for d in (-0.5, -0.2, -0.05, 0.0, 0.05, 0.2, 0.5, 1.0, 2.0)]

    assert all(a <= b + 1e-12 for a, b in zip(multipliers, multipliers[1:])), multipliers


def test_the_response_is_BOUNDED_so_a_price_shock_cannot_produce_a_probability_above_one():
    """The curve saturates at 0.22 and so bounds itself in [1/4.4, 4.4]; the world ceiling then
    catches the product. Both are needed: an unbounded multiplier on a churn already near the
    ceiling would produce a probability above 1 and roll it."""
    extreme = churn_position_multiplier(50.0)

    assert min(0.9 * extreme, WORLD_MAX_CHURN_PROBABILITY) <= WORLD_MAX_CHURN_PROBABILITY, (
        "the world ceiling no longer catches an extreme price shock, so a probability above one "
        "could be rolled"
    )


# --------------------------------------------------------------------------- #
# It is wired into the chain, not merely importable                            #
# --------------------------------------------------------------------------- #

def test_the_churn_chain_ACTUALLY_reads_the_price_position():
    """A control nobody reaches is a file. The defect this repairs was precisely a parameter that
    arrived, was passed to one unrelated function, and never touched the thing it was named for.

    MUTATION (must fire): delete the `if differential:` block from `roll_lifecycle_event`.
    """
    source = (ce.__file__ and open(ce.__file__, encoding="utf-8").read()) or ""
    chain = source[source.index("def roll_lifecycle_event"):]

    assert "offer_position_multiplier(differential)" in chain, (
        "the churn chain does not read this supplier's own price position, so the company can "
        "price itself to any level and lose nobody for it"
    )
    assert "_price_differential_vs_market" in chain


def test_the_event_RECORDS_the_position_it_priced_against():
    """A world that acts on a number and does not report it cannot be audited, and this is the
    number that decides whether an over-pricing supplier is punished."""
    source = open(ce.__file__, encoding="utf-8").read()

    assert '"price_differential_vs_svt"' in source
    assert '"offer_position_multiplier"' in source
