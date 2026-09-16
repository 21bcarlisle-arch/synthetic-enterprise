"""A household leaves once, on a leg the world names — not on a fuel literal, and not on none.

THE DEFECT THIS REPLACES, AND WHY THE REPLACEMENT IS NOT THE SAME CONTROL.
`tests/simulation/test_a_departure_is_booked_only_on_an_electricity_leg.py` recorded a finding:
`run_phase2b` booked its two departures inside `if commodity == "electricity"`, so the 18 billing
accounts on this book holding a gas supply point and no electricity one were never rolled for
departure at all — settled, renewed and billed across 2016-2025 with no route out, 11% of the book
immortal. That file said in its own docstring that it was meant to go red and to be deleted with
the finding when the route landed. It has, so it was
(`SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE`,
discharged 2026-09-16).

What is NOT discharged is the property underneath it, and it now has TWO ways to fail rather than
one. `simulation.customer_events.departure_decision_leg` names, per account, the single leg its
departure is rolled on. The world is wrong if either:

  * a booking goes back under a FUEL LITERAL — the original defect, in whatever spelling. Some
    population is then immortal again, and which one depends on the literal chosen; or
  * a booking sits under NO leg guard at all — the mirror defect, which has never happened here
    and would be invisible in the P&L as anything but good news. A dual-fuel household would roll
    twice a cycle, on electricity and again on gas, and leave at roughly double its own hazard.
    Nothing downstream can see this: `churned_billing_accounts` is a SET, so the second roll of an
    account that already left is a no-op, and the only trace is a departure DATE that moved
    earlier. A churn rate that came out high would read as the world being hard on us.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER, which is the distinction this project has paid for
repeatedly. This file does not assert that the deciding leg is electricity, or gas, or that any
particular account can leave. It asserts that the branch condition is a NAME the world resolves per
account rather than a constant — so a roster whose fuel mix changes keeps passing, and a
re-hardcoding stops being a silent edit.

LEG 3 IS THE REACHABILITY LEG AND IT IS THE POINT OF THE FILE. A guard keyed to a name passes every
structural check above even if that name resolves to `"electricity"` for every account on the
book — which is the defect, exactly, wearing the repair's clothes. So the partition is measured on
the live roster: both answers must be attained. (CLAUDE.md: "When a branch exists to be taken
rarely, assert it CAN be taken before asserting what it does.")

REUSE: tests/simulation/test_a_departure_rolls_on_exactly_one_named_leg.py
CLASS: CUSTOM
INDEX: searched "departure", "decision leg", "churn guard", "gas only", "commodity literal",
       "one roll per account".
       `tests/simulation/test_a_departure_is_booked_only_on_an_electricity_leg.py` is the file this
       supersedes and is DELETED in the same commit — it asserts the negation of leg 1 and the two
       cannot both stand. Its AST walk is reused here rather than imported, because importing a
       scanner from a file whose whole purpose is to be deleted would have made this one undeletable
       in turn; it is twenty lines and the duplication is the cheaper of the two debts.
       `tests/simulation/test_the_tariff_type_read_has_one_home.py` is the SIBLING defect on the
       same 18 accounts and stays red — it holds the gas `tariff_type` READ to one home, which is
       repair 2 and is deliberately not in this commit.
       `tests/company/test_carbon_not_a_target.py` is the reachability shape leg 3 borrows.
       No existing control asks which branches book a departure.
"""
from __future__ import annotations

import ast
import pathlib

from tools.python_code_text import searchable

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WORLD = _REPO / "simulation" / "run_phase2b.py"

#: The set the world adds to when an account leaves. Every departure goes through it —
#: `churned_billing_accounts` gates the whole term loop.
_DEPARTURE_SET = "churned_billing_accounts"

#: The local name `run_phase2b` resolves `departure_decision_leg` into, once per term.
_DECISION_LEG = "_decision_leg"


def _books_a_departure(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == _DEPARTURE_SET
    )


def _commodity_comparisons(test: ast.AST) -> list[ast.expr]:
    """Everything this `if` test compares `commodity` against.

    Returns the comparators, not a verdict, so the two assertions below can ask different
    questions of the same walk — one wants "a Name", the other wants "no Constant". A helper that
    collapsed to a bool would have forced one of them to re-walk and the two could drift.

    A SUBSTRING OF THE TEST, DELIBERATELY: the renewal branch's guard is
    `term_index >= 1 and commodity == _decision_leg and not _indexed_tariff`, and a control
    demanding the guard be exactly the comparison would find neither site.
    """
    found: list[ast.expr] = []
    for node in ast.walk(test):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
            if node.left.id == "commodity":
                found.extend(node.comparators)
    return found


def _departure_sites() -> list[tuple[int, list[ast.expr]]]:
    """Every `churned_billing_accounts.add(...)` with what its enclosing `if`s test `commodity` against."""
    sites: list[tuple[int, list[ast.expr]]] = []

    def walk(node: ast.AST, guards: list[ast.expr]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If):
                inner = guards + _commodity_comparisons(child.test)
                for stmt in child.body:
                    walk(stmt, inner)
                # An `else` is NOT under the `if`'s test, so it keeps the outer guards.
                for stmt in child.orelse:
                    walk(stmt, guards)
                continue
            if _books_a_departure(child):
                sites.append((child.lineno, list(guards)))
            walk(child, guards)

    walk(ast.parse(_WORLD.read_text()), [])
    return sites


