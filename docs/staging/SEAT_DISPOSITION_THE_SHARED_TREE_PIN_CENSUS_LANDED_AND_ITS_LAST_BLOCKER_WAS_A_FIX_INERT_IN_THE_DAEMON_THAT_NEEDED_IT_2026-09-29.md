**Severity:** RECORDED · **Lane:** H_harness · **Item:** `find-what-pins-the-shared-tree-behind-origin` (second draw)

# Disposition: the shared-tree pin census had already landed, and the last blocker was a fix that could not run in the daemon that needed it

The item was drawn a second time at 05:51Z. The duplicate-work note named the same id in
`.seat_work_in_hand.json`. That was this draw's own write: its `claimed_at` of 05:51:46Z matches
this tick's `RUNNING` line.

## What was already done (on origin)

The class census and a named blocker for each refusal are on origin in
`docs/staging/records/SEAT_RESULT_THE_SHARED_TREE_IS_PINNED_BY_A_MERGE_BUDGET_ONE_RECEIPT_OUTGREW_AND_BEHIND_IT_BY_ONE_WITHDRAWN_MANIFEST_DRAFT_2026-09-29.md`.
It landed with `f9023293a` (`origin_reconcile.merge_budget`). That covers the item's first DONE
leg. The census was not redone.

## Re-measured at this draw (shared tree, 06:5x BST)

- The shared tree was **39 behind and 5 ahead** of origin.
- **Class (c): cleared.** `git diff --quiet HEAD -- background/process_manifest.yaml` exits 0, and
  the file's mtime is 05:34Z. Another writer refreshed the withdrawn sanity-daemon draft. The
  continuation `clear-the-withdrawn-sanity-daemon-manifest-draft-from-the-shared-tree` is therefore
  spent by measurement.
- **The remaining blocker was the budget fix itself, and it could not reach the process that needed
  it.** The shared tree's HEAD does not contain `f9023293a`, and `grep -c merge_budget` finds 0 in
  its copy of `background/origin_reconcile.py`. `reconcile-watch` imports that copy, so every
  daemon merge still ran on the flat 1500 s timeout. The daemon's merge (pid 2988440, started
  05:50Z) was killed at 06:15:47Z, as all 12+ before it had been. The fix could only reach the
  shared tree through the merge it exists to let finish.
- **Breaking the loop:** once 2988440 exited, the seat ran `background.origin_reconcile` from this
  isolated worktree, which is at origin `b9c9092e6`. The merge was still built from the shared
  tree's HEAD (`_fresh_worktree`), but under origin's `merge_budget`:
  `(3070, "base 1500s + 1570s, the slowest incoming test leg (f997f8bf7's receipt)")`. The
  daemon's 06:16Z cadence refused on the owner marker, as designed, so the two merges did not race.

## Outcome of the seat-run merge

**In flight when this was landed.** Reconciler pid 3037437 started `surgical_land --merge` pid
3037474 at 06:15:50Z. Its budget ends about 07:07Z. The verdict it prints goes to
`/tmp/seat_reconcile_once.out`, a detached `setsid` job that outlives this tick. The seat's
hand-off `confirm-the-seat-run-merge-advanced-the-shared-tree` checks it:
`git -C /home/rich/synthetic-enterprise merge-base --is-ancestor origin/main HEAD`. If the merge
still timed out at 3070 s, the budget is not the whole story. The next place to look is then the
per-test timing item, not a larger number.

## Where the remainder lives

- `time-the-merge-selection-that-costs-26-minutes-per-test` (a tick worker drew it at 05:4xZ):
  why the subject gate takes 26 minutes. That is the reason the budget must exist at all.
- **Class of defect, for the record:** a repair to a daemon's own recovery path is inert in that
  daemon until the recovery it repairs succeeds. The memory note "a landed repair is inert in a
  running daemon" is this, one level down: the stale code is the code that would install the fresh
  code. Next time a fix lands on `origin_reconcile`, run it once from an origin worktree
  deliberately, rather than waiting for the cadence.
