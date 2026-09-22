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

# The two-hop shape the one-hop `strict_dataflow` rule cannot see: the counted population derives
# from the walked one through an intermediate binding. Strict in SUBSTANCE, loose by the one-hop
# rule. This is the fixture the transitive predicate exists for.
TWO_HOP = '''
from pathlib import Path
DIR = Path(__file__).parent.parent / "background"
def test_bound():
    rows = [p for p in DIR.glob("*.py") if p.name != "x"]
    names = {p.name for p in rows}
    assert len(names) <= 56
'''

# The same name bound in TWO different functions, one from a walk and one not. Python scopes these
# apart and so must the taint; a module-wide merge reports a whole-directory subject that is not
# there. This is the shape that produced the transitive rule's only live hit on its first run.
COLLIDING_SCOPES = '''
from pathlib import Path
def test_a():
    after = list(Path("background").glob("*.py"))
    assert after
def test_b():
    after = compute_something_else()
    assert len(after) >= 5
'''

# A module-level constant walked once and counted inside a function. Scoping the taint must NOT
# lose this -- a global really is visible below, and this is the commonest real shape of all.
MODULE_LEVEL = '''
from pathlib import Path
ROWS = list(Path("company").glob("*.py"))
def test_bound():
    assert len(ROWS) == 12
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


def test_the_transitive_rule_can_say_yes():
    """REACHABILITY for everything below, and it comes first for the same reason as the one above.

    `_transitive_dataflow` reports ZERO promotions on the live tree. That number means "the two-hop
    shape is absent here" only if the rule can recognise the shape at all; a rule that returned
    False unconditionally would report the identical zero and pass every negative test in this file.
    The defect this names is that zero being the predicate's own silence.
    """
    hit = wtsc.classify_source(TWO_HOP)
    assert hit is not None, "the two-hop module is not even a census member"
    assert hit["strict_dataflow"] is False, "the one-hop rule has stopped being one hop"
    assert hit["transitive_dataflow"] is True, (
        "the transitive rule cannot see a two-hop derivation, so its count of 0 on the live tree "
        "says nothing about the tree")


def test_taint_does_not_cross_between_two_functions_binding_the_same_name():
    """The defect this names: a whole-directory subject reported where there is none.

    `after = <a walk>` in one test function and `len(after) >= 5` in another are two different
    variables that Python never confuses. A module-wide taint merge does confuse them, and it is
    not a conservative over-approximation -- it is a misreading, and it was this predicate's only
    hit on the live tree before the scope index went in.

    `strict_dataflow` is deliberately NOT asserted here in either direction. It IS scope-blind and
    fires on this fixture; that is recorded in the census docstring rather than repaired, because
    repairing it would delete two earned lines from the always-run list on a rule that is blind to
    helper return values in the opposite direction. If someone later fixes it, this test must not
    be what stands in the way.
    """
    hit = wtsc.classify_source(COLLIDING_SCOPES)
    assert hit is not None
    assert hit["transitive_dataflow"] is False, (
        "a walk in one function is tainting a count in another; the taint has stopped being scoped")


def test_scoping_the_taint_did_not_lose_module_level_bindings():
    """The OTHER direction of the scope fix, and the reason it is not an asymmetric narrowing.

    A narrowing added to fix a false positive only ever hears the false-positive side. The cheapest
    wrong way to scope taint is to confine it to the function that assigns it -- which would drop
    `ROWS = list(DIR.glob(...))` at module level, the single commonest shape in this repo, and turn
    a real class of members invisible while the count went reassuringly down.
    """
    hit = wtsc.classify_source(MODULE_LEVEL)
    assert hit is not None
    assert hit["transitive_dataflow"] is True, (
        "a module-level walked constant is no longer visible to a bound inside a function")
    assert hit["strict_dataflow"] is True, "the one-hop rule lost the module-level shape too"


def test_editing_a_loose_member_into_strict_form_puts_it_back_in_the_refused_pool():
    """PROMOTION-ON-CHANGE, driven through `unreachable()` rather than argued in a docstring.

    The drawn question offered "a cheaper predicate that promotes a loose member to strict when its
    walk becomes provably the counted population" as work to do. It is already done, by
    construction: the strict control re-runs this census over every tracked test file, so the
    member's own edit is what re-classifies it. The defect this names is that claim being false --
    a census that classified from anything cached, listed or frozen would leave the edited member
    loose and the refusal would never fire.

    Composed on purpose: the classification AND the leg-3 filter, because either alone would pass
    while the pair did nothing.
    """
    before = wtsc.classify_source(LOOSE)
    assert before is not None and before["strict_dataflow"] is False

    promoted = LOOSE.replace(
        '    rows = list(Path("company").glob("*.py"))\n    assert rows\n'
        '    total = 3\n    assert total == 3\n',
        '    rows = list(Path("company").glob("*.py"))\n    assert len(rows) == 3\n',
    )
    assert promoted != LOOSE, "the fixture moved and this test is no longer editing anything"

    after = wtsc.classify_source(promoted)
    assert after is not None and after["strict_dataflow"] is True, (
        "editing a loose member into one-expression form did not make it strict, so nothing would "
        "refuse it at the commit that wrote it")

    row = {"test": "tests/edited.py", "on_control_tests": False, **after}
    assert [r["test"] for r in wtsc.unreachable([row])] == ["tests/edited.py"], (
        "the promoted member does not reach the refused pool")


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
    # Every row carries BOTH readings. There is deliberately no `strict <= transitive` assertion:
    # that was pre-registered as holding by construction and is FALSE, because `strict_dataflow` is
    # scope-blind and `_transitive_dataflow` is not. Two live members are strict and not transitive
    # for exactly that reason -- see the census docstring. Asserting the subset here would pin the
    # instrument's own defect as a property.
    assert all("transitive_dataflow" in r for r in rows), "a row was admitted with one reading only"


# ---------------------------------------------------------------------------
# THE WIDENED LEG 1 (2026-09-23). A population may come from GIT, not only from a filesystem walk.
#
# Each control below names the defect it refuses. They are planted-source rather than live-tree for
# the reason the file's header gives: a control keyed to today's answer goes red when the code
# becomes more honest. The live-tree property control above stays the only one that reads the tree.
# ---------------------------------------------------------------------------

_GIT_LS_FILES = '''
import subprocess
from pathlib import Path
def test_bound():
    rows = subprocess.run(
        ["git", "ls-files", "--", "docs/*.md"], capture_output=True, text=True
    ).stdout.splitlines()
    assert len(rows) >= 20
