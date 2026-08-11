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
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from background import process_run_complete as prc  # noqa: E402


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

    IT HAS NOW FIRED FOR REAL (2026-08-11, launch 11). The shipped subject -- a cold throwaway
    checkout -- measured 1411.2s against the 1291.9s the 2600s bound had been derived from, and
    this test reddened on its own before anyone read the record. The bound moved to 2900s; that
    is the control working, and the note it left is that the old evidence had been timed in the
    since-deleted shared directory and was never the subject the gate ships."""
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


def _pytest_root(parent, n, age_s=None):
    d = parent / "pytest-{}".format(n)
    d.mkdir(parents=True)
    (d / "f").write_text("x")
    if age_s is not None:
        os.utime(d, (age_s, age_s))
    return d


def test_stale_pytest_temp_roots_are_swept_and_the_newest_are_kept(sandbox):
    """The fifteenth wedge. pytest prunes its own numbered roots, but a suite SIGKILLed mid-run
    (rc=-9, the known gate outcome) never gets to -- so they pile up exactly when the gate is
    already in trouble, and on a tmpfs those bytes are RAM.

    Both directions in one test: a sweep that took the newest roots could delete a RUNNING
    suite's tmp_path out from under it, which is worse than the leak it fixes."""
    parent = prc.HEAD_CHECKOUT_ROOT / "pytest-of-someone"
    ancient = time.time() - prc.STALE_HEAD_CHECKOUT_AGE_SECONDS - 60
    # Six roots, ALL old enough to be swept on age alone; mtimes ascend with the number.
    old = [_pytest_root(parent, n, ancient + n) for n in range(6)]
    fresh = _pytest_root(parent, 99)
    unrelated = prc.HEAD_CHECKOUT_ROOT / "someone-elses-tmpdir"
    unrelated.mkdir()
    os.utime(unrelated, (ancient, ancient))

    removed = prc._sweep_stale_pytest_temp_roots()

    kept = [p for p in old + [fresh] if p.exists()]
    assert removed == 4, "the four oldest go; the keep-window is not age-gated"
    assert [p.name for p in kept] == ["pytest-4", "pytest-5", "pytest-99"], kept
    assert fresh.exists(), "a root inside the keep-window may belong to a LIVE suite"
    assert unrelated.exists(), "this sweep owns pytest roots and nothing else"


def test_a_pytest_current_symlink_is_never_the_thing_deleted(sandbox):
    """`pytest-current` points INTO a numbered root. Deleting the link would leave the bytes on
    the tmpfs and lose the only handle to them -- a sweep that makes the leak unreachable."""
    parent = prc.HEAD_CHECKOUT_ROOT / "pytest-of-someone"
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
    parent = root / "pytest-of-rich"
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

    assert prc._sweep_stale_pytest_temp_roots() == len(pytest_roots) - prc.PYTEST_TEMP_KEEP_NEWEST
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
