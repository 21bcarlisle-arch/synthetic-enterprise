**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The operational-layer timeout is SLOW, not blocked — and the subject it names is where the clock stopped, not what stopped it

Drawn 2026-09-10 as RUNG 1b (PRIORITY ZERO), the operational-layer TIMED-OUT self-refill. The draw
set two questions in order: re-run the signal first (a fix may already have landed), and then
settle blocking-vs-slow **on evidence** before deciding anything.

---

## 1. The re-run — NOT green, so the draw is not discharged

The draw's first branch does not apply. The hourly daemon run (PID 1744118, `deadmans_switch.py`,
19:32:43–20:02:43 UTC) timed out again:

```
consecutive_red: 6, last_result: "red_timeout",
timed_out_at: "tests/background/test_supervisor.py::test_stuck_escalation_survives_daemon_restart"
```

**The `-v` subject payload landed at HEAD (59a91d4a2) works on its first live firing.** Sixteen
prior timeouts named nothing; this one names a test. That leg of the previous turn's work is
confirmed in production, not just in its own unit test.

*Process note:* my own `force=True` re-run launched a **second** copy of the same suite alongside
the daemon's in-flight one, under a 900s bash wrapper that would have killed it before its own
1800s timeout could produce a subject. I killed it. A forced re-run of this signal must first check
whether the hourly run is already in flight — two copies starve the box, which is the 2026-08-21
failure mode the draw explicitly warns about.

## 2. Blocking vs slow — SETTLED: it is SLOW. Four independent legs.

1. **The process was CPU-bound, not waiting.** At 22 minutes elapsed: `State: R (running)`,
   100% CPU, 18:53 of CPU time consumed, `wchan` 0. A run blocked on a lock, a socket or a
   `join()` sits at ~0% CPU in `S`/`D`. This refutes the blocked-on-a-waiter class outright.
2. **The box was not contended.** 16 cores, load average 5.76, one other lane's pytest pinning a
   single core. The timeout is not starvation by a sibling.
3. **The named test passes.** Run alone it is **PASSED in 128.54s** — the whole of it in the `call`
   phase (setup and teardown both < 0.005s). It does not hang.
4. **The signal has RECOVERED three times in 63.3 hours**
   (`WORKER_FINDING_REPEATING_ALARM_OPERATIONAL_LAYER_SIGNAL_2026-09-10.md`). A suite that had
   simply outgrown its budget goes red and *stays* red; every recovery is proof the whole suite
   completed inside 1800s. This is the leg that needs no instrumentation at all, and it was
   already in the record.

**So this is the cadence question the director named on 2026-08-21**, and the draw's own ruling
applies: prefer narrowing what it runs to raising the budget, because raising the budget is the
move that produced this state.

## 3. The subject names where the clock stopped, NOT the cause

This is the part that would mislead the next reader, so it is stated plainly.

`test_stuck_escalation_survives_daemon_restart` takes ~128s and **passes**. I read the live run's
own output while it was still in flight, through `/proc/<pid>/fd/1` — under `--capture=fd` pytest
redirects the running test's stdout to a temp file it truncates between tests, so the capture's
first timestamp dates the *current* test. It read 20:00, and the budget expired at 20:02:43: the
killed test was ~2 minutes into its ~2.1-minute runtime. It was not stuck; it was simply the test
under the clock when the clock ran out.

*(That `/proc/<pid>/fd/1` read is worth keeping as a technique: it gets a running suite's per-test
output live, without waiting for the run to end or adding any load to it.)*

**`timed_out_at` is a landmark, not a defendant.** The payload is still worth having — it tells you
*where in the suite* the budget ran out, which is how I found the module below — but a reader who
treats it as the culprit will "fix" a passing test. The next timeout will name a different test for
the same underlying reason.

## 4. What is established about the cost

The operational suite's cost is concentrated in tests that drive **real** `supervisor.run_cycle()`
calls in a loop. `supervisor.STUCK_THRESHOLD_SECONDS` is 3600 and the tests' `_STEP` is 120, so
each loop runs **30–40 cycles**. `tests/background/test_supervisor.py` contains **nine** such loops
(lines 1853, 1876, 1973, 1991, 2016, 2024, 2045, 2072, 2161) — on the order of 300 real supervisor
cycles in one module, one of which is measured at 128.54s.

**The whole-module measurement is the number that decides this.** Run under a 1700s cap, on the
same box and under the same concurrent load the signal itself faces:

```
tests/background/test_supervisor.py -q --durations=15
-> 132 of 201 tests in 1700s, KILLED at the cap without finishing.
```

**One module does not complete inside the budget allowed for the entire operational suite** (1800s).
That is sufficient on its own: no arrangement of the remaining operational tests can fit alongside
it, so the suite's timeouts do not need any further cause. The interleaved greens are then simply
the runs where this module's tail happened to fall the right side of the clock — which is also why
the flap tracks nothing anyone changed.

*Caveat, stated rather than buried:* this run shared the box with the publish gate's own full
non-operational suite and another lane's `tests/simulation` run. That is the realistic operating
condition for this signal, not an artefact — but the same module solo would be faster, and I have
not measured that. The 132/201 figure is an upper bound on throughput under load, not a clean
single-process timing.

## 5. What is NOT established — the honest gap

