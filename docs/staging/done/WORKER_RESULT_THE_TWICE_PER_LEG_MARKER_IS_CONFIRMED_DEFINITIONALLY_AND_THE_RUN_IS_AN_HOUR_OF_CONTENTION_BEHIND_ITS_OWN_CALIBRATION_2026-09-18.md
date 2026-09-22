# The twice-per-leg marker is confirmed definitionally, and the run is an hour of contention behind its own calibration

**Date:** 2026-09-18 (00:37–00:50 BST)
**Lane:** A_strategy_governance (drawn as LANE 0 DELIVERY —
`read-the-next12-twelve-alone-after-the-measured-1131-eta-and-give-the-run-a-per-seed-progress-line`)
**Subject:** `tools/run_value_cycle_ab.py` (`noise_floor`); `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
**Severity:** LATENT — nothing published moves. The primary half of the item is not yet answerable;
the secondary half is landed and mutation-proven.

---

## The premise, re-measured on real disk state

The item was drawn at **00:37**, ten hours before its own stated floor of *"DO NOT DRAW BEFORE
10:45"*. So the primary half could not be done, and this turn did not attempt it.

```
$ ls /var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json
ls: cannot access ...: No such file or directory
$ ps -o lstart=,etime= -p 3819244
Thu Sep 17 19:11:33 2026    05:31:04
```

The run is **alive and working**, 5h31m in. Neither named artefact exists. The two commits the
item cites (`5ce5c3c31`, `e06ada3cc`) are ancestors of `origin/main` as the premise check said —
but they are the item's *basis*, not its deliverable, so the premise is **not spent**: the twelve
have not been read because they do not exist yet.

## The twice-per-leg claim is now definitional, not inferred

The item asserts `Starting treasury` fires twice per arm-leg. That was previously an inference from
two `print` sites. It is now measured against the **completed** sibling run, which runs
byte-identical value-arm code:

```
$ grep -c 'Starting treasury' /var/tmp/floor_auc_20260917.log
18                              # 3 seeds x 3 arm-legs = 9 legs  ->  exactly 2.00 per leg
```

Two print sites, both reached, every leg. `simulation/run_phase2b.py:1258` and `:3436`. The
seven-hour ETA error is fully explained.

## And the same ruler says 11:31 is the OPTIMISTIC end of a bound, not a point estimate

The sibling's own wall clock confirms the item's calibration exactly:

| | legs | wall clock | min/leg |
|---|---|---|---|
| sibling `floor_auc` (completed, clean machine) | 9 | 229.9 min | **25.54** |
| live `next12` (in flight, 21 prints → 10.5 legs) | 10.5 | 331.1 min | **31.53** |

The live run is **23% slower than the code it was calibrated against**, and the cause is on the
clock: `next12` started **19:11:33** and the sibling did not finish until **20:11:44** — so its
first **60.2 minutes** were two full value-arm runs competing for one machine. The calibration was
taken off a run that had the machine to itself; the run it was applied to did not.

With 25.5 legs left at 00:42, that gives a two-sided bound rather than a time:

- **11:33** if the remainder runs at the sibling's clean rate (the contention is behind it — likely)
- **14:06** if the whole-run average holds (it should not, but it is the measured upper end)

**11:31 is the floor of that bound, not its centre.** A draw at 10:45 that expects the file may
still find it absent. I am not revising the item's prediction — it is filed, and the one-variable
explanation for the gap is the contention window, which is measurable and was not the item's error.

## What landed

`noise_floor` printed **nothing per seed**, which is why every reader so far guessed progress off
an incidental marker. Now, flushed, one line per completed seed:

```
[noise_floor] plan 12 seeds key=elasticity mode=all -- one `i/12` progress line follows per COMPLETED seed
[noise_floor] seed 3/12 done seed_id=3100003 took=4598.1s elapsed=13794.3s mean_per_seed=4598.1s(n=3) eta_remaining=41383.0s draw_calls=2431 draws_redrawn=2431
```

Three properties, and the controls are keyed to these rather than to the wording:

1. **The count is stated, never counted.** The line carries `3/12`. A reader does not count
   occurrences of anything, so no marker frequency can mislead them.
2. **The ETA is derived from the seeds that finished** — `elapsed / index`, never from a per-seed
   cost written down in the module. A written-down 25.54 min/leg is precisely what went stale
   above.
3. **The line precedes the per-seed guards**, so a run that dies on seed 9 of 12 says so in the log
   instead of looking like a run still working on seed 9.

### The control caught a real defect in this very change

The plan line originally interpolated `_FLOOR_PROGRESS_MARK` into its own text to be helpful —
making the run-level preamble match the per-seed marker and putting every count exactly **one
over**. That is the twice-per-unit defect again, one size down, introduced by the fix for it. It
went red on first run and the code was changed, not the test.

### Mutation-proven (in `~/.cache` extract, not the shared tree)

| mutation | fires |
|---|---|
| per-seed line deleted | 3 controls red |
| plan line quotes the per-seed marker | 1 red *(fired live, on the real instance)* |
| `mean_seconds = 4598.0` (written-down calibration) | 1 red |
| `enumerate(seeds, start=0)` | 3 controls red |
| index guard disarmed (`if False`) | 1 red |
| per-seed line relocated below the guards | 1 red |

`tests/tools/test_value_cycle_ab_noise_floor.py` — 85 passed.

## The honest limit on this

**The run in flight cannot benefit.** PID 3819244 imported `tools/run_value_cycle_ab.py` at
19:11:33 and holds the old module in memory; editing the file does not reach it. The next floor
run is the first one that will print a countable line, and until then progress on *this* run is
still read off the twice-per-leg marker — correctly, now that the divisor is established.

## Still owed (primary half, unchanged)

Read the twelve **alone** — mean, sem, sems-from-zero, and the **sign** of `selection_gbp` — copy
the artefact into `docs/observability/`, check the five prereg identity rows, and only then add
`..._auc3_...json` for the pre-registered secondary fifteen. The filed prediction stands: if the
twelve's mean lands **positive**, or its sign is not negative, `NOISE_FLOOR_PATH` in
`tools/generate_value_arms_data.py` is the first thing to re-open.