def test_the_scanner_reaches_every_departure_booking_the_source_spells():
    """The defect this fires on: a booking written in a node shape the walker never visits.

    A control whose subject can go missing passes for lack of one. This holds the AST view and the
    text view to the same LINE NUMBERS, so either losing a site is a red.

    Mutation-proven 2026-09-16 by respelling the SVT-segment booking as
    `(churned_billing_accounts).add(...)`: the two views disagree and this fires, naming the line.
    Without it that respelling would take a booking out of the assertions below in silence, leaving
    them green over one site and reading as coverage of two.
    """
    # THE CODE, NOT THE TEXT. `searchable` blanks comments and prose strings while preserving every
    # offset, so a comment naming the call -- there is one, and it is accurate -- is prose about the
    # route rather than a route.
    spelled = {
        number
        for number, line in enumerate(searchable(_WORLD.read_text()).splitlines(), start=1)
        if f"{_DEPARTURE_SET}.add(" in line
    }
    assert spelled, (
        f"no `{_DEPARTURE_SET}.add(` anywhere in {_WORLD.name}: the departure set has been renamed "
        "or the route has moved, and this whole file is now blind"
    )
    reached = {line for line, _ in _departure_sites()}
    assert reached == spelled, (
        f"the AST walk reached departure bookings at {sorted(reached)} and the source spells them "
        f"at {sorted(spelled)}: a site sits in a node shape this scanner does not visit, so the "
        "assertions below are measuring a subset and read as coverage"
    )


def test_no_departure_is_booked_under_a_hardcoded_fuel():
    """The original defect, in any spelling: a fuel literal deciding who may leave.

    Mutation-proven 2026-09-16 by restoring `commodity == "electricity"` at the SVT-segment guard:
    this fires naming that line and the literal. That is the exact edit that made 18 accounts
    immortal for the life of the book, and it passed every other control in the tree.
    """
    hardcoded = [
        (line, comparator.value)
        for line, guards in _departure_sites()
        for comparator in guards
        if isinstance(comparator, ast.Constant)
    ]
    assert not hardcoded, (
        f"a departure booking is gated on a fuel LITERAL at {hardcoded} — that is the shape that "
        "left every billing account without a leg of that fuel unable to ever leave this world "
        "(18 of 164, 2016-2025). The leg an account departs on is per-account and the world "
        "resolves it: `simulation.customer_events.departure_decision_leg`."
    )


def test_every_departure_booking_is_gated_on_the_resolved_decision_leg():
    """The mirror defect: a booking under no leg guard, so a dual-fuel household rolls twice.

    Has never happened here, and would present as the world being hard on us rather than as a bug —
    see the module docstring on why `churned_billing_accounts` being a set hides it.

    Mutation-proven 2026-09-16 by dedenting the SVT-segment booking out of its guard: this fires
    naming the line.
    """
    ungated = [
        line
        for line, guards in _departure_sites()
        if not any(
            isinstance(comparator, ast.Name) and comparator.id == _DECISION_LEG
            for comparator in guards
        )
    ]
    assert not ungated, (
        f"a departure is booked at {ungated} without `commodity == {_DECISION_LEG}` enclosing it. "
        "Either it is gated on nothing — in which case a dual-fuel household rolls on both legs "
        "and leaves at about double its own hazard, invisibly, because the departure set is a set "
        f"— or the resolved leg has been renamed, in which case fix `{_DECISION_LEG}` here."
    )


def test_both_answers_of_the_decision_leg_are_attained_on_the_live_roster():
    """The defect this fires on: the repair being structural only.

    Every assertion above is satisfied by a world where `_decision_leg` is a name that resolves to
    `"electricity"` for every account on the book — which is the original defect exactly, passing a
    control keyed to the spelling of its guard. So the partition is measured rather than assumed:
    both legs must be somebody's.

    It fires the other way too, and that is not a hypothetical to design around but the outcome to
    WANT: if the roster stops holding any gas-only account, the gas branch is unreachable and this
    file should be told so rather than going on reporting coverage of it.
    """
    from simulation.customer_events import departure_decision_leg
    from simulation.household import household_of
    from simulation.run_phase2b import ELEC_CUSTOMERS, GAS_CUSTOMERS

    with_electricity = {household_of(c["customer_id"]) for c in ELEC_CUSTOMERS}
    accounts = with_electricity | {household_of(c["customer_id"]) for c in GAS_CUSTOMERS}
    legs = {
        departure_decision_leg(a, accounts_with_an_electricity_leg=with_electricity)
        for a in accounts
    }
    assert legs == {"electricity", "gas"}, (
        f"the decision leg resolves to {sorted(legs)} across all {len(accounts)} accounts on the "
        "live roster, so one branch of the guard is unreachable. If only 'electricity' is "
        "attained, no account is gas-only and the repair is structural with nothing behind it; if "
        "only 'gas' is, the book has lost its electricity legs and something much larger is wrong."
    )


def test_the_leg_is_unchanged_for_every_account_that_has_an_electricity_supply_point():
    """The defect this fires on: the repair moving a population it claimed not to touch.

    The whole warrant for landing this without re-deriving the book is that the predicate is the
    IDENTITY on the old literal wherever the old literal had an answer. That is a claim about 146
    of 164 accounts and it is asserted here rather than left to the reader.
    """
    from simulation.customer_events import departure_decision_leg
    from simulation.household import household_of
    from simulation.run_phase2b import ELEC_CUSTOMERS

    with_electricity = {household_of(c["customer_id"]) for c in ELEC_CUSTOMERS}
    assert with_electricity, "no account on the roster holds an electricity leg"
    moved = [
        a
        for a in with_electricity
        if departure_decision_leg(a, accounts_with_an_electricity_leg=with_electricity)
        != "electricity"
    ]
    assert not moved, (
        f"{len(moved)} accounts holding an electricity leg now decide on another leg ({moved[:5]}) "
        "— the repair was warranted as behaviour-preserving on exactly this population and is not"
    )
