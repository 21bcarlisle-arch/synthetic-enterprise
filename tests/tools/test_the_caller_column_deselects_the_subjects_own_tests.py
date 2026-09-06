"""The defect: `direct_suites` excludes the subject's own tests one WHOLE FILE at a time, and
`background/direction.py` is the subject that proved a file need not be all one thing.

All four of `direction`'s caller columns import it at module level, and all four are legitimately
the dedicated suite of a module that calls it -- so `b3938b313` ran the census before writing the
caller-verdict gate, found that "imports the subject" would have condemned a correct spec, and
shipped no gate on that discriminator. Asked per TEST the question is decidable: 23 tests across
three of those files assert against `d.validate`, `d.wrong_rows` and `d.focus_multiplier` and never
call the module their file is named for. `tests/background/test_delivery_lane.py` holds one of each
-- one test of the subject and one of the caller -- so no file-level split can keep both, and that
file is why `direct_nodes` exists at all.

These are the controls on the node-grain exclusion, keyed to the PROPERTY -- which tests a column
runs, and which rounds honour it -- and not to `direction`'s current membership, which changes
whenever a contract is repaired.
"""
from __future__ import annotations

import importlib

from tools.contract_battery import BatterySpec

CALLER = "tests/fake/test_caller_a.py"
CALLER_B = "tests/fake/test_caller_b.py"
OWN = "tests/fake/test_the_subjects_own_suite.py"
REPAIR = "tests/fake/test_the_repair.py"
MINE = f"{CALLER}::test_a_contract_of_the_SUBJECT"
THEIRS = f"{CALLER_B}::test_a_contract_of_the_SUBJECT"
IN_OWN = f"{OWN}::test_a_contract_of_the_SUBJECT"


def _spec(**over) -> BatterySpec:
    base = dict(
        name="fake",
        subject="tools/fake_subject.py",
        suites=(CALLER, CALLER_B),
        direct_suites=(OWN,),
        repair_suite=REPAIR,
        direct_nodes=(MINE, THEIRS, IN_OWN),
        mutations=(("M1", "a contract", "old", "new"),),
        poison_old="old",
        poison_new="raise",
    )
    base.update(over)
    return BatterySpec(**base)


def test_the_whole_PARTITION_of_deselection_outcomes_is_REACHABLE_before_any_leg_says_what_it_does():
    """THE PARTITION CONTROL, and it runs first. Every leg below asks "does `deselect_for` exclude
    correctly", and an implementation that returned the baseline reds and NOTHING else would
    satisfy the two negative legs while failing only the positive one -- while one that returned
    every node for every suite would fail only the negatives. CLAUDE.md asks for one control over
    the whole partition rather than a leg per branch.

    Four outcomes, all asserted to be genuinely distinct here: a caller loses its own node; a
    caller does not lose ANOTHER file's node; a direct column loses nothing; baseline reds survive
    in every column.
    """
    spec = _spec()
    red = ("tests/fake/test_caller_a.py::test_already_red_at_head",)

    caller = spec.deselect_for(CALLER, red)
    other_caller = spec.deselect_for(CALLER_B, ())
    own = spec.deselect_for(OWN, red)
    repair = spec.deselect_for(REPAIR, ())

    assert caller == red + (MINE,)
    assert other_caller == (THEIRS,)
    assert own == red
    assert repair == ()
    # ...and the four are DISTINGUISHABLE, or the property would hold for a function that
    # returned one answer for everything.
    assert len({caller, other_caller, own, repair}) == 4


def test_a_node_is_deselected_only_from_the_FILE_IT_NAMES_and_not_from_every_caller():
    """THE FAIL-CLOSED-TOO-HARD SHAPE. `direct_nodes` is one flat tuple across the whole spec, so
    the obvious implementation hands all of it to every caller column. pytest's `--deselect` for a
    node in a file that is not being collected is silently accepted, so nothing would ever fail --
    the column would simply run fewer tests than the spec says and the run would look identical.

    Live risk on `direction`: 22 of its 23 nodes name files other than `test_delivery_lane.py`,
    and the lane column's real caller test would have been the only thing left standing either
    way, which is exactly why this could not have been noticed from the results.
    """
    assert spec_nodes(_spec().deselect_for(CALLER, ())) == {MINE}
    assert spec_nodes(_spec().deselect_for(CALLER_B, ())) == {THEIRS}


