"""A diverged tree cannot fast-forward for a reason no working-tree path can express.

THE DEFECT, measured on the live shared tree 2026-09-05 while the seat held Lane 0. `fork_state`
answered `behind 32, ahead 5`, and `git merge --ff-only origin/main` refused with a sentence this
module had never read:

    hint: Diverging branches can't be fast-forwarded

`paths_blocking_fast_forward` was asked the same question and answered with EIGHTEEN paths -- and
not one of them was the cause. Fourteen of those eighteen already hashed equal to origin's blob.
Four did not, so the all-or-nothing guard refused and no harm was done that day. But the guard
refused for the wrong reason, and the state it was one non-twin away from is the state the twin
sweep exists to produce: had those four been cleared or landed by the lanes holding them, this
would have taken the tree lock, unlinked fourteen files, and then failed the second `--ff-only`
exactly as it failed the first.

That is the module's OWN named worst case -- *"a deletion bought for no advance, the one shape in
which this could actually cost someone something"* -- reached through the door its guard was not
watching. The all-or-nothing property was only ever quantified over dirty-tree collisions, and
divergence is not one.

WHY IT IS NOT HYPOTHETICAL. `reconcile` reads `ahead` once at the top, then merges in an isolated
worktree, gates that merge, and pushes it before calling the advance -- minutes, bounded by
`MERGE_TIMEOUT_SECONDS`. Several sessions and daemons commit into this one shared tree throughout.
A tree that was level when `reconcile` looked is routinely diverged by the time the advance runs.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_a_diverged_tree_clears_nothing_even_when_every_blocker_is_a_twin` -- the defect itself,
    in the exact shape that costs files.
  * `test_the_divergence_refusal_names_divergence_and_not_a_path` -- the refusal has to send the
    next reader at the fork, not at innocent paths.
  * `test_an_unreadable_ahead_count_clears_nothing` -- fail-closed on the new door.
  * `test_a_level_tree_still_clears_its_twins_and_advances` -- REACHABILITY. A guard keyed to the
    condition that selects the route would make the route unreachable, and would pass every
    refusal test above while doing so.
  * `test_the_divergence_question_is_asked_before_anything_is_cleared` -- the ordering control. The
    two orders give genuinely different answers: asked first, nothing is removed; asked after the
    clearing loop, the twins are already gone.
  * `test_the_default_ahead_seam_is_the_modules_own_commits_ahead` -- the guard must read git
    through the seam `reconcile` already trusts, not a constant this test controls.
"""
from __future__ import annotations

import contextlib
import subprocess

from background import origin_reconcile as orc

_DIVERGED = "hint: Diverging branches can't be fast-forwarded, you need to either:"


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


class _Advance:
    """The real `advance_shared_tree` with both destructive edges and the ahead count injected.

    `removed` and `restored` stay separate for the same reason the twin-sweep harness keeps them
    apart: the two kinds are cleared by different acts, and one combined list could not tell a
    correct repair from one that unlinked a tracked path.
    """

    def __init__(self, ff_results, blocking, twins=(), tracked=(), ahead=0):
        self.ff_results = list(ff_results)
        self.blocking = blocking
        self.twins = twins
        self.tracked = tracked
        self.ahead = ahead
        self.removed: list[str] = []
        self.restored: list[str] = []
        self.blockers_asked = 0
        self.ff_calls = 0

    def _ff(self):
        self.ff_calls += 1
        return self.ff_results.pop(0)

    def _blockers(self, _project):
        self.blockers_asked += 1
        return self.blocking

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=self._blockers,
            twins_fn=lambda _project, _blocking: (
                None if self.twins is None else list(self.twins)),
            tracked_twins_fn=lambda _project, _blocking: (
                None if self.tracked is None else list(self.tracked)),
            ff_fn=self._ff,
            remover=self.removed.append,
            restorer=lambda path: self.restored.append(path),
            locker=contextlib.nullcontext,
            ahead_fn=lambda _project: self.ahead,
        )


