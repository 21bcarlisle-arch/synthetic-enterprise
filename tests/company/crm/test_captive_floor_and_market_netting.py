"""R15 contract for the two captive floors in this company's churn belief, and for the
difference between a bill that rose because the market rose and one that rose because we did.

WHY THIS FILE EXISTS. `WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_
UNBOUNDED_2026-08-25`, BLOCKING: expected value is `P(stay) x margin x volume`, so a `P(stay)`
that never falls below some positive floor makes expected value MONOTONE INCREASING IN PRICE
WITHOUT LIMIT. The first decision ever made out of this belief -- `company/pricing/
value_based_renewal.py` -- then priced every one of 263 real accounts thirty to a hundred times
the flat rule and reported that not one was value-negative. The maximiser was not wrong. It
found what the model actually said.

There were TWO such floors, reached by different routes and neither visible while the belief was
only ever REPORTED:

  1. `churn_model.MAX_CHURN_PROBABILITY = 0.95` -- five percent of every account modelled as
     staying whatever it is charged.
  2. `enriched_churn_estimate`'s `p * market_conditions_multiplier` -- which bounds the estimate
     at the MULTIPLIER, so in 2022 (m = 0.44) no customer could be given more than a 44% chance
     of leaving. Fifty-six percent captive, one layer above the first and larger than it.

WHAT WAS NOT DONE, because it was the tempting move and the finding says so in its own words:
"Move the cap so the arm behaves. That is goal-seeking against a calibrated belief." No
sensitivity was retuned. What changed is a SHAPE and a QUANTITY: the asymptote is 1.0 because
nobody is unconditionally captive, the multiplier composes in survival space because it scales a
RATE, and the rate response is taken on the SUPPLIER-SPECIFIC move because that is the move
against which a cheaper alternative demonstrably exists.

Every one of those three moves costs the company money rather than saving it, which is the R13
test that matters: they make over-pricing more expensive and cannot make anything cheaper.
"""
from __future__ import annotations

import pytest

from company.crm import churn_model as cm
from company.crm.churn_model import estimate_churn_probability
from company.crm.enriched_churn_estimate import (
    _apply_market_conditions,
    enriched_churn_estimate,
    enriched_passive_churn_estimate,
)
from company.crm.market_conditions import (
    market_conditions_multiplier,
    market_rate_move_pct,
)

RESI = dict(tenure_years=4.0, prev_annual_bill_gbp=3100.0)
BASE_RATE = 100.0


def _p(rise_pct: float, **kw) -> float:
    """This company's estimate of P(leave) when it raises THIS customer by `rise_pct`."""
    return estimate_churn_probability(
        BASE_RATE, BASE_RATE * (1.0 + rise_pct), RESI["tenure_years"],
        RESI["prev_annual_bill_gbp"], **kw)


# --------------------------------------------------------------------------- #
# Floor 1: nobody is unconditionally captive                                   #
# --------------------------------------------------------------------------- #

def test_there_is_NO_price_at_which_a_share_of_the_book_is_modelled_as_STAYING():
    """THE FINDING'S HEADLINE, stated as the property rather than as the constant.

    MUTATION (must fire): restore `MAX_CHURN_PROBABILITY = 0.95`. Then P(stay) bottoms out at
    0.05 however extreme the price, and `P(stay) x margin` grows without limit.
    """
    assert _p(10.0) > 0.99, "a supplier charging eleven times the market still keeps a share"
    assert 1.0 - _p(20.0) < 1e-3, (
        "P(stay) does not decay to zero, so expected value is unbounded in price"
    )


