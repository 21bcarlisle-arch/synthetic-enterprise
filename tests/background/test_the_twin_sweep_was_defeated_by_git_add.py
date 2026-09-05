"""A byte-identical twin's fate depended on whether anybody had happened to `git add` it.

THE DEFECT, measured on the live shared tree 2026-09-05. Fourteen paths held the fast-forward:
nine untracked, five tracked. `identical_untracked_twins` matched all nine, and the all-or-nothing
property then correctly cleared NONE of them, because five `FF_MODIFIED` paths stood beside them.
Four of those five hashed EQUAL to origin's blob at the same path -- two staging notes another lane
had staged, one test file, and `background/origin_reconcile.py` itself, holding origin's own copy
of its own source. So thirteen of fourteen blockers were files about to be replaced by themselves,
the sweep built for exactly that sentence saw nine of them, and the shared tree sat 22 commits
behind origin while `--check` reported the fork every five minutes.

The sweep was not wrong about untracked files. It was scoped to a kind when the property it acts on
is about CONTENT, and `git add` moves a file from one kind to the other without touching a byte.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_a_staged_twin_is_cleared_and_the_advance_then_succeeds` -- the repair.
  * `test_a_tracked_twin_holding_untracked_twins_hostage_clears_them_all` -- the live shape. The
    untracked half was already correct and still could not fire, because the union is what the
    all-or-nothing test is taken over.
  * `test_a_tracked_path_that_differs_from_origin_still_refuses_everything` -- the safety property
    that must NOT have moved. This is the fifth path.
  * `test_a_tracked_twin_is_restored_not_unlinked` -- `unlink` leaves the index entry, and the
    fast-forward stays refused on a file no longer even on disk.
  * `test_an_unread_tracked_comparison_clears_nothing` -- fail-closed on the NEW `None` door.
  * `test_both_kinds_of_clearing_are_reachable` -- the reachability control over the branch.
  * `test_a_staged_add_leaves_the_index_and_a_tracked_edit_returns_to_head` -- the two shapes of
    `restore_tracked_twin`, against real git in a real throwaway repository.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

import pytest

from background import origin_reconcile as orc


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


class _Advance:
    """The real `advance_shared_tree` with both destructive edges injected and told apart.

    `removed` and `restored` are separate lists on purpose: the whole of the repair is that the two
    kinds are cleared by DIFFERENT acts, and a harness that collected them into one list could not
    tell a correct repair from one that unlinked a tracked path.
    """

    def __init__(self, ff_results, blocking, twins=(), tracked=(), restore_failure=None):
        self.ff_results = list(ff_results)
        self.blocking = blocking
        self.twins = twins
        self.tracked = tracked
        self.restore_failure = restore_failure
        self.removed: list[str] = []
        self.restored: list[str] = []
        self.ff_calls = 0

    def _ff(self):
        self.ff_calls += 1
        return self.ff_results.pop(0)

    def _restore(self, path):
        self.restored.append(path)
        return self.restore_failure

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=lambda _project: self.blocking,
            twins_fn=lambda _project, _blocking: (
                None if self.twins is None else list(self.twins)),
            tracked_twins_fn=lambda _project, _blocking: (
                None if self.tracked is None else list(self.tracked)),
            ff_fn=self._ff,
            remover=self.removed.append,
            restorer=self._restore,
            locker=contextlib.nullcontext,
            # LEVEL WITH ORIGIN, so the subject of every test here stays the TWIN logic. The real
            # `commits_ahead` reads the repository the suite runs in, which is routinely ahead of
            # origin, and that would refuse these cases for a reason none of them is about.
            ahead_fn=lambda _project: 0,
        )


def test_a_staged_twin_is_cleared_and_the_advance_then_succeeds():
    """THE REPAIR. A TRACKED path whose bytes origin already holds is returned to HEAD, and the
    fast-forward git had refused then succeeds.

    Before this, the same file left unstaged would have been cleared and the same file staged would
    not -- identical bytes, opposite outcomes, decided by an act that changes no content.

    MUTATION: drop `tracked` from the `resolvable` union (`resolvable = sorted(set(twins))`) and the
    length comparison refuses, so `advanced` stays False and the first assertion reds.
    """
    twin = "tests/background/test_a_refused_advance_names_the_paths_that_refused_it.py"
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_modified(twin)], tracked=[twin]).run()

    assert adv["advanced"] is True, \
        "the staged path was byte-identical to what origin brings, so the advance had nothing to " \
        "lose by clearing it and should have gone through"
    assert adv["cleared"] == [twin], \
        "the advance must report exactly which paths it cleared -- a reader recovering one needs " \
        "its name, and origin holds every one of them"


def test_a_tracked_twin_holding_untracked_twins_hostage_clears_them_all():
    """THE LIVE 2026-09-05 SHAPE. Untracked twins beside a TRACKED twin: the untracked sweep was
    already correct and still could not fire, because all-or-nothing is taken over the union and
    the tracked path was never a candidate for it.

    Nine untracked staging notes sat behind four tracked twins for 22 commits exactly like this.

    MUTATION: take the length comparison over `twins` alone rather than `resolvable` and the tracked
    path counts as unresolved, so nothing is cleared at all and both assertions red.
    """
    notes = ["docs/staging/SEAT_FINDING_A.md", "docs/staging/SEAT_FINDING_B.md"]
    staged = "background/origin_reconcile.py"
    run = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                   blocking=[_untracked(n) for n in notes] + [_modified(staged)],
                   twins=notes, tracked=[staged])
    adv = run.run()

    assert adv["advanced"] is True, \
        "every blocking path was byte-identical to origin, so the tree had nothing to protect and " \
        "should have advanced"
    assert sorted(run.removed) == sorted(notes) and run.restored == [staged], \
        "the untracked notes must be REMOVED and the tracked file RESTORED -- got removed={}, " \
        "restored={}".format(run.removed, run.restored)


def test_a_tracked_path_that_differs_from_origin_still_refuses_everything():
    """THE SAFETY PROPERTY THAT MUST NOT HAVE MOVED. `background/process_run_complete.py` was the
    fifth path on the live tree, carrying 58 lines origin has never seen. It is a lane's real work,
    it cannot be hashed away, and it must refuse the whole advance however many twins stand beside
    it -- clearing them would be deletion bought for no advance.

    MUTATION: relax the length comparison to `if not resolvable` and the four twins are cleared for
    an advance that cannot happen, reding `cleared == []` and both list assertions.
    """
    twin, staged = "docs/staging/twin.md", "background/origin_reconcile.py"
    mine = "background/process_run_complete.py"
    run = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_untracked(twin), _modified(staged), _modified(mine)],
                   twins=[twin], tracked=[staged])
    adv = run.run()

    assert adv["advanced"] is False
    assert adv["cleared"] == [] and run.removed == [] and run.restored == [], \
        "a tracked path whose bytes origin does NOT hold blocks the fast-forward no matter what " \
        "else is cleared, so this must touch nothing at all"
    assert mine in adv["reason"], \
        "the refusal must name the path that actually held it, or the reader rediscovers it by hand"
    assert staged not in adv["reason"], \
        "a path that IS byte-identical is not what held the advance, and naming it sends the " \
        "reader at a file with nothing wrong with it"


def test_a_tracked_twin_is_restored_not_unlinked():
    """THE TWO KINDS ARE CLEARED BY DIFFERENT ACTS, and the difference is not cosmetic: `unlink` on
    a path with an index entry leaves that entry behind, so the fast-forward stays refused on a
    file that is no longer even on disk -- strictly worse than never having touched it.

    MUTATION: send every path through `_remove` and `restored == [staged]` reds.
    """
    twin, staged = "docs/staging/twin.md", "background/origin_reconcile.py"
    run = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                   blocking=[_untracked(twin), _modified(staged)],
                   twins=[twin], tracked=[staged])
    run.run()

    assert run.removed == [twin], "an untracked twin is removed from disk -- got {}".format(
        run.removed)
    assert run.restored == [staged], \
        "a tracked twin is returned to what HEAD holds, never unlinked -- got {}".format(
            run.restored)


def test_a_failed_restore_stops_the_advance_and_says_which_path():
    """`restore_tracked_twin` reports its failure as a string rather than raising, so a caller that
    only caught `OSError` would read a refusal as a success and fast-forward onto a tree it had
    half-cleared.

    MUTATION: ignore the return value of `_restore` and the advance proceeds to the second
    fast-forward and claims it, reding `advanced is False`.
    """
    staged = "background/origin_reconcile.py"
    run = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                   blocking=[_modified(staged)], tracked=[staged],
                   restore_failure="error: pathspec did not match")
    adv = run.run()

    assert adv["advanced"] is False, \
        "the twin was never actually cleared, so the fast-forward must not be attempted or claimed"
    assert run.ff_calls == 1, "the second fast-forward must not run after a failed clearing"
    assert staged in adv["reason"] and "pathspec did not match" in adv["reason"], \
        "the refusal must name the path and git's own words for why -- got {}".format(adv["reason"])


def test_an_unread_tracked_comparison_clears_nothing():
    """FAIL-CLOSED ON THE NEW `None` DOOR. `identical_tracked_twins` returns `None` for "git would
    not answer", distinct from `[]` for "nothing matched", and a version that treated the new door
    as the old one would clear files on a state nobody read.

    ONE CONTROL OVER BOTH DOORS: the untracked `None` was already guarded, and asserting only the
    new leg would pass against a repair that had dropped the old one.

    MUTATION: change `if twins is None or tracked is None` back to `if twins is None` and the
    tracked leg reds -- `None` is not iterable into the union, so it raises rather than refusing,
    which is a different failure and still red.
    """
    unread_tracked = _Advance(ff_results=[_completed(1, "refused")],
                              blocking=[_modified("background/origin_reconcile.py")],
                              twins=[], tracked=None).run()
    assert unread_tracked["advanced"] is False and unread_tracked["cleared"] == [], \
        "whether the tracked path matched origin byte for byte was never read, so nothing may be " \
        "cleared"

    unread_untracked = _Advance(ff_results=[_completed(1, "refused")],
                                blocking=[_untracked("docs/staging/twin.md")],
                                twins=None, tracked=[]).run()
    assert unread_untracked["advanced"] is False and unread_untracked["cleared"] == [], \
        "the untracked comparison's unread state was guarded before this repair and must still be"


def test_both_kinds_of_clearing_are_reachable():
    """THE REACHABILITY CONTROL over the new branch. Every other control here that involves a
    tracked twin can be satisfied by a `restore` leg that is never taken and a `remove` leg that
    takes everything, or by an `advance_shared_tree` that refuses unconditionally.

    CLAUDE.md, learned three times in one afternoon: when a branch exists to be taken rarely,
    assert it CAN be taken before asserting what it does. Written over the whole partition rather
    than a leg per branch.

    MUTATION: make `advance_shared_tree` refuse unconditionally, or route every path through one of
    the two clearers. Every other control in this file still passes; this one reds.
    """
    twin, staged = "docs/staging/twin.md", "background/origin_reconcile.py"
    both = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                    blocking=[_untracked(twin), _modified(staged)],
                    twins=[twin], tracked=[staged])
    both.run()
    tracked_only = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                            blocking=[_modified(staged)], tracked=[staged])
    tracked_only_adv = tracked_only.run()
    refused = _Advance(ff_results=[_completed(1, "would be overwritten")],
                       blocking=[_modified("background/process_run_complete.py")],
                       twins=[], tracked=[]).run()

    assert both.removed and both.restored, \
        "both clearing legs must be attainable from the same function -- a repair in which the " \
        "restore leg is dead would pass every other control in this file"
    assert tracked_only_adv["advanced"] is True, \
        "an advance held ONLY by tracked twins must be able to succeed, or the repair is a no-op " \
        "wherever nothing untracked happens to be standing beside them"
    assert refused["advanced"] is False and refused["cleared"] == [], \
        "and refusing must still be attainable, or the safety property is what died instead"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True,
                          timeout=60)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A real throwaway git repository. `restore_tracked_twin` shells out to git, and asserting it
    against a mock would be asserting my belief about `git checkout HEAD --` rather than git.
    """
    work = tmp_path / "repo"
    work.mkdir()
    _git(work, "init", "--quiet", "-b", "main")
    _git(work, "config", "user.email", "t@example.invalid")
    _git(work, "config", "user.name", "t")
    (work / "tracked.txt").write_text("head content\n", encoding="utf-8")
    _git(work, "add", "tracked.txt")
    _git(work, "commit", "--quiet", "-m", "base")
    return work


