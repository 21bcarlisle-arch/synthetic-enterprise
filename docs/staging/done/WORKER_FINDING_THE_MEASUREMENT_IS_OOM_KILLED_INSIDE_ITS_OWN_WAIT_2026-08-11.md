> ## ⚠ REFUTED BY THE KERNEL LOG — 2026-08-11, OPS2 tick
>
> **The central claim below — "It died in the wait, not in the suite" — is WRONG**, and it was
> filed as `observed`. The more direct evidence (R9) is `journalctl -k`, which nobody had read:
>
> ```
> Aug 10 23:11:10 kernel: Out of memory: Killed process 3272589 (python3)
>                         total-vm:12949376kB, anon-rss:12928996kB
> Aug 10 23:11:10 kernel: oom-kill:constraint=CONSTRAINT_NONE ... global_oom,
>                         task_memcg=/user.slice/.../publish-gate-subject-cost.service
> ```
>
> The unit's own python was pid **3244117** (`journalctl --user -u publish-gate-subject-cost`).
> **3272589 is its CHILD** — the BASELINE phase's pytest, 12.9G anon RSS on a 15.9G box. The
> launch had already taken the run lock and **was in the suite**. The kill was a GLOBAL oom
> (`CONSTRAINT_NONE`), not a cgroup-limit one.
>
> **Both "unexplained numbers" below are explained by that one fact.** 17 min of CPU is a pytest,
> not a poll loop. 13.3G is that pytest, not a process holding a lock.
>
> **The proposed repair would not have fired.** A memory guard inside the acquire poll guards a
> loop the run had already left.
>
> **Why the misread was reasonable, and what was actually defective.** Every signal available
> said WAITING: the phase banner prints *before* the wait, there is no log line for ACQUIRING
> the lock or for starting a suite, and `last_heartbeat` is stamped only from the three wait
> loops — so the artefact freezes the instant work begins and stays frozen for ~20 minutes. The
> instrument could not distinguish "still waiting" from "working, and killed at it". That blind
> spot, not the acquire poll, was the defect.
>
> **Fixed** (this tick): `_InFlight` in `tools/measure_publish_gate_subject_cost.py` carries
> phase + stage + MemAvailable in the record continuously and checkpoints on every stage change,
> so a killed launch leaves a diagnosis; the next launch republishes it as
> `previous_launch_died_in_flight`. A lock-acquired line and a suite-starting line now exist in
> the journal too. R15 both ways, mutations run not asserted:
> `tests/tools/test_measure_publish_gate_subject_cost.py` (7 new tests) — a no-op `stage()`, one
> literal for every stage, a dropped `clear()`, and a read moved below the first checkpoint each
> red a named test.
>
> **The residual is real and is NOT this finding**: the suite genuinely reaches 12.9G. Filed
> separately as `WORKER_FINDING_THE_MEASUREMENTS_SUBJECT_IS_LARGER_THAN_THE_GATES_2026-08-11.md`.
>
> Everything below is left VERBATIM. It is a good record of a wrong conclusion honestly reached,
> and the lesson is in the gap between it and the kernel log.

---

# [WORKER-FINDING] The OPS2 measurement is OOM-killed inside its own wait, before the deferral that was built to survive this (2026-08-11)

**Rank:** backlog (P-1: this does not outrank the OPS2 exit itself, which it blocks intermittently
rather than absolutely — the resume banks phases and the next launch continues).
**Lane:** `H_harness` · **Class:** a guard whose survivable path is never reached.
**Filed from:** the OPS2 tick of 2026-08-11, per SELF-INTERRUPT DISCIPLINE — queued, not fixed on
sight.

## Observed (R9 — from the unit's own journal, not inferred)

```
Aug 10 22:28:49 Skynet systemd[409]: Started publish-gate-subject-cost.service
Aug 10 22:28:49 [measure] phase 3/3 BASELINE -- the live working tree, the pre-ruling subject
Aug 10 22:28:49 [measure]   . waiting to TAKE the publisher's run lock (not merely for a gap)
Aug 10 23:11:10 Skynet systemd[409]: publish-gate-subject-cost.service: The kernel OOM killer
                                     killed some processes in this unit.
Aug 10 23:11:10 Skynet systemd[409]: Failed with result 'oom-kill'.
Aug 10 23:11:10 Skynet systemd[409]: Consumed 17min 4.287s CPU time over 42min 20.971s wall
                                     clock time, 13.3G memory peak, 1.5G memory swap peak.
```

The last thing it logged was entering `_publisher_exclusion`'s acquire poll. It never logged a
phase start, and `publish_gate_subject_cost.json` banked nothing from that launch. **It died in
the wait, not in the suite.**

## Why this is a finding and not just a busy box

`_publisher_exclusion` was built (2026-08-10, ninth launch) precisely so that losing the race for
the box is **survivable**: the acquire deadline is `QUIET_WAIT_SECONDS` = 3800s, after which it
raises `_Deferred`, banks what it holds, records `deferred.reason` and exits 0. That trade assumes
**the loser of the race gets to defer.** This one was killed at ~2540s — *inside* the deadline —
so the deferral path did not run, and the artefact carries no reason at all. A guard whose
survivable branch is unreachable under the condition it exists for is the shape R15 names.

## Two numbers in that journal line are not explained

Both are `observed`; the explanations below are `inferred` and untested.

1. **17 minutes of CPU for a 30-second poll loop.** `_publisher_exclusion` polls
   `LOCK_EX | LOCK_NB` every `QUIET_POLL_SECONDS` = 30s and calls `heartbeat()` each time — and
   `heartbeat` is `_checkpoint`, which re-serialises the whole record and rewrites the file. That
   is ~85 wakeups over 42 minutes. It should be milliseconds of CPU, not 17 minutes. Something in
   that loop is doing real work; a candidate worth checking first is `_publisher_is_running()` /
   `_ancestor_pids()` if either walks `/proc` per poll, but **this has not been measured.**
2. **A 13.3G memory peak on a 15G box, for a process holding a lock.** The unit's cgroup should
   contain only the waiting Python process at that point. Either the peak is being attributed
   across a boundary this reading assumes (a child that was never logged), or the wait is not the
   only thing running in the unit. Note `/tmp` is a **tmpfs** on this box — pages charged to a
   cgroup that writes there are RAM, and the reused checkout lives at
   `/tmp/publish-gate-head-reused`.

## Nearest working analogue (R4)

`_wait_for_memory_headroom` already exists and already defers on low `MemAvailable` — but it
guards the moment *before a phase starts*, not the acquire poll. The acquire poll has a time
bound and no memory bound. The diff is one guard, in one loop, on a condition the harness already
knows how to evaluate.

## Suggested shape (not built)

Fold the memory check into the acquire poll so the loop can defer on the condition that is
actually killing it, rather than only on elapsed time. Add `MemAvailable` at deferral to the
record, so a future kill leaves a diagnosis instead of a gap. **First, measure** — the two numbers
above should be explained before anything is changed, or the fix will be aimed at the inferred
cause rather than the observed one.

## Related

* `docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md` — the atom; this blocks its criterion 1
  intermittently.
* `feedback_a_wrapper_timeout_below_the_work_it_wraps_decides_the_verdict` — the same family: a
  bound that decides an outcome it was meant to observe.
* `feedback_truncated_pytest_is_an_oom_not_a_failure` — the OOM killer is a known visitor here.
* `reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs`.
