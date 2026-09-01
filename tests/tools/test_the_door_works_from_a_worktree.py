"""The only legal commit door must work from a `git worktree`, or isolation and legality exclude.

`tools/surgical_land` is the sanctioned door — hook-bypass is a wall and no sanctioned bypass shape
exists. The shared working tree is a known collision surface and `git worktree` is the standard
remedy. **Until 2026-08-31 those two facts were mutually exclusive**: the door assumed
`root/.git/objects`, a linked worktree's `.git` is a FILE, and every land from a worktree died with

    error: unable to normalize alternate object path: <worktree>/.git/objects
    fatal: failed to unpack tree object <sha>

so any writer that isolated itself had no way to commit at all. That is why the delivery seat could
not be given its own tree, and it is the reason recorded in
`docs/design/CAN_THE_SEAT_SELF_ADVANCE_2026-08-31.md`.

WHY THIS TESTS `_object_store` AND NOT A WHOLE LANDING. A real land runs the repo's own pre-commit
gate — nine gates, a test selection and the site lane, more than ten minutes. A control that slow is
one nobody runs. The unit that was wrong is the object-store resolution, and the property that was
broken is expressible exactly: **a worktree and its main repo must resolve to the SAME store.** The
end-to-end land was done once, by hand, and is recorded in the commit that fixed this; what is held
here is the thing that can silently regress.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.surgical_land import _object_store

PROJECT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def worktree(tmp_path_factory):
    """A real linked worktree. Created and removed; nothing is committed in it."""
    path = tmp_path_factory.mktemp("door") / "wt"
    subprocess.run(
        ["git", "worktree", "add", "--detach", "-q", str(path), "HEAD"],
        cwd=PROJECT, check=True, capture_output=True,
    )
    try:
        yield path
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(path)],
                       cwd=PROJECT, capture_output=True)
        subprocess.run(["git", "worktree", "prune"], cwd=PROJECT, capture_output=True)


def test_a_worktrees_dot_git_is_a_FILE__which_is_the_whole_cause(worktree):
    """The fixture must actually reproduce the condition, or every leg below proves nothing.

    MUTATION: point the fixture at a plain clone instead of a worktree and this fires.
    """
    assert (worktree / ".git").is_file(), (
        "the fixture did not produce a LINKED worktree — its `.git` is not a file, so the "
        "condition this control exists for is not present and the legs below are vacuous"
    )
    assert not (worktree / ".git" / "objects").exists(), (
        "`<worktree>/.git/objects` exists, so the original bug could not reproduce here"
    )


def test_the_worktree_and_the_main_repo_resolve_to_the_SAME_object_store(worktree):
    """The property that was broken, stated as the identity it is.

    Objects live ONCE, in the shared store. A worktree's own gitdir (`.git/worktrees/<name>`) holds
    its HEAD and index and no objects at all, so lending that instead fails the same way one
    directory down — which is why `--git-common-dir` is the right question and `--git-dir` is not.

    MUTATION: restore `(root / ".git" / "objects").resolve()`, or swap `--git-common-dir` for
    `--git-dir`, and this fires.
    """
    assert _object_store(worktree) == _object_store(PROJECT), (
        f"a worktree resolves to {_object_store(worktree)} and the main repo to "
        f"{_object_store(PROJECT)}. The extracted gate repo borrows the parent commit's objects "
        "through an alternates line built from this path; if it is wrong the door cannot read the "
        "commit it is landing on top of, and refuses."
    )


def test_the_resolved_store_actually_EXISTS_and_holds_objects(worktree):
    """A path that resolves cleanly and points nowhere is the original failure exactly.

    MUTATION: return a plausible-but-absent path and this fires where an equality check alone
    would pass — both sides could be equally wrong.
    """
    layouts = ((worktree, "worktree"), (PROJECT, "main repo"))
    # THE EXACT SET, not a floor, because the population here is the two layouts a commit can be
    # made from and both are the point: the gap this closed was the worktree one, and a scan that
    # silently checked only the main repo would read exactly like a pass.
    assert len(layouts) == 2, "both layouts must be checked — one of them is the gap this closed"
    for where, label in layouts:
        store = _object_store(where)
        assert store.is_dir(), f"the {label}'s object store {store} is not a directory"
        assert any(store.iterdir()), f"the {label}'s object store {store} is empty"


def test_the_normal_repo_path_is_UNCHANGED_by_the_worktree_fix():
    """The fix must not move the answer for the layout every lane uses today.

    This is the blast-radius leg: `surgical_land` is the door every commit in this repository goes
    through, and a change to it that quietly altered the ordinary case would be far worse than the
    gap it closed.

    MUTATION: any change that makes the main-repo answer differ from `<root>/.git/objects` fires.
    """
    assert _object_store(PROJECT) == (PROJECT / ".git" / "objects").resolve(), (
        "the main-repo object store no longer resolves to `<root>/.git/objects` — the worktree fix "
        "has changed the path for the layout every lane commits from"
    )
