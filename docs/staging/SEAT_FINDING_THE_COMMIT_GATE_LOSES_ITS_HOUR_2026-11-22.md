**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Landings are not reaching origin: where the commit gate's hour goes (2026-11-22)

*Delivery seat, 2026-11-22, claim `the-commit-gate-finishes-inside-its-hour`.*

## Pre-registration (written 21:55Z, before attempt 3 of reg 6C was timed)

Three candidate causes, and what each predicts for the reg 6C landing (pid 134360, attempt 3,
hook started 21:34:11Z) and for the 18:40Z bounded landing refused at 19:40Z:

1. **Test-selection growth.** The pytest leg alone runs near the hour, CPU-bound, with no stall.
2. **Contention with s.12g** (admitted 19:32:32Z). Wall time far above CPU time for the gate's
   cgroup; memory/io pressure stall totals large; the same selection ran faster before 19:32Z.
3. **Full re-gating after disjoint origin moves.** Each attempt fits its hour, but the trunk moves
   inside every attempt, the compare-and-swap refuses, and each re-gate pays the whole cost again.

What I expect, stated now: (3) for reg 6C and something other than contention for the 19:40Z
refusal, because receipts after 19:32Z show the same pytest speeds as receipts before it. If the
attempt-3 pytest leg alone exceeds 40 minutes, (1) is a contributor and I will say so.

## What was measured

The gate keeps no record of how long each leg takes; there is no per-leg timing in the hook,
`pre_commit_test_gate` or the landing logs. The legs below are put together from process start
times (`ps -o lstart`), a 15 s process-tree sampler on pid 134360 (`/tmp/gate_probe/reg6c.log`),
the shared tree's reflog, systemd's per-unit accounting and the cgroup's pressure files.

### reg 6C, `land-reg-6c-erroneous-gains` (pid 134360, 6 paths, 173 test files selected)

| attempt | base | started | ended | wall | trunk moves inside it |
|---|---|---|---|---|---|
| 1 | d48ffb389 | 19:40:55 | lost, seeing 80d11db93 (20:24:43 - 20:47:17) | 44-66 min | 3 (19:53, 20:10, 20:24) |
| 2 | 80d11db93 | ~20:25-20:47 | lost, seeing ee82f4c3a (21:18:14 - 21:34:11) | 31-69 min | 5 (20:47, 21:09, 21:10, 21:17, 21:18) |
| 3 | ee82f4c3a | hook 21:34:11 | **killed at 3600 s, 22:34:11** (the hook timed out; no race) | 60 min | -- |

Legs of attempt 3, from process starts:

| leg | from | to | wall |
|---|---|---|---|
| extract, message chain, hook chain up to the test gate | (attempt start) | 21:34:24 | 13 s from hook start |
| test gate's structural checks + selection | 21:34:24 | 21:35:19 | 55 s |
| main pytest, 173 files | 21:35:19 | ~22:30:30 | **~55 min** (48 min 56 s on CPU at 54 min: 90%) |
| import-derived extras (3 min budget; 2 over the per-file cap, the rest past budget) | ~22:30:35 | ~22:33:28 | ~3 min |
| hook legs after the test gate (size ratchet, orphan ratchet, file-scope, ...) | 22:33:35 | 22:34:11 (killed) | 36 s, unfinished |

Count of re-gates after origin moved: **2** so far (attempt 1 -> 2 and attempt 2 -> 3), each of
them a full re-run. The 9 paths the trunk moved between d48ffb389 and ee82f4c3a are **all
disjoint** from reg 6C's 6 paths: eight are docs and work items, one is
`tests/simulation/test_net_new_acquisition.py`.

Contention, measured on the unit's own cgroup: 11,167 s of CPU over ~126 min of wall time (more
than one core at times), memory-pressure stall total 7.4 s, io 12.4 s, MemoryHigh/Max unset. The
gate's pytest runs at 84-87% of a core on a 16-core box with load average ~6.

