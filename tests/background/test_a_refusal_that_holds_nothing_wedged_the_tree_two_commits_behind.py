"""One path can be BOTH blocking kinds at once, and the all-or-nothing comparison counted it twice.

THE DEFECT, measured on the live shared tree 2026-09-09. `origin/main` was 2 commits ahead, the
shared tree would not fast-forward, and `.publish_gate_state.json` carried `last_clean_publish:
null` with `wedge_since` 32 hours old and 32 recorded episode failures.

Exactly ONE path held it:

    docs/staging/SEAT_PREREGISTRATION_WHAT_THE_FIXED_HORIZON_CUTS_OWN_NULL_INTERVAL_WILL_SAY_...md

staged-deleted in the index and still present on disk. That is both kinds at once and legitimately
so -- `git diff --name-only HEAD` reports it because the worktree differs from HEAD, and `git
ls-files --others` reports it because the index has no entry for it. `paths_blocking_fast_forward`
returned TWO entries for it, one per kind, which is correct: the entries are per (path, kind).

Its bytes on disk hashed `75738ea13` and origin's blob at that path hashed `75738ea13`. Identical.
Both twin sweeps matched it, `resolvable` deduplicated to one path, and the comparison
`len(resolvable) != len(blocking)` read 1 != 2 and refused.

THE REFUSAL SAID SO IN ITS OWN WORDS AND NOBODY HAD CAUSE TO DISBELIEVE IT:

    "0 of 2 blocking path(s) are NOT byte-identical to what origin brings, so clearing the 1 that
     are would delete files and still not advance. Nothing was removed. Held by: "

Zero held, one resolvable, two blocking, and a refusal. The sentence is internally contradictory
and it ran every five minutes for 32 hours. R15: the two sides of a comparison were different
DOMAINS -- a set of paths against a list of (path, kind) entries -- and no control in
`test_the_twin_sweep_was_defeated_by_git_add.py` could see it, because every case there gives each
kind its own distinct path and so never constructs the duplicate.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_a_path_blocking_under_both_kinds_does_not_count_as_two_blockers` -- the repair, at the
    live shape.
  * `test_a_refusal_always_names_at_least_one_path_it_is_holding` -- the PROPERTY, over the whole
    partition. This is the one that is not pinned to today's answer: a refusal that cannot name a
    held path is a counting error whatever produced it, and this catches the next domain mismatch
    as well as this one.
  * `test_a_genuinely_dirty_path_wearing_both_kinds_still_refuses_everything` -- the safety
    property, which the repair must NOT have bought its advance with.
"""
from __future__ import annotations

import contextlib
import subprocess

from background import origin_reconcile as orc


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


class _Advance:
    """The real `advance_shared_tree` with both destructive edges injected and told apart."""

    def __init__(self, blocking, twins=(), tracked=(), ff_results=None):
        self.blocking = blocking
        self.twins = twins
        self.tracked = tracked
        self.ff_results = list(
            ff_results or [_completed(1, "local changes would be overwritten"), _completed(0)])
        self.removed: list[str] = []
        self.restored: list[str] = []

    def _ff(self):
        return self.ff_results.pop(0)

    def _restore(self, path):
        self.restored.append(path)
        return None

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=lambda _project: self.blocking,
            twins_fn=lambda _project, _blocking: list(self.twins),
            tracked_twins_fn=lambda _project, _blocking: list(self.tracked),
            ff_fn=self._ff,
            remover=self.removed.append,
            restorer=self._restore,
            locker=contextlib.nullcontext,
            # LEVEL WITH ORIGIN, so the subject stays the counting. The real `commits_ahead` reads
            # the repository the suite runs in, which is routinely ahead of origin.
            ahead_fn=lambda _project: 0,
        )


#: The live 2026-09-09 blocker: staged-deleted in the index, still on disk, bytes equal to origin's.
_WEDGE = ("docs/staging/"
          "SEAT_PREREGISTRATION_WHAT_THE_FIXED_HORIZON_CUTS_OWN_NULL_INTERVAL_WILL_SAY_2026-09-09.md")


def _both_kinds(path: str) -> list[dict]:
    """What `paths_blocking_fast_forward` really returns for a staged deletion still on disk."""
    return [{"path": path, "kind": orc.FF_MODIFIED}, {"path": path, "kind": orc.FF_UNTRACKED}]


