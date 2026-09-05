**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: what the inverse of `undispositioned()` must fire on, written before it was run

**Filed 2026-09-05 by the delivery seat from an isolated worktree at `HEAD = 986499b1f`, BEFORE
deriving any census at any other commit. Claim id: `census-register-erosion-inverse-check`.**

---

## The hole, restated so the control can be judged against it and not against its author

`background/self_clearing_alarm_census.py` has two teeth and neither bites here:

- `census_is_vacuous()` refuses a **totally** empty census — no functions, no paths, no writers, no
  readers, no hits. Per-path erosion is not its subject.
- `undispositioned()` refuses a **hit with no row**.

**Nothing refuses a row whose hit disappeared.** A path that stops being a hit needs no
disposition and `--check` exits 0. That is how five carriers left the class silently on
2026-09-05 (`SEAT_FINDING_THE_CENSUS_LOST_FIVE_HITS_TO_THE_REPAIR_THAT_FIXED_THEM_2026-09-05.md`),
and twelve more had gone the same way in earlier eras before anybody looked.

## What I am building, stated before the numbers

`eroded_dispositions(census, dispositions)` — the inverse. A dispositioned row is a standing claim
that *this state path is a member of the class*. The control asks whether the census can still SEE
its own subject, and it partitions the ways a row can stop being a hit:

| the row's path, in the derived census | verdict |
|---|---|
| still a hit | fine |
| absent from `state_paths` entirely | **RED — the derivation lost the path** |
| present, **zero writers** | **RED — the write derivation went blind on it** |
| present, **zero readers** | **RED — the read derivation went blind on it** (this is exactly `run_history.json`) |
| present, writers AND readers, but no longer a hit | **RED unless the row authors a `declassified` reason** |

The split is the whole design and I am pre-registering the reason for it. **A row that stops being
a hit while the census can still see the path being written and read is a change of
CLASSIFICATION, and that is what a genuine repair looks like** — the failure path no longer writes
what the alarm reads. Keying the control to "every row must still be a hit" would go red exactly
when the code became more honest, which is this project's named backwards-control shape. So a
declassification is admitted, but only when someone WRITES DOWN why — never silently.

A row whose path the census can no longer see written, or no longer see read, is a different
animal: the instrument lost the subject, and that is indistinguishable from the repair-shaped
erosion by construction. It fails loud.

## Predictions, before running anything

1. **At `HEAD` the control returns ZERO rows.** All 50 dispositioned rows are current hits — the
   row set was authored against the post-repair census on 2026-09-05. If it fires at HEAD I have
   either found a further eroded row or written a control that cannot be satisfied, and I must
   establish which before landing it.
2. **Derived at `c30738d77` (the loader sweep, before `18a01f889` repaired the seam), against the
   dispositions file as it stood at that commit, the control fires on at least five rows and the
   five include `run_history.json`, `.harden_cooldown.json`, `.ntfy_digest_state.json`,
   `.supervisor_map_exhausted_state.json` and `retired_paths_served.json`.** This is the
   falsifier. A control that would not have caught the incident that motivated it is not the
   inverse of anything, and if this comes back short I will report the shortfall rather than
   reshape the control until it passes.
   - Sub-prediction, and I do not know this one: I expect those five to fire under the
     **zero-readers / zero-writers** leg rather than the absent-from-`state_paths` leg, because
     the seam killed attribution and not the path.
3. **At HEAD the control cannot fire on real data, so its branches must be INJECTED to be proved.**
   A synthetic census plus a synthetic dispositions mapping, one per leg, and one control over the
   whole partition asserting every leg is reachable — a guard that refuses everything passes every
   per-leg test.

## The second question this turn was handed, and it is a judgement not a measurement

`test_the_executor_writes_no_code_to_the_shared_tree` relativises all three entries of
`seat_executor.SHARED_TREE_WRITES` against `seat_executor.PROJECT_DIR`. Two of them are anchored
to that root; the third, `seat_continuation.STORE`, is anchored to `shared_tree_dir()` **by
design** — that anchoring was the 2026-09-04 hand-off repair. From the shared tree the two roots
coincide and the test passes. From a linked worktree `relative_to` raises, so the control
certifying *"the executor writes no code to the shared tree"* is red in the only environment the
executor ever runs in.

**My decision, registered before I write it: neither root — each path relativises against the root
it is ANCHORED to, and the test discovers which.** Every entry must lie under `docs/observability/`
of the module's own `PROJECT_DIR` **or** of `seat_continuation.shared_tree_dir()`. That is
strictly stronger than what is there now, which checks one root and would admit anything under the
other; it is true from both trees; and it does not require the test to hand-list which entry
belongs to which tree, a list that would decay the next time an entry is added.

I predict this makes the test pass from this worktree and leaves it passing from the shared tree,
and that the stated mutation (add any other shared-tree path) still fires under both roots.
