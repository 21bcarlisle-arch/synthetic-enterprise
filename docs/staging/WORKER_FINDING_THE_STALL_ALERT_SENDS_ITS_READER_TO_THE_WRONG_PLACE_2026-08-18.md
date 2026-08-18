**Severity:** LATENT · **Lane:** H_harness

# The publish-stall alert reports "the publish path failing" when its own signal means no attempt was made

**Found:** 2026-08-18, triaging a director report of "publishing stuck again: one marker,
three cycles, rc=75".

**Class:** `measurements_that_mirror` — an instrument reporting its own blind spot as the
subject's failure.

---

## Observed, with evidence

The run-marker sweep fires this, verbatim, and has fired it at least four times (2026-08-13,
08-14, 08-17 twice, 08-18):

> Run-marker sweep has made ZERO progress for 3 consecutive cycles … Last publisher outcome
> for it: **rc=75 (lock-skipped, not attempted)** … so this is **the publish path failing**,
> not the retry loop stopping. **Look at the publish gate's blocking test** in
> `docs/observability/sim-runner-log.md`, not at the sweep.

The two halves of that contradict each other. `rc=75` is `EXIT_LOCK_SKIPPED`
(`background/process_run_complete.py:90`), emitted by the singleton guard at
`_run_lock()` — it means **another instance already holds the lock, so this attempt never
ran**. A run that never started cannot have failed a blocking test, and the alert sends its
reader to the gate log to look for one.

**What was actually happening, measured at 19:20 BST today.** A publisher was running
normally: PID 2212868, started 19:00, on that exact marker, executing its gate — the pytest
child (PID 2223970) had 4+ minutes of CPU. The gate's own scope line from the 18:13 cycle:

> Publish gate scope: 6 publish-path source(s) -> **146 blocking test file(s)** via the
> static import graph

on a **cold throwaway checkout** (the reused HEAD checkout is disabled after it produced four
false reds). So the publish is not failing. It is SLOWER THAN THE SWEEP'S PATIENCE: the sweep
re-attempts every cycle, the singleton correctly refuses it, three refusals trip a
"ZERO progress" threshold, and the alert concludes the publish path is broken.

`rc=75` is the one outcome that carries NO information about the publish path's health, and
it is the outcome this alert treats as proof of failure.

## Why it matters more than a wording fix

This alert is an `[ACTION NEEDED]` — it is meant to be the signal a human acts on. It has
fired four times across three days, and each time it directed the reader to a blocking test
that does not exist, while the real answer ("a publish is in progress and takes longer than
45 minutes of sweep cycles") was in the same log file. Two costs, both real:

1. **Attention spent in the wrong place.** The director raised it here as "publishing is
   stuck again", which is what the alert says. Nothing was stuck.
2. **A true stall would look identical.** If the publisher genuinely wedged, the sweep would
   emit exactly the same message with exactly the same rc. The alert cannot distinguish
   "someone is working on it" from "nobody can", which is the only distinction that matters.

## Not claimed (R9)

- **Not claimed that no publish has ever genuinely stalled.** The earlier occurrences were
  not re-examined; only today's was measured against a live process table. Whether 08-13,
  08-14 and 08-17 were also healthy-but-slow is *inferred* from the identical rc and message,
  not observed.
- **Not claimed the gate is too slow.** 146 blocking test files on a cold checkout may be
  exactly right for a publish gate. The defect is the alert's reading, not the gate's cost.
- **No claim about the sweep's retry logic**, which the alert correctly exonerates.

## The repair, not taken here (SELF-INTERRUPT DISCIPLINE)

The alert should branch on whether a publisher is ALIVE, which is a `ps`-checkable fact it
already has the means to establish:

* **an instance is running** → not a stall. Report it as a long publish, with its start time
  and elapsed, and do not raise ACTION NEEDED until it exceeds the gate's own known duration.
* **no instance is running and the marker is pending** → THIS is the stall, and the existing
  message is correct for it: look at the gate.
* **rc=75 with no live instance** → a stale singleton, a third state worth naming separately,
  because its repair is different again.

The mechanism must not be another prose threshold: the distinguishing fact is process
liveness, and a control that cannot see it will keep reporting the same sentence for all
three states.