'''

_GIT_WRAPPER_READS = '''
import subprocess
from pathlib import Path
def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout
def test_bound():
    rows = _git("ls-files", "--", "background/*.py").splitlines()
    assert len(rows) >= 12
'''

_GIT_WRAPPER_WRITES = '''
import subprocess
from pathlib import Path
def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout
def test_bound():
    _git("commit", "-m", "background/x.py")
    rows = ["a", "b"]
    assert len(rows) >= 2
'''


def test_a_git_oracled_population_is_seen_at_all():
    """DEFECT REFUSED: leg 1 required an `ast.Attribute` walk, so a control whose subject is the
    COMMITTED bytes matched it not at all -- and the census's resulting 0 was read as "no such
    control exists" by `test_the_strict_census_stays_discharged`, which turns it into a commit-time
    refusal. Five controls with exactly that shape were red at `origin/main` while it said 0.

    MUTATION (must fire): drop the `_is_git_oracle_argv` branch from `_is_population_call` and this
    returns `None`.
    """
    hit = wtsc.classify_source(_GIT_LS_FILES)
    assert hit is not None, "a `git ls-files` population is not a population"
    assert hit["subject_roots"] == ["docs"]
    assert hit["strict_dataflow"], "the oracled population IS the counted one, in one hop"


def test_a_generic_git_wrapper_is_resolved_at_its_call_site_and_not_wholesale():
    """DEFECT REFUSED: `["git", *args]` names no subcommand, so a rule demanding a literal one sees
    no git call -- which is how `_git(*args)`, the wrapper shape every git-oracled member of this
    class actually uses, stayed invisible. But admitting such a wrapper WHOLESALE is the opposite
    error: `_git("commit")` writes the repository and reads no population, and crediting it with one
    would put a test that merely commits into a class it does not belong to.

    So the subcommand is asked at the CALL SITE. Both directions are controlled here, because a rule
    that only ever heard the false-negative side is the asymmetric narrowing this file warns about.

    MUTATION (must fire, either leg): make `_is_population_call` return True for any name in
    `helpers` and the WRITER leg reds; require `helpers[f.id]` and the READER leg reds.
    """
    reader = wtsc.classify_source(_GIT_WRAPPER_READS)
    assert reader is not None, "a wrapper passed `ls-files` by its caller reads a population"
    assert reader["strict_dataflow"], "the wrapper's return IS the counted population"

    writer = wtsc.classify_source(_GIT_WRAPPER_WRITES)
    assert writer is None, (
        "`_git('commit', ...)` was credited with a population. The wrapper writes; the caller's "
        "subcommand is what decides, and reading the wrapper alone cannot tell the two apart"
    )


# ---------------------------------------------------------------------------
# THE SPLIT `tests` EXCLUSION (2026-09-23). `tests` is admitted as a subject root ONLY when it is
# read as a POPULATION, never when a file is merely named.
# ---------------------------------------------------------------------------

_TESTS_CORPUS_RATCHET = '''
from pathlib import Path
TESTS = Path(__file__).resolve().parent.parent / "tests"
def test_bound():
    offenders = [p for p in TESTS.rglob("test_*.py") if "ast.walk" in p.read_text()]
    assert len(offenders) <= 3
