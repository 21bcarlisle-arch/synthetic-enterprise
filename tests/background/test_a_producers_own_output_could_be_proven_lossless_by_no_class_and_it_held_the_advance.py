"""The publisher's own feed held the publisher's own advance, and no class could ever take it.

THE DEFECT, measured on the live shared tree 2026-09-18, 7.8 days into the seventh publish stretch
with `.publish_gate_state.json` recording `last_clean_publish: null` and 74 episode failures. Eleven
paths held the fast-forward. Six were untracked twins the sweep had already hash-proven lossless.
One of the four holding them hostage was `site/data/value_arms.json` -- the arms producer's own
feed, rewritten by its producer at 01:24 that morning.

NO CLASS COULD TAKE IT, AND UNLIKE THE ORPHAN BEFORE IT THAT WAS NOT A GAP IN THE CANDIDATE SET BUT
A GAP IN THE READERS:

  * both twin sweeps need hash equality with origin, and a generated feed is never hash-equal --
    its producer rewrote it after the last landing and rewrites it again on the next tick;
  * `stale_copy_verdicts` answers *"this control has no reader for .json files, so it CANNOT
    establish that the copy has nothing to lose"* -- fail-closed, correctly, because
    `refresh_to_head` reads Python and a feed is not Python;
  * so the path was PERMANENTLY unresolvable, and under the all-or-nothing rule one permanently
    unresolvable path is fatal to every other class beside it. The six proven twins were cleared by
    nothing for as long as the feed sat there.

THE LOOP THAT MAKES IT SELF-SUSTAINING. `reconcile` merges and pushes from an ISOLATED worktree, so
origin advanced on the cadence all week while the shared tree could not follow. Each cadence closed
a fork and re-opened it, and the producer re-dirtied the blocking path every tick regardless. The
exhaust is inside the loop it blocks.

AND THE MODULE ALREADY KNEW. `_split_generated` asks the same two oracles a few hundred lines above,
and `_landing_clause` prints the answer to a human: *"the GENERATED path(s) are a PRODUCER'S OUTPUT,
not work -- do NOT land them"*. The refusal that then held the tree said it could not establish
whether that same path was some lane's work. Both sentences, same refusal, same path, one acted on.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_a_producers_output_is_cleared_and_the_advance_then_succeeds` -- the repair, and the
    reachability leg for the new branch.
  * `test_the_verdict_partition_is_reachable_both_ways` -- the guard that refuses EVERYTHING passes
    every refusal leg below. One control over the whole partition, per CLAUDE.md.
  * `test_an_authored_path_beside_a_generated_one_still_refuses_everything` -- the safety property
    that must NOT have moved. Displacing a lane's holder work is what this class is not, and the
    all-or-nothing rule is what guarantees it.
  * `test_an_unavailable_oracle_refuses_and_touches_nothing` -- fail-closed on the new door, and
    the OPPOSITE of `_split_generated`'s deliberate fail-soft, because this output decides a write.
  * `test_a_generated_path_head_does_not_hold_is_refused` -- the act is `restore_tracked_twin`,
    which writes HEAD's bytes; a path HEAD has no blob for would be reported cleared and then
    refuse again at the advance.
  * `test_the_generated_class_is_asked_only_of_what_the_stale_class_left` -- the QUESTION, not the
    answer. A caller that widened this class to every blocking path would be caught by nothing
    else here, because the fixture's own verdict list would still say False in the right places.
  * `test_a_generated_blocker_is_restored_and_never_unlinked` -- a tracked path removed by `unlink`
    leaves its index entry behind and the fast-forward stays refused on a file no longer on disk.
"""
from __future__ import annotations

import contextlib
import subprocess

from background import origin_reconcile as orc

#: The live 2026-09-18 blocker, and a path both generated-path oracles really do know.
_FEED = "site/data/value_arms.json"
#: The live 2026-09-18 holder work beside it: test functions origin has never seen.
_AUTHORED = "tests/tools/test_fold_noise_floor_family.py"


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["git"], returncode=returncode, stdout="",
                                       stderr=stderr)


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


