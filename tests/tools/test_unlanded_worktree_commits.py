"""Control for `tools.unlanded_worktree_commits`: a finished commit that only a worktree's HEAD holds
must reach the delivery seat's brief, and a worktree git cannot read must print as UNKNOWN.

Every test builds its own throwaway repository with a bare "origin", so nothing here reads the
shared tree's real worktrees -- the answer there changes by the hour.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from background import delivery_seat as seat
from tools import unlanded_worktree_commits as u


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-q", "-b", "main", str(origin)], check=True)
    root = tmp_path / "main"
    subprocess.run(["git", "clone", "-q", str(origin), str(root)], check=True,
                   capture_output=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
        _git(root, "config", k, v)
    (root / "a").write_text("a\n")
    _git(root, "add", "a")
    _git(root, "commit", "-q", "-m", "base")
    _git(root, "push", "-q", "origin", "HEAD:main")
    return root


def _plant(root: Path, wt: Path, subject: str) -> str:
    _git(root, "worktree", "add", "-q", "--detach", str(wt), "HEAD")
    (wt / "b").write_text("finished work\n")
    _git(wt, "add", "b")
    _git(wt, "commit", "-q", "-m", subject)
    return _git(wt, "rev-parse", "HEAD")


def test_a_planted_unlanded_commit_is_NAMED_and_a_pushed_one_is_KEPT(repo, tmp_path):
    """Both arms of the partition in one control: a guard that called EVERY worktree at risk, or
    none, fails one of the two asserts.

    MUTATION (must fire): drop `--not --remotes` from the count -> the kept worktree is at risk.
    MUTATION (must fire): `n == 0` -> `True` -> the planted commit is never named.
    """
    wt = tmp_path / "wt"
    sha = _plant(repo, wt, "SPINE_1 finished and never landed")
    (wt / ".se_worktree_owner").write_text("4242\n")
    _git(repo, "worktree", "lock", "--reason", "seat landing awaiting promotion", str(wt))
    kept = tmp_path / "kept"
    _git(repo, "worktree", "add", "-q", "--detach", str(kept), "origin/main")

    c = u.census(repo)

    assert c["available"] is True and c["worktrees"] == 3
    [row] = c["at_risk"]
    assert row["path"] == str(wt) and row["unlanded"] == 1
    assert row["commits"][0]["sha"] == sha
    assert row["locked"] and row["lock_reason"] == "seat landing awaiting promotion"
    assert row["owner"] == "4242"
    assert c["unknown"] == []

    text = seat._prompt({"unlanded_worktree_commits": c})
    assert sha[:12] in text and "SPINE_1 finished and never landed" in text
    assert str(wt) in text and "owner=4242" in text


def test_a_commit_PUSHED_to_any_branch_is_kept_even_though_it_never_reached_main(repo, tmp_path):
    """The loss question is "is it on a remote ref", not "is it on origin/main".

    MUTATION (must fire): `--not --remotes` -> `--not origin/main` -> this row reads at risk.
    """
    wt = tmp_path / "wt"
    _plant(repo, wt, "pushed to a side branch")
    _git(wt, "push", "-q", "origin", "HEAD:refs/heads/side")
    _git(repo, "fetch", "-q", "origin")

    assert u.census(repo)["at_risk"] == []


def test_an_UNREADABLE_worktree_prints_as_UNKNOWN_never_as_absent(repo, tmp_path):
    """Fail closed. The worktree's directory is gone but git still lists it -- exactly the state
    a hand `rm -rf` leaves -- and the row must say it could not be read.

    MUTATION (must fire): skip rows whose directory is missing -> `unknown` is empty and the
    rendered text claims every worktree was read.
    """
    wt = tmp_path / "wt"
    _plant(repo, wt, "lost")
    shutil.rmtree(wt)

    c = u.census(repo)

    assert [r["path"] for r in c["unknown"]] == [str(wt)]
    text = u.render(c)
    assert "UNKNOWN" in text and "NO WORKTREE HOLDS" not in text


def test_a_census_that_cannot_run_is_UNAVAILABLE_not_empty(tmp_path):
    """Outside any repository `worktree list` fails; the brief must not read that as all clear."""
    c = u.census(tmp_path)

    assert c["available"] is False
    assert "NOT what this says" in seat._prompt({"unlanded_worktree_commits": c})
