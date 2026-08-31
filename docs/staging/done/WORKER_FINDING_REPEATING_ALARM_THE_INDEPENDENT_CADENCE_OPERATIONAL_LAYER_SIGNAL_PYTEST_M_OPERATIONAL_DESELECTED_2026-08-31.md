**Severity:** LATENT · **Lane:** H_harness

# [OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.1h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has been RED for 4 consecutive check(s) (rc=1). This does NOT affect the published site/report -- it is a daemon-lifecycle test regression. Failing tests:
FAILED tests/background/test_process_reconciler.py::test_no_reaper_or_interactive_claude_kill_path_exists_anywhere
FAILED tests/background/test_substep4_exit.py::test_reaper_absent_no_kill_path_in_background
FAILED tests/background/test_supervisor.py::test_find_work_none_when_nothing_open
FAILED tests/background/test_supervisor.py::test_find_work_ignores_in_progress_subdirectory
FAILED tests/background/test_supervisor.py::test_find_work_ignores_gitkeep - ...
FAILED tests/background/test_supervisor.py::test_find_work_ignores_blocked_backlog_items
FAILED tests/background/test_supervisor.py::test_find_work_ignores_review_gate_backlog_items
FAILED tests/background/test_supervisor.py::test_find_work_no_backlog_section_returns_none
FAILED tests/background/test_supervisor.py::test_find_work_ignores_backlog_heading_mentioned_in_prose_before_the_real_heading
FAILED tests/background/test_supervisor.py::test_find_work_missing_priorities_file_returns_none
FAILED tests/background/test_supervisor.py::test_self_refill_draw_single_atom_fast_path_unaffected_by_cap
FAILED tests/background/test_supervisor.py::test_self_refill_draw_single_atom_message_unchanged
... and 6 more failing test(s)
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-31T14:29:35+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live

---

## 2026-08-31 17:10 UTC — DIAGNOSED. The 18 named above are FIXED. The signal is still red, for a cause 3h younger.

**The 18 were TWO defects, and neither was a daemon-lifecycle regression.** The alarm text says
"it is a daemon-lifecycle test regression"; that sentence is a hard-coded label on the alarm, not
an observation, and it was wrong both times. Same class as the collection-error note already in
`process_run_complete.py`: the signal names a cause it never observed.

1. **16 supervisor `find_work` tests — a new draw SOURCE with no fixture isolation.**
   `87709c617` gave `delivery_lane.next_item` a second source, `seat_continuation.live()`, offered
   AHEAD of `focus`. It reads `background.seat_continuation.STORE` — a path the supervisor fixture
   did not isolate, because the fixture isolates the *lane* (`DIRECTION_PATH`, `CLAIMS_FILE`) and
   isolating a lane does not isolate what the lane reads. At 15:36 an interactive session wrote a
   real handoff into the live store, and every "nothing is open → None" test correctly drew LANE 0.
   The lane was working perfectly the entire time.
   *This is the third time this exact class has been paid for* (`feedback_new_draw_rung_needs_fixture_isolation`).
   The same defect had ALSO reddened 12 tests in `test_delivery_lane.py`, which the operational
   marker does not select — so the signal could not see two thirds of its own blast radius.

2. **2 kill-path safety tests — `background/seat_executor.py` (untracked, another lane's in-flight
   module) used the signal-0 liveness probe.** `test_reaper_absent_no_kill_path_in_background` and
   its twin grep every `background/*.py` for a signal-sending call and are deliberately blind to
   the signal ARGUMENT, because a probe and a kill differ by one integer. Fixed by reusing
   `tools.wait_for.pid_is_alive` (`/proc`), which `background/worker_tick.py::_pid_alive` already
   chose for exactly this reason — and which is the better probe anyway, since the signal form
   raises `PermissionError` for a live process owned by someone else.

**WHAT IS RED NOW, AND IT IS NOT THE ABOVE.** A full `pytest -m operational` at 18:05 returns
**35 failures, none of them from the 18**, all `ProductionWriteRefused`, across
`test_boot_announce`, `test_dispatcher`, `test_executor_daemon`, `test_ntfy_responder`,
`test_reconcile_watch`, `test_remote_staging_bridge`, `test_sim_runner`, `test_background_worker`,
`test_substep4_exit::test_exit_143_invariant_still_holds_against_console_sanctity`.

Cause: `tests/production_surface_guard.py`, modified **17:50 today, uncommitted**, promoted the
whole of `docs/observability` from nine hand-listed files to a `PROTECTED_SURFACES` entry. The
change is right and its argument is measured (6,421 of 27,675 lines in `autonomous-runner-log.md`
written by pytest). Its fallout is ~35 daemon tests that log to `docs/observability/*.md` and
were never isolated because nothing made them be.

