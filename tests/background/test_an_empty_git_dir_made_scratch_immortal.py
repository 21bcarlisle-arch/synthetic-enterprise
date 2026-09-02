"""A CONTROL THAT FIRES CORRECTLY AND DOES NOTHING.

2026-09-02. `/tmp` sat at 89% of a 12 GB tmpfs — which on this box is RAM — while the month's
largest red (830 tests, 760 of them `OSError`) was an environmental failure on that filesystem.
`disk_headroom.observe()` was running, had correctly banded the box as PRESSURE, and had called its
own reaper. The reaper's verdict, in the live state file:

    "reaped": "nothing reapable (all scratch in use or within TTL)"

It was not true. `/tmp/hc2` was 232 MB and 40 hours old, and `/var/tmp/head-verify-4161726` was
146 MB and **450 hours** old — nineteen days. Both were spared by one line:

    if (path / ".git").exists():
        continue

The exclusion's stated reason is sound: *"a registered worktree, a clone, or a gate checkout can
hold committed branches or uncommitted edits that exist nowhere else."* **Nothing ever checked
whether it was true of the directory in front of it.** Both of those `.git` directories held ZERO
refs and no resolvable HEAD. An empty `.git` made 378 MB immortal, indefinitely, while the alarm
that exists to prevent exhaustion reported it had nothing to do.

The repair evaluates the reason instead of assuming it, in the one direction that is safe, and every
other outcome still spares. The failure direction of the module is unchanged: uncertainty keeps.
"""
from __future__ import annotations

import inspect
import os
import subprocess
import time
from pathlib import Path

import pytest

from background import disk_headroom as dh

OLD = 200 * 3600          # comfortably past REPO_COPY_TTL


@pytest.fixture
def scratch(tmp_path):
    return tmp_path


def _repo_copy(root: Path, name: str, *, age_s: float = OLD, signature=None) -> Path:
    p = root / name
    for rel in (signature if signature is not None else dh.REPO_SIGNATURE):
        f = p / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")
    stamp = time.time() - age_s
    os.utime(p, (stamp, stamp))
    return p


def _reapable_names(root: Path) -> set[str]:
    return {Path(v["path"]).name for v in dh.repo_copy_scratch(roots=(root,), project_dir=root / "nope")}


# ── THE HOLE ────────────────────────────────────────────────────────────────────────────────
def test_an_empty_git_directory_no_longer_makes_scratch_immortal(scratch):
    """THE LIVE DEFECT, in one assertion. 378 MB across two directories, one of them nineteen
    days old, spared forever by a `.git` holding nothing.

    MUTATION: restore `if (path / ".git").exists(): continue` and this fails.
    """
    plain = _repo_copy(scratch, "plain_stem")
    empty_git = _repo_copy(scratch, "stem_with_empty_git")
    # A READABLE repository holding nothing — which is exactly what both live victims were:
    # `git --git-dir` opened them, `for-each-ref` returned nothing, HEAD did not resolve.
    subprocess.run(["git", "init", "-q", str(empty_git)], check=True, capture_output=True)
    stamp = time.time() - OLD
    os.utime(empty_git, (stamp, stamp))

    assert dh._git_dir_may_hold_work(empty_git / ".git") is False
    found = _reapable_names(scratch)
    assert plain.name in found, "the pre-existing behaviour must be unchanged"
    assert empty_git.name in found, "an empty .git holds nothing and cannot be what the guard protects"