### the 19:40Z refusal, `land-se-seat-executor-1795372804` (the bounded-landing change)

| leg | wall |
|---|---|
| whole unit (extract + chains + pytest to 63%, killed at 3600 s) | 18:40:04 - 19:40:31, 3,627 s |
| CPU over the same window (systemd accounting) | **569 s (16% of wall)** |

52 of its 60 minutes ran **before** s.12g was admitted (19:32:32Z), so contention with s.12g
cannot explain it. It was not computing: with 16% CPU it was blocked for most of the hour, and the
log ends mid-run with no output for the last stretch. Its selection for these paths is 51-52 files
(re-derived with `select_targets`), smaller than reg 6C's. **What it blocked on is NOT
established.** I checked one hypothesis and ruled it out: that the gate's tests inherited the
turn's marker and handed off to a nested unit. The unit sets `SE_DETACHED_LANDING`, so
`in_bounded_turn` is false there, and the journal shows no nested unit started in that window. That
landing is owned by `re-land-the-bounded-landing-hand-off-if-it-did-not-reach-origin`, and a re-run
of it is the next reading.

### before s.12g against after it, same pytest leg (the receipts' own `tests:` line)

| landing | tests | pytest wall |
|---|---|---|
| 21 Nov 11:37Z (before) | 594 | 566 s |
| 22 Nov 18:50Z (before) | 1,912 | 718 s |
| 22 Nov 19:50Z (after) | 608 | 484 s |
| 22 Nov 20:24Z (after) | 594 | 431 s |
| 22 Nov 21:09Z (after) | 973 | 531 s |

The same-sized selection ran no slower after s.12g was admitted.

**Attempt 3 settles part of the pre-registration's last clause.** The pytest leg alone took ~55
minutes, so (1) is a contributor: for THIS change the gate costs about an hour **with no race at
all**. Attempt 1 passed its gate inside the hour (it was refused only by the race), and attempt 3
went over by less than a minute. The two runs differed by a few minutes, at 90% CPU each.

## The named cause

**Full re-gating after trunk commits that touch disjoint paths.** One reg 6C attempt (~45-60 min,
mostly a CPU-bound 173-file pytest) fits inside the 3600 s timeout. But the trunk moved every 15-30
minutes, so every attempt lost the compare-and-swap. Every retry then paid the whole selection
again, on a tree that differed from the one already gated green only in paths the movers brought.
No number of attempts could win that race.

**And for the largest changes, selection size.** reg 6C's 173-file selection (it includes the
whole billing suite, by design, because it touches `simulation/run_phase2b.py`) runs ~55 minutes on
its own. That leaves the rest of the chain about five minutes. Whether that selection is RIGHT,
meaning which files take the 55 minutes and whether each is selected for a reason that holds, is not
measured here; it is handed on. Contention is not the cause: there were no stalls, and the pytest
legs ran no slower after s.12g. So, by this item's own rule, **the 3600 s timeout is not raised**:
the numbers do not show contention as the whole cause.

## The fix (tools/surgical_land.py)

A lost race now writes the commit of the tree it gated GREEN (unreferenced, like the one git's own
CAS strands). The next attempt hands that commit to the gate through `PRE_COMMIT_GATE_MERGE_PARENT`.
The new tree is the merge of that green tree with the new base, so it is gated the way the hook
already gates a merge (`selection_paths`, since 2026-10-03): every structural check reads the whole
change, and pytest selects only the paths that differ from both sides. A disjoint move selects
nothing. A path the lane rewrote between attempts is selected again. A red verdict is never
carried. The receipt names the tree with `prior-green:`. What this gives up is the merge rule's own
stated cost, that a union of two green sides can be red, and nothing more. Mutation-proven in
`tests/tools/test_a_lost_race_regates_only_what_the_move_brought.py`.

Applied to reg 6C, attempt 2 would have selected no tests and taken minutes.

## Not closed here

