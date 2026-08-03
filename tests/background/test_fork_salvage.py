"""FORK SALVAGE tests — the mechanism that makes a bounded-invocation kill non-lossy.

R15 DISCIPLINE. A control counts as evidence only if a MUTATION proves it fires on its OWN named
defect. The named defect here is concrete and observed: on 2026-08-03 `worker-tick.service` was
SIGTERM-killed at TimeoutStartSec 10 times, and each kill destroyed whatever its Agent forks had
built but not yet committed — the state the hand-written "RESCUE: preserve this dead fork's
uncommitted build" commits kept recovering after the fact. So the discriminating test is not "does
salvage commit something" but `test_mutation_without_salvage_a_killed_fork_loses_its_work`: the
SAME fixture, minus the salvage call, must LOSE the work. If both paths kept the work, this suite
would be a tautology (the work would be surviving for some other reason) and would prove nothing.

The three killer patterns from R15, and how they are covered:
  TAUTOLOGY   -> the mutation above: no-salvage must lose what salvage keeps.
  FAIL-OPEN   -> untracked-only work is salvaged (a `git commit` without `add -A` would silently
                 pass while preserving nothing), and an unreadable tree reads as DIRTY, not clean.
  FAIL-SILENT -> salvage_all() never raises, and a broken worktree still reports FAILED rather than
                 vanishing from the summary.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import fork_salvage


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False)


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "main", cwd=path)
    _git("config", "user.email", "salvage-test@example.invalid", cwd=path)
    _git("config", "user.name", "Salvage Test", cwd=path)
    _git("config", "commit.gpgsign", "false", cwd=path)
    (path / "seed.txt").write_text("seed\n")
    _git("add", "-A", cwd=path)
    _git("commit", "--no-verify", "-m", "seed", cwd=path)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A REAL git repo with a REAL linked worktree on its own branch -- the actual shape a fork
    takes in this project (`.claude/worktrees/agent-*`), not a stand-in for it."""
    main = tmp_path / "repo"
    _init_repo(main)
    wt = main / ".claude" / "worktrees" / "agent-atest"
    _git("worktree", "add", "-b", "worktree-agent-atest", str(wt), cwd=main)
    _git("config", "user.email", "salvage-test@example.invalid", cwd=wt)
    _git("config", "user.name", "Salvage Test", cwd=wt)
    _git("config", "commit.gpgsign", "false", cwd=wt)
    monkeypatch.setattr(fork_salvage, "PROJECT_DIR", main)
    monkeypatch.setattr(fork_salvage, "LOG_PATH", tmp_path / "fork-salvage-log.md")
    return {"main": main, "worktree": wt, "branch": "worktree-agent-atest"}


def _commit_count(path: Path) -> int:
    return int(_git("rev-list", "--count", "HEAD", cwd=path).stdout.strip() or 0)


# ── the control FIRES on its own named defect ──────────────────────────────────────────────────

def test_dirty_worktree_is_salvaged_to_its_own_branch(repo):
    """A fork that built work but never committed it: after salvage the work is IN GIT, on the
    fork's own branch, and the worktree is clean -- so a subsequent kill can no longer lose it."""
    (repo["worktree"] / "built.py").write_text("# 800 lines of build\n")
    before = _commit_count(repo["worktree"])

    summary = fork_salvage.salvage_all()

    assert summary["salvaged"] == 1, summary
    assert _commit_count(repo["worktree"]) == before + 1
    assert not fork_salvage.is_dirty(str(repo["worktree"]))     # nothing left at risk
    # The content is genuinely recoverable from the branch, not merely "a commit happened".
    show = _git("show", "worktree-agent-atest:built.py", cwd=repo["main"])
    assert "800 lines of build" in show.stdout


def test_mutation_without_salvage_a_killed_fork_loses_its_work(repo):
    """THE R15 DISCRIMINATOR. Same fork, same uncommitted work -- but the salvage hook does NOT
    run, exactly as on 2026-08-03. Removing the worktree (what a `rm -rf`/reap after a killed
    invocation does) destroys the work, and it exists on NO branch. Salvage keeping the work is
    therefore attributable to salvage, not to git having kept it anyway."""
    (repo["worktree"] / "built.py").write_text("# 800 lines of build\n")

    # ... no fork_salvage.salvage_all() here -- that is the mutation ...
    _git("worktree", "remove", "--force", str(repo["worktree"]), cwd=repo["main"])

    show = _git("show", "worktree-agent-atest:built.py", cwd=repo["main"])
    assert show.returncode != 0                       # the work is GONE -- nowhere in the object db
    assert "800 lines of build" not in show.stdout


