"""The publish gate's SUBJECT is committed truth, in a checkout no other cycle can touch.

WHY THIS MODULE EXISTS. `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` moved the gate's
subject from the shared working tree to a clean checkout of HEAD: *"publishing tests committed
truth only; the working tree belongs to the lanes."* The minimal implementation landed that
night; what it bought -- **a lane's uncommitted work can no longer change the publish verdict**
-- was asserted nowhere. That is the property this module pins, and it pins it by MUTATION: the
same broken-working-tree scenario is run with the gate pointed at the checkout (green) and
pointed back at the tree (red), so the green is demonstrably produced by the checkout.

`OPS2_publish_gate_head_worktree` then made the checkout REUSED between cycles (bytecode is the
whole cost of a clean subject) and that introduced three lifecycle hazards -- two publishers,
test debris, and crash leakage -- each of which is a control here rather than a comment.

REUSE WAS THEN ELIMINATED (2026-08-11, R3, 444402ee0): the shared directory was reset under a
live suite four separate times, each time producing a red that said nothing about any test, and
the last of them left publishing down 41 hours. `REUSE_HEAD_CHECKOUT` ships `False`; every cycle
gets its own throwaway checkout and deletes it. The reuse code was kept behind that one-line
switch, so this module is in two halves: the SHIPPED lifecycle, asserted as it runs, and the
DORMANT one, exercised through the `reuse_enabled` fixture so that flipping the switch back
cannot quietly reintroduce hazards nobody is watching for. The two halves' first tests are each
other's mutation on that one line.

HOW IT AVOIDS TESTING ITSELF INTO A CORNER. Every behavioural test runs against a REAL git repo
built in `tmp_path` with `prc.PROJECT_DIR` pointed at it, never against this repository: writing
a syntax error into a tracked file of the live shared tree -- the honest way to produce a dirty
tree -- would break every daemon that imports it for as long as the test ran. The mechanism under
test (`git archive` -> standalone repo -> `read-tree --reset` refresh) is exercised for real; only
the tree it operates on is a stand-in.
"""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from background import process_run_complete as prc  # noqa: E402
from tests.background.publish_gate_root_shape import (  # noqa: E402
    materialise_repo_shaped_root,
)

# `shutil.disk_usage`'s own return shape, so a stand-in cannot pass by being a different thing
# from what the code under test unpacks.
_DiskUsage = type(shutil.disk_usage("/"))


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=120, check=False)


@pytest.fixture
def logged(monkeypatch):
    lines = []
    monkeypatch.setattr(prc, "log", lines.append)
    return lines


@pytest.fixture
def reuse_enabled(monkeypatch):
    """Turn the DORMANT reused-checkout path back on for one test.

    `REUSE_HEAD_CHECKOUT` shipped `False` on 2026-08-11 (R3 elimination, 444402ee0): the shared
    directory was reset under a live suite four times and produced four reds that said nothing
    about any test. The path behind the switch was NOT deleted -- the commit's own record says it
    is reversible in one line, once the grandchild-outlives-the-lock case is closed by
    construction -- so its hazards (two publishers, an orphaned suite, a corrupt directory, test
    debris across cycles) stay pinned here rather than becoming rediscoveries on the day someone
    flips it back.

    What this fixture must never do is stand in for the shipped behaviour. The switch being OFF
    is asserted by `test_the_shipped_default_gives_every_cycle_its_own_checkout`, which is the
    same scenario as `test_the_checkout_is_reused_and_keeps_its_bytecode` with the flag the other
    way round -- so the two tests are each other's mutation, on the one line that decides it."""
    monkeypatch.setattr(prc, "REUSE_HEAD_CHECKOUT", True)


def _project_dir_paths_this_module_writes(module=None):
    """Module-level path constants declared off `PROJECT_DIR` that the module WRITES.

    DERIVED FROM THE SOURCE, never hand-listed -- that is the whole point. The `sandbox`
    fixture below used to redirect the three live paths whoever wrote it happened to think of
    (`PROJECT_DIR`, `LAST_TESTED_HASH_FILE`, `LOG_FILE`), and every path constant added by a
    LATER atom escaped it silently, because a constant declared as `PROJECT_DIR / ...` is
    resolved at IMPORT time -- re-pointing `prc.PROJECT_DIR` afterwards moves nothing.

    Observed cost (2026-08-10, 20:56:35Z): `GATE_BLOCKING_TESTS_FILE` escaped, so running this
    file wrote the machine's live `docs/observability/.last_gate_blocking_tests.json` with a
    SANDBOX commit SHA (`1c0414e9f...`, which `git cat-file -t` calls a bad object) and an
    empty `node_ids`. That file is the wedge alarm's ONE non-guessing source of "which test is
    blocking publishing", and a fresh-but-empty record does not read as absent -- it reads as
    "the gate printed no FAILED line", so the alarm falls back to citing findings by mtime,
    the exact 0/8-hit-rate guess that constant's own comment was written to end. The file is
    in the gate's own scoped blocking list, so this fired on every publish cycle.
    """
    import ast

    module = prc if module is None else module
    source = ast.parse(Path(module.__file__).read_text())
    declared = {
        node.targets[0].id
        for node in source.body
        if isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and ast.unparse(node.value).startswith("PROJECT_DIR")
    }
    mutating = {"write_text", "write_bytes", "unlink", "touch", "mkdir", "open", "rmdir"}
    written = set()
    for node in ast.walk(source):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in mutating:
            continue
        receiver = node.func.value
        while isinstance(receiver, ast.Attribute):   # NAME.parent.mkdir(...)
            receiver = receiver.value
        if isinstance(receiver, ast.Name) and receiver.id in declared:
            written.add(receiver.id)
    return written


@pytest.fixture
def sandbox(tmp_path, monkeypatch, logged):
    """A real git repo standing in for the shared tree, with one committed source file.

    Returns the repo path. `prc.PROJECT_DIR` and `prc.HEAD_CHECKOUT_ROOT` are redirected here so
    the whole checkout lifecycle runs for real without touching the machine's tree or its live
    reused checkout.

    Every writable `PROJECT_DIR`-derived constant is redirected too, DERIVED rather than listed
    (see above): the named ones below are kept for readability, but the loop is what makes a
    constant added tomorrow isolated tomorrow instead of at the next incident."""
    repo = tmp_path / "tree"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "thing.py").write_text("VALUE = 'committed'\n")
    # REPO-SHAPED, AND COMMITTED (2026-08-12, the eighteenth wedge -- this fixture WAS it).
    # `resolve_scope` refuses a root that is not a checkout of this repo, and `_run_gate_in`
    # turns that refusal into (False, False) before argv exists -- so a stand-in tree holding
    # only `pkg/thing.py` made every assertion below unreachable by any behaviour of the code
    # they are about. Called before `git add`, because the gate's subject here is produced by
    # `git archive HEAD` and an uncommitted shape would not survive the trip.
    materialise_repo_shaped_root(repo)
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "t@example.com"], repo)
    _git(["config", "user.name", "T"], repo)
    _git(["add", "-A"], repo)
    commit = _git(["commit", "-q", "-m", "committed truth", "--no-verify"], repo)
    assert commit.returncode == 0, commit.stderr

    checkout_root = tmp_path / "checkouts"
    checkout_root.mkdir()
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)
    monkeypatch.setattr(prc, "HEAD_CHECKOUT_ROOT", checkout_root)
    # ISOLATE THE PYTEST-TEMP SWEEP'S OWN ROOT (2026-08-12, the nineteenth wedge). It used to
    # borrow HEAD_CHECKOUT_ROOT, so redirecting that one constant isolated both sweeps at once
    # -- and that shared constant was the defect. Now they are separate subjects, this one has
    # to be redirected explicitly, and it MUST be: its production default is the real
    # `tempfile.gettempdir()`, so a test that planted roots and swept without this would delete
    # the temp directories of every other suite running on this box, including its own.
    pytest_temp_root = tmp_path / "pytest-temps"
    pytest_temp_root.mkdir()
    monkeypatch.setattr(prc, "PYTEST_TEMP_ROOT_PARENT", pytest_temp_root)
    # THE MACHINE'S FREE SPACE IS NOT THIS MODULE'S SUBJECT (2026-08-14, the twentieth wedge --
    # and, like the eighteenth, this fixture WAS it).
    #
    # `HEAD_CHECKOUT_ROOT` is redirected above into `tmp_path`, which pytest puts under
    # `tempfile.gettempdir()` -- on this box a 7.8G **tmpfs**. `_head_checkout`'s disk pre-flight
    # then measured that tmpfs against the PRODUCTION floor (`HEAD_CHECKOUT_MIN_FREE_MB` = 400MB,
    # sized for a real 8,662-file checkout) and refused to materialise a stand-in repo of eight
    # files. Observed 2026-08-14 12:03Z, publishing wedged since 06:29Z, with the gate's own log
    # line in the sandbox saying it outright: "DISK, not code -- only 354MB free". `df` agreed:
    # /tmp at 96%. Production was never affected -- its root is `/var/tmp` on ext4, 888G free --
    # so the red was the box's tmpfs weather wearing this test's name, and it would have cleared
    # and returned on its own (`feedback_a_control_that_must_win_a_race_has_the_weather_as_its
    # _subject`).
    #
    # So the pre-flight is PINNED here, exactly as `test_publish_gate_disk_preflight.py` pins it
    # for its own subject -- that module owns the guard's behaviour in both directions and is
    # where a change to it must show up. Nothing here weakens it: the constant is untouched, and
    # `test_a_full_filesystem_under_the_sandbox_cannot_red_the_verdict` below is this pin's
    # mutation test, red the moment this line is removed.
    monkeypatch.setattr(prc, "_free_mb", lambda _p: prc.HEAD_CHECKOUT_MIN_FREE_MB * 10)
    monkeypatch.setattr(prc, "UNTRACKED_DATA_OVERLAY", ())
    monkeypatch.setattr(prc, "REUSED_CHECKOUT_KEEP", ("__pycache__",))
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    # Must EXIST: not every writer in prc mkdirs its parent first (LAST_TESTED_HASH_FILE
    # writes straight into a directory the live tree already has), so a redirect into a
    # nonexistent dir would turn this isolation into a new failure of its own.
    isolated = tmp_path / "isolated"
    isolated.mkdir()
    for name in sorted(_project_dir_paths_this_module_writes()):
        monkeypatch.setattr(prc, name, isolated / name)
    return repo