class _Advance:
    """The real `advance_shared_tree` with its destructive edges injected and told apart.

    `removed` and `restored` are separate lists for the reason the sibling harness gives: the two
    acts are not interchangeable on a tracked path, and one collected list could not tell them
    apart.
    """

    def __init__(self, ff_results, blocking, generated=None, stale=(), tracked=()):
        self.ff_results = list(ff_results)
        self.blocking = blocking
        self.generated = generated
        self.stale = stale
        self.tracked = tracked
        self.removed: list[str] = []
        self.restored: list[str] = []
        #: Which paths the generated class was ASKED about, apart from which it approved. A caller
        #: that widened the question would be invisible to a fixture that only records answers.
        self.offered: list[str] = []

    def _generated_verdicts(self, _project, paths):
        self.offered.extend(paths)
        if self.generated is None:
            return None
        return {p: (p in self.generated, "fixture verdict") for p in paths}

    def run(self):
        return orc.advance_shared_tree(
            blockers_fn=lambda _project: self.blocking,
            twins_fn=lambda _project, _blocking: [],
            tracked_twins_fn=lambda _project, _blocking: list(self.tracked),
            stale_fn=lambda _project, paths: {
                p: (p in self.stale, "fixture verdict") for p in paths},
            generated_fn=self._generated_verdicts,
            orphans_fn=lambda _project, paths: {p: (False, "fixture verdict") for p in paths},
            preserver=lambda paths: ("0" * 40, ""),
            ff_fn=lambda: self.ff_results.pop(0),
            remover=self.removed.append,
            restorer=lambda p: self.restored.append(p) or None,
            locker=contextlib.nullcontext,
            # LEVEL WITH ORIGIN, so the subject stays the generated logic. The real `commits_ahead`
            # reads the repository the suite runs in, which is routinely ahead.
            ahead_fn=lambda _project: 0,
        )


def test_a_producers_output_is_cleared_and_the_advance_then_succeeds():
    """THE REPAIR, and the reachability control over the whole new branch.

    Before it, a generated feed blocking the fast-forward was hash-unequal to origin and unreadable
    by the stale judgement, so it could be resolved by nothing and held the tree indefinitely.

    MUTATION: drop `set(generated)` from the `resolvable` union and the feed falls into `held`, so
    `advanced` is False and the first assertion reds.
    """
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_modified(_FEED)], generated=[_FEED]).run()

    assert adv["advanced"] is True, \
        "the only blocker was a producer's own output -- re-derivable, and rewritten by the next " \
        "tick whatever happens here -- so the fast-forward git refused should have gone through"
    assert adv["cleared"] == [_FEED], \
        "the feed is what was cleared and it should say so, because a reader of this reason is " \
        "deciding whether a lane lost work"


def test_the_verdict_partition_is_reachable_both_ways():
    """A class that approves NOTHING passes every refusal leg in this file.

    One control over the whole partition rather than a leg per branch, per CLAUDE.md: the real
    `generated_output_verdicts` must be able to answer True AND False, asked about the two live
    2026-09-18 blockers, against the real oracles.

    MUTATION: make the verdict body return `(False, ...)` unconditionally -- every refusal leg here
    still passes and only this one reds.
    """
    verdicts = orc.generated_output_verdicts(paths=[_FEED, _AUTHORED])

    assert verdicts is not None, \
        "both generated-path oracles answer in this repository, so a None here is the oracle " \
        "seam breaking and not a verdict"
    assert verdicts[_FEED][0] is True, \
        "`site/data/value_arms.json` is a producer's output both oracles know, and if this class " \
        "cannot say so it can never clear the blocker it was built for"
    assert verdicts[_AUTHORED][0] is False, \
        "a test file carrying functions origin has never seen is holder work, and a class that " \
        "approved it would be clearing a lane's work rather than a producer's exhaust"


