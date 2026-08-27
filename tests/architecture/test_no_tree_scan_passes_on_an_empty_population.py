"""A test that scans the TREE must not pass when its scan finds nothing.

THE DIRECTOR, 2026-08-27: *"the population floor is the right cheap control; add more of them."*
This is that instruction converted from a sweep into a mechanism, per MAKE_IT_STICK — *"convert
policy to mechanism, or accept it will evaporate"*. A sweep fixes today's twelve; a ratchet fails
the thirteenth on the day it lands.

THE DEFECT, stated precisely enough to detect. A test of the shape

    for thing in <derived from the tree>:
        assert <property of thing>

passes **vacuously** when the derivation returns nothing. Every assertion lives inside the loop,
so an empty population is indistinguishable from a clean one. The test goes green, and whatever
it was guarding is unguarded.

WHY THIS SHAPE AND NOT "EVERY TEST WITH A LOOP". The first draft of the detector asked "does this
test loop over something and assert", and returned **1,285** — which meant the detector was
wrong, not the repository. The question that matters is narrower and answerable: *would this test
pass if its population were empty?* That is true only when EVERY assertion sits inside a loop over
a population the test derived from the tree itself. Tightened to that, it returned **twelve**, and
all twelve were genuine.

WHAT THE TWELVE WERE, because the population is the argument for the control. Almost all were
EPISTEMIC-WALL guards — `test_no_sim_import`, `test_the_worlds_codec_never_imports_the_companys`,
`test_company_twin_respects_wall` (twice), `test_module_imports_no_simulation_internals`,
`test_the_world_is_not_imported_here`. Each collects imports from an AST and asserts inside the
loop, so a module restructured into a re-export shim, a rename, or a parse that found no imports
would all read as "the wall is clean". Two more were the exit-143 kill-path guards — a SAFETY
control whose glob could match nothing.

And one of them, `test_the_draw_helpers_the_measurement_rests_on_are_still_defined_where_it_looks`,
carries this in its own docstring:

    "an empty subject is how a census passes while measuring nothing"

and then loops with every assertion inside. **It named the hazard and had it.** That is the whole
case for a mechanism over a maxim, in one test.

THE FLOOR IS CHEAP AND THE MISS IS NOT. Five separate controls were found this day scanning a
subject that had silently shrunk — a store census reading 74 atoms of 298, an evidence page built
from a quarter of the map — and a dated population floor was the only thing that caught three of
them.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TESTS = REPO / "tests"

#: Calls that derive a population FROM THE TREE. A fixture list built inside the test is not in
#: scope: it cannot silently empty, because whoever emptied it edited the test.
_TREE_DERIVATIONS = ("rglob", "glob", "iterdir", "walk")

#: This control's own floor. It must find the whole test corpus, or it is the very defect it
#: exists to catch. Measured 2026-08-27: 1,000+ test functions across the tree.
MIN_TEST_FUNCTIONS_SCANNED = 800


def _derives_from_tree(fn: ast.FunctionDef) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name in _TREE_DERIVATIONS:
                return True
    return False


def _vacuous_on_empty(fn: ast.FunctionDef) -> bool:
    """Every assertion is inside a for-loop, so an empty population passes."""
    loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)]
    if not loops:
        return False
    in_loop = {id(n) for lp in loops for n in ast.walk(lp) if isinstance(n, ast.Assert)}
    asserts = [n for n in ast.walk(fn) if isinstance(n, ast.Assert)]
    return bool(asserts) and all(id(a) in in_loop for a in asserts)


def _scan() -> tuple[list[str], int]:
    """(offenders, test functions examined)."""
    offenders: list[str] = []
    examined = 0
    for path in sorted(TESTS.rglob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(errors="replace"))
        except SyntaxError:
            # FAIL-VISIBLE: an unparseable test file is reported, never skipped into silence.
            offenders.append(f"{path.relative_to(REPO)}::<unparseable>")
            continue
        for fn in (n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")):
            examined += 1
            if _derives_from_tree(fn) and _vacuous_on_empty(fn):
                offenders.append(f"{path.relative_to(REPO)}::{fn.name}")
    return offenders, examined


def test_this_controls_own_population_is_not_empty():
    """THE FLOOR ON THE FLOOR-CHECKER. A control that scans the test corpus and finds nothing
    would report a clean sweep — which is exactly the defect below, one level up."""
    _, examined = _scan()
    assert examined >= MIN_TEST_FUNCTIONS_SCANNED, (
        f"only {examined} test functions examined (floor {MIN_TEST_FUNCTIONS_SCANNED}) — this "
        "control's own subject collapsed, so its green means nothing")


def test_no_tree_scanning_test_passes_on_an_empty_population():
    """THE RATCHET. Add a floor; do not add an exemption list."""
    offenders, _ = _scan()
    assert offenders == [], (
        "these tests derive a population FROM THE TREE and put every assertion inside the loop, "
        "so they pass when the scan finds nothing and whatever they guard is unguarded:\n"
        + "".join(f"    {o}\n" for o in offenders)
        + "\n    Add a population floor — `assert <population>, \"...\"` before the loop, with a "
          "message saying what an empty scan would mean. Do NOT add an exemption list: a control "
          "whose subject can silently empty is the thing this exists to stop."
    )


# ---------------------------------------------------------------------------
# R15 — the control fires on its own named defect
# ---------------------------------------------------------------------------

_VACUOUS = '''
def test_something():
    for p in Path("x").rglob("*.py"):
        assert "bad" not in p.read_text()
'''

_FLOORED = '''
def test_something():
    found = list(Path("x").rglob("*.py"))
    assert found, "the scan found nothing"
    for p in found:
        assert "bad" not in p.read_text()
'''

_NO_TREE = '''
def test_something():
    for item in [1, 2, 3]:
        assert item > 0
'''


def _judge(source: str):
    fn = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef))
    return _derives_from_tree(fn), _vacuous_on_empty(fn)


def test_MUTATION_a_vacuous_tree_scan_is_detected():
    assert _judge(_VACUOUS) == (True, True)


def test_a_floored_scan_is_NOT_an_offender():
    """THE PARTNER. The remedy must actually clear the control, or the only way past it is an
    exemption — and an exemption list is how a ratchet becomes decoration."""
    derives, vacuous = _judge(_FLOORED)
    assert derives is True and vacuous is False


def test_a_loop_over_a_FIXTURE_is_not_in_scope():
    """Scope. A list built inside the test cannot silently empty: whoever emptied it edited the
    test. Flagging those would bury the real ones, which is how a noisy control gets switched
    off.

    NOTE THE SHAPE, corrected after this assertion was written wrong: such a loop IS
    vacuous-on-empty — every assertion is inside it — and that is fine. What takes it out of
    scope is that it does not DERIVE FROM THE TREE. The offender condition is the CONJUNCTION,
    and asserting the second half alone would have pinned the wrong property."""
    derives, vacuous = _judge(_NO_TREE)
    assert derives is False, "a literal list is not a tree derivation"
    assert vacuous is True, "it is vacuous-on-empty, which is why the conjunction is what matters"


@pytest.mark.parametrize("derivation", ["rglob", "glob", "iterdir", "walk"])
def test_every_declared_derivation_is_actually_recognised(derivation):
    """The vocabulary must not drift from the detector: a derivation named in
    `_TREE_DERIVATIONS` that the walker cannot see would be a silent hole in the subject."""
    src = f'''
def test_x():
    for p in Path("x").{derivation}("*"):
        assert p
'''
    assert _derives_from_tree(
        next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)))
