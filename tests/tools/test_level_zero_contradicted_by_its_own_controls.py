"""R15 contract for the level-zero contradiction check.

THE DEFECT IT EXISTS TO CATCH, reproduced in miniature by `test_a_row_at_zero_whose_named_
controls_all_pass_is_REFUSED`: an atom at `level_current: 0`, `loop_stage: build`, naming a test
file that exists and passes. The map is asserting nothing is built about work its own evidence
says is done, and `tools/lane_formation.py` reads exactly those two fields to decide what is
still buildable -- so the row keeps winning draws it has already been paid for.

THE POISON ROUND IS FIRST AND IT IS NOT DECORATION. Every other test here is a NEGATIVE leg --
"this row does not refuse" -- and a check that refuses NOTHING passes all of them. This project
has shipped that shape repeatedly. `test_all_six_verdicts_are_reachable_in_one_pass` is the one
control over the whole partition: it asserts in a single `assess` call that the refusing branch
FIRES, that all four ungradable branches fire, and that the silent branch is silent. If the
refusing branch is ever made unreachable, that assertion goes red and the negative legs below stay
green -- which is the whole point of writing it as one assertion rather than six.

THE DEFECT THE 2026-09-06 LEGS EXIST TO CATCH is the opposite failure and it was live: the check
REFUSED a row on evidence older than the row. `H41_the_map_ratchet_has_no_ongoing_drain` names a
suite born five days before the atom was minted, whose 41 tests pass, and whose subject -- an
ongoing drain -- demonstrably does not exist. Dating is what tells "this atom's build wrote this
control" from "this control was already green". `_ages` is injected for the same reason `_runner`
is; `test_the_dating_function_reads_real_git_history_in_both_orders` is what proves the real one,
because a stub cannot fail in the way the git query can.

WHY THE UNGRADABLE BRANCHES MATTER AS MUCH AS THE REFUSAL. Of the 34 candidate rows in the live
map, ten name a control file at all and four of those ten name one that is not on disk -- two of
the four being the instances this check was built for. Grading the surviving members of a set the
row describes wrongly would publish a verdict about a different set.
`test_an_absent_named_control_makes_the_row_ungradable_ENTIRE` pins that, and it is the leg most
likely to be "simplified" away by someone who reads the absent path as a false positive.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools import level_zero_contradicted_by_its_own_controls as lz

REPO = Path(lz.__file__).resolve().parent.parent


def _atom(aid: str, *, level: int = 0, stage: str = "build", scope=()) -> dict:
    return {"id": aid, "level_current": level, "loop_stage": stage,
            "lane": "T_test", "level_target": 3, "file_scope": list(scope)}


def _runner(verdicts: dict):
    """An injected runner keyed on the tuple of paths it is handed, so a test states its own
    world instead of depending on whatever the real suite happens to do today."""
    def run(paths, root=REPO, timeout_s=0):
        return verdicts[tuple(paths)]
    return run


def _ages(predating: dict | None = None, undatable: dict | None = None):
    """An injected dating function, same reason as `_runner`: a tmp_path is not a git repository,
    so the real one would report every row undatable and no test below could reach any other
    branch. Default: every named control was written no earlier than its row."""
    predating = predating or {}
    undatable = undatable or {}
    def ages(atom_id, controls, root=REPO):
        return list(predating.get(atom_id, [])), list(undatable.get(atom_id, []))
    return ages


# --------------------------------------------------------------------------- #
# The poison round: the refusing branch can FIRE                               #
# --------------------------------------------------------------------------- #

def test_all_six_verdicts_are_reachable_in_one_pass(tmp_path: Path):
    """One control over the whole partition. A guard that refuses nothing passes every negative
    leg below; this is the assertion that cannot be satisfied by a dead refusing branch.

    IT GREW FROM FOUR TO SIX ON 2026-09-06 and that is the point of writing it as one assertion:
    the two dating branches were added underneath it, and a partition control that kept saying
    "four" would have gone on passing while a third of the branches went ungraded."""
    (tmp_path / "test_green.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_red.py").write_text("def test_x():\n    assert False\n")
    (tmp_path / "test_old.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_undated.py").write_text("def test_x():\n    assert True\n")

    atoms = [
        _atom("REFUSES", scope=["test_green.py"]),
        _atom("SILENT", scope=["test_red.py"]),
        _atom("UNGRADABLE_ABSENT", scope=["test_never_written.py"]),
        _atom("UNGRADABLE_NONE", scope=["tests/", "some/module.py"]),
        _atom("UNGRADABLE_OLDER", scope=["test_old.py"]),
        _atom("UNGRADABLE_UNDATED", scope=["test_undated.py"]),
    ]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path,
        runner=_runner({("test_green.py",): (True, "1 passed"),
                        ("test_red.py",): (False, "1 failed"),
                        # Both dating branches must return BEFORE the run: were either to fall
                        # through to the runner it would pass, and a passing set refuses.
                        ("test_old.py",): (True, "1 passed"),
                        ("test_undated.py",): (True, "1 passed")}),
        ages=_ages(predating={"UNGRADABLE_OLDER": ["test_old.py"]},
                   undatable={"UNGRADABLE_UNDATED": ["test_undated.py"]}))

    fired = {c["id"] for c in contradicted}
    could_not_grade = {u["id"]: u["reason"] for u in ungradable}
    assert (
        fired == {"REFUSES"}
        and could_not_grade == {"UNGRADABLE_ABSENT": lz.NAMED_CONTROL_ABSENT,
                                "UNGRADABLE_NONE": lz.NO_CONTROL_NAMED,
                                "UNGRADABLE_OLDER": lz.CONTROL_PREDATES_ROW,
                                "UNGRADABLE_UNDATED": lz.PROVENANCE_UNKNOWN}
    ), (
        "the partition is not fully reachable -- fired={} ungradable={}".format(
            fired, could_not_grade))


def test_a_row_at_zero_whose_named_controls_all_pass_is_REFUSED(tmp_path: Path):
    """PB6's shape once its scope points at the file the build actually wrote."""
    (tmp_path / "test_it.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("PB6_shape", scope=["test_it.py"])]
    contradicted, _ = lz.assess(
        atoms, root=tmp_path, ages=_ages(),
        runner=_runner({("test_it.py",): (True, "3 passed")}))
    assert [c["id"] for c in contradicted] == ["PB6_shape"]


def test_the_cli_exits_nonzero_when_a_row_contradicts_itself(monkeypatch, capsys):
    """The refusal has to reach a caller as an exit code, not only as a return value."""
    monkeypatch.setattr(lz.map_store, "load_live_atoms",
                        lambda: [_atom("SELF_CONTRADICTING", scope=["tests/t/test_a.py"])])
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [{"id": "SELF_CONTRADICTING", "lane": "T", "level_target": 3,
          "paths": ["tests/t/test_a.py"], "detail": "1 passed"}], []))
    assert lz.main([]) == 1
    assert "SELF_CONTRADICTING" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# It stays quiet where the map and the controls agree                          #
# --------------------------------------------------------------------------- #

