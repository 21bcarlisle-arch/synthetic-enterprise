**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the census bound fell under twice its worst run on 09-22, and nothing noticed, because the worst run is moved by hand

Found by Lane 0 `the-head-green-census-suite-duration-is-measured-and-its-bound-follows`, 2026-09-30.

**Measured from systemd's journal** (`journalctl --user -u head-green-census.service`, unit wall clock):

| night | wall | CPU | outcome |
|---|---|---|---|
| 09-22 | 1h52m49s | 1h59m35s | complete |
| 09-23 | **1h59m31s = 7171 s** | 2h07m25s | complete, 29 s under the 7200 s bound |
| 09-24 .. 09-30 | 2h02m–2h03m each | 2h05m–2h06m each | killed at `SUITE_TIMEOUT_SECONDS` = 7200, UNPROVEN |

CPU time tracks wall time every night, so the suite is slow and compute-bound, not hung. The bound's
own rule (`bound > 2 x worst measured`) was already broken on 09-22. `WORST_OBSERVED_SUITE_SECONDS`
still read 3537 (09-02), because it is moved by hand and nobody moved it. So
`test_the_census_timeout_clears_the_duration_it_has_observed` stayed green against a number that was
three weeks stale. That is the literal-bound shape: the control was keyed to the answer on the day it
was written, not to the property.

**Done (this commit).**
- `WORST_OBSERVED_SUITE_SECONDS = 7171.2` (the 09-23 unit wall clock; it includes the checkout, so it
  over-states the suite).
- `SUITE_TIMEOUT_SECONDS = 14400`, and the unit's `TimeoutStartSec = 14700`. From the 03:30 timer,
  the run ends by 07:35.
- The installed unit `~/.config/systemd/user/head-green-census.service` was copied from the repo copy
  and `daemon-reload`ed (`TimeoutStartUSec=4h 5min`). To reverse it, restore
  `/var/tmp/head-green-census.service.pre-2026-09-30.bak` and reload.
- Mutation: `SUITE_TIMEOUT_SECONDS` set back to 7200 makes the control red.

**IT IS INERT TONIGHT unless the shared tree advances.** The unit runs from
`/home/rich/synthetic-enterprise`, and that checkout sat at `aebaaa344` at 19:49Z, behind origin by
`be2a0c202` and `75363670c`. The same gap means `resource_headroom.admitted` did not exist there, so
the memory admission those commits landed is ALSO not running in the nightly unit. A driver that
imported the shared tree's `admitted` died with `AttributeError`. The installed unit's 14700 s is
live, but the suite's own clock is whatever the shared tree's `tools/head_green_census.py` says. The
nightly run still stops at 7200 s until the reconciler brings the shared tree forward.

**Measurement in flight, and its pre-registration.** This was written at 19:52Z, after launch and
before any result. It is one unscoped run of `pytest_argv() + --durations=80` against a clean HEAD
checkout (`aebaaa344`, no overlay shortfall). The run is the transient unit `longjob-hgc-suite-timing`,
logging to `/var/tmp/hgc_suite_timing2.log`, and it has no timeout.
- PREDICTION: it completes in **7,300–9,500 s**. The suite has grown since the 7171 s run, and
  sim-runner and the other lanes are co-resident.
- 14,400 s holds the rule only for a run under **7,200 s**. The prediction says it will NOT hold, so
  the bound moves again when the result lands, and `WORST_OBSERVED` moves to the measured figure.
  If 2x the result plus 300 s no longer fits between 03:30 and 08:00 (about 16,200 s, so a run over
  about 7,950 s), the census is split into two scoped halves instead.
- The `--durations` table names what grew. That table, not this bound, is where the suite gets cheaper.

**Result (22:14Z, written after the run ended). The prediction HELD.**
`28 failed, 36151 passed, 48 skipped, 1321 deselected, 15 xfailed in 8626.87s`, `ELAPSED_SECONDS 8646.7`.
That is inside the 7,300–9,500 s band, and more than 7,200 s, so the bound moved again, as the
prediction said it would.

- `WORST_OBSERVED_SUITE_SECONDS = 8646.7`, `SUITE_TIMEOUT_SECONDS = 17400` (> 2 × 8646.7 = 17293),
  unit `TimeoutStartSec = 17700`. The installed unit was re-copied and `daemon-reload`ed, and now
  reads `TimeoutStartUSec=4h 55min`. To reverse it, restore
  `/var/tmp/head-green-census.service.pre-17700.bak` and reload.
- Mutation: `SUITE_TIMEOUT_SECONDS` set back to 14400 reds
  `test_the_census_timeout_clears_the_duration_it_has_observed`.
- **The split branch triggered and I did not take it. The reason is that its trigger was
  unsourced.** The "03:30 to 08:00" night edge in the prediction above named nothing that actually
  runs at 08:00. The only hard limit is the next firing, 24 h away. A healthy run ends near 05:55,
  and the 17,400 s bound only binds on a hang, which it now catches by 08:20. Splitting the census
  would change what a verdict covers. Nothing measured asks for that.
- **The cheaper remedy is in the durations table, not in the bound.** Four tests take 1,231 s
  together: `test_couple_w2_11_d5::test_cli_runs_and_prints_all_three_gaps` 356 s, two
  `test_home_move_undeliverable_win` tests at 297 s and 295 s, and the
  `test_value_chain_credit_feed_wiring` setup at 284 s. Six `tests/background/` brief/sweep tests
  take about 152 s each, 915 s together, which reads as one shared slow fixture. Together these ten
  are about 25 % of the suite.
- **The 28 reds are the first HEAD-green reading since 09-23.** They are what
  `HEAD_RED_REGISTER.md` has been blind to. Among them: 8 in `tests/harness/test_premise_two_level.py`
  (the premise two-level fidelity corrections, already a 09-30 worker finding); 4
  `launch_long_job` "undeclared peak" refusals; and `test_head_green_census.py:606`. That last one is
  this checkout's own artefact: `aebaaa344`'s 7500 against the installed 14700.
- **Still conditional on the shared tree advancing.** At 22:15Z `/home/rich/synthetic-enterprise`
  sat at `940e9ee86`, 10 behind origin, with `SUITE_TIMEOUT_SECONDS = 7200`. If the reconciler has
  not moved it by 03:30, tonight is killed at 7,200 s again under a 17,700 s unit. That is UNPROVEN,
  and it is not silent.