def test_expected_value_TURNS_OVER_instead_of_rising_forever():
    """THE DISCHARGE TEST, and the only one that speaks in the units the finding was about. It
    is not enough that P(stay) reaches zero eventually -- it must reach zero fast enough that
    `P(stay) x contribution` has an INTERIOR maximum, because that maximum is the price a
    value-based arm would actually choose.

    Measured at HEAD before the fix this sequence was monotone increasing to the last candidate.

    MUTATION (must fire): restore either floor. With 0.95 the sequence rises without limit;
    with `p * m` it rises without limit in every year whose multiplier is below 1.
    """
    eac_mwh, fixed, cost = 3.1, 99.0, 66.0
    curve = [(m, (1.0 - enriched_churn_estimate(
        BASE_RATE, BASE_RATE + m, 4.0, 3100.0, renewal_year=2025)) * (m * eac_mwh + fixed - cost))
        for m in (2, 10, 30, 60, 100, 130, 200, 400, 800, 2000)]
    best = max(curve, key=lambda row: row[1])

    assert best[0] not in (curve[0][0], curve[-1][0]), (
        "the best margin sits at an endpoint of the range searched, which is a ceiling "
        f"reporting itself as a decision: {curve}"
    )
    assert curve[-1][1] < best[1] / 10.0, (
        "pricing at 1000x the flat rule is still worth a tenth of the optimum, so the "
        f"maximiser is being bounded by the candidate list rather than by the belief: {curve}"
    )


def test_every_estimate_BELOW_the_elbow_is_unchanged_because_the_calibration_was_not_touched():
    """The fix must not move any number this model has ever produced in anger. The saturation
    elbow is 0.9 and no real renewal in this book has ever produced an estimate near it, so the
    identity branch is where every shipped figure came from and still comes from.

    MUTATION (must fire): retune `RATE_SENSITIVITY` or `BASE_CHURN_RATE` to make the arm behave
    -- which is exactly what the finding forbids.
    """
    assert _p(0.0) == pytest.approx(0.06)
    assert _p(0.10) == pytest.approx(0.14)
    assert _p(0.50) == pytest.approx(0.46)
    assert _p(1.00) == pytest.approx(0.86)
    for raw in (0.0, 0.05, 0.3, 0.6, cm.CHURN_SATURATION_ELBOW):
        assert cm._saturate_churn_probability(raw) == raw


def test_the_estimate_stays_a_PROBABILITY_however_extreme_the_price():
    for rise in (0.0, 1.0, 5.0, 50.0, 500.0):
        assert 0.0 <= _p(rise) <= 1.0


# --------------------------------------------------------------------------- #
# Floor 2: a multiplier that scales a RATE cannot bound a probability          #
# --------------------------------------------------------------------------- #

def test_a_year_with_a_LOW_switching_multiplier_does_not_make_customers_CAPTIVE():
    """2022's multiplier is 0.44 -- switching collapsed to 3-4% while bills hit GBP 3,549. Under
    `p * m` that made 56% of every account unconditionally retained, which is a far bigger
    captive floor than the 0.95 cap the finding was filed about and sat one layer above it.

    MUTATION (must fire): restore `result = max(rate_est, payment_est) * multiplier`. Then this
    assertion fails at 0.44, because no price on earth can push the estimate past the multiplier.
    """
    assert market_conditions_multiplier(2022) < 0.5, "2022 is no longer the low-switching year"
    extreme = enriched_churn_estimate(BASE_RATE, BASE_RATE * 20.0, 4.0, 3100.0, renewal_year=2022)

    assert extreme > 0.90, (
        "in a low-switching year the company still believes a share of its book cannot be "
        f"driven away by any price: P(leave) saturates at {extreme:.3f}"
    )


def test_survival_space_AGREES_with_multiplication_where_every_real_renewal_sits():
    """The change must be invisible in the regime the multiplier was calibrated on, or it is a
    recalibration wearing a bug fix's clothes. At p = 0.10 and m = 0.44 the old form gave 0.0440
    and the new one gives 0.0453 -- a thirteen-basis-point difference on a figure published to
    two.
    """
    for p, m in ((0.05, 0.44), (0.10, 0.44), (0.10, 0.93), (0.20, 1.0)):
        assert _apply_market_conditions(p, m) == pytest.approx(p * m, abs=0.02)


