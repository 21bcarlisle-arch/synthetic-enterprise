# [WORKER-FINDING] An OOM-killed gate is recorded as a `test_regression` — the wedge detector names the wrong cause

**Found:** 2026-08-10, during the episode-4 publish-gate wedge draw (RUNG 1, PRIORITY ZERO).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. The wedge itself had a *different*, real
cause and is closed at `70d23b088`; this is about how the machine *describes* a wedge, and the
description was actively misleading for two cycles.

**Advances:** OPS2_publish_gate_head_worktree — the gate's subject is now HEAD, so the only
remaining way a green HEAD reads as red is a killed run, which is exactly this.

## Observed, with evidence

Two publish cycles this hour did not fail a test. They were killed:

```
- [2026-08-10 12:12 UTC] Publish gate RED (rc=-15) -- no FAILED/ERROR summary line found
- [2026-08-10 12:17 UTC] Publish gate RED (rc=-15) -- no FAILED/ERROR summary line found
```

`rc=-15` is SIGTERM. The cause is in the user journal, and it is the kernel, not a test:

```
Aug 10 12:45:39 Skynet systemd[409]: worker-tick.service: The kernel OOM killer killed some
                                     processes in this unit.
Aug 10 12:45:39 Skynet systemd[409]: worker-tick.service: Main process exited,
                                     code=killed, status=15/TERM
Aug 10 12:45:40 Skynet systemd[409]: worker-tick.service: Failed with result 'oom-kill'.
```

Eight kernel oom-kills in the last six hours, all `python3` at 2.4–5.7GB RSS, plus `llama-server`
at 6.2GB. The machine's real ceiling is **15.9GB** (WSL2), not the 32GB CLAUDE.md's "Technical
environment" section states, and swap is exhausted (4066 of 4096MB used, 4.4GB available).

**This is the mechanism that matters:** the kernel OOM killer picks *one* process in the cgroup;
systemd then tears down the rest of the unit with SIGTERM, so the surviving pytest child exits
`-15`. An OOM therefore presents to the gate as a plain SIGTERM with no summary line.

## The defect

`_record_publish_gate_outcome` filed both cycles as:

```
Publish-gate failure #7 (test_regression, rc=1) -- alert armed/cooldown
Publish-gate failure #8 (test_regression, rc=1) -- alert armed/cooldown
```

**`test_regression` is false.** No test regressed; the box ran out of memory. The consequences are
not cosmetic:

1. The episode counter (124 consecutive failures) mixes two populations — real red tests and
   resource kills — so "124 failures" overstates how long any *code* defect has been live.
2. The doorbell instructs the next worker to "DIAGNOSE the failing test". For an OOM cycle there
   is no failing test to find, and the recorded evidence (`no FAILED/ERROR summary line found`)
   is the *only* hint — one that already has a memory entry (`truncated pytest is an OOM, not a
   failure`) precisely because a previous worker was sent down this path.
3. It is fail-**open** in the direction that costs most: a run that never finished is scored as
   a run that finished and disagreed.

## Why this is not a duplicate of the filed flag

`ADVISOR_FLAG_RESOURCE_HEADROOM_GOVERNOR_2026-08-09.md` already owns the *prevention* half
(headroom watchdog + heavy-job concurrency budget + pricing the Qwen/llama retirement), and its
evidence is the same class of event. **This finding is the other half: classification.** Even
with a perfect governor, a kill will occasionally happen, and when it does the record must say
`resource_kill`, not `test_regression`. The governor stops the event; this stops the *lie about
the event*, and only the second one protects the next worker's hour.

## Contended, not just short of memory

Three heavy pytest residents were live concurrently in this window, by design and not by accident:
the publisher's own gate (every ~5 min), `publish-gate-subject-cost.service` (a one-shot that runs
the gate suite three times, ~50 min, started 12:22 and still waiting on the live publisher at
13:07), and the worker tick's own suite. The subject-cost measurement exists to price the gate —
and it is itself a third of the load that makes the gate unmeasurable. Worth naming in the
governor's design rather than discovering again.

## The work (not drawn here)

1. Classify by return code at the point of record: a negative rc (signal death) is
   `resource_kill`, never `test_regression`. `rc=-9` (SIGKILL/direct OOM) and `rc=-15` (SIGTERM /
   cgroup teardown) are the two shapes seen so far; a positive rc with no summary line is a third.
2. Carry the evidence R5 asks for: on a signal death, sample `free`/journal for an `oom-kill`
   result in the same unit and put it in the alarm payload, so the cause is in the record rather
   than reconstructable only by a worker who happens to know the class.
3. Keep the episode counter honest — either partition it by cause, or exclude resource kills from
   the "consecutive failures at HEAD" streak, because a kill says nothing about HEAD.
4. R15 both ways: a synthetic SIGTERM of the gate must record `resource_kill` and must NOT arm the
   test-regression alarm; a genuinely red test must still arm it.

---

*Filed by the scheduled worker tick, 2026-08-10, while closing the episode-4 wedge. The wedge's
actual cause was unrelated (a derived-artefact repair downstream of its own gate,
`70d23b088`) — these two cycles were noise layered on top of it, which is exactly why the
mislabel cost time.*
