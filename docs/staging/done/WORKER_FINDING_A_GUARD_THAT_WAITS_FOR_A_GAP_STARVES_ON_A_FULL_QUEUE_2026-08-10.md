# WORKER FINDING — a guard that waits for a gap starves on a queue that never empties

**Date:** 2026-08-10 · **Atom:** `OPS2_publish_gate_head_worktree` (exit criterion 1)
**Class:** R15 — a control that cannot fire · **Status:** closed at the cause, R15 both ways

## The observation (R9: observed, from the unit's own journal)

Nine `--systemd` launches of `tools/measure_publish_gate_subject_cost.py`. `deferral_count`
rising. `in_tree_baseline` — the exit criterion's **denominator** — never once timed.

```
Aug 10 19:55:05  [measure] phase 1/3 COLD -- banked by an earlier launch at 1291.9s, not re-run
Aug 10 19:55:05  [measure] phase 2/3 WARM -- banked by an earlier launch at 1167.5s, not re-run
Aug 10 19:55:05  [measure] phase 3/3 BASELINE -- the live working tree, the pre-ruling subject
Aug 10 19:55:05  [measure]   . waiting for the live publisher to finish before timing
Aug 10 20:40:05  [measure]   ! publisher still live after 2700s -- DEFERRING
```

The resume fix held perfectly. The two earlier deaths in this phase were OOM kills, and the fix
for those (defer rather than measure-anyway) also held. The phase still never ran.

## Why it was never going to run

It was not bad luck, and it was not slow. It was a control that **cannot fire**:

- `docs/staging/` holds **112 pending `run_complete_*.md` markers`**;
- `background_worker.py::process_leftover_run_markers` re-globs every one of them each cycle;
- a publish cycle is now bounded at `GATE_SUITE_TIMEOUT_SECONDS` = 2600s of gate, plus the
  publish path after it.

So the publisher runs very nearly back-to-back. `_wait_for_quiet` polled for the publisher's
**absence** — it had to win a race against a queue that refills faster than it drains. That
starves, and it starves **invisibly**: every banked phase looks healthy in the record, the run
exits 0 (a deferral is a correct outcome), and only a rising `deferral_count` says otherwise.

Worth naming precisely: this failed in the *safe* direction. The starved phase is the ratio's
denominator, so the criterion stayed **unmeasurable** rather than reading a wrong MEETS. That is
the better of the two failures — and still a failure, because the exit criterion cannot be met
by a harness that cannot run.

## The fix — take the gap, don't wait for one

The primitive was already in the repo and the harness was not using it.
`process_run_complete.py::_run_lock` is a non-blocking `flock` on `.process_run_complete.lock`
wrapping the **whole** cycle (`_process`); a publisher that cannot take it exits
`EXIT_LOCK_SKIPPED` (75) with its marker still pending — a path `background_worker.py` already
handles as *"still pending, will retry next cycle"*, not as a failure.

`_publisher_exclusion` now **holds that lock for the duration of a phase**:

1. **It converges.** The acquire waits out at most ONE live publisher; after that no further one
   can start inside the phase.
2. **`box_was_quiet` becomes true by construction.** The seventh launch's invariant
   (`test_a_banked_phase_was_always_admitted_quiet`) previously rested on nothing having started
   in the gap between the last poll and the first test.
3. **The deadline is derived, not restated.** `QUIET_WAIT_SECONDS` is now
   `prc.PUBLISH_PATH_TIMEOUT_SECONDS + 5min`, the longest a publisher may legally hold the lock.
   A hand-typed `45 * 60` sat *below* that — a wait shorter than the work it waits on does not
   bound the wait, it guarantees a deferral. Same defect as the 900s caller cap under the 2600s
   gate that this atom closed one layer down.
4. **Re-entrant**, because COLD must span delete → rebuild → time under one hold; a second
   `flock` on a second fd of the same file blocks even within one process.

**Cost:** one deferred publish cycle per phase, on a queue that is already deferred, and nothing
to the marker.

## R15, both ways (`tests/tools/test_measure_publish_gate_subject_cost.py`)

The lock is interrogated through `prc._run_lock` **itself**, never a second flock written in the
test — so a test cannot pass against a lock the real publisher would not respect.

| Control | Mutation that reds it |
|---|---|
| `test_a_phase_holds_the_publishers_run_lock_while_it_times` | drop the `with _publisher_exclusion(...)` from `_time_suite` |
| `test_the_exclusion_is_released_when_the_phase_is_over` / `..._raises` | drop the `finally:` unlock |
| `test_an_unavailable_exclusion_defers_rather_than_measuring_anyway` | fall through to the suite instead of raising |
| `test_the_exclusion_wait_exceeds_the_longest_a_publisher_may_hold_it` | restore the hand-typed `45 * 60` |
| `test_the_exclusion_is_re_entrant_so_the_cold_phase_can_span_its_setup` | attempt a real re-acquire instead of counting depth |

## The generalisable lesson

**A guard that polls for a resource to become free is only a control if the resource actually
becomes free.** Where an exclusion primitive already exists, take it — waiting for a gap is a
race the guard can lose forever, and losing it looks exactly like patience.
