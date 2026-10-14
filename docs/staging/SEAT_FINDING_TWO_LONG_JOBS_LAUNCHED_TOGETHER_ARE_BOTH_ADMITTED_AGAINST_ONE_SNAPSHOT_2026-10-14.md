# Two long jobs launched together are both admitted against one snapshot

**Fate (2026-10-14):** ATOM -- harness, next week: admission against one memory snapshot.

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Delivery seat, 2026-10-14, while launching `dvn480-seeds-a` and `-b` for
`SEAT_PREREG_THE_DEMAND_VECTOR_N_AT_480K_2026-10-14`.*

## What happened

Two `launch_long_job` calls were started a fraction of a second apart, each declaring
`--peak-mb 2000`. Both printed the same admission line:

    admitted: 20479 MB resident across 80 process(es) + 2000 MB declared peak = 22479 MB, against 23008 MB

The two together need 24,479 MB against a 23,008 MB budget, so on the door's own arithmetic the
second one should have been refused or queued. Neither launch counted the other.

## Why (read from the code, not run)

In `background/launch_long_job.py` the admission path calls `co_residence(peak_mb, residents(),
..., declared=declared_peaks(records_path))` with no lock around the census, the decision and the
record write. Inside `co_residence`, a declared peak lifts a unit only when that unit `if
members:` already has a process in the census. A sibling whose record is not yet written, or whose
unit has not yet spawned its process, is counted at 0 MB. `resource_headroom.queued` takes
`_ledger_lock` for exactly this reason. The long-job door does not.

## Why LATENT and not live

Here it cost nothing. With both legs running, `resource_headroom.sample()["available_mb"]` was
11,823 MB and PSI was 0.13. The door's "resident" counts declared peaks, which are well above
what the jobs actually hold. On a box that is really tight, the same race starts two jobs where
one fits. This box has 355 OOM kills on record.

## Smallest fix

Take `resource_headroom._ledger_lock` around census → decision → record write in the launch path.
Also count a declared unit with no live members at its full declared peak while it is younger than
a short grace period. The control is a test that launches two dry-run admissions under the lock
against a fixture census with room for exactly one, and asserts that exactly one is admitted.
Its mutation is removing the lock or the zero-member leg. Until the fix lands, launch
sibling legs one after another, waiting for the first launcher to print `cgroup: VERIFIED`.
