"""An ABANDONED working copy no class could take held the shared tree behind origin for days.

THE DEFECT, measured over the ten days to 2026-10-04. The shared tree every daemon runs from was
out of step with origin/main for 157 of 231 hours; 50.5 of the attributable hours were
`advance_shared_tree` refusing because one working copy collided with an incoming commit and fitted
none of its six resolvable classes, and the rule is all-or-nothing. The commonest blockers were not
live work but abandoned lane edits: `tests/tools/test_the_concordance_curve_says_what_it_could_
have_seen.py`, last written 2026-09-24, refused 127 cadences; four staging notes and a test from
2026-10-02 about 100 each.

THE SEVENTH CLASS: a copy in none of the six that nobody has written for `ABANDONED_AFTER_HOURS` is
preserved on a ref, read back, cleared, and named in one staging item. Real git, in a throwaway bare
origin and clones, because the subject is git's answer and a faked one would prove the fake.

WHAT EACH CONTROL WOULD CATCH:

  * `test_the_partition_aged_out_live_and_twin_each_take_their_own_branch` -- the rare branch first,
    one control over the whole partition: a 49 h unique copy IS aged out and fast-forwarded past; a
    1 h one still refuses everything; a 49 h TWIN goes through the twin class, not this one.
    MUTATIONS, each applied and reverted 2026-10-04: threshold ignored (`age < ABANDONED_AFTER_HOURS`
    -> `age < 0`) reds this and the all-or-nothing leg; the aged-out set never clearing `held`
    reds this and three more; the in-lock preservation skipped (`= "", ""`) reds this and three
    more, the failed-preservation leg included, since nothing then refuses.
  * `test_one_live_copy_keeps_the_advance_all_or_nothing` -- a 49 h copy beside a 1 h one is NOT
    touched: the class never shortens the all-or-nothing rule for a lane that is still here.
  * `test_the_preserved_ref_holds_the_exact_bytes_and_the_item_names_path_and_ref` -- preservation.
    MUTATION (the preservation call in the lock skipped): no ref, and this reds.
  * `test_an_untracked_abandoned_copy_is_removed_after_preservation` -- the `unlink` act.
  * `test_a_failed_preservation_touches_nothing` -- fail-closed, by injection.
  * `test_the_same_ref_recurring_refreshes_one_item_in_place` -- one document, one section per ref.
"""
from __future__ import annotations

import contextlib
import os
import subprocess
import time
from pathlib import Path

import pytest

from background import origin_reconcile as orc

_WORK = "notes/a_lane_edit.md"
_BASE, _TIP = b"# notes\nbase\n", b"# notes\nbase\norigin's revision\n"
_NOVEL = b"# notes\nbase\na lane's edit that nobody landed\n"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout.strip()


def _commit(seed: Path, path: str, content: bytes, msg: str) -> None:
    target = seed / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    _git(seed, "add", path)
    _git(seed, "commit", "-q", "-m", msg)
    _git(seed, "push", "-q", "origin", "HEAD:main")


@pytest.fixture
def world(tmp_path, monkeypatch):
    """`(seed, clone_at)`: a seed pushing to a bare origin, and a factory for shared trees."""
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


def _age(path: Path, hours: float) -> None:
    then = time.time() - hours * 3600
    os.utime(path, (then, then))


def _advance(shared: Path, **overrides) -> dict:
    kwargs = dict(locker=contextlib.nullcontext)
    kwargs.update(overrides)
    _git(shared, "fetch", "-q", "origin")
    return orc.advance_shared_tree(shared, **kwargs)


def _abandoned_refs(shared: Path) -> list[str]:
    return _git(shared, "for-each-ref", "--format=%(refname)",
                orc.ABANDONED_PRESERVED_PREFIX).splitlines()


def _items(shared: Path) -> list[Path]:
    return sorted((shared / "docs" / "staging").glob(
        "WORKER_FINDING_REPEATING_ALARM_ORIGIN_RECONCILE_ABANDONED_*.md"))


def _three_trees(world) -> tuple[Path, Path, Path]:
    seed, clone_at = world
    _commit(seed, _WORK, _BASE, "base")
    aged, live, twin = clone_at("aged"), clone_at("live"), clone_at("twin")
    _commit(seed, _WORK, _TIP, "origin revises it")
    for tree, content, hours in ((aged, _NOVEL, 49), (live, _NOVEL, 1), (twin, _TIP, 49)):
        (tree / _WORK).write_bytes(content)
        _age(tree / _WORK, hours)
    return aged, live, twin


def test_the_partition_aged_out_live_and_twin_each_take_their_own_branch(world):
    aged, live, twin = _three_trees(world)

    out = {name: _advance(tree) for name, tree in (("aged", aged), ("live", live), ("twin", twin))}

    # THE WHOLE PARTITION IN ONE ASSERTION FIRST: a guard that refuses everything, or one that ages
    # out everything, cannot pass this line whatever the per-branch legs below say.
    assert (out["aged"]["advanced"], out["live"]["advanced"], out["twin"]["advanced"]) == \
        (True, False, True), {k: v["reason"] for k, v in out.items()}

    assert (aged / _WORK).read_bytes() == _TIP, "the fast-forward must leave origin's tip on disk"
    assert _abandoned_refs(aged), "the aged-out copy must have gone to the abandoned ref first"
    assert orc.ABANDONED_PRESERVED_PREFIX in out["aged"]["reason"]

    assert (live / _WORK).read_bytes() == _NOVEL, "a 1 h copy is LIVE work and must be untouched"
    assert not _abandoned_refs(live) and not _items(live)
    assert _WORK in out["live"]["reason"] and "LIVE work" in out["live"]["reason"], \
        out["live"]["reason"]

    assert not _abandoned_refs(twin), "a twin is cleared by the twin class, never preserved here"
    assert not _items(twin), "and no abandoned-copy staging item is filed for it"