**I cannot yet attribute the ~4.3s per `run_cycle()`.** A faithful replication of the test's
isolation *including* its `_FakeClock` runs one cycle in **0.081s** — fifty times faster than the
cycle inside the real test. So the cost lives in a path my replication does not reach; the
difference is the agenda being set to a stuck state and the escalation tracker ageing across
cycles, which I have not yet isolated. I am not guessing at it, and the narrowing decision in §7
does not depend on it.

## 6. Two of my own predictions were wrong, and one measurement damaged the tree

Pre-registered before the answer existed, in
`docs/observability/operational_layer_timeout_prereg_2026-09-10.md`:

- **Prediction 1 (specific nodeid): WRONG.** I named `tests/background/test_worker_tick.py` and two
  others. The answer is `tests/background/test_supervisor.py`, which my grep never returned —
  it drives the producer without naming any of the strings I searched for. *A grep for a name is
  blind to the mechanism.*
- **Prediction 2 (it will name a test, not `IN_COLLECTION`/`NO_OUTPUT`): CORRECT.**
- **Prediction 3 (cost scales with the 140-doc staging queue): REFUTED.** The autouse `_isolate`
  fixture stubs `supervisor.STAGING_DIR` to `tmp_path`. I checked before building on it.

**Tree side effect I caused, recorded so it is attributable.** Measuring `run_cycle()` by hand —
outside pytest, with the real clock and a stubbed sync stamp — triggered the RC3 origin-staging
sync, which pulled **394 origin-staged documents** into `docs/staging/` (root went 140 → 430) via
402 git subprocesses. This is *not* what the real test does: under the test's `_FakeClock`,
`time.time()` returns ~120 against a real stamp of ~1.789e9, so the sync throttle returns early and
the pull never happens. The documents are all origin content, `background/supervisor.py` is running
as a live daemon (PID 1810653) and performs this same sync on its own poll, so they would have
arrived within minutes regardless — deleting them would be churn the daemon immediately undoes.
**They are left in place deliberately.** I did not touch the shared index: 22 paths were already
staged there by other lanes before this turn.

**And it did real damage, which I then had to repair.** A second profiling run stubbed *both*
`STAGING_DIR` and `ORIGIN_STAGING_SYNC_STAMP` to `tmp_path`. The sync builds its "already have it"
set from `STAGING_DIR` — including `done/` and `in_progress/`, precisely so a consumed doc is not
re-materialised — but it **writes to `PROJECT_DIR / "docs/staging/..."`, the real path, regardless**.
With the read side pointed at an empty tmp directory, the `done/` exclusion did nothing, and the
sync **resurrected 8 root documents another lane had archived (root→done) in the working tree but
not yet committed**. That produced 8 TWO ROOMS conflicts and turned `background/finding_classes
--check` — a cheap gate that blocks *every* lane's commit — red.

Repaired: I proved each resurrected root file was byte-identical to its HEAD blob (so removal is
recoverable from HEAD and from origin), removed the 8, and re-ran the gate: **PASS (0 failures)**.
I did *not* try to merge the two copies — origin's root copy is the fuller one (it carries a later
`SETTLED` amendment the local `done/` copy lacks), and reconciling that is the owning lane's call,
not mine to decide from inside an unrelated measurement.

*Two reusable lessons. First: calling a daemon's cycle function by hand is not a read-only
measurement — `run_cycle()` writes to the shared tree, and only the test fixture's fake clock was
holding that back. Second, and the one worth keeping: **`_sync_origin_staging` reads through
`STAGING_DIR` and writes through `PROJECT_DIR`.** Stubbing the module attribute isolates the read
side only, so isolation that looks total is half a seam — and the half that escapes is the half
that writes. Any test that lets this function run with a stubbed `STAGING_DIR` and a stale sync
stamp will overwrite the real staging queue. That is a latent defect in the producer, not just a
hazard of my harness, and it is the one thing here worth fixing in code.*

## 7. The decision

**Narrow what the signal runs; do not raise the budget.** Specifically, and in this order:

1. **The 1800s budget stays.** Raising it is the move that produced this state, and the check
   holding the box for its full timeout is what starved the publish gate on 2026-08-21.
2. **The looping supervisor-cycle tests are the narrowing target**, not the operational marker as a
   whole. They are the only tests here that pay ~30–40 real cycles to assert one transition, and
   they are the reason the suite's tail is minutes rather than seconds.
3. **Attribute the per-cycle cost before changing any test** (§5). The one thing that must not
   happen is a "fix" to the passing test the payload named.

The shape to reach for, when someone picks this up: these tests spend 30–40 real cycles to assert
**one** transition, because the escalation mechanism is wall-clock-based and `_FakeClock` advances
`_STEP` at a time. The property under test is "the tracker survives a restart", and that does not
require walking every intermediate cycle — a shorter `STUCK_THRESHOLD_SECONDS` under test, or a
clock that jumps to the boundary, would preserve the assertion at a fraction of the cost. That is a
proposal, not a finding: it must be checked against R15 first, because a rare branch that stops
being *reachable* is exactly how a control here goes quietly tautological.

Reversal: this document plus `docs/observability/operational_layer_timeout_prereg_2026-09-10.md`
and `.test_supervisor_module_timing.txt`. **No code changed** — the 394-document tree effect in §6
is recorded there and left in place deliberately.
