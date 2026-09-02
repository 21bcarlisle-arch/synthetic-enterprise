"""The defect: a supplier returning money read as an event identical to one taking money.

`bill_shock_pct` was `abs(this - previous) / abs(previous)`. Measured on the published record,
**5,161 of 11,255 bills carrying a shock (45.9%) are bills that went DOWN**, including catch-up
refunds, and each of them was charged the full `min(shock, 1.0) * BILL_SHOCK_PENALTY_FACTOR`
clarity penalty — which drives contact propensity, which drives satisfaction and churn.

The established definition says a shock is an INCREASE, for both populations
(`docs/market_research/what_bill_shock_is.md`): standard credit's three published triggers are
all upward, and the direct-debit triggers (the ±5% review band -- a modelling convention under the
SLC 27.15 duty, since there is no SLC 27B -- and Ofgem's >100% escalation cut)
are about a payment rise. Nothing published describes a household shocked by being asked less.

REUSE: `test_a_published_bill_shock_can_be_recomputed.py` owns the BASELINE and its
reproducibility, and its negative-baseline control was re-keyed to this property rather than
duplicated here. This file is the two things that control cannot reach: the definition function
itself, and the fact that the arithmetic now exists ONCE.
"""
import pytest

from saas.bill_generator import BILL_SHOCK_BASELINE_FLOOR_GBP, bill_movement

# --------------------------------------------------------------------------
# The definition
# --------------------------------------------------------------------------

def test_a_bill_that_fell_carries_no_shock_at_all():
    """THE CENTRAL CONTROL. A refund is not a shock of the same size as a demand.

    MUTATION (must fire): restore `abs()` on the numerator — `movement` becomes +0.20 and the
    bill that halved reports the same shock as the bill that doubled.
    """
    movement, shock, baseline = bill_movement(80.0, 100.0)
    assert movement == pytest.approx(-0.20), "the movement must carry the direction"
    assert shock is None, (
        "a bill that fell 20% reported a shock. That is a supplier returning money scored as "
        "an event that reduces clarity and raises contact propensity"
    )
    assert baseline == 100.0


def test_a_bill_that_fell_publishes_None_and_never_a_measured_zero():
    """THE NAIVE REPAIR, and it is the one worth a control of its own.

    `max(movement, 0.0)` is the one-line change that turns this file green while publishing
    `0.0` for 45.9% of the book. A measured zero enters every downstream mean and drags it
    toward a number no household experienced — this project's
    `a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`.

    MUTATION (must fire): `shock = max(movement, 0.0)`.
    """
    for total in (80.0, 50.0, 0.0, -30.0):
        _, shock, _ = bill_movement(total, 100.0)
        assert shock is None and shock != 0.0, (
            f"a bill of £{total} against £100 published a shock of {shock!r} rather than None"
        )


def test_a_bill_that_did_not_move_publishes_zero_because_that_IS_measured():
    """THE OTHER BRANCH, without which the control above is satisfiable by returning None for
    everything that is not an increase.

    A bill identical to the last one HAS been measured, and the answer is zero shock. Collapsing
    it to None would say "we cannot tell" about the one case we can tell about perfectly.
    """
    movement, shock, _ = bill_movement(100.0, 100.0)
    assert movement == 0.0 and shock == 0.0


def test_a_bill_that_rose_is_the_movement_with_no_transformation():
    movement, shock, _ = bill_movement(150.0, 100.0)
    assert movement == pytest.approx(0.50) and shock == movement


def test_a_negative_baseline_still_reads_the_direction_the_household_experienced():
    """The outage's own shape. An issued total can be negative (a catch-up credit), and 169 of
    this book's bills are. Going from a £100 CREDIT to a £50 charge is the household being asked
    for £150 more, so it is a rise — the denominator is a magnitude, the numerator is not.

    MUTATION (must fire): drop the `abs()` from the denominator. The sign inverts, so a rising
    bill reports None and a falling one reports a shock — the defect, upside down.
    """
    movement, shock, _ = bill_movement(50.0, -100.0)
    assert movement == pytest.approx(1.50) and shock == pytest.approx(1.50)

    movement, shock, _ = bill_movement(-150.0, -100.0)
    assert movement == pytest.approx(-0.50) and shock is None


def test_a_baseline_too_small_to_divide_by_refuses_all_three():
    """The floor stands, and it refuses the trio together — a movement without a baseline is a
    ratio a reader cannot check."""
    assert bill_movement(50.0, None) == (None, None, None)
    assert bill_movement(50.0, BILL_SHOCK_BASELINE_FLOOR_GBP - 0.01) == (None, None, None)
    assert bill_movement(50.0, -(BILL_SHOCK_BASELINE_FLOOR_GBP - 0.01)) == (None, None, None)
    assert bill_movement(50.0, BILL_SHOCK_BASELINE_FLOOR_GBP)[0] is not None, (
        "the floor must admit its own edge, or it is not the floor it declares"
    )


# --------------------------------------------------------------------------
# The guard that crashed the run is KEPT, not lifted
# --------------------------------------------------------------------------

def test_the_world_still_refuses_a_negative_shock_outright():
    """THE LOAD-BEARING ONE. `simulation.contact_propensity` refused -1.4434 on 2026-09-01 and
    took the publish cycle down with it for 75 minutes. The guard was RIGHT: a negative should
    never have reached it, and the repair belongs at the definition.

    Lifting the guard — or wrapping the consumer in `abs()` or `or 0` — is the repair that looks
    like resilience and reinstates the fold. This control exists so that repair cannot be made
    quietly: it asserts the guard is still there and still bites.

    MUTATION (must fire): remove the `shock < 0.0` clause from `_require`-style validation in
    `simulation/contact_propensity.py`.
    """
    from simulation.contact_propensity import contact_propensity

    with pytest.raises(ValueError, match="bill_shock_pct"):
        contact_propensity("SYN-2016-001", 0.7, -0.5)

    # And what the definition actually produces passes it, in both directions — otherwise this
    # control would be satisfied by a producer that never emits anything at all.
    for total in (150.0, 80.0):
        _, shock, _ = bill_movement(total, 100.0)
        contact_propensity("SYN-2016-001", 0.7, shock)


# --------------------------------------------------------------------------
# The arithmetic exists ONCE
# --------------------------------------------------------------------------

def test_the_catchup_recompute_does_not_carry_its_own_copy_of_the_definition():
    """`company.billing.monthly_bill_assembly` recomputed the shock in the same shape after
    folding a catch-up onto the bill. A catch-up REFUND is exactly the bill that branch runs on,
    so a sign fix made here and missed there would have left the defect live in the place it
    bites hardest — and this tree has already paid for that shape once, with one VAT rule in five
    implementations and a July fix still missing from one of them in August.

    Keyed to the property (the definition is imported, not restated), not to today's source: it
    stays green if the recompute is rewritten and reds if it grows a second copy.

    MUTATION (must fire): restore the inline
    `abs(bill["total_amount_gbp"] - previous_bill_total_gbp) / abs(previous_bill_total_gbp)`.
    """
    import inspect

    from company.billing import monthly_bill_assembly

    source = inspect.getsource(monthly_bill_assembly)
    assert "bill_movement(" in source, (
        "the catch-up recompute no longer calls the shared definition"
    )
    assert "/ abs(previous_bill_total_gbp)" not in source, (
        "the catch-up recompute has grown its own copy of the shock arithmetic again"
    )