def test_a_staged_add_leaves_the_index_and_a_tracked_edit_returns_to_head(repo: Path):
    """THE TWO SHAPES, against real git. A twin HEAD knows is restored to HEAD's copy; a twin HEAD
    has never seen is a staged ADD, and there is no HEAD copy to restore it to -- it has to leave
    the index AND the disk or the fast-forward stays refused on it.

    Both are only ever reached for paths already hash-proven against origin, so the content this
    discards is content origin holds. That is asserted upstream; what is asserted here is that each
    shape actually leaves the tree in the state `merge --ff-only` needs.

    MUTATION: drop the `_blob_in_head` discrimination and always `git checkout HEAD -- <path>`, and
    the staged-add leg reds -- git refuses with "did not match any file(s) known to git", which
    `restore_tracked_twin` returns as a failure string rather than None.
    """
    (repo / "tracked.txt").write_text("origin's content\n", encoding="utf-8")
    (repo / "added.txt").write_text("origin's new file\n", encoding="utf-8")
    _git(repo, "add", "added.txt")

    assert orc.restore_tracked_twin(repo, "tracked.txt") is None, \
        "a path HEAD holds is restorable and must report success"
    assert (repo / "tracked.txt").read_text(encoding="utf-8") == "head content\n", \
        "the tracked twin must be back at HEAD's copy, which is what leaves the fast-forward " \
        "nothing to refuse on"

    assert orc.restore_tracked_twin(repo, "added.txt") is None, \
        "a staged ADD has no HEAD copy, and unstaging it is how it stops blocking -- this is the " \
        "leg a single `git checkout HEAD --` cannot do"
    assert not (repo / "added.txt").exists(), \
        "a staged add must leave the disk too: an index-only removal leaves an untracked file that " \
        "git still refuses to clobber, which is the same wedge one kind further along"

    assert _git(repo, "diff", "--name-only", "HEAD").stdout.strip() == "", \
        "after both shapes the tree must be clean against HEAD -- that, and nothing narrower, is " \
        "what `merge --ff-only` actually requires"


def test_a_path_git_will_not_answer_for_is_a_failure_not_a_silent_pass(repo: Path):
    """`restore_tracked_twin` must not report success for a path it did nothing to. A `None` return
    is read by the caller as "cleared", and the advance proceeds on it.

    MUTATION: return `None` unconditionally at the end of `restore_tracked_twin` and this reds.
    """
    failure = orc.restore_tracked_twin(repo, "never_existed_anywhere.txt")
    assert failure is not None, \
        "git holds this path in neither HEAD nor the index, so nothing was cleared and saying so " \
        "is the difference between a refusal and an advance onto a tree still holding the blocker"
