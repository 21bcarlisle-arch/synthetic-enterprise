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

**1. Nothing drains the scratch space.** The gate creates ~139M per cycle and deletes it only
on a clean exit it frequently does not get. Recommend a drain the gate owns: at cycle START,
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
