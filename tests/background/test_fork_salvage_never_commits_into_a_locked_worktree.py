"""A locked worktree is never salvaged; its unlocked twin still is.

Defect named: on 2026-11-20 fork_salvage committed `SALVAGE(auto)` inside the LOCKED, pinned run tree
/var/tmp/value-test-cut012, its diff left the pin, and the replication refused to start (exit 5).
The twin test is the control that the guard can be taken the other way: a guard that skipped every
worktree would pass the first test alone.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import fork_salvage


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False)


def _ident(path: Path) -> None:
    _git("config", "user.email", "salvage-test@example.invalid", cwd=path)
    _git("config", "user.name", "Salvage Test", cwd=path)
    _git("config", "commit.gpgsign", "false", cwd=path)


@pytest.fixture
def twins(tmp_path, monkeypatch):
    main = tmp_path / "repo"
    main.mkdir()
    _git("init", "-b", "main", cwd=main)
    _ident(main)
    (main / "seed.txt").write_text("seed\n")
    _git("add", "-A", cwd=main)
    _git("commit", "--no-verify", "-m", "seed", cwd=main)
    trees = {}
    for name in ("pinned", "twin"):
        wt = tmp_path / f"value-test-{name}"
        _git("worktree", "add", "--detach", str(wt), cwd=main)
        _ident(wt)
        (wt / "seed.txt").write_text(f"ported {name}\n")      # a tracked, uncommitted diff
        (wt / "untracked.txt").write_text("cache\n")           # and an untracked file
        trees[name] = wt
    _git("worktree", "lock", "--reason", "pinned run: value test", str(trees["pinned"]), cwd=main)
    monkeypatch.setattr(fork_salvage, "PROJECT_DIR", main)
    monkeypatch.setattr(fork_salvage, "LOG_PATH", tmp_path / "fork-salvage-log.md")
    monkeypatch.setattr(fork_salvage, "_is_a_live_writers_worktree", lambda _p: False)
    return trees


def _state(wt: Path) -> tuple[str, str, str]:
    return (_git("rev-parse", "HEAD", cwd=wt).stdout,
            _git("diff", "--binary", "HEAD", cwd=wt).stdout,
            _git("status", "--porcelain", "--untracked-files=all", cwd=wt).stdout)


def test_a_locked_worktree_keeps_its_head_and_its_diff(twins):
    before = _state(twins["pinned"])
    summary = fork_salvage.salvage_all()
    assert _state(twins["pinned"]) == before
    skipped = [r for r in summary["results"] if r["action"] == "SKIPPED_LOCKED"]
    assert [Path(r["path"]).resolve() for r in skipped] == [twins["pinned"].resolve()]
    report = fork_salvage.format_report(summary)
    assert "pinned run: value test" in report and str(twins["pinned"].name) in report


def test_its_unlocked_twin_is_still_salvaged(twins):
    head_before = _state(twins["twin"])[0]
    summary = fork_salvage.salvage_all()
    salvaged = [r for r in summary["results"] if r["action"] == "SALVAGED"]
    assert [Path(r["path"]).resolve() for r in salvaged] == [twins["twin"].resolve()]
    assert _state(twins["twin"])[0] != head_before
    assert not fork_salvage.is_dirty(str(twins["twin"]))
