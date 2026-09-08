"""A turn-down is refused below the health floor, and it is refused rather than priced.

REUSE: tests/company/test_turn_down_respects_the_health_floor.py
CLASS: CUSTOM
INDEX: searched "turn down", "health floor", "fabric intervention", "offer book", "comfort".
       `tests/company/test_fabric_intervention*.py` cover the three existing declines and the
       ranking; none of them knows about a zero-capital measure, because until now there was not
       one. `company/crm/vulnerability_register.py` is a different subject -- who a supplier must
       treat carefully, not what physics permits recommending.

THE DEFECT THIS EXISTS FOR, AND THE DESIGN IT REFUSES
------------------------------------------------------
Every measure in the offer book cost the customer at least £300, so the company could recommend
spending money and nothing else -- while the mission's third leg is ADVICE. A one-degree turn-down
is worth real energy at no capital, which is exactly what a household with no capital can act on.

**The obvious implementation is the dangerous one.** Enter it at zero capex against a priced
comfort cost and it wins every ranking for every household, including the coldest. Director,
refusing that design on 2026-09-08:

    "A comfort cost makes warmth a willingness-to-pay question, and the households that would
     accept the trade are the ones who can least afford to refuse it, so the model would find the
     fuel-poor and recommend they be cold."

So comfort is FLOORED, not priced. A floor cannot be bought off by a large enough saving; a price
can. `test_NO_SAVING_HOWEVER_LARGE_BUYS_A_TURN_DOWN_BELOW_THE_FLOOR` is the control for exactly
that distinction, and it is the one that would catch a well-meaning refactor turning the floor
back into a term.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from company.pricing.fabric_intervention import (  # noqa: E402
    DO_NOTHING,
    EFUS_INTERNAL_TEMPERATURE_BY_EPC_C,
    HEALTH_FLOOR_INDOOR_C,
    OFFER_BOOK,
    TURN_DOWN_SETPOINT_C,
    Decision,
    decide,
    turn_down_clears_the_health_floor,
)

_ARGS = dict(
    hlc_pessimistic_kw_per_k=0.195,
    actionable=True,
    annual_heat_kwh=12_000.0,
    annual_degree_days_k_day=2_200.0,
)


def _decide(band, *, rate=7.4):
    return decide("P-1", 0.20, unit_rate_p_per_kwh=rate, epc_band=band, **_ARGS)


def test_NO_SAVING_HOWEVER_LARGE_BUYS_A_TURN_DOWN_BELOW_THE_FLOOR():
    """THE CONTROL THAT DISTINGUISHES A FLOOR FROM A PRICE.

    A priced comfort cost is beaten by a big enough saving; a floor is not. This drives the unit
    rate to an absurd height -- which is the only lever that can make any measure look
    attractive, since savings are counted in kWh and only the rate converts them to pounds -- and
    asserts the cold household is STILL not offered a turn-down.

    If this ever goes green with `turn_down` present, comfort has become a term again."""
    for rate in (7.4, 100.0, 10_000.0):
        recommendation = _decide("F", rate=rate)
        offered = [name for name, _ in recommendation.ranked]
        assert "turn_down" not in offered, (
            f"at {rate} p/kWh an EPC F household -- measured at "
            f"{EFUS_INTERNAL_TEMPERATURE_BY_EPC_C['F']} C, already below the "
            f"{HEALTH_FLOOR_INDOOR_C} C floor -- was offered a turn-down. A floor that a large "
            "enough saving can cross is a price.")
        assert recommendation.zero_capital_measure is None


def test_THE_COLDEST_HOUSEHOLDS_ARE_THE_ONES_REFUSED():
    """The direction matters as much as the rule. A naive zero-cost measure targets the worst
    homes hardest, because they have the most heat to lose -- so the control asserts the refusal
    lands on exactly those, and not on the warm ones."""
    refused = [b for b in "ABCDEFG" if not turn_down_clears_the_health_floor(b)[0]]
    allowed = [b for b in "ABCDEFG" if turn_down_clears_the_health_floor(b)[0]]
    assert refused, "no band is refused — the floor is not biting anywhere"
    assert allowed, "every band is refused — the measure can never be offered at all"
    coldest = min(EFUS_INTERNAL_TEMPERATURE_BY_EPC_C[b] for b in refused)
    warmest_refused = max(EFUS_INTERNAL_TEMPERATURE_BY_EPC_C[b] for b in refused)
    coldest_allowed = min(EFUS_INTERNAL_TEMPERATURE_BY_EPC_C[b] for b in allowed)
    assert coldest_allowed > warmest_refused, (
        "a household is allowed a turn-down while a WARMER one is refused, so the rule is not "
        f"ordered by temperature (coldest refused {coldest:.2f}C, coldest allowed "
        f"{coldest_allowed:.2f}C)")


def test_AN_UNKNOWN_BAND_FAILS_CLOSED():
    """Absent evidence is not evidence of a warm home. A supplier that cannot establish the
    household is above the floor does not get to assume it is."""
    for band in (None, "", "   ", "X", "unknown"):
        allowed, note = turn_down_clears_the_health_floor(band)
        assert not allowed, f"band {band!r} was allowed a turn-down on no evidence"
        assert note, "the refusal carries no reason, so nobody can discover it was wrong"


def test_A_REFUSED_HOUSEHOLD_STILL_GETS_A_RECOMMENDATION_and_it_names_the_fabric():
    """The floor filters the CHOICE SET, not the premise. A cold household is not told 'no' --
    it is told the fabric needs work, which is the actual finding for it."""
    recommendation = _decide("F")
    assert recommendation.decision is Decision.RECOMMEND
    assert recommendation.measure != DO_NOTHING
    assert "fabric needs work" in recommendation.zero_capital_note.lower()


def test_A_WARM_HOUSEHOLD_IS_OFFERED_IT_AND_IT_IS_SURFACED_SEPARATELY():
    """Ranking by lifetime value buries a one-year behaviour change under a 30-year measure, so a
    household that cannot spend £6,000 would be told nothing it can act on. The zero-capital
    answer is carried in its own field for that reason."""
    recommendation = _decide("C")
    assert recommendation.zero_capital_measure == "turn_down"
    assert OFFER_BOOK["turn_down"].capex_gbp == 0.0
    # And it is genuinely surfaced BESIDE a better-scoring capital measure rather than instead
    # of it -- the point is that both reach the customer.
    assert recommendation.measure != "turn_down"


def test_THE_OFFER_BOOK_CONTAINS_A_ZERO_CAPITAL_MEASURE():
    """Keyed to the MISSION's advice leg, not to today's catalogue. Every route to a customer's
    bill running through their capital is no use to the households that need it most, and this
    goes red if the book reverts to one that only knows how to spend the customer's money."""
    free = [o.name for o in OFFER_BOOK.values() if o.capex_gbp <= 0.0]
    assert free, (
        "the offer book has no zero-capital measure. Every piece of advice the company can give "
        "would cost the customer money, which the mission's 'advice' leg is not.")


