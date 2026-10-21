**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-nightly-test-census-holds-the-box-through-the-arm-window`)

# The nightly census already asks admission, and its only lever on the arms is its peak

**Found by** the delivery seat on 21 Oct 2026, working the direction item. The item offered three
changes. Two of them were already in place or had nothing to act on. The third has nothing
behind it in the data.

## Measured

The last seven firings of `head-green-census.service`. Peak is systemd's cgroup peak, read with
`oom_watch.read_unit_memory_peaks_mb`. The journal keeps runs from 10-16 onwards.

| night | peak | wall | outcome |
|---|---|---|---|
| 10-16 | 11.7G (11,981 MB) | 3h49m | ran |
| 10-17 | 11.5G | 4h02m | ran |
| 10-18 | 11.5G | 3h40m | ran |
| 10-19 | 10.0G | 4h50m | ran |
| 10-20 | 1G | 4s | deferred by `resource_headroom`: 15,256 MB declared + 11,162 > 23,008 |
| 10-21 | 9.35G at 3h14m, still running | — | admitted 03:31 BST |

**Pytest workers: one.** `pytest_argv()` passes no `-n`. The 11 GB is a single process and its
children: 3.7 GB anon and 1.8 GB page cache at 06:45 BST. It is not a pool of workers.

## The three options, and why each is spent or rejected

1. **Cap its workers.** There is only one worker, so there is nothing to cap.
2. **Run it through admission.** This has been done since 2026-09-30. `run_suite` holds
   `resource_headroom.admitted("head_green_census")` for the whole suite. 10-20 shows the refusal
   path firing. The control the item asks for already exists:
   `test_the_census_suite_runs_only_when_admitted_and_holds_its_measured_weight` asserts that
   the reservation's weight equals `CLASS_WEIGHTS_MB["head_green_census"]`. So the census is
   *inside* the register, not outside it.
   **The one defect was the weight.** It was declared at 11,162 MB and observed at 11,981 MB.
   `weight_drift` has read "under" on every run since 10-02, which is fail-open. This commit
   re-derives it to 11,981.
3. **Move it to a window the arms do not use.** I summed declared long-job MB by UTC hour over
   10-07..10-20 (200 launch records). The census's current slot, 02:30–06:30Z, is already the
   lowest: 1.5–3.5 GB on average, against 4–6.6 GB at every other hour. That low is partly the
   census itself deferring launches, so the number is confounded, but no other window is shown
   to be emptier. This option is rejected.

## What the morning actually was

`per-customer-switch-arms-8fbb641d8` was launched at 03:26:21Z and its unit started in the same
second, so **it did not wait.** The jobs that died queued were the opex-credit arms and the
bad-debt switches-off arm (`be60ad914`). At 05:20Z the box held the census (11,162), that arm
(7,000) and the sim-runner founder run (~6–7 GB). Without the census, one more 7 GB arm would
have fit.

## The lever that remains: the peak

Budget 23,008 MB. Printed at real inputs:

| beside the census | at 11,162 | at 11,981 |
|---|---|---|
| one 7 GB arm | 18,162 fits | 18,981 fits |
| two arms | 25,162 NO | 25,981 NO |
| arm + sim_run | 25,228 NO | 26,047 NO |
| arm + two commit gates | 22,542 fits | 23,361 NO |

For the census never to delay a registered arm, its peak has to fit beside **an arm plus a
sim-runner cycle**. That means about **8.9 GB or less** (23,008 − 7,000 − 7,066). It needs to come
down by about 3 GB.

**Prediction, written before any measurement.** Running the suite as one pytest process per
top-level `tests/` directory, in sequence, will bring the cgroup peak below 8.9 GB. The reason:
the growth is caches that live for the whole process, not any single test's working set.
**Refuted if** the largest single-directory run peaks above 8.9 GB on its own. In that case the
peak belongs to a few heavy modules, and the remedy is their own `HEAVY_IGNORES`-style handling.

**Not built this turn.** Each measurement costs a whole suite's box-hours, and the arms are using
the box right now. The verdict parser also has to sum several pytest summaries without inventing
an UNPROVEN, and that change needs its own controls. It is handed on as a continuation.
`/var/tmp/census_mem_20261021.log` is sampling tonight's anon/file split every 20 s until the unit
exits. It gives the first reading of how much of the peak is page cache.
