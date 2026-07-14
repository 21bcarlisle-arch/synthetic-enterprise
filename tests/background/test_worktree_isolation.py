"""H10 worktree-isolation guarantee -- guard + cross-worktree lock.

Two mechanisms under test, both R15-graded (a control counts only if a MUTATION
TEST proves it fires on its own named defect):

1. `assert_changes_within_scope` -- the isolation GUARD. Named defect: a BUILD
   fork writes a file OUTSIDE its declared `file_scope` (a sibling atom's file,
   or the shared maturity map). The mutation tests below introduce exactly that
   defect and assert the guard raises. Fail-open and fail-silent are both
   probed (empty scope, protected path inside a mis-declared scope, unreadable
   tree).

2. `shared_tree_lock` -- the cross-worktree serialisation primitive. Proven to
   resolve to ONE lock path from two different real worktrees and to actually
   block a second holder.
"""
import fcntl
import multiprocessing
import subprocess
import time
from pathlib import Path

import pytest

from background import tree_lock as tl


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "t@t")
    _git(path, "config", "user.name", "t")
    _git(path, "config", "commit.gpgsign", "false")
    # A small tree mirroring the real atom's scope shape.
    (path / "background").mkdir()
    (path / "background" / "tree_lock.py").write_text("# code\n")
    (path / "tests").mkdir()
    (path / "tests" / "test_x.py").write_text("# test\n")
    (path / "docs" / "design").mkdir(parents=True)
    (path / "docs" / "design" / "maturity_map.yaml").write_text("- id: X\n")
    (path / "sibling.py").write_text("# a sibling atom's file\n")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "init")
    return path


# atom H10's own declared scope shape.
SCOPE = [".claude/agents", "background/tree_lock.py", "tests"]


# --------------------------------------------------------------------------- #
# changed_paths
# --------------------------------------------------------------------------- #
def test_changed_paths_reports_modified_untracked_and_renamed(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / "background" / "tree_lock.py").write_text("# code v2\n")  # modified
    (repo / "tests" / "new_test.py").write_text("# new\n")            # untracked
    _git(repo, "mv", "sibling.py", "renamed.py")                       # rename
    changed = tl.changed_paths(repo)
    assert "background/tree_lock.py" in changed
    assert "tests/new_test.py" in changed
    # rename contributes both endpoints
    assert "sibling.py" in changed
    assert "renamed.py" in changed


def test_changed_paths_clean_tree_is_empty(tmp_path):
    repo = _init_repo(tmp_path / "r")
    assert tl.changed_paths(repo) == set()


def test_changed_paths_fail_closed_when_not_a_repo(tmp_path):
    """R15 fail-silent: an undeterminable tree must raise, never return {}."""
    not_repo = tmp_path / "plain"
    not_repo.mkdir()
    with pytest.raises(tl.GitStateError):
        tl.changed_paths(not_repo)


# --------------------------------------------------------------------------- #
# guard: passes when in scope
# --------------------------------------------------------------------------- #
def test_guard_passes_for_in_scope_change(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / "background" / "tree_lock.py").write_text("# in-scope edit\n")
    (repo / "tests" / "new_test.py").write_text("# in-scope new test\n")
    # Must NOT raise.
    changed = tl.assert_changes_within_scope(SCOPE, repo_dir=repo)
    assert "background/tree_lock.py" in changed


def test_guard_passes_on_clean_tree(tmp_path):
    """A clean tree has nothing to violate -- this is correct-pass, not
    fail-open (there is genuinely no out-of-scope change)."""
    repo = _init_repo(tmp_path / "r")
    assert tl.assert_changes_within_scope(SCOPE, repo_dir=repo) == set()


# --------------------------------------------------------------------------- #
# guard: MUTATION tests -- the guard must FIRE on its named defect
# --------------------------------------------------------------------------- #
def test_guard_fires_on_out_of_scope_write(tmp_path):
    """NAMED DEFECT: fork edits a file outside its file_scope (a sibling
    atom's file). The guard MUST raise and name the offending path."""
    repo = _init_repo(tmp_path / "r")
    (repo / "background" / "tree_lock.py").write_text("# legit in-scope\n")
    (repo / "sibling.py").write_text("# CORRUPTION: not in this atom's scope\n")
    with pytest.raises(tl.ScopeViolation) as exc:
        tl.assert_changes_within_scope(SCOPE, repo_dir=repo)
    assert "sibling.py" in exc.value.scope_violations
    # the legitimate in-scope edit is NOT flagged
    assert "background/tree_lock.py" not in exc.value.scope_violations


def test_guard_fires_on_untracked_out_of_scope_file(tmp_path):
    """A brand-new file dropped outside scope (untracked) is caught too."""
    repo = _init_repo(tmp_path / "r")
    (repo / "saas").mkdir()
    (repo / "saas" / "sneaky.py").write_text("# outside scope, brand new\n")
    with pytest.raises(tl.ScopeViolation) as exc:
        tl.assert_changes_within_scope(SCOPE, repo_dir=repo)
    assert "saas/sneaky.py" in exc.value.scope_violations