def test_a_diverged_tree_clears_nothing_even_when_every_blocker_is_a_twin():
    """THE DEFECT. Every blocking path is byte-identical to origin -- the all-or-nothing test
    passes, which is precisely what makes this dangerous -- but the tree has diverged, so the
    fast-forward was never available and clearing them buys nothing.

    Before the guard, this unlinked two files and restored one under the tree lock and then
    reported `advanced: False` with a reason blaming a collision that was not the cause.

    MUTATION: delete the `if ahead:` branch and the run falls through to the clearing loop, so
    `removed`/`restored` come back non-empty and the first two assertions red.
    """
    notes = ["docs/staging/SEAT_FINDING_A.md", "docs/staging/SEAT_FINDING_B.md"]
    staged = "background/origin_reconcile.py"
    run = _Advance(ff_results=[_completed(1, _DIVERGED)],
                   blocking=[_untracked(n) for n in notes] + [_modified(staged)],
                   twins=notes, tracked=[staged], ahead=5)
    adv = run.run()

    assert run.removed == [] and run.restored == [], \
        "a diverged tree cannot fast-forward whatever the working tree holds, so clearing these " \
        "would have deleted files and still not advanced -- got removed={}, restored={}".format(
            run.removed, run.restored)
    assert adv["cleared"] == [], \
        "nothing was cleared, so the report must not claim otherwise -- got {}".format(
            adv["cleared"])
    assert adv["advanced"] is False, \
        "the advance did not happen and is never inferred from the absence of an error"
    assert run.ff_calls == 1, \
        "the second fast-forward must never be attempted: nothing changed between the two, so a " \
        "retry is a wasted git invocation on a state already known to refuse"


def test_the_divergence_refusal_names_divergence_and_not_a_path():
    """A refusal that named the blocking paths here would send the next reader to isolate hunks on
    files that are not the cause, which is exactly how the 2026-09-05 tree lost 22 commits of
    ground: `--check` reported the fork every five minutes and named innocent paths every time.

    KEYED TO THE WHOLE CLAUSE, not to the word "diverged" alone -- the count is what tells a reader
    the fork is theirs to close, and the remedy names the leg that closes it.

    MUTATION: reuse the generic collision wording (`"NOTHING local collides with what origin
    brings"`) for this branch and the `DIVERGED` and count assertions red.
    """
    run = _Advance(ff_results=[_completed(1, _DIVERGED)],
                   blocking=[_untracked("docs/staging/SEAT_FINDING_A.md")],
                   twins=["docs/staging/SEAT_FINDING_A.md"], ahead=5)
    reason = run.run()["reason"]

    assert "DIVERGED" in reason, \
        "the reason must name the cause it found, not the collision it did not: {}".format(reason)
    assert "5 local commit(s)" in reason, \
        "the count is the actionable half -- it tells the reader how much of this fork is theirs " \
        "to land: {}".format(reason)
    assert "origin_reconcile" in reason, \
        "a refusal that names its reason should hand over the command that addresses it: " \
        "{}".format(reason)
    assert "SEAT_FINDING_A" not in reason, \
        "naming the blocking paths here would point the reader at files that are NOT the cause, " \
        "which is the misdirection this control exists to prevent: {}".format(reason)


def test_an_unreadable_ahead_count_clears_nothing():
    """FAIL-CLOSED ON THE NEW DOOR. `commits_ahead` returns None when git could not be read, and
    every other comparison in this module already refuses on an unread answer rather than assuming
    the flattering one.

    MUTATION: treat `None` as zero (`if ahead:` alone, with the `is None` branch deleted) and the
    run proceeds to clear on a question nobody answered, so both assertions red.
    """
    note = "docs/staging/SEAT_FINDING_A.md"
    run = _Advance(ff_results=[_completed(1, "would be overwritten")],
                   blocking=[_untracked(note)], twins=[note], ahead=None)
    adv = run.run()

    assert run.removed == [] and adv["cleared"] == [], \
        "whether this tree has diverged was not established, so no file may be deleted on it -- " \
        "got removed={}".format(run.removed)
    assert "could not be established" in adv["reason"], \
        "the refusal must say the question went unanswered, not invent a cause: {}".format(
            adv["reason"])


