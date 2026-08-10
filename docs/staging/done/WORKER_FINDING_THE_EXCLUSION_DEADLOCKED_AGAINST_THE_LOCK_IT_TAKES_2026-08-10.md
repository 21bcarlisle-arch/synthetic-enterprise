# WORKER FINDING — the measurement's new exclusion would have wedged publishing from inside the gate (2026-08-10)

**Atom:** `OPS2_publish_gate_head_worktree` · **caught before commit**, on the working tree, by
running the module rather than by reading it.

## Observed

`tools/measure_publish_gate_subject_cost.py` had been changed (uncommitted) so each measurement
phase **takes** `process_run_complete._run_lock` instead of polling for a gap — the right fix for
the starvation the ninth launch showed. Running its test module before committing:

    timeout 900 python3 -m pytest tests/tools/test_measure_publish_gate_subject_cost.py
    → Terminated (exit 143), stuck in test_a_banked_phase_is_resumed_rather_than_re_run

**Cause, observed not inferred.** The publisher holds `_run_lock` for the whole of `_process`,
and the publish gate's suite runs *inside* that hold. `tests/tools/test_measure_publish_gate_
subject_cost.py` is in the gate's own argv. The tests that drive `_run_measurement` reach the
exclusion through the COLD and WARM phases — which enter it in `_run_measurement` itself, past
the stubbed `_time_suite` — so they blocked on the **live** publisher's lock for
`QUIET_WAIT_SECONDS` (3800s). A local run was killed at 900s; the lock was confirmed HELD by the
live publisher at the time.

## Why it mattered more than a slow test

* Inside the gate, the hang runs to `GATE_SUITE_TIMEOUT_SECONDS` (2600s) and the gate
  **fail-CLOSES** on timeout — so every publish cycle would have blocked publication,
  deterministically, on the exact wedge class this atom exists to close.
* The other branch is no better: when the lock is momentarily FREE, a unit test **acquires the
  live publisher's lock**, and real cycles lock-skip while pytest runs.
* Nothing in the change was wrong about the *production* path. The defect was entirely that a
  test reached a live process's primitive — the isolation was never stated because two of the
  three entry points are not visible at any test's call site.

## Closed

`tests/tools/test_measure_publish_gate_subject_cost.py`:

* an **autouse** fixture redirects `prc.RUN_LOCK_FILE` into each test's `tmp_path` — autouse
  rather than per-test precisely because the entry points are not all nameable;
* `test_no_test_in_this_module_can_reach_the_live_publishers_lock` — the isolation asserted, not
  trusted. **MUTATION: `autouse=False` → reds**, naming the live path (run 2026-08-10, restored);
* `test_any_test_module_that_enters_the_exclusion_redirects_the_lock` — the population is
  **derived from the tree** (every test module referencing the harness *and* one of
  `_publisher_exclusion` / `_time_suite` / `_run_measurement`), not from a list this file
  remembers to extend, with a vacuity guard asserting this module is in it. **MUTATION: a probe
  module that drives the harness without the redirect → reds** naming it (run 2026-08-10, probe
  removed);
* `test_repeated_deferrals_accumulate_a_visible_count` no longer defers at a stubbed
  `_wait_for_quiet`. Under the new ordering that stub let the run reach the **real**
  `prc._head_checkout()`, so the test extracted HEAD into /tmp and its verdict turned on whether
  a live publisher happened to hold the reuse lock. It now defers at the guard that fires first
  — the exclusion — holding the redirected lock itself.

Module: **900s+ hang → 54 passed in 5.3s.**

## The generalisation

A test that exercises a *coordination* primitive must be given its own copy of it, and the
redirect belongs at module scope, because the interesting call paths into a lock are the ones no
test names. Stated as a rule: **when production code starts taking a lock a live daemon holds,
the test module's isolation is part of that change, not a follow-up** — and here the daemon
holding it is the very process that runs the tests.

— worker, 2026-08-10
