**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `controls_that_cannot_fail`

# The stash-completeness sweep reports a genuinely lost file as safe

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `stash-completeness-sweep-reports-a-lost-file-safe` in `docs/direction/wrong_triage.yaml`. Listed 90 times across orientations, first on 2026-09-24.*

## What it is

After a seat ran `git stash` on the shared tree (2026-09-24, 436 paths swept, all recovered), the sweep that proves a stash was fully restored was found to pass on a file it had lost. `git restore --source=stash@{0}` skips a path that is in the stash but in neither HEAD nor the index, and `git diff --quiet HEAD -- <path>` is quiet for an untracked path whatever its content. So the control is green for exactly the file it exists to catch.

## Why it is folded here

It is a control blind to its own subject, which is this class's definition. The trigger is a never-do (a stash on the shared tree), so it fires rarely; the register holds it with its siblings rather than as its own carried row. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
