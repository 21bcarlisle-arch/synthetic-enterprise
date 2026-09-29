**Severity:** HIGH · **Lane:** 0 — delivery seat · **Item:** `find-what-pins-the-shared-tree-behind-origin`

# The shared tree is pinned by a merge budget one receipt outgrew, and behind it by one withdrawn manifest draft

**2026-09-29, measured on the shared tree at HEAD `12f9a0ae7`, origin/main `e297d1169`: 37 behind,
3 ahead.** The duplicate-work note named this same id in `.seat_work_in_hand.json`. That was the
draw's own write (same `claimed_at`), not a second holder.

## Pre-registration (filed before the census ran)

- **P1.** The recent refusals are held by no path class. The tree is diverged, so
  `advance_shared_tree` is never reached, and the merge leg dies at its own 25-minute limit.
- **P2.** Of the paths a fast-forward must write, class (a) is non-empty, but what refuses is
  class (c): the 23:40Z list (`process_manifest.yaml`, `arrears_engine.py`,
  `run_phase4c_on_phase2b.py`, `run_value_cycle_ab.py`).
- **P3.** About 480 dirty paths, with class (d) the largest.
- **P4.** Simulation-run test files in the merge's selection take more than 10 min alone.

## The class census: 491 paths in `git status`

| class | count | of which the fast-forward must write |
|---|---:|---:|
| (a) byte-identical to origin, dirty only because HEAD is behind | 21 | 4 |
| (b) a daemon's observability/state/feed file | 76 | 0 |
| (c) an in-place edit that is not on origin | 114 | **1** |
| (d) untracked | 280 | 7 |

The 12 arriving paths, through the reconciler's own verdicts (read-only):

- All 4 class (a) paths are tracked twins that `advance_shared_tree` already clears:
  `background/process_run_complete.py`, `simulation/arrears_engine.py`,
  `simulation/run_phase4c_on_phase2b.py`, `tests/background/test_process_run_complete.py`.
- All 7 class (d) paths are cleared too: 5 are untracked twins and 2 are orphans it preserves and
  then removes.
- **One path is held: `background/process_manifest.yaml`, class (c).**

(b) is a heuristic split (path under `docs/observability/`, a dot-file `.json`, or the
generated-output oracle). No (b) path arrives, so the split decides nothing here.

**So class (a) is NOT what holds the fast-forward.** The mechanism the direction asked for, a step
that refreshes identical-to-origin paths, already exists (`identical_tracked_twins` plus
`restore_tracked_twin`, landed 2026-09-05). I did not build a second one.

## What blocked each refusal

There are two regimes and two independent blockers. Each one hides the other.

**2026-09-28 until 23:40Z: `NOT_ADVANCED`, 0 ahead.** Each of these was held by class (c) paths
that were in-place drafts while their commits were landing. The last list, 7 paths, is the four
twins above, `background/process_manifest.yaml` and `tools/run_value_cycle_ab.py`. By this census
all but `process_manifest.yaml` have become twins or left the arriving set.

**From 00:10Z, every cadence (12 of 12 up to 03:59Z, and the 04:xx run I watched): `ERROR:
TimeoutExpired`.** The cause is not a path. A seat commit (`65a6294be`, then `6b8b79e8d`,
`12f9a0ae7`) diverged the tree, so only the merge leg can close the fork. Its gate cannot finish
inside `MERGE_TIMEOUT_SECONDS = 1500`:

- `f997f8bf7` landed on origin at 23:19Z. Its receipt reads `tests: 1427 passed, 2 skipped in
  1570.17s (0:26:10)`. That is 26 minutes for its subject's tests alone.
- A merge that closes the fork carries that subject. The gate I watched was killed at 25:00 in
  pytest, having used 1,265 s of CPU on a 75-file selection.
- For comparison, the eight reconciliation merges between 21:31 and 00:01 BST gated in 4:10 to 4:38.

P1 holds. P2 is wrong in its detail: 4 of its 5 named paths are now class (a), and only the manifest
is (c). P3 is right (491; (d) = 280). P4 holds: eight of the selection's simulation/tools files,
run alone at origin HEAD under the box's current load, finished 15 tests in 1,500 s and were killed
before `--durations` could print. **Which test is slow is not yet established.**

