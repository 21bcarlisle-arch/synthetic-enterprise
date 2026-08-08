<!-- SUPERVISOR_DRAW: available -->
# [WORKER-FINDING] Green work is dying uncommitted in the shared tree (2026-08-08, AO2 tick)

**Class:** work-at-risk. **Found by:** the 21:04 tick, while committing `AO2_write_time_reuse_gate`.
**Status:** one instance ADOPTED and committed, one instance STILL AT RISK, class NOT closed.

## What was observed (observed-with-evidence, R9)

Committing AO2 required staging `docs/design/maturity_map.yaml`. The level-promotion gate refused the
commit — not for AO2, but for **a different atom's unrecorded level move sitting in the same file**:
`W2_16_payment_outcome_rng_substream_isolation`, moved 0→2 by an earlier tick that never committed.

Checked rather than assumed:

* the authoring tick's last write was **20:45**; this tick started **21:04**; `ps` showed **no other
  worker process alive**. So: died dirty, not in flight.
* its build was **complete and green** — `simulation/arrears_engine.py:117` defines `bill_substream`,
  all four consumers migrated, `test_arrears_engine.py` + `test_dd_collection_book.py` = **77 passed**.
* **Adopted, verified and committed** as `14e00c2ba`, with the level move recorded in
  `gate_authorizations.jsonl` explicitly as an **adoption** — honest attribution, so the ledger does
  not read as if this tick built it.

## The instance still at risk

`simulation/premise_trace.py` (+176 lines) and `tests/simulation/test_premise_trace.py` (+146 lines)
are **uncommitted in the working tree**, from a *third* tick — household routine-offset work
(the "population envelope is not any single household's clock" argument, an L2.3-class point-mass
defect). **51 tests pass.** This tick did **not** adopt it: it did not block AO2, its owning atom was
not identified, and adopting an unidentified atom's work is a worse defect than leaving it one more
tick. It is one broad `git checkout`/`git add` away from being lost or silently swept.

## Why this is a CLASS, not two incidents (R10)

Three ticks in one evening left green, uncommitted work in a shared tree. The bounded-invocation
contract says *"do the drawn work, commit it, then STOP"* — but a tick that is cut off, or that exits
believing it has finished, leaves the tree carrying value that **only a later tick's accident**
discovers. AO2's gate found this one by luck: it happened to need the same file. Nothing looks for it
on purpose.

The existing machinery is adjacent but does not cover this: `fork_reconciler` watches **fork
branches**, and the unmerged-work draw guard reads **git reality for branches** — both miss
**uncommitted working-tree state on `main` itself**, which is where all three instances lived.

## WORK THIS CREATES

1. **A tick-exit check** — before a bounded invocation exits, report uncommitted green work in the
   tree that is outside its own `file_scope`: whose it is (map cell / recent commits), whether its
   tests pass, and whether it is recorded. Report, never auto-commit — auto-committing another
   lane's half-finished build is the mirror defect.
2. **Dispose of the `premise_trace` orphan** — identify the owning atom, verify, then adopt-and-record
   or discard with a reason. Do not leave it a third night.
3. **A map-file contention note** — two ticks editing `maturity_map.yaml` cannot be separated by
   pathspec, so one tick's commit necessarily carries the other's cell. The ledger record is what
   keeps that honest; the alternative (reverting the other cell) destroys live work and is worse.
   Relates to `H9_map_write_serialisation`, still unbuilt.

*Queued, not fixed on sight, per SELF_INTERRUPT_DISCIPLINE — the machine was not blocked.*
