"""The fast-forward refused on untracked files whose bytes origin already held at the same path.

THE DEFECT. `origin_reconcile` reached a window on 129 of 165 deadman cadences over the 24h to
2026-09-04 (`GATE_RUNNING` on only 36), gated its merge clean, pushed it -- and then could not
advance the shared tree. `NOT_ADVANCED`, on untracked `docs/staging/` notes that origin was adding
its own copy of. So origin moved, this tree did not, the publish path read BEHIND and threw away a
completed cycle, and the next cadence started one commit deeper.

Measured on the live shared tree the same day: of the two paths holding the fast-forward,
`...SEND_ONCE_MEMORY...md` hashed `792088eca` on disk and `792088eca` on origin. Byte-identical.
Git refuses to clobber an untracked file whatever its content, so the refusal was protecting that
file from being replaced by itself, and it was one of the two things keeping the reader stale.

`paths_blocking_fast_forward` already SAID this -- *"Usually byte-identical, and then nobody's work
is at stake at all"* -- and only a human could act on the sentence. These controls are over the
mechanism that acts on it.

WHAT EACH CONTROL WOULD CATCH, and every one of them names its own defect:

  * `test_a_byte_identical_twin_is_cleared_and_the_advance_then_succeeds` -- the repair itself.
  * `test_every_branch_of_the_partition_is_reachable` -- the REACHABILITY control. Every other test
    here asserts the advance REFUSES, and an `advance_shared_tree` that refused unconditionally
    would pass all of them. This one asserts all four outcomes are attainable from the same
    function, so a guard that can only say no cannot hide in the suite.
  * `test_a_path_that_differs_from_origin_is_never_removed` -- the all-or-nothing safety property.
  * `test_a_modified_path_beside_a_twin_removes_nothing` -- deleting for an advance that cannot
    happen is the one shape where this could actually cost a lane its work.
  * `test_an_unread_state_removes_nothing` -- fail-closed. `None` is "I could not look", and a
    version that treated it as `[]` would delete on a state nobody read.
"""
from __future__ import annotations

import contextlib
import subprocess

from background import origin_reconcile as orc


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


class _Advance:
    """The real `advance_shared_tree` with every destructive edge injected.

    `ff_results` is consumed one per call, so a test says "refuse, then succeed" -- which is the
    ONLY way to express the repair: the advance is defined by what the SECOND fast-forward does
    after the twins are gone.
    """

    def __init__(self, ff_results, blocking, twins, tracked=()):
        self.ff_results = list(ff_results)
        self.blocking = blocking
        self.twins = twins
        #: The TRACKED half of the same question, injected so this suite stays hermetic. It was
        #: added on 2026-09-05 with the branch it feeds; left to its default, the real
        #: `identical_tracked_twins` would shell out to git against the live repository and these
        #: controls would grade whatever the shared tree happened to be holding that minute.
        self.tracked = tracked
        self.removed: list[str] = []
        self.ff_calls = 0

    def _ff(self):
        self.ff_calls += 1
        return self.ff_results.pop(0)

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=lambda _project: self.blocking,
            twins_fn=lambda _project, _blocking: self.twins,
            tracked_twins_fn=lambda _project, _blocking: list(self.tracked),
            ff_fn=self._ff,
            remover=self.removed.append,
            restorer=lambda path: None,
            locker=contextlib.nullcontext,
        )


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


def test_a_byte_identical_twin_is_cleared_and_the_advance_then_succeeds():
    """THE REPAIR. An untracked path whose bytes origin already holds is removed, and the
    fast-forward that git had refused then succeeds.

    MUTATION: delete the `_remove(path)` loop body and the second fast-forward is never unblocked,
    so `advanced` stays False and the first assertion reds.
    """
    twin = "docs/staging/SEAT_FINDING_THE_SEND_ONCE_MEMORY.md"
    adv = _Advance(ff_results=[_completed(1, "untracked working tree files would be overwritten"),
                               _completed(0)],
                   blocking=[_untracked(twin)], twins=[twin]).run()

    assert adv["advanced"] is True, \
        "the twin was byte-identical to what origin brings, so the advance had nothing to lose " \
        "by clearing it and should have gone through"
    assert adv["cleared"] == [twin], \
        "the advance must report exactly which paths it removed -- a reader recovering one needs " \
        "its name, and origin holds every one of them"