def test_a_row_whose_named_controls_do_not_all_pass_says_nothing(tmp_path: Path):
    """The map says unbuilt and the evidence says unbuilt. Agreement is not a finding."""
    (tmp_path / "test_a.py").write_text("def test_x():\n    assert False\n")
    atoms = [_atom("HONEST_ZERO", scope=["test_a.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(),
        runner=_runner({("test_a.py",): (False, "1 failed")}))
    assert contradicted == [] and ungradable == []


def test_a_row_above_level_zero_is_outside_the_partition(tmp_path: Path):
    """`tools/scope_evidence_ratchet.py` owns level>0. This check must not double-grade it.

    The control file EXISTS and PASSES here, so the row is excluded by its level alone -- were
    the partition widened, this would land in `contradicted` rather than going quietly absent.
    """
    (tmp_path / "test_a.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("ALREADY_MOVED", level=2, scope=["test_a.py"])]
    called = []
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(),
        runner=lambda p, r=None, t=None: called.append(p) or (True, ""))
    assert contradicted == [] and ungradable == [] and called == []


def test_an_idle_row_at_zero_is_outside_the_partition(tmp_path: Path):
    """A parked proposal naming the files it WOULD create is the map describing future work --
    the case `scope_evidence_ratchet` argues at length must stay legal. `loop_stage: build` is
    what makes the row a claim about work in progress.

    Same construction as the level leg: the named control exists and passes, so `idle` is the
    only thing keeping this row out of the refusal.
    """
    (tmp_path / "test_a.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("PARKED_PROPOSAL", stage="idle", scope=["test_a.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(),
        runner=_runner({("test_a.py",): (True, "1 passed")}))
    assert contradicted == [] and ungradable == []


# --------------------------------------------------------------------------- #
# What counts as a control named in the row                                    #
# --------------------------------------------------------------------------- #

def test_an_absent_named_control_makes_the_row_ungradable_ENTIRE():
    """PB4 and PB6's live shape: two named controls, one of them a name no build ever wrote.

    Grading the survivor would publish a verdict about a set the row does not describe -- and
    the surviving member passing is exactly how a row with a stale path would get promoted on
    evidence that is not the evidence it names.
    """
    atoms = [_atom("STALE_PATH", scope=["tools/level_zero_contradicted_by_its_own_controls.py",
                                        "tests/company/test_a_name_nobody_wrote.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=REPO, runner=lambda *a, **k: (True, "must not be reached"))
    assert contradicted == []
    assert [u["reason"] for u in ungradable] == [lz.NAMED_CONTROL_ABSENT]
    assert ungradable[0]["paths"] == ["tests/company/test_a_name_nobody_wrote.py"]


def test_a_directory_is_scope_and_never_a_named_control():
    """`H40_full_suite_pollution_bisect` names `tests/`. Grading it against the whole suite
    would make every lane's green H40's evidence -- a verdict about the repository wearing an
    atom's name."""
    assert lz.named_controls(_atom("H40", scope=["tests/", "tests/simulation", "tools/x.py"])) == []
    assert lz.named_controls(_atom("D27", scope=["tests/tools/test_couple.py", "tools/x.py"])) == [
        "tests/tools/test_couple.py"]


# --------------------------------------------------------------------------- #
# A control older than its row is not evidence about its row                    #
# --------------------------------------------------------------------------- #

def test_a_control_older_than_its_row_is_UNGRADABLE_and_never_a_contradiction(tmp_path: Path):
    """H41's live shape. The named suite passes -- so the pre-2026-09-06 check called the row
    CONTRADICTED and demanded a level move for work that had not happened.

    The runner is rigged to (True, ...) ON PURPOSE: if the dating branch is ever moved to AFTER
    the run, or deleted, this row lands in `contradicted` and the assertion below goes red. A
    version of this test that stubbed the runner as unreachable would pass even then."""
    (tmp_path / "test_older.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("H41_shape", scope=["test_older.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=lambda *a, **k: (True, "41 passed"),
        ages=_ages(predating={"H41_shape": ["test_older.py"]}))
    assert contradicted == [], "a suite older than its row refused a level move on its strength"
    assert [(u["reason"], u["paths"]) for u in ungradable] == [
        (lz.CONTROL_PREDATES_ROW, ["test_older.py"])]


def test_provenance_that_cannot_be_established_is_UNGRADABLE_and_never_a_contradiction(
        tmp_path: Path):
    """A shallow clone or a `git archive` extract can date nothing. Unknown must fall to the
    non-refusing side: the refusing verdict is the one that demands work of someone."""
    (tmp_path / "test_undated.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("NO_HISTORY", scope=["test_undated.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=lambda *a, **k: (True, "1 passed"),
        ages=_ages(undatable={"NO_HISTORY": ["test_undated.py"]}))
    assert contradicted == []
    assert [u["reason"] for u in ungradable] == [lz.PROVENANCE_UNKNOWN]


def test_the_dating_function_reads_real_git_history_in_both_orders(tmp_path: Path):
    """`_ages` proves `assess`; this proves `controls_older_than_the_row`, which nothing else here
    executes. ONE repository, BOTH orders, so a function that answered "predating" unconditionally
    -- or never -- fails on one half whichever way it is broken.

    An UNDATABLE leg rides along in the same repo: a control on disk that git has never seen is a
    third answer, and collapsing it into "predating" would print a claim about age that nothing
    measured. So does the SAME-COMMIT leg, which is SITE4's live shape -- a build that mints its
    row and writes its control in one commit is the healthy case and must not read as predating.

    THE DATES ARE STAMPED EXPLICITLY, not taken from the wall clock. Git timestamps are whole
    seconds and three commits made as fast as a test makes them share one, which made the first
    draft of this test pass for the wrong reason -- everything looked simultaneous."""
    import subprocess as sp

    def git(*args, when: str | None = None):
        env = None
        if when:
            env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        sp.run(["git", *args], cwd=str(tmp_path), check=True,
               capture_output=True, text=True, env=env)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "docs" / "design").mkdir(parents=True)
    mapfile = tmp_path / "docs" / "design" / "maturity_map.yaml"

    # 1. The OLD control lands first, before any row exists.
    # DISTINCT CONTENT per file, and that is not tidiness: `--follow` detects renames by
    # SIMILARITY, so three byte-identical fixtures make git chase each new file back to the
    # oldest one and every leg reads "predating". Measured -- the first draft did exactly that.
    (tmp_path / "test_old.py").write_text("def test_the_old_one():\n    assert 1 == 1\n")
    git("add", "test_old.py")
    git("commit", "-qm", "a suite that predates every row", when="2026-01-01T00:00:00Z")

    # 2. The rows are minted -- and TWIN_ROW's control is written in the SAME commit, as a build
    #    that mints and builds together does.
    mapfile.write_text("- id: LATE_ROW\n- id: EARLY_ROW\n- id: TWIN_ROW\n")
    (tmp_path / "test_twin.py").write_text("def test_the_twin():\n    assert 2 + 2 == 4\n")
    git("add", "-A")
    git("commit", "-qm", "mint the rows; build TWIN_ROW", when="2026-02-01T00:00:00Z")

    # 3. The NEW control is written afterwards, as an atom's own build would write it.
    (tmp_path / "test_new.py").write_text(
        "def test_the_new_one():\n    assert sorted([3, 1, 2]) == [1, 2, 3]\n")
    git("add", "test_new.py")
    git("commit", "-qm", "build(LATE_ROW): its own control", when="2026-03-01T00:00:00Z")

    # 4. And one git has never seen at all.
    (tmp_path / "test_untracked.py").write_text(
        "def test_never_committed():\n    assert {'a': 1}['a'] == 1\n")

    born_after = lz.controls_older_than_the_row("LATE_ROW", ["test_new.py"], root=tmp_path)
    born_before = lz.controls_older_than_the_row("EARLY_ROW", ["test_old.py"], root=tmp_path)
    born_with = lz.controls_older_than_the_row("TWIN_ROW", ["test_twin.py"], root=tmp_path)
    never_seen = lz.controls_older_than_the_row("LATE_ROW", ["test_untracked.py"], root=tmp_path)

    assert born_after == ([], []), "a control written AFTER its row was called older than it"
    assert born_before == (["test_old.py"], []), (
        "a control that existed before its row was minted was accepted as evidence about it")
    assert born_with == ([], []), (
        "SITE4's shape -- row and control in ONE commit -- must not read as predating")
    assert never_seen == ([], ["test_untracked.py"]), (
        "an undatable control must be its own answer, not folded into 'older than the row'")


def test_an_unfindable_row_makes_every_control_undatable_rather_than_none_predating(
        tmp_path: Path):
    """The fail-open reading this forbids: "no predating controls" out of "I could not date the
    row". An atom id no commit mentions must not come back as a clean bill of health."""
    import subprocess as sp
    sp.run(["git", "init", "-q", "-b", "main"], cwd=str(tmp_path), check=True, capture_output=True)
    assert lz.controls_older_than_the_row(
        "AN_ID_NO_COMMIT_MENTIONS", ["a.py", "b.py"], root=tmp_path) == ([], ["a.py", "b.py"])


# --------------------------------------------------------------------------- #
# No verdict is never a pass                                                   #
# --------------------------------------------------------------------------- #

def test_a_run_that_reaches_no_verdict_is_ungradable_and_never_a_contradiction(tmp_path: Path):
    """A timeout or a runner that will not start must not promote an atom. Only "everything
    passed" refuses, so the fail-closed direction here is silence plus a finding."""
    (tmp_path / "test_a.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("TIMED_OUT", scope=["test_a.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(),
        runner=lambda *a, **k: (None, "timed out after 900s"))
    assert contradicted == []
    assert [u["reason"] for u in ungradable] == [lz.RUN_UNAVAILABLE]


def test_the_real_runner_separates_a_passing_file_from_a_failing_one_and_from_an_empty_one(
        tmp_path: Path):
    """The injected runner above proves `assess`; this proves `run_controls` itself, which no
    other test in this file executes. An empty file collects nothing, and nothing is not a pass
    -- otherwise a control file emptied of its tests promotes its atom."""
    (tmp_path / "test_green.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_red.py").write_text("def test_x():\n    assert False\n")
    (tmp_path / "test_empty.py").write_text("# no tests here\n")
    green, _ = lz.run_controls(["test_green.py"], root=tmp_path, timeout_s=120)
    red, _ = lz.run_controls(["test_red.py"], root=tmp_path, timeout_s=120)
    empty, _ = lz.run_controls(["test_empty.py"], root=tmp_path, timeout_s=120)
    assert (green, red, empty) == (True, False, None)


def test_a_mixed_set_run_together_is_not_a_pass(tmp_path: Path):
    """One invocation over the whole named set, and `-x` deliberately absent. A set with a red
    member is a red set however the members are ordered."""
    (tmp_path / "test_green.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_red.py").write_text("def test_x():\n    assert False\n")
    assert lz.run_controls(["test_green.py", "test_red.py"], root=tmp_path, timeout_s=120)[0] is False
    assert lz.run_controls(["test_red.py", "test_green.py"], root=tmp_path, timeout_s=120)[0] is False


# --------------------------------------------------------------------------- #
# Against the live map, keyed to the property and not to today's answer        #
# --------------------------------------------------------------------------- #

def test_every_verdict_names_a_live_atom_actually_in_the_partition():
    """Keyed to the PROPERTY, not to which rows are red today: a control pinned to the current
    list goes red the moment the map becomes more honest. What must hold forever is that this
    check never reports a row it has no business speaking about."""
    from tools import maturity_map_store as map_store
    atoms = map_store.load_live_atoms()
    candidates = {a["id"] for a in atoms if lz.is_candidate(a)}
    graded = {a["id"] for a in atoms
              if lz.is_candidate(a) and lz.named_controls(a)}
    contradicted, ungradable = lz.assess(
        atoms, root=REPO, runner=lambda *a, **k: (None, "not run in this control"))
    reported = {c["id"] for c in contradicted} | {u["id"] for u in ungradable}
    assert reported <= candidates, "reported a row outside level-0/build: {}".format(
        reported - candidates)
    assert candidates <= reported, (
        "every level-0/build row gets a verdict or a stated reason; silent on: {}".format(
            candidates - reported))
    assert graded, "no live row names a control file at all -- the check has nothing to grade"


# --------------------------------------------------------------------------- #
# The whole pass is bounded, and a row the budget missed is not a clean row     #
# --------------------------------------------------------------------------- #

def test_a_row_the_budget_never_reached_is_UNGRADABLE_and_never_silently_dropped(tmp_path: Path):
    """The fail-silent shape: the pass stops early, the unreached rows vanish from both lists,
    and the caller reads a clean map. Measured, not reasoned -- the first unbudgeted run against
    the live tree was still going at seven minutes with six gradable rows and a 120s per-atom
    cap, which is long enough to wedge `background/delivery_seat.py`'s three-hourly brief."""
    for name in ("test_a.py", "test_b.py", "test_c.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    atoms = [_atom("FIRST", scope=["test_a.py"]),
             _atom("SECOND", scope=["test_b.py"]),
             _atom("THIRD", scope=["test_c.py"])]

    ticks = iter([0, 0, 10, 99])           # start, FIRST, SECOND, THIRD -- budget 50 bites third
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(), runner=lambda *a, **k: (True, "1 passed"),
        budget_s=50, clock=lambda: next(ticks))

    assert [c["id"] for c in contradicted] == ["FIRST", "SECOND"]
    assert [(u["id"], u["reason"]) for u in ungradable] == [("THIRD", lz.BUDGET_EXHAUSTED)], (
        "the row the budget did not reach must be REPORTED, not dropped -- a check that quietly "
        "stops early tells its caller the map is clean")


def test_no_budget_means_every_row_is_reached(tmp_path: Path):
    """The default path must not be silently truncated by a budget nobody asked for."""
    for name in ("test_a.py", "test_b.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    atoms = [_atom("FIRST", scope=["test_a.py"]), _atom("SECOND", scope=["test_b.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(), runner=lambda *a, **k: (True, "1 passed"))
    assert [c["id"] for c in contradicted] == ["FIRST", "SECOND"] and ungradable == []


# --------------------------------------------------------------------------- #
# A contradicted row may be UNMOVABLE, and the remedy printed has to know       #
# --------------------------------------------------------------------------- #

def test_BOTH_freeze_states_are_reachable_in_one_pass(tmp_path: Path):
    """The poison round for this leg, over the whole partition in one assertion.

    A probe that answered "frozen" for everything would pass every negative leg below, and one
    that answered "clear" for everything would pass every positive one. Only asserting that the
    same pass produces both, plus the unreadable third state, can fail either way.

    It is written over `frozen_by` and not over the printed text because the SEAT reads the
    field: `background/delivery_seat.py` splits its brief on exactly this key.
    """
    for name in ("test_a.py", "test_b.py", "test_c.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    atoms = [
        {**_atom("MOVABLE", scope=["test_a.py"]), "lane": "CLEAR_LANE"},
        {**_atom("FROZEN", scope=["test_b.py"]), "lane": "BLOCKED_LANE"},
        {**_atom("LANELESS", scope=["test_c.py"]), "lane": None},
    ]
    contradicted, _ = lz.assess(
        atoms, root=tmp_path, ages=_ages(), runner=lambda *a, **k: (True, "1 passed"),
        blockers_for=lambda lane: ["FINDING_X.md", "FINDING_Y.md"] if lane == "BLOCKED_LANE" else [])

    assert {c["id"]: c["frozen_by"] for c in contradicted} == {
        "MOVABLE": [],
        "FROZEN": ["FINDING_X.md", "FINDING_Y.md"],
        "LANELESS": [lz.BLOCKERS_UNREADABLE],
    }, "the freeze states are not all reachable: {}".format(
        [(c["id"], c["frozen_by"]) for c in contradicted])


def test_a_frozen_row_is_still_CONTRADICTED_and_still_exits_nonzero(monkeypatch, capsys):
    """The freeze says who has to move first. It is never permission for the row to stay wrong,
    and the exit code is the only part of this a caller reads without a human."""
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: [])
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [{"id": "FROZEN_ROW", "lane": "H_harness", "level_target": 2,
          "paths": ["site/test_x.py"], "detail": "38 passed", "frozen_by": ["FINDING_X.md"]}], []))

    assert lz.main([]) == 1
    err = capsys.readouterr().err
    assert "FROZEN_ROW" in err and "FINDING_X.md" in err
    assert "Do not attempt the recording" in err, (
        "a frozen row printed under the RECORD-the-level instruction sends the reader at an "
        "OPS11 refusal -- which is the turn this leg exists to save")


