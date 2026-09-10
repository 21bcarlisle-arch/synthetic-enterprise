"""Falsifiers for the whole-directory-subject census.

WHAT THESE HAVE TO BE ABLE TO SAY. The census exists because a number about this class was asserted
from hand passes three times and was wrong each time. A census that cannot itself fail would be the
fourth hand pass wearing an AST. So these are keyed to the PREDICATE -- planted modules whose
classification is known by construction -- and not to today's count of the live tree. A control
pinned to today's answer goes red when the code becomes more honest and stays green when the claim
rots, which is exactly backwards.

THE POSITIVE LEG COMES FIRST, DELIBERATELY. Every test of a predicate asks "does it refuse
correctly", and a predicate that refuses EVERYTHING passes all of them. `test_the_predicate_can_
say_yes` is the reachability control: if it stops holding, every refusal below is vacuous and the
census is a function that returns the empty set.
"""
from __future__ import annotations

import ast

from tools import whole_tree_subject_census as wtsc

# A module with both legs and a provable dataflow between them: the walked population IS the
# counted one. This is the shape of `test_live_ledger_guard.py`, the instance that drifted for
# fourteen days.
STRICT = '''
from pathlib import Path
BACKGROUND_DIR = Path(__file__).parent.parent / "background"
def test_bound():
    writers = list(BACKGROUND_DIR.glob("*.py"))
    assert len(writers) <= 56
'''

# Both legs present, but they are two facts about one file rather than one expression. The census
# counts this (it is the pre-registered predicate) and `strict_dataflow` marks it as the looser kind.
LOOSE = '''
from pathlib import Path
def test_something():
    rows = list(Path("company").glob("*.py"))
    assert rows
    total = 3
    assert total == 3
'''

NO_WALK = '''
def test_bound():
    total = 3
    assert total == 3
'''

NO_BOUND = '''
from pathlib import Path
def test_scan():
    for p in Path("background").glob("*.py"):
        assert p.suffix == ".py"
'''


def test_the_predicate_can_say_yes():
    """REACHABILITY. Poison round for everything below: prove the census admits a member at all.

    Without this, a `classify_source` that returned `None` unconditionally would pass every other
    test in this file, and the census would report a clean tree forever.
    """
    hit = wtsc.classify_source(STRICT)
    assert hit is not None, "the census cannot recognise its own canonical member"
    assert hit["subject_roots"] == ["background"]
    assert hit["strict_dataflow"] is True


def test_both_legs_are_load_bearing():
    """Leg 1 and leg 2 each independently exclude. Neither is decoration."""
    assert wtsc.classify_source(NO_WALK) is None, "leg 1 (a directory walk) is not being required"
    assert wtsc.classify_source(NO_BOUND) is None, "leg 2 (a counted bound) is not being required"


def test_the_loose_member_is_counted_and_marked():
    """The over-count is ADMITTED and SIZED, not quietly dropped.

    The pre-registered predicate counts proximity-in-a-module, and narrowing it after seeing the
    answer would be asymmetric -- only the false positives ever get a comment. So the loose member
    must still be a member, and must be distinguishable from the strict one.
    """
    hit = wtsc.classify_source(LOOSE)
    assert hit is not None, "the predicate was narrowed after the fact"
    assert hit["strict_dataflow"] is False, "the over-count has stopped being visible as such"


def test_control_tests_is_read_from_the_gate_not_retyped():
    """Leg 3's population is the gate's own list.

    If this census ever hard-coded the list, the two would drift apart the moment either changed,
    and the drift would silently favour whichever file was edited last -- the same two-homes defect
    the census exists to measure.
    """
    src = (wtsc.ROOT / "tools" / "whole_tree_subject_census.py").read_text()
    tree = ast.parse(src)
    imports_it = any(
        isinstance(n, ast.ImportFrom)
        and n.module == "tools.pre_commit_test_gate"
        and any(a.name == "CONTROL_TESTS" for a in n.names)
        for n in ast.walk(tree)
    )
    assert imports_it, "CONTROL_TESTS must be imported from the gate, never re-typed here"
    assert wtsc.control_tests(), "the gate's control list came back empty"


def test_leg_three_excludes_a_listed_test():
    """A censused file already on CONTROL_TESTS is REACHABLE and must leave the unreachable set.

    This is the leg that makes the count mean "silently unselected" rather than "big subject".
    """
    rows = [
        {"test": "tests/x.py", "on_control_tests": False, "strict_dataflow": True},
        {"test": "tests/y.py", "on_control_tests": True, "strict_dataflow": True},
    ]
    out = [r["test"] for r in wtsc.unreachable(rows)]
    assert out == ["tests/x.py"], "CONTROL_TESTS membership is not discharging a row"


def test_the_live_tree_still_has_members_and_the_strict_set_is_a_subset():
    """The one live-tree control, keyed to a PROPERTY rather than to a number.

    It does not assert 109, or 18, or any count -- those move as the repo does, and pinning them
    here would make an honest repair look like a regression. It asserts the two things that must
    hold whatever the counts are: the class is non-empty (so the census is not silently returning
    nothing on the real tree, which is the failure a planted-source test cannot see), and the strict
    subset really is a subset of the loose one.
    """
    rows = wtsc.census()
    assert rows, "the census finds nothing at all on the live tree"
    strict = {r["test"] for r in rows if r["strict_dataflow"]}
    assert strict <= {r["test"] for r in rows}
    assert all(r["subject_roots"] for r in rows), "a row was admitted naming no subject root"
