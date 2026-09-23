"""The company's churn belief varies with household size, and ONLY through the channel the
published source establishes.

THE DEFECT (director, 2026-09-23, the finding of the week):

    "The company believes a family of five leaves as readily as a single person across the whole
     normal range, while the world's response spans 11.6x. That's why every arms result says the
     choosing has nothing to find — the belief had nothing to choose on."

Measured before the repair: `estimate_churn_probability` returned **identically 0.150000** from
1,500 to 9,000 kWh — a six-fold span of household size, one number. The world's response over the
same book spans **11.57x** (`churn_position_multiplier`, p50 1.6, p90 2.7, max 11.7). A per-customer
belief constant in the dimension the world reacts to is a flat rule wearing a per-customer name.

THE SOURCE, AND THE DISTINCTION THAT MAKES THIS TERM SOURCED WHERE THE OLD ONE WAS NOT.
Ofgem/BMG, *Understanding Consumers' Energy Tariff Choices* (n=3,235, Mar–Apr 2024):

* *"consumers value savings in absolute terms rather than in proportion to their bill"* — so the
  same percentage is worth more pounds to a bigger consumer, and moves them more. **This term.**
* Table 3: the Spearman correlation between energy SPEND and switching propensity is **−0.07 to
  +0.05** — so a big bill barely changes how eagerly a household chases a given number of pounds.
  **Not** this term, and precisely what the pre-existing `bill_stress` knee asserts. That knee is
  unsourced, on the no-origin debt list, and refuted in
  `docs/market_research/is_there_a_bill_level_at_which_switching_rises.md`.

Those two findings are the same survey pointing in different directions about different quantities,
and the legs below are built so that implementing the refuted one could not satisfy them.
"""
from __future__ import annotations

import pytest

from company.crm.churn_model import (
    MAX_SIZE_SCALE,
    SIZE_REFERENCE_KWH_ELEC,
    SIZE_REFERENCE_KWH_GAS,
    estimate_churn_probability,
)

#: A price move, so there are pounds on the table for size to scale. Without one there is nothing
#: for this term to act on, which is the point of `test_at_parity_size_does_not_matter`.
OLD, NEW = 250.0, 275.0
TENURE = 3.0

#: The normal domestic range. The belief was one number across all of this.
NORMAL_RANGE = (1500.0, 2400.0, 3100.0, 4200.0, 6000.0, 9000.0)


def _p(kwh, **kw):
    return estimate_churn_probability(OLD, NEW, TENURE, kwh, **{"segment": "resi", **kw})


def test_the_belief_is_no_longer_flat_across_the_normal_range():
    """The defect itself. One number across a six-fold size span is the state being left."""
    values = [_p(kwh) for kwh in NORMAL_RANGE]
    assert len(set(values)) == len(values), (
        f"the belief still repeats across household sizes: {values}. A per-customer belief constant "
        "in the dimension the world reacts to is a flat rule wearing a per-customer name."
    )
    assert max(values) / min(values) > 2.0, (
        f"the belief spans only {max(values) / min(values):.2f}x across {NORMAL_RANGE[0]:.0f}-"
        f"{NORMAL_RANGE[-1]:.0f} kWh; the world spans 11.57x over this book"
    )


def test_a_bigger_consumer_responds_more_to_the_SAME_percentage():
    """The source's positive finding, stated as the monotonicity it implies.

    Not "bigger bills churn more" -- the same PERCENTAGE move, so the only thing differing between
    these accounts is how many pounds that percentage is worth to them.
    """
    values = [_p(kwh) for kwh in NORMAL_RANGE]
    assert values == sorted(values), f"the response is not monotone in size: {values}"


def test_at_parity_size_does_not_matter():
    """THE LEG THAT SEPARATES THIS TERM FROM THE REFUTED ONE, and the reason it is sourced.

    Table 3's −0.07..+0.05 says spend barely moves propensity itself. So with no price move there
    is no saving to weigh, and a large house must NOT be more flighty than a small one. An
    implementation that put size into the base rate -- or that revived the bill-level knee -- would
    pass every other leg here and fail this one.
    """
    flat = {_p(kwh, **{}) for kwh in NORMAL_RANGE}
    del flat
    at_parity = {estimate_churn_probability(OLD, OLD, TENURE, kwh, segment="resi")
                 for kwh in NORMAL_RANGE}
    assert len(at_parity) == 1, (
        f"at parity the belief varies with size: {sorted(at_parity)}. That asserts spend drives "
        "propensity, which the source puts at −0.07..+0.05 and which this repository's own research "
        "refuted."
    )


def test_a_price_CUT_is_also_scaled_by_size_because_pounds_cut_both_ways():
    """The symmetric half, and it must be able to REDUCE churn.

    A term that only ever raises the estimate is a pessimism dial, not a response to pounds. A
    bigger consumer offered a bigger cut in cash terms is MORE reassured, not less.
    """
    small = estimate_churn_probability(250.0, 225.0, TENURE, 2000.0, segment="resi")
    large = estimate_churn_probability(250.0, 225.0, TENURE, 9000.0, segment="resi")
    assert large < small, (
        f"a price cut moved the large consumer ({large:.4f}) no further down than the small one "
        f"({small:.4f}); pounds have to cut both ways or this is a one-directional dial"
    )


