**Severity:** LATENT · **Lane:** H_harness

# The simplifications count invariant is tree-wide, so two atoms red at HEAD refuse every lane's register entry — including the one written to accompany the code landing in the same tick

**Found by:** worker tick 2026-08-25, while landing `PB3_book_growth_as_earned_outcome` exit (b1).
**Not fixed here** (SELF_INTERRUPT_DISCIPLINE — the repair is EP1's lane's own in-flight build).
What this pass did instead is land PB3's code and tests without their register entry, and say so
in the commit message rather than quietly.

## Class registration

Belongs to `uncommitted_and_orphaned_work`: work that exists only in the working tree, is not
landable, and whose presence there taxes every other lane. The tax here
is unusual and is the reason the finding is worth writing separately — it is not paid by the lane
that owns the work, it is paid by whoever next tries to write anything into the register.

## Observed, with evidence

`tests/design/test_simplifications_store.py::test_counts_match_file_contents` compares the map's
`simplifications_count` against `simplifications_store.load_all()` **over every atom in the tree**.
It is therefore not scoped to the atom a commit touches. At HEAD `a94dd33ca` two atoms disagree:

| atom | map `simplifications_count` | store count at HEAD | store count in the working tree |
|---|---|---|---|
| `PB3_book_growth_as_earned_outcome` | 3 | 2 | 3 |
| `EP1_clv_three_horizon` | 18 | 16 | 18 |

Measured, not inferred — `check_counts_match` run against the tree the commit would create
(HEAD + pathspec, `git archive` of the result tree, not the worktree):

```
RESULTING (HEAD + PB3 register entry) -> ['EP1_clv_three_horizon: map simplifications_count=18 != store file count=16']
WORKTREE                              -> clean
```

The worktree is clean because it holds BOTH lanes' uncommitted halves. That is the whole finding:
**neither atom's register entry can land alone, and the invariant that couples them is not one
either lane chose to depend on.**

## Why EP1's half cannot simply be landed alongside

It was attempted, in the same tick, with all three of EP1's store paths in the pathspec (the live
file plus the two archive chunks its roll created). The record-landing-claim gate refused, correctly:

```
[test-gate] ❌ A STORE RECORD CLAIMS A LANDING THIS COMMIT'S TREE DOES NOT CARRY -- COMMIT REFUSED.
  - EP1_clv_three_horizon.yaml: claims `ep1_series_provenance` landed in `tools/couple_clv.py` ...
  - ... `select_belief` ... `flatten_ep1_series` ... in `tools/couple_clv.py`
  - ... `build_three_horizon_clv_snapshots` in `company/analytics/customer_value_view.py`
  - ... `three_horizon_clv_snapshots` in `simulation/run_phase4c_on_phase2b.py`
```

All five symbols exist in the working tree and in no commit. EP1's passes 18 and 19 are a live,
610-line, six-file build (`tools/couple_clv.py` +336, `company/analytics/customer_value_view.py`
+162, `tests/saas/reporting/test_three_horizon_clv_section.py` +78, plus three smaller) that was
not this tick's to adopt or to verify — and `simulation/run_phase4c_on_phase2b.py` is read by the
live sim_runner from the working tree, so a foreign lane landing a partial edit of it is an outage
shape this project has already paid for once.

EP1's store state is otherwise a clean, complete ROLL: passes 11 and 12 moved live → archive
`.009`/`.010`, passes 18 and 19 appended, six live entries either side, no entry lost or duplicated.
The record is not the problem. The record is ahead of its code, which is the ordinary condition of a
lane mid-build, and the invariant makes that ordinary condition contagious.

## Why it is LATENT and not BLOCKING

Nothing this company has published is wrong, and no control's verdict is untrustworthy — the check
is working
exactly as designed and refusing exactly what it says it refuses. Nothing is owed by EP1's lane
beyond finishing the landing it is already in the middle of. Marking this BLOCKING would hold level
raises in a lane whose only fault is being mid-build, which is the opposite of the repair.

## What was landed instead, and the debt it leaves

`50274434a` — PB3's `offer_position_multiplier` mechanism and its 32 tests, without the
simplification entry that names the symmetry assumption the code makes. The entry is written and
sits in the working tree. **That is a real debt and not a bookkeeping one:** the entry is where the
dearer-side symmetry is registered as a named simplification, so until it lands the code makes an
assumption the register does not carry. It lands with EP1's own repair.

## The transferable question, offered rather than answered

A per-atom invariant would have let both lanes land. A tree-wide one catches a class the per-atom
one cannot — an atom whose store file was deleted outright, or a count moved on an atom nobody is
touching. Which of those two failures is worth the coupling is a design question for whoever owns
`OPS10`/the store contract, and this finding does not presume the answer. What it does claim,
`observed-with-evidence`, is that the coupling has now cost two lanes a landing each and that the
cost is invisible from either lane's own diff.