# ── AND EVERY OTHER OUTCOME STILL SPARES ────────────────────────────────────────────────────
def test_a_git_dir_with_a_real_commit_is_still_spared(scratch):
    """The exclusion's whole purpose, and it must survive intact: a copy holding a commit that may
    exist nowhere else is never reaped, at any age.

    MUTATION: return False unconditionally from `_git_dir_may_hold_work` and this fails — and real
    work gets deleted, which is the only irreversible mistake available in this module.
    """
    real = _repo_copy(scratch, "stem_with_real_repo")
    subprocess.run(["git", "init", "-q", str(real)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(real), "add", "CLAUDE.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(real), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "held"], check=True, capture_output=True)
    stamp = time.time() - OLD
    os.utime(real, (stamp, stamp))
    assert real.name not in _reapable_names(scratch)


def test_a_git_dir_holding_only_refs_is_spared(scratch):
    """Refs without a checked-out HEAD are still committed work. Either leg keeps it."""
    p = _repo_copy(scratch, "refs_only")
    subprocess.run(["git", "init", "-q", str(p)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(p), "add", "CLAUDE.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "held"], check=True, capture_output=True)
    (p / ".git" / "HEAD").write_text("ref: refs/heads/nonexistent\n")
    assert dh._git_dir_may_hold_work(p / ".git") is True


def test_a_dot_git_FILE_is_a_linked_worktree_and_is_never_our_business(scratch, monkeypatch):
    """A `.git` FILE is a pointer; the real gitdir is elsewhere and its work belongs to
    `fork_reconciler`, which this reaper must not pre-empt.

    THE PROBE IS STUBBED TO SAY "EMPTY" ON PURPOSE. Deleting the `is_dir()` branch first appeared
    to be an EQUIVALENCE — `git --git-dir=<a file>` fails, the returncode path returns True, and
    the directory is spared anyway. That is true today and rests on git's behaviour rather than on
    this module's intent, so a future git that tolerated the argument would silently remove the
    protection. Forcing the probe to return an empty repository makes the branch load-bearing:
    with it, a pointer is spared because it is a POINTER; without it, only because git happened to
    complain.
    """
    p = _repo_copy(scratch, "linked_worktree")
    (p / ".git").write_text("gitdir: /somewhere/else/.git/worktrees/x\n")

    class _Empty:
        returncode = 0
        stdout = ""

    monkeypatch.setattr(dh.subprocess, "run", lambda *a, **k: _Empty())
    assert dh._git_dir_may_hold_work(p / ".git") is True
    assert p.name not in _reapable_names(scratch)


def test_an_unaskable_git_dir_is_spared(scratch, monkeypatch):
    """FAIL-CLOSED. If the probe cannot run at all, we did not establish emptiness — and a probe
    that took the reaper down would be worse than one that spared.

    MUTATION: let the exception escape and this fails with the raised error instead.
    """
    p = _repo_copy(scratch, "unaskable")
    (p / ".git").mkdir()

    def _boom(*a, **k):
        raise OSError("git is gone")

    monkeypatch.setattr(dh.subprocess, "run", _boom)
    assert dh._git_dir_may_hold_work(p / ".git") is True
    assert p.name not in _reapable_names(scratch)


def test_no_git_at_all_is_unaffected(scratch):
    p = _repo_copy(scratch, "no_git")
    assert dh._git_dir_may_hold_work(p / ".git") is False


def test_a_git_dir_git_cannot_READ_is_still_spared_and_that_boundary_is_deliberate(scratch):
    """THE BOUNDARY OF THE REPAIR, stated rather than discovered later.

    A `.git` that is not a readable repository at all — an empty directory, a half-copied one —
    still spares its parent. `for-each-ref` fails, and a failure to ask is not an answer.

    That IS a residual hole: such a directory is junk by every available measure. It is left
    because the two live victims were both READABLE-and-empty, so widening past the measured case
    would be trading a bounded blindness for the one irreversible mistake this module can make. If
    an unreadable `.git` ever shows up holding real space, that is the evidence to widen on.
    """
    p = _repo_copy(scratch, "unreadable_git")
    (p / ".git").mkdir()          # no HEAD, no config -- not a repository
    assert dh._git_dir_may_hold_work(p / ".git") is True
    assert p.name not in _reapable_names(scratch)


# ── the failure direction of the module is unchanged ────────────────────────────────────────
def test_a_young_copy_is_still_spared_however_empty_its_git(scratch):
    """TTL is untouched: a probe that is still running is not abandoned."""
    p = _repo_copy(scratch, "young", age_s=60)
    (p / ".git").mkdir()
    assert p.name not in _reapable_names(scratch)


def test_a_directory_in_use_is_still_spared(scratch, monkeypatch):
    p = _repo_copy(scratch, "in_use")
    (p / ".git").mkdir()
    monkeypatch.setattr(dh, "in_use_dirs", lambda: {str(p.resolve())})
    assert p.name not in _reapable_names(scratch)


def test_identification_is_still_positive_only(scratch):
    """A directory that is not recognisably a copy of this repo is never a candidate, however old
    and however large. STATED AS A KNOWN GAP: `_is_repo_copy` requires ALL FOUR signature files, so
    a PARTIAL copy is invisible to this reaper at any age — `/tmp/chase` was 128 MB and 105 hours
    old and was plausibly one. Loosening the signature would trade a bounded blindness for an
    unbounded risk of deleting real work, so it is left alone and filed rather than widened."""
    partial = _repo_copy(scratch, "partial", signature=dh.REPO_SIGNATURE[:2])
    assert partial.name not in _reapable_names(scratch)


def test_the_reaper_says_which_rule_found_each_victim():
    """`kind` distinguishes the name list from the content check, so the receipt says which
    identification rule fired — the two are deliberately different things."""
    src = inspect.getsource(dh.repo_copy_scratch)
    assert '"kind": "repo-copy"' in src


# ── and the census's own temp roots ──────────────────────────────────────────────────────────
def test_the_census_puts_pytest_temp_on_real_disk_not_the_tmpfs():
    """The largest lever, and the census already made this argument for its SUBJECT and not for
    its scratch: `/tmp` is a 12 GB tmpfs on a 24 GB box, and an unscoped run of ~24,000 tests wrote
    every `tmp_path` into RAM. `tests/background/conftest.py` has four autouse fixtures each taking
    `tmp_path`, which is why 820 of the 830 reds were in that one directory.

    MUTATION: drop the `TMPDIR` line and this fails.
    """
    from tools import head_green_census as census
    src = inspect.getsource(census.run_suite)
    assert 'env.setdefault("TMPDIR"' in src
    assert "HEAD_CHECKOUT_ROOT" in src, "it must land where the subject already does, not /tmp"
    assert "env=env" in src, "setting it without passing it would be the same defect one line down"
