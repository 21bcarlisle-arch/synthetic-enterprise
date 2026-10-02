"""The renewal-point departure roll is skipped only for a household converting off the SVT.

Defect this catches: a household on the default tariff has two exit routes -- C1b's inertia hazard
on every SVT segment, and the renewal-point roll again when it converts to a fixed term at an
anniversary -- so SVT exits run above the all-cause band C1b is graded against.
"""
from simulation.customer_events import departure_rolled_at_renewal
from simulation.svt_product import SVT_TARIFF_TYPE


def test_only_an_svt_predecessor_skips_the_roll_and_every_other_predecessor_still_rolls():
    # One control over the whole partition: a gate that refuses everything fails the first two
    # legs, and a gate that refuses nothing fails the last.
    plan = {
        "first_term": departure_rolled_at_renewal(None),
        "fixed": departure_rolled_at_renewal("fixed"),
        "svt": departure_rolled_at_renewal(SVT_TARIFF_TYPE),
    }
    assert plan == {"first_term": True, "fixed": True, "svt": False}


def test_every_other_tariff_type_the_world_writes_still_rolls():
    for other in ("fixed", "deemed", "tou", "flex", "indexed"):
        assert departure_rolled_at_renewal(other) is True
