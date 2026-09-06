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

import os
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
