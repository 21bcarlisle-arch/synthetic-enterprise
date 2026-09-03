"""`ensure_worktree` must not destroy an untracked artefact beyond recovery.

THE DEFECT THIS NAMES, measured not inferred. On 2026-09-03 a detached
`systemd-run --user` unit (`se-noise-floor-all-20260903b.service`) finished at 15:18:37 and wrote
`docs/observability/value_cycle_ab_s1_noise_floor_20260903.json` into the executor's worktree —
hours after the bounded turn that launched it had exited, which is the whole point of launching a
2h25m measurement detached. At 15:35:25 the next `ensure_worktree` call did `git reset --hard`
followed by `git clean -qfd` and the file was gone: untracked, never added, in no commit and no
object. `find / -xdev` returned nothing.

WHY A CONTROL AND NOT A COMMENT. `-qfd` is silent, and an absent `--out` path is indistinguishable
from a run still in progress — the exact misreading two earlier findings already paid for (the OOM
kill, then the headroom refusal that returned 2 without writing). Both of those fixes are still
correct and neither could catch this one: here the run SUCCEEDED and printed its answer. A rule in
a docstring saying "don't clean away background artefacts" is an exhortation; this is the
mechanism.

WHAT IT ASSERTS, AND WHY THAT SHAPE. Not "the file is still in the working tree" — it should not
be; scratch discipline is right and the reset stays. The property is RECOVERABILITY: after
`ensure_worktree` returns, the bytes must still be reachable from some git object. That is keyed to
the property, not to today's implementation — swap `fork_salvage` for any other preservation route
and this stays green; delete the preservation and it goes red, which is the correct polarity.

MUTATION PROOF: removing the `salvage_worktree(...)` line from `ensure_worktree` turns
`test_an_untracked_artefact_is_recoverable_after_the_reset` red (the blob is unreachable), while
`test_the_working_tree_is_still_reset` stays green — so the two legs are not the same assertion
wearing different names, and the salvage is not silently equivalent to doing nothing.
"""
from __future__ import annotations

import subprocess

import pytest

from background import seat_executor


def _git(*args: str, cwd) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, timeout=60)


@pytest.fixture
def executor_worktree(tmp_path, monkeypatch):
    """A real git repo plus a real linked worktree, pointed at by the module's own globals.

    Real git rather than a mock: the defect IS git's behaviour (`clean -qfd` deletes untracked
    files that `reset --hard` leaves alone), so a fake that stubs the subprocess calls could not
    have reproduced it and could not refute the fix.
    """
    origin = tmp_path / "origin"
    origin.mkdir()
    _git("init", "-q", "-b", "main", cwd=origin)
    _git("config", "user.email", "t@example.com", cwd=origin)
    _git("config", "user.name", "t", cwd=origin)
    (origin / "seed.txt").write_text("seed\n")
    _git("add", "seed.txt", cwd=origin)
    _git("commit", "-q", "-m", "seed", cwd=origin)
    base = _git("rev-parse", "HEAD", cwd=origin).stdout.strip()

    worktree = tmp_path / "wt"
    _git("worktree", "add", "--detach", "-q", str(worktree), base, cwd=origin)

    monkeypatch.setattr(seat_executor, "PROJECT_DIR", origin)
    monkeypatch.setattr(seat_executor, "WORKTREE", worktree)
    return worktree, base


ARTEFACT = "docs/observability/value_cycle_ab_s1_noise_floor_20260903.json"
PAYLOAD = '{"selection_gbp_stdev": 5923.0446, "distinguishable_from_zero": false}\n'


def test_an_untracked_artefact_is_recoverable_after_the_reset(executor_worktree):
    """The 2026-09-03 loss, reproduced: a detached run's artefact lands untracked between turns."""
    worktree, base = executor_worktree
    target = worktree / ARTEFACT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PAYLOAD)

    seat_executor.ensure_worktree(base)

    # The bytes must still exist as a git object. `hash-object` computes the id the content WOULD
    # have; `cat-file -e` then asks whether the repo actually holds it. Absent salvage, it does not.
    proc = subprocess.run(["git", "hash-object", "-t", "blob", "--stdin"],
                          cwd=str(worktree), input=PAYLOAD, capture_output=True,
                          text=True, timeout=60)
    blob = proc.stdout.strip()
    assert blob, "could not compute the blob id for the artefact payload"

    exists = _git("cat-file", "-e", blob, cwd=worktree)
    assert exists.returncode == 0, (
        f"the detached run's artefact ({ARTEFACT}) was destroyed beyond recovery by "
        f"ensure_worktree: blob {blob} is in no git object. An absent artefact reads exactly like "
        f"a run still in progress, which is what makes this silent."
    )


def test_the_working_tree_is_still_reset(executor_worktree):
    """Salvage must not become an excuse to carry scratch forward — the reset still happens.

    This is the leg that keeps the fix honest: without it, 'preserve everything' would pass the
    test above by simply not cleaning, which would reintroduce the tree-the-next-turn-did-not-build
    problem the reset exists to prevent.
    """
    worktree, base = executor_worktree
    target = worktree / ARTEFACT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PAYLOAD)

    seat_executor.ensure_worktree(base)

    assert not target.exists(), (
        "ensure_worktree left the previous turn's untracked scratch in the working tree; the "
        "reset is still required, only the destruction is not."
    )
    head = _git("rev-parse", "HEAD", cwd=worktree).stdout.strip()
    assert head == base, f"worktree HEAD is {head}, expected the requested base {base}"
