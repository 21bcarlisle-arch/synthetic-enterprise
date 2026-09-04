"""The delivery seat measured the branch with a reader that could only see its own checkout.

THE DEFECT. `delivery_seat.commits_since` assembled the stretch with `git log --since=... ` and NO
revision argument. Git's default is HEAD, so a commit that had reached `origin/main` and that this
checkout had not fast-forwarded to was, to the seat, a commit that had not happened. The seat then
graded the stretch, decided whether anything material had occurred, and -- when the answer was no
-- recorded a SKIP with a reason that was true of HEAD and false of the work. Every judgement in
the module, including the `wrong` rows the orienting session is handed to grade itself against,
rested on that reading.

`grep -n origin background/delivery_seat.py` returned NOTHING over the whole module. It was not
that origin was read badly; it was that the concept was absent.

WHY IT HAD NEVER YET PRODUCED A WRONG BRIEF: luck. The shared tree is usually level when the
three-hourly timer fires, and it was level again on the turn this was fixed. That is exactly the
condition under which a control keyed to TODAY'S ANSWER would be written green and prove nothing.
`WORKER_FINDING_REPEATING_ALARM_PUBLISH_REFUSED_ORIGIN_AHEAD_ORIGIN_MAIN_IS_COMMIT_S_AHEAD_
2026-09-03.md` is the condition firing for real.

SO THE CONTROL IS KEYED TO THE PROPERTY, NOT TO THE STATE: a stretch measured while origin is
AHEAD must report the same work as one measured while the checkout is LEVEL. Both readings are
taken here, from one real repository, and compared to EACH OTHER -- so this test cannot pass by
the divergence happening to be zero, and cannot go red for the tree becoming more honest.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone

import pytest

from background import commit_narrative as cn
from background import delivery_seat as seat


def _run(cwd, *args: str) -> str:
    out = subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True)
    return out.stdout


def _commit(repo, name: str, body: str) -> None:
    (repo / name).write_text(body, encoding="utf-8")
    _run(repo, "add", name)
    _run(repo, "commit", "-m", f"landed {name}")


@pytest.fixture()
def diverged(tmp_path):
    """A real checkout sitting BEHIND a real `origin/main`, plus the means to level it up.

    Not a mock: the subject is what `git log` does with and without a revision argument, and a
    fake git would be a test of the fake.
    """
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _run(upstream, "init", "-q", "-b", "main")
    _commit(upstream, "company_a.py", "x = 1\n")
    _commit(upstream, "company_b.py", "x = 2\n")

    checkout = tmp_path / "checkout"
    _run(tmp_path, "clone", "-q", str(upstream), str(checkout))

    # The two commits the checkout will NOT have. Made after the clone, fetched but never merged --
    # which is the ordinary shape of "another lane pushed while this tree was busy".
    _commit(upstream, "company_c.py", "x = 3\n")
    _commit(upstream, "company_d.py", "x = 4\n")
    _run(checkout, "fetch", "-q", "origin")
    return checkout


def _subjects(rows) -> set[str]:
    return {r["subject"] for r in rows}


def _since():
    return datetime.now(timezone.utc) - timedelta(hours=6)


def test_the_stretch_reports_the_same_work_whether_origin_is_ahead_or_level(diverged, monkeypatch):
    """THE FINISHED CONDITION, stated as the director stated it. Measure while origin is ahead,
    fast-forward, measure again: the work reported must be identical. A HEAD-only reader fails
    this on the first call, reporting two commits where there are four."""
    monkeypatch.setattr(seat, "PROJECT_DIR", diverged)

    assert _run(diverged, "rev-list", "--left-right", "--count", "HEAD...origin/main").split() == \
        ["0", "2"], "fixture precondition: the checkout must actually be behind"
    while_behind = _subjects(seat.commits_since(_since()))

    _run(diverged, "merge", "-q", "--ff-only", "origin/main")
    assert _run(diverged, "rev-list", "--left-right", "--count", "HEAD...origin/main").split() == \
        ["0", "0"], "fixture precondition: the checkout must now be level"
    while_level = _subjects(seat.commits_since(_since()))

    assert while_behind == while_level
    assert while_behind == {"landed company_a.py", "landed company_b.py",
                            "landed company_c.py", "landed company_d.py"}


def test_the_brief_states_a_divergence_instead_of_silently_grading_one_side(diverged, monkeypatch):
    """A divergence is a fact about the machine and belongs on the face of the brief. The old
    module had no way to represent it: `behind` commits were simply absent from the count."""
    monkeypatch.setattr(seat, "PROJECT_DIR", diverged)

    div = seat.branch_divergence()
    assert div["available"] is True
    assert (div["ahead"], div["behind"]) == (0, 2)
    assert div["diverged"] is True
    assert "diverged" in div["says"].lower()
    assert "2" in div["says"], "the count itself must be on the face, not just the fact"

    _run(diverged, "merge", "-q", "--ff-only", "origin/main")
    level = seat.branch_divergence()
    assert level["diverged"] is False
    assert (level["ahead"], level["behind"]) == (0, 0)
    assert "level" in level["says"].lower()


def test_a_checkout_behind_its_branch_is_material_even_with_nothing_else_to_orient_on():
    """`behind` means the daemons running from this tree are on code the branch has moved past --
    pushed is not imported. It must reach `is_material` on its own, because the stretch it would
    otherwise be judged by is exactly the one it makes untrustworthy.

    `ahead` alone deliberately does NOT: work committed and not yet pushed is the normal state of
    a lane mid-turn, and firing on it would make the seat orient on its own commit."""
    quiet = {
        "substantive_count": 0, "shape": {"shape_is_wrong": False}, "levels_recorded": [],
        "levels_moved": {}, "director_inputs": [], "findings": {}, "commit_count": 0,
        "live_direction_age_hours": 0.5,
    }
    assert seat.is_material(dict(quiet, divergence={
        "available": True, "ahead": 0, "behind": 0, "diverged": False}))[0] is False

    material, why = seat.is_material(dict(quiet, divergence={
        "available": True, "ahead": 0, "behind": 3, "diverged": True}))
    assert material is True
    assert "3" in why and "behind" in why

    assert seat.is_material(dict(quiet, divergence={
        "available": True, "ahead": 4, "behind": 0, "diverged": True}))[0] is False


def test_a_checkout_with_no_origin_says_so_rather_than_reporting_no_divergence(tmp_path,
                                                                              monkeypatch):
    """FAIL-CLOSED ON THE UNREADABLE INPUT. "HEAD and origin/main are level" and "there is no
    origin/main to compare against" are different states, and `_git` collapsed them both to "" --
    the empty-string-means-both conflation this project has paid for repeatedly. A worktree cut
    for an isolated run is the ordinary way to land in the second state."""
    lone = tmp_path / "lone"
    lone.mkdir()
    _run(lone, "init", "-q", "-b", "main")
    _commit(lone, "only.py", "x = 1\n")
    monkeypatch.setattr(seat, "PROJECT_DIR", lone)

    div = seat.branch_divergence()
    assert div["available"] is False
    assert div.get("diverged") is None, "an unmeasured divergence must not read as 'no divergence'"
    assert "no origin/main" in div["why"]
    assert "HEAD-ONLY" in div["says"]

    # ...and the stretch still reads, degrading to HEAD alone rather than crashing on a ref that
    # is not there.
    assert _subjects(seat.commits_since(_since())) == {"landed only.py"}


def test_an_unreadable_rev_list_fails_closed_rather_than_reporting_level(diverged, monkeypatch):
    """THE DIGIT PARSE IS THE FAIL-CLOSED LEG, and it is the reason a `_git_or_none` helper was
    deleted as an equivalence rather than kept. `_git` returns "" for a failed command, and ""
    must NOT arrive at the caller as (0, 0) -- "the divergence could not be measured" reported as
    "the branches are level" is the fail-open this whole module was just fixed for.

    Reached by making the rev-list itself unreadable while `origin/main` genuinely exists, so the
    branch under test is the parse and not the missing-ref branch above."""
    monkeypatch.setattr(seat, "PROJECT_DIR", diverged)
    real = seat._git

    def _blind(*args: str) -> str:
        return "" if args[:1] == ("rev-list",) else real(*args)

    monkeypatch.setattr(seat, "_git", _blind)
    div = seat.branch_divergence()
    assert div["available"] is False
    assert div.get("ahead") is None and div.get("behind") is None
    assert div.get("diverged") is None
    assert "unreadable" in div["why"]
    # ...and nothing downstream may read that as something to orient on
    assert seat.is_material({
        "substantive_count": 0, "shape": {"shape_is_wrong": False}, "levels_recorded": [],
        "levels_moved": {}, "director_inputs": [], "findings": {}, "commit_count": 0,
        "live_direction_age_hours": 0.5, "divergence": div})[0] is False


def test_the_shape_reader_reads_both_sides_too(diverged):
    """`commit_shape` is the leg `is_material` trusts to call a stretch a MACHINE FAULT -- a run of
    empty merges. Those get pushed. A HEAD-only shape reader is blind to the run precisely when it
    is happening fastest, so the `revs` argument has to be threaded all the way through
    `narrative` to `read_commits` and not merely accepted."""
    head_only = _subjects(cn.read_commits(diverged, limit=50))
    both = _subjects(cn.read_commits(diverged, limit=50, revs=("HEAD", "origin/main")))
    assert len(head_only) == 2
    assert len(both) == 4
    assert head_only < both

    # threaded, not swallowed: `narrative` must hand it down
    assert cn.narrative(diverged, limit=50, revs=("HEAD", "origin/main"))["count"] == 4
    assert cn.narrative(diverged, limit=50)["count"] == 2
