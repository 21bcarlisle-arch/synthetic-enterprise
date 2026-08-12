# WORKER FINDING — the resurrection guard is blind to a resurrection that exists only in HEAD, because its subject is the working tree

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, worker tick, immediately after causing the defect and then
mis-describing it in the commit that fixed it. Both halves are the finding.

## Observed, with evidence

`background/finding_classes.check` rule 3 is documented as the guard for exactly this:

> 3. Every listed instance is IN the archive and NOT back in the root (exit criterion 2;
>    the resurrection class, `WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_
>    THE_SHARED_TREE_2026-08-10`, is this exact move's known failure mode here).

Its implementation is `(root / name).exists()` and `(archive / name).exists()` — **filesystem
probes on the working tree**. It has no view of what is committed.

Commit `0c0733e0a` archived `WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12.md`.
`git mv` had already made the working tree correct — root copy gone, archive copy present —
but the landing was a pathspec commit, and a pathspec is resolved against paths that EXIST,
so the vanished root path was silently not among the twelve. The committed tree therefore
carried the file in both rooms (`observed-with-evidence`):

```
$ git ls-tree -r --name-only 0c0733e0a -- docs/staging | grep HARNESSES_CONVENIENCE
docs/staging/WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12.md
docs/staging/done/WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12.md

$ git ls-tree -r --name-only 80e0dce91 -- docs/staging | grep HARNESSES_CONVENIENCE
docs/staging/done/WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12.md
```

`--check` returned PASS throughout, correctly: the tree it looks at was never wrong.

## The correction to my own commit message, which is the sharper half

`80e0dce91`'s message says the root scan "is what would have caught this — it did not run
between the two commits." **That is wrong and is corrected here.** Running it between the two
commits would also have passed, because its subject is the working tree and the working tree
was already correct. The check could not have caught this at any moment. Saying "it did not
run" implies a schedule defect; the actual defect is a SUBJECT defect, and the two have
different fixes — one buys a cron entry, the other buys a different question.

## A SECOND instance, caught while filing this one — and it is the same shape

Consolidating this document, I archived it into `docs/staging/done/` and THEN ran `--render`.
`--check` returned PASS. It should not have: the finding was in the archive and named by no
class document at all.

The mechanism, read off the source rather than inferred: `check` derives its
UNCONSOLIDATED failure from `derive_memberships(root)[...].members`, which is the LIVE root
scan — an archived document is not live, so it cannot be missing from a list. And
`archived_instances` only returns names **the class document already lists**, so rendering
after the move cannot recover it either. Archive-then-render is therefore a hole through
which a finding leaves the root, enters no class, and reports green from both directions.

The correct order is render-then-archive, which is what this document ended up doing. But an
order that must be remembered is a rule with no mechanism, and this repo's own record says
those evaporate. `--render` knows the membership it just computed; nothing stops it from being
the thing that MOVES the file, which would delete the ordering question rather than document
it.

Fold into the same atom below: the guard's subject and the consolidation's ordering are one
job on one module, and splitting them would mean touching `finding_classes.py` twice.

## Why it is LATENT and not BLOCKING

Nothing published is affected and no verdict rests on it: the divergence lived for two commits
on one branch, and the state a fresh clone would have seen is now correct. What is untrue is
rule 3's docstring, which claims a guard against the resurrection class that a resurrection
arriving through the commit rather than through the filesystem walks straight past.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_class_check_reads_the_committed_tree`** — give rule 3 the tree the gate is actually
about. The cheap, honest version is not "check both": it is to name the subject in one place
and let the caller choose it, so a HEAD-scoped run is possible at all. R15 both ways: the
check must FAIL on a hand-built tree carrying an instance in both rooms (the `0c0733e0a`
shape, replayable from that commit), and must stay green on the same tree once the root copy
is removed — and the mutation must be the TREE, not the filesystem, or it proves nothing new.

Same class, already filed against other controls here: a control whose subject is the working
tree cannot see a HEAD-only divergence. This is the instance where the control's own docstring
named the failure mode it is blind to.
