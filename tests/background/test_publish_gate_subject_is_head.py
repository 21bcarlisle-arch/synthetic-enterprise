"""The publish gate's SUBJECT is committed truth, and its checkout is reused safely.

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

HOW IT AVOIDS TESTING ITSELF INTO A CORNER. Every behavioural test runs against a REAL git repo
built in `tmp_path` with `prc.PROJECT_DIR` pointed at it, never against this repository: writing
a syntax error into a tracked file of the live shared tree -- the honest way to produce a dirty
tree -- would break every daemon that imports it for as long as the test ran. The mechanism under
test (`git archive` -> standalone repo -> `read-tree --reset` refresh) is exercised for real; only
the tree it operates on is a stand-in.
"""
import fcntl
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
def sandbox(tmp_path, monkeypatch, logged):
    """A real git repo standing in for the shared tree, with one committed source file.

    Returns the repo path. `prc.PROJECT_DIR` and `prc.HEAD_CHECKOUT_ROOT` are redirected here so
    the whole checkout lifecycle runs for real without touching the machine's tree or its live
    reused checkout."""
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
    refactor that quietly loses the `cwd=` keyword cannot pass this."""
    where = sandbox.parent / "where.txt"
    monkeypatch.setattr(
        prc, "publish_gate_pytest_argv",
        lambda test_root="tests/": [sys.executable, "-c",
                                    "import os, pathlib; pathlib.Path({!r}).write_text("
                                    "os.getcwd())".format(str(where))])

    prc.run_fast_tests(_sha(sandbox))

    ran_in = Path(where.read_text())
    assert ran_in != sandbox, "the gate ran in the shared tree"
    assert ran_in.resolve() == (prc.HEAD_CHECKOUT_ROOT / prc.REUSED_HEAD_CHECKOUT_NAME).resolve()


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


# ── THE REUSED CHECKOUT'S LIFECYCLE ──────────────────────────────────────────

def test_the_checkout_is_reused_and_keeps_its_bytecode(sandbox):
    """Exit criterion 1's MECHANISM. The runtime it buys is measured in the atom record, not
    asserted here -- a wall-clock assertion on a shared box is a flake, and R12 says a measured
    number is a diagnostic, not a target. What must hold every cycle is this: the same directory
    comes back, and `__pycache__` survives into it."""
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


def test_the_refresh_follows_head_when_it_moves(sandbox):
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


def test_a_second_publisher_never_shares_the_reused_checkout(sandbox, logged):
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


def test_a_corrupt_reused_checkout_is_rebuilt_rather_than_trusted(sandbox):
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
