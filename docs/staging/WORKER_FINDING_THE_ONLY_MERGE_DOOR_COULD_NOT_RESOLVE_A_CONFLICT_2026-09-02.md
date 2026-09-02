# [WORKER FINDING] The only merge door could not resolve a conflict, so a conflicting merge had no legal route

**Severity:** RECORDED (the door is built, mutation-proven, and used on the conflict that motivated it)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02. Named by the director after I hit it by hand: *"The conflict door needs its
design pass, as you say — the next time two lanes touch one file there's no legal route, and that's
a wall with a hole in it."*

## Class registration

Belongs to `controls_that_cannot_fail`. Not a control that fires wrongly — a wall whose only door
had no handle for one of the two states it must handle.

## All three routes were shut

| route | why it was unavailable |
|---|---|
| `surgical_land --merge` | the ONLY sanctioned reconciliation, and it refused on conflict with no way to settle one |
| `git merge` on the shared tree | forbidden, and rightly: that index held **57 staged entries belonging to another lane** |
| hook-bypass | a wall, never a judgement call |

So a conflicting reconciliation had to be done **by hand in a worktree**. That happened twice in one
morning on one file — the director's own brief, whose unchained copy on origin conflicted with the
chained copy locally — and each time it blocked every landing, the publish path and the site behind
it.

## The design, and the one rule that makes it safe

`--resolve REPOPATH=SRCFILE`, under four rules:

1. **Only a path git itself reports as conflicted.** This is the load-bearing one. Without it,
   `--merge --resolve` is a way to put arbitrary bytes into a commit whose receipt says *merge* and
   whose scope a reader takes to be "whatever the other history changed". Mutation-proven: drop the
   check and a file **neither side edited** changes silently inside a merge commit.
2. **Every conflicted path must be settled, or refuse.** A partial resolution commits git's conflict
   markers as content — a broken file that passed a gate.
3. **The bytes come from outside the repo**, refused at the door rather than trusted. A resolution
   read from the working tree brings back the swap-and-restore hazard of the 2026-08-19 R3 finding,
   where a landing that never happened leaves a tree indistinguishable from one that did.
4. **The gate still runs on the resulting tree.** Resolving a conflict makes a tree *expressible*;
   it buys no exemption from anything.

**It does not choose.** The caller supplies the bytes, because which side wins is a judgement about
two lanes' intent that belongs to a person reading both. `origin_reconcile` therefore still refuses
on conflict and always will — an automatic reconciler must not pick.

**The receipt says a person chose.** `conflicts-resolved: <paths>` is emitted only when a resolution
happened, so absence means absence, and `--verify` reads it back. A merge whose tree is neither
parent's at some path must say so, or a later reader finds a difference that looks like a third lane.

## A pre-existing defect this made load-bearing

`git merge-tree --write-tree --name-only` prints the tree sha, then one path per line, then a
**blank line**, then commentary (`Auto-merging x`, `CONFLICT (content): ...`). The refusal took
everything after the tree sha, so a ONE-file conflict was reported as **"4 conflicted path(s)"** with
`Auto-merging ...` listed as if it were a filename. Observed live this morning and read past twice.

Harmless while the number was only prose in a refusal. **Fatal the moment a resolution has to be
matched against that set**: a caller settling the one real path would be told two commentary lines
were still unresolved, and the door would refuse forever.

## Used on its own subject

The first resolved merge is `e3730c4e9` — the conflict that had blocked this fork twice, settled
through the front door instead of by hand:

```
[surgical-land] landed MERGE e3730c4e9 (origin/main into HEAD)
receipt consistent for e3730c4e9: tree 832227093, 1 path(s), gate-rc 0
conflicts-resolved: docs/staging/DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02.md
```

The resolved content is the director's corrected text verbatim — including his own correction moving
the issued bills out of the raw export, *"because a bill is the calculation"* — plus the severity
header the gate requires. `origin_reconcile` then pushed four gated landings that were sitting
local-only, without being asked.

## What this does not claim

Not that the refusal was wrong: a conflict with nobody choosing is not landable, and that is
unchanged. Not that resolutions should be automated — the opposite. The claim is that **a wall must
have a door for every state it forbids passage through**, and this one had a door for the clean case
and nothing at all for the conflicted one, so the only way past it was outside the wall.
