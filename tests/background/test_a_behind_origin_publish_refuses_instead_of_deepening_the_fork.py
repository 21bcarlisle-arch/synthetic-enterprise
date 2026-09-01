"""THE PUBLISH LOOP WAS WIDENING THE FORK IT WAS BLOCKED BY (2026-09-01).

Measured that morning, after `git fetch`: `origin/main..HEAD` = 3 and `HEAD..origin/main` = 23.
Two of the three local commits were `Auto-process run complete` — created by this very loop,
AFTER its own push had already been rejected:

    ! [rejected]  HEAD -> main (non-fast-forward)
    Updates were rejected because the tip of your current branch is behind its remote counterpart
    ... throttle left untouched, will retry next cycle

The publisher classified that as a transient and re-attempted identically every twelve minutes.
It is not a transient, it is a STATE, and each attempt made it one commit worse: the retry was
the mechanism. Every surface the loop regenerated for nine hours stayed local, and the public
page served a snapshot.

The repair is ordering, not effort: read origin BEFORE the commit is created, and refuse. These
controls are keyed to that PROPERTY — "a commit is not created while origin is ahead" — not to
today's fork, which is already reconciled and would make a pinned control green forever.

REAL GIT, NOT A STUB, for the two that decide the verdict. The question is what `git` answers on
a behind-origin tree, and a fake that answers it for us would be grading a channel that does not
exist (R15: a harness that fabricates the observable). The stubs below are used only where the
subject is the publisher's own branching, with the observation held fixed.
"""

from __future__ import annotations

import contextlib
import subprocess
import types

import pytest

from background import process_run_complete as prc
from background import publish_cause as pc


def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=60, check=False)


@pytest.fixture()
def forked_clone(tmp_path):
    """A real clone whose origin has moved on without it. Returns (clone, origin).

    Built by committing to the origin AFTER the clone was taken, which is exactly the shape the
    incident had: the local tree is not behind because anyone rewrote history, it is behind
    because 23 other commits landed while it was working.
    """
    origin = tmp_path / "origin.git"
    work = tmp_path / "seed"
    work.mkdir()
    _git("init", "-q", "-b", "main", cwd=work)
    _git("config", "user.email", "t@example.invalid", cwd=work)
    _git("config", "user.name", "T", cwd=work)
    (work / "a.txt").write_text("one\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-q", "-m", "seed", cwd=work)
    _git("clone", "-q", "--bare", str(work), str(origin), cwd=tmp_path)

    clone = tmp_path / "clone"
    _git("clone", "-q", str(origin), str(clone), cwd=tmp_path)
    _git("config", "user.email", "t@example.invalid", cwd=clone)
    _git("config", "user.name", "T", cwd=clone)
    return clone, work, origin


def _advance_origin(work, origin, n):
    """Land `n` further commits on the bare origin, from the seed worktree."""
    for i in range(n):
        (work / "a.txt").write_text("upstream {}\n".format(i))
        _git("add", "a.txt", cwd=work)
        _git("commit", "-q", "-m", "upstream {}".format(i), cwd=work)
    _git("push", "-q", str(origin), "main", cwd=work)


# ── The observation ──────────────────────────────────────────────────────────────────────────

def test_the_count_is_read_from_the_remote_and_not_from_the_tracking_ref(
        forked_clone, monkeypatch):
    """THE ONE THAT WOULD HAVE CAUGHT IT. `refs/remotes/origin/main` in the clone still points at
    the seed commit — nothing has fetched since — so a guard reading the tracking ref answers
    ZERO on a tree that is three behind, in precisely the state it exists to detect.

    MUTATION: drop the `git fetch` and read `HEAD..origin/main`, and this reds with 0 != 3.

    WHAT THE FETCH IS FOR, AND WHAT IT IS NOT. I first wrote this control claiming that swapping
    `HEAD..FETCH_HEAD` for `HEAD..origin/main` would red it. Run on 2026-09-01 against git
    2.53.0, that mutation SURVIVED, and the reason is an equivalence rather than a hole here:
    `git fetch origin main` opportunistically updates `refs/remotes/origin/main` too, so once
    the fetch has happened both refs answer 3. Measured, not reasoned — before the fetch the
    tracking ref reads 0 and after it reads 3. So the load-bearing element is the FETCH, and
    that is what the mutation above removes. FETCH_HEAD is kept in the code anyway because it
    does not depend on that opportunistic update, which is a property of the git version rather
    than of the refspec asked for; no control pins that preference and this says so instead of
    implying one does.
    """
    clone, work, origin = forked_clone
    _advance_origin(work, origin, 3)
    monkeypatch.setattr(prc, "PROJECT_DIR", clone)

    stale = _git("rev-list", "--count", "HEAD..origin/main", cwd=clone).stdout.strip()
    assert stale == "0", (
        "premise of this control: the tracking ref is stale here, so a guard reading it sees "
        "no divergence -- if git has started auto-updating it, this test must be re-thought "
        "rather than deleted")

    assert prc._commits_origin_is_ahead_by() == 3