def test_the_two_groups_carry_DIFFERENT_instructions(monkeypatch, capsys):
    """One pass holding both kinds must not collapse them into one paragraph. Written as the
    difference rather than as two substring checks, because a footer naming both remedies under
    every row would satisfy those and teaches the reader nothing."""
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: [])
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [{"id": "MOVABLE_ROW", "lane": "E_finance_treasury", "level_target": 2,
          "paths": ["tests/x/test_a.py"], "detail": "3 passed", "frozen_by": []},
         {"id": "FROZEN_ROW", "lane": "H_harness", "level_target": 2,
          "paths": ["site/test_x.py"], "detail": "38 passed", "frozen_by": ["FINDING_X.md"]}], []))

    lz.main([])
    err = capsys.readouterr().err
    movable_at = err.index("MOVABLE_ROW")
    frozen_at = err.index("FROZEN_ROW")
    assert movable_at < frozen_at
    assert err.index("record_level_up_self_certified") < frozen_at, (
        "the recording instruction must sit with the movable group, above the frozen one")
    assert err.index("record_limitation_accepted") > frozen_at


def test_an_unreadable_lane_is_FROZEN_and_never_movable():
    """Fail-closed in the direction that costs the reader nothing. Being told 'record this' on no
    information is the outcome; being sent to look at a lane that turns out to be clear is not."""
    def boom(lane):
        raise OSError("the severity index could not be listed")

    assert lz.frozen_by("ANY_LANE", boom) == [lz.BLOCKERS_UNREADABLE]
    assert lz.frozen_by("", lambda lane: []) == [lz.BLOCKERS_UNREADABLE]
    assert lz.frozen_by("A_LANE", lambda lane: []) == []


