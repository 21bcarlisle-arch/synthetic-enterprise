# [WORKER FINDING] "Landed" is not "pushed", and a staged document blocked every landing

**Severity:** RECORDED (the fork is closed, the work is on origin, and the block is now self-clearing)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02 by the director: *"none of it is on origin. The last machine commit there is
07:11 — before the reaper restart, the TMPDIR fix and the red register. Same shape as this morning:
landed in the tree, reported as landed, not pushed."*

## Class registration

Belongs to `uncommitted_and_orphaned_work`. Finished, gated work that never became part of the tree
anyone else can see — which is that class exactly, one step further out than usual: the commits
existed, they were just not anywhere a second party could read them.

## Measured, the moment he said it

```
local HEAD  2112a1f03      origin/main 36c8ea3ab
git rev-list --left-right --count origin/main...HEAD  ->  1   4
```

Four gated landings local-only, and origin one ahead. And the machine's own record already named the
cause:

```
docs/observability/.last_publish_cause.json
{"cause": "behind_origin", "evidence": "origin/main is 1 commit(s) AHEAD of HEAD ..."}
```

The site had been stale **3.2 hours** on the same condition.

## His hypothesis was right, and there was a third mechanism as well

The loop he described is real: a document staged to origin moves origin ahead, and
`_divergence_refusal` then refuses every commit until someone reconciles.

Trying to reconcile found a **third** blocker on top of it. The staged brief carried no severity
header, and an UNCLASSIFIED staging document refuses **every lane's commit**. So the first thing the
brief did was block the four landings that were waiting for it. That is the third occurrence
(2026-08-30, 2026-08-31, today) and the remedy has been identical each time: the seat chains it and
records that it did.

**Three independent blocks, all opened by one document arriving.**

## Why the merge could not go through the front door

`surgical_land --merge` **refuses on conflict and offers no resolution route** — no `--content`, no
strategy. The conflict was add/add on the brief itself (origin's unchained copy against the chained
one). And `git merge` in the shared tree was not available either: the shared index held **57 staged
entries belonging to another lane**, which is the exact state CLAUDE.md names when it says the legal
move is `surgical_land`.

Resolved by merging in a **throwaway worktree**, which has its own index — the hook ran in full, the
conflict was resolved to ours after diffing to confirm it was the director's text plus the header
block and nothing else, and the result was pushed. Verified against `origin/main`, not against my own
tree: all six commits are ancestors of it.

## The repair, and why it does not overrule the guard

The director asked to *"make the pull automatic rather than a refusal"*. `_divergence_refusal`
argues against exactly that, and its argument holds:

> *"The only sanctioned reconciliation is `surgical_land --merge origin/main`, which gates the whole
> tree and takes longer than a publish cycle; and there are routinely three lanes with uncommitted
> work in this tree. A daemon that merged unattended would be deciding, every twelve minutes, to
> move other people's work."*

Both halves are true **of the shared working tree** — and the shared tree is the only place either
applies. `background/origin_reconcile` therefore merges somewhere the objections cannot reach:

| the objection | why it dissolves |
|---|---|
| "would move other people's work" | a throwaway worktree has its OWN index; the shared tree is never opened |
| "takes longer than a publish cycle" | it runs on the deadman cadence, not inline — the fork is closed before the publish cycle looks |

**The refusal in the publish path is unchanged**, and a test asserts it still only reports. A
CONFLICT still refuses, naming the paths: a disjoint fast-forward is mechanical, and choosing between
two lanes' edits to one file is a judgement, not a cadence. The shared tree is only ever
`--ff-only`, and git's own refusal is the safety net — never `--force`.

## What I got wrong

**I reported four commits as landed without checking they were on origin.** "Landed" was true of the
tree and false of the record anyone else reads. The verification step now exists and is one command
(`git merge-base --is-ancestor <sha> origin/main`); not running it is what made three reports to the
director overstate what had happened.

And a near-miss worth recording: the merge ran in the worktree because the shell's cwd had persisted
from an earlier `cd`, not because I passed `-C`. Had it persisted the other way it would have
committed another lane's 57 staged entries. Every git call in that sequence should have been
`git -C <path>`, and the ones after it were.

## And I shipped the fix with the same defect in it

The first version of `origin_reconcile` closed the BEHIND direction only. Its own landing then sat
unpushed — *"landed in the tree, reported as landed, not pushed"*, reproduced inside the fix for it,
within the hour.

Found by running the verification step this very finding says I should have been running:
`git merge-base --is-ancestor <sha> origin/main` reported **MISSING** for the reconciler's own
commit. The habit caught the defect the habit is about.

**Reconcile has to mean BOTH directions or it does not mean agreement.** Nothing else on this
machine pushes a `surgical_land` landing: the publish path pushes its own commits and carries
whatever else is on the branch, so a landing reaches origin only when a publish happens to follow
it — and a blocked publish path means no landing ever leaves the machine. That is the whole
mechanism behind the director's complaint, and the behind-only version left it in place.

`LEVEL` now means AGREEMENT rather than "not behind", and an ahead count that cannot be read does
not push, on the same fail-closed direction as the behind side.

## What is not fixed

**The sanctioned merge door cannot resolve a conflict.** `surgical_land --merge` refuses, and there
is no `--merge --content` or equivalent — so a conflicting reconciliation has no legal route at all
and must be done by hand in a worktree, as this one was. That is a real gap in the one door the wall
permits, and it will recur the next time two lanes touch one file. Not built here: it needs a design
pass on what a gated conflict resolution should even look like, because "resolve to ours" is a
judgement the tool cannot make for itself.

## What this finding does not claim

Not that the origin-ahead guard was wrong — it prevented a widening fork and its reasoning is sound.
Not that the director staging documents is a problem; it is the point of the console. The claim is
that **three separate controls each correctly refused, and their combination made a document arriving
from the director into a total block on landing, publishing and the site** — and that no control saw
the combination, because each could only see its own condition.