def test_one_live_copy_keeps_the_advance_all_or_nothing(world):
    seed, clone_at = world
    other = "notes/a_second_lane_edit.md"
    _commit(seed, _WORK, _BASE, "base")
    _commit(seed, other, _BASE, "base 2")
    shared = clone_at("shared")
    _commit(seed, _WORK, _TIP, "revise 1")
    _commit(seed, other, _TIP, "revise 2")
    (shared / _WORK).write_bytes(_NOVEL)
    _age(shared / _WORK, 49)
    (shared / other).write_bytes(_NOVEL + b"and a line written an hour ago\n")
    _age(shared / other, 1)

    out = _advance(shared)

    assert out["advanced"] is False and out["cleared"] == [], out["reason"]
    assert (shared / _WORK).read_bytes() == _NOVEL, "the aged copy is not touched while one is live"
    assert not _abandoned_refs(shared)
    assert other in out["reason"]


def test_the_preserved_ref_holds_the_exact_bytes_and_the_item_names_path_and_ref(world):
    aged, _live, _twin = _three_trees(world)

    out = _advance(aged)

    assert out["advanced"] is True, out["reason"]
    refs = _abandoned_refs(aged)
    assert len(refs) == 1
    shown = subprocess.run(["git", "show", "{}:{}".format(refs[0], _WORK)], cwd=str(aged),
                           capture_output=True, check=True).stdout
    assert shown == _NOVEL, "the ref must hold the abandoned bytes exactly"

    items = _items(aged)
    assert len(items) == 1, items
    text = items[0].read_text(encoding="utf-8")
    assert _WORK in text and refs[0] in text
    assert "git show {}:{}".format(refs[0], _WORK) in text, "the item must carry the recovery command"
    assert "**Severity:**" in text.splitlines()[0]


def test_an_untracked_abandoned_copy_is_removed_after_preservation(world):
    """The orphan class normally takes an untracked path origin adds; refused here by injection so
    the untracked branch of THIS class (`unlink`, not a restore) is what is exercised."""
    seed, clone_at = world
    draft = "docs/staging/A_DRAFT_ORIGIN_ALSO_ADDS.md"
    _commit(seed, "README", b"r\n", "c0")
    shared = clone_at("shared")
    _commit(seed, draft, b"origin's copy\n", "origin adds it")
    (shared / draft).parent.mkdir(parents=True, exist_ok=True)
    (shared / draft).write_bytes(b"an abandoned untracked draft\n")
    _age(shared / draft, 72)

    out = _advance(shared, orphans_fn=lambda _p, paths: {
        p: (False, "fixture: refused") for p in paths})

    assert out["advanced"] is True, out["reason"]
    assert (shared / draft).read_bytes() == b"origin's copy\n"
    ref = _abandoned_refs(shared)[0]
    assert _git(shared, "show", "{}:{}".format(ref, draft)) == "an abandoned untracked draft"


def test_a_failed_preservation_touches_nothing(world):
    aged, _live, _twin = _three_trees(world)
    head = _git(aged, "rev-parse", "HEAD")

    out = _advance(aged, abandoned_preserver=lambda _paths: (None, "injected: the ref was refused"))

    assert out["advanced"] is False and out["cleared"] == [], out["reason"]
    assert "injected: the ref was refused" in out["reason"], "the refusal must say why"
    assert (aged / _WORK).read_bytes() == _NOVEL, "the abandoned bytes must still be on disk"
    assert _git(aged, "rev-parse", "HEAD") == head, "and the tree must not have moved"
    assert not _items(aged), "nothing was aged out, so nothing is named"


def test_the_same_ref_recurring_refreshes_one_item_in_place(tmp_path):
    shared = tmp_path / "shared"
    shared.mkdir()
    ref = orc.ABANDONED_PRESERVED_PREFIX + "origin-reconcile-abc1234"
    first = [{"path": "a.md", "age_hours": 50.0, "kind": "tracked edit"}]
    second = first + [{"path": "b.md", "age_hours": 60.0, "kind": "untracked file"}]

    assert orc.file_abandoned_copies(shared, first, ref, "1" * 40) == ""
    assert orc.file_abandoned_copies(shared, second, ref, "2" * 40) == ""
    other = orc.ABANDONED_PRESERVED_PREFIX + "origin-reconcile-def5678"
    assert orc.file_abandoned_copies(shared, first, other, "3" * 40) == ""

    items = _items(shared)
    assert len(items) == 1, "one staging item for the family, never one per cadence"
    text = items[0].read_text(encoding="utf-8")
    assert text.count("## Aged out at `{}`".format(ref)) == 1, "a recurring ref is refreshed"
    assert "`b.md`" in text and "2222222222" in text, "with the newer contents"
    assert "1111111111" not in text
    assert text.count("## Aged out at `{}`".format(other)) == 1
