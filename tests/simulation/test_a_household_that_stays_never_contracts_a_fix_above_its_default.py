"""A household that stays never contracts a fix above the default it would otherwise pay.

The defect each test names: the world could not refuse a price. Before this rule, an SVT conversion
accepted any offer unconditionally, so 16 of 40 value-arm conversions sat above the default with
renewals capped (36 of 38 uncapped), and a margin the world cannot refuse is transfer, not value.

Pre-registration: docs/staging/records/
WORKER_PREREG_A_HOUSEHOLD_THAT_STAYS_NEVER_CONTRACTS_A_FIX_ABOVE_ITS_DEFAULT_2026-10-02.md
"""
import ast
import inspect

import pytest

import simulation.run_phase2b as p2b
from simulation.customer_events import (
    DEPARTURE_OCCASION_DECLINED_FIX,
    RENEWAL_ACCEPTED,
    RENEWAL_CHURNED,
    RENEWAL_DECLINED_FIX,
    declined_fix_event,
    position_vs_default,
    renewal_outcome,
)

# Offers at known positions against the default: below, at parity, above, and "rule not applied".
_FIXTURE = [
    ("renewed", -0.10),
    ("renewed", 0.0),
    ("renewed", 0.25),
    ("renewed", None),
    ("churned", 0.25),
    ("churned", -0.10),
]


def test_every_outcome_of_the_partition_is_reached_and_each_is_the_right_one():
    """The decline branch exists to be taken rarely in a capped world, so first assert it CAN be
    taken, alongside the other two, before asserting what each does. A rule that declined nothing
    (or everything) fails the first assertion, not a leg further down."""
    outcomes = [renewal_outcome(event_type=e, position_vs_default=p) for e, p in _FIXTURE]
    assert set(outcomes) >= {RENEWAL_ACCEPTED, RENEWAL_DECLINED_FIX, RENEWAL_CHURNED}
    assert outcomes == [
        RENEWAL_ACCEPTED,       # below the default: the fix is worth taking
        RENEWAL_ACCEPTED,       # at parity: no worse than doing nothing, so no refusal
        RENEWAL_DECLINED_FIX,   # above it: staying on the default dominates
        RENEWAL_ACCEPTED,       # rule not applied (off / not domestic / not fixed): never declines
        RENEWAL_CHURNED,        # a departure already rolled stands, whatever the offer
        RENEWAL_CHURNED,
    ]


def test_a_declined_fix_is_a_household_that_stayed_and_contracted_nothing():
    # Shaped as `roll_lifecycle_event` writes it: no `departure_rolled` key.
    rolled = {"customer_id": "C1", "event_type": "renewed", "departure_occasion": "renewal",
              "random_roll": 0.7, "unit_rate_gbp_per_mwh": 300.0}
    from_roll = declined_fix_event(
        customer_id="C1", event_date="2018-01-01", commodity="electricity",
        declined_unit_rate_gbp_per_mwh=300.0, position_vs_default=0.2, rolled_event=rolled,
    )
    unrolled = declined_fix_event(
        customer_id="C1g", event_date="2018-01-01", commodity="gas",
        declined_unit_rate_gbp_per_mwh=80.0, position_vs_default=0.1,
    )
    for ev in (from_roll, unrolled):
        assert ev["event_type"] == "renewed"
        assert ev["departure_occasion"] == DEPARTURE_OCCASION_DECLINED_FIX
        assert ev["unit_rate_gbp_per_mwh"] is None
    # The roll and its evidence survive on a fixed-to-fixed decline; nothing is invented on the other.
    assert from_roll["departure_rolled"] is True and from_roll["random_roll"] == 0.7
    assert unrolled["departure_rolled"] is False and unrolled["random_roll"] is None
    assert rolled["departure_occasion"] == "renewal"  # the caller's dict is not mutated
    with pytest.raises(ValueError, match="STAYED"):
        declined_fix_event(
            customer_id="C1", event_date="2018-01-01", commodity="electricity",
            declined_unit_rate_gbp_per_mwh=300.0, position_vs_default=0.2,
            rolled_event={**rolled, "event_type": "churned"},
        )


def test_the_position_is_read_against_the_households_own_fuels_default():
    """A gas leg graded against the electricity default would refuse almost no gas fix (gas runs
    at about a third of the electricity rate), so the fuel must reach the reading."""
    elec = position_vs_default(100.0, "2018-06-01", commodity="electricity")
    gas = position_vs_default(100.0, "2018-06-01", commodity="gas")
    assert elec is not None and gas is not None
    assert gas > 0 > elec


def _calls_in_main(name: str) -> int:
    tree = ast.parse(inspect.getsource(p2b._main))
    return sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
    )


def test_the_run_loop_takes_the_decision_on_both_legs_and_records_it():
    """The rule's controls above stay green while no production caller reaches it, so control the
    chain: the loop asks the rule at the decision leg AND at the leg that does not decide, and
    writes the record at the decision leg's two shapes (rolled, conversion) and the other leg."""
    assert _calls_in_main("renewal_outcome") >= 2
    assert _calls_in_main("declined_fix_event") >= 3
    assert _calls_in_main("position_vs_default") >= 1
    assert isinstance(p2b.DECLINE_A_FIX_ABOVE_THE_DEFAULT, bool)
