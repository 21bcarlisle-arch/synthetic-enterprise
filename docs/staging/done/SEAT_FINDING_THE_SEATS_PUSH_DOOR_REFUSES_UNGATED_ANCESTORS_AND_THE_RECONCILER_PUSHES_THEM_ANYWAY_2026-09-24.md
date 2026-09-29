**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The seat's sanctioned push door refuses ungated ancestors; the automatic reconciler pushes them anyway — two push routes disagree about what is promotable, and the seat has the strict one

Claim id: `close-the-fork-the-publisher-has-been-dark-for-68-hours`. Measured 2026-09-24 19:39–20:25
from an isolated linked worktree. Prediction filed before any of it:
`records/SEAT_PREREG_CAN_THE_AHEAD_LEG_BE_CLOSED_FROM_A_LINKED_WORKTREE_2026-09-24.md`.

**This document's title and thesis were rewritten once, mid-turn, after the evidence refuted the
first version. The first version is quoted below rather than deleted.**

## What the item asked for was already spent, and this tree's own history said so

The item: *"Land this tree's 3 own commits onto origin so the checkout can fast-forward."* It is
spent, and not by this turn. The automatic reconciler closes the ahead leg by itself, routinely.
This worktree's own commit `398020a36` — *"prediction 2 settled: the ahead leg closed itself and
behind grew under it"* — had already settled exactly this, one invocation earlier. **The item was
drawn asking for work whose own conclusion was two commits below the tip of the tree it was drawn
against.**

Measured live during this turn, which is the cleanest demonstration available:

| time | shared tree | what happened |
|---|---|---|
| 19:39 | 4 ahead, 33 behind | I begin merging the ahead leg |
| 20:09 | — | `d8576cdca` *"automatic reconciliation in an isolated worktree"* pushes the leg **on its own**, parents `63356067f` + `95ec3faa3` |
| 20:23 | **1 ahead, 34 behind** | leg closed; a new commit `cfb5f34c4` had already reopened it; `behind` **grew** |

`contains_origin` is still `false` and `gap_paths` went **32 → 46**. The ahead leg is not a state to
be closed. It is a **flow**: the shared tree commits every ~12–60 minutes (9 commits in the 3 hours
sampled), the reconciler batches them up, and the leg reopens before anyone can act on its being
shut. A one-shot action against it cannot win and this turn is the proof.

**So the publisher's darkness is not the ahead leg.** It is the BEHIND leg — the fast-forward
blockers — which is what the original BLOCKING finding said and what the successor claim
`enact-the-four-path-base-wins-decision-on-the-shared-tree` owns. This item's WHY was a misdiagnosis
of its own subject.

## The finding that IS real, and it is not the one I first wrote

`promote_worktree_landing` refused my landing:

```
REFUSED: 13203ed91 carries no verifying surgical_land receipt, so it was not gated
Only gated commits are promotable. Re-land it through the door, or reset past it if it is not yours.
```

