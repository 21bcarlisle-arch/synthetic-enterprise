"""The finding: a billing account with no electricity leg cannot leave this world, ever.

WHAT WAS MEASURED (2026-09-16, delivery seat). `simulation/run_phase2b.py` books a departure at
exactly two sites — the renewal branch and the SVT-segment branch — and both of them are lexically
inside `if commodity == "electricity"`. There is no third route. So an account whose only supply
point is gas is never rolled for departure at all: it is settled, renewed and billed for the whole
window and the world never offers it the chance to go.

WHY IT MATTERS HERE AND NOT ONLY IN THE P&L. It is the standing objection to admitting the last
158 refused renewals to the value arm. Those 158 terms belong to the **18 gas-only billing
accounts** of this book (164 settled = 146 with an electricity leg + 18 without), and they are
refused today for an unrelated reason — `resolved_tariff_type`'s gas branch still spells the read
`record.get("tariff_type", "fixed")`, which a drawn record defeats by carrying the key present and
`None`. Repair that spelling and the 158 walk straight into the instrument this company uses to
ask whether it knows anything about a household. Every one of them would be a decision whose
account survives **by construction** rather than by being priced well, and
`run_value_cycle_ab._survivorship` publishes that the concordance is conditioned on survival on
the strength of the departures it CAN see. Those 18 accounts are also the exact prize
`SEAT_PREDICTION_WHAT_ADMITTING_GAS_TO_THE_ARM_WILL_AND_WILL_NOT_BUY_2026-09-07.md` named in
advance — *"the gain worth publishing is accounts, not renewals"* — so the temptation to take them
is real and it arrives with a good argument attached.

Determination and the order the two repairs are owed in:
`docs/staging/SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE_2026-09-16.md`.

KEYED TO A FINDING, AND IT IS MEANT TO GO RED. Nothing here says a departure SHOULD be electricity
-only — it is a defect, and the repair is a departure route for a gas-only account. When that
lands, `test_every_departure_booking_sits_under_an_electricity_guard` fails and is deleted together
with the finding it records, which is the same contract
`tests/simulation/test_the_tariff_type_read_has_one_home.py` writes for the sibling defect. What
this control buys in the meantime is that nobody admits the 158 without first noticing the 18.

THE SECOND LEG IS THE SUBJECT AND IT IS NOT DECORATION. A control over "every add is guarded"
passes perfectly on a book with no gas-only accounts in it, where the guard harms nobody. Leg two
measures the live roster and refuses when the population the finding is about has gone to zero,
because at that point the finding is moot and this file is furniture.

REUSE: tests/simulation/test_a_departure_is_booked_only_on_an_electricity_leg.py
CLASS: CUSTOM
INDEX: searched "departure", "churn", "gas only", "immortal", "billing account", "electricity
       guard", "commodity".
       `tests/simulation/test_the_tariff_type_read_has_one_home.py` is the nearest neighbour and
       is the SIBLING defect on the same 18 accounts — it holds the `tariff_type` READ to one
       home; this holds the DEPARTURE route. Neither can see the other's defect and merging them
       would put one finding's deletion in charge of the other's.
       `tests/company/test_carbon_not_a_target.py` is the reachability shape this borrows (walk
       the AST of the real module, never a fixture of it) and is imported from nowhere because
       the shape is four lines, not a library.
       No existing control asks which branches book a departure; `churned_billing_accounts` is
       read by `tests/simulation/` only through run artefacts, which need a decade run to produce
       and therefore cannot be a gate.
"""
from __future__ import annotations

import ast
import pathlib

from tools.python_code_text import searchable

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WORLD = _REPO / "simulation" / "run_phase2b.py"

#: The set the world adds to when an account leaves. One name, and every departure goes through it
#: — `churned_billing_accounts` gates the whole term loop at `run_phase2b.py:1660`.
_DEPARTURE_SET = "churned_billing_accounts"


def _books_a_departure(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == _DEPARTURE_SET
    )


