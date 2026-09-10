# Pre-registration: what the operational-layer timeout will name

Written 2026-09-10 19:55 UTC, while run PID 1744118 (started 19:32:43 UTC, budget 1800s) was
still in flight. Its timeout fires at 20:02:43 UTC and only then writes `timed_out_at` into
`docs/observability/.operational_layer_signal.json`. Everything below is therefore recorded
BEFORE the answer exists, so the answer can refute it.

## What is already measured (not predicted)

- `State: R (running)`, 100% CPU, 18:53 CPU-time at 22 minutes elapsed, 31 threads,
  `rchar` 8.8 GB. The run is **CPU-bound**, not blocked on a lock, a socket or a `join()`.
  This refutes the blocked-on-a-waiter class outright.
- Box is **not** contended: 16 cores, load average 5.76, the only other pytest run pinning
  one core. So the timeout is not starvation by a sibling lane.
- pytest's fd-capture file for the test running at 19:53-19:55 holds
  `background/supervisor.py`'s draw output — `TICK-NEVER-RESTS law`, `AUTHORIZED-SET
  enumeration`, `THREE-LANE self-refill`, `PRODUCT STARVATION` — repeating the same block
  dozens of times per minute, and growing (14,690 -> 22,410 bytes in ~40s).

## The prediction

1. `timed_out_at` will name a test that drives a **real supervisor draw / worker tick** in a
   loop. My single most likely nodeid is in `tests/background/test_worker_tick.py` (it calls
   `wt.run_tick()` directly at line 227); the other candidates that reach the same producer
   are `tests/background/test_daily_self_note.py` and `tests/background/test_doorbell_redaction.py`.
2. The subject will **name a test**, not `IN_COLLECTION` and not `NO_OUTPUT` — the `-v` payload
   landed at HEAD (59a91d4a2) is the thing being exercised for the first time here.
3. The cause is cost that **scales with live tree state**, not a fixed-cost suite that outgrew
   its budget: each draw enumeration walks the staging queue, which currently holds 140 root
   documents against 3,349 archived.

## What would refute me

- `timed_out_at` naming a test in a module that never reaches `supervisor.py` -> prediction 1 is wrong.
- `IN_COLLECTION` / `NO_OUTPUT` -> prediction 2 is wrong and the `-v` payload does not work.
- A green on this run -> the whole diagnosis is deferred and the flap is unexplained.

## What is NOT predicted

Whether the loop is unbounded (a defect in the test) or merely expensive-per-iteration (a cost
that grew under it). The capture cannot tell those apart and I am not guessing.

---

# Round 2 — the per-cycle attribution (written 2026-09-10, BEFORE the profile was read)

Round 1's §5 left an honest gap: a by-hand replication of the test's isolation, *including* its
`_FakeClock`, ran one `run_cycle()` in 0.081s, while the cycle inside the real test costs ~4.3s.
Fifty times. The cost lives on a path the replication never reached. This round attributes it.

`python3 -m cProfile -o /tmp/supervisor_cycle.prof -m pytest
tests/background/test_supervisor.py::test_stuck_escalation_survives_daemon_restart` — 31 real
cycles, the exact test the 2026-09-10 20:02 timeout named.

## The prediction

4. **The cost is in `find_work()`, not in `_check_stuck_escalation()`.** `run_cycle()` stubs
   `is_session_idle` and `grant_turn` in this test, and `_check_stuck_escalation` is disk-state
   bookkeeping over one small JSON file. `find_work()` is the only unstubbed step that reads the
   real repository, and it runs *once per cycle* — 31 times here.
5. **The leaf is a pure-Python parse repeated per cycle, most likely the maturity map's YAML**,
   not a subprocess. Round 1 measured the timed-out process at `State: R`, 100% CPU, `wchan` 0 —
   a run paying for `git` subprocesses would sit in `S`/`D` at low CPU for much of its life.
6. **The by-hand replication returned early.** It set no stuck agenda that survived `find_work`,
   so it returned at the `reason is None` branch and never paid for the expensive step — which is
   exactly why it was 50x fast and why the gap existed.

## What would refute me

- `_check_stuck_escalation` or `surface_missing_work_block_defects` dominating cumulative time
  -> prediction 4 is wrong.
- `subprocess` / `fork_exec` dominating -> prediction 5 is wrong and the 100%-CPU reading was
  mis-read.
- No single step dominating (cost spread evenly across the cycle) -> there is no narrowing target
  and §7 of the round-1 finding needs rewriting, not implementing.

## What is NOT predicted

Whether the expensive step is *cacheable within a process*. A parse that legitimately re-reads
because the tree can change between real 2-minute polls is not a defect in the producer, and the
repair would then belong in the test, not in `supervisor.py`.