- The gate records no per-leg timing, which is why this table had to be rebuilt by hand.
- The 19:40Z hour at 16% CPU has no cause yet (see above).
- reg 6C's pid 134360 ran the OLD code (it had imported it at 19:40) and was refused at 22:34:11
  by the timeout on attempt 3. It was not touched. Its work is the reg 6C lane's to re-land, and
  on this measure that re-landing needs either a selection under ~55 minutes or a split.
- Which of reg 6C's 173 files take the 55 minutes (`--durations`), and whether each is selected
  for a reason that holds: handed on as `the-largest-gate-selection-is-measured-per-file`.

## Done-proof

The fix reached origin at 22:20Z as 229618239 (the code commit is 5a354ebcb). It was gated through
the fixed `surgical_land` in 14 minutes (22:03:53 to ~22:18). The landing that carries this
section was started after the fix was on origin, while s.12g (`longjob-value-test-cut012-new-book`)
was still running; its receipt is that proof.

## Per-file measurement of reg 6C's selection (claim `the-largest-gate-selection-is-measured-per-file`)

### Pre-registration (written 22:50Z, before the run)

`select_targets` over reg 6C's 6 paths, re-derived now, returns 172 files (the hook saw 173; one
billing test has since been deleted in the shared tree). By the rule that puts each one there:

| rule | files |
|---|---|
| `billing_suite_tests` (triggered by `saas/reporting/annual_report.py` matching the `saas/` prefix) | 116 |
| `CONTROL_TESTS` (any code path) | 46 |
| `tests_for` (named for a changed module, or a changed test) | 10 |

`importing_tests` adds nothing to the main run here: every importer it finds is already named.

Run: the 172 files in one pytest, as the hook runs them, with `--durations=0`, in a worktree at
origin/main with reg 6C's six frozen copies (`/tmp/seat_6c`) laid over it.

Predictions, written before the answer:

1. The 10 `tests_for` files carry more than 60% of the wall; `tests/simulation/test_run_phase2b.py`
   alone takes over 15 minutes.
2. The 116 billing files take at most 8 minutes together (183 s whole-suite on 3 Nov).
3. The 46 control files take at most 5 minutes together.

A reason I already doubt, independent of the timing: the billing trigger's own comment says `saas/`
is on it "because billing imports it". `company/billing/` imports `saas.bill_generator`,
`saas.customer_reaction` and `saas.ledger`, and nothing under `saas/reporting/`. If (2) is wrong
and the billing files are heavy, that reason does not hold for `annual_report.py` and the trigger
narrows to the `saas/` modules billing actually imports.

### What it measured (run 22:48Z-23:44Z, `longjob-gate-selection-6c-durations`)

2,916 passed, 2 skipped, **3,342 s (55:42)**, 4,570 s CPU, 3.0 GB peak, so the hook's ~55 minutes
reproduces in isolation. Per-file time (setup + call + teardown), by the rule that selected it:

| rule | files | minutes |
|---|---|---|
| `tests_for` | 10 | **34.9** |
| `CONTROL_TESTS` | 46 | **11.7** |
| `billing_suite_tests` | 116 | **7.9** |

| file | s | rule | where the time goes |
|---|---|---|---|
| tests/simulation/test_run_phase2b.py | 1,551 | tests_for | two whole runs: the 2016-2018 fixture (1,017 s) and reg 6C's new every-win-erroneous 2016-2017 run (534 s) |
| tests/simulation/test_run_phase2b_event_log.py | 534 | tests_for | its own 2016-2017 run |
| tests/background/test_weekly_rhythm.py | 509 | CONTROL_TESTS | annotated 0.43 s when it joined; see below |
| tests/company/billing/test_collections_journey.py | 357 | billing | two live-run fixtures |
| tests/company/billing/test_the_share_of_dd_collections_..._belief.py | 101 | billing | |
| everything else (167 files) | ~220 | | |

