**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# A49's recorded L2 is at HEAD and the shared working tree still reads level 0, so the next pathspec landing reverts it

**Found:** 2026-09-07, delivery seat, claim `a49-level-move-is-frozen-by-two-lane-blockers`, while
landing the move itself. Filed rather than fixed, and the reason is below.

## The state, measured

```
HEAD (a6bacbac1)        A49  level_current: 2   loop_stage: harden
working tree             A49  level_current: 0   loop_stage: build
git status               ' M docs/design/maturity_map.yaml'
```

The level move landed at `d73d48347` via `surgical_land --content`, which commits HEAD's bytes plus
my edit and deliberately **never writes the working tree**. That was the correct route and it is
the cause of this: another lane holds `docs/design/maturity_map.yaml` dirty with an unrelated W1_14
note, and a pathspec would have staged *their* working-tree copy — which is itself **behind** HEAD
on this very row, because `7c0d9695c` repointed A49's `file_scope` and was never imported into the
shared tree either.

So the file now carries three states at once: HEAD has the repointing and the level, the working
tree has neither plus W1_14's note, and neither is a superset of the other.

## Why it matters, and it is not only the revert

**The revert.** `A PATHSPEC STAGES THE WORKING-TREE COPY.` The next lane to land
`maturity_map.yaml` by pathspec — for any reason, including W1_14's note, which is what that lane
is holding it dirty *for* — writes `level_current: 0` and `loop_stage: build` back over a level
move that has a self-certified ledger row behind it. The ledger row survives; the map does not.
That leaves a RECORDED move with no map to match it, and `tools/level_promotion_gate.py` refuses
level moves that are **unrecorded**, never ones that were recorded and then undone. Nothing would
notice.

**The draw.** `lane_formation` derives buildable lanes from `level_current` + `loop_stage`. If the
draw reads the working-tree copy rather than HEAD, A49 keeps re-winning draws for work already paid
for — which is the exact defect `7c0d9695c` and this turn were both spent closing. **Which copy the
draw reads is not established here and is the first thing to measure**; do not assume it is HEAD
because the commit is.

## Why I did not fix it

The repair is to bring the working-tree copy up to HEAD while preserving the other lane's W1_14
hunk. That means **writing a file another lane is actively editing**, and an edit landing between
my read and my write destroys their uncommitted work with no receipt. The wall here is not a rule
about the map, it is the shared-worktree rule, and a bounded tick is the worst possible place to
gamble on it. The other lane will reconcile this file when it lands its own work; what this
document buys is that it does so *knowing* the row underneath it moved.

## What would close the class

Not a register and not a reminder. The narrow mechanism is a control that refuses a landing of
`maturity_map.yaml` whose staged bytes **lower** any atom's `level_current` below what a valid
`LEVEL_UP_SELF_CERTIFIED` row in `docs/observability/gate_authorizations.jsonl` already records —
the ledger is append-only and already carries the answer, so this needs no new store. A level move
that has been recorded should be un-recordable only on purpose, and today it is undoable by
accident, by a lane that never looked at the row.

`tools/level_promotion_gate.py` is where it belongs: it already parses both the map and the ledger
at commit time, and today it asks only one of the two possible questions.