def test_the_probe_asks_the_SAME_mechanism_OPS11_refuses_with(tmp_path: Path):
    """Not a second reading of the staging directory. If this drifts from
    `gate_authorization.lane_blockers`, the check can print MOVABLE over a row whose recording
    then raises -- the two-implementations-of-one-rule shape this repo keeps paying for.

    Run against the live tree, keyed to agreement rather than to today's blocker list. The claim
    is the UNION over both trees, not the working copy alone: until 2026-09-15 this asserted
    equality with the working copy, which is what let the scan call `SITE4` movable while the gate
    refused it on nine findings still live at `HEAD`. Equality with either tree ALONE is now the
    defect, so this asserts both halves are contained and nothing else is invented.
    """
    from background.gate_authorization import lane_blockers
    from tools import maturity_map_store as map_store

    lanes = {a.get("lane") for a in map_store.load_live_atoms() if a.get("lane")}
    assert lanes, "no lane to check agreement on"
    head = lz._head_staging_root(lz.ROOT, tmp_path)
    for lane in sorted(lanes):
        probed = {f.split(lz.ARCHIVED_ONLY_IN_THE_WORKING_TREE)[0] for f in lz.frozen_by(lane)}
        here = {b.finding for b in lane_blockers(lane)}
        committed = {b.finding for b in lane_blockers(
            lane, staging_root=head, repo_root=lz.ROOT)}
        assert probed == here | committed, lane


def test_a_blocker_archived_only_in_the_WORKING_tree_still_FREEZES_the_row(tmp_path: Path):
    """THE POISON ROUND FOR THE TREE QUESTION, and it reproduces the live 2026-09-15 defect in
    miniature: a BLOCKING finding committed at `HEAD`, moved into `docs/staging/done/` in the
    working copy and NOT committed. That is the ordinary state of a shared worktree with a sibling
    lane archiving mid-turn, and the gate -- which runs on the tree the commit would create --
    still refuses the level raise on it.

    A probe reading only the working copy returns `[]` here and the scan prints MOVABLE NOW over a
    row the gate refuses, which is exactly the turn `frozen_by` exists to save. So this leg is red
    for any working-copy-only implementation, and the marker is asserted too: a reader who greps
    `docs/staging/` for the name finds nothing and would otherwise file it as a ghost.
    """
    import subprocess as sp

    def git(*args):
        sp.run(["git", *args], cwd=str(tmp_path), check=True, capture_output=True, text=True)

    staging = tmp_path / "docs" / "staging"
    staging.mkdir(parents=True)
    finding = "WORKER_FINDING_THE_INSTRUMENT_IS_WRONG_2026-09-15.md"
    (staging / finding).write_text(
        "# The instrument is wrong\n\n"
        "**Severity:** BLOCKING · **Lane:** T_test\n\nprose.\n")
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("add", "-A")
    git("commit", "-qm", "file the blocker")

    both_agree = lz._lane_blockers("T_test", root=tmp_path)
    assert both_agree == [finding], (
        "a blocker live in BOTH trees must be named plainly, with no tree marker: %r" % both_agree)

    (staging / "done").mkdir()
    (staging / finding).rename(staging / "done" / finding)  # archived, and NOT committed

    from background.gate_authorization import lane_blockers
    assert lane_blockers("T_test", staging_root=staging, repo_root=tmp_path) == [], (
        "the fixture does not reproduce the defect: the working copy must read CLEAR")

    held = lz._lane_blockers("T_test", root=tmp_path)
    assert held == [finding + lz.ARCHIVED_ONLY_IN_THE_WORKING_TREE], (
        "an uncommitted archival read as a discharge -- the scan would print MOVABLE over a row "
        "the commit gate refuses: %r" % held)
    assert lz.frozen_by("T_test", lambda lane: lz._lane_blockers(lane, root=tmp_path)), (
        "the row must be FROZEN while the trees disagree")


def test_a_tree_git_cannot_read_is_FROZEN_and_never_a_clear_lane(tmp_path: Path):
    """The HEAD half fails closed the same way the working half does. `_lane_blockers` raises
    where `git archive` cannot run, and `frozen_by` is what must turn that into a refusal rather
    than into an empty list that reads as 'this lane is clear'."""
    (tmp_path / "docs" / "staging").mkdir(parents=True)  # a directory, and not a repository
    assert lz.frozen_by("T_test", lambda lane: lz._lane_blockers(lane, root=tmp_path)) == [
        lz.BLOCKERS_UNREADABLE]


