"""The hand-off store must be the one a tick READS, not the one this file happens to sit beside.

THE DEFECT (2026-09-04). `seat_continuation.STORE` was `PROJECT_DIR / "docs" / "observability" /
".seat_continuation.json"`, and `PROJECT_DIR` is derived from the module file's own location. Run
from an isolated worktree — which is how every headless executor turn runs — that resolved to the
**worktree's** copy. The store is untracked, so no commit carries it either. `--hand-off` therefore
reported success, wrote valid JSON, and the file died with the worktree while
`delivery_lane.next_item` went on reading the shared tree's store.

MEASURED, not inferred: the shared tree held `.seat_continuation.json` at 14 KB, written that same
day; the executor worktree had **no such file at all**.

WHY IT IS WORSE THAN AN ORDINARY BUG. This module exists to stop the seat's judgement dying at the
turn boundary — the director's own words, that the contradiction *"resolves onto me pressing
enter"*, are quoted in its docstring. The turns that most need continuity are the isolated ones,
and they were the only ones structurally unable to get it. The failure is silent in the worst way:
no error, valid output, and the next piece of work simply never arrives. **This entry exists only
because somebody checked.**

WHY THESE TESTS ARE A NEW MODULE. `tests/background/test_seat_continuation.py` covers what the
store CONTAINS, and every test in it does `monkeypatch.setattr(seat_continuation, "STORE", ...)` —
so by construction not one of them can observe where `STORE` points. That is the whole subject
here, and it cannot be a variant of a fixture that patches it away.
"""
from __future__ import annotations

from pathlib import Path

from background import seat_continuation as sc


def _fake_main_tree(root: Path) -> Path:
    """A tree that looks like this project to the resolver: a real `.git` DIRECTORY and the
    observability directory the store lives in."""
    main = root / "synthetic-enterprise"
    (main / ".git" / "worktrees").mkdir(parents=True)
    (main / "docs" / "observability").mkdir(parents=True)
    return main


def _fake_worktree(root: Path, main: Path, name: str = "se-seat-executor") -> Path:
    """A linked worktree: `.git` is a FILE pointing at the main gitdir. This is the exact shape
    `git worktree add` produces, and the shape the live executor runs in."""
    wt = root / name
    wt.mkdir()
    (wt / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / name}\n")
    return wt


# ── THE DEFECT ──────────────────────────────────────────────────────────────────────────────
def test_a_worktree_resolves_to_the_shared_tree(tmp_path):
    """THE LIVE DEFECT, in one assertion.

    MUTATION: restore `STORE = PROJECT_DIR / ...` and this fails.
    """
    main = _fake_main_tree(tmp_path)
    wt = _fake_worktree(tmp_path, main)

    resolved = sc.shared_tree_dir(wt)

    assert resolved == main, (
        f"a hand-off written from {wt} would go to its own tree-local store -- no tick reads it")
    assert resolved != wt


def test_a_normal_checkout_still_resolves_to_itself(tmp_path):
    """REACHABILITY / null control -- assert the unchanged path is still taken.

    Without this, `return <anything else>` satisfies the test above while sending every ordinary
    seat's hand-off somewhere new and wrong. The shared tree is the common case and it must be
    provably untouched.
    """
    main = _fake_main_tree(tmp_path)
    assert sc.shared_tree_dir(main) == main


# ── FAIL-CLOSED: every uncertainty returns TODAY'S behaviour ────────────────────────────────
def test_an_unparseable_git_pointer_falls_back_to_the_given_tree(tmp_path):
    wt = tmp_path / "odd"
    wt.mkdir()
    (wt / ".git").write_text("this is not a gitdir pointer")
    assert sc.shared_tree_dir(wt) == wt


def test_a_pointer_that_names_no_git_directory_falls_back(tmp_path):
    wt = tmp_path / "odd2"
    wt.mkdir()
    (wt / ".git").write_text(f"gitdir: {tmp_path / 'nowhere' / 'worktrees' / 'x'}\n")
    assert sc.shared_tree_dir(wt) == wt


def test_a_resolved_tree_that_is_not_this_project_falls_back(tmp_path):
    """The resolver must not write a hand-off into some unrelated repository because a pointer
    happened to parse. `docs/observability` is what makes it THIS project."""
    stranger = tmp_path / "someone-elses-repo"
    (stranger / ".git" / "worktrees").mkdir(parents=True)     # no docs/observability
    wt = _fake_worktree(tmp_path, stranger, name="wt2")
    assert sc.shared_tree_dir(wt) == wt


def test_a_missing_git_entry_falls_back(tmp_path):
    bare = tmp_path / "no-git"
    bare.mkdir()
    assert sc.shared_tree_dir(bare) == bare


# ── THE LIVE SURFACE ────────────────────────────────────────────────────────────────────────
def test_the_live_store_sits_under_the_resolved_shared_tree():
    """The module constant must be built from the resolver, not beside it. Asserted as a PROPERTY
    so it holds in a worktree and in a normal checkout alike -- and so it cannot pass by matching
    whichever tree this suite happens to be running in today."""
    assert sc.STORE == sc.shared_tree_dir() / "docs" / "observability" / ".seat_continuation.json"


def test_running_from_a_worktree_does_not_write_a_worktree_local_store():
    """Fires exactly where the defect lives. In a normal checkout the premise is absent and the
    control says so rather than passing vacuously."""
    if not (sc.PROJECT_DIR / ".git").is_file():
        assert sc.shared_tree_dir() == sc.PROJECT_DIR, (
            "not a linked worktree, so the resolver must be a no-op here")
        return
    assert sc.PROJECT_DIR not in sc.STORE.parents, (
        f"this suite is running from the linked worktree {sc.PROJECT_DIR} and the hand-off store "
        f"is still inside it ({sc.STORE}) -- a store no tick reads")
