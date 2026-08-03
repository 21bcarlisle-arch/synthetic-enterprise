"""H10 -- the UNMERGED-WORK draw guard, and the R15 mutation proving it can FAIL.

WHY THIS EXISTS (2026-07-30). The dispatch draw was blind to work in flight three consecutive
ticks. Two prior attempts to stop it both depended on someone VOLUNTARILY writing a file:
  * `_build_in_progress_ids` reads `.build_in_progress.json`, written by the orchestrator at
    dispatch -- on 2026-07-30 that file was `{}` while five forks held 4,270 uncommitted lines;
  * `.forks_in_flight.json`, a JSON record written to fix the same bug, went unread by the very
    next tick and had literally predicted its own decay in its `caveat` field.
The consequence was TWO independent implementations of SITE_EH1 (818 and 836 lines), neither
fork aware of the other, plus ~4,270 lines that came within one `git worktree prune` of loss.

The guard under test reads GIT REALITY instead -- a branch with commits not in the trunk, or a
dirty worktree, is a FACT of the repo that cannot be forgotten. These tests build a REAL
throwaway git repo in tmp_path (never the live tree) so the guard is exercised against actual
git output rather than a mock of it.

R15: the mutation test (`test_MUTATION_...`) removes the guard's signal and asserts the rival
atom IS re-drawn -- so a regression that neutralises this control fails a test instead of
silently returning to the double-dispatch behaviour.
"""
from __future__ import annotations

import subprocess

import pytest

from background import supervisor


def _run(args, cwd):
    subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path):
    """A real git repo whose state reproduces the 2026-07-30 pathology:
    trunk `main`, plus an unmerged branch that already rebuilt `site/index.html`."""
    root = tmp_path / "repo"
    root.mkdir()
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "t@t.t"], root)
    _run(["git", "config", "user.name", "t"], root)
    (root / "site").mkdir()
    (root / "site" / "index.html").write_text("<h1>original</h1>")
    (root / "sim").mkdir()
    (root / "sim" / "engine.py").write_text("x = 1\n")
    _run(["git", "add", "-A"], root)
    _run(["git", "commit", "-m", "base"], root)
    # the rival fork: a branch that ALREADY built site/index.html and never came home
    _run(["git", "checkout", "-b", "worktree-agent-rival"], root)
    (root / "site" / "index.html").write_text("<h1>segment disclosure built here</h1>")
    _run(["git", "commit", "-am", "SITE_EH1: segment disclosure"], root)
    _run(["git", "checkout", "main"], root)
    return root


# The two atoms are the LITERAL 2026-07-30 draw: one collides with the rival branch's work,
# one is genuinely free. file_scope values copied from the real maturity map.
_EH1_SCOPE = {"id": "SITE_EH1_segment_disclosure",
              "file_scope": ["site/company/", "site/index.html",
                             "tools/generate_dashboard_data.py"]}
_W1_6B_SCOPE = {"id": "W1_6b_merit_order_reconstruction", "file_scope": ["sim", "tests/sim"]}


def test_unmerged_branch_work_is_detected_from_git(repo):
    paths = supervisor._unmerged_work_paths(root=repo)
    assert "site/index.html" in paths, (
        f"a branch with commits not in main carries unmerged work; got {sorted(paths)}")


def test_dirty_worktree_counts_as_in_flight_even_with_zero_commits(repo, tmp_path):
    """The state that nearly lost 4,270 lines: work sitting UNCOMMITTED in a live worktree.
    Zero commits on the branch, so branch-diffing alone would miss it entirely."""
    wt = tmp_path / "live_fork"
    _run(["git", "worktree", "add", "-b", "worktree-agent-live", str(wt)], repo)
    (wt / "sim" / "flex.py").write_text("# 1,000 uncommitted lines of a real build\n")
    paths = supervisor._unmerged_work_paths(root=repo)
    assert "sim/flex.py" in paths, (
        f"an uncommitted edit in a live worktree is in-flight work; got {sorted(paths)}")