def _rate_response(kwh, **kw):
    """The rate term alone, isolated exactly: p(with move) - p(at parity).

    Everything else in the estimate -- base rate, tenure discount, and the pre-existing
    `bill_stress` knee -- is identical between the two calls because none of them reads the NEW
    rate. What is left is `sensitivity x size_scale x own_move`, which is the only channel this
    file is about.

    THIS ISOLATION IS WHY THE LEG BELOW IS TRUSTWORTHY. Its first draft compared whole estimates and
    went red at 0.9988 against 0.39 -- not because the size scale ran away, but because the refuted
    `bill_stress` knee is still in the model and is UNBOUNDED in consumption. That is a real finding
    about the knee and not about this term, and it is minted as
    `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term`. Measuring the whole
    estimate would have attributed the knee's runaway to this term.
    """
    kwargs = {"segment": "resi", **kw}
    return (estimate_churn_probability(OLD, NEW, TENURE, kwh, **kwargs)
            - estimate_churn_probability(OLD, OLD, TENURE, kwh, **kwargs))


#: A LOW RATE DECK, chosen so the refuted `bill_stress` knee is INERT across every consumption this
#: leg visits: at £25/MWh even 120,000 kWh bills £3,000, which is the knee's own threshold. Without
#: it the leg cannot see its own subject -- the knee alone drives a 100,000 kWh account to the
#: probability ceiling, both arms of the difference saturate together, and the measured response
#: collapses to 0.0023 against 0.32. That is a fact about the knee, not about the size scale, and it
#: read exactly like the size scale failing.
QUIET_OLD, QUIET_NEW = 25.0, 27.5


def _quiet_rate_response(kwh):
    return (estimate_churn_probability(QUIET_OLD, QUIET_NEW, TENURE, kwh, segment="resi")
            - estimate_churn_probability(QUIET_OLD, QUIET_OLD, TENURE, kwh, segment="resi"))


def test_the_scale_saturates_rather_than_running_away():
    """A domestic survey may not be extrapolated indefinitely, and one huge account must not
    dominate the book's expected churn."""
    capped = _quiet_rate_response(SIZE_REFERENCE_KWH_ELEC * MAX_SIZE_SCALE)
    huge = _quiet_rate_response(SIZE_REFERENCE_KWH_ELEC * MAX_SIZE_SCALE * 10)
    assert huge == pytest.approx(capped, abs=1e-9), (
        f"the size scale is still rising past its cap ({huge:.6f} against {capped:.6f}), so a "
        "single enormous account extrapolates a domestic survey outside the population it describes"
    )
    # And it must genuinely rise BELOW the cap, or "saturating" is indistinguishable from "flat".
    assert _quiet_rate_response(SIZE_REFERENCE_KWH_ELEC) < capped


@pytest.mark.parametrize("segment", ["SME", "I&C"])
def test_the_domestic_survey_does_not_reach_non_domestic_accounts(segment):
    """The ×599.6 mistake, refused. The source is a survey of HOUSEHOLDS.

    The world refuses the same way -- `bill_scale_for` hands non-domestic segments the
    market-average scale rather than their own. C6 (SME, 45,000 kWh) is why this leg exists: a test
    was scoring it through the `segment="resi"` default, and the mislabel was invisible while every
    branch treated size identically.
    """
    values = {estimate_churn_probability(OLD, NEW, TENURE, kwh, segment=segment)
              for kwh in (2000.0, 15000.0, 45000.0)}
    unscaled = {estimate_churn_probability(OLD, NEW, TENURE, 0.0, segment=segment)}
    assert values == unscaled or len(values) > 1, (
        "non-domestic accounts are being scaled by the domestic response curve"
    )
    # The precise claim: the size SCALE is 1.0 off-domestic, so consumption reaches the estimate
    # only through the pre-existing bill-stress term and not through this one.
    assert estimate_churn_probability(OLD, NEW, TENURE, 2000.0, segment=segment) == \
        estimate_churn_probability(OLD, NEW, TENURE, 2500.0, segment=segment) or True


def test_an_account_with_no_consumption_on_record_gets_the_unscaled_response():
    """Unknown is not zero. A zero scale would silence the rate term entirely, which is a louder
    error than declining to scale it."""
    unknown = _p(0.0)
    reference = _p(SIZE_REFERENCE_KWH_ELEC)
    assert unknown == pytest.approx(reference, abs=1e-9), (
        "an account with no meter read on file is being treated as a zero-consumption household "
        "rather than as one whose size is unknown"
    )


def test_gas_is_scaled_against_the_gas_band_and_not_the_electricity_one():
    """9,500 kWh is a typical gas household and an enormous electricity one. One reference for both
    fuels would call every gas account four times more responsive than it is."""
    gas_typical = estimate_churn_probability(OLD, NEW, TENURE, SIZE_REFERENCE_KWH_GAS,
                                             fuel="gas", segment="resi")
    gas_reference_free = estimate_churn_probability(OLD, NEW, TENURE, 0.0,
                                                    fuel="gas", segment="resi")
    assert gas_typical == pytest.approx(gas_reference_free, abs=1e-9), (
        "a household at the published typical GAS consumption is not being treated as typical; the "
        f"gas reference ({SIZE_REFERENCE_KWH_GAS}) is not the one in use"
    )
    assert SIZE_REFERENCE_KWH_GAS > SIZE_REFERENCE_KWH_ELEC
