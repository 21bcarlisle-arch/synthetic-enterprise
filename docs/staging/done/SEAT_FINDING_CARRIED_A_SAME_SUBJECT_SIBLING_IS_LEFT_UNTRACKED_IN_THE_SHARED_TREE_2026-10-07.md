**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `uncommitted_and_orphaned_work`

# Nothing on the landing path asks whether a same-subject sibling is left behind in the shared tree

*Folded by the console seat's triage of the delivery seat's carried "what it got wrong" items, 2026-10-07. Triage id `a-same-subject-sibling-is-left-behind-in-the-shared-tree` in `docs/direction/wrong_triage.yaml`. Listed 75 times across orientations, first on 2026-09-28.*

## What it is

A landing from a worktree can leave an untracked same-subject copy in the shared checkout (`551f5a736` left the shared copy of a test; the 14-path refusal in `662da7fd3`). The copy then holds the fast-forward or is mistaken for work.

## Why it is folded here

Work left outside the tree beside its landed twin is this class's subject. Folding retires it from the carried list; the register `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` owns it from here, and its `## Disposition` decides it.