'''

# THIS FIXTURE MUST CARRY A REAL POPULATION, and the first draft of it did not. A module that only
# read one test file was excluded by leg 1 (no population call at all), so the control below passed
# without the `tests` discrimination ever being reached -- it would have stayed green with the split
# deleted entirely. Driven out by mutation, not by reading: the `tests`-always mutation left it
# silent. So the population here is a real `background/` glob, the row IS admitted, and the only
# question the assertion asks is whether `tests` joined its subject roots.
_TESTS_NAMED_FILE = '''
from pathlib import Path
BG = Path(__file__).resolve().parent.parent / "background"
def test_bound():
    rows = list(BG.glob("*.py"))
    assert len(rows) >= 5
    named = Path("tests/sim/test_scenario_spine_consumption.py").read_text()
    assert "def test_" in named
'''


def test_a_corpus_wide_ratchet_over_tests_is_admitted():
    """DEFECT REFUSED: `tests` was excluded from `SOURCE_ROOTS` on a reason -- "a test whose subject
    is other tests is reached by staging those tests" -- that is TRUE of a test naming a sibling and
    FALSE of a ratchet over the corpus. Staging `tests/sim/test_x.py` selects that file; it does not
    select the repo-wide ratchet that file just joined. Measured price of the conflation: five
    `ast.walk` offenders accumulated behind `test_no_tree_scan_passes_on_an_empty_population` with
    every arriving commit green.

    MUTATION (must fire): drop the `_test_corpus_population` call from `classify_source` and this
    returns `None`, because no OTHER source root is named here.
    """
    hit = wtsc.classify_source(_TESTS_CORPUS_RATCHET)
    assert hit is not None, "a repo-wide ratchet over the test corpus is not in class"
    assert hit["subject_roots"] == ["tests"]


def test_naming_one_test_file_is_not_a_population_and_stays_excluded():
    """THE OTHER HALF, and it is why the exclusion was SPLIT rather than deleted. A blanket
    un-exclusion would pull in every test file in the tree; the discriminator is POPULATION vs NAMED
    FILE, which is exactly what the original reason turns on -- a named file IS reached by staging
    it.

    MUTATION (must fire): make `_test_corpus_population` return True unconditionally and `tests`
    joins the subject roots below. The row stays ADMITTED under that mutation -- it has a real
    `background/` population -- so this control isolates the split and nothing else.
    """
    hit = wtsc.classify_source(_TESTS_NAMED_FILE)
    assert hit is not None, "the fixture lost its `background/` population and proves nothing"
    assert hit["subject_roots"] == ["background"], (
        f"naming one test file put {hit['subject_roots']} in the subject roots. A named file is "
        "reached by staging it, which is the whole reason the exclusion exists; admitting `tests` "
        "here would put every test that reads a sibling into the class"
    )