def test_the_removal_and_the_advance_actually_happened_in_that_order():
    """A twin is removed BEFORE the second fast-forward, not after it.

    Removing afterwards would delete a file git had just written back as tracked -- the same bytes,
    now missing from a tree that believes it has them.

    MUTATION: move the `_ff()` call above the removal loop and the ordering assertion reds.
    """
    twin = "docs/staging/note.md"
    order: list[str] = []
    ff_results = [_completed(1, "would be overwritten"), _completed(0)]

    def ff():
        order.append("ff")
        return ff_results.pop(0)

    orc.advance_shared_tree(
        blockers_fn=lambda _p: [_untracked(twin)],
        twins_fn=lambda _p, _b: [twin],
        ff_fn=ff,
        remover=lambda p: order.append("rm:{}".format(p)),
        locker=contextlib.nullcontext,
    )
    assert order == ["ff", "rm:{}".format(twin), "ff"], \
        "the advance must try the fast-forward, clear the twins git refused on, and only then try " \
        "again -- got {}".format(order)


def test_a_path_that_differs_from_origin_is_never_removed():
    """ALL-OR-NOTHING. One blocking path is a byte-identical twin and the other is not, so clearing
    the twin would delete a file and STILL leave the fast-forward refused.

    This is the live 2026-09-04 state exactly: two paths blocked, one hashed equal to origin and one
    did not.

    MUTATION: change `len(twins) != len(blocking)` to `not twins` and the advance clears the twin
    for an advance that cannot happen, so `cleared == []` reds.
    """
    twin, theirs = "docs/staging/twin.md", "docs/staging/genuinely_different.md"
    adv = _Advance(ff_results=[_completed(1, "would be overwritten"), _completed(0)],
                   blocking=[_untracked(twin), _untracked(theirs)], twins=[twin]).run()

    assert adv["advanced"] is False
    assert adv["cleared"] == [], \
        "clearing the twin could not have advanced the tree while a non-identical path still " \
        "blocks it, so removing anything here is a deletion bought for nothing"
    assert theirs in adv["reason"], \
        "the refusal must name the path that actually held it, or the reader rediscovers it by hand"


def test_a_modified_path_beside_a_twin_removes_nothing():
    """A tracked file this tree has edited AND WHOSE BYTES DIFFER FROM ORIGIN'S is a lane's
    uncommitted work. The fast-forward cannot succeed while it stands, so nothing may be removed
    for it.

    CORRECTED IN PLACE 2026-09-05, beside the claim it got wrong. This docstring used to say that a
    tracked file this tree has edited *"cannot be hashed away"* -- full stop, of the KIND. That was
    false of the instance and expensive: measured the same day, four of the five `FF_MODIFIED` paths
    holding the live shared tree hashed EQUAL to origin, and the sentence above is why nobody
    looked. `identical_tracked_twins` now asks, and the case this control covers is the one that
    survives the asking -- `background/process_run_complete.py`, carrying 58 lines origin has never
    seen. The subject narrowed; the property did not move.

    MUTATION: filter `blocking` to the FF_UNTRACKED entries before the length comparison and the
    twin gets cleared while the tree still cannot advance -- `cleared == []` reds.
    """
    twin, mine = "docs/staging/twin.md", "background/process_run_complete.py"
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_untracked(twin), _modified(mine)], twins=[twin]).run()

    assert adv["advanced"] is False
    assert adv["cleared"] == [], \
        "a modified tracked path blocks the fast-forward no matter what else is cleared, so this " \
        "must remove nothing at all"
    assert mine in adv["reason"]


