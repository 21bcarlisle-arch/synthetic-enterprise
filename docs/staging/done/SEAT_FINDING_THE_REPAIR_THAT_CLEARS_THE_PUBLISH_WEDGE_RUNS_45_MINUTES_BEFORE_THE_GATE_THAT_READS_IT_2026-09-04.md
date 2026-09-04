**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the repair that clears the publish wedge runs 45 minutes before the gate that reads it

Filed 2026-09-04 by the delivery seat, working the Lane 0 direction *"the figures stopped reaching
the reader and no direction ever named the path"*.

## The doorbell named the wrong subject, twice over

The direction said the wedge was untracked controls in the site lane, named
`site/test_the_site_lane_runs_no_untracked_control.py`, and said the backlog was eight markers.
All three were false at the moment I read them:

* `site/harness/test_the_deployment_reading_reaches_the_reader.py` and `_render_harness.mjs` are
  **tracked and committed**; `git status --porcelain site/` is clean of them and all 7 controls
  in that pair pass.
* The backlog was **eleven**, not eight, and rising on a ~13-minute cadence.
* `.publish_gate_state.json`'s `blocking_tests` named
  `tests/background/test_publish_failure_names_its_cause.py::test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis`,
  which **passes at HEAD** — all 24 tests in that file pass. Its failure was stamped at
  `3d369242c`, a commit from 11:41 that is an ancestor of HEAD: a pre-fix stamp read as current.

Reading the state file from this worktree would have compounded it. The checked-out copy says
`{"alerted_at": null, "failures": []}` — dated Sep 1, my checkout instant. The live file is in the
shared tree and says something else entirely. **Two rooms, and the one the brief points at is the
one that cannot be right.**

## What was actually refusing every commit in the tree

Not a test. The publisher's own log named it at 11:47Z, which is exactly what
`test_publish_failure_names_its_cause.py` exists to guarantee and it worked:

```
[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.
  - TWO ROOMS SEAT_PREREG_DOES_A_DIRECTORY_URL_EVER_CONFIRM_THROUGH_THE_DEPLOY_CHECKS_OWN_FETCH_2026-09-04.md
[process_run] Publish commit REFUSED with no FAILED/ERROR summary in the hook chain's output --
  recording NO blocking test. The gate that refused is the finding-class consolidation: running
  the test suite will not clear it.
```

By 13:19 there were two such pairs. `background/finding_classes --check` in the shared tree:
`check: FAIL (2 failures)`. In this worktree at the same commit: `PASS`. The refusal is a property
of shared-tree *working-tree state*, not of any commit — which is why it is invisible to every
lane that checks its own tree and why no test could name it.

## The mechanism, and it is a timing defect not a logic one

`background/staging_two_rooms_repair.py` is correct. Run against the live shared tree it graded
**both** pairs `redundant` (SAFE) and would have deleted both. Its room-list blindness — the
`records/` room it could not see — was already fixed at `45ba3df6d` (10:10 local), and that fix
is in HEAD and working.

The defect is *when* it runs:

| 12:30 | `background_worker` cycle starts. Runs `staging_two_rooms_repair.observe()`. Tree clean, nothing to do. |
| 12:30 | Same cycle launches `process_run_complete`, which runs for **54+ minutes**. |
| 13:01 | A duplicate is written into both rooms. |
| 13:06 | A second one. |
| ~13:2x | That cycle's `git commit` runs the pre-commit chain. `finding_classes --check` reads the tree **now** and refuses. |

`finding_classes --check` is a *pre-commit* gate, so the refusal is evaluated at the far end of the
interval the repairer sweeps at the near end of. **The window in which a duplicate can wedge a
publish is exactly the window in which the repairer cannot get another turn** — and its next turn
only comes after the publish it would have saved has already been refused. The repair sat one
function call away for the entire 54 minutes and structurally could not be reached.

This is the general shape already in this project's ledger as *"re-read the fork measurement
immediately before acting on it, not just after"*. A check whose subject can change under you is
worth only as much as its recency at the instant of decision.

