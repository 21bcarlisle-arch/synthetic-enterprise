"""A REFUSED ADVANCE NAMED THE FORK AND NEVER ITS CAUSE, AND A READER FOUND THE PATHS BY HAND.

Delivery queue, 2026-09-04: *"a permanently dirty shared tree can never fast-forward, and
`origin_reconcile` correctly declines to force it while reporting a verdict that names no cause a
reader can act on."* The decline is right and is not what changes here. What changes is that
`NOT_ADVANCED` now says WHICH paths refused and which of the two KINDS each one is -- because the
two are cleared by different people, with different commands, and the old verdict sent every reader
to the same dead end.

The instance behind it, from the same orientation: the shared tree sat three commits behind on its
own lane's work, refused by exactly two paths -- `background/process_run_complete.py`, dirty in
index and worktree, and an untracked twin of a staging document that origin also adds. Nothing in
the verdict said so.

THE INTERSECTION IS PROVEN AGAINST REAL GIT, not against two hand-built sets. A test that composes
its own `incoming` and `dirty` lists and asserts they intersect is testing `set.intersection`, and
would have passed just as well against a function asking git the wrong question.
"""
from __future__ import annotations

import subprocess

import pytest

from background import origin_reconcile as orc


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture
def forked(tmp_path):
    """A real clone that is genuinely BEHIND a real origin, and genuinely cannot fast-forward.

    Three local paths, and only two of them may be reported:
      * `shared.py`   -- edited here AND changed on origin      -> blocks, FF_MODIFIED
      * `arriving.md` -- untracked here AND added by origin     -> blocks, FF_UNTRACKED
      * `mine.py`     -- edited here, untouched by origin       -> MUST NOT be reported
    `mine.py` is the leg that makes this a control rather than a demonstration: a function that
    reported every dirty path would pass everything above and fail only here.
    """
    remote, work, other = tmp_path / "origin.git", tmp_path / "work", tmp_path / "other"
    subprocess.run(["git", "init", "--bare", "-b", orc.BRANCH, str(remote)], check=True,
                   capture_output=True)

    for clone in (work, other):
        subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)
        _git(clone, "config", "user.email", "t@example.com")
        _git(clone, "config", "user.name", "t")

    (work / "shared.py").write_text("origin's first take\n")
    (work / "mine.py").write_text("untouched by origin\n")
    _git(work, "add", "shared.py", "mine.py")
    _git(work, "commit", "-m", "base")
    _git(work, "push", orc.REMOTE, "HEAD:{}".format(orc.BRANCH))

    # ORIGIN MOVES, touching one existing path and adding one new one.
    _git(other, "fetch", orc.REMOTE)
    _git(other, "reset", "--hard", "{}/{}".format(orc.REMOTE, orc.BRANCH))
    (other / "shared.py").write_text("origin's second take\n")
    (other / "arriving.md").write_text("a document staged by the director\n")
    _git(other, "add", "shared.py", "arriving.md")
    _git(other, "commit", "-m", "origin moves")
    _git(other, "push", orc.REMOTE, "HEAD:{}".format(orc.BRANCH))

    # AND THIS TREE IS DIRTY IN BOTH KINDS, plus one that collides with nothing.
    (work / "shared.py").write_text("this lane's uncommitted edit\n")
    (work / "mine.py").write_text("this lane's other uncommitted edit\n")
    (work / "arriving.md").write_text("an untracked twin\n")
    _git(work, "fetch", orc.REMOTE)
    return work


# ── the refusal is real before anything is claimed about naming it ──────────────────────────
def test_the_tree_really_cannot_fast_forward(forked):
    """THE REACHABILITY LEG. Everything below describes a refusal; this is what establishes there
    IS one. Without it the whole file could pass against a tree that advances cleanly, and the
    naming would be of a state that never occurs."""
    ff = subprocess.run(["git", "merge", "--ff-only", "{}/{}".format(orc.REMOTE, orc.BRANCH)],
                        cwd=str(forked), capture_output=True, text=True)
    assert ff.returncode != 0, "the fixture no longer builds a tree that refuses to advance"
    assert orc.commits_ahead(forked) == 0 and orc.commits_behind(forked) == 1


def test_it_names_the_dirty_path_and_the_untracked_twin_and_NOTHING_ELSE(forked):
    """MUTATION: report every dirty path instead of the intersection, and `mine.py` appears here.
    Drop either kind from the walk and one of the first two assertions fails."""
    blocking = orc.paths_blocking_fast_forward(forked)
    assert {b["path"] for b in blocking} == {"shared.py", "arriving.md"}
    kinds = {b["path"]: b["kind"] for b in blocking}
    assert kinds["shared.py"] == orc.FF_MODIFIED
    assert kinds["arriving.md"] == orc.FF_UNTRACKED


def test_the_two_kinds_are_actually_DIFFERENT(forked):
    """A partition whose legs carry the same label tells the reader nothing, and every assertion
    above would still pass if both constants held one string."""
    assert orc.FF_MODIFIED != orc.FF_UNTRACKED


