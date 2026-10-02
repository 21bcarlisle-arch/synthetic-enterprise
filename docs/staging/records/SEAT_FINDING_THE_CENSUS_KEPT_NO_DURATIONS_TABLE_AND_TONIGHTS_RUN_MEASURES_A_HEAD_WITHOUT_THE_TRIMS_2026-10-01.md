**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the census kept no durations table, and tonight's run measures a HEAD without the trims

Lane 0 `the-census-bound-follows-the-trimmed-suite`. The direction: after the next complete nightly
census, read its wall clock and `--durations=80` table, move `WORST_OBSERVED_SUITE_SECONDS` to that
run and `SUITE_TIMEOUT_SECONDS` to just over twice it, and trim whatever tops the table.

**Duplicate-work note at draw:** the "other live claim" was this same id, written by this draw's own
executor (pid 2955244, the owner of this worktree). No rival seat or `surgical_land` held it. No
disposition needed.

## Two things stood between the direction and doing it

**1. The table the direction asks for did not exist.** `pytest_argv()` never passed `--durations`,
and `main()` printed only the verdict -- the suite's output was parsed for reds and dropped. The
journal held a wall clock and nothing about which tests spent it; every past trim began with a
separate multi-hour timing run outside the unit. **Fixed in this commit**: the census runs
`--durations=80` and prints each row to the journal as `  SLOW     <row>` (and as `durations` under
`--json`). Three mutations fire: drop the print, empty the parser, drop the flag.

**2. Tonight's 03:34 census does not measure the trimmed suite.** Its subject is
`git rev-parse HEAD` in the SHARED tree (`prc._head_sha`), which at 02:05 was `9a5dc872e`, diverged
from origin (2 ahead, 23 behind) and not containing `571a79e9f` or the other trims. Its driver is
the shared tree's working copy too, so the durations change above also only reaches the unit once
the shared tree carries this commit. Whatever wall clock tonight's run produces is the UNTRIMMED
suite and must not be used to move the bound down.

## Pre-registration (written 02:20 BST, before either run has started)

- **Tonight (03:34, subject `9a5dc872e` or whatever shared HEAD is at 03:34, untrimmed):** if it
  completes, 7,500-9,500 s wall, same band as the 09-30 timing run (8,647 s). No durations table in
  the journal unless the shared tree has advanced past this commit by 03:34 (I predict it will not).
- **First complete census whose subject contains `571a79e9f` AND whose driver carries this
  commit:** 5,800-7,600 s wall (8,647 s less the ~1,750 s the trims saved, widened for contention),
  and a `SLOW` table whose top row is under 300 s.

## What done means for this item

The bound moves when -- and only when -- a complete census with a trimmed subject and a printed
table exists in the journal: `WORST_OBSERVED_SUITE_SECONDS` to that run's wall (unit line
`Consumed ... over <wall>`), `SUITE_TIMEOUT_SECONDS` to just over twice it, unit
`TimeoutStartSec` = timeout + 300, and the top of its `SLOW` table trimmed. That is handed on as a
continuation, because it needs a run that cannot exist inside this turn.

## Result of the 03:34 run (read 06:27 BST, 2026-10-01) -- untrimmed evidence, bound NOT moved

- **Did not complete.** `the suite did not finish inside 7200s -- UNPROVEN`; unit line
  `Consumed 2h 6min 27.594s CPU time over 2h 2.720s wall clock time, 8.1G memory peak`. No `SLOW`
  rows. Wall clock 7,203 s, which is the bound being hit, not a measurement of the suite.
- **Subject and driver were both shared HEAD `c71a78417`** (shared-tree reflog: on it from 03:29
  until a reset to `3f7a0632f` at 05:18). That commit contains `9a5dc872e`, but **not** `571a79e9f`
  (trims), `fb3e406a5` (17400 s bound) or `1542c490e` (durations table). So the driver ran
  `SUITE_TIMEOUT_SECONDS = 7200`, not 17400.
- **The prediction was wrong.** I predicted a complete run in 7,500–9,500 s. I took the 17400 s bound to
  be live, but the driver was the shared working copy, which lacked even the 23:21 bound move. So
  the untrimmed suite was cut off at 7200 s, below the band, as it had been every night since
  09-23. The miss was the driver, not a fact about the suite. "No durations table" held.