def test_a_level_tree_still_clears_its_twins_and_advances():
    """REACHABILITY, and it is the control the other three cannot substitute for. A guard that
    refused EVERY tree would pass every refusal test above -- and would silently retire the twin
    sweep this module exists for, which has already never once fired in production.

    MUTATION: make the guard unconditional (`if ahead is not None:` refusing) and this reds while
    every refusal test above stays green.
    """
    notes = ["docs/staging/SEAT_FINDING_A.md", "docs/staging/SEAT_FINDING_B.md"]
    staged = "background/origin_reconcile.py"
    run = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                   blocking=[_untracked(n) for n in notes] + [_modified(staged)],
                   twins=notes, tracked=[staged], ahead=0)
    adv = run.run()

    assert adv["advanced"] is True, \
        "the tree was level with origin and every blocker was a twin, so the advance had nothing " \
        "to lose and must go through: {}".format(adv["reason"])
    assert sorted(run.removed) == sorted(notes) and run.restored == [staged], \
        "the untracked notes must be REMOVED and the tracked file RESTORED -- got removed={}, " \
        "restored={}".format(run.removed, run.restored)


def test_the_divergence_question_is_asked_before_anything_is_cleared():
    """THE ORDERING CONTROL, and the two orders give different answers rather than the same answer
    by a different route. Asked before the clearing loop, a diverged tree loses no files. Asked
    after it -- which is where a "report the true cause" fix would naturally be written, beside the
    second `--ff-only` that already says the collision was not the cause -- the files are gone by
    the time the truth is told, and the report is honest about a tree that has already paid.

    The blocking set is not even consulted: on a diverged tree it enumerates paths that cannot be
    the cause, so asking is misleading work.

    MUTATION: move the `ahead` check below the clearing loop and `blockers_asked`/`removed` both
    come back non-zero, reding both assertions.
    """
    note = "docs/staging/SEAT_FINDING_A.md"
    run = _Advance(ff_results=[_completed(1, _DIVERGED)],
                   blocking=[_untracked(note)], twins=[note], ahead=5)
    run.run()

    assert run.blockers_asked == 0, \
        "a diverged tree's blocking paths are not the cause, so enumerating them sends the reader " \
        "somewhere the fix is not -- it was asked {} time(s)".format(run.blockers_asked)
    assert run.removed == [], \
        "the ordering is the whole property: after the clearing loop this same truth arrives too " \
        "late to save the file"


def test_the_default_ahead_seam_is_the_modules_own_commits_ahead(monkeypatch):
    """The guard must read git through `commits_ahead` -- the seam `reconcile` already trusts to
    decide whether a merge is legitimate at all -- and not through a value the caller supplies.

    Without this, every test above could pass against a guard wired to a constant, and the live
    advance would still clear twins on a diverged tree.

    MUTATION: default `ahead_fn` to `lambda _p: 0` instead of `commits_ahead` and this reds while
    every injected test above stays green.
    """
    note = "docs/staging/SEAT_FINDING_A.md"
    monkeypatch.setattr(orc, "commits_ahead", lambda _project: 7)

    adv = orc.advance_shared_tree(
        blockers_fn=lambda _project: [_untracked(note)],
        twins_fn=lambda _project, _blocking: [note],
        tracked_twins_fn=lambda _project, _blocking: [],
        ff_fn=lambda: _completed(1, _DIVERGED),
        remover=lambda path: pytest_fail_removed(path),
        restorer=lambda path: None,
        locker=contextlib.nullcontext,
    )

    assert "7 local commit(s)" in adv["reason"], \
        "the count in the refusal must come from the module's own `commits_ahead`, which is what " \
        "makes this guard read the real repository: {}".format(adv["reason"])


def pytest_fail_removed(path):
    raise AssertionError(
        "the default seam reported a diverged tree, so nothing may be cleared -- {} was".format(
            path))
