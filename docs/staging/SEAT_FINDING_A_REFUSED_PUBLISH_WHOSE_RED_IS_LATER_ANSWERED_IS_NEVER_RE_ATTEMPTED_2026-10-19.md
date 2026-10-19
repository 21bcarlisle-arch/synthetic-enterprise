**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `OPS6_scoped_publish_path_suite`

# A refused publish whose red is later answered is never re-attempted

**Found by** the delivery seat on 19 Oct 2026, while re-driving the publish of the 03:30Z run
(`producing_commit` 8b6fea024, marker `docs/staging/done/run_complete_20261019T033010Z.md`).
Direction item `publish-the-19-oct-dual-fuel-run`.

**This is the second time.** `WORKER_FINDING_A_REFUSED_PUBLISH_ARCHIVES_ITS_MARKER_SO_THE_NEXT_SWEEP_PUBLISHES_THE_OLDER_RUN_2026-10-13.md`
found the same mechanism on 13 Oct, fixed it by hand, and proposed the `done/` glob described below.
That was folded into OPS6 and is still unbuilt. This one adds the trigger the 13 Oct note did not have
(a dead `citation_at_head`) and a second stall on the delivery leg.

## What happened

At 06:35Z the hook chain refused the publish commit for the 19 Oct dual-fuel run (rc=77,
`commit_refused`, one red: `test_bill_correctness_addendum_defect4.py`, account C7). At 07:56 BST,
dc4dc0e10 answered that red, and `.publish_gate_state.json` recorded `citation_at_head: dead`
("re-run at HEAD, all 1 cited red(s) PASS"). For the next two hours nothing re-attempted the
publish. The run's outputs were still on disk, byte-identical
(`run_output_latest.json` = `run_output_8b6fea024_20261019T033010Z.json`), and the weekly window
was open. A human had to draw a direction item and run
`python3 background/process_run_complete.py docs/staging/done/run_complete_20261019T033010Z.md` by hand.

## Why nothing retries it (read from the code)

1. **The marker leaves the sweep's sight before the commit.** `_process` calls `_archive_marker`
   *before* `git_commit_push`, so the archive can land in the same commit as the run. After a
   refusal it stays in `done/`, tagged `<!-- publish-outcome: did-not-land ... -->` by
   `_stamp_publish_outcome_on_archived_marker`.
2. **The only retry route globs `staging/` alone.**
   `background/background_worker.py::process_leftover_run_markers` reads
   `STAGING_DIR.glob("run_complete_*.md")` and never looks in `done/`. A refused marker is gone
   from its population.
3. **Not recording the fingerprint is a retry only for a *new* run.** On a non-retryable outcome
   `_process` deliberately skips `_write_last_fingerprint` ("the next identical run must
   re-attempt it"). That re-arms the change-detection gate for the *next marker sim_runner mints*,
   but this morning sim_runner was deferring every cycle on the memory budget (two 7.1 GB
   budget-pay arms). So the only thing that could re-attempt was a run that couldn't start.
4. **The fact that would justify a retry goes nowhere.** `_citation_reading` /
   `_reask_citation_at_head` compute `citation_at_head: dead` and write it into the gate state
   file. Nothing reads that verdict as a trigger. It is a diagnosis for a reader, not an event.

## What in `background/process_run_complete.py` would re-arm it (NOT built here)

The smallest mechanism that can fail is one leg. When the gate state reads `citation_at_head ==
"dead"` and `failures[-1]` names a `git_hash` whose archived marker
`staging_archive_policy.publish_did_not_land` reads True, return that marker to `staging/` (the
inverse of `_archive_marker`), once per failure. `process_leftover_run_markers` would then
publish it newest-first on its next cycle, under the run lock and the weekly window it already
obeys. Two places could own the leg:

- **In `process_run_complete`, where the dead verdict is written** (the `entry["citation_at_head"] =
  citation["verdict"]` path near `_citation_reading`). This is the one instant the answer is known.
- **In `process_leftover_run_markers`, as a second, narrow glob** over `done/` for did-not-land
  markers newer than `_newest_published_stamp`. This keeps the decision beside the existing
  supersession logic, so an overtaken refused marker is retired, not revived.

Controls owed by whichever is built: a refused marker with a dead citation IS re-queued, and one
with a live citation is not (assert the branch can be taken before asserting what it does). A
refused marker overtaken by a later published run is NOT revived. A re-queued marker that fails
again is not re-queued a second time at the same HEAD. That last one is the livelock that
`OPS_run_marker_sweep_livelock` already paid for once.

## Also seen on the re-drive: the delivery leg stalled too

The hand re-run gated green and committed 2a195224b at 09:15Z. Its push was rejected because
origin had moved, and the publisher deferred delivery (`committed_delivery_deferred`, rc=80), its
own `origin_reconcile` call returning `GATE_RUNNING`. Run by hand afterwards, `origin_reconcile`
refused the merge (`REFUSED_GATE`), and its `detail` string is cut off before the red is named. The
same merge, gated in an origin-based worktree, passed and was promoted as f8f3d0fd5. So the
shared-tree refusal came from that tree, not from the merge, and the cut-off `detail` meant it could
not be told which. This is not fixed here. It is a second reason the book sat unpublished, and
whoever builds the re-arm should check that a re-queued publish can actually be delivered.

## Not in scope

- This does not weaken the gate. The re-attempt goes through the same hooks.
- The re-drive this finding came from is recorded in the BLOCKING finding
  `SEAT_FINDING_A_LEAVER_NEVER_READ_BILLS_A_QUARTER_OF_ITS_TRUE_USE_AND_REFUSED_THE_PUBLISH_2026-10-19.md`.