def _sha(repo):
    return _git(["rev-parse", "HEAD"], repo).stdout.strip()


def _argv_that_parses(rel_path):
    """A stand-in 'suite' whose verdict depends only on the file at `rel_path` IN ITS CWD.

    This is the smallest thing that can tell the two subjects apart: it reds on the broken
    working-tree copy and greens on the committed one, in whichever tree it is run."""
    src = ("import ast, pathlib, sys;"
           "ast.parse(pathlib.Path({!r}).read_text());"
           "sys.exit(0)".format(rel_path))
    return lambda test_root="tests/": [sys.executable, "-c", src]


def _break_the_working_tree(repo):
    """The dirty-tree condition, produced the way lanes really produce it: uncommitted work in a
    tracked source file. Here it is uncommitted work that does not even parse."""
    (repo / "pkg" / "thing.py").write_text("VALUE = 'mid-edit'   def (((\n")


# ── THE PROPERTY THE RULING BOUGHT ───────────────────────────────────────────

def test_a_dirty_working_tree_does_not_change_the_verdict(sandbox, monkeypatch):
    """A lane's uncommitted, not-even-parsing work must not touch the publish verdict.

    This is the whole point of the ruling and nothing asserted it until now. Twice on 2026-08-09
    it was the live failure: first one uncommitted isort fix, then KNIFE2's 19 staged-but-
    uncommitted files, which held publishing down from 12:56Z on three reds that HEAD passes."""
    _break_the_working_tree(sandbox)
    monkeypatch.setattr(prc, "publish_gate_pytest_argv", _argv_that_parses("pkg/thing.py"))

    passed, timed_out = prc.run_fast_tests(_sha(sandbox))

    assert passed is True, "committed truth is green; a lane mid-edit must not be able to red it"
    assert timed_out is False
    assert prc.LAST_TESTED_HASH_FILE.read_text().strip() == _sha(sandbox)


def test_mutation_pointing_the_gate_back_at_the_tree_reds(sandbox, monkeypatch):
    """MUTATION (R15). Identical scenario, subject moved back to the working tree: the verdict
    flips to RED. That is what proves the green above is produced BY the checkout and is not the
    test agreeing with itself -- and it reproduces the pre-ruling defect exactly."""
    _break_the_working_tree(sandbox)
    monkeypatch.setattr(prc, "publish_gate_pytest_argv", _argv_that_parses("pkg/thing.py"))

    real_run_gate_in = prc._run_gate_in
    monkeypatch.setattr(
        prc, "_run_gate_in",
        lambda cwd, env, git_hash: real_run_gate_in(prc.PROJECT_DIR, env, git_hash))

    passed, _ = prc.run_fast_tests(_sha(sandbox))

    assert passed is False, (
        "with the shared tree as its subject the gate reds on work that was never committed -- "
        "if this passes, the checkout is no longer what decides the verdict")
    assert not prc.LAST_TESTED_HASH_FILE.exists()


def test_a_full_filesystem_under_the_sandbox_cannot_red_the_verdict(sandbox, monkeypatch):
    """MUTATION (R15) on the `sandbox` fixture's disk pin -- red the moment that pin is removed.

    The incident this reproduces (2026-08-14, the twentieth wedge): the fixture's checkout root
    lives on the box's tmpfs, the tmpfs was at 96%, and the production 400MB floor refused a
    checkout for an eight-file stand-in repo -- so the verdict of the test above was the free
    space on /tmp rather than anything about a dirty tree, and publishing stayed down 6h.

    The sabotage is at the MACHINE measurement (`shutil.disk_usage`), one layer below the pin,
    and it reports a genuinely full filesystem rather than an unreadable one: `_free_mb` maps an
    OSError to None, and None already means "could not measure, proceed", so raising would pass
    with or without the pin and prove nothing. Zero free bytes is the condition that actually
    refuses. With the pin, `_free_mb` is never consulted and the verdict is unmoved."""
    _break_the_working_tree(sandbox)
    monkeypatch.setattr(prc, "publish_gate_pytest_argv", _argv_that_parses("pkg/thing.py"))
    monkeypatch.setattr(prc.shutil, "disk_usage",
                        lambda _p: _DiskUsage(total=1 << 40, used=1 << 40, free=0))

    passed, timed_out = prc.run_fast_tests(_sha(sandbox))

    assert passed is True, (
        "the machine's free space decided this module's verdict -- the pre-flight is production "
        "behaviour and belongs to test_publish_gate_disk_preflight.py, not to a fixture whose "
        "checkout root pytest happens to place on a tmpfs")
    assert timed_out is False


def test_the_gate_runs_with_its_cwd_inside_the_checkout(sandbox, monkeypatch):
    """Directly: the process the gate spawns has the CHECKOUT as its cwd, not PROJECT_DIR.

    Asserted on the child's own `os.getcwd()` rather than on the argv we passed, so a future
    refactor that quietly loses the `cwd=` keyword cannot pass this.

    Asserted on the checkout ROOT and PREFIX rather than on one directory name: which checkout
    the cycle gets is a lifecycle choice that has already changed once (the reused directory was
    eliminated on 2026-08-11), and pinning the name here made this test red on that change while
    the property it exists for -- the gate does not run in the shared tree -- still held."""
    where = sandbox.parent / "where.txt"
    monkeypatch.setattr(
        prc, "publish_gate_pytest_argv",
        lambda test_root="tests/": [sys.executable, "-c",
                                    "import os, pathlib; pathlib.Path({!r}).write_text("
                                    "os.getcwd())".format(str(where))])

    prc.run_fast_tests(_sha(sandbox))

    ran_in = Path(where.read_text())
    assert ran_in != sandbox, "the gate ran in the shared tree"
    assert ran_in.resolve().parent == prc.HEAD_CHECKOUT_ROOT.resolve(), (
        "the gate's cwd is not a checkout this module's own root owns"
    )
    assert ran_in.name.startswith(prc.HEAD_CHECKOUT_PREFIX)


# ── UNAVAILABLE MEANS BLOCKED ────────────────────────────────────────────────

def test_an_unavailable_checkout_blocks_the_publish(sandbox, monkeypatch, logged):
    """R15: an unavailable check is a FAILED check. If committed truth cannot be produced there
    is nothing legitimate to test, so nothing may be published."""
    monkeypatch.setattr(prc, "_materialise_head_into", lambda dest, sha: False)
    monkeypatch.setattr(prc, "publish_gate_pytest_argv", _argv_that_parses("pkg/thing.py"))

    passed, timed_out = prc.run_fast_tests(_sha(sandbox))

    assert (passed, timed_out) == (False, False)
    assert not prc.LAST_TESTED_HASH_FILE.exists(), (
        "a gate with no subject must not leave a claim that this SHA passed -- that hash is the "
        "supervisor wedge draw's independent cross-check")
    assert any("could NOT materialise" in line for line in logged)


def test_mutation_a_permissive_verdict_publishes_unverified(sandbox, monkeypatch):
    """MUTATION (R15). Same unavailable checkout, the fail-closed verdict disarmed to
    `(True, False)`: the publish proceeds on a gate that never ran. The block above is therefore
    produced by `_checkout_unavailable_verdict` and by nothing else in the path."""
    monkeypatch.setattr(prc, "_materialise_head_into", lambda dest, sha: False)
    monkeypatch.setattr(prc, "_checkout_unavailable_verdict", lambda: (True, False))

    passed, _ = prc.run_fast_tests(_sha(sandbox))

    assert passed is True


def test_a_red_suite_does_not_stamp_the_tested_hash(sandbox, monkeypatch):
    """The `.last_tested_hash` contract (LAST_TESTED_HASH_CONTRACT): written by one writer, only
    on rc=0. Anything that stamps it without a green suite turns the supervisor's independence
    cross-check into a tautology."""
    monkeypatch.setattr(prc, "publish_gate_pytest_argv",
                        lambda test_root="tests/": [sys.executable, "-c", "raise SystemExit(1)"])

    passed, _ = prc.run_fast_tests(_sha(sandbox))

    assert passed is False
    assert not prc.LAST_TESTED_HASH_FILE.exists()


