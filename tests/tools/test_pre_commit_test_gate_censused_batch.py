"""The censused batch on `CONTROL_TESTS`: is it reached, is it earned, and is it complete?

WHAT THESE GRADE. `tools/pre_commit_test_gate.py` gained eighteen entries at once
(`CENSUSED_WHOLE_DIRECTORY_SUBJECTS`), derived by `tools/whole_tree_subject_census.py` from a
predicate pre-registered before the first count was run. Every one of them has a whole DIRECTORY
for a subject and, before this, a single filename STEM for a selector -- so the commit that breaks
one of them (a new file in that directory) was exactly the commit that could not select it.

WHY THE FIRST CONTROL IS A POSITIVE ONE, deliberately and in this order: a selector that returns
NOTHING passes every "is X excluded" assertion ever written, and the failure mode of this whole
mechanism is quietly selecting the empty set.

ONE CONTROL WAS WRITTEN HERE AND DELETED BEFORE THE GREEN WAS BELIEVED, recorded because the next
session will be tempted to write it again. It asserted that no member is reachable by filename
stem, by probing `tests_for("<root>/zz_a_module_that_does_not_exist_yet.py")` for each subject
root. That CANNOT FAIL: a fabricated stem matches no test file by construction, so the assertion
was true for reasons having nothing to do with the batch. The honest version -- probing every
module that actually exists under each subject root -- fails in the wrong direction instead: a new
`background/isolation_guards.py` would give `tests/test_isolation_guards.py` a stem route while
leaving its subject (every file under `docs/`) exactly as wide, so the entry would still be earned
and the control would red on a non-defect. Stem-unreachability is the census predicate's business;
re-asserting it here is a tautology or a false red, and neither is worth a line.

WHAT THEY ARE KEYED TO. The property, never today's answer. There is no assertion here that the
batch has eighteen members or that the census returns any particular number -- those move as the
repo does, and a control pinned to them reds when the code becomes more honest. What is asserted is
that each member is reached by a commit no stem can map to it, that each still has the
whole-directory subject that earns its always-run cost, and that the strict census stays discharged.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402
from tools import whole_tree_subject_census as wtsc  # noqa: E402

#: Bound to the MODULE, never imported by name. `tests_for` matches pytest's default
#: `python_functions = test*`, so `from ... import tests_for` gets COLLECTED as a test and errors
#: on a missing `path` fixture -- a red that says nothing about the gate.
CENSUSED_WHOLE_DIRECTORY_SUBJECTS = gate.CENSUSED_WHOLE_DIRECTORY_SUBJECTS

#: A path that cannot exist and therefore cannot be mapped by stem to anything. This is the shape of
#: the commit the whole batch exists for: a NEW module in a directory some control counts.
NEW_MODULE = "background/zz_a_daemon_that_does_not_exist_yet.py"


def test_a_brand_new_module_selects_every_member_of_the_batch():
    """THE POSITIVE LEG, first on purpose.

    The defect this names is a FAIL-OPEN in the gate itself, and it is specific:
    `select_targets` adds `t for t in CONTROL_TESTS if (ROOT / t).exists()`. A member RENAMED or
    MOVED by other work leaves its line here pointing at nothing, and that entry is then dropped
    IN SILENCE -- no error, no warning, a green gate, and a control that has stopped running for
    the same reason it never ran before. Nothing else in this file would notice: the census
    discharges a path by string, not by whether it resolves.

    A line DELETED from the batch is a different defect and a different control --
    `test_the_strict_census_stays_discharged` below is what catches that one, because the member
    reappears in the census the moment its line goes.
    """
    selected = set(gate.select_targets([NEW_MODULE]))
    missing = [t for t in CENSUSED_WHOLE_DIRECTORY_SUBJECTS if t not in selected]
    assert not missing, (
        "a new module selects NONE of these censused whole-directory controls, so the commit that "
        "breaks them cannot run them:\n  " + "\n  ".join(missing))


def test_every_member_still_earns_its_place_by_scanning_a_whole_directory():
    """Each member's OWN source is re-run through the census predicate.

    The defect this names: a member narrowed to a population a stem selector CAN reach keeps
    costing every commit for a reason that has stopped being true. The remedy is one deleted line,
    in the change that narrowed it -- the same maintenance rule the seam ratchet already carries.

    HONEST ABOUT ITS OWN REACH, because the alternative is a comment that oversells it: this file
    is selected by an edit to `tools/pre_commit_test_gate.py`, not by an edit to a member, so it
    catches that drift late. That is proportionate here and would not be elsewhere -- the failure
    it guards costs seconds on a hook, not a blind control.
    """
    unearned = {}
    for member in CENSUSED_WHOLE_DIRECTORY_SUBJECTS:
        hit = wtsc.classify_source((ROOT / member).read_text(encoding="utf-8", errors="replace"))
        if hit is None:
            unearned[member] = "no longer walks a source tree and bounds it against a literal"
        elif not hit["strict_dataflow"]:
            unearned[member] = "the walk is no longer provably the counted population"
        elif not hit["subject_roots"]:
            unearned[member] = "names no subject root"
    assert not unearned, (
        "these entries no longer meet the predicate that earned them a place on an always-run "
        "list; delete the line in the change that narrowed the test:\n  "
        + "\n  ".join(f"{k}: {v}" for k, v in unearned.items()))


def test_the_strict_census_stays_discharged():
    """THE NINETEENTH. The one thing the eighteen do not fix by themselves.

    Adding lines one at a time closed this class ten times and never once stopped the next instance
    being written; the pool grew to eighteen behind those ten fixes. While the pool was non-empty a
    control here could not have helped -- it would have been red on arrival, naming work it could
    not do, which is why the previous turn declined it. The pool is zero at this commit, so the
    argument changes: from here a new whole-directory-subject test with a stem-only selector is a
    ONE-line omission, and this says so at the commit that makes it instead of fourteen days later.

    Deliberately the STRICT set only. The 91 loose members are not owed a line each -- the predicate
    over-counts by construction (legs 1 and 2 are proximity in a module, not dataflow) and a control
    over the loose pool would refuse honest work for a reason it could not defend.

    ~2.9s, an AST walk of every tracked test file. Stated rather than glossed, against the standing
    hook budget, like every other entry on that list.
    """
    owed = wtsc.unreachable([r for r in wtsc.census() if r["strict_dataflow"]])
    assert not owed, (
        "a test whose subject is a whole directory has no selector but its own filename stem, so "
        "the commit that breaks it cannot run it. Add it to "
        "`pre_commit_test_gate.CENSUSED_WHOLE_DIRECTORY_SUBJECTS` in THIS change, with its cost:\n  "
        + "\n  ".join(f"{r['test']}  subject: {', '.join(r['subject_roots'])}" for r in owed))


def test_this_control_is_itself_on_the_always_run_list():
    """The guard above has every test file for a subject, so it is its own class's next instance.

    The defect this names is the one the census exists for, aimed at the census's own guard: left
    stem-selected, `test_the_strict_census_stays_discharged` would run only when someone edited the
    gate -- never on the commit that adds the nineteenth control. A guard against this class that
    is itself unreachable is the joke this repo has already paid for twice.
    """
    rel = str(Path(__file__).resolve().relative_to(ROOT))
    assert rel in gate.CONTROL_TESTS, (
        f"{rel} guards the whole-directory-subject class and is not on CONTROL_TESTS, so the "
        "commit that adds the next member cannot run it")


def test_the_batch_constant_is_not_re_typed_anywhere():
    """One population, one definition -- the rule the census states for its own read of the list.

    The defect this names: a second copy of these eighteen paths, in a test or a tool, that agrees
    today and diverges the moment either side is edited, with the divergence favouring whichever
    file was touched last. Nothing here spells a member out; every assertion above walks the
    imported constant.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = {
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
        and n.value.startswith("tests/") and n.value.endswith(".py")
    }
    assert not literals & set(CENSUSED_WHOLE_DIRECTORY_SUBJECTS), (
        "a batch member is spelled out as a literal in this file; import the constant instead so "
        f"the two cannot drift apart: {sorted(literals & set(CENSUSED_WHOLE_DIRECTORY_SUBJECTS))}")
