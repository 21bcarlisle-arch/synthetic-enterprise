# The 14 fast-forward paths are all superseded by origin, and the reconcile waits for memory — 2026-09-29

**Item:** `clear-the-14-shared-tree-paths-that-hold-the-fast-forward` (lane 0). It also retires
`judge-the-stale-fold-noise-floor-test-copy-holding-the-shared-tree-fast-forward`, which is the
same subject under a second id.

**The premise was re-measured at 09:50Z. Nothing is left to land.** The shared tree is 1 ahead and
48 behind origin/main.

- **Modified (4).** `background/process_run_complete.py`, `simulation/arrears_engine.py`,
  `simulation/run_phase4c_on_phase2b.py` and `tests/background/test_process_run_complete.py` are
  byte-identical to origin/main. `git diff origin/main -- <path>` is empty for each. They differ
  from the shared HEAD only because HEAD is behind.
- **The holder work (1).** `tests/tools/test_fold_noise_floor_family.py` is now identical to the
  shared HEAD. Origin carries a later version of it. The 4 names the 08:08Z refusal said it held are
  no longer held by anything in the working tree.
- **Generated (1).** `CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md` is identical to origin. It is
  +1 line against HEAD.
- **Untracked drafts (8).** Five are byte-identical to origin's copies. Three differ:
  `SEAT_DISPOSITION_THE_SHARED_TREE_PIN_CENSUS_…`, `SEAT_FINDING_A_MULTI_ARM_RUN_REREADS_THE_WEATHER_STORE_…`
  and `SEAT_FINDING_EVERY_GENERATED_DAEMON_UNIT_NOW_RUNS_PYTHONUNBUFFERED_…`. Each paragraph the
  local copy seems to add is already in origin's copy of the same file. I checked this by searching
  origin for a unique string from each paragraph (`REFUSED_RACE\` at 06:59:16Z`,
  `weather-store-digest-in-each-arms-identity`, `noise-floor-seeds-reconcile-on-weather-store`,
  `manifest-log-silence-rows-reread-after-unbuffered`). Origin rewrote them later, so each local
  copy is the older one.

So all 14 paths are copies that origin/main supersedes. Clearing them loses nothing, and
`origin_reconcile` clears copies like these on its own.

**The one thing still holding the fast-forward is the ahead leg.** The shared HEAD is `a3b1ae3c5`,
the five-seed prereg. It is committed locally and not on origin. Origin has no copy of its file. The
reconcile therefore has to gate a merge. The last such gate ran for 43 minutes.

**I did not run it now: it would risk the running experiment.** At 09:50Z the box had 3,162 MB free
and 1,000 MB of swap. The two five-seed runs the prereg grades (`run_value_cycle_ab`, pids 3527043
and 3528271) held about 7.8 GB RSS each, an hour in. Neither `origin_reconcile` nor
`surgical_land` checks headroom. When memory runs out, the OOM killer takes the largest process,
which is one of those two runs. Losing one would cost that run, and the grade waits on both.

**Handed on:** `reconcile-the-shared-tree-after-the-five-seed-runs-finish`, embargoed to after the
runs are due. Done means `python3 -m background.origin_reconcile` has been run once the runs have
exited and headroom allows, and the shared tree has 0 behind. If it refuses, it names a path this
record does not already account for.
