"""Controls on the size dimension of the company's churn belief — `tools/churn_belief_size_response.py`.

The defect this file was written for is
`SEAT_RESULT_THE_COMPANYS_CHURN_BELIEF_IS_FLAT_IN_THE_DIMENSION_THE_WORLD_RESPONDS_TO_2026-09-22.md`:
`estimate_churn_probability` reads `annual_consumption_kwh` in exactly one place, a bill-stress
hinge that is identically zero below GBP 3,000 of previous annual bill, so the belief's derivative
with respect to household size is exactly zero across almost the whole book — while the world's
`churn_position_multiplier` scales by each household's OWN annual spend and spans an order of
magnitude over those same accounts.

WHY ONE CONTROL OVER THE WHOLE PARTITION AND NOT A LEG PER CLAIM. The claim being published is
"the belief is flat here". An instrument that returns a constant for EVERY input satisfies that
claim at every point and would pass any number of individually-correct flatness legs — this
project's most expensive recurring shape, entered three times in one afternoon through three
different doors. So the partition is asserted in one function: flat below the knee, MOVING above
it, the world varying below it where the belief does not, and the world flat above it for the one
segment where the belief varies. A guard that reports "flat" for everything fails the second leg;
a guard that reports "varies" for everything fails the first; an instrument that has stopped
reading the world at all fails the third.

MUTATION RECORD (2026-09-22), per `docs/design/CONTROLS_THAT_CANNOT_FAIL.md`. Each mutation was
applied to an INJECTED copy of the subject module, never to the shared tree, and an unmutated
baseline run is recorded first so a leg that fires on everything would be visible:

  * baseline, no mutation — SILENT. Nothing fires without a mutation.
  * `BILL_STRESS_SENSITIVITY = 0.25 -> 0.0` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 3) and by
    `test_the_knee_is_a_bill_and_not_a_consumption`. The belief goes flat at every consumption,
    so the partition collapses AND `knee_kwh` correctly returns None at every rate.
  * `BILL_STRESS_THRESHOLD_GBP = 3000.0 -> 500.0` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 1) alone. The knee drops
    below the probe pair and the two domestic households stop agreeing. The knee control does NOT
    fire, and correctly so: a knee at GBP 500 is still a bill and still moves in kWh with rate.
  * `max(0.0, ...) -> abs(...)` in `churn_model`'s bill-stress line — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 1) and by
    `test_the_knee_is_a_bill_and_not_a_consumption`. A two-sided hinge makes the belief vary below
    the knee, and leaves no flat arm for the bisection to find.
  * `bill_scale_for` non-domestic branch `None -> bill_gbp` — CAUGHT by
    `test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` (leg 4). This is the leg that
    stops the mirror claim being asserted about a world that no longer has the asymmetry.
  * `PROBE_DIFFERENTIAL_PCT = 0.12 -> 0.30` — SILENT, and it is an EQUIVALENCE, not a missing leg.
    Every world leg here is a strict comparison BETWEEN two bills at ONE differential, and
    `churn_position_multiplier` is monotone in the bill at any positive differential, so the
    ordering asserted is invariant to where the probe sits. Recorded rather than patched: pinning
    the probe position would key the control to today's answer instead of to the property, which
    is the failure mode named in CLAUDE.md.
  * `_KNEE_TOLERANCE_KWH = 1.0 -> 100.0` — SILENT, and it is an EQUIVALENCE for these legs: the
    knee control asserts the derived knee is a BILL (one figure across three rates, to within GBP
    10) and a coarser bisection still resolves that well inside the bar. It is NOT an equivalence
    for the precision of `knee.by_rate[].knee_kwh`, which no leg here reads — so the honest
    statement is that this control does not cover the bisection's precision and does not claim to.
"""
from __future__ import annotations

import pytest

from company.crm.enriched_churn_estimate import enriched_churn_estimate
from simulation.market_switching_propensity import bill_scale_for, churn_position_multiplier
from tools import churn_belief_size_response as cb

#: The probe deck. GBP 250/MWh puts the knee at 12,000 kWh, so both "below" households are real
#: domestic sizes and the "above" one is the item's own 25,000 kWh probe.
_OLD_RATE = 250.0
_OFFER = 280.0
_SMALL_KWH = 1_500.0
_LARGE_KWH = 6_000.0
_ABOVE_KNEE_KWH = 25_000.0


def _belief(kwh: float, segment: str = "resi") -> float:
    return enriched_churn_estimate(_OLD_RATE, _OFFER, 3.0, kwh, segment=segment)


def _world(kwh: float, segment: str = "resi") -> float:
    bill = _OLD_RATE * kwh / 1000.0
    return churn_position_multiplier(cb.PROBE_DIFFERENTIAL_PCT, bill_scale_for(segment, bill))