def test_a_clone_level_with_origin_reads_zero_and_is_not_refused(forked_clone, monkeypatch):
    """THE PASS BRANCH IS REACHABLE, on the same fixture as the fail branch. Without this the
    guard could return a constant refusal and every other assertion here would still be green
    (R15: a control whose PASS branch is unreachable reports a constant verdict).

    MUTATION: return a non-zero count unconditionally and this reds.
    """
    clone, _work, _origin = forked_clone
    monkeypatch.setattr(prc, "PROJECT_DIR", clone)

    assert prc._commits_origin_is_ahead_by() == 0
    assert prc._divergence_refusal() is None


def test_an_unreadable_origin_is_none_and_not_zero(tmp_path, monkeypatch):
    """FAIL-CLOSED ON THE MISSING READ. A remote that cannot be reached is the condition under
    which a commit is LEAST likely to reach origin, so "we could not tell" must not be spelled
    the same way as "we are level".

    MUTATION: return 0 from the `fetched.returncode != 0` branch and this reds.

    IT DOES NOT COVER THE `except` HANDLER, AND IT WAS FIRST WRITTEN CLAIMING IT DID. This
    docstring used to read "MUTATION: `except ...: return 0` ... and this reds". Run on
    2026-09-01, that mutation SURVIVED. The reason is that `git fetch origin main` in a repo with
    no remote EXITS 128 rather than raising, so this fixture returns at the returncode branch and
    never reaches the handler at all — a missing test, not an equivalence, and the flattering
    reading was the wrong one. The two controls below reach the handler on its own terms.
    """
    repo = tmp_path / "no_remote"
    repo.mkdir()
    _git("init", "-q", "-b", "main", cwd=repo)
    _git("config", "user.email", "t@example.invalid", cwd=repo)
    _git("config", "user.name", "T", cwd=repo)
    (repo / "a.txt").write_text("one\n")
    _git("add", "a.txt", cwd=repo)
    _git("commit", "-q", "-m", "seed", cwd=repo)
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._commits_origin_is_ahead_by() is None
    refusal = prc._divergence_refusal()
    assert refusal is not None and "UNREADABLE" in refusal


@pytest.mark.parametrize("how, break_it", [
    ("the fetch hangs past its timeout",
     lambda cmd, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired(cmd, 60))),
    ("git answers rc=0 with nothing on stdout",
     lambda cmd, **kw: types.SimpleNamespace(returncode=0, stdout="", stderr="")),
])
def test_a_raising_or_unparseable_git_is_none_and_not_zero(how, break_it, monkeypatch):
    """THE `except` HANDLER, ON ITS OWN TERMS — the branch the no-remote fixture above cannot
    reach, and which nothing covered until this was written.

    STUBBED ON PURPOSE, AND THE SUBJECT SAYS WHY. Everywhere else in this file the observation is
    measured against real git, because the question is what git answers on a forked tree. Here
    the question is the opposite one: what the publisher does when git DOESN'T answer. A hung
    fetch and a garbled stdout are not states a real repository can be asked to hold on demand,
    and the branching under test is the publisher's own.

    BOTH ARMS ARE REACHABLE IN PRODUCTION. The fetch is a network read with a 60-second bound, on
    the exact machine whose origin froze for 3.5 hours on 2026-07-24; and `int("")` is what an
    rc=0-with-empty-stdout git hands this function. On either, "we could not tell" must not be
    spelled `0` — that is the state in which a commit is LEAST likely to reach origin.

    MUTATION: `except (...): return 0` and this reds on both arms. That is the fail-open shape
    the R15 catalogue names first (missing/zero/empty/malformed), and it is the mutation the
    control above was wrongly credited with killing.
    """
    monkeypatch.setattr(prc.subprocess, "run", break_it)

    assert prc._commits_origin_is_ahead_by() is None, how
    refusal = prc._divergence_refusal()
    assert refusal is not None and "UNREADABLE" in refusal, how


# ── The act ──────────────────────────────────────────────────────────────────────────────────

