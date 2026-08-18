**Severity:** LATENT · **Lane:** H_harness

# A swap that protects an uncommitted lane is a live producer outage for as long as it is held

**Found:** 2026-08-18, working the RUNG-1d producer-starvation draw. The instance is
repaired in the same tick (the uncommitted lane is landed); the mechanism below is not,
which is why this is written down rather than closed.

**Class:** `uncommitted_and_orphaned_work` — the shared-tree family.

---

## The defect, one line

The live producer executes the shared **working tree**, so the only legal way to land a
file that carries two lanes — swap the worktree copy to a one-lane version for the gate
window — is a producer outage that lasts exactly as long as the swap is held.

## Observed, with evidence (R9)

1. **The outage.** `docs/observability/.sim_producer_state.json` recorded
   `consecutive_failures: 10`, `first_failure_ts` 2026-08-18T10:58:25Z through
   `last_failure_ts` 12:16:25Z — a **1.3 hours** (1h18m) producer outage, every run dying at ~210s with
   `KeyError: 'net_margin_gbp'` from `simulation/run_phase4c_on_phase2b.py:403`
   (full tracebacks in `docs/observability/sim-runner-log.md`).
2. **It was not a new edit.** The run immediately before, 10:16:53Z, SUCCEEDED, and its
   artefact `docs/reports/run_output_latest.json` carries `net_of_all_costs_margin_gbp` —
   a key that only exists in the repaired `saas/cost_to_serve.py`. The repaired pair was
   live and green minutes before the first failure. A file went **backwards**.
3. **Which file, and by whose hand — in that lane's own words.** `febf7e51f`'s commit
   message: *"simulation/run_phase4c_on_phase2b.py carries two lanes: this atom's B13 door
   cut and an unrelated margin-basis repair reading keys defined only in an uncommitted
   saas/cost_to_serve.py. A pathspec cannot split a file, so the worktree copy was swapped
   for a KNIFE-only version under a trap and restored after."* The KNIFE-only version is
   the pre-repair reader. The restore stamped the file at 13:17:43.376 BST — the same
   second as that commit, and two minutes after the last failed run.
4. **The trap worked.** Nothing was left broken; the swap was restored exactly as
   designed. The damage was done entirely *inside* the window the design intends to hold.
5. **Second occurrence.** `tests/background/test_producer_starvation_draw.py` records the
   identical `KeyError: 'net_margin_gbp'` killing nine consecutive runs on 2026-08-17
   between 15:59Z and 17:17Z. Same key, same reader, same uncommitted lane, 24h apart.

## Why no control saw it

Every existing control's subject is a **committed** tree, and the tree that ran was not one.

* The pre-commit gate judges the tree a commit *would create*. During a swap, no commit is
  being attempted on the swapped-out lane at all.
* The publish-gate wedge detector keys on publish FAILURES; ten failed runs produce zero
  publish attempts (the fail-open-on-empty already recorded in `background/sim_runner.py`).
* The census that would have caught the un-paired reader —
  `tests/saas/test_net_after_cts_and_blindfold_arithmetic.py::
  test_no_module_reads_net_margin_gbp_off_a_cost_to_serve_view` — reads the working tree
  and was **green on disk throughout**, because the swap window is shorter than any test
  run and no one ran it during one. It was also itself uncommitted, so it had no automated
  caller and protected nothing.

The signature of this class: no state is corrupt, so no checker fires. Here it is sharpened
by a second axis — the risk window is **transient**, so even a checker pointed at the right
tree only fires if it happens to run inside it.

## What was done about the instance

The repair was **landed whole** rather than re-typed: producer side (`saas/cost_to_serve.py`
deleting `net_margin_gbp`), every migrated reader, and the census. A swap only exists
because the other lane's hunk is uncommitted; once landed, no lane ever needs to swap that
file again, and the key-deletion and the readers that stopped asking for it can no longer
be separated by any working-tree operation. Re-typing the reader hunk would have cleared
the rung and left the next lane to swap the same file next week — the instance fix this
class exists to refuse (R10), and the second strike (R3) on the same component.

## What is still open

A two-lane file is not rare, and the next one may also be on the producer's import path.
The residual exposure, in priority order:

1. **The cheapest real mitigation is the one taken here: land, don't hold.** A hunk that
   sits uncommitted in a producer-path file is a scheduled outage waiting for the next
   lane that needs that file. Time-to-land is the control variable, not swap technique.
2. **A swap window is not currently visible to anything.** A lane that must swap a file the
   producer imports has no way to say so, and nothing correlates a producer failure streak
   with a swap in flight — which is why the diagnosis above needed a commit message and a
   millisecond mtime rather than an instrument.
3. Not proposed here as a build: pausing the producer for the swap window trades a
   guaranteed short stall for a possible long one, and the honest fix upstream is (1).