def test_a_lane_is_probed_ONCE_per_pass_however_many_rows_share_it(tmp_path: Path):
    """The probe reads the whole severity index. Two live contradictions share `H_harness`
    today; re-reading it per row is how a three-hourly orientation grows a cost nobody meant."""
    for name in ("test_a.py", "test_b.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    asked = []
    atoms = [{**_atom("ONE", scope=["test_a.py"]), "lane": "SAME_LANE"},
             {**_atom("TWO", scope=["test_b.py"]), "lane": "SAME_LANE"}]
    lz.assess(atoms, root=tmp_path, ages=_ages(), runner=lambda *a, **k: (True, "1 passed"),
              blockers_for=lambda lane: asked.append(lane) or [])
    assert asked == ["SAME_LANE"]


# --------------------------------------------------------------------------- #
# WHY a row cannot be graded, which is not the same question as the reason     #
# --------------------------------------------------------------------------- #
#
# THE DEFECT THESE EXIST TO CATCH, measured on the live map 2026-09-16: thirty-one ungradable
# rows under four reasons, and the count had not moved in twelve briefs. The reasons describe
# the SHAPE of `file_scope`; none of them says what to do, and rows sharing one reason had
# different causes and opposite repairs. Three rows read "names a control file that is not on
# disk": `A51` had a subject that MOVED, `PB5` had a control nobody wrote over a subject that is
# on disk, and `W1_28` was honestly unbuilt and correctly reading zero. Three repairs, one
# number, so the number could not go down -- and an instrument whose number cannot go down reads
# as a stuck problem rather than as a mixed class.
#
# WHAT THE SPLIT ACTUALLY MEASURED, kept here beside the prediction it corrects. The reading
# going in was that a large part of the census was never a defect. It is not. Of the 31 rows:
# 3 are honestly unbuilt and owe no repair, 14 have a subject on disk and no control anyone
# wrote, 4 have a rotted pointer (3 of those ALSO owe a control), 4 name only directories, and
# 6 are instrument states carrying no cause at all. The census was not mostly noise -- it was
# mostly a real backlog of unwritten controls wearing one undifferentiated label. The wrong
# prediction stays written down: it is the only evidence the split was designed before its
# answer was known.


def _known(answers: dict):
    """An injected `git log --all` oracle: `{path: True|False|None}`. Injected for the same
    reason `_runner` and `_ages` are -- a `tmp_path` is not a repository, so the real one answers
    None for every path and only the undecidable branch could ever be reached."""
    def known(rel, root=REPO):
        return answers.get(rel)
    return known


def test_all_seven_causes_are_reachable_in_one_pass(tmp_path: Path):
    """One control over the whole cause partition, and the reason it is one assertion and not
    seven is this file's own opening paragraph: every leg below is a POSITIVE claim about one
    cause, and a classifier that returned the same cause for everything would pass each of them
    read alone. This is the leg that goes red when a cause stops being reachable.

    It is keyed to REACHABILITY, not to today's live map: the fixture states eight worlds over
    seven causes, and the assertion is that the classifier distinguishes them. Repairing every
    live row leaves it green, which is what a control over a property rather than over an answer
    has to do.

    EIGHT WORLDS FOR SEVEN CAUSES, because `NAMES_ONLY_A_SCOPE` has two doors as of 2026-09-25
    and a single world would leave one of them unreachable while this stayed green -- which is
    precisely the shape the file's opening paragraph is about. `SCOPE_ONLY` is a row whose every
    entry is a directory; `SUBJECT_PLUS_TEST_DIR` is a row that names subject FILES and points
    its evidence at a directory that holds controls. The second used to come out
    `CONTROL_NEVER_WRITTEN`.

    AND THE `NO_CONTROL` / `UNNAMED_CONTROL` PAIR IS WHY THE ASSERTION IS ON THE WHOLE MAPPING.
    Those two worlds differ by one thing -- whether the row NAMES the control it lacks -- and
    they carried one cause until 2026-09-25. Two shapes collapsing into one state is invisible to
    a control that only asks "is each cause reachable"; comparing the whole dict is what sees it.
    """
    (tmp_path / "subject.py").write_text("x = 1\n")
    (tmp_path / "test_here.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "tests").mkdir()
    # A directory that HOLDS a control, which is what `_is_a_control_scope` measures. Deliberately
    # NOT under `tests/`: the live map's `W2_18` and `W2_19` point at `site/knowledge/`, which
    # holds seven controls, so a predicate keyed to a `tests/` prefix would have missed them.
    (tmp_path / "suite").mkdir()
    (tmp_path / "suite" / "test_inside.py").write_text("def test_y():\n    assert True\n")

    worlds = {
        "ROTTED": (_atom("ROTTED", scope=["gone/moved.py", "subject.py", "test_here.py"]),
                   {"gone/moved.py": True}),
        "UNDECIDABLE": (_atom("UNDECIDABLE", scope=["gone/unknown.py", "subject.py",
                                                    "test_here.py"]),
                        {"gone/unknown.py": None}),
        "SCOPE_ONLY": (_atom("SCOPE_ONLY", scope=["tests/"]), {}),
        "SUBJECT_PLUS_TEST_DIR": (_atom("SUBJECT_PLUS_TEST_DIR",
                                        scope=["subject.py", "suite"]), {}),
        "UNBUILT": (_atom("UNBUILT", scope=["never/made.py", "tests/test_planned.py"]),
                    {"never/made.py": False, "tests/test_planned.py": False}),
        # NAMES a control, and git has never heard of it: the only shape that earns the claim
        # "never written", because it is the only one where a control was asked for by name.
        "NO_CONTROL": (_atom("NO_CONTROL", scope=["subject.py", "tests/test_nobody.py"]),
                       {"tests/test_nobody.py": False}),
        # Names NO control. Nothing is absent, nothing was measured, and saying "never written"
        # here is the PB4/PB6 shape: a build that wrote a control under a name the row never
        # cited. `suite/` is absent from this row on purpose.
        "UNNAMED_CONTROL": (_atom("UNNAMED_CONTROL", scope=["subject.py"]), {}),
        # The row that is not the problem: subject and control both on disk, nothing absent.
        # This world used to return `[]` and was the hole in the partition.
        "NOTHING_WRONG": (_atom("NOTHING_WRONG", scope=["subject.py", "test_here.py"]), {}),
    }
    got = {name: [c["cause"] for c in lz.ungradable_causes(atom, root=tmp_path,
                                                           known=_known(answers))]
           for name, (atom, answers) in worlds.items()}

    assert got == {
        "ROTTED": [lz.POINTER_ROT],
        "UNDECIDABLE": [lz.CAUSE_UNDECIDABLE],
        "SCOPE_ONLY": [lz.NAMES_ONLY_A_SCOPE],
        "SUBJECT_PLUS_TEST_DIR": [lz.NAMES_ONLY_A_SCOPE],
        "UNBUILT": [lz.HONESTLY_UNBUILT],
        "NO_CONTROL": [lz.CONTROL_NEVER_WRITTEN],
        "UNNAMED_CONTROL": [lz.CONTROL_UNNAMED],
        "NOTHING_WRONG": [lz.NOTHING_IN_THE_ROW],
    }, "the cause partition is not fully reachable: {!r}".format(got)


def test_a_row_that_names_NO_control_is_not_told_the_control_was_NEVER_WRITTEN(tmp_path: Path):
    """THE DEFECT: `CONTROL_NEVER_WRITTEN` claims the control "was never written", and until
    2026-09-25 it was also returned for rows that name no control at all -- where nothing was
    measured. Fourteen of its sixteen live members were that shape. The printed repair told the
    reader to write "the named control", and there was none to write.

    WHY THE TWO MUST NOT SHARE A CAUSE, in one sentence: this module's own docstring records
    `PB4` and `PB6` as rows whose build DID write a control under a name the row does not cite,
    so "never written" over a row that names nothing is a coin-flip published as a finding.

    MUTATION (must fire): make the `elif not controls` branch append `CONTROL_NEVER_WRITTEN`
    again. Note what does NOT fire: the reachability test above stays green under that mutation
    unless its `UNNAMED_CONTROL` world is also present, which is why both exist."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    causes = lz.ungradable_causes(_atom("NAMES_NOTHING", scope=["subject.py"]),
                                  root=tmp_path, known=_known({}))
    assert [c["cause"] for c in causes] == [lz.CONTROL_UNNAMED], causes
    assert lz.CONTROL_NEVER_WRITTEN not in {c["cause"] for c in causes}, (
        "a row that names no control was told its control was never written: %r" % causes)
    # The paths must be openable. The placeholder this used to carry --
    # "(file_scope names no test_*.py)" -- is a path-shaped token in a `paths` field, and the
    # repair sends the reader to `git log -- <path>` with it.
    assert causes[0]["paths"] == ["subject.py"], causes
    assert all((tmp_path / p).exists() for p in causes[0]["paths"]), causes


def test_a_control_scope_is_measured_and_not_matched_on_a_tests_prefix(tmp_path: Path):
    """`_is_a_control_scope` asks the TREE whether controls live in a directory, and the live map
    is why: `W2_18` and `W2_19` point their evidence at `site/knowledge/`, which holds seven
    `test_*.py` files and no `tests/` in its path. A prefix literal would have classed both as
    rows with no control at all and sent them to write one.

    THE OTHER HALF IS THE NEGATIVE, and it is the leg that stops the predicate from returning
    True for every directory: the subject directories these rows also name -- on the live map
    `docs/market_research/`, `company/billing/`, `site/data/` -- hold no control and must not be
    read as evidence of one.

    MUTATION (must fire): `return here.is_dir()`. Or make the positive leg
    `rel.startswith("tests")`."""
    (tmp_path / "site" / "knowledge").mkdir(parents=True)
    (tmp_path / "site" / "knowledge" / "test_door.py").write_text("def test_z():\n    pass\n")
    (tmp_path / "docs" / "market_research").mkdir(parents=True)
    (tmp_path / "docs" / "market_research" / "note.md").write_text("# a source\n")
    (tmp_path / "tests").mkdir()

    assert lz._is_a_control_scope("site/knowledge", tmp_path) is True
    assert lz._is_a_control_scope("docs/market_research/", tmp_path) is False
    # Present, named like the suite root, and holding nothing: FALSE, so the row falls to
    # `CONTROL_UNNAMED`, whose repair says go and look -- rather than being told to name a file
    # in a directory that has none.
    assert lz._is_a_control_scope("tests/", tmp_path) is False
    assert lz._is_a_control_scope("nowhere/at/all", tmp_path) is False


def test_a_row_with_a_rotted_pointer_AND_an_unwritten_control_names_BOTH(tmp_path: Path):
    """`A51`'s live shape, and the leg that stops the split being re-merged one level up.

    Its ruling moved into `docs/staging/done/` and it names a test nobody has written. A
    classifier returning one primary cause sends the reader to repoint the pointer and call the
    row repaired -- and the row stays ungradable, which is how a census reports work it has
    already been given. A mixed class is resolved by its sub-breakdown or refused, never whole."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    atom = _atom("A51_shape", scope=["moved/ruling.md", "subject.py", "tests/test_nobody.py"])
    causes = lz.ungradable_causes(
        atom, root=tmp_path,
        known=_known({"moved/ruling.md": True, "tests/test_nobody.py": False}))
    assert [c["cause"] for c in causes] == [lz.POINTER_ROT, lz.CONTROL_NEVER_WRITTEN], (
        "both repairs must be printed on the first pass, not one per re-run: %r" % causes)


def test_a_mislaid_subject_is_never_read_as_HONESTLY_UNBUILT(tmp_path: Path):
    """The rot gate, stated as its own leg because removing it is a one-word change that leaves
    every other test here green.

    `honestly unbuilt` is the only cause that says "this row owes NO repair". Reached over a path
    the row names wrongly it is exactly backwards -- the subject can be on disk under the name
    the row stopped using -- and it would close an atom that is built. The undecidable answer is
    held to the same bar: "git could not be asked" is not "the file was never written"."""
    atom = _atom("MISLAID", scope=["gone/moved.py", "tests/test_planned.py"])
    for answer in (True, None):
        causes = [c["cause"] for c in lz.ungradable_causes(
            atom, root=tmp_path,
            known=_known({"gone/moved.py": answer, "tests/test_planned.py": False}))]
        assert lz.HONESTLY_UNBUILT not in causes, (
            "a row whose subject pointer is {} was declared right to read zero: {!r}".format(
                "rotted" if answer else "unreadable", causes))


def test_every_cause_carries_the_repair_it_instructs(tmp_path: Path):
    """A cause without its repair is the undifferentiated count again, one level down. The
    twelve-brief failure was not that the census said too little -- it said thirty-one, loudly,
    every time -- it was that nothing it said could be acted on."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    causes = lz.ungradable_causes(_atom("NEEDS_A_CONTROL", scope=["subject.py"]),
                                  root=tmp_path, known=_known({}))
    assert causes and all(c["repair"] == lz.CAUSE_REPAIR[c["cause"]] and c["repair"].strip()
                          for c in causes), causes


def test_assess_attaches_causes_to_every_ungradable_row(tmp_path: Path):
    """The classifier has to reach the census's own output, not merely exist beside it. A
    refusal landed in the producer while the published surface goes on printing the old answer
    is this repository's most-repeated shape."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    atoms = [_atom("NEEDS_A_CONTROL", scope=["subject.py"])]
    _, ungradable = lz.assess(atoms, root=tmp_path, ages=_ages(),
                              runner=lambda *a, **k: (True, "1 passed"),
                              causes=lambda atom, root: lz.ungradable_causes(
                                  atom, root=root, known=_known({})))
    assert [c["cause"] for c in ungradable[0]["causes"]] == [lz.CONTROL_UNNAMED], (
        "the cause did not reach the record the brief and the CLI both read: %r" % ungradable)


def test_an_instrument_state_says_the_refusal_is_IN_THE_PASS_and_not_in_the_row(
        tmp_path: Path):
    """A row the budget never reached, or one whose control predates it, is a fact about the
    PASS or about the dating -- not about whether the atom is built. The instruction it owes the
    reader is therefore "do not edit `file_scope`, re-run it", and NOTHING_IN_THE_ROW says
    exactly that.

    CORRECTION, 2026-09-16, replacing the assertion that stood here. This test used to demand
    `causes == []` and argued the emptiness was the honest answer. It was not. "The refusal is in
    the pass" is a reading, and returning nothing left five of the thirty live ungradable rows
    with no cause at all -- invisible to `delivery_seat._by_cause`, which groups by exactly that
    field. A fail-silent in the control built to end an undifferentiated count, defended by its
    own test. The honest empty list was the flattering half of "a mutation that does not fire is
    either a missing test or an equivalence".

    The leg it keeps: no cause here may instruct a REPAIR TO THE ROW, because nothing in the row
    is wrong. That is asserted directly rather than by the absence of a cause."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    (tmp_path / "test_old.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("OLDER", scope=["subject.py", "test_old.py"])]
    _, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(predating={"OLDER": ["test_old.py"]}),
        runner=lambda *a, **k: (True, "1 passed"),
        causes=lambda atom, root: lz.ungradable_causes(atom, root=root, known=_known({})))
    assert ungradable[0]["reason"] == lz.CONTROL_PREDATES_ROW
    assert [c["cause"] for c in ungradable[0]["causes"]] == [lz.NOTHING_IN_THE_ROW]
    assert "do not edit" in ungradable[0]["causes"][0]["repair"], (
        "the row's scope is correct, so a repair pointing at `file_scope` would send the reader "
        "to edit a row that is right: %r" % ungradable[0]["causes"])


def test_EVERY_ungradable_row_carries_at_least_one_cause(tmp_path: Path):
    """Totality, over the partition rather than over an example. The hole this closes was not a
    wrong cause -- it was five rows with no cause at all, which every consumer that groups by
    cause silently drops.

    THE FIXTURE SPANS ALL FOUR REFUSAL SHAPES `assess` can emit, because the hole was in the one
    nobody thought to check: the row whose scope is entirely correct. A per-shape leg would have
    been written for the three that obviously need a cause and would have missed it again.

    MUTATION (must fire): delete the `if not out` tail in `ungradable_causes` and OLDER,
    NO_VERDICT and NEVER_REACHED all come back empty."""
    (tmp_path / "subject.py").write_text("x = 1\n")
    (tmp_path / "test_old.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_slow.py").write_text("def test_x():\n    assert True\n")
    atoms = [
        _atom("NAMES_NOTHING", scope=["subject.py"]),
        _atom("ABSENT_CONTROL", scope=["subject.py", "tests/test_gone.py"]),
        _atom("OLDER", scope=["subject.py", "test_old.py"]),
        _atom("NO_VERDICT", scope=["subject.py", "test_slow.py"]),
    ]
    _, ungradable = lz.assess(
        atoms, root=tmp_path, ages=_ages(predating={"OLDER": ["test_old.py"]}),
        runner=lambda *a, **k: (None, "timed out"),
        causes=lambda atom, root: lz.ungradable_causes(
            atom, root=root, known=_known({"tests/test_gone.py": False})))

    assert {u["id"] for u in ungradable} == {a["id"] for a in atoms}
    uncaused = sorted(u["id"] for u in ungradable if not u.get("causes"))
    assert not uncaused, (
        "row(s) reached the brief with no cause at all: {}. A consumer grouping by cause drops "
        "them entirely, which is the undifferentiated count with a hole in it".format(uncaused))


# --------------------------------------------------------------------------- #
# The count carries its DENOMINATOR                                            #
#                                                                              #
# THE DEFECT THESE NAME. On 2026-09-25 the live pass returned                   #
# `{"contradicted": 0, "ungradable": 28}` with a partition of exactly 28 rows:  #
# nothing was weighed, and the delivery seat twice read the 0 as evidence that  #
# the map was an honest record. A count published without the denominator its   #
# sample size earns cannot be distinguished from a clean bill of health.        #
# --------------------------------------------------------------------------- #

def test_a_pass_that_GRADED_NOTHING_says_so_and_never_lets_zero_read_as_clean(
        monkeypatch, capsys):
    """The live 2026-09-25 shape: every row in the partition ungradable, nothing weighed."""
    rows = [_atom("UNGRADABLE_A"), _atom("UNGRADABLE_B")]
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: rows)
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [], [{"id": r["id"], "reason": lz.NO_CONTROL_NAMED, "paths": [], "detail": "",
              "causes": []} for r in rows]))

    assert lz.main([]) == 0, "a row that cannot be graded still does not refuse"
    err = capsys.readouterr().err
    assert "NOTHING WAS GRADED" in err
    assert "2 row(s) in the partition" in err
    assert "cannot tell" in err


def test_BOTH_denominator_states_are_reachable_in_one_pass(monkeypatch, capsys):
    """The partition control. A denominator line printed unconditionally would pass the vacuous
    arm on its own, so the graded arm asserts the vacuous sentence is ABSENT -- not merely that
    some other word is present, which is the shape that passes the unconditional mutation."""
    rows = [_atom("GRADED_SILENT"), _atom("CANNOT_GRADE")]
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: rows)

    # ARM 1 -- one row weighed and silent (its controls do not all pass), one ungradable.
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [], [{"id": "CANNOT_GRADE", "reason": lz.NO_CONTROL_NAMED, "paths": [], "detail": "",
              "causes": []}]))
    assert lz.main([]) == 0
    graded_err = capsys.readouterr().err
    assert "1 of 2 row(s) in the partition were GRADED" in graded_err
    assert "NOTHING WAS GRADED" not in graded_err, (
        "the vacuous sentence fired on a pass that DID weigh a row -- the denominator line is "
        "unconditional, which is the whole defect with the sign flipped")

    # ARM 2 -- the same two rows, neither weighed.
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [], [{"id": r["id"], "reason": lz.NO_CONTROL_NAMED, "paths": [], "detail": "",
              "causes": []} for r in rows]))
    assert lz.main([]) == 0
    vacuous_err = capsys.readouterr().err
    assert "NOTHING WAS GRADED" in vacuous_err
    assert "were GRADED" not in vacuous_err


def test_the_JSON_surface_carries_the_denominator_and_not_only_the_two_lists(
        monkeypatch, capsys):
    """A machine consumer reads `contradicted` and has to be able to ask what it was out of."""
    rows = [_atom("UNGRADABLE_A"), _atom("UNGRADABLE_B")]
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: rows)
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [], [{"id": "UNGRADABLE_A", "reason": lz.NO_CONTROL_NAMED, "paths": [], "detail": "",
              "causes": []}]))

    assert lz.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["population"] == 2
    assert payload["graded"] == 1
    assert payload["contradicted"] == []


def test_the_denominator_counts_THE_PARTITION_and_not_the_whole_live_map(monkeypatch, capsys):
    """Keyed to `is_candidate`, the predicate `assess` itself filters on. A live map of 110 atoms
    with 28 in the partition must report 28: a denominator counting every live row would make the
    graded share look tiny for a reason that has nothing to do with grading."""
    rows = [_atom("IN_PARTITION"),
            _atom("ABOVE_ZERO", level=2),
            _atom("NOT_BUILDING", stage="idle")]
    monkeypatch.setattr(lz.map_store, "load_live_atoms", lambda: rows)
    monkeypatch.setattr(lz, "assess", lambda *a, **k: (
        [], [{"id": "IN_PARTITION", "reason": lz.NO_CONTROL_NAMED, "paths": [], "detail": "",
              "causes": []}]))

    assert lz.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["population"] == 1, (
        "the denominator counted rows `assess` never grades -- level>0 and loop_stage!=build are "
        "outside the partition by the same predicate")
    assert payload["graded"] == 0


# --------------------------------------------------------------------------- #
# A MIXED set is graded on the atom's own half                                 #
# --------------------------------------------------------------------------- #

def test_a_row_naming_ONE_control_its_own_build_wrote_is_GRADED_though_another_predates_it(
        tmp_path: Path):
    """KNIFE3's live shape, and the defect that made the whole pass return zero graded rows.

    THE DEFECT. Until 2026-09-25 a single predating entry refused the row entire. An atom that
    EXTENDS an existing suite always names one: KNIFE3 names twelve controls, nine written after
    the row by its own build and three older because they already existed and it cut into them.
    Nine pieces of the atom's own evidence were discarded for three that carry none, and on the
    live map every one of the 28 rows in the partition came back ungradable.

    THE MUTATION THIS FIRES ON. Restore `if predating:` in place of `if predating and not
    atom_own:` and this row lands in `ungradable` under CONTROL_PREDATES_ROW, which is what the
    assertion below names. The runner is rigged to pass so that the age branch is the only thing
    that can decide the verdict -- if the branch is deleted outright the row is contradicted and
    this test stays green, which is why it is written alongside the two below and not alone.
    """
    (tmp_path / "test_older.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_mine.py").write_text("def test_y():\n    assert True\n")
    atoms = [_atom("KNIFE3_shape", scope=["test_older.py", "test_mine.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=_runner({("test_older.py", "test_mine.py"): (True, "2 passed")}),
        ages=_ages(predating={"KNIFE3_shape": ["test_older.py"]}))
    assert [u["reason"] for u in ungradable] == [], (
        "a row with one control its own build wrote was thrown away for naming an older one too")
    assert [c["id"] for c in contradicted] == ["KNIFE3_shape"]


def test_a_row_whose_controls_ALL_predate_it_is_still_ungradable_ENTIRE(tmp_path: Path):
    """The other side of the same partition, and the leg that keeps the relaxation honest.

    H41's shape: BOTH named suites were on disk before the row was minted, so nothing in the set
    is this atom's own evidence and there is nothing to grade it on. The mutation this fires on is
    dropping `predating and` from the condition, or widening `atom_own` to include the predating
    entries -- either makes this row CONTRADICTED on the strength of suites that were passing
    before the atom existed, which is the 2026-09-06 defect the age branch was written for.
    """
    (tmp_path / "test_old_a.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "test_old_b.py").write_text("def test_y():\n    assert True\n")
    atoms = [_atom("H41_shape", scope=["test_old_a.py", "test_old_b.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=lambda *a, **k: (True, "41 passed"),
        ages=_ages(predating={"H41_shape": ["test_old_a.py", "test_old_b.py"]}))
    assert contradicted == []
    assert [(u["reason"], u["paths"]) for u in ungradable] == [
        (lz.CONTROL_PREDATES_ROW, ["test_old_a.py", "test_old_b.py"])]


def test_a_PREDATING_control_that_FAILS_still_silences_a_mixed_row(tmp_path: Path):
    """The anti-loosening leg, and the one the relaxation above is only safe because of.

    A predating control may silence a row; it may never refuse one. So the whole named set is
    still run and still has to pass -- the mixed row is graded, and its verdict here is SILENCE
    because the older suite is red. The mutation this fires on is `runner(atom_own or controls,
    ...)` (the obvious way to write the relaxation): that runs the one atom-own control, sees it
    pass, and refuses a level move for an atom whose own scope is red -- a refusal earned by
    dropping the evidence against it, which is the failure this whole module exists to name.

    THE RUNNER ANSWERS ANY SUBSET, deliberately. Keyed on the exact tuple it would raise KeyError
    under that mutation, and the test would go red on the lookup rather than on the assertion --
    green-adjacent, and indistinguishable in the log from the leg actually holding. Measured
    2026-09-25: the first draft did exactly that.
    """
    for name in ("test_older.py", "test_mine.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    atoms = [_atom("MIXED_RED", scope=["test_older.py", "test_mine.py"])]

    def run_any_subset(paths, root=None, timeout_s=0):
        return (("test_older.py" not in tuple(paths)), "{} run".format(len(tuple(paths))))

    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=run_any_subset,
        ages=_ages(predating={"MIXED_RED": ["test_older.py"]}))
    assert contradicted == [], "a mixed row was refused while a control in its own scope was red"
    assert ungradable == [], "silence is the verdict here, not an ungradable row"


def test_an_UNDATABLE_control_beside_an_atom_own_one_is_still_PROVENANCE_UNKNOWN(tmp_path: Path):
    """The relaxation is scoped to AGE, and this is what stops it leaking into provenance.

    The age relaxation above opens a mixed set to grading. Provenance must NOT get the parallel
    relaxation, and nothing in the age branch gives it one: the `if undatable:` leg fires on ANY
    undatable entry, whatever else the row names.

    THE MUTATION THIS FIRES ON, and it is not the one the first draft named. That draft claimed
    the leg was carried by subtracting `undatable` from `atom_own`, and mutating that subtraction
    away was GREEN -- an equivalence, because the provenance leg had already fired by then. The
    dead term is gone and the real mutation is relaxing the provenance leg the same way the age
    leg was relaxed: `if undatable and not atom_own:`. That is the edit a reader who had just
    written the age relaxation would reach for, and this row is then graded on a set holding a
    control the tree could not date -- the fail-open reading `PROVENANCE_UNKNOWN` exists to forbid.
    """
    for name in ("test_undated.py", "test_mine.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    atoms = [_atom("MIXED_UNDATED", scope=["test_undated.py", "test_mine.py"])]
    contradicted, ungradable = lz.assess(
        atoms, root=tmp_path, runner=lambda *a, **k: (True, "2 passed"),
        ages=_ages(undatable={"MIXED_UNDATED": ["test_undated.py"]}))
    assert contradicted == []
    assert [u["reason"] for u in ungradable] == [lz.PROVENANCE_UNKNOWN]


# --------------------------------------------------------------------------- #
# The red-at-HEAD short circuit, and the stale arm that must stay reachable    #
# --------------------------------------------------------------------------- #

def _observed(tmp_path: Path, *, runs, tests) -> Path:
    """Write a HEAD-red observation store under `tmp_path` at the path the real one lives at,
    derived from the store module's own declaration so a moved store moves this too."""
    from background import head_red_register as hrr
    p = tmp_path / hrr.OBSERVED_PATH.relative_to(hrr.PROJECT_DIR)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"runs": runs, "tests": tests}))
    return p