## The class (c) blocker, read

The shared-tree copy of `background/process_manifest.yaml` is HEAD plus one 16-line
`sanity-daemon` `log_silence` block (mtime 2026-09-28 16:20 BST).

- That subject landed, rewritten, as `27aba4242` (18:19 BST).
- Origin then **withdrew** the row in `0afe22631` ("rows deleted" once PYTHONUNBUFFERED made the
  cause false).
- The draft's exact text is in no commit.
- `refresh_to_head` refuses it as holder work. Against origin it counts 85 "supplied" names, and
  most of those are rows origin deliberately deleted.

The copy is a superseded draft of withdrawn content. The measurement it carried (the 128 KiB
buffer) is on origin in the finding `27aba4242` landed. Clearing it is a judgement about another
lane's working copy, so this isolated turn did not write it.

## What landed with this result

`origin_reconcile.merge_budget`: the merge's timeout is now `MERGE_TIMEOUT_SECONDS` plus the
slowest test leg any incoming commit's receipt records.

- It reads 3,070 s on the live range (1,500 + 1,570, `f997f8bf7`) and 1,500 s on a level tree.
- A timed-out merge now returns a refusal naming its budget and the receipt that set it, instead of
  a truncated `TimeoutExpired: Command [...]`.

The control is `tests/background/test_the_merge_budget_is_floored_by_the_slowest_incoming_receipt.py`.
It asserts first that both branches are reachable. Four mutations each red it: no extension; the
budget not handed to the production runner; the last receipt taken instead of the slowest; the
timeout unnamed.

**The fix is inert where the daemon runs until the shared tree advances.** `reconcile-watch` imports
the shared tree's working copy, and the tree cannot advance without the merge. The seat breaks that
once by running the same reconciler from a worktree at origin (see below). The owner marker on
`/var/tmp/se-origin-reconcile` makes that run and the daemon's mutually exclusive.

## Where it stands, and what clears the rest

- **Class still holding HEAD behind origin: (c), one path, `background/process_manifest.yaml`.**
  The divergence clears once the merge leg is given a budget it can finish in.
- **The item that clears it:** refresh the copy to HEAD. Its only bytes not on any branch are the
  16-line hunk, preserved verbatim below, so the refresh loses nothing. Handed on as `clear-the-withdrawn-sanity-daemon-manifest-draft-from-the-shared-tree`.
- **Second hand-off:** time the merge selection per test. A 26-minute subject gate is the reason a
  budget has to exist at all.

## The withdrawn draft's bytes, preserved (the shared tree's hunk over `12f9a0ae7`, after line 262)

```yaml
    log_silence: >-
      UNFLUSHED STDOUT, the mechanism on `supervisor` above, BUT THE BUFFER IS 128 KiB, NOT 8 KiB,
      and that changes the arithmetic. Established 2026-09-28 against live pid 1639131 (up 14h,
      no restart): `docs/observability/sanity-daemon-log.md` gained entries at 14:40 and 15:10 UTC,
      one per 30-minute cycle, and `/proc/1639131/wchan` reads `hrtimer_nanosleep`, its ordinary
      POLL_INTERVAL sleep. Not wedged. `sanity_daemon.py:98` is one unflushed `print()`, stdout is
      a journal socket, and on this box's Python 3.14 `io.DEFAULT_BUFFER_SIZE` is 131072. MEASURED,
      not inferred from the constant: the only own lines in the journal since 2026-09-15 are ONE
      burst of 302 lines (130,200 bytes) from pid 2358963 at 2026-09-20 17:29:24 BST, stamped
      2026-09-17 09:27 to 09-20 10:59 UTC -- three days of cycles released as a single block --
      plus one stray line at 09-24 03:00:24, the partial line the block's boundary split, which
      journald emitted when the stream closed at that restart. At ~640 bytes a cycle the buffer
      takes about four days to fill; `deploy_restart --report` does cycle this unit (09-24 every
      10 minutes for 4h, then 09-25, 09-27 twice, 09-28 02:10), and each SIGTERM discards what is
      buffered. So the journal is not silent for hours but for days, and silent FOREVER whenever
      restarts come oftener than four days. The file is the log; the journal is not a reader.
```