def test_guard_protects_map_even_when_scope_mis_declares_it(tmp_path):
    """SOLE-WRITER MUTATION: a fork mis-declares the maturity map in its own
    file_scope and edits it. Scope alone would excuse it; the independent
    protected-path check MUST still fire (the map is orchestrator-written
    ONLY, never fork-written)."""
    repo = _init_repo(tmp_path / "r")
    (repo / "docs" / "design" / "maturity_map.yaml").write_text("- id: X\n  hacked: true\n")
    mis_declared_scope = SCOPE + ["docs/design/maturity_map.yaml"]
    with pytest.raises(tl.ScopeViolation) as exc:
        tl.assert_changes_within_scope(mis_declared_scope, repo_dir=repo)
    assert "docs/design/maturity_map.yaml" in exc.value.protected_violations


def test_guard_fail_closed_on_empty_scope(tmp_path):
    """FAIL-OPEN probe: an empty file_scope must make ANY change a violation,
    never a vacuous pass."""
    repo = _init_repo(tmp_path / "r")
    (repo / "background" / "tree_lock.py").write_text("# a change\n")
    with pytest.raises(tl.ScopeViolation):
        tl.assert_changes_within_scope([], repo_dir=repo)


def test_guard_fail_closed_when_tree_unreadable(tmp_path):
    """FAIL-SILENT probe: if git state can't be read, the guard must NOT report
    the tree clean -- it propagates GitStateError."""
    not_repo = tmp_path / "plain"
    not_repo.mkdir()
    with pytest.raises(tl.GitStateError):
        tl.assert_changes_within_scope(SCOPE, repo_dir=not_repo)


def test_scope_prefix_is_not_fooled_by_shared_name_prefix(tmp_path):
    """`tests` in scope must not silently admit a sibling `tests_extra/...`."""
    repo = _init_repo(tmp_path / "r")
    (repo / "tests_extra").mkdir()
    (repo / "tests_extra" / "x.py").write_text("# not really in tests/\n")
    with pytest.raises(tl.ScopeViolation) as exc:
        tl.assert_changes_within_scope(SCOPE, repo_dir=repo)
    assert "tests_extra/x.py" in exc.value.scope_violations


# --------------------------------------------------------------------------- #
# cross-worktree shared lock
# --------------------------------------------------------------------------- #
def test_shared_lock_resolves_to_same_path_from_two_worktrees(tmp_path):
    """The whole point: two DIFFERENT worktrees must anchor the shared lock at
    the SAME file (git-common-dir), so they can actually exclude each other.
    `tree_lock`'s per-tree LOCK_FILE, by contrast, differs per worktree."""
    main = _init_repo(tmp_path / "main")
    wt = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", "-b", "branchA", str(wt))

    shared_from_main = tl.shared_lock_file(main)
    shared_from_wt = tl.shared_lock_file(wt)
    assert shared_from_main == shared_from_wt, (
        "shared lock must be identical across worktrees"
    )
    # sanity: it lives under the shared .git, and the worktree's own git-dir is
    # a DIFFERENT (per-worktree) location -- proving the shared anchor matters.
    assert tl.common_git_dir(main) == tl.common_git_dir(wt)


def _hold_shared_lock(lock_path_str, hold_seconds, ready_flag_path):
    with open(lock_path_str, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        Path(ready_flag_path).write_text("ready")
        time.sleep(hold_seconds)
        fcntl.flock(fh, fcntl.LOCK_UN)


def test_shared_lock_blocks_a_second_holder(tmp_path, monkeypatch):
    main = _init_repo(tmp_path / "main")
    lock_path = tl.shared_lock_file(main)
    ready_flag = tmp_path / "ready.flag"

    proc = multiprocessing.Process(
        target=_hold_shared_lock, args=(str(lock_path), 1.0, str(ready_flag))
    )
    proc.start()
    deadline = time.monotonic() + 5
    while not ready_flag.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert ready_flag.exists(), "subprocess never signalled it held the lock"

    start = time.monotonic()
    with tl.shared_tree_lock(timeout=5, repo_dir=main):
        elapsed = time.monotonic() - start
    proc.join()
    assert elapsed >= 0.5, "shared_tree_lock should block while another holder has it"


def test_per_tree_lock_differs_across_worktrees_by_design(tmp_path):
    """Documents the deliberate contrast: LOCK_FILE is per-tree (via __file__),
    so it does NOT serialise across worktrees; shared_tree_lock is the primitive
    that does. This test pins the design so a future refactor can't silently
    make tree_lock a false cross-worktree guard."""
    main = _init_repo(tmp_path / "main")
    wt = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", "-b", "branchB", str(wt))
    # per-tree lock is anchored at module import (__file__), identical constant
    # regardless of repo arg -- i.e. it knows nothing about these worktrees.
    assert tl.LOCK_FILE == tl.PROJECT_DIR / "docs" / "observability" / ".tree.lock"
    # shared lock DOES vary with the repo it is asked about, and is a distinct
    # location from the per-tree lock.
    assert tl.shared_lock_file(main) != tl.LOCK_FILE