def test_the_belief_is_flat_in_size_exactly_where_the_world_is_not():
    """The whole partition. Catches a belief that is flat everywhere AND one that varies everywhere.

    Four legs, and each one kills a different degenerate instrument:
      1. flat below the knee          -- the finding itself
      2. the world varies there       -- so the flatness is a real difference, not an equivalence
      3. the belief MOVES above it    -- so "flat" is not what this instrument says about everything
      4. the world is flat for SME    -- so the mirror claim is about a world that has the asymmetry
    """
    # 1. Two domestic households, four times apart in size, both below the knee. The company's
    #    belief cannot tell them apart -- not approximately, exactly.
    assert _belief(_SMALL_KWH) == _belief(_LARGE_KWH)

    # 2. And that is a difference the world makes, in the direction size predicts. Without this
    #    leg the flatness could be an equivalence -- two routes to one correct answer.
    assert _world(_SMALL_KWH) < _world(_LARGE_KWH)

    # 3. The belief is NOT constant in consumption at every input: above the knee it moves. An
    #    estimator that had stopped reading consumption altogether fails here, which is what stops
    #    leg 1 from being passed by a guard that reports "flat" for everything.
    assert _belief(_ABOVE_KNEE_KWH) > _belief(_LARGE_KWH)

    # 4. The mirror, and it is the sharper half of the finding: the world scales by the
    #    household's own bill for DOMESTIC supply only, so for a non-domestic account the world is
    #    flat in size by construction -- and that is the one segment where the belief does vary.
    assert _world(_SMALL_KWH, "SME") == _world(_ABOVE_KNEE_KWH, "SME")
    assert _belief(_ABOVE_KNEE_KWH, "SME") > _belief(_SMALL_KWH, "SME")


def test_the_knee_is_a_bill_and_not_a_consumption():
    """Keyed to the PROPERTY, not to 12,000 kWh — which is only the knee at GBP 250/MWh.

    A control pinned to the kWh location goes red the next time the price deck moves and stays
    green while the mechanism rots. What is durable is that the knee sits at a fixed number of
    POUNDS and therefore at a DIFFERENT number of kilowatt-hours at every rate.
    """
    derived = [cb.knee_kwh(rate) for rate in cb.PROBE_RATES_GBP_PER_MWH]
    assert all(kwh is not None for kwh in derived), "the belief never moves at any consumption"

    bills = [rate * kwh / 1000.0
             for rate, kwh in zip(cb.PROBE_RATES_GBP_PER_MWH, derived)]
    # One bill, to within the bisection's own resolution.
    assert max(bills) - min(bills) < 10.0
    # Three different consumptions. This is the leg that fails if the knee ever becomes a kWh
    # constant -- at which point the belief WOULD be a size term and this finding would be spent.
    assert len(set(round(kwh) for kwh in derived)) == len(derived)
    assert max(derived) / min(derived) > 2.0


def test_the_book_census_counts_every_leg_on_one_side_or_the_other():
    """A census whose filters empty the evidence reads as 'no complaint'. This asserts it did not.

    `share_below_the_knee` is the published figure; a census that dropped the accounts it could
    not classify would report a clean share over a population it had quietly shrunk.
    """
    import json

    book = json.loads(cb.BOOK_PATH.read_text(encoding="utf-8"))
    dist = cb.book_distribution(book, 3000.0)
    assert dist["available"]
    assert dist["supply_legs"] > 0
    assert dist["legs_above_the_knee"] + dist["legs_below_the_knee"] == dist["supply_legs"]
    # BOTH sides are populated. A book entirely below the knee would make leg 3 of the partition
    # control unreachable on real data, and saying "the belief is flat across the book" would then
    # be unfalsifiable rather than measured.
    assert dist["legs_above_the_knee"] > 0
    assert dist["legs_below_the_knee"] > 0
    # The claim the page publishes is about the MAJORITY, so the census must be able to say which.
    assert 0.0 < dist["share_below_the_knee"] <= 1.0


def test_the_reading_refuses_rather_than_reporting_an_absence():
    """A refusal that names its reason, per the standing rule. Reachable, not decorative."""
    empty = cb.book_distribution({"customers": []}, 3000.0)
    assert empty["available"] is False
    reading = cb._reading(cb.knee(), cb.partition(), empty)
    assert reading.startswith("REFUSED:")


@pytest.mark.parametrize("field", ["population_is_not_the_published_arms_book",
                                   "bill_is_an_upper_bound"])
def test_the_census_carries_what_it_could_not_establish(field):
    """The 154-account arms book is not this book, and the bill here is an upper bound.

    Both caveats are load-bearing: the first is the difference `generate_value_arms_data` already
    refuses to smooth over, and the second is what makes the below-the-knee count safe in the
    direction it is claimed.
    """
    import json

    book = json.loads(cb.BOOK_PATH.read_text(encoding="utf-8"))
    assert cb.book_distribution(book, 3000.0)[field].strip()
