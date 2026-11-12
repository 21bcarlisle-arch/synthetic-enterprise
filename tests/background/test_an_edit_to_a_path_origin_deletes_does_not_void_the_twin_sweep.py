"""One edited path that origin DELETES voided the whole tracked-twin sweep, and with it 1,314 twins.

MEASURED ON THE SHARED TREE 2026-11-12, 56 commits behind origin. 1,472 paths held the
fast-forward; 1,314 of the 1,452 tracked ones hashed EQUAL to origin's blob. Yet
`identical_tracked_twins` returned `None` ("git would not answer"), so `advance_shared_tree`
cleared nothing and every daemon kept running code 4 to 16 commits old.

Two paths caused it: `docs/state/billing_ledger.json` (origin deleted it in e816040ce8) and a
staging finding origin retired (63ede2e3bb). Both were edited here. HEAD held them and origin's tree
had no entry, so the disk hash answered and the origin hash did not, and `here is None or theirs is
None` read that as an unanswered question. It IS answered: origin deletes the path and this tree
edited it, which is a lane's work and not a twin, exactly like the sibling shape (a lane's deletion
of a path origin keeps).

CONTROLS, each naming what it catches:
  * the voiding leg -- the twin beside an origin-deleted edit is still found. Red at origin/main.
  * the safety leg -- the origin-deleted edit is NOT a twin, and nor is a path whose bytes differ.
  * the fail-closed leg -- when git cannot list origin's tree, the answer is still `None`.

MUTATIONS: make the new branch `return None` and the voiding leg reds. Make it `twins.append(path)`
and the safety leg reds. Make `_origin_has_entry` answer False when git fails and the fail-closed
leg reds.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True,
                          timeout=60)


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """HEAD holds three files; origin edits `twin.txt` and `differs.txt` and deletes `gone.txt`.
    The disk then holds origin's `twin.txt`, its own `differs.txt`, and an edit to `gone.txt`."""
    work = tmp_path / "repo"
    work.mkdir()
    _git(work, "init", "--quiet", "-b", "main")
    _git(work, "config", "user.email", "t@example.invalid")
    _git(work, "config", "user.name", "t")
    for name in ("twin.txt", "differs.txt", "gone.txt"):
        (work / name).write_text("head {}\n".format(name), encoding="utf-8")
    _git(work, "add", ".")
    _git(work, "commit", "--quiet", "-m", "base")
    (work / "twin.txt").write_text("origin twin\n", encoding="utf-8")
    (work / "differs.txt").write_text("origin differs\n", encoding="utf-8")
    _git(work, "rm", "--quiet", "gone.txt")
    _git(work, "add", ".")
    _git(work, "commit", "--quiet", "-m", "origin moves on")
    _git(work, "update-ref", "refs/remotes/origin/main", "HEAD")
    _git(work, "reset", "--quiet", "--hard", "HEAD~1")
    (work / "twin.txt").write_text("origin twin\n", encoding="utf-8")
    (work / "differs.txt").write_text("a lane's own edit\n", encoding="utf-8")
    (work / "gone.txt").write_text("a lane edited what origin deleted\n", encoding="utf-8")
    return work


BLOCKING = [_modified("twin.txt"), _modified("differs.txt"), _modified("gone.txt")]


def test_an_edit_origin_deletes_does_not_void_the_twin_beside_it(repo: Path):
    twins = orc.identical_tracked_twins(repo, BLOCKING)
    assert twins is not None, \
        "an edit to a path origin deletes is an ANSWERED question (origin's tree has no entry " \
        "there), and reading it as 'git would not answer' voids every twin beside it -- 1,314 " \
        "of them on 2026-11-12"
    assert twins == ["twin.txt"], \
        "only the path whose disk bytes equal origin's blob is a twin; got {}".format(twins)


def test_neither_the_origin_deleted_edit_nor_a_differing_copy_is_a_twin(repo: Path):
    twins = orc.identical_tracked_twins(repo, BLOCKING) or []
    assert "gone.txt" not in twins, \
        "restoring gone.txt to HEAD and fast-forwarding deletes the lane's edit, which origin " \
        "has never seen -- that is the judgement this sweep must never automate"
    assert "differs.txt" not in twins, \
        "differs.txt holds bytes origin does not have (the live example is " \
        "background/live_payment_triad.py) and must keep refusing"
    # Reachability over the partition: one call yields a twin AND two refusals.
    assert twins and len(twins) < len(BLOCKING)


def test_a_git_that_cannot_list_origins_tree_still_fails_closed(repo: Path, monkeypatch):
    real = orc._git

    def broken(cwd, *args, **kw):
        if args and args[0] == "ls-tree":
            return subprocess.CompletedProcess(args=["git", *args], returncode=128, stdout="",
                                               stderr="fatal: simulated")
        return real(cwd, *args, **kw)

    monkeypatch.setattr(orc, "_git", broken)
    assert orc.identical_tracked_twins(repo, BLOCKING) is None, \
        "whether origin deletes gone.txt was NOT answered, so the sweep must not report a list " \
        "a caller would clear paths on"
