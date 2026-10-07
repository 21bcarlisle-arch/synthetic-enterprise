**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `uncommitted_and_orphaned_work`

# A finished, gated commit can sit on no remote while the queue re-issues its work

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-receipted-commit-on-no-remote-has-its-work-reissued` in `docs/direction/wrong_triage.yaml`. Listed 11 times across orientations, first on 2026-10-06.*

## What it is

`c5770c404` (B11 slice 3, receipt gate-rc 0) sat in an unlocked, ownerless worktree while a continuation re-issued the same change; `51bbb4d3d` and `ab5c181dd` recurred the shape. A receipt is not a landing, and nothing asks whether a receipted commit reached origin.

## Why it is folded here

Finished work stranded off every remote is this class's definition. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
