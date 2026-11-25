"""A landing that queues for the gate lock gates the base its holder LEFT, not the one it read first.

THE DEFECT (2026-11-25, /var/tmp/longjob-land-se-seat-executor-1795590119.log). The replay read
origin (8d11dcab8), then waited 1,185 s for c355db288's gate, then gated the stale base and lost
the promotion to c355db288. The base is now read with the lock held, and a holder keeps the lock
until its landing has moved the ref.

Each test fakes a holder that moves the base WHILE the landing under test waits for the lock, and
asserts the landing's commit sits on the holder's commit. Mutations that fire:
  * `_land_once` reads HEAD before taking the lock -> the swap loses to the holder (BaseMoved)
  * `replay` keeps the `onto` it was handed       -> its commit's parent is the stale base
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from tools import pre_commit_test_gate as g
from tools import surgical_land as sl

ROOT = Path(__file__).resolve().parents[2]
HOOK = "#!/bin/sh\necho '3 passed in 0.01s'\nexit 0\n"
MSG_HOOK = "#!/bin/sh\nexit 0\n"

#: Takes the lock, signals it holds it, waits long enough for the landing under test to queue,
#: runs the shell command that MOVES THE BASE, and only then releases.
_HOLDER = textwrap.dedent("""
    import subprocess, sys, time
    from pathlib import Path
    from tools.pre_commit_test_gate import LandingGateLock
    with LandingGateLock("fake holder", Path(sys.argv[1]), poll_s=0.05):
        Path(sys.argv[2]).write_text("held")
        time.sleep(1.5)
        subprocess.run(sys.argv[3], shell=True, check=True)
""")


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args} failed: {r.stderr}"
    return r.stdout.strip()


def _repo(path: Path) -> Path:
    (path / "tools" / "git-hooks").mkdir(parents=True)
    _git(path.parent, "init", "-q", "-b", "main", str(path))
    _git(path, "config", "user.email", "t@example.com")
    _git(path, "config", "user.name", "T")
    (path / "tools" / "git-hooks" / "pre-commit").write_text(HOOK)
    (path / "tools" / "git-hooks" / "commit-msg").write_text(MSG_HOOK)
    (path / "code.py").write_text("VALUE = 1\n")
    (path / "other.txt").write_text("base\n")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "base")
    return path


def _hold_and_move(tmp: Path, lock: Path, cmd: str) -> subprocess.Popen:
    flag = tmp / "held.flag"
    p = subprocess.Popen([sys.executable, "-c", _HOLDER, str(lock), str(flag), cmd],
                         cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True)
    end = time.time() + 30
    while not flag.exists():
        assert time.time() < end and p.poll() is None, p.communicate()[0]
        time.sleep(0.02)
    return p


@pytest.fixture()
def lock(tmp_path, monkeypatch) -> Path:
    path = tmp_path / "gate.lock"
    monkeypatch.setenv(g.LANDING_GATE_LOCK_ENV, str(path))
    monkeypatch.setattr(sl, "announce_landing", lambda *a, **k: None)
    return path


def test_a_landing_that_waits_gates_the_commit_its_holder_landed(tmp_path, lock, capsys):
    repo = _repo(tmp_path / "repo")
    (repo / "code.py").write_text("VALUE = 2\n")
    holder = _hold_and_move(tmp_path, lock, (
        "cd {} && echo holder > other.txt && git commit -q -m holder -- other.txt".format(repo)))
    try:
        sha = sl.land(repo, ["code.py"], "mine: VALUE becomes 2", attempts=1)
    finally:
        out = holder.communicate(timeout=60)[0]
    holders = _git(repo, "rev-parse", sha + "^")
    assert _git(repo, "log", "-1", "--format=%s", holders) == "holder", out
    # The waiting branch was TAKEN, so the property was asked of a real wait, not a free lock.
    assert "another landing gate is running" in capsys.readouterr().out
    assert _git(repo, "show", sha + ":other.txt") == "holder"


def test_a_replay_that_waits_builds_on_the_origin_its_holder_pushed(tmp_path, lock, capsys):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = _repo(tmp_path / "seed")
    _git(seed, "push", "-q", str(origin), "main")
    wt, colleague = tmp_path / "wt", tmp_path / "colleague"
    for clone in (wt, colleague):
        _git(tmp_path, "clone", "-q", str(origin), clone.name)
        _git(clone, "config", "user.email", "t@example.com")
        _git(clone, "config", "user.name", "T")
    (wt / "code.py").write_text("VALUE = 2\n")
    sl.land(wt, ["code.py"], "mine: VALUE becomes 2")

    def push(text: str) -> str:
        (colleague / "other.txt").write_text(text)
        _git(colleague, "commit", "-q", "-am", text)
        _git(colleague, "push", "-q", "origin", "main")
        return _git(colleague, "rev-parse", "HEAD")

    stale = push("first")
    _git(wt, "fetch", "-q", "origin")
    # The holder's landing reaches origin, and this worktree's tracking ref, inside its hold --
    # the order `bounded_landing.promote_until_landed` now keeps.
    holder = _hold_and_move(tmp_path, lock, (
        "cd {c} && echo second > other.txt && git commit -q -am second && "
        "git push -q origin main && cd {w} && git fetch -q origin").format(c=colleague, w=wt))
    try:
        sha = sl.replay(wt, stale)
    finally:
        holder.communicate(timeout=60)
    moved = _git(wt, "rev-parse", "refs/remotes/origin/main")
    assert moved != stale
    assert _git(wt, "rev-parse", sha + "^") == moved
    assert _git(wt, "show", sha + ":code.py") == "VALUE = 2"
    said = capsys.readouterr().out
    assert "another landing gate is running" in said
    assert "while this landing waited for the gate lock" in said