def _run(at, *, head="abc123", passed=100, red=1):
    return {"at": at, "head": head, "passed": passed, "red": red}


def test_all_four_states_of_the_red_at_head_probe_are_reachable(tmp_path: Path):
    """One control over the whole partition of `reds_at_head`, written this way deliberately.

    THE DEFECT THIS CATCHES is the one CLAUDE.md names: a screen written to fire rarely, whose
    every test asks "does it decline correctly", and which therefore passes every leg while
    declining EVERYTHING. A probe that returned `([], REGISTER_UNOBSERVED)` unconditionally would
    satisfy three of the four assertions below and this one assertion would still go red.

    The fourth state -- SILENCE -- is the only one that changes a verdict, and the three unusable
    states are not decoration: each of them must fall through to the run, so each of them being
    reachable is what proves the fail-closed half is not dead code.
    """
    fresh = datetime.now(timezone.utc).isoformat()
    ancient = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    tests = {"tests/x/test_a.py::test_one": {"currently_red": True},
             "tests/x/test_b.py::test_two": {"currently_red": False},
             # A DIFFERENT FILE whose path merely ENDS WITH the named one. Added 2026-09-25
             # after mutating `str(node).split("::", 1)[0] in wanted` to a substring match and
             # watching all 45 tests stay green: that mutation is not an equivalence, it silences
             # a row on a red in a file the row does not name, so the gap was a missing leg and
             # not a harmless one. Establishing which of the two it was is the rule.
             "vendor/tests/x/test_a.py::test_one": {"currently_red": True}}

    silenced = tmp_path / "silenced"
    _observed(silenced, runs=[_run(fresh)], tests=tests)
    stale = tmp_path / "stale"
    _observed(stale, runs=[_run(ancient)], tests=tests)
    undated = tmp_path / "undated"
    _observed(undated, runs=[_run(None)], tests=tests)
    unobserved = tmp_path / "unobserved"
    _observed(unobserved, runs=[], tests=tests)
    # A store whose rows are not mappings at all. This probe runs inside the delivery seat's
    # orientation, so a row that raises does not fail closed -- it takes the whole pass and the
    # brief with it. Corrupt must land in the SAME place as every other unusable state.
    corrupt = tmp_path / "corrupt"
    _observed(corrupt, runs=["not a mapping"], tests={"tests/x/test_a.py::test_one": "nor this"})
    # ...and the SAME corruption one level down, behind a run row that IS well formed. Added
    # 2026-09-25 because the fixture above never reaches the tests loop -- it returns UNDATED on
    # the run row first -- so mutating away the per-test guard left all 45 green. A missing leg,
    # not an equivalence: without the guard this raises AttributeError out of the seat's
    # orientation instead of falling through to the run.
    corrupt_rows = tmp_path / "corrupt_rows"
    _observed(corrupt_rows, runs=[_run(fresh)],
              tests={"tests/x/test_a.py::test_one": "not a mapping"})

    named = ["tests/x/test_a.py"]
    states = {
        "SILENCED": lz.reds_at_head(named, root=silenced),
        "STALE": lz.reds_at_head(named, root=stale),
        "UNDATED": lz.reds_at_head(named, root=undated),
        "UNOBSERVED": lz.reds_at_head(named, root=unobserved),
        "CORRUPT": lz.reds_at_head(named, root=corrupt),
        "CORRUPT_ROWS": lz.reds_at_head(named, root=corrupt_rows),
        # A red that is NOT in the named set says nothing about this row.
        "RED_ELSEWHERE": lz.reds_at_head(["tests/x/test_b.py"], root=silenced),
    }

    assert states["SILENCED"] == (["tests/x/test_a.py::test_one"], None), (
        "the named control is matched on its WHOLE path or not at all -- a red in "
        "`vendor/tests/x/test_a.py` is a red in a file this row does not name: {}".format(
            states["SILENCED"]))
    assert states["RED_ELSEWHERE"] == ([], None), states["RED_ELSEWHERE"]
    for label in ("STALE", "UNDATED", "UNOBSERVED", "CORRUPT"):
        reds, why = states[label]
        assert reds == [] and why, "{} is not reachable: {}".format(label, states[label])
    # A well-formed run over malformed test rows is a USABLE register holding no readable red:
    # empty list, no reason, and the row falls through to its run. It must not raise, and it must
    # not be mistaken for one of the unusable states -- those three send a reader to a daemon.
    assert states["CORRUPT_ROWS"] == ([], None), states["CORRUPT_ROWS"]
    # And the three unusable reasons are DISTINCT, because they send a reader to three different
    # places. Collapsing them would pass every assertion above.
    assert len({states[k][1] for k in ("STALE", "UNDATED", "UNOBSERVED")}) == 3, states