def test_the_multiplier_still_DOES_something_or_it_would_not_be_worth_reading():
    """A fix that quietly neutralised the market-conditions signal would pass every test above.
    Low-switching years must still lower the estimate and high-switching years raise it.

    MUTATION (must fire): return `p_leave` unchanged.
    """
    quiet = enriched_churn_estimate(BASE_RATE, BASE_RATE * 1.2, 4.0, 3100.0, renewal_year=2022)
    normal = enriched_churn_estimate(BASE_RATE, BASE_RATE * 1.2, 4.0, 3100.0, renewal_year=2025)

    assert quiet < normal
    assert _apply_market_conditions(0.3, 1.0) == pytest.approx(0.3), "m = 1 must be the identity"


def test_the_passive_path_got_the_same_multiplier_fix_because_it_had_the_same_floor():
    """`enriched_passive_churn_estimate` multiplied by the same multiplier and so carried the
    same captive floor. Passive rollers are the MAJORITY of domestic renewals (65%), so fixing
    only the active path would have left this floor under most of the book.

    MUTATION (must fire): restore `* market_conditions_multiplier(...)` on the passive path.
    """
    assert _apply_market_conditions(0.99, 0.44) > 0.44, (
        "the multiplier can still bound a probability below itself"
    )
    assert enriched_passive_churn_estimate(BASE_RATE, BASE_RATE, 4.0, renewal_year=None) == (
        pytest.approx(enriched_passive_churn_estimate(BASE_RATE, BASE_RATE, 4.0)))


def test_the_PASSIVE_CAP_is_the_next_instance_of_this_class_and_is_DELIBERATELY_not_touched_here():
    """WHAT THIS COMMIT DOES NOT FIX, pinned so it is a recorded boundary and not an oversight.

    `PASSIVE_CHURN_CAP = 0.10` is a harder captive floor than either of the two removed above --
    ninety percent of a passive roller is modelled as staying at ANY price -- and it sits under
    65% of domestic renewals. It is not fixed here for two reasons, both structural rather than
    convenient:

      * it is MIRRORED, not owned. `simulation/renewal_engagement.PASSIVE_CHURN_CAP` is the
        world's ground truth and the company's copy is its ESTIMATE of it, with a seam test
        (`tests/company/interfaces/test_churn_estimation_seam.py`) whose whole purpose is that
        the company may not read the world's. Moving the company's copy alone would widen a
        belief-versus-truth gap; moving both is a baseline change (R13) about how inert an SVT
        roller really is, which is a separate question with its own evidence.
      * it is NOT what bounds the decision that surfaced this. `value_based_renewal` prices
        through the ACTIVE path.

    MUTATION (must fire): change either copy of the cap without the other. This asserts they
    agree, so a one-sided move reds here and names why.
    """
    from simulation import renewal_engagement as world

    assert cm.PASSIVE_CHURN_CAP == world.PASSIVE_CHURN_CAP == 0.10
    at_any_price = enriched_passive_churn_estimate(BASE_RATE, BASE_RATE * 20.0, 4.0,
                                                   renewal_year=None)

    assert at_any_price == pytest.approx(cm.PASSIVE_CHURN_CAP), (
        "the passive path's remaining ceiling is no longer the passive cap, so the boundary "
        "this test records has moved and the reasoning above needs revisiting"
    )


# --------------------------------------------------------------------------- #
# The move that was ours, and the move that was everybody's                    #
# --------------------------------------------------------------------------- #

def test_the_SAME_bill_rise_means_different_things_depending_on_who_caused_it():
    """THE SUBSTANTIVE CORRECTION, and the half of the finding that was `inferred` rather than
    observed. A customer whose bill rises 60% because THIS SUPPLIER raised its price has a
    cheaper alternative and it is obvious -- the market average. A customer whose bill rises 60%
    because the market rose has nowhere to go. That is not a hypothesis: it is 2022.

    MUTATION (must fire): drop `- market_move_pct` from the rate response.
    """
    ours = _p(0.60, market_move_pct=0.0)
    everybodys = _p(0.60, market_move_pct=0.60)

    assert ours > everybodys + 0.3, (
        "the company cannot tell 'we put your price up 60%' from 'everyone did'"
    )


