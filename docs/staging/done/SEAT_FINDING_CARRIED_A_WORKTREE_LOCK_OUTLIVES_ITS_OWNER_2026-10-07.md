**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `uncommitted_and_orphaned_work`

# A worktree lock outlives its owner

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-worktree-lock-outlives-its-owner` in `docs/direction/wrong_triage.yaml`. Listed 17 times across orientations, first on 2026-10-05.*

## What it is

`acff52923` is locked to pid 1364549, which is dead, and nothing re-asks the owner's liveness before the work is treated as in hand. Its `supervisor.py` is byte-identical to `20c9c52c9` on origin, so it is disposable. The seat's own `bab878923` was briefly in the same state.

## Why it is folded here

An orphaned worktree held by a dead owner is this class. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