def test_a_row_naming_a_control_red_at_HEAD_is_SILENT_and_its_suites_are_NEVER_RUN(tmp_path: Path):
    """The economy itself. `KNIFE3_wall_crossing_paydown` names twelve suites costing 1078s
    against a production cap of 60s, so the rows naming the most controls could never be weighed:
    the live pass returned population 28, graded 0. Two of KNIFE3's 224 tests have been red at
    HEAD for 19 consecutive census runs, and CONTRADICTED needs the WHOLE set to pass -- so the
    run was buying a verdict already known.

    THE `ran` LIST IS THE ASSERTION, not the verdict. A leg that reached the same silence BY
    RUNNING the suites would satisfy a verdict-only test and buy nothing at all."""
    for name in ("test_red_at_head.py", "test_fine.py"):
        (tmp_path / name).write_text("def test_x():\n    assert True\n")
    _observed(tmp_path, runs=[_run(datetime.now(timezone.utc).isoformat())],
              tests={"test_red_at_head.py::test_x": {"currently_red": True}})

    ran: list = []

    def runner(paths, root=REPO, timeout_s=0):
        ran.append(tuple(paths))
        return (True, "1 passed")

    contradicted, ungradable = lz.assess(
        [_atom("SILENCED_BY_A_RED", scope=["test_red_at_head.py"]),
         _atom("GRADED_BY_A_RUN", scope=["test_fine.py"])],
        root=tmp_path, ages=_ages(), runner=runner, blockers_for=lambda lane: [])

    assert ran == [("test_fine.py",)], (
        "the short circuit did not save the run, or it swallowed the row that needed one: {}"
        .format(ran))
    assert [c["id"] for c in contradicted] == ["GRADED_BY_A_RUN"], contradicted
    assert ungradable == [], (
        "a row silenced by a red at HEAD is GRADED -- we have evidence its named set does not "
        "all pass -- and must not be reported as a row nobody could weigh: {}".format(ungradable))


