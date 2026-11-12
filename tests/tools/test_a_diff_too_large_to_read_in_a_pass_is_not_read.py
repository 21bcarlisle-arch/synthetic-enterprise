"""The containment diff abstains on a copy too large to read inside one reconcile pass.

MEASURED 2026-11-12. Once the twin sweep stopped voiding itself (bb10c3a5d), the reconciler reached
`stale_copy_verdicts` for the first time in weeks. There `refresh_to_head.diff_held` met
`docs/state/customer_sample.json` (355,758 lines, ~37k changed), and its quadratic diff held the
reconcile-watch pass for over 20 minutes. Nothing else was judged and nothing advanced.

CONTROLS:
  * over the budget, `_diff_held_by_base` answers `None` (unread, nothing established);
  * under the budget, the same copy is still read and held (reachability: the budget does not
    switch the judgement off).

MUTATION: delete the budget guard and the first leg reds (the diff is read and held).
Make the guard unconditional and the second leg reds.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import refresh_to_head as rth


def _run(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), check=True, capture_output=True, timeout=60)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """HEAD holds 40 lines. `origin` changes line 20, and the disk holds that same change."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    lines = ["line {}\n".format(i) for i in range(40)]
    (root / "big.json").write_text("".join(lines))
    _run(root, "add", "big.json")
    _run(root, "commit", "-qm", "base")
    lines[20] = "line 20 changed upstream\n"
    (root / "big.json").write_text("".join(lines))
    _run(root, "commit", "-qam", "upstream")
    _run(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    _run(root, "reset", "-q", "--hard", "HEAD~1")
    (root / "big.json").write_text("".join(lines))
    return root


def test_a_copy_over_the_budget_is_not_read(repo: Path, monkeypatch):
    monkeypatch.setattr(rth, "DIFF_HELD_LINE_BUDGET", 10)
    work = (repo / "big.json").read_text()
    assert rth._diff_held_by_base(repo, "big.json", work, "origin/main") is None, \
        "a copy too large to diff within a pass must abstain, not stall the reconciler"


def test_a_copy_under_the_budget_is_still_read_and_held(repo: Path, monkeypatch):
    monkeypatch.setattr(rth, "DIFF_HELD_LINE_BUDGET", 1000)
    work = (repo / "big.json").read_text()
    assert rth._diff_held_by_base(repo, "big.json", work, "origin/main") is not None, \
        "under the budget the copy's diff is read and found whole in origin"
