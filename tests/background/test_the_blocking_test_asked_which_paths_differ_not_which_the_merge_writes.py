"""The reconciler's blocking test asked which paths DIFFER, not which the merge would WRITE.

THE DEFECT. `paths_blocking_fast_forward` built its candidate set from
`git diff --name-only HEAD origin/main` -- the symmetric difference of two endpoint trees. The
property that actually blocks a checkout is different: which paths the merge RESULT differs from
HEAD on, because those and only those are the paths git must write. A path HEAD DELETED that origin
still carries differs between the endpoints and so was reported, while the merge result also lacks
it, so git writes nothing there and it blocks nothing.

WHY IT WAS A WEDGE AND NOT A NUISANCE. `e4aa02359` took two head-red paths out of the index on
purpose and left them on disk; origin had not touched either since the merge base. Reported as
untracked blockers for ever -- their producer rewrites them on every run, so they re-diverge within
minutes of any clearing, and an all-or-nothing clearing rule fed a self-regenerating false positive
has no exit. Measured 2026-09-10: 4 -> 9 -> 12 -> 15 commits behind across one day, the same
complaint every five minutes, `last_clean_publish: null`, cause `behind_origin` on all nine
episode failures.

THIS IS A STRICT NARROWING, so the asymmetry is what needs proving and it is proved here rather
than argued: `test_a_path_the_merge_GENUINELY_writes_is_still_reported` and
`test_a_CONFLICTED_path_is_still_reported` are the poison legs, and
`test_the_OLD_predicate_really_did_report_the_deletion` is what stops the whole file passing
against a tree where the two questions happen to coincide.
"""
import subprocess

import pytest

import background.origin_reconcile as orc


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


@pytest.fixture()
def diverged(tmp_path):
    """A real fork on disk carrying all three shapes at once.

      * `ours_deleted.txt` -- HEAD deletes it, origin never touches it after the base, and it is
        still on disk untracked. THE FALSE POSITIVE: endpoint-different, merge writes nothing.
      * `origin_adds.md`   -- origin adds it, this tree has an untracked copy. A TRUE positive.
      * `both_edit.py`     -- both sides edit it, so the merge CONFLICTS, and it is dirty here on
        top of that. A true positive, and the one a careless narrowing would drop.
      * `mine.py`          -- dirty here, untouched by origin. Must never be named by either
        predicate; without it a function reporting every dirty path would pass everything else.
    """
    remote, work, other = tmp_path / "origin.git", tmp_path / "work", tmp_path / "other"
    subprocess.run(["git", "init", "--bare", "-b", orc.BRANCH, str(remote)], check=True,
                   capture_output=True)
    for clone in (work, other):
        subprocess.run(["git", "clone", str(remote), str(clone)], check=True, capture_output=True)
        _git(clone, "config", "user.email", "t@example.com")
        _git(clone, "config", "user.name", "t")

    (work / "ours_deleted.txt").write_text("machine state a checkout must not inherit\n")
    (work / "both_edit.py").write_text("base = 1\n")
    (work / "mine.py").write_text("untouched by origin\n")
    _git(work, "add", "ours_deleted.txt", "both_edit.py", "mine.py")
    _git(work, "commit", "-m", "base")
    _git(work, "push", orc.REMOTE, "HEAD:{}".format(orc.BRANCH))

    # ORIGIN MOVES: it adds one path and edits the shared one. It does NOT touch the path we delete.
    _git(other, "fetch", orc.REMOTE)
    _git(other, "reset", "--hard", "{}/{}".format(orc.REMOTE, orc.BRANCH))
    (other / "origin_adds.md").write_text("a document arriving from origin\n")
    (other / "both_edit.py").write_text("base = 2  # origin's take\n")
    _git(other, "add", "origin_adds.md", "both_edit.py")
    _git(other, "commit", "-m", "origin moves")
    _git(other, "push", orc.REMOTE, "HEAD:{}".format(orc.BRANCH))

    # AND THIS TREE DIVERGES: it commits a deletion that leaves the file on disk (the
    # `--content-remove` shape), and edits the shared path.
    _git(work, "rm", "--cached", "ours_deleted.txt")
    (work / "both_edit.py").write_text("base = 3  # this lane's take\n")
    _git(work, "add", "both_edit.py")
    _git(work, "commit", "-m", "the head-red path leaves the index and stays on disk")
    # AND THE CONFLICTED PATH IS DIRTY ON TOP OF THE COMMIT. This is deliberate and it is the
    # distinction the first draft of this file got wrong: `paths_blocking_fast_forward` reports
    # what LOCAL DIRT stops git writing, so a conflict that is only committed blocks the merge but
    # not the checkout and is correctly absent. To poison the narrowing against conflicts the path
    # has to be both -- conflicted in the merge AND uncommitted here.
    (work / "both_edit.py").write_text("base = 4  # and uncommitted on top\n")
    (work / "mine.py").write_text("this lane's uncommitted edit\n")
    (work / "origin_adds.md").write_text("an untracked twin of what origin adds\n")
    _git(work, "fetch", orc.REMOTE)
    return work