def _declared_path_expression(module_path, name):
    """The SOURCE text of a module-level assignment, e.g. `PROJECT_DIR / "docs" / ...`.

    Read from source rather than from the imported attribute on purpose: this suite's conftest
    monkeypatches `supervisor.LAST_TESTED_HASH_FILE` into a tmp_path for isolation, so the live
    attributes are not what the machine runs on. The declarations are."""
    import ast

    tree = ast.parse(Path(module_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.unparse(node.value)
    raise AssertionError("{} does not declare {}".format(module_path, name))


def test_the_hash_contract_is_stated_in_one_place():
    """Two consumers, one contract. The supervisor's wedge draw reads this file as its
    INDEPENDENCE cross-check; if the two paths ever diverge the cross-check silently reads a file
    nobody writes, and a stale wedge draws forever."""
    from background import supervisor

    assert (_declared_path_expression(supervisor.__file__, "LAST_TESTED_HASH_FILE")
            == _declared_path_expression(prc.__file__, "LAST_TESTED_HASH_FILE"))
    contract = prc.LAST_TESTED_HASH_CONTRACT
    assert "_run_gate_in" in contract and "rc=0" in contract, "the WRITER must be named"
    assert "run_fast_tests" in contract and "wedge" in contract, "both READERS must be named"


# ── THIS FILE MUST NOT WRITE THE MACHINE'S OWN OBSERVABILITY STATE ───────────
#
# R10: the instance was `GATE_BLOCKING_TESTS_FILE`; the CLASS is "the sandbox isolates the
# paths its author thought of". Closed by DERIVING the population from prc's source, so the
# fixture cannot fall behind the module. The three tests below are that derivation's own R15:
# it must be non-empty, it must discriminate written from merely-read, and the redirect must
# demonstrably move every member off the real tree.

def test_the_isolated_population_is_not_empty_and_names_the_path_that_escaped():
    """VACUITY GUARD. A derivation that quietly returns the empty set would make the fixture's
    redirect loop a no-op and this whole control theatre -- the same fail-open shape as a
    scope that narrows to nothing. `GATE_BLOCKING_TESTS_FILE` is asserted BY NAME because it
    is the one that actually reached the machine's live state."""
    population = _project_dir_paths_this_module_writes()

    assert len(population) >= 3, "suspiciously small writable-path population: {}".format(
        sorted(population))
    assert "GATE_BLOCKING_TESTS_FILE" in population, (
        "the wedge alarm's blocking-test record is written by this module and MUST be "
        "isolated -- it escaping is what put a sandbox SHA in the live file on 2026-08-10")


def test_the_derivation_tells_a_written_path_from_a_read_one(tmp_path):
    """MUTATION on the DERIVATION, not on the source. Two near-identical modules: one only
    reads its PROJECT_DIR constant, one writes it. If the derivation cannot separate them it
    is returning 'every constant' and its agreement with reality is a coincidence."""
    import types

    def _derive(body):
        path = tmp_path / "m{}.py".format(abs(hash(body)))
        path.write_text(body)
        return _project_dir_paths_this_module_writes(
            types.SimpleNamespace(__file__=str(path)))

    read_only = _derive('PROJECT_DIR = 1\nA = PROJECT_DIR / "x"\ndef f():\n    return A.read_text()\n')
    written = _derive('PROJECT_DIR = 1\nA = PROJECT_DIR / "x"\ndef f():\n    A.write_text("y")\n')
    nested = _derive('PROJECT_DIR = 1\nA = PROJECT_DIR / "x"\ndef f():\n    A.parent.mkdir()\n')

    assert read_only == set(), "a path that is only READ needs no isolation"
    assert written == {"A"} and nested == {"A"}, "a written path must be caught, incl. via .parent"


def test_the_sandbox_moves_every_writable_path_off_the_real_tree(sandbox):
    """THE LIVE CONTROL. Reds if any writable constant still resolves inside this repo while
    the fixture is active -- which is exactly the state that let a gate test overwrite the
    alarm's diagnostic payload every publish cycle."""
    real_repo = Path(__file__).resolve().parents[2]

    escaped = [name for name in sorted(_project_dir_paths_this_module_writes())
               if real_repo in Path(getattr(prc, name)).resolve().parents]

    assert not escaped, (
        "{} still point inside {} under the sandbox fixture -- running this test file writes "
        "the machine's live observability state".format(escaped, real_repo))


# ── THE BOUND IS CHECKED AGAINST ITS EVIDENCE, NOT AGAINST A COPY OF ITSELF ──
#
# OPS2 criterion 2 asks for GATE_SUITE_TIMEOUT_SECONDS to be re-derived from the measured
# runtime. It was -- but the only control on the result compared the constant against
# `MEASURED_SUITE_SECONDS = 1291.9`, a second hand-copied transcription of the same phase of the
# same record. Two copies of one number cannot disagree unless someone re-copies one of them, so
# that control could fail on a typo and on nothing else -- least of all on the failure this bound
# has actually suffered twice, the measured runtime moving out from under it (600s and 1800s were
# both undersized, and the timeout fail-CLOSES, so undersized WEDGES PUBLISHING).
#
# Meanwhile the harness computed `implied_timeout_floor_2x` into the record and nothing read it.
# These tests are that consumer, and the mutation below proves they can fail.

def _cost_record(tmp_path, **record):
    path = tmp_path / "publish_gate_subject_cost.json"
    path.write_text(json.dumps(record))
    return path


def test_the_timeout_clears_the_floor_the_measurement_implies():
    """THE LIVE CONTROL. The committed record is the evidence the bound was derived from; this
    asserts the bound still clears it.

    IT HAS NOW FIRED FOR REAL TWICE, ON THE SAME DAY (2026-08-11).
      * Launch 11: the shipped subject -- a cold throwaway checkout -- measured 1411.2s against
        the 1291.9s the 2600s bound had been derived from, and this test reddened on its own
        before anyone read the record. The bound moved to 2900s. The note it left is that the old
        evidence had been timed in the since-deleted shared directory and was never the subject
        the gate ships.
      * Launch 13: the same phase re-timed at 1784.6s (floor 3569) and the bound moved to 3600s.
        This firing is the sharper evidence, because it happened WITHIN one worker tick: the
        write-time gate's scope ran 557-green at 15:20Z and 1-red at 15:35Z with no source change
        between them. The record moved underneath the claim, unprompted, which is precisely the
        failure mode a hand-copied transcription of the same number cannot detect."""
    floor = prc.measured_gate_timeout_floor()

    assert floor is not None, (
        "{} answers no floor -- the bound's evidence is gone, which is a FAILED check, not a "
        "pass: re-run `python3 -m tools.measure_publish_gate_subject_cost --systemd`"
        .format(prc.GATE_SUBJECT_COST_RECORD))
    assert prc.GATE_SUITE_TIMEOUT_SECONDS >= floor, (
        "the gate's timeout is {}s but the measured runtimes imply a floor of {}s at {}x. An "
        "undersized bound does not degrade this gate, it WEDGES PUBLISHING -- raise the constant "
        "and move test_the_gate_timeout_exceeds_the_suites_own_runtime's with it."
        .format(prc.GATE_SUITE_TIMEOUT_SECONDS, floor, prc.GATE_TIMEOUT_SAFETY_FACTOR))


def test_the_floor_rises_when_a_measured_phase_gets_slower(tmp_path):
    """MUTATION (R15), on the evidence rather than on the source: one phase measured slower and
    the floor overtakes the constant, so the control above goes red. Without this the live
    assertion is unfalsifiable -- a check that has only ever been observed passing."""
    # DERIVED FROM THE BOUND, not hardcoded at 1500.0. This fixture's only job is to be slower
    # than whatever the shipped bound was derived against, and a literal made that true only for
    # the bound of the day -- the 2600 -> 2900 move (2026-08-11) left it 100s from asserting
    # nothing, and the next move would have reddened a test that is not about the bound at all.
    slower_than_the_bound = prc.GATE_SUITE_TIMEOUT_SECONDS / prc.GATE_TIMEOUT_SAFETY_FACTOR + 100
    slower = _cost_record(tmp_path, phases={"cold_checkout": {"seconds": slower_than_the_bound}})

    floor = prc.measured_gate_timeout_floor(slower)

    assert floor == int(slower_than_the_bound * prc.GATE_TIMEOUT_SAFETY_FACTOR)
    assert floor > prc.GATE_SUITE_TIMEOUT_SECONDS, (
        "a phase measured slower than the bound's own evidence must put the floor above the "
        "shipped bound -- if it does not, the live control cannot red on the only thing that "
        "goes wrong with this bound")


def test_a_partial_record_still_yields_a_floor(tmp_path):
    """The measurement has been killed or deferred eight times and `complete` has never once been
    true. A floor that waits for a complete record is a control that never fires, so every banked
    phase counts -- each one is admitted-quiet by construction."""
    partial = _cost_record(tmp_path, complete=False, phases_missing=["in_tree_baseline"],
                           phases={"cold_checkout": {"seconds": 1000.0},
                                   "warm_checkout": {"seconds": 900.0}})

    assert prc.measured_gate_timeout_floor(partial) == 2000, "the WORST banked phase, x2"


def test_the_harness_stated_floor_is_never_under_read(tmp_path):
    """`implied_timeout_floor_2x` is the harness's own answer. If a re-derivation here ever drifts
    below it, the higher of the two wins -- one name must not end up meaning two numbers, and the
    safe direction on a timeout is up."""
    stated = _cost_record(tmp_path, phases={"cold_checkout": {"seconds": 100.0}},
                          implied_timeout_floor_2x=4000)

    assert prc.measured_gate_timeout_floor(stated) == 4000


@pytest.mark.parametrize("record", [
    None,                                            # absent
    "{not json",                                     # malformed
    json.dumps([1, 2, 3]),                           # right file, wrong shape
    json.dumps({"phases": {}}),                      # a checkpoint written before phase one
    json.dumps({"phases": {"cold": {"seconds": None}}}),      # phase banked with no runtime
    json.dumps({"phases": {"cold": {"seconds": True}}}),      # bool is not a duration
    json.dumps({"phases": {"cold": {"seconds": "1291.9"}}}),  # string is not a duration
])
def test_a_record_that_cannot_answer_yields_no_floor(tmp_path, record):
    """FAIL-CLOSED, not fail-open: an unanswerable record must produce None so the live control
    reds, never a small floor the constant happens to clear. `seconds: 0` and `seconds: True`
    are the shapes that would sneak a 0-second floor past a naive `if seconds:`."""
    path = tmp_path / "publish_gate_subject_cost.json"
    if record is not None:
        path.write_text(record)

    assert prc.measured_gate_timeout_floor(path) is None


# ── THE SHIPPED LIFECYCLE: ONE THROWAWAY CHECKOUT PER CYCLE ──────────────────
#
# The atom minted exit criterion 1 as "a REUSED checkout so __pycache__ survives between
# cycles". That criterion is SUPERSEDED, not met: reuse was eliminated on 2026-08-11 under R3
# after the shared directory produced a fourth false red and left publishing down 41 hours. The
# cost of the elimination is cold bytecode every cycle; what it bought is a gate that can pass
# at all. The atom record carries the supersession and the residual (the per-cycle tax is still
# real and still unmeasured against an in-tree baseline).

def test_the_shipped_default_gives_every_cycle_its_own_checkout(sandbox, logged):
    """THE R3 ELIMINATION, as a property of the shipped default rather than as a comment.

    Every cycle gets a directory nothing else has touched, and it does not outlive the cycle. No
    lock, no liveness heuristic, no occupancy guard stands between two publishers -- they cannot
    reach the same directory, which is the only form of that guarantee that survived four
    attempts to make sharing safe.

    MUTATION (R15), and it is one line: `test_the_checkout_is_reused_and_keeps_its_bytecode`
    below is this exact scenario with `REUSE_HEAD_CHECKOUT = True`, and there the directory both
    persists and comes back. Each test reds if the switch is flipped under it."""
    assert prc.REUSE_HEAD_CHECKOUT is False, (
        "the reused checkout is live again -- re-read the R3 record in `_head_checkout` first: "
        "re-enabling is only legitimate once a killed publisher's suite dies with it"
    )

    with prc._head_checkout() as first:
        assert first is not None
        assert first.name != prc.REUSED_HEAD_CHECKOUT_NAME, (
            "the cycle took the shared directory -- the four false reds are reachable again"
        )
        (first / "debris.txt").write_text("written by this cycle's suite")

    assert not first.exists(), (
        "a throwaway checkout outlived its cycle -- 130MB per publish, and the sweep is the "
        "only thing left holding the tmpfs open"
    )

    with prc._head_checkout() as second:
        assert second is not None
        assert second != first, "the next cycle was handed the previous cycle's directory"
        assert not (second / "debris.txt").exists()
        assert _git(["rev-parse", "HEAD"], second).stdout.strip() == _sha(sandbox)

    assert any("R3 elimination" in line for line in logged), (
        "R5 -- the log must name WHY the gate is paying for a cold checkout, or the next reader "
        "diagnoses the cost as a regression and re-enables the thing that caused the outage"
    )


# ── THE DORMANT REUSE PATH (behind the one-line switch) ──────────────────────

def test_the_checkout_is_reused_and_keeps_its_bytecode(sandbox, reuse_enabled):
    """The reuse MECHANISM, exercised behind `reuse_enabled` because it no longer ships on.

    Doubles as the mutation partner of the test above: same scenario, switch the other way. The
    runtime reuse buys is measured in the atom record, not asserted here -- a wall-clock
    assertion on a shared box is a flake, and R12 says a measured number is a diagnostic, not a
    target. What holds while the switch is on is this: the same directory comes back, and
    `__pycache__` survives into it."""
    with prc._head_checkout() as first:
        assert first is not None
        pyc = first / "pkg" / "__pycache__" / "thing.cpython-x.pyc"
        pyc.parent.mkdir(parents=True, exist_ok=True)
        pyc.write_text("bytecode")
        (first / "debris.txt").write_text("written by a previous suite")

    assert first.exists(), "the reused checkout must survive between cycles -- that is the point"

    with prc._head_checkout() as second:
        assert second == first
        assert pyc.exists(), "bytecode did not survive the refresh; every cycle recompiles cold"
        assert not (second / "debris.txt").exists(), (
            "a previous suite's leftovers survived into this cycle -- the gate is no longer "
            "hermetic and cycle N can judge cycle N+1")


def test_the_refresh_follows_head_when_it_moves(sandbox, reuse_enabled):
    """A reused directory that kept judging yesterday's commit would be worse than a fresh one:
    it would pass a SHA nobody asked about while reporting the new one."""
    with prc._head_checkout() as first:
        assert (first / "pkg" / "thing.py").read_text() == "VALUE = 'committed'\n"

    (sandbox / "pkg" / "thing.py").write_text("VALUE = 'second commit'\n")
    (sandbox / "pkg" / "added.py").write_text("NEW = 1\n")
    _git(["add", "-A"], sandbox)
    _git(["commit", "-q", "-m", "second", "--no-verify"], sandbox)

    with prc._head_checkout() as second:
        assert (second / "pkg" / "thing.py").read_text() == "VALUE = 'second commit'\n"
        assert (second / "pkg" / "added.py").exists()
        assert _git(["rev-parse", "HEAD"], second).stdout.strip() == _sha(sandbox)


def test_a_second_publisher_never_shares_the_reused_checkout(sandbox, logged, reuse_enabled):
    """Two publishers refreshing one directory would corrupt each other's run: `read-tree
    --reset` under a live suite deletes and rewrites the files it is executing. The lock is
    non-blocking, so the second publisher gets a correct (cold) throwaway rather than a wait."""
    lock_path = prc.HEAD_CHECKOUT_ROOT / prc.REUSED_HEAD_CHECKOUT_LOCK_NAME
    holder = open(str(lock_path), "a+")
    fcntl.flock(holder.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with prc._head_checkout() as path:
            assert path is not None, "a held lock must not block the publish, only slow it"
            assert path.name != prc.REUSED_HEAD_CHECKOUT_NAME
            assert (path / "pkg" / "thing.py").exists()
            throwaway = path
    finally:
        fcntl.flock(holder.fileno(), fcntl.LOCK_UN)
        holder.close()

    assert not throwaway.exists(), "the fallback checkout must not outlive its cycle"
    assert any("another publisher" in line for line in logged)


def test_the_throwaway_checkout_is_removed_even_when_the_run_raises(sandbox):
    """`finally:` is the only thing standing between a raising gate and a 130MB leak per cycle."""
    lock_path = prc.HEAD_CHECKOUT_ROOT / prc.REUSED_HEAD_CHECKOUT_LOCK_NAME
    holder = open(str(lock_path), "a+")
    fcntl.flock(holder.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    seen = {}
    try:
        with pytest.raises(RuntimeError):
            with prc._head_checkout() as path:
                seen["path"] = path
                raise RuntimeError("the gate blew up mid-run")
    finally:
        fcntl.flock(holder.fileno(), fcntl.LOCK_UN)
        holder.close()

    assert seen["path"] is not None
    assert not seen["path"].exists()


def test_stale_checkouts_are_swept_and_live_ones_are_not(sandbox):
    """Crash-safety. `finally:` does not run under SIGKILL and rc=-9 is a known gate outcome, so
    leaked checkouts are expected -- 4.4GB of them exhausted the tmpfs on 2026-08-09 and wedged
    publishing with a message about git. The sweep runs BEFORE the disk pre-flight, which is what
    makes that failure self-healing.

    Both directions in one test on purpose: a sweep that also removed live directories would
    delete a running publisher's subject out from under its own suite."""
    root = prc.HEAD_CHECKOUT_ROOT
    old = root / (prc.HEAD_CHECKOUT_PREFIX + "abandoned")
    fresh = root / (prc.HEAD_CHECKOUT_PREFIX + "running")
    reused = root / prc.REUSED_HEAD_CHECKOUT_NAME
    unrelated = root / "someone-elses-tmpdir"
    for d in (old, fresh, reused, unrelated):
        d.mkdir()
        (d / "f").write_text("x")
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    os.utime(old, (ancient, ancient))
    os.utime(unrelated, (ancient, ancient))

    removed = prc._sweep_stale_head_checkouts()

    assert removed == 1
    assert not old.exists()
    assert fresh.exists(), "a checkout younger than the bound may be a LIVE publisher's subject"
    assert reused.exists(), "the reused checkout is never debris"
    assert unrelated.exists(), "the sweep owns its own prefix and nothing else"


def test_the_stale_bound_clears_the_gate_timeout(sandbox):
    """Anti-vacuity for the bound itself: if the age threshold were ever set below the suite's
    own timeout, the sweep could delete a running publisher's checkout mid-suite."""
    assert prc.STALE_HEAD_CHECKOUT_AGE_SECONDS > prc.GATE_SUITE_TIMEOUT_SECONDS * 1.5


def _pytest_root(parent, n, age_s=None, lock_pid=None):
    """A numbered pytest root. `lock_pid` writes pytest's own `.lock` the way pytest does.

    NO lock is the CLEAN-EXIT state (pytest's atexit hook unlinks it), which since 2026-08-12 is
    provable debris rather than a root of unknown standing -- so tests that mean "a live suite
    owns this" must now say so with a live PID, not with a recent mtime."""
    d = parent / "pytest-{}".format(n)
    d.mkdir(parents=True)
    (d / "f").write_text("x")
    if lock_pid is not None:
        (d / prc.PYTEST_TEMP_LOCK_NAME).write_text(str(lock_pid))
    if age_s is not None:
        os.utime(d, (age_s, age_s))
    return d


def test_stale_pytest_temp_roots_are_swept_and_a_live_holder_is_kept(sandbox):
    """The fifteenth wedge. pytest prunes its own numbered roots, but a suite SIGKILLed mid-run
    (rc=-9, the known gate outcome) never gets to -- so they pile up exactly when the gate is
    already in trouble, and on a tmpfs those bytes are RAM.

    Both directions in one test: a sweep that took a RUNNING suite's tmp_path out from under it
    would be worse than the leak it fixes. Since 2026-08-12 that direction is held by PROOF of
    the holder (pytest's `.lock` PID) rather than by the newest-three window, which measurement
    showed was protecting three finished sessions while the one live suite sat fourth."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-someone"
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    # Six roots, ALL ancient; mtimes ascend with the number. None carries a lock, so each is a
    # session that exited cleanly -- provable debris whatever its rank.
    old = [_pytest_root(parent, n, ancient + n) for n in range(6)]
    # Ancient AND held by a live PID -- this process. The old rule would have deleted it.
    live = _pytest_root(parent, 7, ancient, lock_pid=os.getpid())
    # Lockless but inside the create race: pytest makes the directory just before the lock.
    fresh = _pytest_root(parent, 99)
    unrelated = prc.PYTEST_TEMP_ROOT_PARENT / "someone-elses-tmpdir"
    unrelated.mkdir()
    os.utime(unrelated, (ancient, ancient))

    removed = prc._sweep_stale_pytest_temp_roots()

    kept = sorted((p.name for p in old + [live, fresh] if p.exists()))
    assert removed == 6, "every root whose holder is proved gone, regardless of rank or age"
    assert kept == ["pytest-7", "pytest-99"], kept
    assert live.exists(), (
        "a root whose `.lock` names a LIVE pid is held at any age -- the 3h bound used to "
        "delete it out from under a suite still running at 3h01")
    assert fresh.exists(), "inside PYTEST_TEMP_MIN_AGE_SECONDS: not yet debris"
    assert unrelated.exists(), "this sweep owns pytest roots and nothing else"


def test_a_dead_lock_pid_is_debris_the_age_bound_cannot_see(sandbox):
    """R15, against defect 2's own named defect -- the reason the drain reclaimed nothing.

    MEASURED 2026-08-12 05:12Z, gate wedged ~19h: four roots holding 2.0G named PIDs that were
    gone (SIGKILLed sessions, atexit never ran), and every one of them was YOUNGER than the 3h
    bound -- the oldest 1h, the newest 16 minutes. This reconstructs that population. It fails
    on the pre-fix rule, which reclaims nothing from it."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-rich"
    now = time.time()
    dead_pid = _a_pid_that_is_not_running()
    # Ages as measured: all well inside the 3h bound, all well outside the create race.
    killed = [_pytest_root(parent, n, now - age, lock_pid=dead_pid)
              for n, age in ((104, 3600), (114, 2700), (116, 2100), (134, 960))]

    assert all(now - p.stat().st_mtime < prc.STALE_HEAD_CHECKOUT_AGE_SECONDS for p in killed), (
        "vacuity guard: this population must be INSIDE the age bound, or it is not the one "
        "that wedged publishing and this test proves nothing about the clock's blindness")

    removed = prc._sweep_stale_pytest_temp_roots()

    assert removed == len(killed), (
        "a root whose lock names a dead PID is debris at any age -- the clock could not see "
        "2.0G of it while the tmpfs filled")
    assert not any(p.exists() for p in killed)


def test_liveness_that_cannot_be_established_falls_back_to_the_age_bound(sandbox, monkeypatch):
    """R15 fail-silent: an unavailable check is a FAILED check, never permission to delete.

    If the holder cannot be proved -- an unreadable lock, no procfs, a lock that is not a PID --
    the sweep must behave exactly as it did before this mechanism existed, because the direction
    that matters is deleting a live suite's root."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-someone"
    now = time.time()
    ancient = now - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    # One root inside the age bound (rank 0), then five ancient ones, mtimes ascending. Under the
    # old rule the keep-window takes ranks 0-2, so two ANCIENT roots are spared by rank alone --
    # which is what makes this test see the window rather than only the clock.
    recent = _pytest_root(parent, 0, now - 3600)
    old = [_pytest_root(parent, n, ancient + n) for n in range(10, 15)]

    monkeypatch.setattr(prc, "_pytest_root_holder",
                        lambda path: (prc.HOLDER_UNPROVEN, None))

    removed = prc._sweep_stale_pytest_temp_roots()

    assert recent.exists(), "unproven and inside the age bound: spared, exactly as before"
    assert [p.name for p in old if p.exists()] == ["pytest-14", "pytest-13"][::-1], (
        "the two ancient roots inside the keep-window are spared by RANK -- the old rule's "
        "other half, and it must still be live on the unproven path")
    assert removed == 3, (
        "unproven falls back to the OLD rule whole -- keep-newest window, then the 3h bound")


def test_a_recycled_pid_does_not_hold_a_root_forever(sandbox):
    """The pid-reuse guard. "There is a process numbered N" is not evidence that the session
    which wrote N into the lock still runs; Linux recycles PIDs. Without this, one collision
    strands a root permanently -- a leak that no clock and no proof would ever clear."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-someone"
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    root = _pytest_root(parent, 1, ancient, lock_pid=os.getpid())
    # The lock predates this process, so THIS pid cannot be the session that wrote it.
    lock = root / prc.PYTEST_TEMP_LOCK_NAME
    stranded = prc._process_start_epoch(os.getpid()) - prc.PID_REUSE_SLACK_SECONDS - 60
    os.utime(lock, (stranded, stranded))

    assert prc._pytest_root_holder(root)[0] == prc.HOLDER_DEBRIS
    assert prc._sweep_stale_pytest_temp_roots() == 1


def test_the_holder_is_proved_from_the_lock_not_from_a_proc_reference_scan(sandbox):
    """R15 against the design that MEASUREMENT REFUTED, so it cannot be re-adopted quietly.

    The filed finding proposed proving liveness by scanning /proc for a process referencing the
    root. Measured at 05:12Z: NO live process referenced any pytest root by cwd, open fd or
    memory map -- including pid 836345, the suite demonstrably running inside `pytest-128`.
    pytest closes the lock fd the moment it has written it. A reference scan reads a live suite's
    own root as unheld, which is fail-open in the only direction that matters.

    So: a root that no process references in any way, but whose lock names a live PID, is HELD."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-someone"
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    root = _pytest_root(parent, 1, ancient, lock_pid=os.getpid())

    referenced = [readlink for readlink in (_paths_this_process_references())
                  if str(root) in str(readlink)]
    assert not referenced, (
        "vacuity guard: this test only says something if the live holder really does NOT "
        "reference its own root -- it does here: {}".format(referenced))

    assert prc._pytest_root_holder(root)[0] == prc.HOLDER_HELD
    assert prc._sweep_stale_pytest_temp_roots() == 0
    assert root.exists()


def _a_pid_that_is_not_running():
    """A PID with no live process. Reaped children are the only honest way to get one."""
    proc = subprocess.Popen([sys.executable, "-c", ""])
    proc.wait()
    assert not Path("/proc/{}".format(proc.pid)).exists(), (
        "PID {} was recycled between wait() and the check -- rerun".format(proc.pid))
    return proc.pid


def _paths_this_process_references():
    """Everything this process points at through /proc: cwd, open fds, mapped files."""
    me = Path("/proc/self")
    out = []
    try:
        out.append(os.readlink(str(me / "cwd")))
    except OSError:
        pass
    for fd in (me / "fd").iterdir():
        try:
            out.append(os.readlink(str(fd)))
        except OSError:
            continue
    for line in (me / "maps").read_text().splitlines():
        parts = line.split(None, 5)
        if len(parts) == 6 and parts[5].startswith("/"):
            out.append(parts[5])
    return out


def test_the_pytest_sweep_is_rooted_where_pytest_actually_builds_its_roots(tmp_path):
    """R15, against the nineteenth wedge's own defect, with an INDEPENDENT oracle.

    Every other test of this sweep PLANTS its population under whatever root the sweep is
    reading, so all of them stay green for any value of that constant -- including a value on a
    filesystem where a pytest temp root can never appear. That is what happened: 53e82b105 moved
    HEAD_CHECKOUT_ROOT from /tmp to /var/tmp for the CHECKOUTS' sake, this sweep was rooted on
    the same constant, and for 19 hours it globbed `/var/tmp/pytest-of-*` while `/tmp` filled to
    69% with 3.3G of the roots it exists to drain. Its own tests could not see it and its log
    line never fired, because it only speaks when it removes something.

    So the oracle here is not a directory this test created and not a string this test typed.
    It is `tmp_path` -- pytest telling us where it really puts a basetemp, in this very run.
    NOTE: deliberately no `sandbox`, which redirects the constant under test.
    """
    # `tmp_path` is <parent>/pytest-of-<user>/pytest-<N>/<test-name><i>. Find the `pytest-of-*`
    # link in its real chain rather than counting parents, which would pin pytest's layout.
    of_user = next((p for p in tmp_path.parents if p.name.startswith("pytest-of-")), None)
    assert of_user is not None, (
        "oracle unavailable: pytest's basetemp is not under a `pytest-of-*` root, so this test "
        "cannot say where the sweep should point -- an unavailable check is a FAILED check "
        "(R15), not a pass. Re-derive from the basetemp layout before deleting this.")

    assert of_user.parent == prc.PYTEST_TEMP_ROOT_PARENT, (
        "the sweep globs {}/{} but pytest is building its roots in {} -- the drain is pointed at "
        "a filesystem where its subject cannot exist, and will silently reclaim nothing while "
        "the tmpfs fills".format(prc.PYTEST_TEMP_ROOT_PARENT, prc.PYTEST_TEMP_ROOT_GLOB,
                                 of_user.parent))

    # And the glob really does select it, not merely sit in the right directory.
    assert of_user in set(prc.PYTEST_TEMP_ROOT_PARENT.glob(prc.PYTEST_TEMP_ROOT_GLOB))


def test_the_two_sweeps_do_not_share_one_root_constant(tmp_path, monkeypatch):
    """The CLASS, not the instance. Moving either subject must never move the other.

    The instance fix is one path; the defect was that one constant answered two questions. This
    fails if someone later re-points the pytest sweep at HEAD_CHECKOUT_ROOT for tidiness, which
    is precisely the shape that shipped.

    Asserted on BEHAVIOUR, not on the two constants being unequal: the pre-fix code had no
    second constant to compare, it simply read the checkout root, and that shape must fail here.
    """
    moved = tmp_path / "checkouts-moved-somewhere-else"
    own = tmp_path / "pytest-temps"
    moved.mkdir(), own.mkdir()
    monkeypatch.setattr(prc, "HEAD_CHECKOUT_ROOT", moved)
    monkeypatch.setattr(prc, "PYTEST_TEMP_ROOT_PARENT", own)
    # THIS TEST WAS WRITING INTO THE LIVE OBSERVABILITY LOG (caught 2026-08-12). It takes
    # `tmp_path`, not `sandbox`, so `prc.LOG_FILE` stayed pointed at the real
    # docs/observability/sim-runner-log.md and the sweep's own success line landed there --
    # 33 lines naming a `pytest-temps` path inside a test basetemp. Same class as
    # WORKER_REPORT_THE_GATES_OWN_TESTS_WERE_WRITING_THE_ALARMS_EVIDENCE_2026-08-10: a test
    # that manufactures the evidence an operator reads to judge the live system.
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60

    # Four ancient roots in each place. Only the ones on PYTEST'S root are this sweep's business.
    at_checkouts = [_pytest_root(moved / "pytest-of-someone", n, ancient + n) for n in range(4)]
    at_own = [_pytest_root(own / "pytest-of-someone", n, ancient + n) for n in range(4)]

    removed = prc._sweep_stale_pytest_temp_roots()

    assert all(p.exists() for p in at_checkouts), (
        "the sweep followed HEAD_CHECKOUT_ROOT -- that coupling is the nineteenth wedge, where "
        "moving the checkouts off tmpfs carried the tmpfs drain away with them")
    # All four are lockless, i.e. cleanly-exited sessions, so all four are proved debris. Before
    # 2026-08-12 this read `- PYTEST_TEMP_KEEP_NEWEST`: the keep-window now applies only where
    # the holder cannot be proved. The subject of THIS test is the root constant, not the count.
    assert removed == len(at_own)
    assert not at_own[0].exists(), "and it must still drain its own root"


def test_a_pytest_current_symlink_is_never_the_thing_deleted(sandbox):
    """`pytest-current` points INTO a numbered root. Deleting the link would leave the bytes on
    the tmpfs and lose the only handle to them -- a sweep that makes the leak unreachable."""
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-someone"
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    targets = [_pytest_root(parent, n, ancient + n) for n in range(5)]
    link = parent / "pytest-current"
    link.symlink_to(targets[0], target_is_directory=True)

    prc._sweep_stale_pytest_temp_roots()

    assert link.is_symlink(), "the link itself is never a sweep candidate"
    assert not targets[0].exists(), "its TARGET is swept on the same rule as any other root"


def test_the_checkout_sweep_alone_could_not_reclaim_what_wedged_it(sandbox):
    """R15, against this control's own named defect.

    The fourteen-wedge claim was that sweeping `publish-gate-head-*` before the disk pre-flight
    makes exhausted-tmpfs SELF-HEALING. It is not, and the recurrence proves it: of the 3.9G
    reclaimed by hand on 2026-08-10, the checkout sweep could see none. This reconstructs that
    measured population and asserts the pre-fix control reclaims NOTHING from it -- so if someone
    later deletes the pytest sweep, this fails rather than quietly restoring the 22h wedge."""
    root = prc.HEAD_CHECKOUT_ROOT
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    # The two halves of that measured population now sit on two filesystems (2026-08-12): the
    # checkouts moved to disk, pytest's roots stayed on the tmpfs. Reconstructing them under one
    # root would restore exactly the conflation that misrouted the drain for 19 hours.
    parent = prc.PYTEST_TEMP_ROOT_PARENT / "pytest-of-rich"
    # The offset only ORDERS the mtimes; it must stay far inside `ancient` or a root drifts back
    # within the age bound and is spared on age rather than by the keep-window.
    pytest_roots = [_pytest_root(parent, n, ancient + n * 0.01)
                    for n in (0, 31, 36, 122, 154, 158, 176, 214, 234, 235, 240, 254, 259)]
    # The ad-hoc diagnostic checkouts, under the names the investigations actually used.
    diagnostics = []
    for name in ("gate_verify", "wedge-diag2-m3fsd036", "headchk", "gatechk2",
                 "gatechk.GNMR", "headtree_probe", "headprobe2"):
        d = root / name
        d.mkdir()
        os.utime(d, (ancient, ancient))
        diagnostics.append(d)
    # The single matching checkout, 20 minutes old -- correctly OUTSIDE the bound.
    matching = root / (prc.HEAD_CHECKOUT_PREFIX + "9z78t7lu")
    matching.mkdir()

    assert prc._sweep_stale_head_checkouts() == 0, (
        "the pre-fix control reclaims nothing from the population that exhausted the tmpfs -- "
        "this is the false self-healing claim, pinned")

    # Lockless: thirteen cleanly-exited sessions, all proved debris. Was `- KEEP_NEWEST` before
    # 2026-08-12, when rank stood in for liveness; the holder is proved now.
    assert prc._sweep_stale_pytest_temp_roots() == len(pytest_roots)
    assert matching.exists(), "a 20-minute-old checkout is a live publisher's, not debris"
    assert all(d.exists() for d in diagnostics), (
        "ad-hoc diagnostic names are closed by CONVENTION, not by a glob that would have this "
        "process deleting directories it does not own")


def test_a_corrupt_reused_checkout_is_rebuilt_rather_than_trusted(sandbox, reuse_enabled):
    """The directory is state that outlives the process, so it can be found in any condition --
    truncated by a full disk, left by an older layout, borrowing an object store that has since
    moved. Unusable must mean REBUILD, never 'run the gate in it and see'."""
    with prc._head_checkout() as first:
        assert first is not None
        (first / ".git" / "objects" / "info" / "alternates").write_text("/nonexistent/objects\n")
        assert prc._checkout_is_usable(first) is False

    with prc._head_checkout() as second:
        assert second == first
        assert prc._checkout_is_usable(second) is True
        assert _git(["rev-parse", "HEAD"], second).stdout.strip() == _sha(sandbox)


# ── THE LOCK IS NOT THE OCCUPANCY (2026-08-10, the wedge that outlived its own fix) ──────────

def test_a_live_suite_in_the_reused_checkout_is_seen_even_with_the_lock_free():
    """R15 direction 1 -- the defect is REACHABLE, and it is not hypothetical.

    `flock` is held on a descriptor owned by the publisher PROCESS; the suite runs in a
    GRANDCHILD. A caller's deadline SIGKILLs the direct child only, so the pytest keeps running
    with its cwd inside the checkout while the dead parent's lock is released. The lock then
    says 'free' about a directory that is occupied, and the next cycle's `read-tree --reset` /
    `git clean` / `rmtree` lands on a live run. That produced both reds of 2026-08-10 --
    `ModuleNotFoundError: tools.test_execution_metric` at 18:25Z and `FileNotFoundError:
    '/tmp/publish-gate-head-reused'` at 18:51Z -- neither of which is about any test."""
    import tempfile as _tempfile

    with _tempfile.TemporaryDirectory() as tmp:
        occupied = Path(tmp) / "occupied"
        occupied.mkdir()
        assert prc._reused_checkout_is_in_use(occupied) is False, (
            "an empty directory reads as occupied -- the guard would wedge every cycle"
        )
        # A real process, really cwd'd in there. Nothing is mocked: the guard's whole claim is
        # that it reads first-hand occupancy, so a stubbed /proc would prove nothing.
        child = subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.read()"],
                                 cwd=str(occupied), stdin=subprocess.PIPE)
        try:
            assert prc._reused_checkout_is_in_use(occupied) is True, (
                "a live process cwd'd in the checkout was not seen -- this is the sighting the "
                "lock cannot make"
            )
        finally:
            child.stdin.close()
            child.wait(timeout=30)
        assert prc._reused_checkout_is_in_use(occupied) is False, (
            "the guard LATCHED after the process exited -- a guard that never clears wedges "
            "publishing exactly as hard as the bug it prevents"
        )


def test_the_caller_standing_in_the_checkout_is_itself_an_occupant(tmp_path, monkeypatch):
    """The RECURRENCE, 2026-08-10: the guard above was blind to the one occupant that matters.

    It skipped `os.getpid()`, so a process asking about a directory it was ITSELF standing in
    got False. That is not a hypothetical caller. `test_publish_gate_head_checkout_is_a_repo.py`
    calls `_head_checkout()` against the real root and runs inside the gate's own blocking
    scope, so an ORPHANED gate suite (killed publisher, lock released) reaches this guard as the
    sole occupant of the directory it is executing from -- and refreshed the tree under itself.

    MUTATION, and it is the code this replaces: restore `if pid == os.getpid(): continue` and
    this test fails while every other occupancy test still passes -- which is exactly how the
    same red survived the 19:08Z fix and returned at 20:18Z and 20:47Z."""
    occupied = tmp_path / "occupied"
    (occupied / "inner").mkdir(parents=True)

    assert prc._reused_checkout_is_in_use(occupied) is False, (
        "reachability -- from outside, the directory must read as free, or the guard would "
        "wedge every cycle rather than only the orphaned ones"
    )

    # No subprocess and nothing mocked: THIS process becomes the occupant, which is precisely
    # the shape the previous version could not see.
    monkeypatch.chdir(occupied)
    assert prc._reused_checkout_is_in_use(occupied) is True, (
        "the caller is standing in the directory and the guard called it free -- "
        "`_prepare_reused_checkout` would now `read-tree --reset` the tree under this very "
        "process, which is the 2026-08-10 corruption"
    )

    # A child directory counts too: pytest's own cwd sits below the checkout root, not on it.
    monkeypatch.chdir(occupied / "inner")
    assert prc._reused_checkout_is_in_use(occupied) is True, (
        "occupancy was read as the root only -- a suite cwd'd in a SUBDIRECTORY of the checkout "
        "is just as much inside it"
    )


def test_an_occupied_reused_checkout_is_not_refreshed_under_its_orphan(
        sandbox, logged, monkeypatch, reuse_enabled):
    """The wiring, not just the predicate. With the lock genuinely FREE but the directory
    occupied, the cycle must take the throwaway branch and leave the occupant's tree alone.

    MUTATION: drop the `_reused_checkout_is_in_use` call from `_head_checkout` and the reused
    directory is handed out, its marker file wiped by the refresh -- which is precisely what
    corrupted the orphaned suite in the live incident."""
    with prc._head_checkout() as first:
        assert first is not None
        assert first.name == prc.REUSED_HEAD_CHECKOUT_NAME
    # An artefact of the "still running" suite. `git clean -xdf` at refresh removes exactly this.
    (first / "orphan_was_here.txt").write_text("a live suite's working file\n")

    monkeypatch.setattr(prc, "_reused_checkout_is_in_use", lambda path: path == first)
    with prc._head_checkout() as second:
        assert second is not None, "occupancy must not block the publish, only slow it"
        assert second.name != prc.REUSED_HEAD_CHECKOUT_NAME, (
            "the gate took the occupied reused checkout and refreshed the tree under a live "
            "suite -- the 2026-08-10 corruption, reintroduced"
        )

    assert (first / "orphan_was_here.txt").exists(), (
        "the orphaned suite's tree was cleaned under it"
    )
    assert any("orphaned suite" in line for line in logged), (
        "R5 -- the fallback must say WHICH condition caused it; 'held by another publisher' "
        "would send the next diagnosis to the wrong mechanism"
    )


# ── THE CONTRACT'S ONE CONSEQUENCE, COMPOSED ACROSS BOTH CONSUMERS ───────────
#
# Criterion 5 of this atom asked for the `.last_tested_hash` semantics to be stated in ONE
# place rather than inferred from two call sites. `LAST_TESTED_HASH_CONTRACT` states them, and
# `test_the_hash_contract_is_stated_in_one_place` above guards it -- but what that test compares
# is the two modules' PATH expressions, plus a grep of the contract text for the names of its
# writer and its readers. Neither is the property the contract exists to protect.
#
# The contract's own last paragraph warns that "anything that stamps this file without a green
# suite collapses [the independence cross-check] into a tautology and blinds the wedge draw".
# Until these tests that warning was REPORTED STATE, NOT A CONTROL: no test had ever run the
# WRITER (`prc._run_gate_in`, via `run_fast_tests`) and the READER
# (`supervisor._publish_gate_wedge_active`, the RUNG-1 priority-zero draw) against one file, so
# the collapse it describes could have happened with nothing going red. A stated contract with
# no falsifier is the same shape as the prose rules CLAUDE.md says evaporate.
#
# The first two below are each other's mutation on ONE variable -- the suite's return code --
# with BOTH sides driven by the real writer, so the difference in the draw is produced by the
# gate's actual verdict and not by anything the test arranged. The third breaks the writer's
# rule and shows the tautology arriving.

def _wedged_state(now):
    """The state file of a gate that is genuinely wedged: sustained failures, comfortably past
    the rung-1 age bound.

    Derived from the detector's OWN constants rather than hardcoded, so a retuned threshold
    cannot leave this fixture describing a wedge the detector no longer recognises -- the
    fixture would then agree with the code by construction and these tests would pass on a
    detector that had stopped firing."""
    from background import supervisor

    oldest = now - (supervisor.PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS + 600)
    return {
        "failures": [{"ts": oldest + i, "reason": "a red test"}
                     for i in range(supervisor.PUBLISH_GATE_WEDGE_MIN_FAILURES)],
        "wedge_since": oldest,
    }


@pytest.fixture
def wedge(tmp_path):
    """The RUNG-1 wedge draw, pointed at prc's OWN `.last_tested_hash` -- the file the writer
    under test has just written, not a copy of it.

    That single-file wiring IS the subject. The supervisor's cross-check is independent only
    while the file it reads is the file the gate writes; a fixture that gave the reader its own
    copy would pass on exactly the divergence criterion 5 was raised to prevent."""
    from background import supervisor

    now = 1_760_000_000.0
    state_path = tmp_path / ".publish_gate_state.json"
    state_path.write_text(json.dumps(_wedged_state(now)))

    def draw(head):
        return supervisor._publish_gate_wedge_active(
            now=now, head=head, state_path=state_path,
            last_tested_path=prc.LAST_TESTED_HASH_FILE)

    return draw


def test_a_red_gate_leaves_the_rung_one_wedge_draw_armed(sandbox, monkeypatch, wedge):
    """The composition, in the direction that matters: the gate really fails, the writer really
    declines to stamp, and the wedge really draws.

    This is the path that was silent for 2h17m on both 2026-07-23 and 2026-07-24 -- the episode
    that made this rung priority zero. What keeps it armed is a NEGATIVE: the absence of a stamp
    at HEAD. Absences are the easiest thing to break by accident and the hardest to notice, which
    is why the arming is asserted here rather than assumed from the detector's own unit tests."""
    monkeypatch.setattr(prc, "publish_gate_pytest_argv",
                        lambda test_root="tests/": [sys.executable, "-c", "raise SystemExit(1)"])
    head = _sha(sandbox)

    passed, _ = prc.run_fast_tests(head)

    assert passed is False
    assert not prc.LAST_TESTED_HASH_FILE.exists(), (
        "the writer stamped a hash for a suite that failed -- the cross-check is now a tautology"
    )
    message = wedge(head)
    assert message is not None, (
        "the gate is failing and unpassed at HEAD, and the priority-zero draw stayed silent"
    )
    assert "PUBLISH-GATE WEDGE" in message


def test_a_green_gate_at_head_makes_the_same_wedge_state_stale(sandbox, monkeypatch, wedge):
    """The other direction, and the mutation of the test above on ONE variable.

    Identical wedged state file; the only difference is that the suite returns 0. The real
    writer stamps HEAD, the reader sees a pass at HEAD, and the in-window failures are correctly
    read as STALE -- no draw. Together these two show the draw tracks the gate's actual verdict
    and not merely the presence of failures in a file, which is what makes it a cross-check
    rather than a second reading of the same source."""
    monkeypatch.setattr(prc, "publish_gate_pytest_argv", _argv_that_parses("pkg/thing.py"))
    head = _sha(sandbox)

    passed, _ = prc.run_fast_tests(head)

    assert passed is True
    assert prc.LAST_TESTED_HASH_FILE.read_text().strip() == head
    assert wedge(head) is None, (
        "a gate that passed at HEAD still drew unwedge work -- the rung would draw forever on "
        "failures a later cycle already cleared"
    )


def test_mutation_a_writer_that_stamps_without_a_green_blinds_the_wedge_draw(
        sandbox, monkeypatch, wedge):
    """MUTATION (R15) -- the collapse the contract names, made to actually happen.

    The stamp is written after a run that genuinely FAILED: exactly the file state a
    `_run_gate_in` with its `rc == 0` guard loosened would leave behind. The wedge is unchanged
    and real, and the draw goes silent. So the arming asserted two tests up is produced by the
    writer's rule and by nothing else -- and a future edit that stamps on a timeout, on a
    partial run, or "so the skip works" is not a tidy-up, it is this silence.

    Scope, stated rather than implied: this reproduces the loosened writer's OUTPUT, it does not
    re-run a patched `_run_gate_in`. The guard itself is pinned one test file section up, by
    `test_a_red_suite_does_not_stamp_the_tested_hash`; this test supplies the CONSEQUENCE that
    test cannot see, because the consequence lives in another module."""
    monkeypatch.setattr(prc, "publish_gate_pytest_argv",
                        lambda test_root="tests/": [sys.executable, "-c", "raise SystemExit(1)"])
    head = _sha(sandbox)
    passed, _ = prc.run_fast_tests(head)
    assert passed is False

    prc.LAST_TESTED_HASH_FILE.write_text(head)

    assert wedge(head) is None, (
        "this assertion FAILING is the good news: it would mean the draw survives a stamped "
        "hash, i.e. the cross-check reads something other than this file and the contract's "
        "warning no longer describes the code"
    )


def test_the_supervisor_cites_the_contract_instead_of_restating_it():
    """Criterion 5's other half: the READER must point at the one place, not keep its own copy.

    The supervisor had the write rule paraphrased in two of its own prose sites ("rewritten only
    on a PASS"). Nothing bound those paraphrases to `LAST_TESTED_HASH_CONTRACT`, so the rule
    could change in prc and leave two confident, stale restatements next to the code that depends
    on it -- "stated in one place" plus two copies is not one place.

    WHAT THIS DOES AND DOES NOT CATCH, stated so nobody reads more into a green than is there:
    it catches the citation being deleted, and the contract being renamed or removed out from
    under it (the name is resolved on the real module, not grepped as a string). It does NOT
    detect a paraphrase drifting from the contract's meaning -- prose cannot be diffed against
    prose. The semantic collapse is caught behaviourally instead, by the three composition tests
    above; this test only guarantees there is one findable place to change."""
    from background import supervisor

    assert hasattr(prc, "LAST_TESTED_HASH_CONTRACT"), (
        "the contract this citation points at no longer exists under that name"
    )
    source = Path(supervisor.__file__).read_text()
    assert "LAST_TESTED_HASH_CONTRACT" in source, (
        "the supervisor stopped citing the contract -- its two prose sites are back to being an "
        "independent restatement of a rule that lives in another module"
    )


# ── THE EXIT CRITERION MUST NOT REQUIRE A MECHANISM THE CODE SHIPS DISABLED ──
#
# OBSERVED, and it is why this atom has been drawn nine times without its level moving. The R3
# elimination of 2026-08-11 (444402ee0) moved everything it was asked to move EXCEPT the one
# sentence that decides whether the atom is done. `REUSE_HEAD_CHECKOUT` went False; the
# instrument was rewritten around it (`tools/measure_publish_gate_subject_cost.py`'s header
# states the criterion is SUPERSEDED and it no longer emits `meets_exit_criterion`); the design
# doc was updated; this module grew a `reuse_enabled` fixture for the dormant half. And
# `maturity_map.yaml` -- the text the drawer reads and the level move is certified against --
# still opened with *"EXIT: (1) a REUSED checkout so __pycache__ survives between cycles, and
# the clean-subject gate runs within 1.3x the in-tree baseline"*.
#
# So every draw handed the next worker a first criterion whose mechanism ships switched off and
# whose bound was derived under warm bytecode that no longer exists at any price. The two
# available readings were both wrong: rebuild the eliminated thing, or hold forever. That is not
# a bookkeeping lag -- an exit criterion is the only thing standing between an atom and a level,
# and this one had no subject.
#
# THE CLASS, which this project has filed from the other side twice: an elimination must move
# the controls that pin it, and retiring a configuration must not starve the control that reads
# its evidence. Both of those were done here. What neither covers is the criterion that CONSUMES
# the verdict, one level up from any instrument -- so the elimination is now pinned to the
# criterion itself, and the pin is a biconditional rather than a one-way assertion: a map that
# declared the criterion superseded while the code shipped the mechanism would be the same
# disagreement in the other direction, and would let a re-enablement land unread.
#
# NOT KEYED TO THE SENTENCE. The predicate is two derived booleans over the live map text, and
# the mutation below feeds it the REAL pre-elimination wording rather than a fixture invented to
# fail -- the string is quoted from 88f851846, so the control is tried against the state it
# exists to catch and not against a convenient stand-in.

def _ops2_exit_text() -> str:
    """This atom's exit criterion, as the drawer and the level move actually read it.

    THROUGH THE SEAM, not off the map dict (2026-08-14, and it wedged publishing for four
    cycles). The `name` field drained out of `maturity_map.yaml` into the per-atom record
    store that same morning (`ab0a6a396`, `notes_rehomed: [build_note, name]`); the drain
    converted every PRODUCTION reader to `simplifications_store.atom_name` and missed this
    one, so the vacuity guard below -- correctly -- refused to grade an empty criterion and
    took the blocking gate red with it. Reading inline here would also make the control
    LIE in the other direction once the store is the only copy: `""` names no mechanism, so
    `_criterion_agrees_with_configuration` would return the pass branch if the guard were
    ever softened. One seam, so a future rehome moves one line."""
    import yaml

    sys.path.insert(0, str(REPO))
    from tools import maturity_map_store as map_store
    from tools import simplifications_store as _store

    # BOTH HALVES. This walks the map for ONE atom by id, and that atom reaching its target is
    # the success path -- at which point its record moves to the closed file and a drawn-half
    # read finds nothing, which this test would report as "the simplification is absent".
    raw = map_store.load_atoms(REPO / "docs" / "design" / "maturity_map.yaml")
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("id") == "OPS2_publish_gate_head_worktree":
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(raw)
    # VACUITY, and it is answerable by something that cannot legitimately go empty: this atom is
    # in the map for as long as it is drawable, and a rename that loses it must fail here rather
    # than pass an empty check.
    assert len(found) == 1, (
        "expected exactly one OPS2_publish_gate_head_worktree in the map, found {} -- this "
        "control cannot grade a criterion it cannot find".format(len(found))
    )
    text = _store.atom_name(found[0])
    assert "EXIT:" in text, (
        "OPS2 carries no exit criterion to grade, inline or in the record store -- the "
        "criterion a level move is certified against has gone missing, which is a louder "
        "defect than any disagreement this control was built to catch"
    )
    return text


def _criterion_agrees_with_configuration(exit_text: str, reuse_is_shipped: bool):
    """(ok, why) -- does the written criterion match the checkout mechanism that ships?

    Deliberately two coarse booleans over the text, not a match on the sentence: the defect is a
    criterion REQUIRING an eliminated mechanism, and any wording that does so has to name it."""
    import re

    demands_reuse = re.search(r"\bREUSED?\b[^.]{0,120}checkout", exit_text) is not None
    marks_superseded = ("SUPERSEDED" in exit_text
                        and "REUSE_HEAD_CHECKOUT ships False" in exit_text)
    if reuse_is_shipped:
        if marks_superseded:
            return False, ("the map declares criterion 1 SUPERSEDED by the reuse elimination "
                           "while REUSE_HEAD_CHECKOUT ships True -- the switch went back on and "
                           "the criterion nobody re-read now understates what the atom owes")
        return True, "reuse ships and the criterion may name it"
    if demands_reuse and not marks_superseded:
        return False, ("the exit criterion requires a REUSED checkout, and REUSE_HEAD_CHECKOUT "
                       "ships False (R3 elimination, 444402ee0) -- the criterion's mechanism "
                       "cannot be built at any price, so the atom can only be rebuilt-in-vain "
                       "or held forever")
    return True, "the criterion does not require the eliminated mechanism"


def test_the_exit_criterion_agrees_with_the_checkout_mechanism_that_ships():
    """Live record, graded against the live switch -- so it can red mid-tick with no source change.

    That is wanted, and it is the same shape as this atom's basis control: the map IS the
    evidence a level move is certified against, so a criterion drifting out from under the code
    must surface as a red here rather than as nine quiet redraws."""
    ok, why = _criterion_agrees_with_configuration(_ops2_exit_text(), prc.REUSE_HEAD_CHECKOUT)
    assert ok, why


def test_mutation_the_pre_elimination_criterion_text_reds():
    """MUTATION (R15), fed the REAL superseded wording -- quoted from 88f851846, not invented.

    Both directions, because the pin is a biconditional: the shipped-False box must refuse the
    old text, and the shipped-True box must refuse the new one."""
    old = ("... EXIT: (1) a REUSED checkout so __pycache__ survives between cycles, and the "
           "clean-subject gate runs within 1.3x the in-tree baseline (measured both sides, not "
           "asserted); (2) GATE_SUITE_TIMEOUT_SECONDS re-derived ...")
    ok, why = _criterion_agrees_with_configuration(old, reuse_is_shipped=False)
    assert not ok, "the pre-elimination criterion passed against a box that cannot build it"
    assert "cannot be built at any price" in why

    ok, _ = _criterion_agrees_with_configuration(old, reuse_is_shipped=True)
    assert ok, "the old criterion was correct while the mechanism shipped, and must stay so"

    live = _ops2_exit_text()
    ok, why = _criterion_agrees_with_configuration(live, reuse_is_shipped=True)
    assert not ok, ("a re-enabled REUSE_HEAD_CHECKOUT must red against the superseded criterion "
                    "-- otherwise flipping the switch back is invisible to the atom's own exit")
    assert "went back on" in why
