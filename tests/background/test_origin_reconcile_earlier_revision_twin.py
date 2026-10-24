"""A shared-tree copy equal to an EARLIER origin revision of its path held the fast-forward (H49).

THE DEFECT, measured on the shared tree 2026-10-01. Three of twelve paths holding the fast-forward
were staging docs `supervisor._sync_origin_staging` had copied in from origin and never refreshed;
origin revised each afterwards. Their bytes equalled `627f05756`, `8d6123c6a` and `8cbda4280` --
commits ON origin/main -- and the twin sweeps asked only origin's TIP, so the tree sat behind until
a hand cleared them. For a TRACKED non-Python copy no class could take it at all: the stale
judgement reads Python, and the file is no producer's output.

Real git, in a throwaway origin and clone, because the subject IS git's answer about history: a
faked `_origin_revisions` would prove the fake. The two classes that have no reader for `.md` are
injected as refusing, and the orphan class too, so the only class that can clear anything here is
the one under test -- otherwise an untracked case would pass on the orphan class's act.

WHAT EACH CONTROL WOULD CATCH:

  * `test_a_tracked_copy_of_an_earlier_revision_is_cleared_and_the_tree_advances` -- the repair on
    the shape no other class reaches. MUTATION: drop `set(earlier)` from the `resolvable` union ->
    held, `advanced` False. MUTATION: ask only the tip (`revisions[here] == tip`) -> same red.
  * `test_an_untracked_copy_of_an_earlier_revision_is_cleared_and_the_tree_advances` -- the
    supervisor-sync shape itself, cleared by `unlink` and preserved on its own prefix.
  * `test_novel_bytes_are_never_cleared` -- the safety property. MUTATION: match every path in
    `earlier_revision_twins` -> the novel file is overwritten and this reds.
  * `test_bytes_that_change_after_the_verdict_are_not_cleared` -- the in-lock re-proof. MUTATION:
    skip the `git show` comparison in `preserve_earlier_revision_twins` -> the novel bytes a lane
    wrote after the verdict are destroyed and this reds.
  * `test_a_staged_rename_to_done_holding_heads_blob_is_unstaged_and_the_tree_advances` -- the
    2026-10-24 wedge: a worker's uncommitted `git mv` to done/. MUTATION: drop `--force` from the
    staged-add `git rm --cached` -> held. MUTATION: drop the HEAD-tree leg of
    `_staged_blob_refusal` -> held, because the rename's blob is HEAD's at the SOURCE path only.
  * `test_a_staged_blob_no_history_holds_is_never_dropped` -- the other side of the partition.
    MUTATION: `_staged_blob_refusal` returns None always -> the novel staged blob is dropped.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc

_DOC = "docs/staging/SEAT_FINDING_A_DOC_ORIGIN_REVISED_AFTER_THE_SYNC_COPIED_IT.md"
_V1, _V2, _V3 = b"# finding\nResult: pending\n", b"# finding\nResult: 3 of 12\n", \
    b"# finding\nResult: 3 of 12\n\nDONE, landed.\n"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout.strip()


def _commit(seed: Path, content: bytes | None, msg: str) -> str:
    target = seed / _DOC
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        (seed / "README").write_text(msg)
        _git(seed, "add", "README")
    else:
        target.write_bytes(content)
        _git(seed, "add", _DOC)
    _git(seed, "commit", "-q", "-m", msg)
    _git(seed, "push", "-q", "origin", "HEAD:main")
    return _git(seed, "rev-parse", "HEAD")


@pytest.fixture
def world(tmp_path, monkeypatch):
    """`(seed, clone_at)`: a seed pushing to a bare origin, and a factory for the shared tree."""
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    _git(seed, "checkout", "-q", "-b", "main")

    def clone_at(name: str) -> Path:
        shared = tmp_path / name
        _git(tmp_path, "clone", "-q", "-b", "main", str(origin), str(shared))
        return shared

    return seed, clone_at


def _advance(shared: Path, **overrides) -> dict:
    refuse = lambda _project, paths: {p: (False, "fixture: no reader") for p in paths}  # noqa: E731
    kwargs = dict(stale_fn=refuse, generated_fn=refuse, orphans_fn=refuse,
                  locker=contextlib.nullcontext)
    kwargs.update(overrides)
    _git(shared, "fetch", "-q", "origin")
    return orc.advance_shared_tree(shared, **kwargs)


def _earlier_refs(shared: Path) -> str:
    return _git(shared, "for-each-ref", "--format=%(refname)", orc.EARLIER_PRESERVED_PREFIX)


def test_a_tracked_copy_of_an_earlier_revision_is_cleared_and_the_tree_advances(world):
    seed, clone_at = world
    _commit(seed, None, "c0")
    _commit(seed, _V1, "v1")
    shared = clone_at("shared")                      # HEAD holds v1
    v2 = _commit(seed, _V2, "v2")
    _commit(seed, _V3, "v3")
    (shared / _DOC).write_bytes(_V2)                 # modified; equals v2, neither HEAD nor tip

    assert orc.earlier_revision_twins(shared, [{"path": _DOC, "kind": orc.FF_MODIFIED}]) == {}, \
        "before the fetch the clone's origin/main does not hold v2, so nothing may match yet"
    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert (shared / _DOC).read_bytes() == _V3, "the fast-forward must leave origin's tip on disk"
    assert _earlier_refs(shared), "the bytes must have gone to the earlier-revision ref first"
    assert v2[:9] in _git(shared, "log", "-1", "--format=%B",
                          _earlier_refs(shared).splitlines()[0]), \
        "the preservation must name the origin commit that holds these bytes -- that commit is " \
        "the recovery route"


def test_an_untracked_copy_of_an_earlier_revision_is_cleared_and_the_tree_advances(world):
    seed, clone_at = world
    _commit(seed, None, "c0")
    shared = clone_at("shared")                      # HEAD has no copy of the doc
    _commit(seed, _V1, "v1")
    _commit(seed, _V2, "v2")
    (shared / _DOC).parent.mkdir(parents=True, exist_ok=True)
    (shared / _DOC).write_bytes(_V1)                 # the sync's stale copy, untracked

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert (shared / _DOC).read_bytes() == _V2
    assert orc.EARLIER_PRESERVED_PREFIX in out["reason"]


def test_novel_bytes_are_never_cleared(world):
    seed, clone_at = world
    _commit(seed, None, "c0")
    _commit(seed, _V1, "v1")
    shared = clone_at("shared")
    _commit(seed, _V2, "v2")
    _commit(seed, _V3, "v3")
    novel = b"# finding\na lane's work origin has never seen\n"
    (shared / _DOC).write_bytes(novel)

    out = _advance(shared)

    assert out["advanced"] is False, "novel bytes are holder work and must hold the tree"
    assert (shared / _DOC).read_bytes() == novel, "and they must still be on disk, untouched"
    assert _DOC in out["reason"], "the refusal must name the path it is holding on"
    assert not _earlier_refs(shared)


def test_bytes_that_change_after_the_verdict_are_not_cleared(world):
    """The verdict is read outside the lock; a lane can write between it and the clearing."""
    seed, clone_at = world
    _commit(seed, None, "c0")
    _commit(seed, _V1, "v1")
    shared = clone_at("shared")
    v2 = _commit(seed, _V2, "v2")
    _commit(seed, _V3, "v3")
    novel = b"written after the verdict\n"
    (shared / _DOC).write_bytes(novel)

    # The verdict as it read a moment earlier, when the bytes were still v2's.
    out = _advance(shared, earlier_fn=lambda _project, _blocking: {_DOC: v2})

    assert out["advanced"] is False, out["reason"]
    assert (shared / _DOC).read_bytes() == novel, \
        "bytes that are on no origin revision were destroyed on a proof made about other bytes"
    assert "changed after it was judged" in out["reason"]


_SRC = "docs/staging/advisor/DIRECTOR_READING_A_FILE_THE_DRAW_MOVED_TO_DONE.md"
_DONE = "docs/staging/advisor/done/DIRECTOR_READING_A_FILE_THE_DRAW_MOVED_TO_DONE.md"


def _commit_paths(seed: Path, writes: dict[str, bytes], removes: tuple[str, ...], msg: str) -> str:
    for path, content in writes.items():
        (seed / path).parent.mkdir(parents=True, exist_ok=True)
        (seed / path).write_bytes(content)
        _git(seed, "add", path)
    for path in removes:
        _git(seed, "rm", "-q", path)
    _git(seed, "commit", "-q", "-m", msg)
    _git(seed, "push", "-q", "origin", "HEAD:main")
    return _git(seed, "rev-parse", "HEAD")


def _staged_rename_world(world, disk: bytes):
    """The 2026-10-24 shape: a worker's uncommitted `git mv` to done/, and origin's copy on disk.

    HEAD holds the file at its source path. Origin moved it to done/ in the commit that appended
    its Done section, so v1 is never on origin at done/, and then revised it again. The
    shared tree's index holds HEAD's blob at the done/ path (the staged rename) while the disk
    holds `disk`. `git rm --cached` refuses that entry: its blob is neither the file's nor HEAD's.
    """
    seed, clone_at = world
    _commit_paths(seed, {_SRC: _V1}, (), "v1 at the source path")
    shared = clone_at("shared")
    _commit_paths(seed, {_DONE: _V2}, (_SRC,), "origin's own move to done/, with its Done section")
    _commit_paths(seed, {_DONE: _V3}, (), "v3")
    (shared / _DONE).parent.mkdir(parents=True, exist_ok=True)
    _git(shared, "mv", _SRC, _DONE)                  # the worker's staged, uncommitted rename
    (shared / _DONE).write_bytes(disk)
    return shared


def test_a_staged_rename_to_done_holding_heads_blob_is_unstaged_and_the_tree_advances(world):
    shared = _staged_rename_world(world, _V2)        # disk = an earlier origin revision

    out = _advance(shared)

    assert out["advanced"] is True, out["reason"]
    assert (shared / _DONE).read_bytes() == _V3
    assert not (shared / _SRC).exists()


def test_a_staged_blob_no_history_holds_is_never_dropped(world):
    """The control over the partition: the same shape with novel STAGED bytes must still hold."""
    shared = _staged_rename_world(world, _V2)
    novel = b"# finding\nstaged by a lane, on no branch\n"
    (shared / _DONE).write_bytes(novel)
    _git(shared, "add", _DONE)                        # index now holds the novel blob
    (shared / _DONE).write_bytes(_V2)                 # and the disk is an earlier origin revision
    staged = _git(shared, "ls-files", "-s", "--", _DONE).split()[1]

    out = _advance(shared)

    assert out["advanced"] is False, "a staged blob no history holds is a lane's work"
    assert _git(shared, "ls-files", "-s", "--", _DONE).split()[1] == staged, \
        "and its index entry must still be there, untouched"