**NOT DRAWN, DELIBERATELY.** That lane is live in this tree right now — edits at 17:50, 17:52,
17:57, 18:00, 18:03, 18:05, 18:09 across `production_surface_guard`, `autonomous_runner`,
`test_isolation_guards`, `seat_executor` and `seat_continuation`. Two writers choosing the same
work under two labels is the failure `seat_work_in_hand` exists to prevent, and this is that
shape. It is 20 minutes old, not 4 hours; it has not been through paging.

**If it is still red at the next hourly check, the drawable work is the 35, not the 18** — and the
fix is isolation in those fixtures, never a narrowing of the guard.

## Still live

---

## 2026-08-31 18:40 UTC — RESOLVED. `pytest -m operational` is GREEN: 1187 passed, rc=0.

**The 19 were not a nineteenth instance of the 18. They were three attribute NAMES.**
`agent_status.STATUS_FILE` (16 tests — every daemon calls `update_agent_status`),
`reconcile_watch.STATE_FILE` (2), `console_sanctity.REGISTRY_PATH` (1). All three are exactly
what `tests/background/conftest.py::_no_daemon_log_reaches_the_live_record` had already been
doing for a whole directory — for the one attribute called `LOG_FILE`. The isolation was keyed
to an attribute name, and `background/` declares **138 such path constants across 72 modules**.

Fixed in that fixture (now `_no_daemon_state_reaches_the_live_record`). **The guard was not
narrowed**, as the entry above required.

### The wide closure was RUN, and it is why the shipped fix is narrower

The obvious class fix — re-root every one of the 138 — was written and run against the whole
of `tests/background/` (3,852 tests, 19 minutes). It fixed the 19 and **cost 43 other
controls**, because for a large class of these constants **the live artefact is the control's
own subject**, not an incidental write destination:

    test_suite_duration_watch::test_a_test_process_cannot_append_to_the_live_series
    test_publish_provenance::test_a_test_cannot_write_the_published_provenance_claim
    test_live_ledger_guard::test_write_gap_entry_refuses_the_default_path
    test_suppression_register::test_live_register_passes        (+ test_model_tier,
    test_harness_exit_criterion, test_open_question_register, test_publish_step_ledger,
    test_segmentation_testability_ledger, test_tree_divergence, test_worktree_isolation)

Re-rooting moves the subject out from under the control: each then asserts that a test cannot
write a path nothing was ever going to write — a tautology, and R15's own headline killer.
**Isolation and a live-artefact control want opposite things from the same constant, and
nothing in the constant distinguishes them.** The measurement is recorded in the fixture
docstring so the next session does not spend the 19 minutes re-deriving it.

Two smaller things the wide run also proved, both kept in the shipped version:
- **Re-root preserving the repo-relative path, never flattened.** A flattening redirect turns
  `test_process_run_complete::_PIPELINE_OUTPUT_PATHS` red while claiming the isolation was lost.
- **Do not pre-create the parent directory.** All four writers `mkdir` their own; eagerly
  creating `tmp_path/site/data` red-ed a test that builds that directory itself with a bare
  `mkdir()`. A fixture that materialises directories inside another test's `tmp_path` is
  changing the world it exists to isolate.
- **Import the named modules, do not `sys.modules.get` them.** `test_substep4_exit` imports
  `console_sanctity` inside the test BODY, so a lookup-based fixture isolated it only when
  `test_console_sanctity.py` happened to be in the same selection — a control that passes or
  fails on which other files you ran.

### TWO STILL RED, NOT MINE AND NOT OPERATIONAL — for the guard-promotion lane

    test_process_run_complete::TestFrozenBaselineOutOfBandTrigger::test_spawns_detached_when_stale_and_never_runs_inline
    test_process_run_complete::TestFrozenBaselineOutOfBandTrigger::test_does_not_spawn_when_fresh

Neither is `@pytest.mark.operational` (the file is 82-deselected under that marker), so they do
not touch this signal — but they are in the CONTENT publish gate. Cause: `import
tools.run_frozen_baseline` → `simulation.run_phase4c_on_phase2b` → `live_population
._resolve_campaign` writes `docs/observability/book_growth_campaign.json` **at import time**.
No fixture can isolate that: the import IS the write, and it happens before any test body runs.
This is not fixture isolation, it is an import-time side effect on a production surface, and it
belongs to the same lane that promoted the surface. Recorded here rather than minted as a new
document, per "look for the parked atom before minting a new one".
