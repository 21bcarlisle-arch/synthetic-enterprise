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

Result: *pending — appended beside this prediction when the run ends.*