def test_a_tree_that_CAN_advance_reports_an_empty_list_and_not_a_refusal(forked):
    """The null control. With the collisions removed the same call returns `[]` -- so a non-empty
    answer above was attainable AND avoidable, which is what makes it evidence."""
    _git(forked, "checkout", "--", "shared.py")
    (forked / "arriving.md").unlink()
    assert orc.paths_blocking_fast_forward(forked) == []
    ff = subprocess.run(["git", "merge", "--ff-only", "{}/{}".format(orc.REMOTE, orc.BRANCH)],
                        cwd=str(forked), capture_output=True, text=True)
    assert ff.returncode == 0, "nothing collided, so the advance must now succeed"


def test_an_unreadable_git_is_None_and_never_an_empty_list(tmp_path):
    """`[]` says "nothing collides" and `None` says "I could not look". A verdict that renders
    them the same is how a fail-open reads as a clean bill -- and this directory is not a repo."""
    assert orc.paths_blocking_fast_forward(tmp_path) is None


# ── and the verdict carries it ──────────────────────────────────────────────────────────────
def _not_advanced(blockers, **kw):
    """`reconcile` driven to a refused advance with nothing of ours to land."""
    return orc.reconcile(state_fn=lambda _p=None: (3, 0), gate_fn=lambda _p=None: False,
                         blockers_fn=lambda _p=None: blockers,
                         runner=lambda w: None, pusher=lambda w: None,
                         make_worktree=lambda p, w: (True, ""), drop_worktree=lambda p, w: None,
                         **kw)


def test_NOT_ADVANCED_names_the_paths_in_its_detail_and_carries_them_as_data(monkeypatch):
    """MUTATION: drop the clause from the detail string and the first assertion fails; drop the
    `blocking_paths` key and the second does. Both are needed -- the string is what a person reads
    in the log, the key is what the next mechanism can act on without parsing prose."""
    monkeypatch.setattr(orc, "_git", lambda *a, **k: subprocess.CompletedProcess(
        args=["git"], returncode=1, stdout="", stderr="local changes would be overwritten"))
    blockers = [{"path": "background/process_run_complete.py", "kind": orc.FF_MODIFIED},
                {"path": "docs/staging/A_FINDING.md", "kind": orc.FF_UNTRACKED}]
    r = _not_advanced(blockers)
    assert r["status"] == orc.NOT_ADVANCED
    assert "background/process_run_complete.py" in r["detail"]
    assert "docs/staging/A_FINDING.md" in r["detail"]
    assert orc.FF_UNTRACKED in r["detail"]
    assert r["blocking_paths"] == blockers


def test_a_verdict_that_could_not_look_says_so_rather_than_reading_as_clean(monkeypatch):
    """The `None` leg reaching the reader. "could NOT be established" and "NOTHING local collides"
    are opposite findings and the rendering must never collapse them."""
    monkeypatch.setattr(orc, "_git", lambda *a, **k: subprocess.CompletedProcess(
        args=["git"], returncode=1, stdout="", stderr="refused"))
    detail = _not_advanced(None)["detail"]
    assert "could NOT be established" in detail
    assert "NOTHING local collides" not in detail


def test_a_long_list_says_how_many_it_dropped(monkeypatch):
    """NO SILENT CAP. A truncated list that does not say it truncated reads as the whole set."""
    monkeypatch.setattr(orc, "_git", lambda *a, **k: subprocess.CompletedProcess(
        args=["git"], returncode=1, stdout="", stderr="refused"))
    many = [{"path": "p{}.py".format(i), "kind": orc.FF_MODIFIED} for i in range(20)]
    detail = _not_advanced(many)["detail"]
    assert "20 path(s)" in detail and "8 further path(s)" in detail


def test_the_post_merge_refusal_names_them_too(monkeypatch):
    """THE SECOND SITE. `NOT_ADVANCED` is returned from two places -- nothing-of-ours, and a merge
    that pushed and still left the tree behind. A repair wired into one of two sites is this
    project's most repeated defect, so the other site is asserted rather than assumed."""
    monkeypatch.setattr(orc, "_git", lambda *a, **k: subprocess.CompletedProcess(
        args=["git"], returncode=1, stdout="", stderr="refused"))
    states = [(2, 1), (3, 0)]
    r = orc.reconcile(state_fn=lambda _p=None: states.pop(0) if len(states) > 1 else states[0],
                      gate_fn=lambda _p=None: False,
                      blockers_fn=lambda _p=None: [{"path": "held.py", "kind": orc.FF_MODIFIED}],
                      runner=lambda w: subprocess.CompletedProcess(args=[], returncode=0, stdout=""),
                      pusher=lambda w: subprocess.CompletedProcess(args=[], returncode=0, stdout=""),
                      make_worktree=lambda p, w: (True, ""), drop_worktree=lambda p, w: None)
    assert r["status"] == orc.NOT_ADVANCED and r["pushed"] is True
    assert "held.py" in r["detail"] and r["blocking_paths"]
    assert "did NOT advance" in r["detail"], "the loop-detection wording must survive the edit"
