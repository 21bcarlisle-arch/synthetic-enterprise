# FINDING — a finished cut sat uncommitted on the shared tree, and every control was green

**Date:** 2026-08-12 · **Atom:** `KNIFE3_wall_crossing_paydown` · **Class:** record/code divergence
**Status:** instance repaired and landed (`f3de95f94`, `55a841d12`); the CLASS is filed here, not fixed on sight.

## Observed, with evidence

This tick drew `KNIFE3_wall_crossing_paydown` and found step 19 — the counterparty
collateral desk cut — **already built and not committed**:

```
?? company/interfaces/counterparty_collateral.py
?? company/risk/counterparty_collateral_desk.py
?? tests/company/interfaces/test_counterparty_collateral_seam.py
 M simulation/run_phase2b.py
 M tests/architecture/test_epistemic_wall_ratchet.py
 M docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md
```

All six mtimes 2026-08-12 00:25–00:30. The work was complete: 14 seam tests, 5 of them
mutations; the ratchet allowlist already had its three `LEGACY_SIM_READS_COMPANY` tuples
deleted; register §3n already written. Run on the working tree it was green —
92 passed across the four wall/architecture suites, `wall_crossing_dispositions` rc 0.

## Why nothing caught it

**The three artefacts agreed with each other.** The register said `cut`, the ratchet
allowlist no longer named the edges, and the code no longer made the imports — so every
control that compares one of these to another was satisfied. `wall_crossing_dispositions.py`
measures **the working tree** and printed `OK`. There was no red anywhere, on any machine,
for anyone to see.

That is the distinguishing feature: this is not a control that failed open, it is a
**complete and internally consistent change set that simply never became a commit**. The
controls were doing exactly their job on exactly the tree in front of them.

## Why it matters more than a lost afternoon

On this tree there are concurrent writers (`process_run_complete.py`, the interactive
session, `autonomous_runner.py` turns). An orphaned change set of this size is one broad
`git add` away from landing under another lane's commit message — a five-file cut, its
ratchet allowlist and its register section attributed to a publish commit. It is also one
worktree prune away from being gone. Related, already recorded:
`feedback_forks_die_dirty_audit_before_prune`,
`feedback_a_concurrent_sweeper_can_commit_one_half_of_a_two_file_atomic_write`,
`feedback_untracked_build_passes_local_green`.

## The second half of the same finding

The atom's own record (`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`)
still read **STEP 17 / "36 of 91 live"**. Step 18 (`9ef7d5d6e`, flexibility revenue,
register §3m, 36 → 34) had landed its code and its register section and **not** updated the
record either. So the record was two steps behind the tree, in the direction that
*understates* progress.

This is the mirror of `feedback_the_record_can_outrun_the_code`: here the **code outran the
record**. Both break the same property — a reader re-deriving the atom's progress from its
own store gets the wrong number — and the previous step already filed a version of this
(`WORKER_FINDING_AN_ATOMS_OWN_RECORD_STATES_TWO_COUNTS_FOR_ONE_TREE_2026-08-11`). That is
now **three consecutive steps** in which this atom's record was wrong about the tree, which
under R3 (two-strike redesign) means the mechanism, not the instance, is the thing to change.

## Recommendation — and what I did

The prose remedy ("a KNIFE step is not done at green, it is done at LANDED-AND-RECORDED")
is an exhortation, and MAKE_IT_STICK says exhortations evaporate. The mechanised version:

**A tick-boundary orphan check.** At the end of a bounded invocation, `git status --porcelain`
restricted to the drawn atom's `file_scope` must be empty, or the tick names what it left
behind. This is cheap, it reads real git state, and it fails on exactly the shape found
here — a green, complete, uncommitted change set. A weaker variant that only checks for
*untracked* paths would miss the two modified files that carried half of this cut.

**Recommendation: mint this as a harness atom** (`H_harness`, small) rather than build it
inside a KNIFE step — a wall pass must not land a scheduler change in the same commit as an
import move, which is B7's rule and the reason step 17's naming residual was also left
alone. I have not minted it in this tick: minting is a code change to the map and this tick's
`file_scope` is the wall pass. **Unless objected to, the next harness draw takes it.**

I did the reversible parts: landed step 19 with its receipt verified
(`tree d3c964b46, 6 paths, gate-rc 0`), then brought the record up to step 19 with the
divergence stated in the record itself rather than quietly corrected.

## Not claimed

Nothing here identifies *why* the previous tick exited without committing — no evidence was
found either way, and per R9 that stays `inferred`-at-best and therefore unstated. The
finding is about what the controls could and could not see, which is observable.
