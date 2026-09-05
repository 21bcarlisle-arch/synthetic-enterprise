"""PB6: the antecedent the world carries reaches the company, and changes what it believes.

PB4 made engagement recoverable IN THE WORLD. This is the other half: a trait that is learnable and
invisible at the wall satisfies the letter of R1's claim and none of its point.

Each test names the defect it exists to catch.
"""
from __future__ import annotations

import inspect

from company.crm.enriched_churn_estimate import (
    enriched_churn_estimate,
    payment_method_engagement_factor,
)
from company.interfaces.sim_interface import LiveSimInterface, StubSimInterface


def test_the_seam_carries_the_payment_method_and_it_varies_by_household():
    """THE DEFECT: `sim_interface` carried no payment method at all, so the company could not see
    its own billing arrangement.

    Varying MATTERS as much as crossing: a seam that returned one method for every account would
    pass a "does it cross" test while making every downstream decision constant.
    """
    live = LiveSimInterface()
    methods = {live.get_payment_method(f"CUST{i:05d}") for i in range(400)}

    assert methods <= {"direct_debit", "standard_credit", "prepayment"}, methods
    assert len(methods) == 3, f"the seam must carry all three channels, saw {methods}"


def test_the_seam_agrees_with_the_world_rather_than_drawing_its_own():
    """A seam that redrew the trait would hand the company a household that does not exist.

    This is not hypothetical here: the tree already holds TWO independent draws of a household's
    payment method (`household_segments` and `payment_behaviour_source`) which agree on only 58.8%
    of households, exactly what chance gives. A third would have been worse than either.
    """
    from simulation.household_segments import payment_channel_for_customer

    live = LiveSimInterface()
    for i in range(200):
        cid = f"CUST{i:05d}"
        assert live.get_payment_method(cid) == payment_channel_for_customer(cid).value


def test_a_lookup_failure_falls_to_the_majority_channel_and_not_to_prepayment():
    """FAIL-SAFE DIRECTION, chosen deliberately and asserted because it is a judgement call.

    A CRM record the supplier cannot resolve is a broken record, not an unknown customer -- it
    still bills them. Falling to prepayment would silently move a household into BOTH the
    vulnerability score's +10 band and the low-engagement band on a lookup error.
    """
    live = LiveSimInterface()
    # An id the world's draw cannot resolve at all.
    assert live.get_payment_method(None) == "direct_debit"  # type: ignore[arg-type]


def test_the_stub_can_be_made_to_vary_so_a_consumer_can_be_tested_at_all():
    stub = StubSimInterface()
    assert stub.get_payment_method("A") == "direct_debit"
    stub._payment_methods["A"] = "prepayment"
    assert stub.get_payment_method("A") == "prepayment"


def test_the_companys_churn_belief_actually_moves_with_the_observable():
    """DONE MEANS THE ANSWER CHANGED. An observable the company receives and does not use is the
    `no_caller_and_never_runs` class wearing a seam's clothes -- and this seam was built precisely
    because `vulnerability_index.assess_vulnerability` already takes a `has_ppm` argument and has
    no caller anywhere in the tree.
    """
    args = (100.0, 115.0, 2.0, 3000.0)
    dd = enriched_churn_estimate(*args, payment_method="direct_debit")
    ppm = enriched_churn_estimate(*args, payment_method="prepayment")

    assert ppm < dd * 0.75, (
        f"prepayment ({ppm:.4f}) must read as materially less likely to leave than direct debit "
        f"({dd:.4f}) -- Ofgem CIM w6 puts them at 3.1% and 5.6%"
    )


def test_a_caller_that_does_not_pass_a_method_is_bit_for_bit_unchanged():
    """The other branch, and the one that protects every existing caller. Without it the factor
    could apply a blanket uplift to the whole book and the test above would still pass."""
    args = (100.0, 115.0, 2.0, 3000.0)

    assert payment_method_engagement_factor(None) == 1.0
    assert payment_method_engagement_factor("a method nobody has heard of") == 1.0
    assert enriched_churn_estimate(*args) == enriched_churn_estimate(*args, payment_method=None)


def test_the_company_reads_the_published_statistic_and_not_the_worlds_parameter():
    """THE WALL QUESTION, asked of the thing that would be easiest to get wrong here.

    The company is entitled to Ofgem's published CIM survey -- a regulator's public statistic is
    exactly what a real supplier reads. It is NOT entitled to `simulation.household_segments`'s own
    `CIM_SWITCH_RATE_BY_CHANNEL`, even though the two carry the same numbers from the same source:
    importing the world's copy would make the company's belief move whenever the WORLD's parameter
    moved, which is the company reading ground truth by a side channel.
    """
    source = inspect.getsource(
        __import__("company.crm.enriched_churn_estimate", fromlist=["x"])
    )
    assert "simulation" not in source and "from sim" not in source, (
        "the company's churn model must not reach into the world for this figure"
    )
