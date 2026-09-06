"""The world's account-state record: what it carries for EVERY term, and for BOTH fuels.

`account_state_log` exists because nine of eleven of `tools/r1_inference_ceiling.py`'s observables
sat at 69 households of 177 and read as a limit on what a supplier can see. They were not a limit —
they were what this company happened to WRITE DOWN, at renewals, on fixed electricity terms, which
most of the book never has. A49 gates R3 and R4 on a rung built from those fields, so a field's
coverage being a fact about the book rather than about which rows a writer fired on is the
property this file controls.

Two ways that record can quietly go back to being renewal-shaped, one control each:

  - a leg's fuel goes unanswered, so the field is `None` for every gas-only household;
  - the append moves under a condition, so the record inherits that condition's coverage.
"""

import ast
from pathlib import Path

import pytest

from simulation.run_phase2b import _account_state_svt_rate

#: A date inside the published cap schedule, so BOTH fuels have a real ceiling to be read from the
#: regulation commons. Not a boundary — the boundaries are `simulation/svt_rates`' own business and
#: are controlled in `tests/simulation/test_svt_rates.py`.
_POST_CAP_DAY = "2019-06-01"


def test_the_account_state_rate_answers_for_GAS_and_is_NOT_the_electricity_series():
    """The defect and the warned-against fix in one control, because they fail in opposite
    directions and a test of either alone passes on the other.

    Before 2026-09-06 the writer answered `None` for a gas leg, and 449 of `account_state_log`'s
    2,098 rows are gas — 105 households, every one of them gas-only, with no value for the field
    in any term. The obvious repair, and the one the original comment warned against, is to write
    the ELECTRICITY cap against a gas leg: that is a spread between two commodities, a number and
    not a quantity.

    So this asserts neither shape can return. `gas is not None` kills the first; `gas != elec`
    kills the second. Both legs are asserted reachable first, or a day outside the cap schedule
    would satisfy the inequality with two `None`s and prove nothing.
    """
    gas = _account_state_svt_rate("gas", _POST_CAP_DAY)
    elec = _account_state_svt_rate("electricity", _POST_CAP_DAY)

    assert gas is not None, (
        "a gas leg has no default-tariff rate to be graded against — this is the defect that put "
        "105 gas-only households outside `svt_rate_gbp_per_mwh` on the rung A49 gates R3 and R4 on"
    )
    assert elec is not None, (
        "reachability: the electricity leg must answer on this day too, or the inequality below "
        "is satisfied by two absent readings and discriminates nothing"
    )
    assert gas != elec, (
        "the gas leg is being written the ELECTRICITY cap — a spread between two commodities"
    )


def test_the_gas_cap_sits_far_BELOW_the_electricity_cap_as_the_published_schedule_has_it():
    """Not-equal is satisfied by any two numbers; this is the one that says WHICH series answered.

    The published windows in `ofgem_default_tariff_cap_windows.json` carry gas at roughly a fifth
    of electricity per MWh across the whole cap era — the fuels are priced in different markets and
    delivered through different networks. A dispatch that answered gas with any electricity-shaped
    figure (this year's, last year's, a blend) would clear the inequality above and fail here.

    Keyed to the ORDERING and not to either value, so it stays true when the commons is extended
    and goes red only if the two fuels stop being told apart.
    """
    gas = _account_state_svt_rate("gas", _POST_CAP_DAY)
    elec = _account_state_svt_rate("electricity", _POST_CAP_DAY)

    assert gas < elec / 2, (
        f"gas ({gas}) is not below half of electricity ({elec}) — the published cap schedule has "
        "them far further apart than that, so this reading is not the gas leg"
    )


@pytest.mark.parametrize("commodity", ["", "heat", "dual_fuel", "ELECTRICITY", "water"])
def test_an_UNNAMED_fuel_gets_no_rate_rather_than_a_guessed_one(commodity):
    """Fail closed, and the refusal names its reason in the function's docstring.

    There is no default tariff for a fuel we cannot name. Falling back to electricity — the
    tempting default, because it is the one the record was built on — would write an unfalsifiable
    rate under the wrong fuel, and `rate_vs_svt_pct` downstream would then be a spread nobody
    could check. `ELECTRICITY` is in this list on purpose: the commodity is a literal the world
    writes, and a case-insensitive match would be this dispatch inventing a rule the writer has no
    idea about.
    """
    assert _account_state_svt_rate(commodity, _POST_CAP_DAY) is None


def test_the_account_state_record_is_written_OUTSIDE_the_renewal_gate():
    """The property, asserted on the source, because reaching it any other way costs a decade run.

    `account_state_log.append` and the portfolio-position read that feeds it must be statements of
    the term loop's OWN body, under no `if`. That is not a style preference: every other customer
    log in `run_phase2b` is written inside `if term_index >= 1 and commodity == "electricity" and
    not _indexed_tariff:`, which is exactly why they cover the renewing minority. An edit that
    tucked the account record under a condition would restore the defect, coverage would fall back
    to the renewal subset, and nothing downstream could tell that from a book that got smaller.

    THE POSITION READ IS HELD TO THE SAME PROPERTY AS THE APPEND. `_position` is taken ~280 lines
    above the row it lands in; if it moved under the renewal gate it would keep the value from a
    PREVIOUS iteration — a different customer's book — and the row would carry a plausible figure
    with no reading behind it. Ungated, that cannot happen.

    BOTH LEGS. The last assertion is the reachability half: it proves the gated shape is real in
    this file, so this control is discriminating between two shapes that both exist rather than
    asserting a property everything in the file happens to have.
    """
    src = Path(__file__).resolve().parents[2] / "simulation" / "run_phase2b.py"
    tree = ast.parse(src.read_text())

    def _appends_to(node, name):
        return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "append"
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == name)

    def _assigns_unconditionally(node, name, callee):
        """A statement of the body is not enough: `x = None if gate else f(...)` is a statement
        too, and it reinstates the gate inside the expression where the shape control cannot see
        it. This poisoned that exact mutant and it survived, so the assertion is on the VALUE —
        a bare call to `callee` — and not on the statement's presence."""
        if not (isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)):
            return False
        return (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                and node.value.func.id == callee)

    term_loops = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.For) and isinstance(n.target, ast.Tuple)
        and [e.id for e in n.target.elts if isinstance(e, ast.Name)]
        == ["term_start_str", "cid", "commodity", "term"]
    ]
    assert len(term_loops) == 1, f"expected exactly one term loop to reason about: {term_loops}"
    body = term_loops[0].body

    assert any(_appends_to(stmt, "account_state_log") for stmt in body), (
        "`account_state_log.append` must be a statement of the term loop's OWN body — under any "
        "`if` it inherits that condition's coverage, which is the defect this record exists to fix"
    )
    assert any(_assigns_unconditionally(stmt, "_position", "portfolio_position")
               for stmt in body), (
        "the portfolio position must be read UNCONDITIONALLY in the term loop's own body — under "
        "a gate, whether an `if` or a ternary, the row carries the previous iteration's reading, "
        "taken on a different customer's book"
    )

    gated = [n for n in ast.walk(term_loops[0])
             if isinstance(n, ast.If)
             and any(_appends_to(s, "churn_journey_log") for s in n.body)]
    assert gated, (
        "reachability: the renewal-gated shape must still exist in this file, or the assertions "
        "above are not discriminating between two shapes and would pass on anything"
    )