def _named(project):
    return {b["path"] for b in orc.paths_blocking_fast_forward(project)}


def _old_predicate(project):
    """The question the module used to ask, spelled out so the difference is measurable here."""
    return set(orc._paths(project, "diff", "--name-only", "-z", "HEAD",
                          "{}/{}".format(orc.REMOTE, orc.BRANCH)))


# ── the fork is real before anything is claimed about it ────────────────────────────────────
def test_the_fixture_really_is_diverged_and_really_does_conflict(diverged):
    """THE REACHABILITY LEG. Every assertion below describes a diverged tree whose merge
    conflicts; this is what establishes there is one. Without it the file could pass against a
    tree that fast-forwards cleanly, where the two questions coincide and prove nothing."""
    assert orc.commits_ahead(diverged) == 1 and orc.commits_behind(diverged) == 1
    merged = subprocess.run(
        ["git", "merge-tree", "--write-tree", "HEAD", "{}/{}".format(orc.REMOTE, orc.BRANCH)],
        cwd=str(diverged), capture_output=True, text=True)
    assert merged.returncode == 1, "the fixture no longer produces a CONFLICTED merge"


def test_the_OLD_predicate_really_did_report_the_deletion(diverged):
    """The defect, reproduced. If this ever goes green the fixture has stopped carrying the shape
    and every other assertion in this file is about a defect that is no longer reachable."""
    assert "ours_deleted.txt" in _old_predicate(diverged), (
        "the endpoint diff no longer reports a path HEAD deleted, so the false positive this "
        "change removes is not in the fixture and the narrowing below is unproven")


def test_a_path_THIS_BRANCH_DELETED_is_no_longer_reported(diverged):
    """THE FIX. Uncontested deletion: origin never touched it after the base, so the merge result
    lacks it too and git writes nothing there.

    MUTATION: restore `incoming` to the endpoint diff and this goes red -- which is the one
    assertion in this file that the old predicate fails.
    """
    assert (diverged / "ours_deleted.txt").exists(), (
        "the fixture's file left the disk, so 'untracked and blocking' is unreachable")
    assert "ours_deleted.txt" not in _named(diverged), (
        "a path this branch deliberately deleted, which origin has not touched and the merge "
        "would not write, is still being reported as blocking the advance")


def test_a_path_the_merge_GENUINELY_writes_is_still_reported(diverged):
    """THE POISON LEG. A narrowing that cannot hide a true positive has to be shown not to, on a
    true positive of the same KIND as the one it removes -- an untracked file whose name arrives
    from origin. Drop `origin_adds.md` here and the narrowing is a fail-open."""
    assert "origin_adds.md" in _named(diverged), (
        "the merge adds this path and an untracked copy is in the way, so git cannot write it -- "
        "the narrowing has hidden a real blocker")


def test_a_CONFLICTED_path_is_still_reported(diverged):
    """THE SECOND POISON LEG, and the one a reader is most likely to doubt. On a conflicted merge
    `merge-tree` still writes a tree, and the conflicted path's blob in it holds git's markers --
    which differ from HEAD, so the path is still named. A narrowing that quietly dropped conflicts
    would be at its most dangerous exactly when the tree is hardest to reconcile."""
    assert "both_edit.py" in _named(diverged), (
        "a path both sides edited -- a conflict the merge must write markers into -- is not "
        "reported as blocking")


def test_a_dirty_path_ORIGIN_NEVER_TOUCHED_is_named_by_neither(diverged):
    """The other side of the partition. A function that reported every dirty path would pass both
    poison legs above and fail only here."""
    assert "mine.py" not in _named(diverged)
    assert "mine.py" not in _old_predicate(diverged)


def test_an_unreadable_git_is_still_None_and_never_an_empty_list(tmp_path):
    """The narrowing must not convert "I could not look" into "nothing collides". `merge-tree`
    fails in a non-repo, the fallback's `diff` fails too, and `None` has to survive both."""
    assert orc.paths_blocking_fast_forward(tmp_path) is None


def test_an_UNANSWERABLE_merge_tree_falls_back_to_the_wider_answer(diverged, monkeypatch):
    """FAILS TOWARD OVER-REPORTING, stated as a control rather than as a comment. If `merge-tree`
    will not answer, the old endpoint diff is restored -- a false refusal a reader can clear, not a
    silent `[]` that reads as a clean bill."""
    real = orc._git

    def _broken(cwd, *args, **kw):
        if args and args[0] == "merge-tree":
            return subprocess.CompletedProcess(args, 129, "", "unknown option `--write-tree'")
        return real(cwd, *args, **kw)

    monkeypatch.setattr(orc, "_git", _broken)
    assert orc._arriving_paths(diverged) is not None, (
        "an unanswerable merge-tree returned None, so the caller reports no path at all")
    assert "ours_deleted.txt" in set(orc._arriving_paths(diverged)), (
        "the fallback is not the old wider answer, so the failure direction is untested")