def test_a_stale_or_unreadable_register_FAILS_CLOSED_and_the_suites_still_run(tmp_path: Path):
    """The half that is not free, and the arm the work item asked be PROVEN REACHABLE.

    If an unusable register silenced rows, one missing untracked file would retire the whole
    partition at a stroke -- the blanket disposition `background/head_red_register` refuses by
    design ("one paragraph must not be able to retire 830 subjects"). So an unusable register
    must leave the verdict exactly as it was before this leg existed, and the proof of that is
    that the SAME world which silences on a fresh store REFUSES on a stale one.

    Both arms are asserted against one fixture on purpose: a test that only pinned the stale arm
    would pass against a leg that had been disabled altogether."""
    (tmp_path / "test_red_at_head.py").write_text("def test_x():\n    assert True\n")
    atoms = [_atom("A_ROW", scope=["test_red_at_head.py"])]
    reds = {"test_red_at_head.py::test_x": {"currently_red": True}}

    def graded_with(runs):
        _observed(tmp_path, runs=runs, tests=reds)
        ran: list = []

        def runner(paths, root=REPO, timeout_s=0):
            ran.append(tuple(paths))
            return (True, "1 passed")

        contradicted, _ = lz.assess(atoms, root=tmp_path, ages=_ages(), runner=runner,
                                    blockers_for=lambda lane: [])
        return ran, [c["id"] for c in contradicted]

    fresh_ran, fresh_verdict = graded_with([_run(datetime.now(timezone.utc).isoformat())])
    stale_ran, stale_verdict = graded_with(
        [_run((datetime.now(timezone.utc) - timedelta(days=30)).isoformat())])
    gone_ran, gone_verdict = graded_with([])

    assert fresh_ran == [] and fresh_verdict == [], (
        "the silence arm is unreachable, so the stale arm below proves nothing: {} {}"
        .format(fresh_ran, fresh_verdict))
    assert stale_ran == [("test_red_at_head.py",)] and stale_verdict == ["A_ROW"], (
        "a STALE register did not fail closed -- it silenced the row instead of running it: "
        "{} {}".format(stale_ran, stale_verdict))
    assert gone_ran == [("test_red_at_head.py",)] and gone_verdict == ["A_ROW"], (
        "an UNOBSERVED register did not fail closed: {} {}".format(gone_ran, gone_verdict))


def test_a_red_a_person_has_ACCEPTED_still_silences_the_row(tmp_path: Path):
    """Acceptance is a DECISION about whether we owe work; redness is an OBSERVATION about
    whether the test passes. This leg asks only the second, so it must not read through
    `head_red_register.owed` or `head_red_baseline.load_baseline`, both of which subtract the
    first.

    The defect if it did: a red accepted in `head_red_baseline.json` would drop out of the probe,
    the row's expensive suites would be run to discover the set does not pass, and the verdict
    would be the same silence at full price -- the exact cost this leg exists to avoid.

    THE ACCEPTANCE FILE IS REALLY WRITTEN, into the fixture tree at the path the loader resolves,
    and that is the whole reason this test can fail. Without it the mutation "subtract the
    accepted set" is a NO-OP in a tmp_path -- there is no baseline to subtract -- and this
    control would go green against the very defect it names. (Caught 2026-09-25 by mutating it:
    the first draft asserted `owed()` behaviour with the list passed in BY HAND, which proves
    something about `owed` and nothing about this probe.)"""
    from background import head_red_baseline as hrb
    from background import head_red_register as hrr

    node = "test_accepted_red.py::test_x"
    (tmp_path / "test_accepted_red.py").write_text("def test_x():\n    assert True\n")
    store = {"runs": [_run(datetime.now(timezone.utc).isoformat())],
             "tests": {node: {"currently_red": True}}}
    _observed(tmp_path, runs=store["runs"], tests=store["tests"])

    baseline = tmp_path / hrb.BASELINE_PATH.relative_to(hrb.PROJECT_DIR)
    baseline.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_text(json.dumps({"known_red": [node]}))

    # The premise, asserted rather than assumed: this node really IS accepted by both of the
    # mechanisms the probe must not route through. A rotted premise here would make the
    # assertion below pass for the wrong reason.
    assert hrb.load_baseline(baseline) == {node}, baseline.read_text()
    assert hrr.owed(store, hrb.load_baseline(baseline)) == [], (
        "this test's premise is gone: the node it calls accepted is not being subtracted by "
        "`owed`, so it cannot show that this leg ignores acceptance")

    reds, why = lz.reds_at_head(["test_accepted_red.py"], root=tmp_path)
    assert why is None and reds == [node], (
        "an accepted red stopped silencing the row, so the leg is reading the DECISION store "
        "and not the OBSERVATION: {} {}".format(reds, why))