def test_THE_TURN_DOWN_IS_A_DEMAND_REDUCTION_AND_NOT_A_FABRIC_ONE():
    """A thermostat does not change a building. Keeping the two as separate parameters is what
    stops a behaviour being summed with an insulation measure by accident."""
    offer = OFFER_BOOK["turn_down"]
    assert offer.demand_reduction_fraction > 0.0
    assert offer.hlc_reduction_fraction == 0.0, (
        "the turn-down is declared as reducing the heat-loss coefficient, which would mean "
        "turning a thermostat down insulates the house")
    assert offer.lifetime_years == pytest.approx(1.0), (
        "a thermostat setting is a choice that can be undone the same afternoon; valuing it over "
        "an insulation lifetime lets a behaviour outrank a building fabric")


def test_THE_QUOTED_SAVING_IS_THE_CAUTIOUS_PUBLISHED_ONE_not_the_degree_day_upper_bound():
    """Where the physics and the field disagree about a number a CUSTOMER acts on, the company
    quotes the field, at its cautious end.

    Measured over the HadUK-Grid normals for all 245,077 GB land cells, a one-degree drop removes
    11.7% of annual degree-days at an 18 C base and 14.3% at 15.5 C. That is an upper bound for a
    continuously-heated house; real heating is intermittent. Overstating a saving to a household
    that then does not see it is a mis-selling harm."""
    fraction = OFFER_BOOK["turn_down"].demand_reduction_fraction
    assert 0.04 <= fraction <= 0.10, (
        f"the quoted turn-down saving is {fraction:.1%}. The published field range is 6-10%; "
        "the degree-day arithmetic says 11.7-14.3% and is an upper bound that must not be "
        "quoted to a customer.")
    assert fraction < 0.117, (
        "the quoted saving has reached the degree-day upper bound, so the model is promising a "
        "continuously-heated house's saving to a household that heats intermittently")


def test_TURN_DOWN_SETPOINT_IS_FIXED_and_not_optimised_per_household():
    """A household-specific optimum would be a turn-down computed to the edge of the floor, which
    is the priced-comfort design under another name."""
    assert TURN_DOWN_SETPOINT_C == pytest.approx(1.0)
