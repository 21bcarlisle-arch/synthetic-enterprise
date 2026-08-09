"""The ghost-pusher tripwire must tell a test's commit from a COLLEAGUE's (EPISODE4 item 1).

WHY THIS FILE EXISTS. The session-scoped guard in this directory's conftest compared HEAD before
and after the suite and blamed "this test session" for any move. On this box an autonomous worker
commits several times an hour and the publish-gate suite takes ~11 minutes, so the guard fired on
other people's work: a real D14 build commit landing mid-run failed a 22,525-green suite, the
publish gate booked it as `test_regression`, and publishing could only succeed in the lulls
between colleagues' commits. Measured twice in two days.

The named defect the guard must STILL fire on is unchanged: a test that reaches a
credential-holding publish path and commits to the real checkout. These tests pin both
directions, because a guard that stops firing is not a fix, it is a silencing.
"""
from __future__ import annotations

import subprocess

import pytest

from tests.background import conftest as C


# ── the discriminator, as a pure function ────────────────────────────────────────────────────
def test_a_colleagues_commit_is_not_ours():
    """MUTATION: make partition_commits put every row in `mine` and this fails."""
    rows = [("abc1234", "rich@example.com", "D14: world-first confounder work")]
    mine, theirs = C.partition_commits(rows)
    assert mine == []
    assert theirs == ["abc1234 D14: world-first confounder work"]


def test_a_commit_from_this_process_is_ours():
    """The named defect. MUTATION: make partition_commits put every row in `theirs` -- i.e.
    silence the guard -- and this fails."""
    rows = [("def5678", C.GHOST_SENTINEL_EMAIL, "chore(liveness): publish heartbeat")]
    mine, theirs = C.partition_commits(rows)
    assert mine == ["def5678 chore(liveness): publish heartbeat"]
    assert theirs == []


def test_a_mixed_range_still_reports_only_ours():
    """The realistic case: our ghost push lands in the same window as a colleague's real work.
    Both must be classified, and the colleague must not be blamed."""
    rows = [
        ("aaa1111", "rich@example.com", "D17: counterfactual handed an injected error"),
        ("bbb2222", C.GHOST_SENTINEL_EMAIL, "chore(liveness): publish heartbeat"),
        ("ccc3333", "rich@example.com", "H_GAP: L2.4 anchored on a real panel"),
    ]
    mine, theirs = C.partition_commits(rows)
    assert mine == ["bbb2222 chore(liveness): publish heartbeat"]
    assert len(theirs) == 2


# ── the sentinel actually reaches a real `git commit` ────────────────────────────────────────
def test_the_sentinel_is_inherited_by_a_real_git_subprocess(tmp_path):
    """The discriminator is worthless unless a commit made from inside this process really does
    carry the sentinel. Proven against a REAL git, in a throwaway repo -- never the live tree.

    MUTATION: drop the `os.environ.setdefault(GIT_COMMITTER_EMAIL, ...)` line in conftest and
    this fails, because the commit inherits the box's normal identity instead."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def run(*a):
        return subprocess.run(a, cwd=str(repo), capture_output=True, text=True, timeout=30)

    run("git", "init", "-q")
    run("git", "config", "user.name", "t")
    run("git", "config", "user.email", "config-level@example.com")   # committer env must WIN
    (repo / "f.txt").write_text("x")
    run("git", "add", "f.txt")
    assert run("git", "commit", "-q", "-m", "probe").returncode == 0
    committer = run("git", "log", "-1", "--format=%ce").stdout.strip()
    assert committer == C.GHOST_SENTINEL_EMAIL, (
        f"a git commit from inside pytest carried {committer!r}, so the tripwire cannot "
        "attribute commits and would blame colleagues again"
    )

# ── fail-closed when attribution is impossible (R15) ─────────────────────────────────────────
def test_unattributable_head_move_fails_closed():
    """R15: an unavailable check is a FAILED check. If HEAD moved and the log cannot be read,
    the guard must refuse rather than wave it through.

    MUTATION: `return None` instead of the message in the `rows is None` branch and this fails."""
    msg = C.ghost_verdict("BEFORE", "AFTER", None, "a probe")
    assert msg and "unattributable" in msg.lower()


def test_head_that_did_not_move_is_never_a_ghost_push():
    assert C.ghost_verdict("SAME", "SAME", None, "a probe") is None


def test_a_colleague_only_move_does_not_fail_the_suite():
    """The regression this whole change exists to kill: a colleague commits mid-run and the
    suite stays green.

    MUTATION: restore an unconditional message on any HEAD move and this fails."""
    rows = [("abc1234", "rich@example.com", "D14: real build work")]
    assert C.ghost_verdict("BEFORE", "AFTER", rows, "a probe") is None


def test_our_own_commit_still_fails_the_suite():
    """...and the guard still has its teeth on its own named defect."""
    rows = [("def5678", C.GHOST_SENTINEL_EMAIL, "chore(liveness): publish heartbeat")]
    msg = C.ghost_verdict("BEFORE", "AFTER", rows, "a probe")
    assert msg and "GHOST PUSHER" in msg and "def5678" in msg


def test_a_mixed_range_blames_only_ours():
    rows = [
        ("aaa1111", "rich@example.com", "D17: injected error"),
        ("bbb2222", C.GHOST_SENTINEL_EMAIL, "ghost"),
    ]
    msg = C.ghost_verdict("BEFORE", "AFTER", rows, "a probe")
    assert msg and "bbb2222" in msg
    assert "NOT ours" in msg and "aaa1111" in msg
