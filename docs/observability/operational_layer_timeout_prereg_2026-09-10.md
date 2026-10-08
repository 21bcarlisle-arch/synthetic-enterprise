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

---

# Round 3 — 2026-10-08: three test leaks, two of them git subprocesses, and a production quadratic

Four consecutive `red_timeout`s (budget 1800s), the last naming
`test_stuck_escalation_does_not_fire_when_grants_fail`. Measured, not predicted: in isolation the
test PASSES in 38s (40 cycles, ~0.95s each) — so it is not hung. cProfile in an `origin/main`
worktree, then sampling the full-file run, attributed the time to five costs, the first three reads the `_isolate` fixture does not cover:

1. **The real maturity map, parsed ~6x per cycle.** `_product_priority_ids` called
   `maturity_map_store.load_live_atoms()` with the store's default path, not the supervisor's own
   `MATURITY_MAP_PATH` the fixture redirects; and `delivery_lane._atom_ids` reads
   `delivery_lane.MATURITY_MAP`, which the fixture never touched. ~80% of profiled time was YAML.
2. **A real `git fetch origin main` every cycle** (`_sync_origin_staging`, 45s timeout per call):
   120 git calls per test, 0.4–0.7s each when origin answers promptly. With `STAGING_DIR` isolated
   it also saw every origin staging doc as missing and `git show`-WROTE one into the checkout's real
   `docs/staging/`. This is the leg that can wait rather than compute — a contended fetch lock or a
   slow remote costs up to 45s x 40 cycles — which is the only reading here consistent with
   timeouts interleaved with green runs. Rounds 1–2 measured `State: R`; a run caught inside this
   leg would read `S`.
3. **`_unmerged_work_paths` runs `git status` in EVERY linked worktree of the real repo** on any
   draw with candidates — 126 worktrees on 2026-10-08, 7.0s a call when quiet, a 20s timeout per
   worktree when not. Found by sampling the full-file run's children (a steady ~2/s stream of
   `git status --porcelain`) while the process sat in `do_sys_poll` at flat CPU. Its cost scales
   with how many worktrees lanes have open, which rises and falls through the day: **this is the
   leg that best explains timeouts interleaved with greens.** It also runs in PRODUCTION on every
   BUILD/SITE draw (~7s against a ~2-minute poll); that is recorded here, not changed.
4. **A PRODUCTION quadratic in the delivery-lane draw, found while pre-running the landing.**
   `delivery_lane._retired_ids` called `current_orientation()` inside a comprehension over every
   retired continuation (847 on 2026-10-08); each call re-reads and validates `DIRECTION.yaml`, and
   `direction.validate` parsed the live map once per focus item carrying a lane. One `_retired_ids()`
   on live state: **431s, 4,210 map parses.** After hoisting both reads: 0.12s, 1 parse, the same 39
   ids as the base. It sits on every delivery-lane draw (the supervisor's 2-minute poll, the pull
   hook), and it reached tests that do not isolate `seat_continuation.STORE` —
   `test_forward_discovery_draw.py::test_propose_half_forbids_rest_the_overnight_breach` ran >180s on
   pristine origin/main, stack in `_retired_ids`. The store only grows, so this cost rose week by week:
   the likeliest MAIN driver of the suite-wide timeout, with legs 1–3 adding to it.
5. `gap_ledger_reconciler.discover_writers` and `gap_register_scan` scanning the real tree: CPU,
   ~0.3s/cycle, bounded. Left in place (see below).

**Verdict: slow, with a lock/network-dependent component — not a cadence question.** The repair
narrows what the test touches; the 1800s budget is unchanged. (1) `_product_priority_ids` reads
`MATURITY_MAP_PATH` (the same file in production); (2) the fixture redirects
`delivery_lane.MATURITY_MAP`; (3) the fixture replaces `_default_git_runner` with one that raises,
so the sync takes its existing fail-safe no-op; its own tests inject `_runner`; (4) the fixture
stubs `_unmerged_work_paths` to the empty set (its own module builds a repo to test it). (5) `_retired_ids` reads the orientation once, and `validate` reads the map's lanes once per record —
production code, behaviour-preserving. Named test: 38s ->
13.6s, zero git calls. Whole module after: 201 passed in 224s, no git children sampled (no clean
"before" for the module was taken — the pre-repair run was killed once leg 3 was found). `pytestmark = operational` covers the whole module, so every `run_cycle`
test there gains the same.

**The class, not the instance.** Each new draw rung that reads the tree is a new leak into a fixture
that enumerates paths by hand; rounds 1–3 each found one. Leg 5 is the next one. The structural
remedy — a fixture that refuses any real-tree read rather than listing redirects — is not built here.

**Prediction, filed before the next signal run:** the next operational-layer run either goes green
inside 1800s or, if it times out, names a test outside `tests/background/test_supervisor.py`.
A timeout naming a test in that module again refutes this round's attribution.