def _publish_with_origin_ahead_by(monkeypatch, tmp_path, ahead):
    """Drive `git_commit_push` with the divergence observation held at `ahead`.

    The observation is stubbed HERE and only here: the subject of these two tests is what the
    publisher DOES with the answer, and the answer itself is measured against real git above.
    Returns (returned, outcome_reason, git_commands_run).
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / "cause.json")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: ahead)
    monkeypatch.setattr(prc, "_push_due", lambda: False)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    outcome = {}
    returned = prc.git_commit_push("abc1234", 1000.0, outcome=outcome)
    return returned, outcome.get("reason"), calls


def test_no_commit_is_created_while_origin_is_ahead(tmp_path, monkeypatch):
    """THE REGRESSION, as a property: on a behind-origin tree the publish path must not reach
    `git commit` at all. Asserting on the outcome name alone would not catch a version that
    named the state and committed anyway -- and committing anyway is the entire defect, because
    the commit is what widens the fork.

    MUTATION: delete the `_divergence_refusal` block at the top of `git_commit_push` and this
    reds on both assertions -- a `git commit` appears in the call list and the reason is not
    `behind_origin`.
    """
    returned, reason, calls = _publish_with_origin_ahead_by(monkeypatch, tmp_path, ahead=23)

    assert returned is False
    assert reason == prc.BEHIND_ORIGIN
    assert not any(c[:2] == ["git", "commit"] for c in calls), \
        "a commit created while origin is ahead can only be rejected, and leaves the fork wider"
    assert not any(c[:2] == ["git", "add"] for c in calls), \
        "nothing may be staged either -- a left-staged payload is the next lane's problem"


def test_a_level_tree_still_publishes(tmp_path, monkeypatch):
    """SCOPE. The guard must refuse the behind-origin case and NOTHING ELSE; a control that only
    ever sees the refusal cannot tell a guard from a shutdown.

    MUTATION: refuse unconditionally (or on `ahead is not None`) and this reds.
    """
    _returned, reason, calls = _publish_with_origin_ahead_by(monkeypatch, tmp_path, ahead=0)

    assert reason != prc.BEHIND_ORIGIN
    assert any(c[:2] == ["git", "commit"] for c in calls), \
        "with origin level, the publish path must go all the way to the commit as before"


def test_the_liveness_and_banner_path_refuses_on_the_same_state(tmp_path, monkeypatch):
    """THE SECOND COMMIT SITE. The heartbeat and the provenance banner commit through
    `_commit_and_push_paths`, and a commit from there deepens the fork exactly as a content
    commit does. Fixing only the site the incident was observed at is what makes a class recur.

    MUTATION: remove the `_divergence_refusal` block in `_commit_and_push_paths` and this reds.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 23)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    assert prc._commit_and_push_paths(["site/data/tick_heartbeat.json"], "chore(liveness)",
                                      label="Liveness heartbeat", git_hash="abc1234") is False
    assert not any(c[:2] == ["git", "commit"] for c in calls)


# ── The record the reader works from ─────────────────────────────────────────────────────────

def test_behind_origin_is_a_failure_that_retries_and_carries_its_own_cause(tmp_path,
                                                                          monkeypatch):
    """It must NOT be fingerprinted as a no-op (or the reconciled tree never re-publishes this
    run), it must exit 77 (or the alarm is told a freeze succeeded), and it must attribute to a
    cause of its OWN rather than borrowing `push_never_landed` -- which is true of the fork but
    sends the reader to the push, when the fixable fact is that the commit should not have been
    made.

    MUTATION: put `BEHIND_ORIGIN` in `RETRYABLE_PUBLISH_OUTCOMES`, or map it to
    `PUSH_NEVER_LANDED`, and this reds.
    """
    assert prc.BEHIND_ORIGIN not in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert prc.publish_exit_code(prc.BEHIND_ORIGIN) == prc.EXIT_PUBLISH_DID_NOT_LAND
    assert prc.PUBLISH_CAUSE_FOR_REASON[prc.BEHIND_ORIGIN] == pc.BEHIND_ORIGIN
    assert pc.BEHIND_ORIGIN != pc.PUSH_NEVER_LANDED

    _returned, _reason, _calls = _publish_with_origin_ahead_by(monkeypatch, tmp_path, ahead=23)
    cause, evidence = pc.read_cause(tmp_path / "cause.json", "abc1234")
    assert cause == pc.BEHIND_ORIGIN
    assert "surgical_land" in evidence, \
        "a refusal must name the remedy, or the reader is left to guess at the reconciliation"


def test_no_test_is_implicated_by_a_behind_origin_refusal():
    """No test ran, so no blocking list or suspect may be attached to this cause. A publish that
    fails without running the suite is otherwise filed as a red, and hours go into hunting a
    test that was never executed.

    MUTATION: drop `BEHIND_ORIGIN` from `NO_TEST_JUDGED_CAUSES` and this reds.
    """
    assert pc.BEHIND_ORIGIN in pc.NO_TEST_JUDGED_CAUSES