def test_a_path_blocking_under_both_kinds_does_not_count_as_two_blockers():
    """THE REPAIR, at the live shape. One path, hash-proven against origin under both kinds, must
    not count as two blockers against a deduplicated `resolvable`.

    This is the whole 32-hour wedge: the tree's bytes at this path were ALREADY origin's, and the
    fast-forward was about to write them back unchanged.

    MUTATION: restore `if len(resolvable) != len(blocking)` and this reds -- 1 != 2 refuses, so
    `advanced` is False and nothing is cleared.
    """
    run = _Advance(blocking=_both_kinds(_WEDGE), twins=[_WEDGE], tracked=[_WEDGE])
    adv = run.run()

    assert adv["advanced"] is True, \
        "the ONE blocking path was byte-identical to what origin brings under both kinds, so the " \
        "tree had nothing to protect and must advance -- got: {}".format(adv["reason"])
    assert adv["cleared"] == [_WEDGE], \
        "the path must be cleared exactly ONCE -- clearing it under both kinds would unlink a file " \
        "that had just been restored, got {}".format(adv["cleared"])
    assert run.restored == [_WEDGE] and run.removed == [], \
        "a path with an index entry is RESTORED, never unlinked: `unlink` leaves the staged " \
        "deletion behind and the fast-forward stays refused -- got removed={}, restored={}".format(
            run.removed, run.restored)


def test_a_refusal_always_names_at_least_one_path_it_is_holding():
    """THE PROPERTY, over the whole partition, and it is NOT pinned to today's answer.

    A refusal on the twin comparison means "some path is not byte-identical to origin". If it can
    name no such path, the refusal is a counting error -- whatever the counting error happens to
    be. The 2026-09-09 wedge printed `Held by: ` with nothing after it for 32 hours and the empty
    tail read as formatting.

    Keyed to the property rather than to the duplicate-path instance, so the NEXT domain mismatch
    on this comparison reds here too. CLAUDE.md: key a control to the property, not to today's
    answer.

    MUTATION: restore the length comparison and the both-kinds case reds -- it refuses with an
    empty `held`. Any future change that refuses without a named holder reds the same way.
    """
    cases = {
        "one path wearing both kinds, hash-proven": _Advance(
            blocking=_both_kinds(_WEDGE), twins=[_WEDGE], tracked=[_WEDGE]),
        "duplicate untracked entries for one path": _Advance(
            blocking=[{"path": _WEDGE, "kind": orc.FF_UNTRACKED}] * 2, twins=[_WEDGE]),
        "twins reported for paths not in the blocking set": _Advance(
            blocking=[{"path": _WEDGE, "kind": orc.FF_MODIFIED}],
            tracked=[_WEDGE, "docs/staging/not_blocking_at_all.md"]),
    }
    for label, run in cases.items():
        adv = run.run()
        if adv["advanced"]:
            continue
        assert "Held by: " not in adv["reason"] or adv["reason"].split("Held by: ")[1].strip(), \
            "{}: the advance refused on the twin comparison and named NO path holding it. A " \
            "refusal that is holding nothing is an arithmetic error, not a protection -- " \
            "got: {}".format(label, adv["reason"])


def test_a_genuinely_dirty_path_wearing_both_kinds_still_refuses_everything():
    """THE SAFETY PROPERTY THE REPAIR MUST NOT HAVE BOUGHT ITS ADVANCE WITH.

    Deduplicating the comparison must not make an unproven path resolvable. A path carrying a
    lane's real work refuses the whole advance however many twins stand beside it -- and it must do
    so when it wears both kinds too, which is exactly the shape the repair touched.

    MUTATION: compute `held` from `resolvable` alone (`if not resolvable`) rather than as the
    blocking paths MINUS the resolvable ones, and the dirty path is cleared for an advance it
    cannot support -- `cleared == []` and both list assertions red.
    """
    mine = "background/process_run_complete.py"
    run = _Advance(blocking=_both_kinds(_WEDGE) + _both_kinds(mine),
                   twins=[_WEDGE], tracked=[_WEDGE])
    adv = run.run()

    assert adv["advanced"] is False, \
        "a path whose bytes origin does NOT hold blocks the fast-forward no matter what else is " \
        "byte-identical beside it"
    assert adv["cleared"] == [] and run.removed == [] and run.restored == [], \
        "nothing may be touched: clearing the proven twin would be a deletion bought for no advance"
    assert mine in adv["reason"], \
        "the refusal must name the path that actually held it, once -- got: {}".format(adv["reason"])
    assert adv["reason"].count(mine) == 1, \
        "the held path wears two kinds and must still be reported ONCE, or the reader is sent " \
        "hunting for a second file that does not exist -- got: {}".format(adv["reason"])
    assert _WEDGE not in adv["reason"], \
        "a path that IS byte-identical is not what held the advance, and naming it sends the " \
        "reader at a file with nothing wrong with it"
