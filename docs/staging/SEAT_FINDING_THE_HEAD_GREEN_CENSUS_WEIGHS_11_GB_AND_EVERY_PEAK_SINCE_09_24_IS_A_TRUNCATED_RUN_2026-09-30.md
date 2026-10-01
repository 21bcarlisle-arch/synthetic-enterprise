**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the nightly census weighs 10.9 GB, and every peak recorded since 09-24 is a floor from a killed run

Found by Lane 0 `the-head-green-census-declares-a-measured-weight`, 2026-09-30.

**Measured.** `oom_watch.read_unit_memory_peaks_mb(unit="head-green-census.service")` returns 11 peaks
over the whole retained journal (09-20..09-30; `-30d` and `-365d` give the same set):

| nights | outcome | memory peak |
|---|---|---|
| 09-20, 21, 22, 23 | finished (NEW_RED 48/48/41/37) | 7.5G, 8.9G, 10.5G, **10.9G** |
| 09-24 .. 09-30 | killed at `SUITE_TIMEOUT_SECONDS` = 7200 s, UNPROVEN | 7.5G, 6.5G, 8.1G, 7.5G, 6.4G, 8.5G, 6.8G |

The last seven are floors on a truncated suite, not the job's size. The weight is the largest
*complete* run: `CLASS_WEIGHTS_MB["head_green_census"] = 11162`. That is 7x the scoped gate's 1,536 MB,
and the largest routine pytest resident on the box. It is a cgroup peak, so it counts page cache the
same way `sim_run`'s does.

**Done (this commit).**
- `CLASS_UNITS["head_green_census"] = "head-green-census.service"`, so `weight_drift` re-derives it.
  At real inputs it reads `matches` (11,161.6 observed across 12 samples).
- `CLASS_DRIFT_WINDOWS = {"head_green_census": "-30d"}`. A once-nightly unit leaves ONE peak in
  `DRIFT_WINDOW = -24h`. Against a 6.4G..10.9G spread, that makes the verdict a coin: "over" most nights
  and "matches" on the rest. `sim_run` keeps `-24h`.
- `tools.head_green_census.run_suite` runs its suite inside
  `resource_headroom.admitted("head_green_census")`. A refusal returns `""`, which reads as UNPROVEN
  and records nothing (the existing fail-safe). The reason goes on `observed["deferred"]` and into the
  verdict's own sentence. It is UNPROVEN, not NEW_RED, so it never pages. At real inputs tonight
  (nothing reserved, 19,973 MB available) it is admitted. So is census + `sim_run` (18,228 of a
  23,008 MB budget).
- Control: `test_the_census_suite_runs_only_when_admitted_and_holds_its_measured_weight` is one
  partition, with both branches asserted reached. Four mutations, each red: the suite runs outside
  `admitted`; a refusal is ignored; the `deferred` block is dropped from `main`; the per-class window is
  removed.

**Still owed, and it matters more than this weight.** The timeout finding
(`done/SEAT_FINDING_THE_NIGHTLY_HEAD_GREEN_CENSUS_HAS_TIMED_OUT_FOUR_NIGHTS_RUNNING_…_2026-09-27.md`)
was archived with its owed measurement undone. The census has now timed out **seven** nights running,
and `HEAD_RED_REGISTER.md` still reads "observed 2026-09-23". The nightly HEAD-green control has been
blind for a week. Handed on as a continuation: time the unscoped suite once, outside the unit, then
set the bound by the constant's own rule, or split the census.

A consequence for this weight: once a full run completes again, its peak will be the first honest
reading since 09-23, and the suite has grown since then. If it exceeds 11,162 MB, `weight_drift`
reads "under", which is the alarm doing its job.