Graded against the predictions: (1) **held**, `tests_for` is 64% and test_run_phase2b.py alone
26 min. (2) **held, at the edge**: billing 7.9 min against "at most 8". (3) **wrong**: control
files 11.7 min, not under 5, and 8.5 of it is one file.

### Each heavy file's reason, and what changed

- **billing suite, `saas/` prefix: the reason does not hold.** The trigger says `saas/` is on it
  "because billing imports it". Walked by AST, `company/billing/` and the two billing tools reach
  15 `saas/` modules, transitively, and nothing under `saas/reporting/`. Importing all 116 billing
  test modules loads no `saas.reporting` module either. The prefix is now that derived set
  (`billing_reached_saas`, 0.2 s; an unreadable file on the walk makes every `saas/` path a trigger
  again). Control: `test_a_saas_module_billing_never_imports_does_not_select_the_billing_suite`.
  It goes red under both mutations: restoring the prefix, and stopping the walk at billing's direct
  imports. The old control named `saas/reporting.py`, a file that does not exist, as a trigger.
  **reg 6C's selection: 172 -> 56 files.**
- **test_weekly_rhythm.py, `CONTROL_TESTS`: the reason holds, and the file is slow by accident.**
  Its fixture already stubs the step document's live reads (transcripts, the orphan index, the
  director's note) because each has its own suite. Five sections added since then were never
  stubbed: the map's mutation index (~25 s a step, AST over ~600 modules), the drawn world, the
  draw history, git's merge log, the knowledge plan. Three tests called `_step_body` without the
  fixture at all (155 s, 81 s, 35 s). Stubbed, with the fixture added to those three:
  **509 s -> 21 s**, 40 passed. The Friday test's own stated mutation (drop the balance section)
  still fires.
- **test_run_phase2b.py and _event_log.py, `tests_for`: the reason holds** (each is named for the
  module). The time is three whole runs, and one of them is wasted, and it is **not landed here**:
  `test_run_phase2b_event_log.py` runs its own 2016-2017 run (534 s). By its sibling fixture's own
  2026-08-31 measurement, that window now holds **no retention offers**, so four of its tests
  (`..._entries_have_required_fields`, `..._cost_events_are_negative_amounts`,
  `..._entries_above_threshold`, `..._entries_have_expected_margin`) loop over an empty list and
  pass on nothing. Moving them onto the 2016-2018 run fixes both the time and the vacuity.
  Not re-measured by me: it needs a 9-minute run. Handed on.
- **test_collections_journey.py (357 s, billing)**: its reason holds for billing paths. It is no
  longer selected for reg 6C. Not changed.

Expected for reg 6C now, before re-measurement: 55.7 min, less 7.9 (billing) and ~8 (weekly
rhythm), comes to **about 40 minutes**. That is inside the hour with about 20 minutes for the rest
of the chain. Every code commit's gate is ~8 minutes faster from the weekly-rhythm stubs alone.

## 2026-11-23: the event-log file reads the shared 2016-2018 run (worker; claim `the-event-log-tests-read-the-shared-2016-2018-run`)

The hand-on above, done. `tests/simulation/conftest.py::phase2b_2016_2018` is one session-scoped
2016-2018 run (with its `gap_ledger_path`), and both `test_run_phase2b.py` and
`test_run_phase2b_event_log.py` read it. The gate runs its selection in one serial pytest, so the
two files now pay for one run, not two. A new control,
`test_every_log_these_tests_loop_over_has_entries`, refuses an empty company event log, retention
log, retention cost list or no-offer log, and a window with no `uneconomical` no-offer. Under five
mutations (each log emptied in turn, plus the no-offer reasons with no `uneconomical`), every leg
goes red. Before this change, on 2016-2017, the retention legs held nothing.

Predicted before the run: the two files would take about 1,050 s on origin's code. Measured at
origin 8a52399b8: **45 passed, 972 s**. The 534 s event-log run is gone, and every per-entry loop
in that file now runs over entries from the 2016-2018 window. reg 6C's extra 2016-2017 fixture is
not on origin, so it is not in this figure.
