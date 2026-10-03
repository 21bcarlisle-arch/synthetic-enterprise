"""A merge's tests are selected by its COMBINED DIFF, not by everything the other side brought.

The defect this names: `pre_commit_test_gate` read `git diff --cached` against HEAD, which for a
base-advancing merge is every path origin landed since the merge-base -- code each side already
gated. 101 of 115 such merges in 48 h (2026-10-03) authored nothing and re-ran ~10 h of pytest.

Two legs, one control, over a real two-parent repo whose paths are this repo's own module names so
`select_targets` resolves them against the real test tree:

  * NON-EMPTY: the merge changes a path to bytes NEITHER parent has -> that path's tests are
    still selected.
  * EMPTY: the merge is the plain union -> nothing is selected, although the first-parent diff
    alone would select the other side's tests (asserted first, so the empty leg cannot pass by
    selecting nothing for everything).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from tools import pre_commit_test_gate as gate
from tools import surgical_land as sl

SUBJECT = "tools/surgical_land.py"        # the other side's change: has tests/tools/test_surgical_land.py
OURS = "tools/live_hook_drift.py"         # this side's change: has tests/tools/test_live_hook_drift.py


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True,
                          text=True, env=sl._gitless_env()).stdout.strip()


def _write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def _two_sides(repo: Path) -> tuple[str, str]:
    """base -> ours (HEAD) and base -> theirs; returns (ours, theirs) and leaves HEAD at ours."""
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _write(repo, SUBJECT, "A = 0\n")
    _write(repo, OURS, "B = 0\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", "theirs")
    _write(repo, SUBJECT, "A = 1\n")
    _git(repo, "commit", "-q", "-am", "theirs")
    theirs = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "main")
    _write(repo, OURS, "B = 1\n")
    _git(repo, "commit", "-q", "-am", "ours")
    return _git(repo, "rev-parse", "HEAD"), theirs


def _stage_union(repo: Path) -> None:
    _write(repo, SUBJECT, "A = 1\n")
    _git(repo, "add", SUBJECT)


def _staged(repo: Path) -> list[str]:
    return _git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACM").split()


def test_a_merge_selects_its_combined_diff_and_nothing_a_parent_already_carried(tmp_path):
    # EMPTY leg. The plain union: the staged diff against HEAD is the other side's work.
    empty = tmp_path / "empty"
    _, theirs = _two_sides(empty)
    _stage_union(empty)
    staged = _staged(empty)
    assert staged == [SUBJECT]
    assert "tests/tools/test_surgical_land.py" in gate.select_targets(staged), (
        "precondition: keyed on the first-parent diff, the other side's tests ARE selected -- "
        "otherwise the empty leg below would pass by selecting nothing for anything")
    selected, why = gate.selection_paths(staged, empty, {gate.MERGE_PARENT_ENV: theirs})
    assert selected == [] and gate.select_targets(selected) == [], (
        f"a merge that authored nothing selected {selected}: {why}")

    # NON-EMPTY leg. The merge writes bytes in SUBJECT that neither parent has.
    full = tmp_path / "full"
    _, theirs = _two_sides(full)
    _write(full, SUBJECT, "A = 2  # resolved to neither side\n")
    _git(full, "add", SUBJECT)
    selected, why = gate.selection_paths(_staged(full), full, {gate.MERGE_PARENT_ENV: theirs})
    assert selected == [SUBJECT], why
    assert "tests/tools/test_surgical_land.py" in gate.select_targets(selected)


def test_a_merge_parent_token_that_is_not_a_merge_selects_everything(tmp_path):
    """The token cannot shrink an ordinary commit. Named against an ANCESTOR of HEAD, a staged
    revert to that ancestor's bytes would read as "already carried"; named as garbage, it means
    nothing. Both fall back to the full staged set -- and with no token at all, so does a merge."""
    repo = tmp_path / "r"
    ours, theirs = _two_sides(repo)
    base = _git(repo, "rev-parse", "HEAD~1")
    _write(repo, OURS, "B = 0\n")          # reverts ours to base's bytes
    _git(repo, "add", OURS)
    staged = _staged(repo)
    assert staged == [OURS]
    for token in (base, "not-a-commit"):
        assert gate.merge_parent(repo, {gate.MERGE_PARENT_ENV: token}) is None
        assert gate.selection_paths(staged, repo, {gate.MERGE_PARENT_ENV: token})[0] == staged
    assert gate.selection_paths(staged, repo, {})[0] == staged
    # ...and the same index named against the genuine other side IS narrowed, so the refusal
    # above is a refusal of the token and not a selector that never narrows.
    assert gate.merge_parent(repo, {gate.MERGE_PARENT_ENV: theirs}) == theirs


def test_surgical_land_hands_the_merge_parent_to_the_hook(tmp_path, monkeypatch):
    """The extract has no MERGE_HEAD, so without this the combined-diff selection is never
    reached on the door every base advance comes through."""
    monkeypatch.delenv(gate.MERGE_PARENT_ENV, raising=False)  # set when THIS runs in a merge's gate
    hook = tmp_path / "hook.sh"
    hook.write_text(f'echo "mp=${gate.MERGE_PARENT_ENV}"\n')
    rc, out, _ = sl.run_gate(tmp_path, "hook.sh", merge_parent="abc123")
    assert rc == 0 and "mp=abc123" in out
    rc, out, _ = sl.run_gate(tmp_path, "hook.sh")
    assert out.strip() == "mp="


def test_the_gate_selects_on_what_selection_paths_returns(monkeypatch):
    """The wiring in `main`: the paths handed to `select_targets` are `selection_paths`'s, not
    the raw staged set. Every structural check is stubbed green -- they are not the subject."""
    for name in dir(gate):
        if name.startswith("_") and name.endswith("_check"):
            monkeypatch.setattr(gate, name, lambda *a, **k: (True, ""))
    monkeypatch.setattr(gate, "staged_files", lambda: [SUBJECT])
    monkeypatch.setattr(gate, "selection_paths", lambda staged: ([], "combined diff is empty"))
    seen: list[list[str]] = []
    monkeypatch.setattr(gate, "select_targets", lambda files: seen.append(list(files)) or [])
    assert gate.main() == 0
    assert seen == [[]]