## The repair, and the trap in the obvious version of it

Both live pairs were byte-identical, and **their tracking was opposite**:

| file | tracked copy | untracked duplicate |
|---|---|---|
| `..._DEPLOY_CHECKS_OWN_FETCH_...` | `records/` | root |
| `..._BLOCKING_TEST_ACTUALLY_RED_...` | root | `records/` |

So "delete the untracked copy" and "delete the root copy" are different rules, and each is wrong
for one of the two. The governing rule is neither: it is
`staging_rooms.room_for(KIND_PREREGISTRATION) == records`. I removed the **untracked** copy of each
pair — which is the redundant one in both cases, and the choice that leaves the shared tree's
fast-forward clean, since removing a tracked copy would have left origin adding a path a
byte-identical untracked file already occupies. `finding_classes --check` went to
`PASS (0 failures)` at 13:19. That leaves the second prereg in the wrong room, which is a separate
and much smaller defect than a wedged publisher; it is named in the hand-off.

The code fix moves the repair to the point of use: `_clear_two_rooms_before_commit()` in
`background/process_run_complete.py`, called immediately before the publish `git commit`. It does
not replace the worker's sweep — that still catches duplicates appearing while no publish runs.
Two call sites of one repair, covering different intervals.

## Grading the pre-registration

`docs/staging/records/SEAT_PREREG_CAN_THE_PRE_COMMIT_TWO_ROOMS_REPAIR_BE_PROVEN_BY_AN_ORDERING_CONTROL_2026-09-04.md`,
filed before the test was attempted.

* **P1 — `git_commit_push` is drivable in a unit test: CONFIRMED**, though the prereg's stub list
  was incomplete. It also needed `LATEST_MD` (a module-level constant, so unaffected by
  monkeypatching `PROJECT_DIR`), `publish_cause`, `log`, and `_record_commit_refusal_reds`
  returning `[]` rather than `None` — `[]` being precisely the "no test was judged" shape a
  non-test gate refusal produces. The fallback to a source-order control was not needed.
* **P2 — the ordering control discriminates: CONFIRMED.** With the repair wired the root copy is
  ABSENT at commit time; with `_clear_two_rooms_before_commit` stubbed to a no-op on the same
  fixture it is PRESENT. Both legs are asserted. Without the second leg the first would pass
  against a fixture that never held a duplicate.

## Controls

`tests/background/test_process_run_complete.py::TestTheTwoRoomsRepairRunsAtTheCommitRatherThanACycleEarlier`
— four tests. Mutation-proven, `python3 -B`, both mutations fired:

* helper returns without calling the repairer → 2 red.
* call site deleted from `git_commit_push` → 2 red.

The discriminating leg stays green under both, correctly: it stubs the repair itself, and its job
is to show the fixture *can* report PRESENT.

## What is still open

* **The writer is unidentified.** I repaired the state, not whatever writes a prereg into both
  rooms. `staging_two_rooms_repair`'s own docstring records the same admission from 2026-08-19 and
  declines to name a cause it cannot show; I am declining on the same grounds. A concurrent
  autonomous worker (pid 2033380) was working the staging queue across the window, which is a
  suspect and not evidence.
* **`.publish_gate_state.json` names a green test as the blocker.** Its `blocking_tests` survived
  from a pre-fix commit and points readers at a suite that will not clear anything. That is the
  same fail-silent shape this file is about, in the state record rather than the gate.
* **Sediment.** `staging_rooms --check`: 221 documents filed into the root in 7 days, 183
  dispositioned, net +38. Not caused by any of the above and not fixed by any of it.

## Disposition

Filed already-repaired: the code fix, its four controls and this document land in one commit, so
the finding is consolidated into `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` and archived here
rather than sitting in the root as work. It is named in that register's **What is owed** as
BLOCKING, which is where the two items above that are NOT repaired — the unidentified writer, and
`.publish_gate_state.json` naming a green test as its blocker — stay visible.

The live wedge itself was cleared by hand at 13:19 local, before any of this landed; that is what
let the queued runs move at all.
