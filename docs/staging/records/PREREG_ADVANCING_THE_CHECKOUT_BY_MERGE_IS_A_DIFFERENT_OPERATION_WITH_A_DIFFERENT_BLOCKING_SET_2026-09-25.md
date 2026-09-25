# PREREGISTRATION — advancing the checkout by MERGE is a different operation from fast-forwarding, and its blocking set is a different set

**SEVERITY: HIGH** — the shared checkout has been structurally unadvanceable since the tree diverged,
and the live `pre-commit` chain has therefore been running a version of itself the trunk has moved
past. Written BEFORE the merge was attempted on the shared tree.

Claim id: `advance-the-shared-checkout-by-merge-because-ff-only-can-never-pass-a-diverged-tree`.

## The duplicate-work check cited my own draw

The draw warned that this id is `ALREADY HELD ... another writer has it in hand right now`.
`docs/observability/.seat_work_in_hand.json` carries one row, `claimed_at` 1790299214.67 =
**2026-09-25 02:20:14**, and this invocation read it at **02:22:52** — 2m38s later, `paths: []`.
It is this draw. No disposition taken; carrying on. (Known shape: the duplicate-work check can cite
your own draw.)

## What is already established, and is not re-asked here

Landed in `90486abba`: `core.hooksPath` is the shared tree's working copy, that copy is a clean
snapshot of shared `HEAD` (disk == index == HEAD blob), and `advance_shared_tree` is `--ff-only`
while `git merge-base --is-ancestor HEAD origin/main` is FALSE. Re-measured today and unchanged:
shared `HEAD` = `025b2793c`, **9 ahead / 4 behind** `origin/main` = `90486abba`.

The ahead leg's unpromotability, re-asked rather than inherited — every one of the 9 ahead commits
graded for a `[surgical-land receipt]` and a hook-gate mark:

    6a422ea0f  receipt=0  mark=0   chore(liveness): publish heartbeat while sim out
    430e5b00e  receipt=0  mark=1
    8e40bb205  receipt=0  mark=5
    e18f85222  receipt=0  mark=1
    (the other five carry receipts)

`6a422ea0f` carries neither. So the promote door refuses the whole leg, permanently, and the ff-only
advance refuses on divergence, permanently. Both legs of the loop confirmed at their own oracle.

## PREDICTIONS, each falsifiable, none of them yet measured

**P1 — THE BLOCKING SET IS A DIFFERENT SET, AND THE FF ONE IS STRICTLY LARGER ON A DIVERGED TREE.**
`paths_blocking_fast_forward` computes arriving paths as `git diff HEAD origin/main`. On a diverged
tree that includes paths only *we* changed, which a merge never writes. The set a merge is refused
on is `git diff $(git merge-base HEAD origin/main) origin/main`. I predict the two differ today and
that most of what the ff refusal names is not the cause of a merge.

**P2 — GIT REFUSES A MERGE ON A DIRTY INDEX ENTRY EVEN AT AN UNINVOLVED PATH.** If true, the
2026-09-02 fear this module is built on — *"57 index entries belonging to another lane ... a `git
merge` there would have swept every one"* — is FALSE for staged entries: git refuses rather than
sweeps. The sweeping danger would then be a danger that does not exist in the shape it is written in,
and the merge leg needs no new index rule of its own, only git's refusal reported in git's words.

**P3 — THE `commit-msg` CHAIN RUNS ON A MERGE COMMIT AND SOMETHING IN IT REFUSES.** `pre-commit`
does not run for a merge (git runs `pre-merge-commit`, which this repo does not have), but
`commit-msg` does. I do not know whether it passes.

**P4 — I CANNOT YET SAY whether the shared tree can be merged today.** The blocking set has to be
graded by `advance_shared_tree`'s own five classes first, and it is read from a tree three daemons
are writing. Between two reads three minutes apart the staged set already moved from 4 paths to 3
(`site/data/publish_provenance.json` left it). Any count below is of the second read and will be
recounted after the act, not before.

## What done means, decided here and not after

1. The shared tree's checkout **contains** `origin/main` — `git merge-base --is-ancestor origin/main
   HEAD` is TRUE in `/home/rich/synthetic-enterprise` — so the live `tools/git-hooks/pre-commit` is
   the trunk's, verified by reading the live file and not by inferring it from the ref having moved.
2. `advance_shared_tree` can reach that state on its own next time, without a seat: the merge leg
   exists in code, keyed to `is-ancestor` rather than to today's 9-ahead.
3. Whatever refuses the merge is repaired **as a class**, or named as a finding with its reason.

## What is explicitly NOT in scope, and why that is the cut

The ahead leg is **not** promoted and no amnesty is given to `6a422ea0f`. A gated commit and a
`--no-verify` one are byte-identical to the receipt check, so an amnesty reopens the hole the mark
closed. The cut is that **advancing the CHECKOUT and promoting the AHEAD LEG are two operations, and
only the second needs the wall**: the merge commit made here is local, is never pushed, and carries
no authored bytes of its own — which is a property that can be asserted, and below it is.