def test_a_move_that_merely_TRACKS_the_market_reads_as_no_move_at_all():
    """The netting is exact, not a discount: a supplier passing through a market-wide rise has
    not changed its position, and position is what the response is about."""
    for move in (0.10, 0.6667, -0.13):
        assert _p(move, market_move_pct=move) == pytest.approx(_p(0.0))


def test_a_supplier_that_UNDERCUTS_a_rising_market_is_rewarded_for_it():
    """The mirror, and the reason this is a correction rather than a shield. In 2022 a supplier
    whose price rose 10% while the cap rose 66.7% became dramatically cheaper than everyone, and
    the model must say so."""
    assert _p(0.10, market_move_pct=0.6667) < _p(0.0)


def test_the_response_is_MONOTONE_in_the_supplier_specific_move():
    curve = [_p(r, market_move_pct=0.2) for r in (-0.5, 0.0, 0.2, 0.5, 1.0, 3.0)]

    assert all(a <= b + 1e-12 for a, b in zip(curve, curve[1:])), curve


def test_NO_new_sensitivity_constant_was_introduced_for_the_supplier_specific_move():
    """A fresh 'supplier-specific sensitivity' would have been a free parameter that nothing
    outside this company could settle, sitting in the exact place a maximiser is about to read.
    The correction moves an EXISTING calibrated sensitivity onto the quantity it was always meant
    to describe.

    MUTATION (must fire): add one, and this fails by name.
    """
    added = [n for n in dir(cm) if "SUPPLIER" in n or "OWN_MOVE" in n or "SPECIFIC" in n]

    assert not added, f"a new free parameter appeared in the churn model: {added}"


# --------------------------------------------------------------------------- #
# Where the market move comes from                                             #
# --------------------------------------------------------------------------- #

def test_the_market_move_is_READ_from_the_published_cap_not_written_down():
    """The Default Tariff Cap is the one domestic price series a real supplier can look up
    without knowing anybody else's book. 2022 is the year it rose most; 2023 is a year it fell.

    MUTATION (must fire): hard-code a table of yearly moves. Then a cap revision stops moving it.
    """
    assert market_rate_move_pct(2022) > 0.5
    assert market_rate_move_pct(2023) < 0.0


def test_an_UNKNOWN_year_nets_NOTHING_rather_than_inventing_a_market_move():
    """FAIL-SOFT, deliberately: with no observation the only claim the company can make is that
    it does not know, and the safe expression of that is to degrade to the pre-existing model.
    Fabricating a move would let a missing cap year silently change every estimate.
    """
    assert market_rate_move_pct(None) == 0.0
    assert market_rate_move_pct(1990) == 0.0
    assert _p(0.5, market_move_pct=market_rate_move_pct(None)) == pytest.approx(_p(0.5))


def test_the_enriched_estimate_ACTUALLY_passes_the_market_move_down():
    """A control nobody reaches is a file. The finding this repairs was precisely a belief that
    was computed, published and consumed by no decision.

    MUTATION (must fire): stop passing `market_move_pct` from `enriched_churn_estimate`.
    """
    same_rise_2022 = enriched_churn_estimate(BASE_RATE, BASE_RATE * 1.6667, 4.0, 3100.0,
                                             renewal_year=2022)
    same_rise_2025 = enriched_churn_estimate(BASE_RATE, BASE_RATE * 1.6667, 4.0, 3100.0,
                                             renewal_year=2025)

    assert same_rise_2022 < same_rise_2025 / 2.0, (
        "a 66.7% rise in the year the cap itself rose 66.7% is being read as if this company "
        "had done it alone"
    )