def test_an_authored_path_beside_a_generated_one_still_refuses_everything():
    """The safety property that must NOT have moved: holder work is never displaced.

    The all-or-nothing rule is what guarantees it -- one unprovable path refuses the whole advance,
    so the clearable feed beside it is not touched either.

    MUTATION: clear the resolvable set before checking `held` (or drop the all-or-nothing guard)
    and the authored path's bytes get written over while the advance still cannot succeed.
    """
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten")],
                   blocking=[_modified(_FEED), _modified(_AUTHORED)], generated=[_FEED])
    result = adv.run()

    assert result["advanced"] is False, \
        "a lane's holder work held the advance and no amount of clearing exhaust addresses it"
    assert adv.restored == [] and adv.removed == [], \
        "nothing may be written when the advance cannot succeed anyway -- that is the one shape " \
        "in which clearing a path actually costs someone something"
    assert _AUTHORED in result["reason"], \
        "a refusal that cannot name what is holding the tree sends the next reader at the wrong " \
        "path, which is the 2026-09-09 wedge"


def test_an_unavailable_oracle_refuses_and_touches_nothing():
    """Fail-closed on the new door, and deliberately the OPPOSITE of `_split_generated`'s rule.

    There the output is remedy prose and failing soft costs a reader a hand-check. Here it decides
    whether a file is written over, so an unasked oracle must read as neither "generated" (a write
    bought on an unread state) nor silently "authored".

    MUTATION: treat a `None` verdict map as an empty one and this reds -- the advance would proceed
    to clear the twins beside it on a classification nobody read.
    """
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten")],
                   blocking=[_modified(_FEED)], generated=None)
    result = adv.run()

    assert result["advanced"] is False and result["cleared"] == [], \
        "whether the blocker was a producer's output was not established, so nothing may advance"
    assert adv.restored == [] and adv.removed == [], \
        "a file is never written over on an unread classification"
    assert "could not be established" in result["reason"], \
        "the refusal must say the oracle would not answer, because that is a broken seam to " \
        "repair and not a lane's work to go and land"


def test_a_generated_path_head_does_not_hold_is_refused(tmp_path, monkeypatch):
    """The act is `restore_tracked_twin`, which writes HEAD's bytes -- so HEAD must hold some.

    A path approved here that HEAD has no blob for would be reported as cleared and then refuse the
    fast-forward a second time, on a file this had already told the reader was dealt with.

    MUTATION: drop the `_blob_in_head` leg and this reds while every other leg stays green.
    """
    monkeypatch.setattr(orc, "_blob_in_head", lambda _project, _path: None)
    verdicts = orc.generated_output_verdicts(paths=[_FEED])

    assert verdicts[_FEED][0] is False, \
        "HEAD holds no blob at this path, so there are no bytes to restore it to"
    assert "HEAD holds no blob" in verdicts[_FEED][1], \
        "the reason names the missing base, because a reader told only 'refused' would look for " \
        "a lane holding the file and find none"


def test_the_generated_class_is_asked_only_of_what_the_stale_class_left():
    """The QUESTION, not the answer -- and nothing else in this file would catch it.

    A caller that offered every blocking path to this class would still refuse in the right places
    here, because the fixture's own verdict list says False for the authored path. Only the set of
    paths OFFERED can see the widening.

    MUTATION: pass `candidates` rather than `candidates` minus `stale` and this reds alone.
    """
    stale_path = "background/some_stale_module.py"
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_modified(_FEED), _modified(stale_path)],
                   generated=[_FEED], stale=[stale_path])

    adv.run()

    assert stale_path not in adv.offered, \
        "the stale judgement already took this path; asking a second class about it invites two " \
        "mechanisms for one act, which is how they drift apart"
    assert _FEED in adv.offered, \
        "the feed is exactly what this class exists to be asked about"


def test_a_generated_blocker_is_restored_and_never_unlinked():
    """Two acts on a tracked path are not interchangeable, and the wrong one re-refuses.

    `unlink` on a path with an index entry leaves that entry behind, so the fast-forward stays
    refused on a file that is no longer even on disk -- a strictly worse state than the blocker.

    MUTATION: fold `generated` into the untracked branch instead of `tracked_set` and this reds.
    """
    adv = _Advance(ff_results=[_completed(1, "local changes would be overwritten"), _completed(0)],
                   blocking=[_modified(_FEED)], generated=[_FEED])
    adv.run()

    assert adv.restored == [_FEED], \
        "a tracked generated path is RESTORED to HEAD's bytes for the fast-forward to overwrite"
    assert adv.removed == [], \
        "unlinking it would leave the index entry behind and the advance would refuse again"