def test_the_subjects_OWN_columns_keep_their_own_tests_or_they_would_measure_nothing():
    """The exclusion is one-directional and this is the leg that says so. `direct_suites` and
    `repair_suite` exist to report what the subject's own tests prove; deselecting the subject's
    own tests from them empties precisely the thing they measure, and the column would report
    `survived` for every contract while looking like a column that ran.

    The inverse of the defect above, and the reason `deselect_for` keys on `suite in self.suites`
    rather than on the node's filename alone."""
    spec = _spec()

    assert IN_OWN not in spec.deselect_for(OWN, ())
    assert spec.deselect_for(OWN, ()) == ()
    assert spec.deselect_for(REPAIR, ()) == ()


def test_declaring_ONE_MORE_node_changes_the_FINGERPRINT():
    """A resumed row keeps the verdict it was written with -- `run()` skips a mutation whose cells
    are all present and never re-reduces it. Declaring a test as the subject's own leaves `suites`
    and `direct_suites` untouched and every recorded cell measuring exactly what it measured
    before; what changes is what `survived_all` MEANS. Drop `direct_nodes` from the hashed payload
    and a re-split spec silently inherits rows scored under the old one.

    Measured rather than assumed: this is the same hole that survived on `direct_suites` until a
    leg compared two specs differing in that field alone."""
    from tools.contract_battery import fingerprint

    base = _spec(direct_nodes=(MINE,))
    wider = _spec(direct_nodes=(MINE, THEIRS))

    assert fingerprint(base) != fingerprint(wider)
    # ...and identical splits still collide, or this would prove only that "any two specs differ"
    # and would be refusing every resume rather than this move.
    assert fingerprint(base) == fingerprint(_spec(direct_nodes=(MINE,)))


def test_EVERY_ROUND_THAT_GRADES_A_COLUMN_HONOURS_THE_DESELECTION_not_only_the_mutations():
    """THE FAIL-OPEN, and it is the one worth a control rather than a comment.

    The poison round decides `reaches_subject`, and every survivor in a blind column is stamped
    `survived_but_unreachable` off that verdict. Run the floor over the FULL file while the
    mutation rounds run the deselected subset and a column whose only subject-reaching tests are
    `direct_nodes` is stamped `reaches` on the strength of tests no later round executes -- so its
    survivors read UNPROVED when the honest reading is UNREACHABLE. That is the exact confusion
    the floor exists to prevent, let in through the floor itself.

    Asserted over the SOURCE of every `_run_suite` call site, because the alternative is running
    four subprocess rounds to observe an argument. A new round added beside these three that
    hand-rolls `known_red` regresses the repair, which is the shape this project keeps finding.

    MUTATION (must fire): revert any one of the poison, hard-poison or null call sites to
    `known_red.get(suite, ())`.
    """
    import inspect

    from tools import contract_battery

    source = inspect.getsource(contract_battery)
    graded = source.count("_run_suite(suite, spec.deselect_for(")
    # The baseline is the ONE round that must NOT deselect: its reds are what later rounds
    # deselect, and a baseline blind to a red in a direct node could not record it.
    assert "_run_suite(suite, (), stop_first=False)" in source, "the baseline still runs the file"
    assert graded == 4, (
        f"{graded} of the 4 grading rounds (poison, hard poison, null, mutation) route through "
        "deselect_for; one that hand-rolls known_red grades a population the others do not"
    )
    assert "known_red.get(suite, ())," not in source, (
        "a grading round still passes the baseline reds alone and skips the node exclusion"
    )


def test_every_declared_node_NAMES_A_TEST_THAT_EXISTS_in_a_suite_the_spec_scores():
    """The census, over the live specs rather than a fixture. A node id that has gone stale --
    a renamed test, a moved file -- is silently accepted by `--deselect` and quietly stops
    excluding anything, so the column drifts back to grading the subject with the subject's own
    tests and no run ever says so.

    Keyed to the property and not to today's membership: it stays green as nodes are added or
    removed and reds the moment one names a test the tree does not have."""
    import ast
    import pathlib

    from tools.contract_battery import PROJECT

    for name in ("company_data", "direction", "grid_intensity_feed", "ops_repo",
                 "segment_vocabulary"):
        spec = importlib.import_module(f"tools.{name}_contract_battery").SPEC
        for node in spec.direct_nodes:
            path, _, test = node.partition("::")
            assert path in spec.selectable, f"{name}: {node} names a suite this spec never runs"
            source = (PROJECT / path).read_text(encoding="utf-8")
            names = {n.name for n in ast.walk(ast.parse(source))
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            assert test in names, f"{name}: {node} names a test that does not exist"
            assert pathlib.Path(PROJECT / path).exists()


def spec_nodes(deselected: tuple[str, ...]) -> set[str]:
    return {n for n in deselected if "::" in n}