def test_an_unread_state_removes_nothing():
    """FAIL-CLOSED over the whole partition of "I could not look". `None` from either the blocking
    read or the hash comparison means a state nobody observed, and a file is never deleted on one.

    ONE CONTROL OVER BOTH `None` DOORS deliberately: they are the same property, and a version that
    guarded only the first would pass a per-leg test for the second.

    AND IT IS KEYED TO THE REASON, NOT TO `advanced`/`cleared` -- because the first draft was not,
    and a mutation caught it. Deleting the `blocking is None` guard SURVIVED: `None` is falsy, so
    it fell through to `if not blocking` one line below and returned the same `False`/`[]` by the
    other route. Same values, opposite meanings -- "I could not look" and "I looked and nothing
    collides" -- which is the distinction `paths_blocking_fast_forward` says in its own docstring
    is deliberate. An assertion over the values alone graded a fail-open as fail-closed.

    MUTATION: delete the `if blocking is None` branch and `None` is reported as "NOTHING local
    collides", reding the final assertion. Mutating the VALUES alone does not fire, and that is
    the point of writing it this way.
    """
    unread_blocking = _Advance(ff_results=[_completed(1, "refused")],
                               blocking=None, twins=["docs/staging/twin.md"]).run()
    assert unread_blocking["advanced"] is False and unread_blocking["cleared"] == [], \
        "the paths holding the advance could not be established, so nothing may be removed"

    unread_hashes = _Advance(ff_results=[_completed(1, "refused")],
                             blocking=[_untracked("docs/staging/twin.md")], twins=None).run()
    assert unread_hashes["advanced"] is False and unread_hashes["cleared"] == [], \
        "whether the blocking path matched origin byte for byte was never read, so nothing may " \
        "be removed"

    nothing_collides = _Advance(ff_results=[_completed(1, "refused for some other reason")],
                                blocking=[], twins=[]).run()
    assert nothing_collides["advanced"] is False and nothing_collides["cleared"] == []
    assert unread_blocking["reason"] != nothing_collides["reason"], \
        "'the blocking paths could not be READ' and 'nothing collides' are different findings " \
        "reached by opposite routes, and a verdict that renders them the same is how a fail-open " \
        "reads as a clean bill"
    assert "could NOT be established" in unread_blocking["reason"], \
        "an unread state must say so in the words a reader acts on, not merely decline to advance"


def test_a_clean_fast_forward_removes_nothing():
    """When git takes the fast-forward first time there is nothing to clear, and the advance must
    not go looking for files to delete.

    MUTATION: run the blocking read before the first fast-forward and this still passes -- but
    remove the `if first.returncode == 0` early return and the twin is cleared on a tree that never
    needed it, reding `cleared == []`.
    """
    run = _Advance(ff_results=[_completed(0)], blocking=[_untracked("docs/staging/twin.md")],
                   twins=["docs/staging/twin.md"])
    adv = run.run()
    assert adv["advanced"] is True and adv["cleared"] == []
    assert run.ff_calls == 1, "a fast-forward that succeeded must not be attempted twice"


def test_every_branch_of_the_partition_is_reachable():
    """THE CONTROL OVER THE WHOLE PARTITION. Every other test here asserts a REFUSAL, and an
    `advance_shared_tree` that refused unconditionally -- or that never removed anything -- would
    pass all of them. This asserts the four outcomes are each attainable from the same function.

    This project has entered that trap three times in one afternoon through three different doors
    (CLAUDE.md, "when a branch exists to be taken rarely, assert it CAN be taken"), so the guard is
    written over the partition rather than a leg per branch.

    MUTATION: make `advance_shared_tree` return `{"advanced": False, "cleared": [], ...}`
    unconditionally. Every other control in this file still passes; this one reds on `cleared_ok`
    and `advanced_ok` together.
    """
    twin = "docs/staging/twin.md"
    cleared_and_advanced = _Advance([_completed(1, "x"), _completed(0)],
                                    [_untracked(twin)], [twin]).run()
    advanced_untouched = _Advance([_completed(0)], [_untracked(twin)], [twin]).run()
    refused_intact = _Advance([_completed(1, "x"), _completed(0)],
                              [_untracked(twin), _modified("a.py")], [twin]).run()
    cleared_but_refused = _Advance([_completed(1, "x"), _completed(1, "still refused")],
                                   [_untracked(twin)], [twin]).run()

    advanced_ok = {cleared_and_advanced["advanced"], advanced_untouched["advanced"],
                   refused_intact["advanced"], cleared_but_refused["advanced"]}
    assert advanced_ok == {True, False}, \
        "the advance must be able to both succeed and refuse, or the controls asserting it " \
        "refuses are graded against a function that can only say no"

    cleared_ok = {bool(cleared_and_advanced["cleared"]), bool(advanced_untouched["cleared"]),
                  bool(refused_intact["cleared"]), bool(cleared_but_refused["cleared"])}
    assert cleared_ok == {True, False}, \
        "the advance must be able to both remove and refuse to remove -- a version that never " \
        "removed anything would satisfy every safety control in this file"

    assert cleared_but_refused["cleared"] == [twin] and not cleared_but_refused["advanced"], \
        "a twin cleared while the fast-forward STILL refuses is a real state and must be reported " \
        "with the paths named, because they are recoverable from origin and nothing else says how"
    assert "git checkout" in cleared_but_refused["reason"], \
        "the one branch that leaves files removed without advancing must carry the command that " \
        "puts them back"
