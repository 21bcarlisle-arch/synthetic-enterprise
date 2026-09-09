"""A chosen case stands for many households, and nothing may quietly make it stand for one.

`DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07` §3, verbatim:

    "Two things must remain reversible, and nothing may be built that forecloses them: a weighted
     case can later be **inflated into a small population** with within-group variation, once the
     physics is settled; the count on high-volume cases can be **raised** where a use case makes
     that worth doing. Neither is built now. Both must stay possible."

**This is a negative deliverable, which is exactly why it needs a control and not a build.** An
intention cannot hold a property open. The foreclosure does not arrive as a decision to foreclose --
it arrives as another lane's reasonable simplification, with a green suite, in a lane that has never
read this canon: an integer count, a 1:1 case-to-account join, a uniqueness assumption on the
roster. Every one of those looks like tidying up.

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_real_seam_does_not_foreclose_inflation` -- the defect is the seam itself being
    simplified so a case stands for exactly one household. It runs the REAL pipeline
    (`generated_population` -> `choose_for_difference` -> `fit_weights` -> `case_household_counts`),
    not a fixture, because a fixture would only prove the arithmetic.
  * `test_POISON_every_way_of_foreclosing_is_refused` -- the reachability round. A control over a
    property nobody violates today passes vacuously, and "it passed" would then mean two opposite
    things: the property holds, or the predicate is dead. Four poisoned seams, one per reason the
    predicate can give, and the test asserts the poisons cover the WHOLE reason set rather than
    merely that each is caught -- so a reason added later without a poison reds this immediately.
  * `test_production_reaches_the_seam` -- the defect is a seam that is correct and called by
    nothing. A control that drives the estimator directly is blind to whether production wires it,
    and an unreached seam forecloses nothing because nobody is standing on it.

WHAT THIS CONTROL CANNOT SEE, stated because a control's blind spot read as coverage is worse than
no control. It guards the seam. A lane that builds a SECOND, private case-to-household mapping
elsewhere -- rather than changing this one -- forecloses the property without reding anything here.
The defence against that is that the seam is now named and reported on `measurement()`'s own
surface, so a rival mapping is a visible second home rather than the only one.
"""

import ast
import pathlib

import pytest

from tools import demand_vector_coverage as dvc

#: Every way the seam can foreclose the canon's two reversible properties. The poison round below
#: asserts this set is exactly what the poisons provoke -- a reason with no poison is a branch that
#: has never been shown to be reachable.
REASONS = frozenset({
    "SLOT_ABSENT",
    "SLOT_UNEXPLAINED",
    "ONE_HOUSEHOLD_PER_CASE",
    "COUNT_NOT_RAISABLE",
})

#: An arbitrary second household total, used only to ask whether the count is linear in it. Any
#: value other than the first would do; the property is the ratio, not the number.
RAISED_FACTOR = 2.0


def forecloses(rows, doubled) -> str | None:
    """Why `rows` foreclose inflation, or None if they do not.

    `rows` is a seam output at some household total; `doubled` is the same seam's output at
    `RAISED_FACTOR` times that total. Keyed to the PROPERTY, never to today's counts: it does not
    care how many households the biggest case carries, only that a case is permitted to carry more
    than one and that the total it is read against can be raised.
    """
    if not rows:
        return "ONE_HOUSEHOLD_PER_CASE"
    if any("within_group_variation" not in r for r in rows):
        return "SLOT_ABSENT"
    if any(r["within_group_variation"] is None
           and not str(r.get("within_group_variation_unset_because") or "").strip()
           for r in rows):
        return "SLOT_UNEXPLAINED"
    counts = [r.get("households") for r in rows]
    if not any(c is not None and c > 1.0 for c in counts):
        return "ONE_HOUSEHOLD_PER_CASE"
    raised = [r.get("households") for r in doubled]
    if len(raised) != len(counts):
        return "COUNT_NOT_RAISABLE"
    for before, after in zip(counts, raised):
        if before is None or after is None:
            return "COUNT_NOT_RAISABLE"
        if abs(after - before * RAISED_FACTOR) > 1e-6 * max(1.0, abs(after)):
            return "COUNT_NOT_RAISABLE"
    return None


@pytest.fixture(scope="module")
def real_weights():
    """Weights from the real choosing, not a fixture -- so the counts below are the book's own."""
    import numpy as np

    pop = dvc.generated_population(points=3_000, seed=0)
    values = np.asarray(pop["values"])[:, [dvc.AXES.index(a) for a in dvc.AXES]]
    reference = dvc._Reference(values, dvc.AXES)
    chosen = dvc.choose_for_difference(values, 40, seed=0)
    return dvc.fit_weights(values, chosen, reference)


