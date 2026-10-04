**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-forced-run-phase2b-legs-stop-building-fabric-for-the-whole-book` (Lane 0 delivery)

# The second forced home-move leg reuses the first's fabric traces

## Premise, re-measured at draw time

The duplicate-work note named this same id in `.seat_work_in_hand.json`. That entry was this draw's
own write. `ps` showed no other seat or `surgical_land` working this id.

The item said the fabric build "is book-wide and does not depend on the window". **That is half
wrong.** `run_phase2b` already bounds it: `_fabric_start = REPORT_START`, `_fabric_end = effective_end`.
For a forced leg that is 2016-01-01..2017-04-30, which is 486 days. What does not shrink is the
lead-in, because `REPORT_START` is fixed. So "bound it to the window" is already done, and the cost
is 137 premises × the window (79 electricity, 58 gas-fit years).

## What the time is, measured without the profiler

I captured the 137 real trace inputs from a forced leg and replayed them in a fresh process. That
takes **45.8 s**; cProfile had put the same work at 120 s. Plain timers over 40 of those cases
(16.2 s in total):

| part | s |
|---|---|
| `simulate_day` (1,440 sub-steps a day, about 0.24 µs per step) | 6.2 |
| `reconstruct_ambient_profile` | 3.8 |
| `cold_appliance_kwh` | 1.5 |
| `switched_units_on` | 1.2 |

**Exact micro-optimisation is spent.** Hoisting the per-step property and attribute reads out of
`simulate_day` was bit-identical over all 137 cases and moved the wall clock from 45.8 s to 45.5 s.
It was reverted. The loop was already hoisted on 2026-10-01, and what remains is CPython float
arithmetic. A faster solve that is not bit-identical would move the world's numbers, and that would
be a fidelity decision, not a speed fix.

**The digests flagged two cases, and the cause was the digest.** The in-run and replayed traces of
SYN-2016-004 and SYN-2016-006 were equal field by field. Only their pickle bytes differed, because
pickle memoises shared objects. The inputs (customer, households by day, weather days, latitude,
seed) determine the trace.

## What landed

`fabric_demand_path.sharing_traces()` is an OPT-IN scope. Inside it, `build_fabric_series_for_site`
reuses a trace whose inputs are all identical. It is not a module cache: the 2026-08-24 note at the
foot of `fabric_physics` records a cache that served one test's monkeypatched physics to another,
and four test modules monkeypatch the physics today. `test_home_move_undeliverable_win.py` enters
the scope around its two forced legs, which do not touch the physics.

The control is
`test_fabric_demand_path.py::test_a_shared_trace_is_reused_only_for_the_same_inputs_and_only_inside_the_scope`.
Each of these three mutations reds it:

- never reusing a trace;
- dropping the household from the key;
- leaking the scope past its `with`.

`run_phase2b.py` was NOT touched, because another lane was landing it during this turn.

## Pre-registration (written before the timing run)

Same box, same load, this module's two forced legs, the HEAD test file against the new one:

- **Leg 1 (no successor), which runs first:** unchanged, within ±10 s.
- **Leg 2 (with successor):** falls by the trace build. That is 45 ± 15 s on an idle box, or
  proportionally more under census load (the census rows were 125–130 s).
- **Results:** neither leg's assertions change. A reused trace is the same value the leg would have
  built.

## Result

Measured back to back on the same box, one `pytest` process per file:

| leg | HEAD file | this change |
|---|---|---|
| no successor (runs first) | 88.3 s | 85.0 s |
| with successor | 87.6 s | **36.2 s** |

**All three predictions held.**

- Leg 2 fell by 51 s, inside the 45 ± 15 predicted.
- Leg 1 moved by −3 s, inside ±10.
- Both legs pass.

The module's forced pair went from 181.7 s to 127.2 s. The census rows were 125–130 s, so under
census load the saving should be proportionally larger. That is not measured here.

## Next

Any other test module that runs `run_phase2b` more than once over the same window, without
monkeypatching the physics, can enter the same scope. Eight other test files call `rp.main`. I have
not checked which of them qualify: the scope is opt-in by design, and each module has to be read
before it opts in.
