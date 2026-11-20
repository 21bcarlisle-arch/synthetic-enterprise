"""A dual household's two fuels answered their anniversary offers apart: the gas leg read its own
offer against its own default after the electricity leg had answered, so SYN-2016-023 could sit on
a fix for one fuel and the default for the other (SEAT_FINDING_A_DUAL_HOUSEHOLDS_TWO_FUELS_ANSWER_
THEIR_ANNIVERSARY_OFFERS_APART_2026-10-26). The household now answers once (contact page s.7.5c).
"""
import ast
import inspect

import simulation.run_phase2b as p2b
from simulation.customer_events import (
    RENEWAL_ACCEPTED,
    RENEWAL_DECLINED_FIX,
    RIDING_HOUSEHOLD_DECLINED,
    RIDING_NO_HOUSEHOLD_ANSWER,
    RIDING_PAIR_ABOVE_DEFAULT_AFTER_THE_DECISION_LEG_CONTRACTED,
    RIDING_PAIR_UNPRICED,
    RIDING_PAIR_WITHIN_DEFAULT,
    RIDING_RULE_DOES_NOT_APPLY,
    pair_position_vs_default,
    riding_leg_outcome,
)

DAY = "2017-01-17"


def _household(outcome, position, kwh=2900):
    return {"outcome": outcome, "position": position, "commodity": "electricity", "day": DAY,
            "kwh": kwh}


def _gas(own_position, household, own_kwh=11500):
    return riding_leg_outcome(own_position=own_position, household=household, commodity="gas",
                              day=DAY, own_kwh=own_kwh)


def test_every_basis_of_the_riding_answer_can_be_reached():
    """Reachability over the whole partition first, so no leg below passes by refusing all."""
    reached = {
        _gas(None, _household(RENEWAL_ACCEPTED, -0.05))[1],
        _gas(0.05, None)[1],
        _gas(-0.10, _household(RENEWAL_DECLINED_FIX, 0.04))[1],
        _gas(0.05, _household(RENEWAL_ACCEPTED, None))[1],
        _gas(0.03, _household(RENEWAL_ACCEPTED, -0.05))[1],
        _gas(0.20, _household(RENEWAL_ACCEPTED, -0.10))[1],
    }
    assert reached == {
        RIDING_RULE_DOES_NOT_APPLY, RIDING_NO_HOUSEHOLD_ANSWER, RIDING_HOUSEHOLD_DECLINED,
        RIDING_PAIR_UNPRICED, RIDING_PAIR_WITHIN_DEFAULT,
        RIDING_PAIR_ABOVE_DEFAULT_AFTER_THE_DECISION_LEG_CONTRACTED}


def test_a_household_that_declined_on_its_decision_leg_declines_its_gas_too():
    """The two-answers shape: electricity on the default, gas on a fix it would take alone."""
    assert _gas(-0.10, _household(RENEWAL_DECLINED_FIX, 0.04)) == (
        RENEWAL_DECLINED_FIX, RIDING_HOUSEHOLD_DECLINED)


def test_a_household_that_took_its_fix_takes_the_gas_fix_where_the_pair_is_within_its_default():
    """The other half of the shape: gas alone 3% over its default, the pair 1% under."""
    assert pair_position_vs_default(
        [(-0.05, "electricity", DAY, 2900), (0.03, "gas", DAY, 11500)]) < 0
    assert _gas(0.03, _household(RENEWAL_ACCEPTED, -0.05)) == (
        RENEWAL_ACCEPTED, RIDING_PAIR_WITHIN_DEFAULT)


def test_the_run_loop_asks_the_household_rule_and_publishes_every_riding_answer():
    """Keyed to the property: the riding-leg branch reads its answer from `riding_leg_outcome`,
    never from `renewal_outcome` on its own position, and the answers reach the run result."""
    src = inspect.getsource(p2b._main)
    tree = ast.parse(src)
    riding = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.If) and any(
            isinstance(c, ast.Compare) and isinstance(c.ops[0], ast.NotEq)
            and isinstance(c.left, ast.Name) and c.left.id == "commodity"
            and isinstance(c.comparators[0], ast.Name) and c.comparators[0].id == "_decision_leg"
            for c in ast.walk(n.test))
        and any(isinstance(c, ast.Name) and c.id == "_renewal_outcome" for c in ast.walk(n.test))
    ]
    assert len(riding) == 1, "expected exactly one riding-leg answer branch in _main"
    called = {c.func.id for c in ast.walk(riding[0])
              if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    assert "riding_leg_outcome" in called
    assert "renewal_outcome" not in called
    assert '"riding_leg_answers": riding_leg_answers' in inspect.getsource(p2b)
