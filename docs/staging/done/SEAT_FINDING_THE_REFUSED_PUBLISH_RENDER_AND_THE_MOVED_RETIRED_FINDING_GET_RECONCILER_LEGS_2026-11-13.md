**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The refused-publish render and the moved retired finding get reconciler legs (2026-11-13)

*Lane-0 item `the-refused-publish-render-and-the-moved-retired-finding-get-reconciler-classes`,
continuing `SEAT_FINDING_THE_81_PATHS_HOLDING_THE_SHARED_TREE_ARE_ONE_UNLANDED_ORIENTATION_AND_ONE_REFUSED_PUBLISH_2026-11-12.md`.*

## Premise, re-measured at 00:44Z

Still live. The five cited commits are on origin, but they are the evidence, not the work: no class
for B or C exists on origin (5377dcfc42). The shared tree is at 40a48b5d84, 65 behind. B's copies were
last written 11 Nov 16:26-16:34Z (about 32 h), C's 11 Nov 11:07Z (about 38 h). Both are under the 48 h
abandoned line, so nothing clears them before 13 Nov 11:07Z (C) and 16:34Z (B). Waiting would clear them
as ABANDONED work, which is the wrong label: neither is anybody's work.

The duplicate-claim note named `the-final-bill-issue-day-has-one-home-beside-bill-due-date`. That item
holds `origin_reconcile.py` for a different subject (the final bill's issue day), so it is not this work.

## Pre-registration (written before the post-build dry run)

Both legs ride the ninth class (`superseded_live_verdicts`), because the act is the same: preserve the
bytes on a ref, restore HEAD, then fast-forward.

- **C, the moved leg.** Origin has no entry at the path. Origin adds a path with the same basename in
  HEAD..origin. That copy holds every line of the shared copy (as a multiset), and every line the shared
  copy deleted from HEAD is absent there too.
- **B, the refused-publish leg.** An origin commit in HEAD..origin is an `Auto-process run complete`
  publish for run `git=R`. That commit touches the path, and its committer time is later than the copy's
  mtime. The same commit carries the run's `run_complete_<ts>.md` marker. That marker records a
  `did-not-land` outcome at or after the copy's mtime, and its Finished stamp is at or before that mtime.
  No other `run_complete_*` marker on origin finished between the two. So the copy is a render of run R
  from a publish that was refused, and origin later published R at this path.

**Prediction:** run the same no-write dry run over the shared tree (every writer, the lock and the ff
injected to raise) at the origin this lands on. It holds **none of the 76** (71 customer pages,
`docs/state/{customer_sample,sim_data}.json`, `site/code/galaxy.png`, `site/data/director_delta.json`,
and the 205-of-238 finding). Any path it still holds was written after 11 Nov 20:31Z, and it is held for
a reason this build does not touch. If any of the 76 is still held, the reason it prints names the leg
that failed.

## Result (00:55Z, the built module over the shared tree, origin at 5377dcfc42)

**None of the 76 held. The prediction holds.** The dry run imports this worktree's module, runs it
against `/home/rich/synthetic-enterprise`, makes the ff refuse, and has every writer, the lock and the
filer raise. It reports `4 of 1478 blocking path(s) could NOT be proven lossless`, so 1,474 are proven.
The 4 held are new copies, written after 20:31Z on 11 Nov, as the prediction allowed:

- `docs/direction/DIRECTION.yaml`, `decisions.jsonl` and `docs/status/SEAT_STRETCH_LOG.md`, written
  13 Nov 00:29Z. This is the next orientation's record, which is live and still landing itself.
- `background/origin_reconcile.py`, written 12 Nov 22:24Z. A lane wrote this earlier draft of the same
  `reconcile()` comment and `detail` ordering that 5377dcfc42 landed. Its wording is different, so it has
  5 lines origin lacks and 1 merge conflict. The ninth class leaves an earlier WORDING held on purpose
  (see its docstring). It reaches the 48 h abandoned line at 14 Nov 22:24Z. If nobody lands or drops it
  first, it is aged out to a ref then. This item does not touch it.

So the advance waits only on the orientation landing its record. That is the ordinary shape. Nothing in
B or C holds it now.

Mutation check: each leg, and each refusal condition inside the refused-publish leg, fires at least one
test (`tests/background/test_a_refused_publish_render_and_a_moved_retired_finding_are_cleared.py`).
That covers the leg itself, the moved leg, another run finishing in between, the render being after the
last refusal, and origin's publish predating the render. The last condition had no test when first run.
It was a missing test, not an equivalence: a render written after origin's publish is not one origin
overtook. The test was added and the mutation now fires.

To reverse: revert the commit. The legs only widen which copies are preserved to
`refs/preserved/origin-reconcile-superseded-live/` and restored. Every cleared byte is on that ref.

The legs act on the next `reconcile-watch` tick after they land, with no bootstrap wait.
`reconcile_watch` runs `origin/main`'s `origin_reconcile` from a checkout of origin
(`background/reconcile_watch.py:345`), so it does not use the shared tree's stale copy. The handed-on
work is the 22:24Z draft of `origin_reconcile.py` on the shared tree. Its lane should land it or drop it
before 14 Nov 22:24Z, when it would otherwise be aged out.

## Retired (2026-11-14)

The build is on origin (04ce326626) and its result holds: none of the 76 is held. The handed-on draft
of `background/origin_reconcile.py` is no longer on the shared tree (`git status` shows the path clean),
so nothing this item named is left open. The 12 Nov finding it continued was retired to `done/` in the
same commit. The shared tree's remaining lag behind origin (39 commits at 14 Nov) is the ordinary
advance, not this item's.