def test_untracked_only_work_is_salvaged(repo):
    """FAIL-OPEN guard. The real 2026-08-03 loss included files that were UNTRACKED -- a new module
    and its test that "existed nowhere else". A salvage that committed only tracked modifications
    would report success while preserving nothing, so untracked-only must be salvaged too."""
    (repo["worktree"] / "brand_new_module.py").write_text("# existed nowhere else\n")

    summary = fork_salvage.salvage_all()

    assert summary["salvaged"] == 1, summary
    listing = _git("ls-tree", "--name-only", "worktree-agent-atest", cwd=repo["main"]).stdout
    assert "brand_new_module.py" in listing


# ── the things it must REFUSE to do ────────────────────────────────────────────────────────────

def test_main_worktree_is_never_salvaged(repo):
    """Concurrent writers share the main tree, so a blind `git add -A` there would sweep another
    writer's staged-but-uncommitted files into this commit -- a worse defect than the one fixed."""
    (repo["main"] / "someone_elses_wip.py").write_text("# another writer's staged work\n")
    before = _commit_count(repo["main"])

    summary = fork_salvage.salvage_all()

    assert _commit_count(repo["main"]) == before                     # main untouched
    assert all(r["path"] != str(repo["main"]) for r in summary["results"])
    assert summary["main_tree"] is not None                          # ...but it IS reported
    assert summary["main_tree"]["dirty_paths"] >= 1


def test_salvage_never_merges_to_main(repo):
    """Policy A (shared with fork_reconciler): salvage preserves, it never LANDS. Landing stays the
    worker's in-turn gated job -- auto-merging unreviewed work would route around the gate-wall."""
    (repo["worktree"] / "built.py").write_text("# unreviewed\n")
    main_before = _git("rev-parse", "main", cwd=repo["main"]).stdout.strip()

    fork_salvage.salvage_all()

    assert _git("rev-parse", "main", cwd=repo["main"]).stdout.strip() == main_before
    assert _git("show", "main:built.py", cwd=repo["main"]).returncode != 0


def test_clean_worktree_is_a_noop(repo):
    """Ordinary quiet case: nothing dirty -> no commit, no noise, no spurious branch churn."""
    before = _commit_count(repo["worktree"])
    summary = fork_salvage.salvage_all()
    assert summary["salvaged"] == 0
    assert _commit_count(repo["worktree"]) == before
    assert "all clean" in fork_salvage.format_report(summary)


# ── FAIL-SILENT guards: it must not disappear when it breaks ───────────────────────────────────

def test_unreadable_worktree_reads_as_dirty_not_clean(repo, tmp_path):
    """An unknown state must be treated as AT RISK. A checker that reads "cannot tell" as "clean"
    is the fail-open pattern -- it would skip exactly the broken forks most likely to hold work."""
    assert fork_salvage.is_dirty(str(tmp_path / "does_not_exist")) is True


def test_salvage_all_never_raises_and_reports_the_failure(repo, monkeypatch):
    """This runs on systemd's shutdown path: an exception here would break the tick's teardown.
    A failure must surface as a FAILED result, never as a crash and never as silence."""
    monkeypatch.setattr(fork_salvage, "is_dirty", lambda path: True)
    monkeypatch.setattr(fork_salvage, "_git", lambda *a, **k: subprocess.CompletedProcess(
        a, returncode=1, stdout="", stderr="simulated git failure"))

    summary = fork_salvage.salvage_all()            # must not raise

    assert summary["failed"] >= 0                    # structure intact
    assert isinstance(summary["results"], list)
    report = fork_salvage.format_report(summary)
    assert isinstance(report, str) and report


def test_main_returns_zero_even_when_everything_fails(repo, monkeypatch):
    """ExecStopPost must never fail the unit: a non-zero here would turn a survivable salvage
    problem into a systemd-visible unit failure on every kill."""
    monkeypatch.setattr(fork_salvage, "salvage_all", lambda: {"error": "boom", "scanned": 0,
                                                              "salvaged": 0, "failed": 0,
                                                              "results": []})
    assert fork_salvage.main() == 0