def _mentions_the_electricity_guard(test: ast.AST) -> bool:
    """Does this `if` test compare `commodity` against the electricity literal?

    Deliberately a SUBSTRING of the test rather than the whole of it: the renewal branch's guard
    is `term_index >= 1 and commodity == "electricity" and not _indexed_tariff`, and a control
    that demanded the guard be exactly the comparison would have found neither site.

    KNOWN LIMIT, STATED RATHER THAN NARROWED AWAY. Only `==` is recognised, so respelling a live
    guard as `commodity in ("electricity",)` reds this file without changing any behaviour. That
    is a false positive and it is left in, because the honest reading of `in` is "this branch is
    about to take a second commodity" and that is exactly the event this file exists to be told
    about. The refusal message says which of the two it is and what to do either way.
    """
    for node in ast.walk(test):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
            if node.left.id != "commodity":
                continue
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value == "electricity":
                    return True
    return False


def _departure_sites() -> list[tuple[int, list[int]]]:
    """Every `churned_billing_accounts.add(...)` with the electricity guards enclosing it."""
    sites: list[tuple[int, list[int]]] = []

    def walk(node: ast.AST, guards: list[int]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If):
                inner = guards + (
                    [child.lineno] if _mentions_the_electricity_guard(child.test) else []
                )
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

    The walker recurses through `ast.iter_child_nodes`, so a site inside a comprehension, a
    `with`, a lambda or a nested function is reached by the generic arm — but "is reached" is a
    claim, and a control whose subject can go missing passes for lack of one. This holds the AST
    view and the text view to the same LINE NUMBERS, so either one losing a site is a red.

    Mutation-proven 2026-09-16 by respelling the SVT-segment booking as
    `(churned_billing_accounts).add(...)`: the two views disagree at line 1895 and this fires,
    naming the line. Without this leg that respelling would have taken a booking out of the guard
    assertion below in silence, leaving it green over one site and reading as coverage of two.
    """
    # THE CODE, NOT THE TEXT. `searchable` blanks comments and prose strings while preserving
    # every offset, so the line numbers below are the file's own and a comment naming the call --
    # `run_phase2b.py:3417` is one, and it is accurate -- is prose about the route rather than a
    # route. Hand-rolling that as `line.split("#")[0]` was the first draft and
    # `tests/architecture/test_a_control_reads_python_as_code.py` refused it, correctly: the split
    # is blind to a `#` inside a string and to a call spelled across two lines.
    spelled = {
        number
        for number, line in enumerate(searchable(_WORLD.read_text()).splitlines(), start=1)
        if f"{_DEPARTURE_SET}.add(" in line
    }
    assert spelled, (
        f"no `{_DEPARTURE_SET}.add(` anywhere in {_WORLD.name}: the departure set has been "
        "renamed or the route has moved, and this whole file is now blind"
    )
    reached = {line for line, _ in _departure_sites()}
    assert reached == spelled, (
        f"the AST walk reached departure bookings at {sorted(reached)} and the source spells them "
        f"at {sorted(spelled)}: a site sits in a node shape this scanner does not visit, so the "
        "guard assertion below is measuring a subset and reads as coverage"
    )


def test_every_departure_booking_sits_under_an_electricity_guard():
    """THE FINDING. Delete this test, with its file, when a gas-only account can leave.

    It is red on the repair and green on the defect, and that is deliberate — see the module
    docstring. Mutation-proven 2026-09-16 by dedenting the SVT-segment booking
    (`run_phase2b.py:1895`) out of its `if commodity == "electricity"` block: this goes red naming
    that line, which is the only reason it is worth having over reading the two branches.
    """
    unguarded = [line for line, guards in _departure_sites() if not guards]
    assert not unguarded, (
        "a departure is now booked outside `commodity == \"electricity\"` at "
        f"{unguarded} — if that is the gas-only departure route landing, this control and the "
        "finding it records are both spent: delete this file and "
        "docs/staging/.../EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE together. If it is not, "
        "a departure has grown a second home and the two will disagree."
    )


def test_the_book_still_holds_accounts_the_finding_is_about():
    """The defect this fires on: this file outliving its own subject and reading as coverage.

    Every assertion above is satisfied by a book with no gas-only account in it, where an
    electricity-only departure route excludes nobody. So the population is measured, not assumed.
    """
    from simulation.household import household_of
    from simulation.run_phase2b import ELEC_CUSTOMERS, GAS_CUSTOMERS

    with_electricity = {household_of(c["customer_id"]) for c in ELEC_CUSTOMERS}
    gas_only = {
        household_of(c["customer_id"])
        for c in GAS_CUSTOMERS
        if household_of(c["customer_id"]) not in with_electricity
    }
    assert gas_only, (
        "no billing account on the live roster is gas-only, so no account is shut out of the "
        "departure route and this finding has no subject left: delete this file"
    )