def test_the_real_seam_does_not_foreclose_inflation(real_weights):
    households = 27_291_846  # GB, the counted total; see `dvc.gb_households`
    rows = dvc.case_household_counts(real_weights, households)
    doubled = dvc.case_household_counts(real_weights, int(households * RAISED_FACTOR))

    reason = forecloses(rows, doubled)
    biggest = max((r["households"] for r in rows if r["households"] is not None), default=None)
    assert reason is None, (
        f"the seam forecloses the canon's reversible property: {reason}. Biggest case stands for "
        f"{biggest} households.")
    # The canon's own claim, measured rather than asserted: one case carries many households.
    assert biggest is not None and biggest > 1.0, (
        f"no chosen case stands for more than one household (biggest={biggest}) -- the book has "
        "become a roster of individuals and the weighting is doing no work.")


def test_the_slot_is_present_and_honestly_empty(real_weights):
    """Absent is the foreclosure; empty-with-a-reason is the canon's own instruction."""
    rows = dvc.case_household_counts(real_weights, 27_291_846)
    assert all("within_group_variation" in r for r in rows)
    assert all(r["within_group_variation"] is None for r in rows), (
        "within-group variation has been filled. That is allowed -- the canon asks only that it "
        "stay possible -- but this control was keyed to it being an honest gap, so update the "
        "control deliberately rather than letting an invented spread land silently.")
    assert dvc.WITHIN_GROUP_VARIATION_IS_UNSET_BECAUSE.strip()


def test_an_absent_household_total_is_stated_and_not_defaulted(real_weights):
    """A machine without the census tables must get a stated absence, never a plausible count."""
    rows = dvc.case_household_counts(real_weights, None)
    assert all(r["households"] is None for r in rows)
    assert all("within_group_variation" in r for r in rows)


def _poison_slot_absent(weights, households):
    return [{k: v for k, v in r.items() if k != "within_group_variation"}
            for r in dvc.case_household_counts(weights, households)]


def _poison_slot_unexplained(weights, households):
    return [{**r, "within_group_variation_unset_because": ""}
            for r in dvc.case_household_counts(weights, households)]


def _poison_one_household_per_case(weights, households):
    """The reasonable simplification: a case IS a household, so its count is one."""
    return [{**r, "households": 1.0} for r in dvc.case_household_counts(weights, households)]


def _poison_count_not_raisable(weights, households):
    """A count pinned to today's book -- raising the population no longer raises the case."""
    fixed = dvc.case_household_counts(weights, 27_291_846)
    return [{**r, "households": f["households"]}
            for r, f in zip(dvc.case_household_counts(weights, households), fixed)]


#: One poison per reason. The mapping is asserted to be onto `REASONS`, so this is a partition
#: control rather than four independent legs.
POISONS = {
    "SLOT_ABSENT": _poison_slot_absent,
    "SLOT_UNEXPLAINED": _poison_slot_unexplained,
    "ONE_HOUSEHOLD_PER_CASE": _poison_one_household_per_case,
    "COUNT_NOT_RAISABLE": _poison_count_not_raisable,
}


def test_POISON_every_way_of_foreclosing_is_refused(real_weights):
    households = 27_291_846
    provoked = set()
    for expected, poison in POISONS.items():
        rows = poison(real_weights, households)
        doubled = poison(real_weights, int(households * RAISED_FACTOR))
        got = forecloses(rows, doubled)
        assert got is not None, (
            f"the poison `{expected}` was NOT refused -- this control passes vacuously and its "
            "green says nothing about the canon's property.")
        provoked.add(got)
    assert provoked == set(REASONS), (
        f"the poison round provoked {sorted(provoked)} but the predicate can give {sorted(REASONS)}"
        " -- a reason with no poison is a branch nobody has shown to be reachable.")


def test_production_reaches_the_seam():
    """A seam nothing calls forecloses nothing, because nobody is standing on it."""
    source = pathlib.Path(dvc.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    definitions = {n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "case_household_counts"}
    inside = {id(c) for d in definitions for c in ast.walk(d)}
    callers = [n for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "case_household_counts" and id(n) not in inside]
    assert callers, (
        "`case_household_counts` is defined and called by nothing in its own module. The seam is "
        "then a claim in a docstring rather than the path the book's counts actually take.")
