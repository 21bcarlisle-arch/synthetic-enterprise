**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `uncommitted_and_orphaned_work`

# A bounded executor turn can be reset over finished, unlanded work

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-bounded-executor-turn-resets-over-unlanded-work` in `docs/direction/wrong_triage.yaml`. Listed 39 times across orientations, first on 2026-10-02.*

## What it is

An executor turn that hits its limit mid-gate leaves finished work in its worktree, and the next tick resets the worktree over it (`822218441` exists only because a worker recovered the diff). The brief now reads all worktree HEADs against a remote ref, so the instances are seen, but nothing prevents the class.

## Why it is folded here

Finished work that never became part of the tree is this class's definition. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
