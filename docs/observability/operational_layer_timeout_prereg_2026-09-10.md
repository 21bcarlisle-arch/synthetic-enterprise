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