- Fails qualification on (a) no summary, (b) subject lacks `571a79e9f`, (c) no SLOW rows.
- **For the next run:** the shared tree is now at `2acb617d4` = origin/main. That carries the trims, the
  17400 s bound and the table. The 2026-10-02 03:34 run is the first that can qualify, unless the
  shared checkout falls behind origin again. Check its subject's ancestry before reading its wall.

## Result of the 2026-10-02 run (read 2026-10-02) -- QUALIFIES; the band held, the bound is deliberately NOT lowered

Lane 0 `the-census-bound-follows-the-2026-10-02-census-run`. The duplicate-work note at draw named
this same id in `.seat_work_in_hand.json`, which was the draw's own write. No rival held it.

- **(a) Completed.** `NEW_RED: 47 test(s) red at HEAD ... 36302 passed`, not UNPROVEN. Started
  03:38:27, failed-as-red at 05:44:59. Unit line: `Consumed 2h 15min 52.226s CPU time over 2h 6min
  32.163s wall clock time, 11.6G memory peak`. **Wall = 7,592 s.**
- **(b) Subject `1263a63aa`.** The shared-tree reflog shows it on that commit from 03:29:24 to
  04:02. It has `571a79e9f` AND `fb3e406a5` as ancestors (checked with `git merge-base
  --is-ancestor`).
- **(c) 80 `SLOW` rows** were printed.
- **Pre-registration:** the wall band of 5,800-7,600 s **HELD**, at its top edge (7,592). The
  prediction that the top row would be under 300 s **was WRONG**. The top row is 370.77 s (see
  below).

**Decision: the bound does NOT move.** The direction said to set `WORST_OBSERVED_SUITE_SECONDS` to
this run's wall. That would LOWER it, from 8,646.7 to 7,592, and the timeout from 17,400 to about
15,200. The constant's own contract is "the worst COMPLETE census duration on record, moved by hand
when a SLOWER run is observed". 7,592 is not slower. The 8,647 s run happened, and it ran under
contention a night can repeat. Lowering the bound gains nothing: the timer fires once every 24 h,
and 17,400 s from 03:30 ends by 08:20. The only thing lowering could change is turning a slow night
into UNPROVEN, which is the silence this bound exists to prevent. The direction assumed the trimmed
run would set a new worst. It set a new best-observed instead, and that is evidence, not a bound.
Reverse by editing the two constants and the unit's `TimeoutStartSec`; the control
`test_the_census_timeout_clears_the_duration_it_has_observed` holds the relation either way.

**The top SLOW rows cannot be trimmed inside this item:**

1. `370.77s setup test_couple_w2_11_d5.py::test_cli_runs_and_prints_all_three_gaps`. This time is
   NOT the test's own. It is the setup of the three module-scoped sweep fixtures
   (`drift_resolution`, `own_drift_resolution`, `recon_saturation`). This test is the first one in
   file order to request them, and 29 other tests share them. The `1603fb367` trim already stopped
   its CALL from re-running the sweeps. Deleting or reordering the test would only move the 371 s
   onto the next test that requests the fixtures. So this is an equivalence, not a trim target. The
   real lever is the cost of the sweeps themselves.
2. `129.67s` and `124.99s call test_home_move_undeliverable_win.py`, the two forced `run_phase2b`
   legs. These were already trimmed to a 4-month window (`571a79e9f`, which is in the subject).
   cProfile of one leg, standalone, 234 s in `run_phase2b._main`:
   - `fabric_providers_for_book` takes **103 s**. It runs `build_fabric_series_for_site` ×137, which
     is book-wide and does not depend on the window.
   - `seasonal_gas_splits_for_book` takes **37 s**.
   - The settlement fold takes 22 s.

   So over half of each leg is a fixed cost of building fabric series for the whole book, and a
   shorter window cannot reach it. Trimming it would mean bounding fabric construction to the run
   window or caching it per process. That is a `simulation/` change for the sim lane, not a census
   edit, and it is handed on.