Two of the four ahead commits carry no receipt — `13203ed91` (*"delivery seat: direction for the
next stretch"*) and `61b67fa0d` (a daemon liveness heartbeat). `ec667ff1e` and `63356067f` do.

**Thirty minutes later all four were on `origin/main`**, ungated ones included, pushed by the
automatic reconciler through `d8576cdca` — a merge with *parents identical to the one I had built*.
`git merge-base --is-ancestor 13203ed91 origin/main` → **YES**.

So the refusal is a property of **the door, not the push path**:

> **The seat's sanctioned route is strictly stronger than the daemon's. Work a seat is forbidden to
> push, a daemon pushes nine minutes later, unexamined.**

This is the finding. It matters in three directions:

1. **It is a live denial-of-service on the seat.** Any ungated commit on the shared tree blocks
   *every* seat landing built on top of it, for as long as it is unpushed — while costing the
   daemons nothing. A seat that hits this burns a full ~10-minute gate cycle to discover it, as
   this turn did twice.
2. **The wall is enforced where it is cheap, not where it binds.** A control that the automated
   majority of writers routes around is not a wall; it is a toll on the one writer who reads the
   rules. That is this project's own *"a control that only guards your own controls"* shape.
3. **It cannot be fixed by tightening the daemon** without first answering the next section, because
   tightening it would wedge the reconciler on every heartbeat it writes — which is the deadlock
   this whole finding family is about.

## What is NOT established, and is recorded rather than guessed

**Whether those two commits were actually ungated.** The refusal says *"carries no verifying
surgical_land receipt, **so it was not gated**"*, and that clause **infers beyond its evidence**.
Checked directly: `RECEIPT_HEADER` is written only by `tools/surgical_land.py:185`;
`tools/git-hooks/pre-commit` writes no receipt at all. An ordinary `git commit` **does** run the
hook, producing a gated commit with no receipt, refused in identical words.

What the door observes is *"not landed through `surgical_land`"*. What it reports is *"not gated"*.
**I cannot tell from the commits which of these is true**, and the two imply opposite remedies — a
real bypass to close, or an over-strict door to relax. Not guessing. This is the cheap next
measurement and it is handed on.

## A second, independent defect

`promote_worktree_landing` **exits 0 on refusal**. All four rounds printed `REFUSED:` then
`promote rc=0`. A retry loop keyed to the exit code spins silently forever; a caller branching on it
reads refusal as success. Mirror of the known shape where `surgical_land` exits 1 on a landing that
succeeded. Not fixed here — its own atom, its own controls.

## What this turn actually did, and what it did not

- Merged the ahead leg from an isolated **linked** worktree, and **it worked**: `.git` here is
  `gitdir: .../worktrees/se-seat-executor`, one shared object store, so all four commits were
  reachable and the merge needed no access to the shared working tree. `surgical_land --merge
  63356067f` gated clean → `f0d9442d5`. **The standing belief that such a fork cannot be closed from
  a seat worktree is too strong** — that is true of a *working-tree* resolution, which is what the
  successor item is correctly scoped to, and false of a commit-graph one.
- Re-landed the leg's content on gated ancestry → `4f7eb613d`, gated clean.
- **Neither reached origin, and neither needed to.** The reconciler had already put the same content
  there by another route. `4f7eb613d` is abandoned deliberately: pushing it would add a duplicate
  commit of content already on `origin/main` (`git diff origin/main f0d9442d5` is **empty**).
- **The fork is NOT closed and this turn did not close it.** `contains_origin: false`, 34 behind.

**I cannot attribute the leg's closure to anything I did.** Two things changed — I built a merge
locally, and the reconciler pushed its own — and mine was never pushed. The honest reading is that
the reconciler would have done it with this turn absent.

## The first version of this document, kept because it was wrong in an instructive way

It was titled *"An ungated commit anywhere in the ahead leg makes the WHOLE leg unpromotable — and
that is why the publisher went dark"*, and argued that this was the permanent, recurring, binding
cause the contested-paths diagnosis had missed. **Refuted within twenty minutes** by the ungated
commits appearing on origin. The error: I generalised from *one door's refusal* to *a property of
the repository*, having checked exactly one door. The correct claim was available from the same
evidence and is narrower and more useful — two routes disagree. **A refusal tells you about the
thing that refused, not about the world**, and this is the second time this turn that a confident
reading of a refusal was wrong in the same direction.

## Predictions, graded beside themselves

**P1 REFUTED.** I gave ~60% that the gate would red on `site/data/*` generated against a
33-commit-older base. It passed clean. The door's stale-copy check reported those paths *"unchanged
on this side since the merge-base"* — origin had never touched them, so there was nothing to be
stale against. **I reasoned from the AGE of the bytes; what governs is whether the OTHER SIDE moved
them.** Age is not staleness.

**P2 half-right, and the wrong half is the trap.** Success shape right, route wrong. I predicted the
leg would close by being pushed by me; it closed by the reconciler while I gated.

**P3 CONFIRMED.** The publisher is still dark, still `behind_origin`. The mechanism argument holds:
the only production caller of `origin_reconcile.advance_shared_tree` is
`background/process_run_complete.py:6436` — **the publisher itself**. The repair for `behind_origin`
lives inside the daemon that refuses for it.

**Both of my named hypotheses were wrong and the load-bearing cause was on neither list.** The
pre-registration's value was in forcing the measurement, not in being right — and its
refuting-condition clause is the only part that fired as designed.

## Handed on

1. **Which reading is true** — ungated, or gated-without-receipt. Cheap: ask whether the hook ran,
   not whether a receipt exists. It decides whether the two-route disagreement closes by tightening
   the daemon or by relaxing the door.
2. **The two push routes disagreeing** is the real repair and it is not small.
3. `promote_worktree_landing` exiting 0 on a refusal.
4. The BEHIND leg — 15 blockers, 46 gap paths — remains the publisher's actual wedge, under the
   successor claim.
