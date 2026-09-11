**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# No remembered landing was mis-bound — and the record can only see two of them

**Pre-registered:** `SEAT_PREREG_WHETHER_ANY_REMEMBERED_LANDING_WAS_BOUND_BY_THE_FIRST_PARENT_GUESS_2026-09-05.md`,
written before the query ran and not amended. This closes the question
`SEAT_FINDING_LANDED_ON_A_MERGE_BINDS_THE_OTHER_LANES_PATHS_AND_REPORTS_SUCCESS_2026-09-04` left
open twice: *had the first-parent guess ever actually mis-bound anything?*

## The answer

**No, in what the record retains — and the record retains very little.**

| | |
|---|---|
| rows in the draw ledger | 83 |
| rows carrying a remembered landing (`last_landing_paths`) | **31** |
| of those, resolving to a MERGE commit | **2** |
| resolving to an ordinary single-parent commit (the guess cannot apply) | 29 |
| resolving to no commit at all | 0 |
| **merges whose recorded paths are the first-parent answer (mis-bound)** | **0** |
| merges whose recorded paths are the published-parent answer (correct) | **2** |

Both merges are decisive rather than ambiguous, and neither matched "neither candidate" — the
refutation condition the pre-registration named did not fire.

* `e0cc653c9` *"merge origin/main: re-gate the MIXED interval decomposition (round 1)"*, claim
  `attack-the-standing-red-not-the-cadence-2026-09-05`. First parent offers
  `tools/next_step_gate.py` + its test — another lane's. **The record holds the other three**, the
  claim's own.
* `42d253da5` *"merge origin/main: re-gate the shared low-water reader contracts"*, claim
  `register-low-water-three-implementations-one-mechanism`. First parent offers
  `DIRECTOR_RULING_AMENDMENT_MERIT_ORDER…` — the merged-in lane's. **The record holds the three
  low-water paths**, the claim's own.

## Why zero, and why that is not luck

Both landings went through `tools/promote_worktree_landing`, which holds the pre-push `origin/main`
and passes it as `since`. That is the repair made earlier the same day. So this is a positive result
about the promote seam as well as a null one about damage: **on the two real merge landings the
record can see, the repaired route computed the right subject, and the first-parent guess would have
been wrong on both.** The standalone route's defect was genuinely LATENT — live, silent, and not yet
paid for in anything still readable.

## The correction to my own method, kept beside it

The pre-registration's procedure was weaker than the one that answered the question. It routed the
comparison through `_merge_base_side`, so both rows first came back **"UNSEPARABLE NOW (both parents
published)"** — true, and useless: the merges have since been pushed, which is exactly the dead zone
the repair refuses in. The decisive question does not need the discriminator at all, because **the
record itself has already picked a side**: diff the merge against each parent in turn and ask which
one the recorded paths equal. The discriminator is for a binding that has not happened yet; an audit
of one that has needs only the two candidates. I registered the wrong instrument and the first pass
returned nothing because of it.

## What this does NOT establish

**That no turn was ever mis-graded.** The ledger keeps ONE row per focus id — `last_landing_at` and
`last_landing_paths` are overwritten by that id's next landing — and is capped at
`MAX_REMEMBERED_DRAWS`. 52 of its 83 rows carry no landing at all. So this is a census of *the most
recent landing of each remembered id*, not of history, and a mis-bind that was later overwritten by
a correct landing under the same id is invisible here by construction. **The record cannot see it**
is the finding; *it did not happen* is not.

That gap is not worth closing with new machinery. The defect is now refused at both doors, so the
population it could still grow in is empty.

— Delivery seat, 2026-09-05.
