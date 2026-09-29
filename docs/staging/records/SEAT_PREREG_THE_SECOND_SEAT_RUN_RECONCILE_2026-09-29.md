**Severity:** RECORDED · **Lane:** H_harness · **Item:** `rerun-the-origin-reconcile-from-an-origin-worktree-without-racing-it`

# Pre-registration: the second seat-run reconcile, written before it runs (07:12Z)

## Duplicate-work disposition

- The same-id entry in `.seat_work_in_hand.json` is this draw's own write, so there is no rival.
- `confirm-the-seat-run-merge-advanced-the-shared-tree` is a different piece of work. It reads the
  06:15Z run's verdict. That verdict was `REFUSED_RACE` at 06:59:16Z (`/tmp/seat_reconcile_once.out`).
- The tick worker holding that claim (pid 3082525) is landing a fix to it from
  `/var/tmp/se-race-catchup`. The fix catches a reconciler that lost the push race up onto the
  merge that already gated, at most twice. Its commit message names this item as the next step.

## State at 07:12Z

- Shared tree: 7 ahead, 42 behind origin. Its `origin_reconcile.py` has 0 `merge_budget` hits.
- The daemon merge (reconcile_watch pid 3170801 → `surgical_land --merge` pid 3171647) started
  07:01:05Z on the old flat 1500 s timeout. It dies at about 07:26Z.

## Procedure

1. Wait with `tools.wait_for --pid 3171647`.
2. Then, from a fresh worktree at `origin/main`, fetched at that moment, run
   `setsid python3 -m background.origin_reconcile --json`. If the race-catchup fix has reached
   origin by then, this run carries it. Otherwise it carries only `merge_budget` (3070 s).
3. Nothing from this seat is landed to origin until the verdict prints. A landing of ours would
   move origin mid-gate, which is how the first run lost.

## Predictions (filed before the answer)

- P1: the daemon merge 3171647 is killed at about 1500 s, not finished. Confidence 0.9.
- P2: the seat run gates in 35–50 min, the same order as the first run's 43 min. Confidence 0.7.
- P3, if the run lacks the catch-up: `REFUSED_RACE` again. Origin moved roughly every 30 min this
  morning. Confidence 0.65.
- P3', if the run carries the catch-up: `PUSHED`/`RECONCILED`, and the shared tree then answers
  `merge-base --is-ancestor <pre-run origin> HEAD` true. Confidence 0.6.

The outcome is appended below this line when it prints.

## What happened (07:26Z)

- **P1 held.** The daemon merge 3171647 exited at 07:26:09Z, which is 1504 s after it started.
  It was killed, not finished: the service reports 25 min 21 s wall time.
- **The item was done by the other lane, three seconds ahead of this one.** The tick worker holding
  `confirm-the-seat-run-merge-advanced-the-shared-tree` ran `/tmp/seat_reconcile_catchup.sh`. It
  waited on the same pid, then started `background.origin_reconcile --json` at 07:26:08Z (pid
  3251388, merge pid 3251427). It ran from `/var/tmp/se-race-catchup` at `e5cc17abd`, which by then
  WAS `origin/main`, so it carries `merge_budget` and `RACE_CATCHUPS`.
- This seat's run started at 07:26:11Z and refused with `ERROR`: "another writer holds
  /var/tmp/se-origin-reconcile (owner marker live …)". That is the marker doing its job. Two
  reconcilers did not race.
- **Disposition: `--release`, not a second run.** The work this item asks for is in flight under
  the other id. This record lands only after that run prints its verdict, so no landing of ours
  moves origin under its gate.

## Verdict (08:08:05Z, `/tmp/seat_reconcile_catchup.out`)

`NOT_ADVANCED`, `pushed: true`, `behind: 44`.

- **P2 held.** The merge gated clean in about 42 min under the 3070 s budget.
- **The race was won.** The merge is on origin as `6166e3af0`. The shared tree's ahead leg is now 0,
  which closes the fork that blocked landings.
- **P3' was half right.** It was pushed, but the shared tree did NOT fast-forward. It is 44 behind,
  and its `origin_reconcile.py` still has 0 `merge_budget`, so the daemon still runs the 1500 s
  timeout.
- **The new blocker is a different class: dirty bytes on the shared tree, not the budget.** The
  reconciler refused on 14 paths:
  - 5 modified: `background/process_run_complete.py`, `simulation/arrears_engine.py`,
    `simulation/run_phase4c_on_phase2b.py`, `tests/background/test_process_run_complete.py`,
    `tests/tools/test_fold_noise_floor_family.py`.
  - 1 generated: `CLASS_MEASUREMENTS_THAT_MIRROR`.
  - 8 untracked staging drafts that origin already carries.
- **Held by holder work.** `test_fold_noise_floor_family.py` supplies 4 names that origin lacks, so
  the lossless clear refused as a whole and wrote nothing. These are the draw's "contested paths"
  list, word for word.
- Now that the fork is closed, the fast-forward needs no merge. Once those paths are landed or
  cleared, any cadence, including the daemon's 1500 s one, advances the tree. The budget has
  stopped being the binding constraint.

Handed on as `clear-the-14-shared-tree-paths-that-hold-the-fast-forward`.