def test_collision_is_directory_aware_in_both_directions():
    """file_scope mixes granularities, so containment must work both ways."""
    unmerged = frozenset({"site/index.html"})
    # scope entry IS the changed file
    assert supervisor._atom_collides_with_unmerged(_EH1_SCOPE, unmerged)
    # scope entry is a DIRECTORY containing the changed file (SITE1_expert_doors: scope ['site'])
    assert supervisor._atom_collides_with_unmerged({"file_scope": ["site"]}, unmerged)
    # a disjoint scope must NOT collide -- the guard has to stay narrow or it zeroes the draw
    assert not supervisor._atom_collides_with_unmerged(_W1_6B_SCOPE, unmerged)
    # a near-miss prefix is NOT a collision (`site_archive` is not inside `site`)
    assert not supervisor._atom_collides_with_unmerged(
        {"file_scope": ["site_archive"]}, unmerged)


def test_undeclared_scope_is_never_newly_excluded():
    """An atom with no declared file_scope already fails closed for CONCURRENT grants; this
    guard must not make the single-atom draw stricter than it was."""
    assert not supervisor._atom_collides_with_unmerged(
        {"id": "no_scope"}, frozenset({"site/index.html"}))


def test_guard_deprioritises_the_rival_and_keeps_the_free_atom(repo, monkeypatch, tmp_path):
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "PROJECT_DIR", repo)
    kept = supervisor._prefer_unmerged_free([dict(_EH1_SCOPE), dict(_W1_6B_SCOPE)])
    ids = [a["id"] for a in kept]
    assert ids == ["W1_6b_merit_order_reconstruction"], (
        "the atom whose scope overlaps the rival branch must be deprioritised, the free one kept; "
        f"got {ids}")


def test_MUTATION_guard_without_git_signal_redraws_the_rival(repo, monkeypatch, tmp_path):
    """R15: prove this control CAN FAIL -- neutralise its signal (exactly what the marker-file
    guard did when `.build_in_progress.json` was `{}`) and the rival atom is handed out again.
    If a future change breaks the guard, this asserts the old double-dispatch behaviour returns,
    so the guard's value is measured rather than assumed."""
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "_unmerged_work_paths", lambda *a, **k: frozenset())
    kept = supervisor._prefer_unmerged_free([dict(_EH1_SCOPE), dict(_W1_6B_SCOPE)])
    assert [a["id"] for a in kept] == ["SITE_EH1_segment_disclosure",
                                       "W1_6b_merit_order_reconstruction"], (
        "with no git signal the guard must fall open to the FULL set -- this is the failure mode "
        "the marker-based guard exhibited, and the reason this one reads git instead")


def test_RULE_0_all_colliding_candidates_still_draw(repo, monkeypatch, tmp_path):
    """A guard must never zero the feasible set (Rule 0). When every candidate overlaps
    unmerged work, the full set is returned rather than false exhaustion."""
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "PROJECT_DIR", repo)
    only_colliding = [dict(_EH1_SCOPE), {"id": "SITE1_expert_doors", "file_scope": ["site"]}]
    kept = supervisor._prefer_unmerged_free(only_colliding)
    assert len(kept) == 2, f"an all-colliding set must survive intact; got {kept}"


def test_FAIL_OPEN_on_broken_git_never_stalls_the_draw(monkeypatch, tmp_path):
    """An unreadable repo must yield no exclusion, not an exception and not an empty draw."""
    monkeypatch.setattr(supervisor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path / "definitely_not_a_repo")
    assert supervisor._unmerged_work_paths(root=tmp_path / "definitely_not_a_repo") == frozenset()
    kept = supervisor._prefer_unmerged_free([dict(_EH1_SCOPE)])
    assert [a["id"] for a in kept] == ["SITE_EH1_segment_disclosure"]


def test_trunk_is_resolved_not_hardcoded(tmp_path):
    """R15 fail-silent: on a checkout whose trunk is not called `main`, hardcoding `main` would
    make every rev-list error and the guard would fail-open completely and silently."""
    root = tmp_path / "master_repo"
    root.mkdir()
    _run(["git", "init", "-b", "master"], root)
    _run(["git", "config", "user.email", "t@t.t"], root)
    _run(["git", "config", "user.name", "t"], root)
    (root / "site").mkdir()
    (root / "site" / "index.html").write_text("original")
    _run(["git", "add", "-A"], root)
    _run(["git", "commit", "-m", "base"], root)
    _run(["git", "checkout", "-b", "rival"], root)
    (root / "site" / "index.html").write_text("rebuilt")
    _run(["git", "commit", "-am", "rival work"], root)
    _run(["git", "checkout", "master"], root)
    assert "site/index.html" in supervisor._unmerged_work_paths(root=root)
