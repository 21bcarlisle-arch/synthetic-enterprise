# [WORKER-FINDING] The gate's scratch space is RAM, nothing drains it, and exhaustion is reported as "git is not installed"

**Found:** 2026-08-12, unwedging the 18th publish wedge (the lint cause is separate and landed
as `4bee2bd47`). This is the SECOND, independent contributor found in the same episode.
**Disposition:** the instance is relieved (space reclaimed, measured below); the CLASS is
QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight — a `rm -rf` is a cleanup, not a
control (`feedback_a_ratchet_with_no_drain_is_a_cleanup_not_a_control`).
**Rank:** promote above backlog — this recurs on a clock, and it degrades the gate silently.

## Observed, with evidence

The publish gate, mid-cycle at 03:38 UTC:

```
[process_run] Publish gate: could not make the HEAD checkout a git repo: git is not installed
[process_run] Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
[process_run] Publish gate scope: VACUITY GUARD: scope resolved to 0 test file(s), below the
              floor of 20 -- a collapsed scope is green over nothing ... Full suite blocks.
```

`git` is installed. The rc=128 line, one line above, carries the real cause: **`cannot mkdir`**.
At that moment:

```
$ df -h /tmp
tmpfs           7.8G  6.4G  1.5G  82% /tmp
```

**`/tmp` is a tmpfs — it is RAM** (`reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs`). So the
6.4G in it was also 6.4G off the memory ceiling, on a box where `free` showed 3.4G available
with two suites live. Each HEAD checkout is ~139M and the gate makes a fresh one per cycle
("the reused HEAD checkout is DISABLED ... using a throwaway checkout for this cycle").

The occupants were overwhelmingly **leaked pytest fixture dirs from runs that had already
died** — 1,428 of them, `h24_*`, `sitelane_*`, `site_lane_r15_*`, `pymp-*`, timestamped 00:29
and 00:53, plus eleven `pytest-of-rich/pytest-N` trees where pytest's own retention policy
keeps three. Killed runs never run their teardown, and this gate's runs are killed routinely
(deadline kills are an established failure kind in `.publish_gate_state.json`).

Reclaimed, measured, touching nothing newer than 60 minutes and nothing under a live process:

```
/tmp  82% used, 1.5G avail   ->   52% used, 3.9G avail
free available: 3.4G         ->   5.9G
```

## Why this is a wedge cause and not just untidiness

The failure is **silent and self-worsening**. A failed checkout does not red the gate — it
collapses the scope to zero, which trips the vacuity guard, which **falls back to the full
suite**. So exhaustion converts every cycle into the slowest possible cycle, on a box that is
simultaneously short of the RAM the full suite needs, which raises the odds of the OOM kill
that is then recorded as a test regression
(`WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10`). Full suite →
more tmpdirs → less space → more full suites. Nothing in the loop drains.

The vacuity guard is behaving correctly and is not the defect: refusing to call an empty scope
green is exactly right. The defect is that a resource failure is laundered into a scope result.

## Two defects, ranked

> **DISPOSITION 2026-08-12 04:2xZ (landed `3e745e2a5`, pushed, receipt gate-rc 0).** Defect 1
> below is **narrower and worse than stated**, and is now FIXED. It is not that the sweeper's
> subject was "too narrow": for the pytest half the subject was **empty**. The sweep globbed
> `HEAD_CHECKOUT_ROOT/pytest-of-*` = `/var/tmp/pytest-of-*`, which cannot match — pytest builds
> its roots under `tempfile.gettempdir()` = `/tmp`. `53e82b105` moved the CHECKOUTS off the
> tmpfs (right for checkouts) and carried the tmpfs drain off with them, because one constant
> answered two questions. The sweep root is now derived from pytest's own rule; R15 both arms,
> oracle is `tmp_path`. Reach 0 → 8 live roots.
> Defect 2 below (the misleading `git is not installed`) is **still open**. A THIRD defect,
> measured while fixing this one, is filed separately and is why the exhaustion loop still
> closes: the drain's 3h age bound is longer than the ~80-minute fill, so restored reach
> reclaims nothing yet. Both in
> `WORKER_FINDING_THE_TMPFS_DRAIN_WAS_POINTED_AT_THE_WRONG_FILESYSTEM_2026-08-12.md`.

**1. The drain that exists covers one class out of several.** Correction to this finding's own
title, observed after filing — the publisher DOES sweep:

```
[2026-08-12 03:51 UTC] [process_run] Publish gate: swept 1 abandoned HEAD checkout(s) from
/tmp/pytest-of-rich/pytest-130/... -- these are the debris of runs that were killed before
their cleanup could run.
```

So the mechanism is not absent; its SUBJECT is too narrow. It reclaims abandoned *HEAD
checkouts* and had swept exactly one, while the 1,428 dirs actually holding the space were
`h24_*`, `sitelane_*`, `site_lane_r15_*`, `pymp-*` — pytest fixture dirs from other suites,
which no sweeper claims. This is the familiar shape (`feedback_control_set_hole_not_control
_defect`): not a broken control, a **hole in the control set**, and the narrow sweeper's log
line reads like the space is being managed.

The gate creates ~139M per cycle and deletes it only
on a clean exit it frequently does not get. Recommend widening that existing sweeper rather
than adding a second one: at cycle START,
remove `/tmp` gate/fixture dirs older than a threshold and not held by a live pid — start-time,
not exit-time, because the exit is the path that is missing. Guard it with a floor check that
FAILS LOUD when free space is below one checkout's worth, rather than proceeding into a
mkdir that will fail. (`/var/tmp` sits on the 893G disk and the live gate already uses it for
`publish-gate-head-*`; moving the throwaway checkouts there is the cheaper half of the same
fix and should be done regardless.)

**2. The error message names a cause it did not measure.** "git is not installed" is an
inference from a failed `git init`, printed beside the rc=128 that says `cannot mkdir`. It sent
this investigation toward a toolchain problem. Under R9 that string is an `inferred` claim
presented as `observed`. Recommend it report the rc and stderr it actually has, and check
`shutil.which("git")` before ever claiming the binary is absent.

## Related, already recorded

- `feedback_a_ratchet_with_no_drain_is_a_cleanup_not_a_control` — why the `rm -rf` I ran is not
  the fix.
- `feedback_truncated_pytest_is_an_oom_not_a_failure`, and
  `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10` — the downstream
  mislabelling this feeds.
- `reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs` — the fact that makes disk pressure into
  memory pressure.
- `WORKER_FINDING_A_TIMEOUT_CENSORS_THE_MEASUREMENT_THAT_WOULD_SIZE_IT_2026-08-10` — same
  shape: a resource limit corrupting a measurement rather than reporting itself.
